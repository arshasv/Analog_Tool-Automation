"""
Sky130 CMOS Inverter - Netlist Generator

Standardized with scale=1u compatibility and high-fidelity analysis hints.
"""

import os

def generate_netlist(w_n: float = 1.0, w_p: float = 2.0,
                     l: float = 0.15, cload: float = 10.0) -> str:
    pdk = os.environ.get("SKY130_PDK", "/opt/sky130_pdk/sky130A")

    netlist = f"""* Sky130 CMOS Inverter
* Generator: inverter.py
* @AC_SOURCE: Vin
* @AC_EXPR: vdb(vout)
* @TRAN_EXPR: v(vout)
* @DC_EXPR: v(vout)

* Parameters (scale=1u is applied by orchestrator)
.param W_n = {w_n}
.param W_p = {w_p}
.param L = {l}

* Supply & Stimulus
Vdd vdd 0 1.8
Vin vin 0 DC 0.9 pulse(0 1.8 1u 1n 1n 5u 10u) AC 1

* Circuit Implementation
XMn vout vin 0 0 sky130_fd_pr__nfet_01v8 w={{W_n}} l={{L}}
XMp vout vin vdd vdd sky130_fd_pr__pfet_01v8 w={{W_p}} l={{L}}

* Load (cload is in fF)
Cload vout 0 {cload}f

* Analysis
.dc Vin 0 1.8 0.01
.ac dec 100 10 10G
.tran 1n 20u
.end
"""
    return netlist
