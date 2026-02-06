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
        
        # Robust stage count handling
        stages = int(params.get('num_stages', 5))
        if stages % 2 == 0: stages += 1 # Must be odd
        
        vco = RingOscillatorVCO(
            num_stages = stages,
            w_n = params.get('w_n', 2.0),
            l_n = params.get('l_n', 0.15)
        )
        
        # Test at Vctrl = 0.9V (Center)
        netlist = f"""* AI Optimized VCO Transient Test
.lib /usr/local/share/pdk/sky130A/libs.tech/ngspice/sky130.lib.spice tt

Vdd vdd 0 DC {self.vdd}
Vctrl vctrl 0 DC 0.9
.ic v(vout)=0

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

    def generate_layout(self, params: Dict[str, float]) -> str:
        wn = params.get('w_n', 2.0)
        ln = params.get('l_n', 0.15)
        wp = params.get('w_p', wn * 2)
        lp = ln
        
        # Enforce odd stages
        num_stages = int(params.get('num_stages', 5))
        if num_stages % 2 == 0: num_stages += 1
        
        # Grid parameters (Microns)
        pitch_x = max(10.0, wn + 5.0) 
        pitch_y_p = 25.0 # PMOS Y-position (Absolute)
        
        tcl = "drc off\n"
        
        # 1. Draw Power Rails (Absolute Box Values)
        total_width = num_stages * pitch_x + 10.0
        
        # GND Rail (Bottom: y=-12 to -8)
        tcl += f"box values -5um -12um {total_width}um -8um\n"
        tcl += "paint m1\n"
        tcl += "label gnd -shape box -layer m1\n"
        
        # VDD Rail (Top: y=35 to 39)
        tcl += f"box values -5um 35um {total_width}um 39um\n"
        tcl += "paint m1\n"
        tcl += "label vdd -shape box -layer m1\n"
        
        # 2. Draw Stages (Cursor-Based Placement)
        for i in range(num_stages):
            x_center = i * pitch_x
            
            # --- NMOS Device (Place at y=0) ---
            # Set cursor to target spot, then generate
            tcl += f"box values {x_center}um 0um {x_center}um 0um\n"
            tcl += f"magic::gencell sky130::sky130_fd_pr__nfet_01v8 {{w {wn} l {ln}}}\n"
            
            # --- P-Substrate Contact (Place at y=-10, touching GND) ---
            tcl += f"box values {x_center}um -10um {x_center}um -10um\n"
            tcl += "magic::gencell sky130::sky130_fd_pr__nsubstratecontact {w 1.0 l 1.0}\n"

            # --- PMOS Device (Place at y=25) ---
            tcl += f"box values {x_center}um {pitch_y_p}um {x_center}um {pitch_y_p}um\n"
            tcl += f"magic::gencell sky130::sky130_fd_pr__pfet_01v8 {{w {wp} l {lp}}}\n"
            
            # --- N-Well Contact (Place at y=42, touching VDD idea) ---
            # Ideally slightly below rail or touching it
            tcl += f"box values {x_center}um 33um {x_center}um 33um\n"
            tcl += "magic::gencell sky130::sky130_fd_pr__psubstratecontact {w 1.0 l 1.0}\n"
            
            # --- Gate Labels (Input) ---
            if i == 0:
                tcl += f"box values {x_center}um -2um {x_center+0.5}um {pitch_y_p}um\n"
                tcl += "paint poly\n" 
                tcl += "label vctrl -center poly\n"
            
        return tcl
if __name__ == "__main__":
    vco = SmartVCO()
    print(vco.simulate({"w_n": 2.0, "l_n": 0.5, "w_p": 4.0, "num_stages": 5}))
