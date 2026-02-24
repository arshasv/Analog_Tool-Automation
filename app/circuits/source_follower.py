"""
Sky130 Source Follower (Common Drain) - Netlist Generator

Standardized with scale=1u compatibility and high-fidelity analysis hints.
"""

import os

def generate_netlist(width: float = 10.0, length: float = 0.15,
                     ibias: float = 100e-6) -> str:
    pdk = os.environ.get("SKY130_PDK", "/opt/sky130_pdk/sky130A")

    netlist = f"""* Sky130 Source Follower (Common Drain Buffer)
* Generator: source_follower.py
* @AC_SOURCE: Vin
* @AC_EXPR: vdb(vout)
* @TRAN_EXPR: v(vout)
* @DC_EXPR: v(vout)

* Parameters (scale=1u is applied by orchestrator)
.param W = {width}
.param L = {length}

* Supply & Stimulus
Vdd vdd 0 1.8
Vin vin 0 DC 0.9 pulse(0.8 1.0 1u 1n 1n 5u 10u) AC 1

* Circuit Implementation
XM1 vdd vin vout 0 sky130_fd_pr__nfet_01v8 w={{W}} l={{L}}
Ibias vout 0 {ibias}

* Load Capacitor
CL vout 0 0.5p

* Analysis
.dc Vin 0 1.8 0.01
.ac dec 100 10 10G
.tran 1n 20u
.end
"""
    return netlist
