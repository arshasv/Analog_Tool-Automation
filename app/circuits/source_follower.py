"""
Sky130 Source Follower (Common Drain) - Netlist Generator

Parameters (all use consistent SI-prefix units for the parameter box):
  - width (float): Transistor width in µm (default 10.0)
  - length (float): Channel length in µm (default 0.15)
  - ibias (float): Bias current in µA (default 100.0)
"""

import os

def generate_netlist(width: float = 10.0, length: float = 0.15,
                     ibias: float = 100.0) -> str:
    """ibias is in µA (e.g. 100.0 = 100µA). SPICE appends the 'u' suffix."""
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
Ibias vout 0 {ibias}u

* Load Capacitor
CL vout 0 0.5p

* Analysis
.dc Vin 0 1.8 0.01
.ac dec 100 10 10G
.tran 1n 20u
.end
"""
    return netlist
