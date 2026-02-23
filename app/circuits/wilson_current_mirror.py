"""
Sky130 Wilson Current Mirror - Netlist Generator

Improved current mirror with higher output impedance compared to
the basic mirror. Uses feedback through M3 to boost Rout.

Upload via POST /api/v1/run with optional parameters:
  - width (float): Transistor width in um (default: 2.0)
  - length (float): Channel length in um (default: 1.0)
"""

import os


def generate_netlist(width: float = 2.0, length: float = 1.0) -> str:
    pdk = os.environ.get("SKY130_PDK", "/opt/sky130_pdk/sky130A")
    lib_path = f"{pdk}/libs.tech/ngspice/sky130.lib.spice"

    netlist = f"""* Sky130 Wilson Current Mirror
* @AC_SOURCE: Iref
* @AC_EXPR: db(-i(Vmeas))
* @TRAN_EXPR: -i(Vmeas)
* @DC_EXPR: -i(Vmeas)

* Parameters
.param W = {width}u
.param L = {length}u

* Supply
Vdd vdd 0 1.8

* Reference current (DC + AC + Pulse)
Iref vdd d_ref pulse(80u 120u 1u 1n 1n 5u 10u) AC 1

* Circuit — Wilson Current Mirror
XM1 gate1 gate1 0 0 sky130_fd_pr__nfet_01v8 w={{W}} l={{L}}
XM2 s3 gate1 0 0 sky130_fd_pr__nfet_01v8 w={{W}} l={{L}}
XM3 vout_node d_ref s3 0 sky130_fd_pr__nfet_01v8 w={{W}} l={{L}}

* Feedback jump
R_jump d_ref gate1 0.1

* Measurement and Load
Vmeas vout vout_node 0
Rload vdd vout 10k
Cout vout_node 0 1p

* Analysis
.dc Iref 1u 200u 10u
.ac dec 50 10 100Meg
.tran 10n 20u
.end
"""
    return netlist
