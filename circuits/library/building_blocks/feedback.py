"""
Sky130 Feedback Network - Basic Analog Building Block
"""

class ResistiveFeedback:
    """
    Standard Resistive Voltage Divider
    
    Nodes:
    IN   - Input
    FB   - Feedback Node (Output of divider)
    VSS  - Ground
    """
    def __init__(self, name: str = "fb_res", r1_val: float = 10e3, r2_val: float = 10e3):
        self.name = name
        self.r1_val = r1_val
        self.r2_val = r2_val

    def generate_netlist_fragment(self, node_in: str, node_fb: str, node_vss: str) -> str:
        spice = f"* Feedback Network {self.name}\n"
        spice += f"R{self.name}1 {node_in} {node_fb} {self.r1_val}\n"
        spice += f"R{self.name}2 {node_fb} {node_vss} {self.r2_val}\n"
        return spice

class CompensationNetwork:
    """
    RC Miller Compensation Network
    """
    def __init__(self, name: str = "comp", r_val: float = 1e3, c_val_pf: float = 2.0):
        self.name = name
        self.r_val = r_val
        self.c_val = c_val_pf * 1e-12

    def generate_netlist_fragment(self, node_a: str, node_b: str) -> str:
        spice = f"* Miller Compensation {self.name}\n"
        spice += f"R{self.name} {node_a} {self.name}_int {self.r_val}\n"
        spice += f"C{self.name} {self.name}_int {node_b} {self.c_val}\n"
        return spice

if __name__ == "__main__":
    fb = ResistiveFeedback()
    print(fb.generate_netlist_fragment("vout", "vfb", "0"))
