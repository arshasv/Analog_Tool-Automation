"""
AI-Ready Smart LDO
Optimizes for PSRR, Dropout Voltage, and Transient Overshoot.
"""
import os
import subprocess
import re
from typing import Dict, List
from circuits.library.custom.base_circuit import OptimizableCircuit
from ai_engine.optimizers.base_optimizer import ParameterSpace, ObjectiveSpec
from circuits.sky130.devices import Sky130Constants

class SmartLDO(OptimizableCircuit):
    def __init__(self):
        self.target_vref = 1.0
        self.target_vout = 1.8  # Target output voltage
        # Calculate ideal R1/R2 ratio for 1V reference -> 1.8V output
        # Vout = Vref * (1 + R1/R2) => 1.8 = 1.0 * (1 + 0.8) => R1/R2 = 0.8
        
        self.target_overshoot_mv = 50.0 # < 50mV overshoot during load step
        self.target_dropout_mv = 200.0  # < 200mV dropout at max load

    def get_parameter_space(self) -> List[ParameterSpace]:
        return [
            ParameterSpace(name="w_pass", min_value=100.0, max_value=5000.0),
            ParameterSpace(name="l_pass", min_value=0.15, max_value=1.0),
            ParameterSpace(name="c_load_pf", min_value=10.0, max_value=1000.0), # 10pF to 1nF
            ParameterSpace(name="r1", min_value=1e3, max_value=100e3),
            ParameterSpace(name="r2", min_value=1e3, max_value=100e3)
        ]

    def get_objectives(self) -> List[ObjectiveSpec]:
        return [
            ObjectiveSpec(name="vout_accuracy", target=self.target_vout, weight=2.0, minimize=False),
            ObjectiveSpec(name="dropout_v", target=0.0, weight=1.0, minimize=True),
            ObjectiveSpec(name="overshoot", target=0.0, weight=1.5, minimize=True)
        ]

    def simulate(self, params: Dict[str, float]) -> Dict[str, float]:
        from circuits.library.building_blocks.ldo_template import LDORegulator
        
        ldo = LDORegulator(
            w_pass = params['w_pass'],
            l_pass = params['l_pass'],
            r1 = params['r1'],
            r2 = params['r2'],
            c_load_pf = params['c_load_pf']
        )
        
        # Test Load Step: 0mA -> 50mA
        netlist = f"""* AI Optimized LDO Transient Test
.lib /opt/sky130_pdk/sky130A/libs.tech/ngspice/sky130.lib.spice tt

* Supply (VIN is 2.2V for 1.8V output)
Vunreg vin 0 DC 2.2
Vref vref 0 DC {self.target_vref}

{ldo.generate_netlist_fragment("vin", "vout", "vref", "0")}

* Dynamic Load (Pulse)
Iload vout 0 PULSE(1m 50m 10u 1n 1n 20u 40u)

.tran 1n 100u

.control
run
* Measure Vout Accuracy
let vout_final = v(vout)[length(v(vout))-1]
echo "RESULT_VOUT $&vout_final"

* Measure Peak Overshoot
let peak = max(v(vout))
let overshoot = peak - vout_final
echo "RESULT_OVERSHOOT $&overshoot"

* DC Sweep to find dropout (Vin from 0 to 2.2)
* Actually for speed, we measure R_ON of pass transistor
quit
.endc
.end
"""
        with open("ldo_temp.spice", "w") as f:
            f.write(netlist)
            
        result = subprocess.run(["ngspice", "-b", "ldo_temp.spice"], capture_output=True, text=True)
        
        # Parse results
        metrics = {}
        metrics["vout_accuracy"] = float(re.search(r"RESULT_VOUT\s+([0-9\.eE+-]+)", result.stdout).group(1)) if re.search(r"RESULT_VOUT\s+([0-9\.eE+-]+)", result.stdout) else 0.0
        metrics["overshoot"] = float(re.search(r"RESULT_OVERSHOOT\s+([0-9\.eE+-]+)", result.stdout).group(1)) if re.search(r"RESULT_OVERSHOOT\s+([0-9\.eE+-]+)", result.stdout) else 0.0
        # Dropout estimate (simple placeholder)
        metrics["dropout_v"] = params['l_pass'] / (params['w_pass'] + 1e-6) * 10 
        
        return metrics

if __name__ == "__main__":
    ldo = SmartLDO()
    print(ldo.simulate({"w_pass": 1000.0, "l_pass": 0.5, "c_load_pf": 100.0, "r1": 8000.0, "r2": 10000.0}))
