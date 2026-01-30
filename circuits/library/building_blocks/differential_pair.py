"""
Sky130 Differential Pair - Basic Analog Building Block
"""
from circuits.sky130.devices import nmos, pmos, Sky130Constants
from typing import Dict, Any

class DifferentialPair:
    """
    Standard NMOS Differential Pair with Tail Current Source
    
    Nodes:
    VP - Positive Input
    VN - Negative Input
    OUTP - Positive Output (Drain of M2)
    OUTN - Negative Output (Drain of M1)
    VDD - Supply
    VSS - Ground / Tail Source
    """
    def __init__(
        self, 
        name: str = "diff_pair",
        width: float = 5.0, 
        length: float = 0.5,
        tail_current: float = 20e-6
    ):
        self.name = name
        self.width = width
        self.length = length
        self.tail_current = tail_current
        
        # Differential pair transistors
        self.m1 = nmos(name=name+"_m1", width=width, length=length)
        self.m2 = nmos(name=name+"_m2", width=width, length=length)
        
        # Tail current source (ideal for now, but can be replaced by another NMOS)
        self.itail_name = name + "_itail"

    def generate_netlist_fragment(self, node_vp: str, node_vn: str, node_outp: str, node_outn: str, node_vdd: str, node_vss: str) -> str:
        """
        Generate netlist fragment for the diff pair.
        Assumes OUTP/OUTN are connected to loads (e.g. resistors or current mirrors)
        """
        tail_node = self.name + "_tail"
        
        spice = f"* Differential Pair {self.name}\n"
        # M1: Drain=OUTN, Gate=VP, Source=Tail, Bulk=VSS
        spice += self.m1.to_spice(node_outn, node_vp, tail_node, node_vss) + "\n"
        # M2: Drain=OUTP, Gate=VN, Source=Tail, Bulk=VSS
        spice += self.m2.to_spice(node_outp, node_vn, tail_node, node_vss) + "\n"
        
        # Tail Current Source
        spice += f"I{self.itail_name} {tail_node} {node_vss} DC {self.tail_current}\n"
        
        return spice

if __name__ == "__main__":
    dp = DifferentialPair(width=10, length=1, tail_current=50e-6)
    print(dp.generate_netlist_fragment("vin_p", "vin_n", "vout_p", "vout_n", "vdd", "0"))
