"""
Sky130 Schmitt Trigger - Netlist Generator

Standardized with scale=1u compatibility and high-fidelity analysis hints.
"""

import os

def generate_netlist(w_n: float = 1.0, w_p: float = 2.0,
                     w_nfb: float = 0.5, w_pfb: float = 1.0,
                     l: float = 0.15) -> str:
    pdk = os.environ.get("SKY130_PDK", "/opt/sky130_pdk/sky130A")

    netlist = f"""* Sky130 CMOS Schmitt Trigger
* Generator: schmitt_trigger.py
* @AC_SOURCE: Vin
* @AC_EXPR: vdb(vout)
* @TRAN_EXPR: v(vout)
* @DC_EXPR: v(vout)

* Parameters (scale=1u is applied by orchestrator)
.param W_n = {w_n}
.param W_p = {w_p}
.param W_nfb = {w_nfb}
.param W_pfb = {w_pfb}
.param L = {l}

* Supply & Stimulus (Triangular wave for hysteresis verification)
Vdd vdd 0 1.8
Vin vin 0 DC 0.9 pulse(0 1.8 1u 5u 5u 1u 12u) AC 1

* Circuit Implementation
XM1 vout vin vdd vdd sky130_fd_pr__pfet_01v8 w={{W_p}} l={{L}}
XM2 n1 vout vdd vdd sky130_fd_pr__pfet_01v8 w={{W_pfb}} l={{L}}
XM3 vout vin n2 0 sky130_fd_pr__nfet_01v8 w={{W_n}} l={{L}}
XM4 n2 vout 0 0 sky130_fd_pr__nfet_01v8 w={{W_nfb}} l={{L}}

* Load
Cload vout 0 10f

* Analysis
.dc Vin 0 1.8 0.001
.ac dec 100 10 10G
.tran 1n 20u
.end
"""
    return netlist
