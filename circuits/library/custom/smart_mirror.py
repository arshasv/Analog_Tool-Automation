import os
import subprocess
import re
from typing import Dict, List
from circuits.library.custom.base_circuit import OptimizableCircuit
from ai_engine.optimizers.base_optimizer import ParameterSpace, ObjectiveSpec
from circuits.sky130.devices import nmos, Sky130Constants

class SmartCurrentMirror(OptimizableCircuit):
    """
    An AI-Ready version of the Current Mirror.
    This design 'knows' how to optimize itself.
    """
    
    def __init__(self):
        self.iref = 10e-6
        self.ratio = 4.0
        self.expected_iout = self.iref * self.ratio

    def get_parameter_space(self) -> List[ParameterSpace]:
        # The AI is allowed to change Length and Width
        return [
            ParameterSpace(name="length", min_value=0.15, max_value=2.0),
            ParameterSpace(name="width", min_value=1.0, max_value=20.0)
        ]

    def get_objectives(self) -> List[ObjectiveSpec]:
        # The goal is to get output current equal to 40uA
        return [
            ObjectiveSpec(name="iout", target=self.expected_iout, weight=1.0, minimize=False)
        ]

    def simulate(self, params: Dict[str, float]) -> Dict[str, float]:
        w = params['width']
        l = params['length']
        
        # 1. Create transistors
        m1 = nmos(name="1", width=w, length=l)
        m2 = nmos(name="2", width=w * self.ratio, length=l)
        
        # 2. Generate Netlist
        netlist = f"""* AI Optimized Current Mirror
.lib /usr/local/share/pdk/sky130A/libs.tech/ngspice/sky130.lib.spice tt
Vdd vdd 0 DC 1.8
Iref vdd ref {self.iref}
{m1.to_spice("ref", "ref", "0", "0")}
{m2.to_spice("out", "ref", "0", "0")}
Rload vdd out 1k
.op
.control
run
let iout_val = @m.x2.msky130_fd_pr__nfet_01v8[id]
echo "RESULT_IOUT $&iout_val"
quit
.endc
.end
"""
        with open("opt_temp.spice", "w") as f:
            f.write(netlist)
            
        # 3. Run Simulation
        result = subprocess.run(["ngspice", "-b", "opt_temp.spice"], capture_output=True, text=True)
        
        # 4. Parse Result
        match = re.search(r"RESULT_IOUT\s+([0-9\.eE+-]+)", result.stdout)
        iout = float(match.group(1)) if match else 0.0
        
        return {"iout": iout}

if __name__ == "__main__":
    # Test simulation
    mirror = SmartCurrentMirror()
    print(mirror.simulate({"width": 2.0, "length": 0.5}))
