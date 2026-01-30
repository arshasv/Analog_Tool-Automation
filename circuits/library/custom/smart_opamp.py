"""
AI-Ready Smart Op-Amp
A complex two-stage Miller op-amp that optimizes for Gain, Phase Margin, and UGB.
"""
import os
import subprocess
import re
from typing import Dict, List
from circuits.library.custom.base_circuit import OptimizableCircuit
from ai_engine.optimizers.base_optimizer import ParameterSpace, ObjectiveSpec
from circuits.library.building_blocks.opamp_two_stage import TwoStageOpAmp
from circuits.sky130.devices import Sky130Constants

class SmartOpAmp(OptimizableCircuit):
    def __init__(self):
        # Design Targets
        self.target_gain = 60.0    # 60dB
        self.target_pm = 60.0      # 60 Degrees
        self.target_ugb = 10e6     # 10 MHz
        
        self.vdd = 1.8
        self.vbias = 0.7  # Constant bias for now

    def get_parameter_space(self) -> List[ParameterSpace]:
        return [
            # Stage 1
            ParameterSpace(name="w_diff", min_value=1.0, max_value=50.0),
            ParameterSpace(name="l_diff", min_value=0.5, max_value=2.0),
            ParameterSpace(name="w_mirror", min_value=1.0, max_value=50.0),
            # Stage 2
            ParameterSpace(name="w_gain_p", min_value=1.0, max_value=100.0),
            # Compensation
            ParameterSpace(name="cc_pf", min_value=0.1, max_value=10.0),
            ParameterSpace(name="rz_k", min_value=0.1, max_value=20.0),
        ]

    def get_objectives(self) -> List[ObjectiveSpec]:
        return [
            ObjectiveSpec(name="gain_db", target=self.target_gain, weight=1.0, minimize=False),
            ObjectiveSpec(name="pm", target=self.target_pm, weight=1.5, minimize=False),
            ObjectiveSpec(name="ugb", target=self.target_ugb, weight=0.5, minimize=False)
        ]

    def simulate(self, params: Dict[str, float]) -> Dict[str, float]:
        # Instantiate the template with AI parameters
        amp = TwoStageOpAmp(
            w_diff = params.get('w_diff', 20.0),
            l_diff = params.get('l_diff', 1.0),
            w_mirror = params.get('w_mirror', 10.0),
            w_gain_p = params.get('w_gain_p', 40.0),
            cc_pf = params.get('cc_pf', 2.0),
            rz_k = params.get('rz_k', 1.0)
        )
        
        netlist_frag = amp.generate_netlist_fragment("vin_p", "vin_n", "vout", "vbias", "vdd", "0")
        
        # Complete SPICE Netlist for AC analysis
        netlist = f"""* AI Optimized Op-Amp AC Analysis
.lib /opt/sky130_pdk/sky130A/libs.tech/ngspice/sky130.lib.spice tt

Vdd vdd 0 DC {self.vdd}
Vbias vbias 0 DC {self.vbias}

* Differential Input for AC Gain
Vin_p vin_p 0 DC 0.9 AC 0.5
Vin_n vin_n 0 DC 0.9 AC -0.5

{netlist_frag}

* Load Capacitor
Cload vout 0 5p

.ac dec 20 1 1G

.control
run
* Find DC Gain (at low freq)
let gain_mag = mag(v(vout))
let gain_db = 20*log10(gain_mag)
let dc_gain = gain_db[0]

* Find UGB (where gain = 1 or 0dB)
meas ac ugb_freq when gain_db=0

* Find Phase Margin at UGB
let phase = ph(v(vout)) * 180 / 3.14159
let pm = 180 + phase[0]

echo "RESULT_GAIN $&dc_gain"
echo "RESULT_UGB $&ugb_freq"
echo "RESULT_PM $&pm"
quit
.endc
.end
"""
        with open("opamp_temp.spice", "w") as f:
            f.write(netlist)
            
        result = subprocess.run(["ngspice", "-b", "opamp_temp.spice"], capture_output=True, text=True)
        
        # Parse results
        metrics = {}
        metrics["gain_db"] = float(re.search(r"RESULT_GAIN\s+([0-9\.eE+-]+)", result.stdout).group(1)) if re.search(r"RESULT_GAIN\s+([0-9\.eE+-]+)", result.stdout) else 0.0
        metrics["ugb"] = float(re.search(r"RESULT_UGB\s+([0-9\.eE+-]+)", result.stdout).group(1)) if re.search(r"RESULT_UGB\s+([0-9\.eE+-]+)", result.stdout) else 0.0
        metrics["pm"] = float(re.search(r"RESULT_PM\s+([0-9\.eE+-]+)", result.stdout).group(1)) if re.search(r"RESULT_PM\s+([0-9\.eE+-]+)", result.stdout) else 0.0
        
        return metrics

if __name__ == "__main__":
    amp = SmartOpAmp()
    print(amp.simulate({"w_diff": 20.0, "l_diff": 1.0, "w_mirror": 10.0, "w_gain_p": 40.0, "cc_pf": 2.0, "rz_k": 1.0}))
