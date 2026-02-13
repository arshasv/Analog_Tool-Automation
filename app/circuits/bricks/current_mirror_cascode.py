"""Cascode Current Mirror Brick"""
from app.circuits.primitives import nmos

ROLE = "LOAD"
PORTS = ["in", "out", "gnd"]
DEFAULT_PARAMS = {"w": 4.0, "l": 1.0}

def generate_netlist(params: dict) -> str:
    w = params.get("w", 4.0)
    l = params.get("l", 1.0)
    
    # NMOS Cascode Mirror (Standard high-swing)
    # M1, M2 are main mirror
    m1 = nmos.generate_netlist({"w": w, "l": l}).format(d="m1d", g="m1d", s="{gnd}", b="{gnd}")
    m2 = nmos.generate_netlist({"w": w, "l": l}).format(d="m2d", g="m1d", s="{gnd}", b="{gnd}")
    # M3, M4 are cascodes
    m3 = nmos.generate_netlist({"w": w, "l": l}).format(d="{in}", g="{in}", s="m1d", b="{gnd}")
    m4 = nmos.generate_netlist({"w": w, "l": l}).format(d="{out}", g="{in}", s="m2d", b="{gnd}")
    
    return f"* NMOS Cascode Current Mirror\n{m1}\n{m2}\n{m3}\n{m4}"
