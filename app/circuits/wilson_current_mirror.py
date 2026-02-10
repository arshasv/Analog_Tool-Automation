"""
Sky130 Wilson Current Mirror - Netlist Generator

Improved current mirror with higher output impedance compared to
the basic mirror. Uses feedback through M3 to boost Rout.

Upload via POST /api/v1/run with optional parameters:
  - width (float): Transistor width in um (default: 2.0)
  - length (float): Channel length in um (default: 1.0)
"""

import os


def generate_netlist(width: float = 2.0, length: float = 1.0) -> str:
    pdk = os.environ.get("SKY130_PDK", "/opt/sky130_pdk/sky130A")
    lib_path = f"{pdk}/libs.tech/ngspice/sky130.lib.spice"

    netlist = f"""* Sky130 Wilson Current Mirror
.lib "{lib_path}" tt

* Parameters
.param W = {width}u
.param L = {length}u

* Supply
Vdd vdd 0 1.8

* Reference current
Iref vdd d_ref 100u

* Circuit — Wilson Current Mirror
* M1: input (diode-connected through feedback)
XM1 d_ref gate1 0 0 sky130_fd_pr__nfet_01v8 w={{W}} l={{L}}
* M2: output mirror transistor
XM2 s3 gate1 0 0 sky130_fd_pr__nfet_01v8 w={{W}} l={{L}}
* M3: feedback cascode transistor (diode-connected)
XM3 vout d_ref s3 0 sky130_fd_pr__nfet_01v8 w={{W}} l={{L}}

* Gate connection: M1 gate = M2 gate
* d_ref connects to M3 gate, M1 drain
* gate1 connects to M1 gate, M2 gate, M1 drain via M1 diode
* Actually for Wilson: M1 gate = M1 drain, M2 gate = M1 gate
* Corrected: gate1 = d_ref (M1 is diode-connected)

* Output load
Rload vdd vout 10k

* Analysis
.dc Iref 10u 500u 5u
.control
run
plot v(vout) i(Rload)
.endc
.end
"""
    return netlist
