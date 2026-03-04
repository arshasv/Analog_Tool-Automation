"""Two-Stage Miller Op-Amp Macro"""
from app.circuits.bricks import diff_pair_nmos, current_mirror_simple
from app.circuits.primitives import nmos, pmos, capacitor

ROLE = "GAIN_CORE"
TOPOLOGY_ROLE = "GAIN_CORE"
SUPPORTED_INPUTS = ["diff_n", "diff_p"]
REQUIRES = [] # miller is internal in this basic one

PORTS = ["vin+", "vin-", "vout", "vdd", "gnd"]
DEFAULT_PARAMS = {
    "w_diff": 10.0, "l_diff": 0.5,
    "w_load": 5.0,  "l_load": 0.5,
    "w_out": 20.0,  "l_out": 0.5,
    "cc": 1.0,       # pF (Miller compensation cap)
    "itail": 50.0   # µA (tail current of diff pair)
}

def generate_netlist(params: dict) -> str:
    # 1. First Stage: NMOS Diff Pair
    st1_diff = diff_pair_nmos.generate_netlist({
        "w": params.get("w_diff", 10.0), 
        "l": params.get("l_diff", 0.5)
    }).format(d1="st1_d1", d2="st1_d2", in1="{vin+}", in2="{vin-}", tail="st1_tail", sub="{gnd}")
    
    # 2. First Stage Load: PMOS Current Mirror (Simple)
    # Note: Using bricks if available, but users can use primitives too
    # Let's use PMOS primitives for active load
    m3 = pmos.generate_netlist({"w": params.get("w_load", 5.0), "l": params.get("l_load", 0.5)}).format(d="st1_d1", g="st1_d1", s="{vdd}", b="{vdd}")
    m4 = pmos.generate_netlist({"w": params.get("w_load", 5.0), "l": params.get("l_load", 0.5)}).format(d="st1_d2", g="st1_d1", s="{vdd}", b="{vdd}")
    
    # 3. Tail Current Source (NMOS primitive)
    mtail = nmos.generate_netlist({"w": 5.0, "l": 1.0}).format(d="st1_tail", g="v_bias", s="{gnd}", b="{gnd}")

    # 4. Second Stage: NMOS CS
    m5 = nmos.generate_netlist({"w": params.get("w_out", 20.0), "l": params.get("l_out", 0.5)}).format(d="{vout}", g="st1_d2", s="{gnd}", b="{gnd}")
    m6 = pmos.generate_netlist({"w": params.get("w_out", 20.0), "l": params.get("l_out", 0.5)}).format(d="{vout}", g="v_bias_p", s="{vdd}", b="{vdd}")
    
    # 5. Compensation Capacitor (Primitive)
    cc = capacitor.generate_netlist({"c": params.get("cc", 1e-12)}).format(n1="st1_d2", n2="{vout}")
    
    return f"""* Two-Stage Op-Amp Macro
{st1_diff}
* Stage 1 Active Load
{m3}
{m4}
* Tail Source
{mtail}
* Stage 2
{m5}
{m6}
* Miller Cap
{cc}
"""
