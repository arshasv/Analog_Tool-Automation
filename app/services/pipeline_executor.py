"""Minimal circuit pipeline executor with architecture synthesis support."""
import asyncio
import logging
import ast
import os
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

from app.models.circuit import CircuitRequest, ProcessState, ProcessStatus
from app.services.analysis_orchestrator import AnalysisOrchestrator, get_circuit_type_from_filename
from app.services.ngspice_executor import NgSpiceExecutor, OptimizationObjectives
from app.core.optimization.optimizer import WLOptimizer

logger = logging.getLogger(__name__)


class PipelineExecutor:
    """Execute circuit pipeline and provide architecture synthesis capabilities."""
    
    # In-memory process storage
    processes = {}
    
    @staticmethod
    def _parse_spice_value(value: Any) -> float:
        """Helper to parse spice values like 10u to 1e-5."""
        if isinstance(value, (int, float)):
            return float(value)
        if not value or not isinstance(value, str):
            return 0.0
        
        trimmed = value.strip().lower()
        if not trimmed:
            return 0.0
            
        multipliers = {
            't': 1e12, 'g': 1e9, 'meg': 1e6, 'k': 1e3,
            'm': 1e-3, 'u': 1e-6, 'n': 1e-9, 'p': 1e-12,
            'f': 1e-15, 'a': 1e-18
        }
        
        # Match number and unit
        import re
        match = re.match(r"^([-+]?\d*\.?\d+(?:[e][-+]?\d+)?)(meg|[tgkmunpfa])?.*$", trimmed)
        if not match:
            try:
                return float(trimmed)
            except ValueError:
                return 0.0
                
        num_part = float(match.group(1))
        unit_part = match.group(2)
        
        if unit_part and unit_part in multipliers:
            return num_part * multipliers[unit_part]
        return num_part

    @staticmethod
    def parse_parameters_from_file(file_path: str) -> Dict[str, Any]:
        """Simple parameter extraction using AST."""
        params = {}
        try:
            with open(file_path, "r") as fh:
                tree = ast.parse(fh.read())
            
            for node in tree.body:
                # Handle PARAMETERS dict
                if isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name):
                    if node.targets[0].id in ("PARAMETERS", "DEFAULT_PARAMS"):
                        if isinstance(node.value, ast.Dict):
                            for k, v in zip(node.value.keys, node.value.values):
                                try:
                                    params[ast.literal_eval(k)] = ast.literal_eval(v)
                                except: pass
                # Handle generate_netlist function signature
                if isinstance(node, ast.FunctionDef) and node.name == "generate_netlist":
                    args = node.args.args
                    defaults = node.args.defaults
                    # zip from the end
                    for arg, default in zip(reversed(args), reversed(defaults)):
                        try:
                            params[arg.arg] = ast.literal_eval(default)
                        except: pass
        except Exception as e:
            logger.warning(f"AST parse failed for {file_path}: {e}")
        return params

    @staticmethod
    def run_circuit_from_file(
        process_id: str,
        file_path: str,
        parameters: Dict[str, Any] = None,
        mode: str = "simulate",
    ):
        """Standard flow: simulate a specific uploaded file with parameters."""
        parameters = parameters or {}
        try:
            # 1. Setup
            out_dir = Path("data/designs")
            out_dir.mkdir(parents=True, exist_ok=True)
            PipelineExecutor.processes[process_id]["status"] = ProcessStatus.RUNNING
            PipelineExecutor.processes[process_id]["progress"] = 5
            
            # 2. Extract info
            circuit_name = Path(file_path).stem
            file_defaults = PipelineExecutor.parse_parameters_from_file(file_path)
            # Merge: File Defaults < User Parameters
            merged_params = {**file_defaults, **parameters}
            # Derived params for ngspice (single-token values to avoid "unknown parameter" errors)
            if "i_tail" in merged_params:
                merged_params["i_tail_A"] = float(merged_params["i_tail"]) * 1e-6
            if "cc" in merged_params:
                merged_params["cc_F"] = float(merged_params["cc"]) * 1e-12
            PipelineExecutor.processes[process_id]["parameters"] = merged_params
            
            # 3. Generate base circuit netlist once
            circuit_block = AnalysisOrchestrator._get_circuit_netlist(file_path, merged_params)

            # Normalise mode and dispatch
            mode_norm = (mode or "simulate").lower()
            if mode_norm not in {"simulate", "optimize"}:
                mode_norm = "simulate"
            PipelineExecutor.processes[process_id]["mode"] = mode_norm

            if mode_norm == "optimize":
                # Split out non-W/L parameters used by higher level analyses
                non_wl_params = {
                    k: v for k, v in merged_params.items()
                    if not str(k).lower().startswith(("w", "l"))
                    and str(k).lower() not in {"width", "length"}
                }

                # Optional optimization targets and weights can be provided
                targets = {
                    "current": float(PipelineExecutor._parse_spice_value(merged_params.get("I_target", merged_params.get("target_current", 0.0)))),
                    "gain": float(PipelineExecutor._parse_spice_value(merged_params.get("gain_target", merged_params.get("target_gain", 0.0)))),
                }
                weights = {
                    "w1": float(merged_params.get("w_current", 1.0) or 1.0),
                    "w2": float(merged_params.get("w_gain", 1.0) or 1.0),
                    "w3": float(merged_params.get("w_power", 1.0) or 1.0),
                }
                power_max = merged_params.get("power_max")
                power_max_val = float(power_max) if power_max is not None else None
                
                # Extract optimization settings from parameters
                epochs = None
                if "epochs" in merged_params:
                    try:
                        epochs = int(merged_params["epochs"])
                    except (ValueError, TypeError):
                        pass

                PipelineExecutor.processes[process_id]["progress"] = 20

                opt_config = None
                if epochs:
                    opt_config = WLOptimizer.config_class(epochs=epochs) if hasattr(WLOptimizer, 'config_class') else None
                
                # We'll use a local config if epochs is provided
                from app.core.optimization.optimizer import OptimizationConfig
                config = OptimizationConfig(epochs=epochs) if epochs else None
                
                optimizer = WLOptimizer(config=config)
                opt_result = optimizer.optimize(
                    process_id=process_id,
                    circuit_name=circuit_name,
                    base_netlist=circuit_block,
                    base_parameters=non_wl_params,
                    work_dir=out_dir,
                    targets=targets,
                    weights=weights,
                    power_max=power_max_val,
                )

                PipelineExecutor.processes[process_id]["progress"] = 100
                PipelineExecutor.processes[process_id]["status"] = ProcessStatus.COMPLETED
                PipelineExecutor.processes[process_id]["results"] = {
                    "mode": "optimize",
                    "best_assignment": opt_result.best_assignment,
                    "optimized_parameters": opt_result.best_assignment,
                    "metrics": opt_result.best_metrics,
                    "best_cost": opt_result.best_cost,
                    "iterations": opt_result.iterations,
                    "history": opt_result.history,
                    # For compatibility with existing consumers that
                    # expect these keys, we leave them as None.
                    "score": None,
                    "checks": {},
                    "netlists": {},
                    "raw_output": {},
                    "plots": [],
                }

                # Also write best point into design memory for future reuse
                try:
                    PipelineExecutor._store_design_memory({
                        "process_id": process_id,
                        "circuit": circuit_name,
                        "topology": {},
                        "parameters": {**non_wl_params, **opt_result.best_assignment},
                        "metrics": opt_result.best_metrics,
                        "score": -opt_result.best_cost,
                    })
                except Exception as e:
                    logger.warning(f"Failed to store optimization design memory: {e}")

            else:
                # 3b. Standard simulate mode: create analysis sequence
                analysis_paths = AnalysisOrchestrator.create_analysis_sequence(
                    process_id, circuit_name, merged_params, out_dir,
                    file_path=file_path
                )
                PipelineExecutor.processes[process_id]["progress"] = 30

                # 4. Run Simulations
                sim_results = NgSpiceExecutor.run_analysis_sequence(
                    analysis_paths["dc"],
                    analysis_paths["ac"],
                    analysis_paths["transient"],
                    out_dir
                )
                PipelineExecutor.processes[process_id]["progress"] = 80

                # 5. Flatten results for fitness computation
                # Combine AC and Transient metrics into a single flat dict
                flat_metrics = {
                    **sim_results.get("operating_point", {}),
                    **sim_results.get("ac_analysis", {}),
                    **sim_results.get("transient_analysis", {})
                }

                # 6. Compute Fitness (Vectorized)
                objs = OptimizationObjectives.create_objectives_from_analysis(sim_results, circuit_name)
                fitness_vector = OptimizationObjectives.compute_fitness(objs, flat_metrics)

                # 7. Finalize
                PipelineExecutor.processes[process_id]["progress"] = 100
                PipelineExecutor.processes[process_id]["status"] = ProcessStatus.COMPLETED
                PipelineExecutor.processes[process_id]["results"] = {
                    "mode": "simulate",
                    "metrics": fitness_vector["metrics"],
                    "score": fitness_vector["score"],
                    "checks": fitness_vector["checks"],
                    "netlists": analysis_paths,
                    "raw_output": sim_results,
                    "plots": sim_results.get("plots", [])
                }
            
            # 7. Design Memory
            try:
                import ast
                with open(file_path, "r") as f:
                    node = ast.parse(f.read())
                topology_info = {}
                for item in node.body:
                    if isinstance(item, ast.Assign) and isinstance(item.targets[0], ast.Name) and item.targets[0].id == "TOPOLOGY":
                        if isinstance(item.value, ast.Dict):
                            # Correct zip and eval for older python compatibility if needed, but literals are safe
                            topology_info = {ast.literal_eval(k): ast.literal_eval(v) for k, v in zip(item.value.keys, item.value.values)}
                
                PipelineExecutor._store_design_memory({
                    "process_id": process_id,
                    "circuit": circuit_name,
                    "topology": topology_info,
                    "parameters": merged_params,
                    "metrics": fitness_vector["metrics"],
                    "score": fitness_vector["score"]
                })
            except Exception as e:
                logger.warning(f"Failed to store design memory: {e}")

        except Exception as e:
            logger.error(f"Pipeline failed for {process_id}: {e}", exc_info=True)
            PipelineExecutor.processes[process_id]["status"] = ProcessStatus.FAILED
            PipelineExecutor.processes[process_id]["errors"].append(str(e))

    @staticmethod
    def run_architecture_search(process_id: str, specs: Dict[str, Any]):
        """Architecture Search Mode: Enumerates topologies and samples parameters."""
        from app.services.topology import enumerate_valid_topologies
        from app.services.parameter_synthesizer import random_sample_params
        from app.services.architecture_synthesizer import ArchitectureSynthesizer
        
        try:
            PipelineExecutor.processes[process_id]["status"] = ProcessStatus.RUNNING
            topologies = enumerate_valid_topologies()
            results_pool = []
            
            total = len(topologies)
            # Limit search to 20 for interactive performance in this version
            search_space = topologies[:20]
            
            for i, topo in enumerate(search_space):
                PipelineExecutor.processes[process_id]["progress"] = int((i / len(search_space)) * 95)
                
                # Coarse sample (N=3 instead of 5 for speed in this demo)
                param_sets = random_sample_params(topo, specs, n=3)
                
                for p_idx, params in enumerate(param_sets):
                    netlist_str = ArchitectureSynthesizer.generate_netlist_string(topo, params)
                    sub_id = f"{process_id}_{i}_{p_idx}"
                    
                    analysis_paths = AnalysisOrchestrator.create_analysis_sequence(
                        sub_id, "search_node", params, Path("data/designs"),
                        circuit_netlist=netlist_str
                    )
                    
                    sim_results = NgSpiceExecutor.run_analysis_sequence(
                        analysis_paths["dc"], analysis_paths["ac"], analysis_paths["transient"]
                    )
                    
                    flat_metrics = {
                        **sim_results.get("operating_point", {}),
                        **sim_results.get("ac_analysis", {}),
                        **sim_results.get("transient_analysis", {})
                    }
                    
                    objs = OptimizationObjectives.create_objectives_from_analysis(sim_results, "generic")
                    fitness = OptimizationObjectives.compute_fitness(objs, flat_metrics)
                    
                    results_pool.append({
                        "topology": topo.as_dict(),
                        "parameters": params,
                        "metrics": fitness["metrics"],
                        "score": fitness["score"]
                    })
                
                # Sort and store top 10
                PipelineExecutor.processes[process_id]["results"] = {
                    "top_candidates": sorted(results_pool, key=lambda x: x["score"], reverse=True)[:10]
                }

            PipelineExecutor.processes[process_id]["status"] = ProcessStatus.COMPLETED
            PipelineExecutor.processes[process_id]["progress"] = 100
            
            # Batch save to memory
            for res in results_pool:
                PipelineExecutor._store_design_memory(res)

        except Exception as e:
            logger.error(f"Arch search failed: {e}", exc_info=True)
            PipelineExecutor.processes[process_id]["status"] = ProcessStatus.FAILED

    @staticmethod
    def _store_design_memory(data: Dict[str, Any]):
        """Persist design points to JSON lines."""
        memory_file = Path("data/results/design_memory.jsonl")
        memory_file.parent.mkdir(parents=True, exist_ok=True)
        with open(memory_file, "a") as f:
            f.write(json.dumps(data) + "\n")
