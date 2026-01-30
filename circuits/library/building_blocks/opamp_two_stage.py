"""
Sky130 Two-Stage Miller Operational Amplifier
Topology: NMOS Input Differential Pair + PMOS Gain Stage + Miller Compensation
"""
from circuits.sky130.devices import nmos, pmos, Sky130Constants

class TwoStageOpAmp:
    """
    Standard Two-Stage Miller Op-Amp
    
    Nodes:
    INP, INN - Differential Inputs
    OUT      - Output
    VDD, VSS - Supply/Ground
    VBIAS    - External bias voltage or bias node
    """
    def __init__(
        self, 
        name: str = "opamp",
        # Stage 1 (Diff Pair)
        w_diff: float = 20.0, l_diff: float = 1.0,
        w_mirror: float = 10.0, l_mirror: float = 1.0,
        # Stage 2 (Gain Stage)
        w_gain_p: float = 40.0, l_gain_p: float = 1.0,
        w_gain_n: float = 20.0, l_gain_n: float = 1.0,
        # Compensation
        cc_pf: float = 2.0, rz_k: float = 1.0
    ):
        self.name = name
        
        # Stage 1: Diff Pair transistors
        self.m1 = nmos(name=name+"_m1", width=w_diff, length=l_diff)
        self.m2 = nmos(name=name+"_m2", width=w_diff, length=l_diff)
        # Stage 1: Active Load (Current Mirror)
        self.m3 = pmos(name=name+"_m3", width=w_mirror, length=l_mirror)
        self.m4 = pmos(name=name+"_m4", width=w_mirror, length=l_mirror)
        
        # Stage 2: PMOS Driver
        self.m5 = pmos(name=name+"_m5", width=w_gain_p, length=l_gain_p)
        # Stage 2: NMOS Load (Current Source)
        self.m6 = nmos(name=name+"_m6", width=w_gain_n, length=l_gain_n)
        
        # Tail Current Source (NMOS)
        self.mtail = nmos(name=name+"_tail", width=w_gain_n, length=l_gain_n)
        
        self.cc = cc_pf * 1e-12
        self.rz = rz_k * 1e3

    def generate_netlist_fragment(self, node_inp: str, node_inn: str, node_out: str, node_vbias: str, node_vdd: str, node_vss: str) -> str:
        spice = f"* Two-Stage Op-Amp {self.name}\n"
        
        # Node Names
        tail_node = f"{self.name}_tail_node"
        stage1_out = f"{self.name}_s1_out"
        inner_node = f"{self.name}_s1_mirror"
        comp_node = f"{self.name}_comp_int"
        
        # --- STAGE 1 ---
        # Tail Current
        spice += self.mtail.to_spice(tail_node, node_vbias, node_vss, node_vss) + "\n"
        # Diff Pair
        spice += self.m1.to_spice(inner_node, node_inp, tail_node, node_vss) + "\n"
        spice += self.m2.to_spice(stage1_out, node_inn, tail_node, node_vss) + "\n"
        # Mirror Load
        spice += self.m3.to_spice(inner_node, inner_node, node_vdd, node_vdd) + "\n"
        spice += self.m4.to_spice(stage1_out, inner_node, node_vdd, node_vdd) + "\n"
        
        # --- STAGE 2 ---
        # Driver
        spice += self.m5.to_spice(node_out, stage1_out, node_vdd, node_vdd) + "\n"
        # Load
        spice += self.m6.to_spice(node_out, node_vbias, node_vss, node_vss) + "\n"
        
        # --- COMPENSATION ---
        spice += f"Cc_{self.name} {stage1_out} {comp_node} {self.cc}\n"
        spice += f"Rz_{self.name} {comp_node} {node_out} {self.rz}\n"
        
        return spice

if __name__ == "__main__":
    amp = TwoStageOpAmp()
    print(amp.generate_netlist_fragment("vin_p", "vin_n", "vout", "vbias", "vdd", "0"))
