"""
Sky130 Gain Stage - Basic Analog Building Block
"""
from circuits.sky130.devices import nmos, pmos, Sky130Constants

class GainStage:
    """
    Common Source Gain Stage with PMOS Active Load
    
    Nodes:
    IN   - Input Signal
    OUT  - Output Signal
    VBIAS - Bias voltage for PMOS load
    VDD  - Supply
    VSS  - Ground
    """
    def __init__(
        self, 
        name: str = "gain_stage",
        w_nmos: float = 10.0, 
        l_nmos: float = 1.0,
        w_pmos: float = 20.0,
        l_pmos: float = 1.0
    ):
        self.name = name
        self.mn = nmos(name=name+"_n", width=w_nmos, length=l_nmos)
        self.mp = pmos(name=name+"_p", width=w_pmos, length=l_pmos)

    def generate_netlist_fragment(self, node_in: str, node_out: str, node_vbias: str, node_vdd: str, node_vss: str) -> str:
        spice = f"* Gain Stage {self.name}\n"
        # NMOS Driver: Drain=OUT, Gate=IN, Source=VSS, Bulk=VSS
        spice += self.mn.to_spice(node_out, node_in, node_vss, node_vss) + "\n"
        # PMOS Load: Drain=OUT, Gate=VBIAS, Source=VDD, Bulk=VDD
        spice += self.mp.to_spice(node_out, node_vbias, node_vdd, node_vdd) + "\n"
        return spice

if __name__ == "__main__":
    gs = GainStage()
    print(gs.generate_netlist_fragment("vin", "vout", "vbias", "vdd", "0"))
