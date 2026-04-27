"""Open-Loop Comparator Macro"""
from app.circuits.bricks import diff_pair_nmos
from app.circuits.primitives import nmos, pmos

ROLE = "INTERFACE"
TOPOLOGY_ROLE = "COMPARATOR"
SUPPORTED_INPUTS = ["diff_n"]
REQUIRES = []

PORTS = ["vin", "vref", "vout", "vdd", "gnd"]
DEFAULT_PARAMS = {"w_diff": 2.0, "l": 0.5}

def generate_netlist(params: dict) -> str:
    # 1. Diff Pair
    diff = diff_pair_nmos.generate_netlist({
        "w": params.get("w_diff", 2.0),
        "l": params.get("l", 0.5)
    }).format(d1="d1", d2="d2", in1="{vin}", in2="{vref}", tail="tail", sub="{gnd}")
    
    # 2. Active Load
    m3 = pmos.generate_netlist({"w": 4.0, "l": 0.5}).format(d="d1", g="d1", s="{vdd}", b="{vdd}")
    m4 = pmos.generate_netlist({"w": 4.0, "l": 0.5}).format(d="d2", g="d1", s="{vdd}", b="{vdd}")
    
    # 3. Output Inverter (for rail-to-rail)
    inv_n = nmos.generate_netlist({"w": 1.0, "l": 0.15}).format(d="{vout}", g="d2", s="{gnd}", b="{gnd}")
    inv_p = pmos.generate_netlist({"w": 2.0, "l": 0.15}).format(d="{vout}", g="d2", s="{vdd}", b="{vdd}")
    
    return f"* Comparator Macro\n{diff}\n{m3}\n{m4}\n{inv_n}\n{inv_p}"
