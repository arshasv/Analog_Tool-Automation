"""
Sky130 Common Gate Amplifier - Netlist Generator

Low input impedance, high output impedance amplifier.
Often used as cascode stage, TIA front-end, or in cascode LNAs.

Upload via POST /api/v1/run with optional parameters:
  - width (float): NMOS width in um (default: 5.0)
  - length (float): Channel length in um (default: 0.15)
  - vbias (float): Gate bias voltage (default: 1.0)
"""

import os


def generate_netlist(width: float = 5.0, length: float = 0.15,
                     vbias: float = 1.0) -> str:
    pdk = os.environ.get("SKY130_PDK", "/opt/sky130_pdk/sky130A")
    lib_path = f"{pdk}/libs.tech/ngspice/sky130.lib.spice"

    netlist = f"""* Sky130 Common Gate Amplifier
* @AC_SOURCE: Vin
* @AC_EXPR: vdb(vout)
* @TRAN_EXPR: v(vout)
* @DC_EXPR: v(vout)
.lib "{lib_path}" tt

* Parameters
.param W = {width}u
.param L = {length}u

* Supply
Vdd vdd 0 1.8

* Bias and input
Vbias vbias 0 {vbias}
Vin vin 0 pulse(0.45 0.55 1u 1n 1n 5u 10u) DC 0.5 AC 1

* Input coupling — signal enters at source terminal
Rin vin src 50

* Circuit — Common Gate
* M1: gate is AC-grounded (biased), signal enters at source
XM1 vout vbias src 0 sky130_fd_pr__nfet_01v8 w={{W}} l={{L}}
* Drain load resistor
Rd vdd vout 5k

* Load Capacitor
CL vout 0 0.2p

* Analysis
.dc Vin 0.3 0.7 0.01
.ac dec 50 10 10G
.tran 10n 20u
.end
"""
    return netlist
