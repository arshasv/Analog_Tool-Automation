"""
Sky130 Wilson Current Mirror - Netlist Generator

Standardized with scale=1u compatibility and high-fidelity analysis hints.
"""

import os

def generate_netlist(width: float = 2.0, length: float = 1.0) -> str:
    pdk = os.environ.get("SKY130_PDK", "/opt/sky130_pdk/sky130A")

    netlist = f"""* Sky130 Wilson Current Mirror
* Generator: wilson_current_mirror.py
* @AC_SOURCE: Iref
* @AC_EXPR: i(vmeas)
* @TRAN_EXPR: i(vmeas)
* @DC_EXPR: i(vmeas)

* Parameters (scale=1u is applied by orchestrator)
.param W = {width}
.param L = {length}

* Supply & Stimulus
Vdd vdd 0 1.8
Iref vdd d_ref DC 100u pulse(80u 120u 1u 1n 1n 5u 10u) AC 1

* Circuit Implementation — Wilson Current Mirror
XM1 gate1 gate1 0 0 sky130_fd_pr__nfet_01v8 w={{W}} l={{L}}
XM2 s3 gate1 0 0 sky130_fd_pr__nfet_01v8 w={{W}} l={{L}}
XM3 vout_node d_ref s3 0 sky130_fd_pr__nfet_01v8 w={{W}} l={{L}}

* Connection between reference node and XM1/XM2 gate
V_link d_ref gate1 0

* Measurement and Load
Vmeas vout vout_node 0
Rload vdd vout 10k
Cout vout_node 0 1p

* Analysis
.dc Iref 1u 200u 1u
.ac dec 100 10 100Meg
.tran 1n 20u
.end
"""
    return netlist
