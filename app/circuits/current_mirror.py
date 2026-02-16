"""
Sky130 Current Mirror - Netlist Generator

Upload this file via POST /api/v1/run with optional parameters:
  - width (float): Transistor width in um (default: 2.0)
  - length (float): Transistor length in um (default: 0.5)
"""

import os


def generate_netlist(width: float = 2.0, length: float = 0.5, process_id: str = "sim") -> str:
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
* @AC_SOURCE: Iref
* @AC_EXPR: db(i(Vmeas))
* @TRAN_EXPR: i(Vmeas)
.lib "{lib_path}" tt

* Parameters
.param W = {width}u
.param L = {length}u

* Supply
Vdd vdd 0 1.8

* Reference current (DC + AC excitation)
Iref vdd d_ref 100u ac 1

* Circuit — Current Mirror
XM1 d_ref d_ref 0 0 sky130_fd_pr__nfet_01v8 w={{W}} l={{L}}
XM2 vout d_ref 0 0 sky130_fd_pr__nfet_01v8 w={{W}} l={{L}}

* Output load with current measurement
Vmeas vout v_load_pin 0
Rload vdd v_load_pin 10k

* Analysis
.dc Iref 1u 200u 1u
.ac dec 100 10 100Meg

.control
run
* Export data for Python plotting
set filetype=ascii
wrdata {process_id}_ac.csv db(i(Vmeas))
wrdata {process_id}_dc_sweep.csv i(Vmeas)
.endc
.end
"""
    return netlist
