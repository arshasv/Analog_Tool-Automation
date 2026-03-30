"""Two-stage W/L optimizer using existing ngspice pipeline.

This module implements the mandatory two-stage optimization strategy:

1. Coarse search (random sampling over W/L variables).
2. Local Nelder–Mead search starting from the best coarse candidate.

It reuses the existing AnalysisOrchestrator and NgSpiceExecutor so that
no new simulation entry points are needed.
"""

from __future__ import annotations

import logging
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Tuple, Callable

from app.core.config import settings
from app.services.analysis_orchestrator import AnalysisOrchestrator
from app.services.ngspice_executor import NgSpiceExecutor
from .cost_function import compute_cost
from .param_update import (
    WLVariable,
    extract_wl_variables,
    apply_wl_assignment,
    assignment_from_vector,
    vector_from_assignment,
)

logger = logging.getLogger(__name__)


@dataclass
class OptimizationConfig:
    """Configuration for W/L optimization run."""

    max_iterations: int = settings.MAX_OPTIMIZATION_ITERATIONS
    coarse_samples: int = 12
    top_n: int = 5
    cost_threshold: float | None = None


@dataclass
class OptimizationResult:
    """Result of an optimization run."""

    best_assignment: Dict[str, float]
    best_metrics: Dict[str, float]
    best_cost: float
    iterations: int
    history: List[Dict[str, Any]]


class WLOptimizer:
    """End-to-end W/L optimization orchestrator."""

    def __init__(self, config: OptimizationConfig | None = None) -> None:
        self.config = config or OptimizationConfig()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def optimize(
        self,
        process_id: str,
        circuit_name: str,
        base_netlist: str,
        base_parameters: Dict[str, Any],
        work_dir: Path,
        targets: Dict[str, float] | None = None,
        weights: Dict[str, float] | None = None,
        power_max: float | None = None,
    ) -> OptimizationResult:
        """Run two-stage optimization on a base SPICE netlist.

        Args:
            process_id: ID used for generating per-iteration artifacts.
            circuit_name: Logical circuit name (for logging only).
            base_netlist: SPICE netlist string (unmodified template).
            base_parameters: Non-W/L parameters passed to orchestrator.
            work_dir: Directory where analysis netlists/results are stored.
            targets: Optional dict with keys "current", "gain".
            weights: Optional dict with keys "w1", "w2", "w3".
            power_max: Optional maximum allowed power.
        """
        targets = targets or {}
        weights = weights or {}

        # All SPICE netlists and intermediate artifacts for optimization runs
        # are written into a temporary directory so that nothing persists on
        # disk after the optimization completes.
        with tempfile.TemporaryDirectory(prefix=f"opt_{process_id}_") as tmpdir:
            sim_work_dir = Path(tmpdir)

            variables = extract_wl_variables(base_netlist)
            if not variables:
                logger.warning("No W/L parameters detected in netlist; skipping optimization")
                # Degenerate result: run a single simulation using base netlist.
                metrics, cost = self._evaluate_assignment(
                    process_id + "_base",
                    circuit_name,
                    base_netlist,
                    base_parameters,
                    variables,
                    {name: var.value for name, var in variables.items()},
                    sim_work_dir,
                    targets,
                    weights,
                    power_max,
                )
                return OptimizationResult(
                    best_assignment={name: var.value for name, var in variables.items()},
                    best_metrics=metrics,
                    best_cost=cost,
                    iterations=0,
                    history=[],
                )

            history: List[Dict[str, Any]] = []

            # Stage 1: Coarse search
            coarse_results = self._coarse_search(
                process_id,
                circuit_name,
                base_netlist,
                base_parameters,
                variables,
                sim_work_dir,
                targets,
                weights,
                power_max,
                history,
            )

            best_assignment, best_metrics, best_cost = coarse_results

            # Early exit if cost already good enough
            if self.config.cost_threshold is not None and best_cost <= self.config.cost_threshold:
                return OptimizationResult(
                    best_assignment=best_assignment,
                    best_metrics=best_metrics,
                    best_cost=best_cost,
                    iterations=len(history),
                    history=history,
                )

            # Stage 2: Nelder–Mead local search
            nm_assignment, nm_metrics, nm_cost, nm_iters = self._nelder_mead(
                process_id,
                circuit_name,
                base_netlist,
                base_parameters,
                variables,
                sim_work_dir,
                targets,
                weights,
                power_max,
                best_assignment,
                history,
            )

            # Choose the better of coarse vs local optimum
            if nm_cost < best_cost:
                best_assignment, best_metrics, best_cost = nm_assignment, nm_metrics, nm_cost

            return OptimizationResult(
                best_assignment=best_assignment,
                best_metrics=best_metrics,
                best_cost=best_cost,
                iterations=len(history),
                history=history,
            )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _coarse_search(
        self,
        process_id: str,
        circuit_name: str,
        base_netlist: str,
        base_parameters: Dict[str, Any],
        variables: Dict[str, WLVariable],
        work_dir: Path,
        targets: Dict[str, float],
        weights: Dict[str, float],
        power_max: float | None,
        history: List[Dict[str, Any]],
    ) -> Tuple[Dict[str, float], Dict[str, float], float]:
        import random

        names = list(variables.keys())
        best_assignment: Dict[str, float] | None = None
        best_metrics: Dict[str, float] | None = None
        best_cost = float("inf")

        samples = max(self.config.coarse_samples, len(names) * 3)
        logger.info("Starting coarse W/L search: %d samples", samples)

        # Simple random sampling within bounds
        for idx in range(samples):
            candidate = {}
            for name, var in variables.items():
                candidate[name] = random.uniform(var.min_value, var.max_value)

            metrics, cost = self._evaluate_assignment(
                f"{process_id}_c{idx}",
                circuit_name,
                base_netlist,
                base_parameters,
                variables,
                candidate,
                work_dir,
                targets,
                weights,
                power_max,
            )

            history.append({
                "stage": "coarse",
                "iteration": idx,
                "assignment": candidate,
                "metrics": metrics,
                "cost": cost,
            })

            if cost < best_cost:
                best_cost = cost
                best_assignment = candidate
                best_metrics = metrics

        assert best_assignment is not None and best_metrics is not None
        logger.info("Coarse search best cost=%.4g, assignment=%s", best_cost, best_assignment)
        return best_assignment, best_metrics, best_cost

    def _nelder_mead(
        self,
        process_id: str,
        circuit_name: str,
        base_netlist: str,
        base_parameters: Dict[str, Any],
        variables: Dict[str, WLVariable],
        work_dir: Path,
        targets: Dict[str, float],
        weights: Dict[str, float],
        power_max: float | None,
        start_assignment: Dict[str, float],
        history: List[Dict[str, Any]],
    ) -> Tuple[Dict[str, float], Dict[str, float], float, int]:
        """Basic Nelder–Mead simplex search (gradient-free)."""
        alpha, gamma, rho, sigma = 1.0, 2.0, 0.5, 0.5

        names = list(variables.keys())
        n = len(names)
        x0 = vector_from_assignment(variables, start_assignment)

        # Initial simplex: x0 plus unit perturbations
        simplex: List[List[float]] = [x0]
        for i in range(n):
            x = x0.copy()
            step = 0.1 * max(abs(x0[i]), 1.0)
            x[i] = x[i] + step
            simplex.append(x)

        # Cache evaluations to avoid duplicate simulations
        cache: Dict[Tuple[float, ...], Tuple[Dict[str, float], float]] = {}

        def eval_vec(vec: List[float], label: str) -> Tuple[Dict[str, float], float]:
            key = tuple(vec)
            if key in cache:
                return cache[key]
            assignment = assignment_from_vector(variables, vec)
            metrics, cost = self._evaluate_assignment(
                label,
                circuit_name,
                base_netlist,
                base_parameters,
                variables,
                assignment,
                work_dir,
                targets,
                weights,
                power_max,
            )
            cache[key] = (metrics, cost)
            history.append({
                "stage": "local",
                "iteration": len(history),
                "assignment": assignment,
                "metrics": metrics,
                "cost": cost,
            })
            return metrics, cost

        # Evaluate initial simplex
        f_vals: List[float] = []
        metrics_list: List[Dict[str, float]] = []
        for i, x in enumerate(simplex):
            metrics_i, f_i = eval_vec(x, f"{process_id}_nm{i}")
            metrics_list.append(metrics_i)
            f_vals.append(f_i)

        max_iters = self.config.max_iterations
        iters = 0

        while iters < max_iters:
            # Order
            sorted_idx = sorted(range(len(simplex)), key=lambda i: f_vals[i])
            simplex = [simplex[i] for i in sorted_idx]
            f_vals = [f_vals[i] for i in sorted_idx]
            metrics_list = [metrics_list[i] for i in sorted_idx]

            best_cost = f_vals[0]
            if self.config.cost_threshold is not None and best_cost <= self.config.cost_threshold:
                break

            # Convergence check: diameter of simplex
            if max(abs(f - best_cost) for f in f_vals[1:]) < 1e-3:
                break

            # Centroid excluding worst
            x0_vec = [0.0] * n
            for i in range(len(simplex) - 1):
                for j in range(n):
                    x0_vec[j] += simplex[i][j]
            for j in range(n):
                x0_vec[j] /= (len(simplex) - 1)

            worst = simplex[-1]

            # Reflection
            xr = [x0_vec[j] + alpha * (x0_vec[j] - worst[j]) for j in range(n)]
            mr, fr = eval_vec(xr, f"{process_id}_nm_r{iters}")

            if f_vals[0] <= fr < f_vals[-2]:
                simplex[-1] = xr
                f_vals[-1] = fr
                metrics_list[-1] = mr
            elif fr < f_vals[0]:
                # Expansion
                xe = [x0_vec[j] + gamma * (xr[j] - x0_vec[j]) for j in range(n)]
                me, fe = eval_vec(xe, f"{process_id}_nm_e{iters}")
                if fe < fr:
                    simplex[-1] = xe
                    f_vals[-1] = fe
                    metrics_list[-1] = me
                else:
                    simplex[-1] = xr
                    f_vals[-1] = fr
                    metrics_list[-1] = mr
            else:
                # Contraction
                xc = [x0_vec[j] + rho * (worst[j] - x0_vec[j]) for j in range(n)]
                mc, fc = eval_vec(xc, f"{process_id}_nm_c{iters}")
                if fc < f_vals[-1]:
                    simplex[-1] = xc
                    f_vals[-1] = fc
                    metrics_list[-1] = mc
                else:
                    # Shrink
                    best = simplex[0]
                    for i in range(1, len(simplex)):
                        simplex[i] = [best[j] + sigma * (simplex[i][j] - best[j]) for j in range(n)]
                        mi, fi = eval_vec(simplex[i], f"{process_id}_nm_s{iters}_{i}")
                        metrics_list[i] = mi
                        f_vals[i] = fi

            iters += 1

        # Return best point found
        best_idx = min(range(len(simplex)), key=lambda i: f_vals[i])
        best_vec = simplex[best_idx]
        best_assignment = assignment_from_vector(variables, best_vec)
        best_metrics = metrics_list[best_idx]
        best_cost = f_vals[best_idx]
        return best_assignment, best_metrics, best_cost, iters

    def _evaluate_assignment(
        self,
        iter_id: str,
        circuit_name: str,
        base_netlist: str,
        base_parameters: Dict[str, Any],
        variables: Dict[str, WLVariable],
        assignment: Dict[str, float],
        work_dir: Path,
        targets: Dict[str, float],
        weights: Dict[str, float],
        power_max: float | None,
    ) -> Tuple[Dict[str, float], float]:
        """Evaluate one W/L assignment by running the ngspice pipeline.

        On any simulation failure, returns a large penalty cost.
        """
        work_dir.mkdir(parents=True, exist_ok=True)

        try:
            # 1) Mutate the base netlist with this assignment
            mutated = apply_wl_assignment(base_netlist, assignment)

            # 2) Build DC/AC/TRAN analysis netlists using the orchestrator
            analysis_paths = AnalysisOrchestrator.create_analysis_sequence(
                iter_id,
                circuit_name,
                base_parameters,
                work_dir,
                circuit_netlist=mutated,
            )

            # 3) Run ngspice
            sim_results = NgSpiceExecutor.run_analysis_sequence(
                analysis_paths["dc"],
                analysis_paths["ac"],
                analysis_paths["transient"],
                work_dir,
            )

            if not sim_results.get("success", False):
                logger.warning("Simulation failed for %s: %s", iter_id, sim_results.get("errors"))
                # High penalty cost on failure; zero metrics
                return {"current": 0.0, "gain": 0.0, "power": 0.0}, 1e9

            metrics = self._extract_primary_metrics(sim_results)
            cost = compute_cost(metrics, targets, weights, power_max)
            return metrics, cost

        except Exception as exc:  # Robustness: never crash the outer pipeline
            logger.error("Optimization evaluation failed for %s: %s", iter_id, exc)
            return {"current": 0.0, "gain": 0.0, "power": 0.0}, 1e9

    @staticmethod
    def _extract_primary_metrics(sim_results: Dict[str, Any]) -> Dict[str, float]:
        """Heuristically derive current / gain / power from analysis outputs."""
        op = sim_results.get("operating_point", {}) or {}
        ac = sim_results.get("ac_analysis", {}) or {}

        # Current: prefer explicit measurement nodes if present
        current_keys_priority = [
            "i_vmeas",
            "i_rload",
            "i_i1",
            "i_iref",
            "i_vdd",
        ]
        current = 0.0
        for key in current_keys_priority:
            if key in op:
                current = float(op[key])
                break
        else:
            for k, v in op.items():
                if k.startswith("i_"):
                    current = float(v)
                    break

        gain = float(ac.get("gain_db", 0.0))

        # Power: try supply V * I if we have it
        vdd = op.get("v_vdd") or op.get("v_vdd!", 1.8)
        power = abs(float(vdd)) * abs(float(op.get("i_vdd", current))) if op else 0.0

        return {
            "current": float(current),
            "gain": gain,
            "power": float(power),
        }
