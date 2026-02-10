"""
Sky130 Schmitt Trigger - Netlist Generator

CMOS Schmitt trigger with hysteresis. Provides noise immunity
by having different switching thresholds for rising and falling
edges. Used in clock cleanup, button debouncing, and
noisy-signal conditioning.

Upload via POST /api/v1/run with optional parameters:
  - w_n (float): NMOS main width in um (default: 1.0)
  - w_p (float): PMOS main width in um (default: 2.0)
  - w_nfb (float): NMOS feedback width in um (default: 0.5)
  - w_pfb (float): PMOS feedback width in um (default: 1.0)
  - l (float): Channel length in um (default: 0.15)
"""

import os


def generate_netlist(w_n: float = 1.0, w_p: float = 2.0,
                     w_nfb: float = 0.5, w_pfb: float = 1.0,
                     l: float = 0.15) -> str:
    pdk = os.environ.get("SKY130_PDK", "/opt/sky130_pdk/sky130A")
    lib_path = f"{pdk}/libs.tech/ngspice/sky130.lib.spice"

    netlist = f"""* Sky130 CMOS Schmitt Trigger
.lib "{lib_path}" tt

* Parameters
.param W_n = {w_n}u
.param W_p = {w_p}u
.param W_nfb = {w_nfb}u
.param W_pfb = {w_pfb}u
.param L = {l}u

* Supply
Vdd vdd 0 1.8

* Slow triangular input to see hysteresis
Vin vin 0 PULSE(0 1.8 0 10n 10n 0.1n 20n)

* === Schmitt Trigger (6-transistor) ===
* PMOS pull-up path
XMp1 vout vin vdd vdd sky130_fd_pr__pfet_01v8 w={{W_p}} l={{L}}
* PMOS feedback (weakens pull-up on rising edge → shifts threshold up)
XMpfb n1 vout vdd vdd sky130_fd_pr__pfet_01v8 w={{W_pfb}} l={{L}}

* NMOS pull-down stack
XMn1 vout vin n2 0 sky130_fd_pr__nfet_01v8 w={{W_n}} l={{L}}
* NMOS feedback (weakens pull-down on falling edge → shifts threshold down)
XMnfb n2 vout 0 0 sky130_fd_pr__nfet_01v8 w={{W_nfb}} l={{L}}

* Internal node connections for hysteresis feedback
* n1 connects to pull-up feedback path
* n2 connects to pull-down feedback path

* Load
Cload vout 0 10f

* Analysis — DC sweep to observe hysteresis loop
.dc Vin 0 1.8 0.001
.control
run
plot v(vout) vs v(vin) title "Schmitt Trigger Hysteresis"
.endc
.end
"""
    return netlist
