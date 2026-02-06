"""
Analog Circuit Design Reasoner
Encodes analog design knowledge and heuristics for faster optimization.
Based on gm/ID methodology (Binkley et al.) and transistor matching theory.
"""
import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class CircuitSpecs:
    """Target specifications for analog circuits"""
    target_gain: Optional[float] = None  # dB or V/V
    target_bandwidth: Optional[float] = None  # Hz
    target_current: Optional[float] = None  # A
    target_stability: Optional[str] = None  # "conservative", "normal", "aggressive"
    supply_voltage: float = 1.8  # V (Sky130 default)
    process: str = "sky130"


class AnalogReasoner:
    """Analog design knowledge and heuristics"""
    
    # Device parameters for Sky130 @ 1.8V
    DEVICE_PARAMS = {
        "nfet": {
            "vth": 0.45,  # V
            "min_W": 0.42,  # µm
            "min_L": 0.15,  # µm
            "max_W": 100.0,  # µm
        },
        "pfet": {
            "vth": -0.45,  # V (magnitude)
            "min_W": 0.84,  # µm (typically 2x nfet)
            "min_L": 0.15,  # µm
            "max_W": 100.0,  # µm
        }
    }
    
    @staticmethod
    def estimate_gain_from_gm_id(W: float, L: float, gm_id: float = 10, VDD: float = 1.8) -> float:
        """
        Estimate DC gain using gm/ID methodology.
        Analog circuits follow power-law relationships in W/L.
        
        Args:
            W: Transistor width (µm)
            L: Transistor length (µm)
            gm_id: Transconductance efficiency (mS/A) — typical 8-15 for analog
            VDD: Supply voltage (V)
        
        Returns:
            Estimated DC gain (V/V, linear)
        """
        # Higher W/L ratio → higher gain, but nonlinear relationship
        aspect_ratio = W / L
        
        # Power-law relationship: gain ~ (W/L)^0.6 to (W/L)^0.8
        # Using 0.7 as middle ground
        gain_scaling = aspect_ratio ** 0.7
        
        # gm/ID ∝ gain (simplified)
        estimated_gain = gm_id * gain_scaling * 0.1  # Empirical scaling
        
        return np.clip(estimated_gain, 5, 1000)  # Reasonable bounds
    
    @staticmethod
    def estimate_bandwidth(L: float, C_load: float = 1e-12, freq_type: str = "pole") -> float:
        """
        Estimate -3dB bandwidth from transistor length.
        Shorter channel → higher transconductance → higher bandwidth.
        
        Args:
            L: Transistor length (µm)
            C_load: Load capacitance (F) — default 1pF
            freq_type: "pole" for single-pole or "unity" for unity-gain freq
        
        Returns:
            Estimated bandwidth (Hz)
        """
        # Shorter L → smaller C_gs → higher gm → higher bandwidth
        # Empirical: BW ≈ constant / (L * C_load)
        
        base_freq = 1e9  # 1 GHz at L=0.15µm, C=1pF
        bw = base_freq / (L * C_load * 1e12)
        
        if freq_type == "pole":
            return np.clip(bw, 1e6, 1e10)  # 1MHz to 10GHz
        else:  # unity-gain
            return np.clip(bw * 2, 1e6, 1e10)
    
    @staticmethod
    def stability_margin_check(stage_gain_db: float, bandwidth_hz: float) -> Tuple[bool, str]:
        """
        Quick stability check using loop gain margin heuristic.
        
        Returns:
            (is_stable, message)
        """
        # Gain-bandwidth product
        gbw = (10 ** (stage_gain_db / 20)) * bandwidth_hz
        
        if gbw > 1e10:
            return True, "Stable (GBW >> 1GHz)"
        elif gbw > 1e9:
            return True, "Stable (GBW ~ 1GHz)"
        elif gbw > 100e6:
            return False, "Marginal stability (GBW ~ 100MHz) — add compensation"
        else:
            return False, "Unstable (GBW < 100MHz) — increase gain or reduce BW"
    
    @staticmethod
    def suggest_initial_parameters(circuit_type: str, specs: CircuitSpecs) -> Dict[str, float]:
        """
        Generate good starting point using design equations and heuristics.
        
        Args:
            circuit_type: "current_mirror", "opamp", "ldo", "comparator", etc.
            specs: Target specifications
        
        Returns:
            Dictionary of suggested parameter values
        """
        if circuit_type == "current_mirror":
            # Current mirrors: focus on matching (equal W/L)
            # Longer L → better matching, but lower frequency
            return {
                "W": 5.0,      # µm (balanced)
                "L": 0.5,      # µm (good matching + reasonable freq)
                "iref": specs.target_current or 10e-6,
            }
        
        elif circuit_type == "opamp":
            # Differential pair for opamp input stage
            # Higher W/L → higher gain but lower bandwidth
            target_gain = specs.target_gain or 60  # dB
            
            # Estimate required aspect ratio from gain target
            gain_linear = 10 ** (target_gain / 20)
            required_ratio = (gain_linear / 10) ** (1 / 0.7)  # Invert the power law
            
            return {
                "W_diff": max(5.0, required_ratio * 0.5),  # Differential pair
                "L_diff": 0.5,
                "W_cascode": required_ratio * 0.25,
                "L_cascode": 1.0,  # Longer for better gain
            }
        
        elif circuit_type == "ldo":
            # LDO: emphasis on stability
            return {
                "W_pass": 20.0,    # Large pass transistor
                "L_pass": 0.5,
                "W_ea": 2.0,       # Small error amp
                "L_ea": 0.5,
            }
        
        elif circuit_type == "comparator":
            # Comparator: fast response
            return {
                "W": 10.0,  # Larger W/L for speed
                "L": 0.15,  # Minimum L (fastest)
            }
        
        else:
            # Generic circuit
            return {
                "W": 5.0,
                "L": 0.5,
            }
    
    @staticmethod
    def validate_design_constraints(params: Dict[str, float], warnings: bool = True) -> Tuple[bool, List[str]]:
        """
        Check if design satisfies minimum design rules and heuristics.
        
        Returns:
            (is_valid, list_of_issues)
        """
        issues = []
        
        for key, value in params.items():
            if "W" in key:
                if value < 0.42:  # Sky130 min width
                    issues.append(f"{key}={value:.3f}µm too small (min 0.42µm)")
                if value > 100:
                    issues.append(f"{key}={value:.3f}µm too large (typically < 100µm)")
            
            if "L" in key:
                if value < 0.15:  # Sky130 min length
                    issues.append(f"{key}={value:.3f}µm smaller than min (0.15µm)")
                if value > 10:
                    issues.append(f"{key}={value:.3f}µm very long (> 10µm) — slow")
        
        # Check aspect ratios
        W_keys = [k for k in params.keys() if "W" in k and "L" not in k]
        for W_key in W_keys:
            L_key = W_key.replace("W", "L")
            if L_key in params:
                aspect_ratio = params[W_key] / params[L_key]
                if aspect_ratio > 500:
                    issues.append(f"{W_key}/{L_key}={aspect_ratio:.1f} very high — matching concerns")
                if aspect_ratio < 0.5:
                    issues.append(f"{W_key}/{L_key}={aspect_ratio:.1f} very low — area waste")
        
        is_valid = len(issues) == 0
        return is_valid, issues
    
    @staticmethod
    def suggest_optimization_hints(circuit_type: str, current_params: Dict[str, float]) -> List[str]:
        """
        Provide optimization hints based on current design state.
        """
        hints = []
        
        # Check for common issues
        for key in ["W", "W_diff", "W_ea"]:
            if key in current_params:
                if current_params[key] < 1.0:
                    hints.append(f"Increase {key} for better gain and lower noise")
                elif current_params[key] > 50.0:
                    hints.append(f"Decrease {key} to reduce area and parasitic capacitance")
        
        for key in ["L", "L_diff"]:
            if key in current_params:
                if current_params[key] < 0.2:
                    hints.append(f"Increase {key} slightly for better matching")
                elif current_params[key] > 2.0:
                    hints.append(f"Decrease {key} to improve bandwidth")
        
        return hints


class AnalogConstraintValidator:
    """Validate design constraints and specifications"""
    
    @staticmethod
    def check_gain_bandwidth_tradeoff(
        gain_db: float,
        bandwidth_hz: float,
        circuit_type: str = "opamp"
    ) -> Tuple[bool, str]:
        """
        Check if gain-bandwidth product is feasible.
        
        Typical limits for Sky130:
        - Opamp: GBW < 10MHz
        - Comparator: GBW < 100MHz
        """
        gbw = (10 ** (gain_db / 20)) * bandwidth_hz
        
        limits = {
            "opamp": 10e6,
            "comparator": 100e6,
            "ldo": 1e6,
            "current_mirror": 500e6,
        }
        
        limit = limits.get(circuit_type, 10e6)
        
        if gbw > limit:
            return False, f"GBW {gbw:.2e} exceeds {circuit_type} limit {limit:.2e}"
        else:
            return True, f"GBW {gbw:.2e} within limits"
    
    @staticmethod
    def check_power_constraints(
        current_ma: float,
        supply_voltage: float = 1.8,
        max_power_mw: float = 10.0
    ) -> Tuple[bool, str]:
        """Check if power consumption is within budget"""
        power_mw = current_ma * supply_voltage
        
        if power_mw > max_power_mw:
            return False, f"Power {power_mw:.2f}mW exceeds budget {max_power_mw}mW"
        else:
            return True, f"Power {power_mw:.2f}mW within budget"
