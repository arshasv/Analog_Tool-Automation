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
.lib "{lib_path}" tt

* Parameters
.param W_n = {width}u
.param L_n = {length}u
.param R_d = {res_val}

* Supply
Vdd vdd 0 1.8
Vin vin 0 SIN(0.9 0.1 1k)

* Circuit
XM1 vout vin 0 0 sky130_fd_pr__nfet_01v8 w={{W_n}} l={{L_n}}
R1 vdd vout {{R_d}}

* Analysis
.tran 1n 10u
.control
run
plot v(vout) v(vin)
.endc
.end
"""
    return netlist
