"""
Sky130 Common Source Amplifier - Netlist Generator

Standardized with scale=1u compatibility and high-fidelity analysis hints.
"""

import os

def generate_netlist(width: float = 1.0, length: float = 0.15, res_val: float = 1000.0) -> str:
    """
    Generates a SPICE netlist for a Common Source Amplifier using Sky130 models.
    """
    pdk = os.environ.get("SKY130_PDK", "/opt/sky130_pdk/sky130A")

    netlist = f"""* Sky130 Common Source Amplifier
* Generator: common_source.py
* @AC_SOURCE: Vin
* @AC_EXPR: vdb(vout)
* @TRAN_EXPR: v(vout)
* @DC_EXPR: v(vout)

* Parameters (scale=1u is applied by orchestrator)
.param W_n = {width}
.param L_n = {length}
.param R_d = {res_val}

* Supply & Stimulus
Vdd vdd 0 1.8
Vin vin 0 DC 0.9 pulse(0.85 0.95 1u 1n 1n 5u 10u) AC 1

* Circuit Implementation
XM1 vout vin 0 0 sky130_fd_pr__nfet_01v8 w={{W_n}} l={{L_n}}
R1 vdd vout {{R_d}}

* Load Capacitor
CL vout 0 0.1p

* Analysis
.dc Vin 0 1.8 0.01
.ac dec 100 10 1G
.tran 1n 20u
.end
"""
    return netlist
