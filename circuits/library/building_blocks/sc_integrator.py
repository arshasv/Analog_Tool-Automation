"""
Sky130 Switched-Capacitor Integrator template
Key building block for Delta-Sigma Modulators and Filters.
"""
from circuits.sky130.devices import nmos, pmos, Sky130Constants

class SC_Integrator:
    """
    Standard Parasitic-Insensitive SC Integrator
    
    Nodes:
    VIN  - Input Signal
    VOUT - Output Signal
    PHI1, PHI2 - Non-overlapping Clocks
    VREF - Reference / Common Mode
    """
    def __init__(
        self, 
        name: str = "sc_int",
        c_inst_pf: float = 1.0,
        c_int_pf: float = 5.0,
        sw_w: float = 2.0
    ):
        self.name = name
        self.cs = c_inst_pf * 1e-12
        self.ci = c_int_pf * 1e-12
        self.sw_w = sw_w

    def generate_netlist_fragment(self, node_vin: str, node_vout: str, node_phi1: str, node_phi2: str, node_vref: str, node_vss: str, node_vdd: str) -> str:
        spice = f"* SC Integrator {self.name}\n"
        
        # Internal nodes
        node_1 = f"{self.name}_n1"
        node_2 = f"{self.name}_n2"
        node_sum = f"{self.name}_sum" # Op-Amp virtual ground
        
        # Switches (Using Transmission Gates for wide signal swing)
        # S1 (Phi1): Vin to Node 1
        spice += f"XM_s1_p {node_vin} {node_phi1} {node_1} {node_vdd} sky130_fd_pr__pfet_01v8 w={self.sw_w*2} l=0.15\n"
        spice += f"XM_s1_n {node_vin} {node_phi1} {node_1} {node_vss} sky130_fd_pr__nfet_01v8 w={self.sw_w} l=0.15\n"
        
        # Sampling Capacitor
        spice += f"Csample_{self.name} {node_1} {node_2} {self.cs}\n"
        
        # S2 (Phi2): Node 1 to Vref
        spice += f"XM_s2_n {node_1} {node_phi2} {node_vref} {node_vss} sky130_fd_pr__nfet_01v8 w={self.sw_w} l=0.15\n"
        
        # S3 (Phi1): Node 2 to Vref
        spice += f"XM_s3_n {node_2} {node_phi1} {node_vref} {node_vss} sky130_fd_pr__nfet_01v8 w={self.sw_w} l=0.15\n"
        
        # S4 (Phi2): Node 2 to Summing junction
        spice += f"XM_s4_n {node_2} {node_phi2} {node_sum} {node_vss} sky130_fd_pr__nfet_01v8 w={self.sw_w} l=0.15\n"
        
        # Integrating Capacitor
        spice += f"Cint_{self.name} {node_sum} {node_vout} {self.ci}\n"
        
        # Ideal Op-Amp (Behavioral)
        spice += f"Eop_{self.name} {node_vout} {node_vref} {node_vref} {node_sum} 10000\n"
        
        return spice

if __name__ == "__main__":
    sci = SC_Integrator()
    print(sci.generate_netlist_fragment("vin", "vout", "phi1", "phi2", "0.9", "0", "1.8"))
