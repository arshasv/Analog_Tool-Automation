"""
Sky130 Ring Oscillator VCO Template
Topology: Current-Starved Inverter Ring
"""
from circuits.sky130.devices import nmos, pmos, Sky130Constants

class RingOscillatorVCO:
    """
    Current-Starved Voltage Controlled Oscillator
    
    Nodes:
    VCTRL  - Input controlling frequency
    VOUT   - Oscillating pulse output
    VDD    - Supply
    VSS    - Ground
    """
    def __init__(
        self, 
        name: str = "vco",
        num_stages: int = 5,
        w_n: float = 2.0, l_n: float = 0.5,
        w_p: float = 4.0, l_p: float = 0.5
    ):
        self.name = name
        self.stages = num_stages # Must be odd
        self.w_n = w_n
        self.l_n = l_n
        self.w_p = w_p
        self.l_p = l_p

    def generate_netlist_fragment(self, node_vctrl: str, node_vout: str, node_vdd: str, node_vss: str) -> str:
        spice = f"* VCO Ring Oscillator {self.name} ({self.stages} stages)\n"
        
        # 1. Bias Stage (V-to-I Converter)
        node_pbias = f"{self.name}_pbias"
        node_nbias = f"{self.name}_nbias"
        
        # NMOS to mirror the control current
        spice += f"XM_bias_n {node_nbias} {node_vctrl} {node_vss} {node_vss} sky130_fd_pr__nfet_01v8 w=2 l=1\n"
        # PMOS Mirror to get top-side starving voltage
        spice += f"XM_bias_p1 {node_pbias} {node_pbias} {node_vdd} {node_vdd} sky130_fd_pr__pfet_01v8 w=4 l=1\n"
        spice += f"XM_bias_p2 {node_pbias} {node_nbias} {node_vss} {node_vss} sky130_fd_pr__nfet_01v8 w=2 l=1\n"
        
        # 2. Inverter Stages
        nodes = [f"{self.name}_n{i}" for i in range(self.stages)]
        
        for i in range(self.stages):
            node_in = nodes[i]
            node_out = nodes[(i + 1) % self.stages]
            # If it's the last stage, connect to output
            if i == self.stages - 1:
                node_out = node_vout
            
            # Current Starved Inverter
            # PMOS Starver
            node_p_st = f"{self.name}_p_st_{i}"
            spice += f"XM_p_st_{i} {node_p_st} {node_pbias} {node_vdd} {node_vdd} sky130_fd_pr__pfet_01v8 w={self.w_p} l={self.l_p}\n"
            # Inverter PMOS
            spice += f"XM_inv_p_{i} {node_out} {node_in} {node_p_st} {node_vdd} sky130_fd_pr__pfet_01v8 w={self.w_p} l={self.l_p}\n"
            # Inverter NMOS
            node_n_st = f"{self.name}_n_st_{i}"
            spice += f"XM_inv_n_{i} {node_out} {node_in} {node_n_st} {node_vss} sky130_fd_pr__nfet_01v8 w={self.w_n} l={self.l_n}\n"
            # NMOS Starver
            spice += f"XM_n_st_{i} {node_n_st} {node_vctrl} {node_vss} {node_vss} sky130_fd_pr__nfet_01v8 w={self.w_n} l={self.l_n}\n"
            
        return spice

if __name__ == "__main__":
    vco = RingOscillatorVCO()
    print(vco.generate_netlist_fragment("vctrl", "vout", "1.8", "0"))
