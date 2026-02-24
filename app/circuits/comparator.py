"""
Sky130 Comparator - Netlist Generator

Standardized with scale=1u compatibility and high-fidelity analysis hints.
"""

import os

def generate_netlist(w_diff: float = 2.0, w_load: float = 4.0,
                     l: float = 0.5, itail: float = 20e-6) -> str:
    pdk = os.environ.get("SKY130_PDK", "/opt/sky130_pdk/sky130A")

    netlist = f"""* Sky130 Comparator
* Generator: comparator.py
* @AC_SOURCE: Vin
* @AC_EXPR: vdb(vout)
* @TRAN_EXPR: v(vout)
* @DC_EXPR: v(vout)

* Parameters (scale=1u is applied by orchestrator)
.param W_diff = {w_diff}
.param W_load = {w_load}
.param L = {l}

* Supply & Stimulus
Vdd vdd 0 1.8
Vref vref 0 0.9
Vin vin 0 DC 0.9 pulse(0.5 1.3 10u 1n 1n 40u 80u) AC 1

* Circuit Implementation
* Differential Pair
Itail vs 0 {itail}
XM1 d1 vin vs 0 sky130_fd_pr__nfet_01v8 w={{W_diff}} l={{L}}
XM2 d2 vref vs 0 sky130_fd_pr__nfet_01v8 w={{W_diff}} l={{L}}

* PMOS active load (current mirror)
XM3 d1 d1 vdd vdd sky130_fd_pr__pfet_01v8 w={{W_load}} l={{L}}
XM4 d2 d1 vdd vdd sky130_fd_pr__pfet_01v8 w={{W_load}} l={{L}}

* Output Inverter (sharpens transition)
XM5 vout d2 0 0 sky130_fd_pr__nfet_01v8 w={{W_diff}} l={{L}}
XM6 vout d2 vdd vdd sky130_fd_pr__pfet_01v8 w={{W_load}} l={{L}}

* Load Capacitor
CL vout 0 0.1p

* Analysis
.dc Vin 0 1.8 0.01
.ac dec 100 10 100Meg
.tran 10n 150u
.end
"""
    return netlist
