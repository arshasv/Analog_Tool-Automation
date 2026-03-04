"""
Sky130 PMOS Current Mirror - Netlist Generator

Parameters (all use consistent SI-prefix units for the parameter box):
  - width (float): Transistor width in µm (default 4.0)
  - length (float): Channel length in µm (default 0.5)
  - iref (float): Reference current in µA (default 50.0)
"""

import os

def generate_netlist(width: float = 4.0, length: float = 0.5,
                     iref: float = 50.0) -> str:
    """iref is in µA (e.g. 50.0 = 50µA). SPICE appends the 'u' suffix."""
    pdk = os.environ.get("SKY130_PDK", "/opt/sky130_pdk/sky130A")

    netlist = f"""* Sky130 PMOS Current Mirror
* Generator: pmos_current_mirror.py
* @AC_SOURCE: Iref
* @AC_EXPR: i(vmeas)
* @TRAN_EXPR: i(vmeas)
* @DC_EXPR: i(vmeas)

* Parameters (scale=1u is applied by orchestrator)
.param W = {width}
.param L = {length}

* Supply & Stimulus
Vdd vdd 0 1.8
Iref d_ref 0 DC {iref}u pulse(40u 60u 1u 1n 1n 5u 10u) AC 1

* Circuit Implementation
XM1 d_ref d_ref vdd vdd sky130_fd_pr__pfet_01v8 w={{W}} l={{L}}
XM2 vout_node d_ref vdd vdd sky130_fd_pr__pfet_01v8 w={{W}} l={{L}}

* Measurement and Load
Vmeas vout_node vout 0
Rload vout 0 10k
Cout vout_node 0 1p

* Analysis
.dc Iref 1u 100u 1u
.ac dec 100 10 100Meg
.tran 1n 20u
.end
"""
    return netlist
