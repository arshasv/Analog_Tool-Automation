"""
Sky130 Switch and Capacitor - Basic Analog Building Block
"""
from circuits.sky130.devices import nmos, pmos, Sky130Constants

class TransmissionGate:
    """
    Standard Transmission Gate (NMOS + PMOS)
    
    Nodes:
    IN   - Input
    OUT  - Output
    CTR  - Control Signal (Active High for NMOS)
    CTRB - Complementary Control (Active Low for PMOS)
    """
    def __init__(self, name: str = "tg", width_n: float = 2.0, width_p: float = 4.0, length: float = 0.15):
        self.name = name
        self.mn = nmos(name=name+"_n", width=width_n, length=length)
        self.mp = pmos(name=name+"_p", width=width_p, length=length)

    def generate_netlist_fragment(self, node_in: str, node_out: str, node_ctr: str, node_ctrb: str, node_vss: str, node_vdd: str) -> str:
        spice = f"* Transmission Gate {self.name}\n"
        # NMOS: Drain=IN, Gate=CTR, Source=OUT, Bulk=VSS
        spice += self.mn.to_spice(node_in, node_ctr, node_out, node_vss) + "\n"
        # PMOS: Drain=IN, Gate=CTRB, Source=OUT, Bulk=VDD
        spice += self.mp.to_spice(node_in, node_ctrb, node_out, node_vdd) + "\n"
        return spice

class SwitchedCapacitor:
    """
    Basic Switched Capacitor stage (One switch + One Cap)
    Often used in integrators or filters.
    """
    def __init__(self, name: str = "sc", switch_w: float = 2.0, cap_val_pf: float = 1.0):
        self.name = name
        self.sw = nmos(name=name+"_sw", width=switch_w, length=0.15)
        self.cap_val = cap_val_pf * 1e-12

    def generate_netlist_fragment(self, node_in: str, node_out: str, node_phi1: str, node_vss: str) -> str:
        spice = f"* Switched Cap {self.name}\n"
        # Switch
        spice += self.sw.to_spice(node_in, "mid", node_phi1, node_vss) + "\n"
        # Capacitor (Ideal for now, but can be replaced by Sky130 mimcap)
        spice += f"C{self.name} mid {node_vss} {self.cap_val}\n"
        return spice

if __name__ == "__main__":
    tg = TransmissionGate()
    print(tg.generate_netlist_fragment("in", "out", "phi", "phi_b", "0", "1.8"))
