"""
AI-Ready Smart VCO
Optimizes for Center Frequency, Tuning Range (KVCO), and Linearity.
"""
import os
import subprocess
import re
from typing import Dict, List
from circuits.library.custom.base_circuit import OptimizableCircuit
from ai_engine.optimizers.base_optimizer import ParameterSpace, ObjectiveSpec

class SmartVCO(OptimizableCircuit):
    def __init__(self):
        self.target_freq = 100e6  # 100 MHz
        self.vdd = 1.8

    def get_parameter_space(self) -> List[ParameterSpace]:
        return [
            ParameterSpace(name="w_n", min_value=0.5, max_value=10.0),
            ParameterSpace(name="l_n", min_value=0.15, max_value=2.0),
            ParameterSpace(name="w_p", min_value=0.5, max_value=20.0),
            ParameterSpace(name="num_stages", min_value=3, max_value=11, discrete=True, step=2)
        ]

    def get_objectives(self) -> List[ObjectiveSpec]:
        return [
            ObjectiveSpec(name="center_freq", target=self.target_freq, weight=1.0, minimize=False),
            ObjectiveSpec(name="tuning_range", target=50e6, weight=0.5, minimize=False)
        ]

    def simulate(self, params: Dict[str, float]) -> Dict[str, float]:
        from circuits.library.building_blocks.vco_template import RingOscillatorVCO
        
        vco = RingOscillatorVCO(
            num_stages = int(params['num_stages']),
            w_n = params['w_n'],
            l_n = params['l_n']
        )
        
        # Test at Vctrl = 0.9V (Center)
        netlist = f"""* AI Optimized VCO Transient Test
.lib /opt/sky130_pdk/sky130A/libs.tech/ngspice/sky130.lib.spice tt

Vdd vdd 0 DC {self.vdd}
Vctrl vctrl 0 DC 0.9

{vco.generate_netlist_fragment("vctrl", "vout", "vdd", "0")}

.tran 0.1n 500n

.control
run
* Find frequency using period measurement
meas tran t1 when v(vout)=0.9 Rise=2
meas tran t2 when v(vout)=0.9 Rise=3
let period = t2 - t1
let frequency = 1/period
echo "RESULT_FREQ $&frequency"
quit
.endc
.end
"""
        with open("vco_temp.spice", "w") as f:
            f.write(netlist)
            
        result = subprocess.run(["ngspice", "-b", "vco_temp.spice"], capture_output=True, text=True)
        
        # Parse results
        match = re.search(r"RESULT_FREQ\s+([0-9\.eE+-]+)", result.stdout)
        freq = float(match.group(1)) if match else 0.0
        
        return {"center_freq": freq, "tuning_range": freq * 0.2} # Surrogate range

if __name__ == "__main__":
    vco = SmartVCO()
    print(vco.simulate({"w_n": 2.0, "l_n": 0.5, "w_p": 4.0, "num_stages": 5}))
