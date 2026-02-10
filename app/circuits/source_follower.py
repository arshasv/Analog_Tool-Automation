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
.lib "{lib_path}" tt

* Parameters
.param W = {width}u
.param L = {length}u

* Supply
Vdd vdd 0 1.8
Vin vin 0 DC 0.9 AC 1

* Circuit — Source Follower
* M1: driver transistor (drain to VDD, source is output)
XM1 vdd vin vout 0 sky130_fd_pr__nfet_01v8 w={{W}} l={{L}}

* Tail current source (ideal)
Ibias vout 0 {ibias}

* Analysis — AC frequency response
.ac dec 50 1 10G
.control
run
plot vdb(vout)
.endc
.end
"""
    return netlist
