"""
Sky130 Comparator with Hysteresis
Topology: Diff Pair with Cross-coupled Active Load
"""
from circuits.sky130.devices import nmos, pmos, Sky130Constants

class HysteresisComparator:
    """
    High-speed comparator with built-in hysteresis.
    
    Nodes:
    VP, VN - Inputs
    OUT    - Digital Output
    VDD    - Supply
    VSS    - Ground
    VBIAS  - Bias current control
    """
    def __init__(
        self, 
        name: str = "comp",
        w_diff: float = 10.0, l_diff: float = 0.5,
        w_cross: float = 5.0, l_cross: float = 0.5,
        w_tail: float = 20.0, l_tail: float = 1.0
    ):
        self.name = name
        self.w_diff = w_diff
        self.l_diff = l_diff
        self.w_cross = w_cross
        self.l_cross = l_cross
        self.w_tail = w_tail
        self.l_tail = l_tail

    def generate_netlist_fragment(self, node_vp: str, node_vn: str, node_out: str, node_vbias: str, node_vdd: str, node_vss: str) -> str:
        spice = f"* Comparator {self.name}\n"
        
        # Internal nodes
        node_tail = f"{self.name}_tail"
        node_1 = f"{self.name}_int1"
        node_2 = f"{self.name}_int2"
        
        # 1. Tail Current
        spice += f"XM_tail {node_tail} {node_vbias} {node_vss} {node_vss} sky130_fd_pr__nfet_01v8 w={self.w_tail} l={self.l_tail}\n"
        
        # 2. Input Diff Pair
        spice += f"XM_ip {node_1} {node_vp} {node_tail} {node_vss} sky130_fd_pr__nfet_01v8 w={self.w_diff} l={self.l_diff}\n"
        spice += f"XM_in {node_2} {node_vn} {node_tail} {node_vss} sky130_fd_pr__nfet_01v8 w={self.w_diff} l={self.l_diff}\n"
        
        # 3. Cross-coupled PMOS load (provides Hysteresis)
        # Ratio of Diode-connected vs Cross-coupled determines Hysteresis width
        spice += f"XM_p1 {node_1} {node_1} {node_vdd} {node_vdd} sky130_fd_pr__pfet_01v8 w={self.w_cross} l={self.l_cross}\n"
        spice += f"XM_p2 {node_2} {node_2} {node_vdd} {node_vdd} sky130_fd_pr__pfet_01v8 w={self.w_cross} l={self.l_cross}\n"
        spice += f"XM_h1 {node_1} {node_2} {node_vdd} {node_vdd} sky130_fd_pr__pfet_01v8 w={self.w_cross*0.8} l={self.l_cross}\n"
        spice += f"XM_h2 {node_2} {node_1} {node_vdd} {node_vdd} sky130_fd_pr__pfet_01v8 w={self.w_cross*0.8} l={self.l_cross}\n"
        
        # 4. Output Stage (Simple inverter buffer)
        node_pre = f"{self.name}_pre"
        spice += f"XM_inv1_p {node_pre} {node_2} {node_vdd} {node_vdd} sky130_fd_pr__pfet_01v8 w=4 l=0.15\n"
        spice += f"XM_inv1_n {node_pre} {node_2} {node_vss} {node_vss} sky130_fd_pr__nfet_01v8 w=2 l=0.15\n"
        
        spice += f"XM_inv2_p {node_out} {node_pre} {node_vdd} {node_vdd} sky130_fd_pr__pfet_01v8 w=8 l=0.15\n"
        spice += f"XM_inv2_n {node_out} {node_pre} {node_vss} {node_vss} sky130_fd_pr__nfet_01v8 w=4 l=0.15\n"
        
        return spice

if __name__ == "__main__":
    comp = HysteresisComparator()
    print(comp.generate_netlist_fragment("vin+", "vin-", "vout", "vbias", "1.8", "0"))
