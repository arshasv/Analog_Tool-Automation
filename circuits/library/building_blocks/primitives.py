"""
Sky130 MOS Primitives - Single Device Usage
Demonstrates MOS biased in different regions for specific circuit roles.
"""
from circuits.sky130.devices import nmos, pmos, Sky130Constants
from typing import Dict, Any

class MOSPrimitive:
    def __init__(self, name: str, w: float = 1.0, l: float = 0.5):
        self.name = name
        self.w = w
        self.l = l
        self.dev = nmos(name=name, width=w, length=l)

    def current_source(self, vgs: float, vds: float) -> str:
        """MOS biased in Saturation (Strong Inversion)"""
        return f"* Current Source {self.name}\n" + \
               self.dev.to_spice("drain", "gate", "0", "0") + \
               f"\nVgate gate 0 DC {vgs}\n" + \
               f"Vdrain drain 0 DC {vds}"

    def voltage_switch(self, v_on: float) -> str:
        """MOS biased in Triode/Cutoff (Linear region for RDS_ON)"""
        return f"* Switch {self.name}\n" + \
               self.dev.to_spice("out", "ctrl", "in", "0") + \
               f"\nVctrl ctrl 0 DC {v_on}"

    def active_resistor(self, vgs: float) -> str:
        """MOS biased in Deep Triode (Linear Region)"""
        return f"* Lead Resistor {self.name}\n" + \
               self.dev.to_spice("node_a", "gate", "node_b", "node_b") + \
               f"\nVgate gate 0 DC {vgs}"

    def mos_capacitor(self, v_bias: float) -> str:
        """MOS Capacitor (Gate to Source/Drain/Bulk)"""
        return f"* MOS Cap {self.name}\n" + \
               self.dev.to_spice("gate", "bulk", "bulk", "bulk") + \
               f"\nVbias bulk 0 DC {v_bias}"

def generate_primitive_demo():
    m = MOSPrimitive("M1", w=5, l=1)
    print("--- Current Source Mode ---")
    print(m.current_source(vgs=0.8, vds=1.0))
    print("\n--- Switch Mode ---")
    print(m.voltage_switch(v_on=1.8))

if __name__ == "__main__":
    generate_primitive_demo()
