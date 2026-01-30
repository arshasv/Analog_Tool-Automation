"""
Sky130 Low-Dropout Regulator (LDO) Template
Topology: Error Amp + PMOS Pass Transistor + Resistive Feedback
"""
from circuits.sky130.devices import nmos, pmos, Sky130Constants

class LDORegulator:
    """
    Standard PMOS LDO
    
    Nodes:
    VIN  - Unregulated Input Power
    VOUT - Regulated Output Power
    VREF - Reference Voltage (usually from Bandgap)
    VSS  - Ground
    """
    def __init__(
        self, 
        name: str = "ldo",
        w_pass: float = 1000.0, l_pass: float = 0.5,
        r1: float = 20e3, r2: float = 10e3,
        c_load_pf: float = 1.0
    ):
        self.name = name
        self.w_pass = w_pass
        self.l_pass = l_pass
        self.r1 = r1
        self.r2 = r2
        self.c_load = c_load_pf * 1e-12

    def generate_netlist_fragment(self, node_vin: str, node_vout: str, node_vref: str, node_vss: str) -> str:
        spice = f"* LDO Regulator {self.name}\n"
        
        # Internal nodes
        node_fb = f"{self.name}_fb"
        node_gate = f"{self.name}_gate"
        
        # 1. Error Amplifier
        # We can use an E-source (VCVS) for behavioral simulation or a real OpAmp
        # Gain of ~60dB (1000)
        spice += f"Eamp_{self.name} {node_gate} {node_vss} {node_vref} {node_fb} 1000\n"
        
        # 2. PMOS Pass Transistor (Huge device for high current)
        # Using mult to handle layout and finger counts properly in the future
        spice += f"XPass_{self.name} {node_vout} {node_gate} {node_vin} {node_vin} sky130_fd_pr__pfet_01v8 w={self.w_pass} l={self.l_pass}\n"
        
        # 3. Feedback Divider
        spice += f"R1_{self.name} {node_vout} {node_fb} {self.r1}\n"
        spice += f"R2_{self.name} {node_fb} {node_vss} {self.r2}\n"
        
        # 4. Filter Capacitor
        spice += f"Cload_{self.name} {node_vout} {node_vss} {self.c_load}\n"
        
        return spice

if __name__ == "__main__":
    ldo = LDORegulator()
    print(ldo.generate_netlist_fragment("vin", "vout", "vref", "0"))
