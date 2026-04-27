"""PMOS Differential Pair Brick"""
from app.circuits.primitives import pmos

ROLE = "INPUT"
PORTS = ["d1", "d2", "in1", "in2", "tail", "sub"]
DEFAULT_PARAMS = {"w": 10.0, "l": 0.5}

def generate_netlist(params: dict) -> str:
    w = params.get("w", 10.0)
    l = params.get("l", 0.5)
    
    m1 = pmos.generate_netlist({"w": w, "l": l}).format(d="{d1}", g="{in1}", s="{tail}", b="{sub}")
    m2 = pmos.generate_netlist({"w": w, "l": l}).format(d="{d2}", g="{in2}", s="{tail}", b="{sub}")
    
    return f"* PMOS Diff Pair Brick\n{m1}\n{m2}"
