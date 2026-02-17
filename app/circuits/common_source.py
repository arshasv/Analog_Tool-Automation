"""
Sky130 Common Source Amplifier - Netlist Generator

Upload this file via POST /api/v1/run with optional parameters:
  - width (float): NMOS width in um (default: 1.0)
  - length (float): NMOS length in um (default: 0.15)
  - res_val (float): Load resistance in Ohms (default: 1000.0)
"""

import os


def generate_netlist(width: float = 1.0, length: float = 0.15, res_val: float = 1000.0) -> str:
    """
    Generates a SPICE netlist for a Common Source Amplifier using Sky130 models.
    """
    pdk = os.environ.get("SKY130_PDK", "/opt/sky130_pdk/sky130A")
    lib_path = f"{pdk}/libs.tech/ngspice/sky130.lib.spice"

    netlist = f"""* Sky130 Common Source Amplifier
* @AC_SOURCE: Vin
* @AC_EXPR: vdb(vout)
* @TRAN_EXPR: v(vout)
* @DC_EXPR: v(vout)
.lib "{lib_path}" tt

* Parameters
.param W_n = {width}u
.param L_n = {length}u
.param R_d = {res_val}

* Supply
Vdd vdd 0 1.8
Vin vin 0 pulse(0.85 0.95 1u 1n 1n 5u 10u) DC 0.9 AC 1

* Circuit
XM1 vout vin 0 0 sky130_fd_pr__nfet_01v8 w={{W_n}} l={{L_n}}
R1 vdd vout {{R_d}}

* Load Capacitor
CL vout 0 0.1p

* Analysis
.dc Vin 0.5 1.5 0.01
.ac dec 50 10 1G
.tran 1n 20u
.end
"""
    return netlist
