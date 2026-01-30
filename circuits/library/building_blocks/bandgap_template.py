"""
Sky130 Bandgap Reference Circuit Template
Uses Sky130 PNP Transistors (sky130_fd_pr__pnp_05v5)
"""
from circuits.sky130.devices import nmos, pmos, Sky130Constants

class BandgapReference:
    """
    Standard Bandgap Reference (Kuijk Topology)
    Generates ~1.2V reference stable across temperature.
    
    Nodes:
    VREF - Stable Output Reference
    VDD  - Supply
    VSS  - Ground
    """
    def __init__(
        self, 
        name: str = "bgr",
        r_ptat: float = 10e3,
        r_out: float = 100e3,
        pnp_ratio: int = 8
    ):
        self.name = name
        self.r_ptat = r_ptat
        self.r_out = r_out
        self.n = pnp_ratio

    def generate_netlist_fragment(self, node_vref: str, node_vdd: str, node_vss: str) -> str:
        spice = f"* Bandgap Reference {self.name}\n"
        
        # Subcircuit or direct instantiation of PNPs
        # Sky130 PNP: X1 c b e sky130_fd_pr__pnp_05v5_W0p68L0p68
        # Standard unit PNP
        pnp_model = "sky130_fd_pr__pnp_05v5_W0p68L0p68"
        
        # Internal nodes
        node_va = f"{self.name}_va"
        node_vb = f"{self.name}_vb"
        node_gate = f"{self.name}_pmos_gate"
        
        # 1. Op-Amp (Ideal behavior for template or link to OpAmp class)
        # Using a behavioral E-source as an ideal op-amp to ensure the template works
        spice += f"Eopamp_{self.name} {node_gate} {node_vss} {node_va} {node_vb} 1000\n"
        
        # 2. PMOS Current Sources (Top side)
        # Assuming we use a common gate PMOS to mirror currents
        spice += f"XM1 {node_va} {node_gate} {node_vdd} {node_vdd} sky130_fd_pr__pfet_01v8 w=10 l=2\n"
        spice += f"XM2 {node_vb} {node_gate} {node_vdd} {node_vdd} sky130_fd_pr__pfet_01v8 w=10 l=2\n"
        spice += f"XM3 {node_vref} {node_gate} {node_vdd} {node_vdd} sky130_fd_pr__pfet_01v8 w=20 l=2\n"
        
        # 3. PNP Branch A (Smaller, unit PNP)
        spice += f"XPNP1 {node_vss} {node_vss} {node_va} {pnp_model}\n"
        
        # 4. PNP Branch B (Ratioed PNPs + PTAT Resistor)
        node_vbe2 = f"{self.name}_vbe2"
        spice += f"XPNP2 {node_vss} {node_vss} {node_vbe2} {pnp_model} mult={self.n}\n"
        spice += f"Rptat {node_va} {node_vbe2} {self.r_ptat}\n"
        
        # 5. Output Resistor (To generate Vref = Vbe + I_ptat * R_out)
        spice += f"Rout {node_vref} {node_vss} {self.r_out}\n"
        
        return spice

if __name__ == "__main__":
    bgr = BandgapReference()
    print(bgr.generate_netlist_fragment("vref", "vdd", "0"))
