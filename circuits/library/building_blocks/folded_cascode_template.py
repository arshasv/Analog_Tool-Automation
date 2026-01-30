"""
Sky130 Folded Cascode OTA Template
High-gain, High-swing OTA architecture.
"""
from circuits.sky130.devices import nmos, pmos, Sky130Constants

class FoldedCascodeOTA:
    """
    NMOS Input Folded Cascode OTA
    
    Nodes:
    INP, INN - Differential Inputs
    OUT      - Output
    VDD, VSS - Supply/Ground
    VBN1, VBN2 - NMOS Bias voltages
    VBP1, VBP2 - PMOS Bias voltages
    """
    def __init__(
        self, 
        name: str = "fc_ota",
        w_in: float = 20.0, l_in: float = 1.0,
        w_cas: float = 10.0, l_cas: float = 1.0
    ):
        self.name = name
        self.w_in = w_in
        self.l_in = l_in
        self.w_cas = w_cas
        self.l_cas = l_cas

    def generate_netlist_fragment(self, node_inp: str, node_inn: str, node_out: str, node_vdd: str, node_vss: str, bias_nodes: dict) -> str:
        spice = f"* Folded Cascode OTA {self.name}\n"
        
        # Internal nodes
        node_tail = f"{self.name}_tail"
        node_1 = f"{self.name}_x1"
        node_2 = f"{self.name}_x2"
        node_cas_p = f"{self.name}_cas_p"
        
        # 1. Input Diff Pair
        spice += f"XM_tail {node_tail} {bias_nodes['vbn1']} {node_vss} {node_vss} sky130_fd_pr__nfet_01v8 w={self.w_in*2} l=1\n"
        spice += f"XM_in_p {node_1} {node_inp} {node_tail} {node_vss} sky130_fd_pr__nfet_01v8 w={self.w_in} l={self.l_in}\n"
        spice += f"XM_in_n {node_2} {node_inn} {node_tail} {node_vss} sky130_fd_pr__nfet_01v8 w={self.w_in} l={self.l_in}\n"
        
        # 2. Folded PMOS Devices (Cascode)
        spice += f"XM_p_top1 {node_1} {bias_nodes['vbp1']} {node_vdd} {node_vdd} sky130_fd_pr__pfet_01v8 w={self.w_cas*2} l=1\n"
        spice += f"XM_p_top2 {node_2} {bias_nodes['vbp1']} {node_vdd} {node_vdd} sky130_fd_pr__pfet_01v8 w={self.w_cas*2} l=1\n"
        
        spice += f"XM_p_cas1 {node_cas_p} {bias_nodes['vbp2']} {node_1} {node_vdd} sky130_fd_pr__pfet_01v8 w={self.w_cas} l={self.l_cas}\n"
        spice += f"XM_p_cas2 {node_out} {bias_nodes['vbp2']} {node_2} {node_vdd} sky130_fd_pr__pfet_01v8 w={self.w_cas} l={self.l_cas}\n"
        
        # 3. NMOS Current Mirror Load (Cascode)
        node_cas_n = f"{self.name}_cas_n"
        spice += f"XM_n_cas1 {node_cas_p} {bias_nodes['vbn2']} {node_cas_n} {node_vss} sky130_fd_pr__nfet_01v8 w={self.w_cas} l={self.l_cas}\n"
        spice += f"XM_n_cas2 {node_out} {bias_nodes['vbn2']} {node_cas_n} {node_vss} sky130_fd_pr__nfet_01v8 w={self.w_cas} l={self.l_cas}\n"
        
        spice += f"XM_n_bot {node_cas_n} {node_cas_p} {node_vss} {node_vss} sky130_fd_pr__nfet_01v8 w={self.w_cas*2} l=1\n"
        
        return spice

if __name__ == "__main__":
    ota = FoldedCascodeOTA()
    biases = {"vbn1": "0.7", "vbn2": "0.4", "vbp1": "1.1", "vbp2": "1.4"}
    print(ota.generate_netlist_fragment("vin+", "vin-", "vout", "1.8", "0", biases))
