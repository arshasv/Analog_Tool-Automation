"""
Sky130 Current Mirror - Netlist Generator

Upload this file via POST /api/v1/run with optional parameters:
  - width (float): Transistor width in um (default: 2.0)
  - length (float): Transistor length in um (default: 0.5)
"""

import os


def generate_netlist(width: float = 2.0, length: float = 0.5) -> str:
    """
    Generates a SPICE netlist for a Current Mirror using Sky130 NMOS.

    Topology:
      - M1: diode-connected reference (gate=drain)
      - M2: mirror transistor (gate tied to M1 gate)
      - Iref: reference current source
      - Rload: output load resistor
    """
    pdk = os.environ.get("SKY130_PDK", "/opt/sky130_pdk/sky130A")
    lib_path = f"{pdk}/libs.tech/ngspice/sky130.lib.spice"

    netlist = f"""* Sky130 Current Mirror
.lib "{lib_path}" tt

* Parameters
.param W = {width}u
.param L = {length}u

* Supply
Vdd vdd 0 1.8

* Reference current
Iref vdd d_ref 100u

* Circuit — Current Mirror
* M1: diode-connected reference transistor
XM1 d_ref d_ref 0 0 sky130_fd_pr__nfet_01v8 w={{W}} l={{L}}
* M2: mirror output transistor
XM2 vout d_ref 0 0 sky130_fd_pr__nfet_01v8 w={{W}} l={{L}}

* Output load
Rload vdd vout 10k

* Analysis — DC sweep of reference current
.dc Iref 1u 200u 1u
.control
run
plot i(Rload) vs @Iref[dc]
.endc
.end
"""
    return netlist
