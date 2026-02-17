"""
Sky130 PMOS Current Mirror - Netlist Generator

PMOS current mirror used as active load in amplifier stages.

Upload via POST /api/v1/run with optional parameters:
  - width (float): PMOS width in um (default: 4.0)
  - length (float): Channel length in um (default: 0.5)
  - iref (float): Reference current in A (default: 50e-6)
"""

import os


def generate_netlist(width: float = 4.0, length: float = 0.5,
                     iref: float = 50e-6) -> str:
    pdk = os.environ.get("SKY130_PDK", "/opt/sky130_pdk/sky130A")
    lib_path = f"{pdk}/libs.tech/ngspice/sky130.lib.spice"

    netlist = f"""* Sky130 PMOS Current Mirror
* @AC_SOURCE: Iref
* @AC_EXPR: db(-i(Vmeas))
* @TRAN_EXPR: -i(Vmeas)
* @DC_EXPR: -i(Vmeas)
.lib "{lib_path}" tt

* Parameters
.param W = {width}u
.param L = {length}u

* Supply
Vdd vdd 0 1.8

* Reference current (DC + AC + Pulse)
Iref d_ref 0 pulse(40u 60u 1u 1n 1n 5u 10u) AC 1

* Circuit — PMOS Current Mirror
XM1 d_ref d_ref vdd vdd sky130_fd_pr__pfet_01v8 w={{W}} l={{L}}
XM2 vout_node d_ref vdd vdd sky130_fd_pr__pfet_01v8 w={{W}} l={{L}}

* Measurement and Load
Vmeas vout_node vout 0
Rload vout 0 10k
Cout vout_node 0 1p

* Analysis
.dc Iref 1u 100u 1u
.ac dec 50 10 100Meg
.tran 10n 20u
.end
"""
    return netlist
