"""8-bit Current Steering DAC Block"""
from app.circuits.primitives import nmos

ROLE = "DAC"
TOPOLOGY_ROLE = "DAC"
PORTS = ["d7", "d6", "d5", "d4", "d3", "d2", "d1", "d0", "iout", "vbias", "gnd"]
DEFAULT_PARAMS = {"i_unit": 1e-6}

def generate_netlist(params: dict) -> str:
    i_unit = params.get("i_unit", 1e-6)
    netlist = ["* 8-bit Binary Weighted Current DAC"]
    
    for bit in range(8):
        # Weight = 2^bit
        multiplier = 2**bit
        netlist.append(f"* Bit {bit} - Multiplicity {multiplier}")
        # Current source (NMOS biased by vbias)
        # Switch (NMOS driven by digital input)
        sw_out = f"sw_{bit}"
        netlist.append(nmos.generate_netlist({"w": 2.0 * multiplier, "l": 1.0}).format(d=sw_out, g="{vbias}", s="{gnd}", b="{gnd}"))
        netlist.append(nmos.generate_netlist({"w": 5.0, "l": 0.15}).format(d="{iout}", g=f"{{d{bit}}}", s=sw_out, b="{gnd}"))
        
    return "\n".join(netlist)
