"""NMOS Differential Pair Brick"""
from app.circuits.primitives import nmos

ROLE = "INPUT"
PORTS = ["d1", "d2", "in1", "in2", "tail", "sub"]
DEFAULT_PARAMS = {"w": 5.0, "l": 0.15}

def generate_netlist(params: dict) -> str:
    w = params.get("w", 5.0)
    l = params.get("l", 0.15)
    
    # Instantiate two NMOS primitives
    m1 = nmos.generate_netlist({"w": w, "l": l}).format(d="{d1}", g="{in1}", s="{tail}", b="{sub}")
    m2 = nmos.generate_netlist({"w": w, "l": l}).format(d="{d2}", g="{in2}", s="{tail}", b="{sub}")
    
    return f"* NMOS Diff Pair Brick\n{m1}\n{m2}"
