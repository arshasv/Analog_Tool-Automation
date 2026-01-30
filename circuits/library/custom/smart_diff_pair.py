"""
AI-Ready Differential Pair
An optimizable differential pair that targets specific gain and bandwidth.
"""
import os
import subprocess
import re
from typing import Dict, List
from circuits.library.custom.base_circuit import OptimizableCircuit
from ai_engine.optimizers.base_optimizer import ParameterSpace, ObjectiveSpec
from circuits.sky130.devices import nmos, Sky130Constants

class SmartDiffPair(OptimizableCircuit):
    def __init__(self):
        self.itail = 50e-6
        self.rload = 10e3
        # Goals
        self.target_gain = 20.0  # 26dB approx
        
    def get_parameter_space(self) -> List[ParameterSpace]:
        return [
            ParameterSpace(name="width", min_value=1.0, max_value=50.0),
            ParameterSpace(name="length", min_value=0.15, max_value=2.0)
        ]

    def get_objectives(self) -> List[ObjectiveSpec]:
        return [
            ObjectiveSpec(name="gain", target=self.target_gain, weight=1.0, minimize=False)
        ]

    def simulate(self, params: Dict[str, float]) -> Dict[str, float]:
        w = params['width']
        l = params['length']
        
        m1 = nmos(name="1", width=w, length=l)
        m2 = nmos(name="2", width=w, length=l)
        
        # Netlist for Differential Gain
        netlist = f"""* AI Optimized Diff Pair
.lib /usr/local/share/pdk/sky130A/libs.tech/ngspice/sky130.lib.spice tt

Vdd vdd 0 DC 1.8
Vss 0 0 DC 0

* Input signals
Vid_p inp 0 DC 0.9 AC 0.5
Vid_n inn 0 DC 0.9 AC -0.5

* Diff Pair
{m1.to_spice("outn", "inp", "tail", "0")}
{m2.to_spice("outp", "inn", "tail", "0")}

* Tail current
Itail tail 0 {self.itail}

* Load resistors
R1 vdd outn {self.rload}
R2 vdd outp {self.rload}

.ac dec 10 1 1G

.control
run
* Calculate differential gain at 1kHz
let gain = mag(v(outp)-v(outn))
echo "RESULT_GAIN $&gain[0]"
quit
.endc
.end
"""
        with open("diff_temp.spice", "w") as f:
            f.write(netlist)
            
        result = subprocess.run(["ngspice", "-b", "diff_temp.spice"], capture_output=True, text=True)
        
        match = re.search(r"RESULT_GAIN\s+([0-9\.eE+-]+)", result.stdout)
        gain = float(match.group(1)) if match else 0.0
        
        return {"gain": gain}

if __name__ == "__main__":
    dp = SmartDiffPair()
    print(dp.simulate({"width": 20.0, "length": 0.5}))
