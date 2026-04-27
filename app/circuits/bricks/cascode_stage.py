"""Cascode Gain Stage Brick"""
from app.circuits.primitives import nmos

ROLE = "GAIN"
PORTS = ["d", "g_vcasc", "in", "s", "b"]
DEFAULT_PARAMS = {"w": 5.0, "l": 0.15, "w_casc": 5.0, "l_casc": 0.15}

def generate_netlist(params: dict) -> str:
    w = params.get("w", 5.0)
    l = params.get("l", 0.15)
    wc = params.get("w_casc", 5.0)
    lc = params.get("l_casc", 0.15)
    
    # Stacked NMOS
    # NMOS 1: Transconductance
    m1 = nmos.generate_netlist({"w": w, "l": l}).format(d="mid", g="{in}", s="{s}", b="{b}")
    # NMOS 2: Cascode
    m2 = nmos.generate_netlist({"w": wc, "l": lc}).format(d="{d}", g="{g_vcasc}", s="mid", b="{b}")
    
    return f"* NMOS Cascode Stage\n{m1}\n{m2}"
