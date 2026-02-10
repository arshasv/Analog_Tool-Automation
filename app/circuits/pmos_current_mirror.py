"""
Sky130 PMOS Current Mirror - Netlist Generator

PMOS current mirror used as active load in amplifier stages.

Upload via POST /api/v1/run with optional parameters:
  - width (float): PMOS width in um (default: 4.0)
  - length (float): Channel length in um (default: 0.5)
  - iref (float): Reference current in A (default: 50e-6)
"""

import os


def generate_netlist(width: float = 4.0, length: float = 0.5,
                     iref: float = 50e-6) -> str:
    pdk = os.environ.get("SKY130_PDK", "/opt/sky130_pdk/sky130A")
    lib_path = f"{pdk}/libs.tech/ngspice/sky130.lib.spice"

    netlist = f"""* Sky130 PMOS Current Mirror
.lib "{lib_path}" tt

* Parameters
.param W = {width}u
.param L = {length}u

* Supply
Vdd vdd 0 1.8

* Reference current source (sinks from VDD through M1)
Iref d_ref 0 {iref}

* Circuit — PMOS Current Mirror
* M1: diode-connected reference (source=VDD, drain=gate)
XM1 d_ref d_ref vdd vdd sky130_fd_pr__pfet_01v8 w={{W}} l={{L}}
* M2: mirror output (gate tied to M1)
XM2 vout d_ref vdd vdd sky130_fd_pr__pfet_01v8 w={{W}} l={{L}}

* Output load
Rload vout 0 10k

* Analysis — sweep VDD to see mirror compliance
.dc Vdd 0 1.8 0.01
.control
run
plot -i(Vdd) i(Rload)
.endc
.end
"""
    return netlist
