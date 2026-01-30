"""
Sky130 Capacitive DAC (CDAC) Template
Key component for SAR ADCs.
"""
from circuits.sky130.devices import capacitor

class CapacitiveDAC:
    """
    Binary-weighted Capacitive DAC
    
    Nodes:
    VOUT - Analog Output (Summing junction)
    B[N:0] - Digital Control bits
    VREF - High Reference
    VGND - Low Reference
    """
    def __init__(self, name: str = "cdac", num_bits: int = 8, c_unit_ff: float = 1.0):
        self.name = name
        self.bits = num_bits
        self.c_unit = c_unit_ff * 1e-15

    def generate_netlist_fragment(self, node_out: str, nodes_bits: list, node_vref_h: str, node_vref_l: str) -> str:
        spice = f"* {self.bits}-bit CDAC {self.name}\n"
        
        for i in range(self.bits):
            # Binary weighting: 2^i * C_unit
            cap_val = (2**i) * self.c_unit
            cap_name = f"C{self.name}_{i}"
            
            # Internal node between Switch and Cap
            node_sw = f"{self.name}_sw_{i}"
            
            # Capacitor from Summing node to Switch
            spice += f"{cap_name} {node_out} {node_sw} {cap_val}\n"
            
            # Ideal Behavioral Switch (Controlled by digital bit i)
            # Switches between VREF_H (if Bit=1) and VREF_L (if Bit=0)
            spice += f"Sw_{cap_name} {node_sw} {node_vref_h} {node_vref_l} {nodes_bits[i]} behavioral_sw\n"
            
        return spice

if __name__ == "__main__":
    dac = CapacitiveDAC(num_bits=4)
    print(dac.generate_netlist_fragment("vout", ["b3", "b2", "b1", "b0"], "1.8", "0"))
