"""
Sky130 Bias Generator Template
Distributes reference current from a BGR to internal circuit blocks.
"""
from circuits.sky130.devices import nmos, pmos, Sky130Constants

class BiasGenerator:
    """
    Current Distribution Network
    
    Nodes:
    IREF_IN - Input Reference Current (e.g. from Bandgap)
    VBN_OUT[N] - Multiple NMOS Bias voltages
    VBP_OUT[N] - Multiple PMOS Bias voltages
    VDD, VSS - Supply/Ground
    """
    def __init__(self, name: str = "bias_gen", num_outputs: int = 4):
        self.name = name
        self.num_outputs = num_outputs

    def generate_netlist_fragment(self, node_iref: str, nodes_vbn: list, nodes_vbp: list, node_vdd: str, node_vss: str) -> str:
        spice = f"* Bias Generator {self.name}\n"
        
        # Internal master nodes
        node_vbn_mast = f"{self.name}_vbn_master"
        node_vbp_mast = f"{self.name}_vbp_master"
        
        # 1. Master NMOS Mirror (converts Iref to Vbn)
        spice += f"XM_mast_n {node_vbn_mast} {node_vbn_mast} {node_vss} {node_vss} sky130_fd_pr__nfet_01v8 w=5 l=2\n"
        spice += f"I_ref_in {node_vdd} {node_vbn_mast} DC 10u\n" # Placeholder for BGR input
        
        # 2. Master PMOS Mirror (generates Vbp)
        spice += f"XM_mast_p1 {node_vbp_mast} {node_vbp_mast} {node_vdd} {node_vdd} sky130_fd_pr__pfet_01v8 w=10 l=2\n"
        spice += f"XM_mast_p2 {node_vbp_mast} {node_vbn_mast} {node_vss} {node_vss} sky130_fd_pr__nfet_01v8 w=5 l=2\n"
        
        # 3. Distributed Outputs
        for i in range(min(len(nodes_vbn), self.num_outputs)):
            spice += f"XM_vbn_out_{i} {nodes_vbn[i]} {node_vbn_mast} {node_vss} {node_vss} sky130_fd_pr__nfet_01v8 w=5 l=2\n"
            
        for i in range(min(len(nodes_vbp), self.num_outputs)):
            spice += f"XM_vbp_out_{i} {nodes_vbp[i]} {node_vbp_mast} {node_vdd} {node_vdd} sky130_fd_pr__pfet_01v8 w=10 l=2\n"
            
        return spice

if __name__ == "__main__":
    bg = BiasGenerator(num_outputs=2)
    print(bg.generate_netlist_fragment("iref", ["vbn1", "vbn2"], ["vbp1", "vbp2"], "1.8", "0"))
