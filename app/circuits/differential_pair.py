"""
Sky130 Differential Pair Amplifier - Netlist Generator

Upload this file via POST /api/v1/run with optional parameters:
  - width (float): NMOS width in um (default: 2.0)
  - length (float): NMOS length in um (default: 0.15)
"""

import os


def generate_netlist(width: float = 2.0, length: float = 0.15) -> str:
    """
    Generates a SPICE netlist for a Differential Pair using Sky130 NMOS.

    Topology:
      - M1, M2: matched NMOS input pair
      - R1, R2: passive load resistors to VDD
      - Iss: tail current source (100 uA)
      - Vin1: positive input (AC signal)
      - Vin2: negative input (DC reference)
    """
    pdk = os.environ.get("SKY130_PDK", "/opt/sky130_pdk/sky130A")
    lib_path = f"{pdk}/libs.tech/ngspice/sky130.lib.spice"

    netlist = f"""* Sky130 Differential Pair Amplifier
.lib "{lib_path}" tt

* Parameters
.param W_n = {width}u
.param L_n = {length}u

* Supplies
Vdd vdd 0 1.8

* Inputs
Vcm vcm 0 DC 0.9
Vin_p vin_p vcm SIN(0 0.05 1k)
Vin_n vin_n vcm DC 0

* Circuit — Differential Pair
* Input transistors
XM1 vout_p vin_p vs 0 sky130_fd_pr__nfet_01v8 w={{W_n}} l={{L_n}}
XM2 vout_n vin_n vs 0 sky130_fd_pr__nfet_01v8 w={{W_n}} l={{L_n}}

* Load resistors
R1 vdd vout_p 10k
R2 vdd vout_n 10k

* Tail current source
Iss vs 0 100u

* Analysis
.tran 1n 10u
.control
run
plot v(vout_p) v(vout_n) v(vin_p) v(vin_n)
.endc
.end
"""
    return netlist
