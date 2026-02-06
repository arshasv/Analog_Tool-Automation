"""
Circuit Reasoning Engine
Autonomous constraint solver for circuit optimization.
Given a design spec and current performance, proposes next device parameters.
"""
import logging
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class OptimizationDirection(Enum):
    """Direction of parameter adjustment"""
    INCREASE = 1.0
    DECREASE = -1.0
    HOLD = 0.0


@dataclass
class DesignPoint:
    """A parametric design point"""
    width: float  # µm
    length: float  # µm
    multiplicity: int  # Number of fingers
    
    def __str__(self):
        return f"W={self.width}µm L={self.length}µm M={self.multiplicity}"


@dataclass
class PerformanceMetrics:
    """Extracted from simulation"""
    gm: float  # Transconductance (S)
    gds: float  # Output conductance (S)
    id: float  # Drain current (A)
    vgs: float  # Gate-source voltage (V)
    vds: float  # Drain-source voltage (V)
    power: float  # Power dissipation (W)
    gain_dc: float  # DC voltage gain (V/V)
    gain_db: float  # Gain in dB
    bandwidth: float  # Bandwidth (Hz)
    slew_rate: Optional[float] = None  # V/ns
    phase_margin: Optional[float] = None  # degrees


@dataclass
class CircuitSpec:
    """Design specification"""
    circuit_type: str  # "current_mirror", "amplifier", etc.
    iref: float  # Reference current (A)
    gain_target: float  # Minimum DC gain (V/V)
    bandwidth_target: float  # Minimum BW (Hz)
    power_budget: float  # Maximum power (W)
    vdd: float = 1.8  # Supply voltage (V)
    temperature: float = 27.0  # Temperature (°C)
    margin: float = 1.1  # Safety margin (10% margin = 1.1)


class CircuitReasoner:
    """
    AI-driven circuit reasoning engine.
    
    Strategy:
    1. Parse spec into constraints
    2. Extract performance from simulation
    3. Compute delta (spec - performance)
    4. Solve for device parameters using analytic models
    5. Propose next design point
    6. Iterate until converged or max iterations
    """
    
    def __init__(self, max_iterations: int = 5, tolerance: float = 0.05):
        """
        Initialize reasoner
        
        Args:
            max_iterations: Max optimization loops
            tolerance: Convergence threshold (5%)
        """
        self.max_iterations = max_iterations
        self.tolerance = tolerance
        self.iteration_count = 0
        self.history = []
    
    def reason(
        self,
        spec: CircuitSpec,
        current_performance: PerformanceMetrics,
        current_design: DesignPoint,
        circuit_type: str = "current_mirror"
    ) -> Tuple[Optional[DesignPoint], str]:
        """
        Reason about circuit and propose next design point.
        
        Args:
            spec: Circuit specification
            current_performance: Measured/simulated performance
            current_design: Current W/L/M values
            circuit_type: Type of circuit for type-specific reasoning
        
        Returns:
            (next_design_point, explanation)
        """
        self.iteration_count += 1
        
        # Check convergence
        convergence_status = self._check_convergence(spec, current_performance)
        if convergence_status["converged"]:
            explanation = f"✅ CONVERGED: {convergence_status['reason']}"
            logger.info(f"[Iter {self.iteration_count}] {explanation}")
            return None, explanation
        
        # Type-specific reasoning
        if circuit_type == "current_mirror":
            next_design, reason = self._reason_current_mirror(
                spec, current_performance, current_design
            )
        elif circuit_type == "amplifier":
            next_design, reason = self._reason_amplifier(
                spec, current_performance, current_design
            )
        else:
            next_design, reason = self._reason_generic(
                spec, current_performance, current_design
            )
        
        # Log history
        self.history.append({
            "iteration": self.iteration_count,
            "design": current_design,
            "performance": current_performance,
            "next_design": next_design,
            "reason": reason
        })
        
        logger.info(f"[Iter {self.iteration_count}] {current_design} → {next_design}")
        logger.info(f"  Reason: {reason}")
        
        return next_design, reason
    
    def _check_convergence(self, spec: CircuitSpec, perf: PerformanceMetrics) -> Dict[str, Any]:
        """Check if all specs are met"""
        
        checks = {
            "gain": perf.gain_db >= (20 * (spec.gain_target - 1)),  # Convert V/V to dB
            "power": perf.power <= spec.power_budget,
            "iteration_limit": self.iteration_count >= self.max_iterations
        }
        
        converged = all([checks["gain"], checks["power"]]) or checks["iteration_limit"]
        
        reason = []
        if checks["gain"]:
            reason.append(f"Gain: {perf.gain_db:.1f} dB ≥ {20*(spec.gain_target-1):.1f} dB ✓")
        else:
            reason.append(f"Gain: {perf.gain_db:.1f} dB < {20*(spec.gain_target-1):.1f} dB ✗")
        
        if checks["power"]:
            reason.append(f"Power: {perf.power*1e6:.1f} µW ≤ {spec.power_budget*1e6:.1f} µW ✓")
        else:
            reason.append(f"Power: {perf.power*1e6:.1f} µW > {spec.power_budget*1e6:.1f} µW ✗")
        
        return {
            "converged": converged,
            "reason": " | ".join(reason)
        }
    
    def _reason_current_mirror(
        self,
        spec: CircuitSpec,
        perf: PerformanceMetrics,
        design: DesignPoint
    ) -> Tuple[Optional[DesignPoint], str]:
        """
        Reason for current mirror topology.
        
        Analytic model:
            gm = sqrt(2 * µ_n * Cox * (W/L) * ID)
            ID = IREF (in steady state)
            Power = ID * VDD
        
        Constraint solving:
            If gm is too low → increase W/L ratio
            If power exceeds budget → reduce W/L or use cascode
        """
        
        # Extract targets
        target_gain = spec.gain_target  # V/V
        target_power = spec.power_budget  # W
        current_iref = spec.iref  # A
        
        # Sky130 n-channel FET parameters (typical, tt corner)
        mu_n_cox = 100e-6  # µ_n * C_ox [A/V²]
        
        # Current design performance
        current_gm = perf.gm  # S
        current_power = perf.power  # W
        
        # Compute deltas
        gm_needed = 2 * target_gain / 100  # Rough estimate for gain
        power_available = target_power
        
        # Decision logic
        reasons = []
        delta_w = design.width
        delta_l = design.length
        delta_m = design.multiplicity
        
        # 1. Check power first (hard constraint)
        if current_power > power_available * 0.9:  # 90% utilization
            reasons.append(f"Power {current_power*1e6:.1f}µW > budget {power_available*1e6:.1f}µW")
            # Reduce current: decrease W or increase L
            delta_l = design.length * 1.2
            reasons.append(f"Increase L to {delta_l:.2f}µm to reduce I_D")
        
        # 2. Check gain/gm (soft constraint)
        if current_gm < gm_needed * 0.95:  # 5% margin
            reasons.append(f"gm {current_gm*1e3:.1f}mS < target {gm_needed*1e3:.1f}mS")
            # Increase W/L ratio to boost gm
            delta_w = design.width * 1.3
            reasons.append(f"Increase W to {delta_w:.2f}µm to boost gm")
        
        # 3. If all specs met, try to optimize for power
        if current_power < power_available * 0.5:  # Lots of margin
            reasons.append("Significant power margin, optimizing area...")
            delta_l = design.length * 0.95  # Reduce L slightly for area
        
        # Build next design point
        next_design = DesignPoint(
            width=max(0.5, delta_w),  # Enforce min W = 0.5µm
            length=max(0.15, delta_l),  # Enforce min L = 0.15µm (gate length)
            multiplicity=delta_m
        )
        
        reason_str = " | ".join(reasons) if reasons else "No change needed"
        
        return next_design, reason_str
    
    def _reason_amplifier(
        self,
        spec: CircuitSpec,
        perf: PerformanceMetrics,
        design: DesignPoint
    ) -> Tuple[Optional[DesignPoint], str]:
        """Reason for amplifier topology"""
        
        reasons = []
        delta_w = design.width
        delta_l = design.length
        
        # If gain is low, increase transconductance by increasing W
        if perf.gain_db < 30:
            delta_w = design.width * 1.5
            reasons.append(f"Gain {perf.gain_db:.1f}dB < 30dB target, increase W")
        
        # If phase margin is bad, might need compensation (not W/L tuning)
        if perf.phase_margin and perf.phase_margin < 45:
            reasons.append(f"Phase margin {perf.phase_margin:.1f}° < 45°, needs compensation")
        
        next_design = DesignPoint(
            width=delta_w,
            length=delta_l,
            multiplicity=design.multiplicity
        )
        
        reason_str = " | ".join(reasons) if reasons else "Amplifier specs met"
        return next_design, reason_str
    
    def _reason_generic(
        self,
        spec: CircuitSpec,
        perf: PerformanceMetrics,
        design: DesignPoint
    ) -> Tuple[Optional[DesignPoint], str]:
        """Generic reasoning (fallback)"""
        
        reason = f"Generic scaling: adjusting for {spec.circuit_type}"
        next_design = DesignPoint(
            width=design.width,
            length=design.length,
            multiplicity=design.multiplicity
        )
        return next_design, reason
    
    def get_summary(self) -> str:
        """Get optimization summary"""
        if not self.history:
            return "No optimization history"
        
        summary_lines = [
            f"=== Optimization Summary ({len(self.history)} iterations) ===",
            f"Final design: {self.history[-1]['design']}"
        ]
        
        return "\n".join(summary_lines)
