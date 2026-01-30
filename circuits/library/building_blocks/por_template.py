"""
Sky130 Power-On Reset (POR) Template
Ensures the chip starts in a known state as VDD rises.
"""
from circuits.sky130.devices import nmos, pmos, Sky130Constants

class PowerOnReset:
    """
    Standard Voltage Detector POR
    
    Nodes:
    RST  - Output Reset Signal (Active Low or High depending on config)
    VDD  - Monitored Supply
    VSS  - Ground
    """
    def __init__(self, name: str = "por", threshold_v: float = 1.4):
        self.name = name
        self.threshold = threshold_v

    def generate_netlist_fragment(self, node_rst: str, node_vdd: str, node_vss: str) -> str:
        spice = f"* POR {self.name}\n"
        
        # Internal nodes
        node_div = f"{self.name}_div"
        node_detect = f"{self.name}_detect"
        
        # 1. Voltage Divider (Determines threshold)
        # Using long-channel devices as pseudo-resistors to save area
        spice += f"XM_r1 {node_div} {node_div} {node_vdd} {node_vdd} sky130_fd_pr__pfet_01v8 w=1 l=10\n"
        spice += f"XM_r2 {node_div} {node_div} {node_vss} {node_vss} sky130_fd_pr__nfet_01v8 w=1 l=5\n"
        
        # 2. Threshold Comparator (Behavioral or small CMOS stage)
        # Inverters with specific switching thresholds
        spice += f"XM_inv1_p {node_detect} {node_div} {node_vdd} {node_vdd} sky130_fd_pr__pfet_01v8 w=2 l=1\n"
        spice += f"XM_inv1_n {node_detect} {node_div} {node_vss} {node_vss} sky130_fd_pr__nfet_01v8 w=0.5 l=1\n"
        
        # 3. Buffer stage to output
        spice += f"XM_inv2_p {node_rst} {node_detect} {node_vdd} {node_vdd} sky130_fd_pr__pfet_01v8 w=4 l=0.15\n"
        spice += f"XM_inv2_n {node_rst} {node_detect} {node_vss} {node_vss} sky130_fd_pr__nfet_01v8 w=2 l=0.15\n"
        
        return spice

if __name__ == "__main__":
    por = PowerOnReset()
    print(por.generate_netlist_fragment("reset_b", "vdd", "0"))
