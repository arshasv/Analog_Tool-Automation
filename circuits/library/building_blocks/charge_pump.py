"""
Sky130 Charge Pump Template
Topology: Standard Switched-Current Charge Pump
"""
from circuits.sky130.devices import nmos, pmos, Sky130Constants

class ChargePump:
    """
    Standard Tri-state Charge Pump
    
    Nodes:
    UP, DN - Digital control signals
    VOUT   - Connection to Loop Filter
    VDD    - Supply
    VSS    - Ground
    VBIAS_P, VBIAS_N - Bias voltages for current mirrors
    """
    def __init__(
        self, 
        name: str = "cp",
        i_pump: float = 20e-6,
        w_sw: float = 2.0, l_sw: float = 0.15
    ):
        self.name = name
        self.i_pump = i_pump
        self.w_sw = w_sw
        self.l_sw = l_sw

    def generate_netlist_fragment(self, node_up: str, node_dn: str, node_vout: str, node_vbias_p: str, node_vbias_n: str, node_vdd: str, node_vss: str) -> str:
        spice = f"* Charge Pump {self.name}\n"
        
        # Internal nodes
        node_p_src = f"{self.name}_p_src"
        node_n_src = f"{self.name}_n_src"
        
        # 1. PMOS Current Source and Switch
        spice += f"XM_p_curr {node_p_src} {node_vbias_p} {node_vdd} {node_vdd} sky130_fd_pr__pfet_01v8 w=20 l=1\n"
        spice += f"XM_p_sw {node_vout} {node_up} {node_p_src} {node_vdd} sky130_fd_pr__pfet_01v8 w={self.w_sw} l={self.l_sw}\n"
        
        # 2. NMOS Current Source and Switch
        spice += f"XM_n_sw {node_vout} {node_dn} {node_n_src} {node_vss} sky130_fd_pr__nfet_01v8 w={self.w_sw} l={self.l_sw}\n"
        spice += f"XM_n_curr {node_n_src} {node_vbias_n} {node_vss} {node_vss} sky130_fd_pr__nfet_01v8 w=10 l=1\n"
        
        return spice

if __name__ == "__main__":
    cp = ChargePump()
    print(cp.generate_netlist_fragment("up", "dn", "vout", "vbp", "vbn", "1.8", "0"))
