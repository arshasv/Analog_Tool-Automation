"""
Sky130 Current Mirror Circuit
Demonstrates MOSFET-based analog design with Sky130 PDK
"""
import sys
sys.path.append('/home/eda')

from circuits.sky130.devices import nmos, pmos, Sky130Constants, DeviceType
from typing import Dict, Any


class Sky130CurrentMirror:
    """
    Basic current mirror using Sky130 NMOS transistors
    
    Circuit topology:
    VDD
     |
    REF_CURRENT
     |
     +---[M1]--- (diode-connected)
     |       |
     +---[M2]--- OUT_CURRENT
             |
            GND
    """
    
    def __init__(
        self,
        iref: float = 10e-6,  # Reference current in amperes
        width: float = 1.0,    # Transistor width in micrometers
        length: float = 0.5,   # Transistor length in micrometers
        nf: int = 1,           # Number of fingers
        mirror_ratio: int = 1  # Current mirror ratio (Iout/Iref)
    ):
        """
        Initialize current mirror with Sky130 NMOS devices
        
        Args:
            iref: Reference current (A)
            width: Transistor width (μm)
            length: Transistor length (μm)
            nf: Number of fingers
            mirror_ratio: Output current ratio (M2_width / M1_width)
        """
        self.iref = iref
        self.width = width
        self.length = length
        self.nf = nf
        self.mirror_ratio = mirror_ratio
        
        # Create Sky130 NMOS devices
        self.m1 = nmos(name="1", width=width, length=length, nf=nf)
        self.m2 = nmos(name="2", width=width * mirror_ratio, length=length, nf=nf)
        
        self.circuit_name = "Sky130 Current Mirror"
    
    def calculate_vgs(self) -> float:
        """Estimate VGS for given Iref (simplified square-law model)"""
        # Simplified calculation - actual value comes from simulation
        # ID = (1/2) * μn * Cox * (W/L) * (VGS - VTH)²
        # This is a rough estimate
        vgs_est = Sky130Constants.VTH_NMOS + 0.2  # Typical overdrive ~200mV
        return vgs_est
    
    def generate_netlist(self, output_file: str = "sky130_current_mirror.spice") -> str:
        """Generate SPICE netlist for current mirror"""
        
        vgs_est = self.calculate_vgs()
        
        netlist = f"""* {self.circuit_name}
* Sky130 NMOS Current Mirror
* Reference Current: {self.iref*1e6:.2f} μA
* Mirror Ratio: {self.mirror_ratio}:1

.lib /opt/sky130_pdk/sky130A/libs.tech/ngspice/sky130.lib.spice tt

* Supply
Vdd vdd 0 DC {Sky130Constants.VDD_NOMINAL}

* Reference current source
Iref vdd ref {self.iref}

* Sky130 NMOS transistors
{self.m1.to_spice("ref", "ref", "0", "0")}
{self.m2.to_spice("out", "ref", "0", "0")}

* Load resistor to measure output current
Rload out 0 1k

* Operating point analysis
.op

* DC sweep for characterization
.dc Vdd 0 {Sky130Constants.VDD_NOMINAL} 0.1

* AC analysis  
.ac dec 10 1 1G

.control
run

* Operating point results
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Sky130 Current Mirror - Operating Point"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
print all

* Calculate currents
let iref_actual = @m.xm1.msky130_fd_pr__nfet_01v8[id]
let iout_actual = @m.xm2.msky130_fd_pr__nfet_01v8[id]
let mirror_error = (iout_actual - iref_actual*{self.mirror_ratio})/(iref_actual*{self.mirror_ratio})*100

echo ""
echo "Reference Current (M1): " iref_actual "A"
echo "Output Current (M2):    " iout_actual "A"
echo "Expected Iout:          " iref_actual*{self.mirror_ratio} "A"
echo "Mirror Error:           " mirror_error "%"
echo ""

* Calculate output resistance
let rout = 1/@m.xm2.msky130_fd_pr__nfet_01v8[gds]
echo "Output Resistance:      " rout "Ω"

* Save results
set wr_singlescale
set wr_vecnames
option numdgt=3
wrdata sky130_cm_results.csv iref_actual iout_actual

quit
.endc

.end
"""
        
        # Write netlist
        with open(output_file, "w") as f:
            f.write(netlist)
        
        # Print circuit information
        print(f"✓ Generated {output_file}")
        print(f"\n{self.circuit_name}")
        print(f"━" * 60)
        print(f"Design Parameters:")
        print(f"  Reference Current: {self.iref*1e6:.2f} μA")
        print(f"  Mirror Ratio: {self.mirror_ratio}:1")
        print(f"  Expected Iout: {self.iref * self.mirror_ratio * 1e6:.2f} μA")
        print(f"\nM1 (Reference):")
        print(f"  Type: {self.m1.device_type.value}")
        print(f"  W/L: {self.m1.width:.2f}/{self.m1.length:.2f} μm")
        print(f"  Fingers: {self.m1.nf}")
        print(f"  Area: {self.m1.area():.2f} μm²")
        print(f"\nM2 (Mirror):")
        print(f"  Type: {self.m2.device_type.value}")
        print(f"  W/L: {self.m2.width:.2f}/{self.m2.length:.2f} μm")
        print(f"  Fingers: {self.m2.nf}")
        print(f"  Area: {self.m2.area():.2f} μm²")
        print(f"\nEstimated VGS: {vgs_est:.3f} V")
        print(f"━" * 60)
        
        return output_file


class Sky130PMOSCurrentMirror:
    """PMOS current mirror variant"""
    
    def __init__(self, iref: float = 10e-6, width: float = 2.0, length: float = 0.5, mirror_ratio: int = 1):
        self.iref = iref
        self.m1 = pmos(name="1", width=width, length=length)
        self.m2 = pmos(name="2", width=width * mirror_ratio, length=length)
        self.mirror_ratio = mirror_ratio
    
    def generate_netlist(self, output_file: str = "sky130_pmos_cm.spice") -> str:
        """Generate PMOS current mirror netlist"""
        netlist = f"""* Sky130 PMOS Current Mirror

.lib /opt/sky130_pdk/sky130A/libs.tech/ngspice/sky130.lib.spice tt

Vdd vdd 0 DC {Sky130Constants.VDD_NOMINAL}
Iref ref 0 {self.iref}

{self.m1.to_spice("ref", "ref", "vdd", "vdd")}
{self.m2.to_spice("out", "ref", "vdd", "vdd")}

Rload out 0 1k

.op
.control
run
print all
quit
.endc
.end
"""
        with open(output_file, "w") as f:
            f.write(netlist)
        print(f"✓ Generated {output_file} (PMOS variant)")
        return output_file


def main():
    """Main execution"""
    
    # Create NMOS current mirror: 10μA reference, 1:1 ratio
    cm = Sky130CurrentMirror(
        iref=10e-6,      # 10 μA
        width=2.0,       # 2 μm
        length=0.5,      # 0.5 μm (L > Lmin for good matching)
        nf=1,
        mirror_ratio=1
    )
    
    netlist = cm.generate_netlist()
    print(f"\nTo simulate: ngspice {netlist}")
    
    print("\n" + "="*60)
    
    # Create 1:4 current mirror
    cm_ratio = Sky130CurrentMirror(
        iref=10e-6,
        width=2.0,
        length=0.5,
        mirror_ratio=4  # 4x current multiplication
    )
    
    netlist2 = cm_ratio.generate_netlist("sky130_current_mirror_4x.spice")
    print(f"\nTo simulate: ngspice {netlist2}")


if __name__ == "__main__":
    main()
