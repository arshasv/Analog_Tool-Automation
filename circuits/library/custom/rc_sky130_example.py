"""
Sky130 RC Circuit Example
Demonstrates integration with Sky130 PDK models
"""
import sys
sys.path.append('/home/eda')

from circuits.sky130.devices import resistor, capacitor, Sky130Constants


class Sky130RCCircuit:
    """RC circuit using Sky130 components"""
    
    def __init__(self, resistance: float = 10e3, capacitance: float = 10e-12):
        """
        Initialize RC circuit with Sky130 devices
        
        Args:
            resistance: Resistance in ohms
            capacitance: Capacitance in farads
        """
        self.resistance = resistance
        self.capacitance = capacitance
        
        # Create Sky130 devices
        self.resistor = resistor(name="1", resistance=resistance)
        self.capacitor = capacitor(name="1", capacitance=capacitance)
        
        self.circuit_name = "Sky130 RC Transient"
    
    def generate_netlist(self, output_file: str = "sky130_rc.spice"):
        """Generate SPICE netlist with Sky130 models"""
        
        netlist = f"""* {self.circuit_name}
* Generated using Sky130 PDK

.lib /opt/sky130_pdk/sky130A/libs.tech/ngspice/sky130.lib.spice tt

* Power supply
Vdd vdd 0 DC {Sky130Constants.VDD_NOMINAL}
Vin vin 0 DC 0 PULSE(0 {Sky130Constants.VDD_NOMINAL} 1n 1n 1n 5u 10u)

* Sky130 Devices
{self.resistor.to_spice("vin", "vout")}
{self.capacitor.to_spice("vout", "0")}

* Analysis
.tran 100n 20u
.control
run
* Write results
set wr_singlescale
set wr_vecnames
option numdgt=3
wrdata sky130_rc_results.csv time v(vin) v(vout)

* Calculate time constant
meas tran tau_meas trig v(vin) val={Sky130Constants.VDD_NOMINAL*0.5} rise=1 targ v(vout) val={Sky130Constants.VDD_NOMINAL*0.63212} rise=1
print tau_meas

* Calculate settling time
meas tran t_settle trig v(vin) val={Sky130Constants.VDD_NOMINAL*0.5} rise=1 targ v(vout) val={Sky130Constants.VDD_NOMINAL*0.95} rise=1
print t_settle

quit
.endc

.end
"""
        
        # Write netlist to file
        with open(output_file, "w") as f:
            f.write(netlist)
        
        # Print device information
        print(f"✓ Generated {output_file}")
        print(f"\nCircuit: {self.circuit_name}")
        print(f"━" * 60)
        print(f"Resistor R1:")
        print(f"  Resistance: {self.resistor.resistance:.2e} Ω")
        print(f"  Dimensions: {self.resistor.width:.2f} × {self.resistor.length:.2f} μm")
        print(f"  Area: {self.resistor.area():.2f} μm²")
        print(f"\nCapacitor C1:")
        print(f"  Capacitance: {self.capacitor.capacitance:.2e} F ({self.capacitor.capacitance*1e12:.2f} pF)")
        print(f"  Dimensions: {self.capacitor.width:.2f} × {self.capacitor.length:.2f} μm")
        print(f"  Area: {self.capacitor.area():.2f} μm²")
        print(f"\nTheoretical τ = RC = {self.resistance * self.capacitance:.2e} s")
        print(f"━" * 60)
        
        return output_file


def main():
    """Main execution"""
    # Create RC circuit with Sky130 devices
    # 10kΩ resistor, 10pF capacitor → τ = 100ns
    rc_circuit = Sky130RCCircuit(resistance=10e3, capacitance=10e-12)
    
    # Generate netlist
    netlist_file = rc_circuit.generate_netlist()
    
    print(f"\nTo simulate: ngspice {netlist_file}")
    

if __name__ == "__main__":
    main()
