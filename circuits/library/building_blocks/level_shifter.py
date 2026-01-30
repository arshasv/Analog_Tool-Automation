"""
Sky130 Level Shifter Template
Converts logic levels from Core (e.g. 1.8V) to IO (e.g. 3.3V/5V) domains.
"""
from circuits.sky130.devices import nmos, pmos, Sky130Constants

class LevelShifter:
    """
    Standard Cross-coupled Level Shifter
    
    Nodes:
    IN   - Input (Logic Level VDD_LOW)
    OUT  - Output (Logic Level VDD_HIGH)
    VDDL - Supply Low (e.g. 1.8V)
    VDDH - Supply High (e.g. 3.3V or 5V)
    VSS  - Ground
    """
    def __init__(self, name: str = "ls"):
        self.name = name

    def generate_netlist_fragment(self, node_in: str, node_out: str, node_vddl: str, node_vddh: str, node_vss: str) -> str:
        spice = f"* Level Shifter {self.name}\n"
        
        # Internal nodes
        node_in_b = f"{self.name}_in_b"
        node_mid_p = f"{self.name}_mid1"
        node_mid_n = f"{self.name}_mid2"
        
        # 1. Low-voltage Inverter (to get IN and IN_B)
        spice += f"XM_inv_p {node_in_b} {node_in} {node_vddl} {node_vddl} sky130_fd_pr__pfet_01v8 w=1 l=0.15\n"
        spice += f"XM_inv_n {node_in_b} {node_in} {node_vss} {node_vss} sky130_fd_pr__nfet_01v8 w=0.5 l=0.15\n"
        
        # 2. High-voltage Cross-coupled stage
        # Using HV devices if VDDH > 1.8V
        p_model = "sky130_fd_pr__pfet_g5v0d10v5" # Sky130 5V PMOS
        n_model = "sky130_fd_pr__nfet_g5v0d10v5" # Sky130 5V NMOS
        
        # NMOS Drivers
        spice += f"XM_drv1 {node_mid_p} {node_in} {node_vss} {node_vss} {n_model} w=2 l=0.5\n"
        spice += f"XM_drv2 {node_mid_n} {node_in_b} {node_vss} {node_vss} {n_model} w=2 l=0.5\n"
        
        # PMOS Load
        spice += f"XM_load1 {node_mid_p} {node_mid_n} {node_vddh} {node_vddh} {p_model} w=4 l=1\n"
        spice += f"XM_load2 {node_mid_n} {node_mid_p} {node_vddh} {node_vddh} {p_model} w=4 l=1\n"
        
        # 3. Output Buffer
        spice += f"XM_buf_p {node_out} {node_mid_n} {node_vddh} {node_vddh} {p_model} w=8 l=0.5\n"
        spice += f"XM_buf_n {node_out} {node_mid_n} {node_vss} {node_vss} {n_model} w=4 l=0.5\n"
        
        return spice

if __name__ == "__main__":
    ls = LevelShifter()
    print(ls.generate_netlist_fragment("in_1v8", "out_5v", "1.8", "5.0", "0"))
