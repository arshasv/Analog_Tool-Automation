"""Ring Oscillator VCO Macro"""
from app.circuits.primitives import nmos, pmos

ROLE = "VCO"
TOPOLOGY_ROLE = "VCO"
SUPPORTED_INPUTS = ["v_ctrl"]
REQUIRES = []

PORTS = ["vctrl", "vout", "vdd", "gnd"]
DEFAULT_PARAMS = {"stages": 5, "w_n": 1.0, "w_p": 2.0}

def generate_netlist(params: dict) -> str:
    stages = int(params.get("stages", 5))
    if stages % 2 == 0: stages += 1
    
    netlist = [
        "* VCO Ring Oscillator",
        "* @TRAN_EXPR: v(vout)",
        "* @DC_EXPR: v(vout)"
    ]
    for i in range(stages):
        curr_inp = f"node_{i}" if i > 0 else "vnode_osc"
        curr_out = f"node_{i+1}" if i < stages - 1 else "vnode_osc"
        netlist.append(f"* Stage {i}")
        netlist.append(nmos.generate_netlist({"name": f"XMNS_{i}", "w": params.get("w_n", 1.0), "l": 0.15}).format(d=curr_out, g=curr_inp, s="{gnd}", b="{gnd}"))
        netlist.append(pmos.generate_netlist({"name": f"XMPS_{i}", "w": params.get("w_p", 2.0), "l": 0.15}).format(d=curr_out, g=curr_inp, s="{vctrl}", b="{vctrl}"))
    
    netlist.append(f".alias {{vout}}=vnode_osc")
    return "\n".join(netlist)
