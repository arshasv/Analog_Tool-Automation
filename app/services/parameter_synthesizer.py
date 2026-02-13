"""
Parameter Synthesizer — DRC-safe initial parameter generation

Provides:
  - Sky130 DRC clamp functions
  - Analytical initial sizing from specs
  - Random sampling within DRC-safe bounds
"""
import random
import math
import logging
from typing import Dict, Any, List
from app.services.topology import Topology

logger = logging.getLogger(__name__)

# ── Sky130 DRC Limits ─────────────────────────────────────────────────

SKY130_W_MIN = 0.42e-6   # 0.42 um
SKY130_W_MAX = 50e-6     # 50 um
SKY130_L_MIN = 0.15e-6   # 0.15 um
SKY130_L_MAX = 5e-6      # 5 um
SKY130_I_MIN = 1e-6      # 1 uA
SKY130_I_MAX = 5e-3      # 5 mA
SKY130_C_MIN = 0.1e-12   # 0.1 pF
SKY130_C_MAX = 50e-12    # 50 pF
SKY130_R_MIN = 100       # 100 Ohm
SKY130_R_MAX = 1e6       # 1 MOhm


def clamp_w(x: float) -> float:
    """Clamp width to Sky130 DRC-safe range (in meters)."""
    return max(SKY130_W_MIN, min(x, SKY130_W_MAX))


def clamp_l(x: float) -> float:
    """Clamp length to Sky130 DRC-safe range (in meters)."""
    return max(SKY130_L_MIN, min(x, SKY130_L_MAX))


def clamp_i(x: float) -> float:
    """Clamp current to safe range."""
    return max(SKY130_I_MIN, min(x, SKY130_I_MAX))


def clamp_c(x: float) -> float:
    """Clamp capacitance to safe range."""
    return max(SKY130_C_MIN, min(x, SKY130_C_MAX))


# ── Convenience: values in um for netlist generation ──────────────────

def w_um(x_m: float) -> float:
    return clamp_w(x_m) * 1e6


def l_um(x_m: float) -> float:
    return clamp_l(x_m) * 1e6


# ── Sky130 NMOS/PMOS approximate parameters ──────────────────────────

SKY130_NMOS = {
    "mu_cox": 270e-6,   # uA/V^2 → A/V^2
    "vth": 0.49,        # V (typical tt)
    "lambda": 0.1,      # 1/V (CLM)
}

SKY130_PMOS = {
    "mu_cox": 60e-6,    # A/V^2
    "vth": -0.45,       # V
    "lambda": 0.05,     # 1/V
}


# ── Analytical Initial Sizing ─────────────────────────────────────────

def synthesize_initial_params(
    topology: Topology,
    specs: Dict[str, float],
) -> Dict[str, float]:
    """
    Compute initial W/L/I parameters from specs using first-order equations.

    Specs may include:
      gain_db, ugbw_hz, phase_margin_deg, power_mw, vdd
    """
    vdd = specs.get("vdd", 1.8)
    gain_db = specs.get("gain_db", 40.0)
    gain_lin = 10 ** (gain_db / 20.0)
    ugbw = specs.get("ugbw_hz", 1e6)
    power_mw = specs.get("power_mw", 1.0)
    i_total = (power_mw * 1e-3) / vdd  # total current budget

    params = {}

    # ── Tail current from power budget ────────────────────────────────
    if topology.gain == "two_stage":
        i_tail = i_total * 0.4  # 40% for first stage
        i_out = i_total * 0.5   # 50% for output stage
    else:
        i_tail = i_total * 0.7
        i_out = i_total * 0.2

    i_tail = clamp_i(i_tail)
    i_out = clamp_i(i_out)
    params["i_tail"] = i_tail * 1e6  # in uA for netlist

    # ── Diff pair W/L from gain = gm * Rout ───────────────────────────
    # gm = 2*Id / (Vgs - Vth)  ≈ sqrt(2 * mu_cox * (W/L) * Id)
    # For required gain: gm ≈ gain * gds ≈ gain * lambda * Id
    gm_needed = gain_lin * SKY130_NMOS["lambda"] * (i_tail / 2)
    # gm = sqrt(2 * mu_cox * W/L * Id) → W/L = gm^2 / (2 * mu_cox * Id)
    wl_ratio = (gm_needed ** 2) / (2 * SKY130_NMOS["mu_cox"] * (i_tail / 2))
    wl_ratio = max(1.0, min(wl_ratio, 200.0))

    # Choose L, compute W
    if topology.gain in ("telescopic", "folded"):
        l_diff = 1.0e-6  # longer L for gain
    elif topology.gain == "two_stage":
        l_diff = 0.5e-6
    else:
        l_diff = 0.15e-6  # minimum for speed

    l_diff = clamp_l(l_diff)
    w_diff = clamp_w(wl_ratio * l_diff)

    params["w_diff"] = w_um(w_diff)
    params["l_diff"] = l_um(l_diff)

    # ── Load transistor sizing (PMOS mirror) ──────────────────────────
    pmos_ratio = SKY130_NMOS["mu_cox"] / SKY130_PMOS["mu_cox"]  # ~4.5x
    w_load = clamp_w(w_diff * pmos_ratio)
    l_load = l_diff
    params["w_load"] = w_um(w_load)
    params["l_load"] = l_um(l_load)

    # ── Bias transistor sizing ────────────────────────────────────────
    params["w_bias"] = w_um(clamp_w(2e-6))
    params["l_bias"] = l_um(clamp_l(1e-6))

    # ── Output stage (if two-stage or classAB) ────────────────────────
    if topology.gain == "two_stage" or topology.output in ("source_follower", "classAB"):
        # Output stage needs larger W for drive strength
        # UGBW ≈ gm_out / (2π * CL), CL ~ 5pF
        cl = 5e-12
        gm_out = 2 * math.pi * ugbw * cl
        wl_out = (gm_out ** 2) / (2 * SKY130_NMOS["mu_cox"] * i_out)
        wl_out = max(2.0, min(wl_out, 300.0))
        w_out = clamp_w(wl_out * 0.5e-6)
        params["w_out"] = w_um(w_out)
        params["l_out"] = l_um(0.5e-6)
        params["i_out"] = i_out * 1e6  # uA

    # ── Compensation cap (Miller) ─────────────────────────────────────
    if topology.comp == "miller":
        # Cc > gm1 / (2π * UGBW) for dominant pole placement
        # Typical: Cc = 0.2 * CL to CL
        cc = max(0.5e-12, min(5e-12, cl * 0.3 if 'cl' in dir() else 1e-12))
        params["cc"] = cc * 1e12  # in pF

    # ── Cascode transistor sizing ─────────────────────────────────────
    if topology.gain in ("telescopic", "folded") or topology.load == "cascode":
        params["w_casc"] = params["w_diff"]
        params["l_casc"] = params["l_diff"]

    params["vdd"] = vdd
    return params


def random_sample_params(
    topology: Topology,
    specs: Dict[str, float],
    n: int = 5,
) -> List[Dict[str, float]]:
    """
    Generate N random parameter sets within DRC-safe bounds.
    Uses the analytical sizing as center and samples around it.
    """
    center = synthesize_initial_params(topology, specs)
    samples = [center]  # always include the analytical point

    for _ in range(n - 1):
        p = {}
        for key, val in center.items():
            if key == "vdd":
                p[key] = val
                continue
            # Random perturbation: 0.3x to 3x of center value
            factor = random.uniform(0.3, 3.0)
            new_val = val * factor
            # Apply DRC clamps based on key type
            if key.startswith("w_"):
                new_val = w_um(new_val * 1e-6)
            elif key.startswith("l_"):
                new_val = l_um(new_val * 1e-6)
            elif key.startswith("i_"):
                new_val = clamp_i(new_val * 1e-6) * 1e6
            elif key == "cc":
                new_val = clamp_c(new_val * 1e-12) * 1e12
            p[key] = round(new_val, 4)
        samples.append(p)

    return samples
