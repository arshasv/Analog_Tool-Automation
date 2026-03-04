"""8-bit Current Steering DAC Block"""
from app.circuits.primitives import nmos, resistor, capacitor

ROLE = "DAC"
TOPOLOGY_ROLE = "DAC"
PORTS = ["d7", "d6", "d5", "d4", "d3", "d2", "d1", "d0", "iout", "vbias", "gnd"]
DEFAULT_PARAMS = {"i_unit": 1.0}  # i_unit is in µA (e.g. 1.0 = 1µA per LSB)

def generate_netlist(params: dict) -> str:
    i_unit = params.get("i_unit", 1.0)  # in µA
    netlist = [
        "* 8-bit Binary Weighted Current DAC",
        "* @AC_SOURCE: Vbias",
        "* @DC_EXPR: i(Vmeas)",
        "* @AC_EXPR: i(Vmeas)",
        "* @TRAN_EXPR: i(Vmeas)",
        "",
        "* Power Supplies",
        "Vdd vdd 0 1.8",
        "Vbias vbias 0 0.9",
        "",
        "* Digital Input Signals (8-bit counter pattern)",
        "Vd7 d7 0 pulse(0 1.8 10n 1n 1n 50n 100n)",
        "Vd6 d6 0 pulse(0 1.8 20n 1n 1n 50n 100n)",
        "Vd5 d5 0 pulse(0 1.8 40n 1n 1n 50n 100n)",
        "Vd4 d4 0 pulse(0 1.8 80n 1n 1n 50n 100n)",
        "Vd3 d3 0 pulse(0 1.8 160n 1n 1n 50n 100n)",
        "Vd2 d2 0 pulse(0 1.8 320n 1n 1n 50n 100n)",
        "Vd1 d1 0 pulse(0 1.8 640n 1n 1n 50n 100n)",
        "Vd0 d0 0 pulse(0 1.8 1280n 1n 1n 50n 100n)",
        "",
        "* Current Sources and Switches",
    ]
    
    for bit in range(8):
        # Weight = 2^bit
        multiplier = 2**bit
        netlist.append(f"* Bit {bit} - Multiplicity {multiplier}")
        
        # Current source transistor (biased by vbias)
        cs_name = f"MCS_{bit}"
        cs_w = multiplier * 2.0  # Scale width for current
        netlist.append(f"{cs_name} cs_{bit} vbias 0 0 nmos w={cs_w}u l=1.0u")
        
        # Switch transistor (controlled by digital input)
        sw_name = f"MSW_{bit}"
        sw_w = 2.0  # Fixed switch size
        netlist.append(f"{sw_name} iout cs_{bit} d{bit} 0 nmos w={sw_w}u l=0.15u")
        
    netlist.extend([
        "",
        "* Measurement and Load",
        "Vmeas iout 0 0",  # Zero-volt source for current measurement
        "Rload iout 0 1k",   # Load resistor
        "Cload iout 0 10p",   # Load capacitor for stability
        "",
        "* Analysis Commands",
        ".dc Vd0 0 1.8 0.1",  # Sweep one input to see step response
        ".ac dec 10 1 100Meg",
        ".tran 1n 200n",
        ".end"
    ])
        
    return "\n".join(netlist)
