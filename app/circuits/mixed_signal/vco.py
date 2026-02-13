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
    
    netlist = ["* VCO Ring Oscillator"]
    for i in range(stages):
        inp = f"n{i}"
        out = f"n{(i+1)%stages}"
        # In this simple VCO, vctrl could be supply or bias. 
        # Here we assume it's a starvation VCO where vctrl is supply for inverters
        netlist.append(f"* Stage {i}")
        netlist.append(nmos.generate_netlist({"w": params.get("w_n", 1.0), "l": 0.15}).format(d=out, g=inp, s="{gnd}", b="{gnd}"))
        netlist.append(pmos.generate_netlist({"w": params.get("w_p", 2.0), "l": 0.15}).format(d=out, g=inp, s="{vctrl}", b="{vctrl}"))
    
    netlist.append(f".alias {{vout}}=n0")
    return "\n".join(netlist)
