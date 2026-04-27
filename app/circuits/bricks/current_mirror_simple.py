"""Simple Current Mirror Brick"""
from app.circuits.primitives import nmos

ROLE = "LOAD"
PORTS = ["in", "out", "gnd"]
DEFAULT_PARAMS = {"w": 2.0, "l": 0.5}

def generate_netlist(params: dict) -> str:
    w = params.get("w", 2.0)
    l = params.get("l", 0.5)
    
    # NMOS Current Mirror (assuming NMOS for now)
    m1 = nmos.generate_netlist({"w": w, "l": l}).format(d="{in}", g="{in}", s="{gnd}", b="{gnd}")
    m2 = nmos.generate_netlist({"w": w, "l": l}).format(d="{out}", g="{in}", s="{gnd}", b="{gnd}")
    
    return f"* Simple NMOS Current Mirror\n{m1}\n{m2}"
