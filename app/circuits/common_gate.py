"""
Sky130 Common Gate Amplifier - Netlist Generator

Standardized with scale=1u compatibility and high-fidelity analysis hints.
"""

import os

def generate_netlist(width: float = 5.0, length: float = 0.15,
                     vbias: float = 1.0) -> str:
    pdk = os.environ.get("SKY130_PDK", "/opt/sky130_pdk/sky130A")

    netlist = f"""* Sky130 Common Gate Amplifier
* Generator: common_gate.py
* @AC_SOURCE: Vin
* @AC_EXPR: vdb(vout)
* @TRAN_EXPR: v(vout)
* @DC_EXPR: v(vout)

* Parameters (scale=1u is applied by orchestrator)
.param W = {width}
.param L = {length}

* Supply & Stimulus
Vdd vdd 0 1.8
Vbias vbias 0 {vbias}
Vin vin 0 DC 0.5 pulse(0.45 0.55 1u 1n 1n 5u 10u) AC 1

* Input coupling
Rin vin src 50

* Circuit Implementation
XM1 vout vbias src 0 sky130_fd_pr__nfet_01v8 w={{W}} l={{L}}
Rd vdd vout 5k

* Load Capacitor
CL vout 0 0.2p

* Analysis
.dc Vin 0 1.2 0.01
.ac dec 100 10 10G
.tran 1n 20u
.end
"""
    return netlist
