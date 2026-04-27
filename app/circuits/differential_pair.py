"""
Sky130 Differential Pair Amplifier - Netlist Generator

Standardized with scale=1u compatibility and high-fidelity analysis hints.
"""

import os

def generate_netlist(width: float = 2.0, length: float = 0.15) -> str:
    """
    Generates a SPICE netlist for a Differential Pair using Sky130 NMOS.
    """
    pdk = os.environ.get("SKY130_PDK", "/opt/sky130_pdk/sky130A")

    netlist = f"""* Sky130 Differential Pair Amplifier
* Generator: differential_pair.py
* @AC_SOURCE: Vin_p
* @AC_EXPR: vdb(vout_p,vout_n)
* @TRAN_EXPR: v(vout_p,vout_n)
* @DC_EXPR: v(vout_p,vout_n)

* Parameters (scale=1u is applied by orchestrator)
.param W_n = {width}
.param L_n = {length}

* Supplies
Vdd vdd 0 1.8
Vcm vcm 0 DC 0.9

* Inputs
Vin_p vin_p vcm DC 0 pulse(-0.01 0.01 1u 1n 1n 5u 10u) AC 0.5
Vin_n vin_n vcm DC 0 AC -0.5

* Circuit — Differential Pair
XM1 vout_p vin_p vs 0 sky130_fd_pr__nfet_01v8 w={{W_n}} l={{L_n}}
XM2 vout_n vin_n vs 0 sky130_fd_pr__nfet_01v8 w={{W_n}} l={{L_n}}

* Load resistors
R1 vdd vout_p 10k
R2 vdd vout_n 10k

* Load Capacitors
CL1 vout_p 0 0.1p
CL2 vout_n 0 0.1p

* Tail current source
Iss vs 0 100u

* Analysis
.dc Vin_p -0.05 0.05 0.001
.ac dec 50 10 1G
.tran 1n 20u
.end
"""
    return netlist
