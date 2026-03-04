"""Folded Cascode OTA Macro"""
from app.circuits.bricks import diff_pair_nmos
from app.circuits.primitives import nmos, pmos

ROLE = "GAIN_CORE"
TOPOLOGY_ROLE = "GAIN_CORE"
SUPPORTED_INPUTS = ["diff_n"]
REQUIRES = []

PORTS = ["vin+", "vin-", "vout", "vdd", "gnd"]
DEFAULT_PARAMS = {
    "w_diff": 10.0, "l_diff": 0.5,
    "w_casc": 5.0,  "l_casc": 0.5,
    "itail": 100.0  # µA (tail current)
}

def generate_netlist(params: dict) -> str:
    # 1. NMOS Diff Pair
    diff = diff_pair_nmos.generate_netlist({
        "w": params.get("w_diff", 10.0), 
        "l": params.get("l_diff", 0.5)
    }).format(d1="d1", d2="d2", in1="{vin+}", in2="{vin-}", tail="tail", sub="{gnd}")
    
    # 2. PMOS Folding Current Sources (Primitives)
    m3 = pmos.generate_netlist({"w": 10.0, "l": 1.0}).format(d="d1", g="v_gate_p", s="{vdd}", b="{vdd}")
    m4 = pmos.generate_netlist({"w": 10.0, "l": 1.0}).format(d="d2", g="v_gate_p", s="{vdd}", b="{vdd}")
    
    # 3. PMOS Cascode Load
    m5 = pmos.generate_netlist({"w": params.get("w_casc", 5.0), "l": params.get("l_casc", 0.5)}).format(d="out_p", g="v_casc_p", s="d1", b="{vdd}")
    m6 = pmos.generate_netlist({"w": params.get("w_casc", 5.0), "l": params.get("l_casc", 0.5)}).format(d="out_n", g="v_casc_p", s="d2", b="{vdd}")
    
    # 4. NMOS Current Mirror Load (Cascode)
    # Using primitives to build it here for precision
    m7 = nmos.generate_netlist({"w": 5.0, "l": 1.0}).format(d="out_p", g="out_p", s="{gnd}", b="{gnd}")
    m8 = nmos.generate_netlist({"w": 5.0, "l": 1.0}).format(d="out_n", g="out_p", s="{gnd}", b="{gnd}")
    
    return f"""* Folded Cascode OTA Macro
{diff}
{m3} {m4}
{m5} {m6}
{m7} {m8}
.alias {vout}=out_n
"""
