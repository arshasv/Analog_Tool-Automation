"""Cross-Coupled Level Shifter Block"""
from app.circuits.primitives import nmos, pmos

ROLE = "IO"
TOPOLOGY_ROLE = "LEVEL_SHIFTER"
PORTS = ["in", "vout", "vddl", "vddh", "gnd"]
DEFAULT_PARAMS = {"w_n": 1.0, "w_p": 2.0}

def generate_netlist(params: dict) -> str:
    wn = params.get("w_n", 1.0)
    wp = params.get("w_p", 2.0)
    
    # Complementary input generator (Inverter on VDDL)
    inv_n = nmos.generate_netlist({"w": wn, "l": 0.15}).format(d="in_b", g="{in}", s="{gnd}", b="{gnd}")
    inv_p = pmos.generate_netlist({"w": wp, "l": 0.15}).format(d="in_b", g="{in}", s="{vddl}", b="{vddl}")
    
    # Level shifter core (Cross-coupled on VDDH)
    ls_n1 = nmos.generate_netlist({"w": wn, "l": 0.15}).format(d="out_b", g="{in}", s="{gnd}", b="{gnd}")
    ls_n2 = nmos.generate_netlist({"w": wn, "l": 0.15}).format(d="{vout}", g="in_b", s="{gnd}", b="{gnd}")
    
    ls_p1 = pmos.generate_netlist({"w": wp, "l": 0.15}).format(d="out_b", g="{vout}", s="{vddh}", b="{vddh}")
    ls_p2 = pmos.generate_netlist({"w": wp, "l": 0.15}).format(d="{vout}", g="out_b", s="{vddh}", b="{vddh}")
    
    return f"* Cross-Coupled Level Shifter\n{inv_n}\n{inv_p}\n{ls_n1}\n{ls_n2}\n{ls_p1}\n{ls_p2}"
