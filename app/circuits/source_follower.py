"""
Sky130 Source Follower (Common Drain) - Netlist Generator

Unity-gain voltage buffer. Provides high input impedance and
low output impedance — used for driving loads and level shifting.

Upload via POST /api/v1/run with optional parameters:
  - width (float): NMOS width in um (default: 10.0)
  - length (float): Channel length in um (default: 0.15)
  - ibias (float): Tail bias current in A (default: 100e-6)
"""

import os


def generate_netlist(width: float = 10.0, length: float = 0.15,
                     ibias: float = 100e-6) -> str:
    pdk = os.environ.get("SKY130_PDK", "/opt/sky130_pdk/sky130A")
    lib_path = f"{pdk}/libs.tech/ngspice/sky130.lib.spice"

    netlist = f"""* Sky130 Source Follower (Common Drain Buffer)
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
Vin vin 0 pulse(0.8 1.0 1u 1n 1n 5u 10u) DC 0.9 AC 1

* Circuit — Source Follower
XM1 vdd vin vout 0 sky130_fd_pr__nfet_01v8 w={{W}} l={{L}}

* Tail current source
Ibias vout 0 {ibias}

* Load Capacitor
CL vout 0 0.5p

* Analysis
.dc Vin 0 1.8 0.01
.ac dec 50 10 10G
.tran 10n 20u
.end
"""
    return netlist
