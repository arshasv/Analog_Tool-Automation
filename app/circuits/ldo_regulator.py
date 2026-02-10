"""
Sky130 Low Dropout Regulator (LDO) - Netlist Generator

PMOS-pass LDO with error amplifier feedback loop.
Regulates output voltage from unregulated supply.

Upload via POST /api/v1/run with optional parameters:
  - w_pass (float): Pass transistor width in um (default: 100.0)
  - l_pass (float): Pass transistor length in um (default: 0.5)
  - w_ea (float): Error amp transistor width in um (default: 5.0)
  - l_ea (float): Error amp transistor length in um (default: 1.0)
  - r1 (float): Feedback top resistor in Ohms (default: 100000)
  - r2 (float): Feedback bottom resistor in Ohms (default: 100000)
  - cl (float): Output capacitor in uF (default: 1.0)
"""

import os


def generate_netlist(w_pass: float = 100.0, l_pass: float = 0.5,
                     w_ea: float = 5.0, l_ea: float = 1.0,
                     r1: float = 100000, r2: float = 100000,
                     cl: float = 1.0) -> str:
    pdk = os.environ.get("SKY130_PDK", "/opt/sky130_pdk/sky130A")
    lib_path = f"{pdk}/libs.tech/ngspice/sky130.lib.spice"

    netlist = f"""* Sky130 Low Dropout Regulator (LDO)
.lib "{lib_path}" tt

* Parameters
.param W_pass = {w_pass}u
.param L_pass = {l_pass}u
.param W_ea = {w_ea}u
.param L_ea = {l_ea}u

* Unregulated supply (e.g. battery)
Vdd vdd 0 3.3

* Reference voltage (~1.2V from bandgap)
Vref vref 0 1.2

* === Error Amplifier (simple diff pair) ===
* Tail current
Itail ea_tail 0 50u

* Diff pair: compares Vref to feedback voltage
XM1 ea_out1 vref ea_tail 0 sky130_fd_pr__nfet_01v8 w={{W_ea}} l={{L_ea}}
XM2 ea_out vfb ea_tail 0 sky130_fd_pr__nfet_01v8 w={{W_ea}} l={{L_ea}}

* PMOS active load
XM3 ea_out1 ea_out1 vdd vdd sky130_fd_pr__pfet_01v8 w={{W_ea}} l={{L_ea}}
XM4 ea_out ea_out1 vdd vdd sky130_fd_pr__pfet_01v8 w={{W_ea}} l={{L_ea}}

* === Pass Transistor (PMOS) ===
* Gate driven by error amplifier output
XM_pass vout ea_out vdd vdd sky130_fd_pr__pfet_01v8 w={{W_pass}} l={{L_pass}}

* === Feedback Network ===
R1 vout vfb {r1}
R2 vfb 0 {r2}

* === Output Capacitor ===
CL vout 0 {cl}u

* === Load ===
Rload vout 0 100

* Analysis — Load regulation (DC sweep of load)
.dc Rload 50 500 5
.control
run
plot v(vout) title "LDO Output vs Load"
.endc
.end
"""
    return netlist
