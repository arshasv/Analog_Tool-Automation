"""
Sky130 CMOS Inverter - Netlist Generator

Most fundamental digital/mixed-signal building block.
Used for switching, buffering, and as gain stage in ring oscillators.

Upload via POST /api/v1/run with optional parameters:
  - w_n (float): NMOS width in um (default: 1.0)
  - w_p (float): PMOS width in um (default: 2.0)
  - l (float): Channel length in um (default: 0.15)
  - cload (float): Load capacitance in fF (default: 10.0)
"""

import os


def generate_netlist(w_n: float = 1.0, w_p: float = 2.0,
                     l: float = 0.15, cload: float = 10.0) -> str:
    pdk = os.environ.get("SKY130_PDK", "/opt/sky130_pdk/sky130A")
    lib_path = f"{pdk}/libs.tech/ngspice/sky130.lib.spice"

    netlist = f"""* Sky130 CMOS Inverter
* @AC_SOURCE: Vin
* @AC_EXPR: vdb(vout)
* @TRAN_EXPR: v(vout)
* @DC_EXPR: v(vout)
.lib "{lib_path}" tt

* Parameters
.param W_n = {w_n}u
.param W_p = {w_p}u
.param L = {l}u

* Supply
Vdd vdd 0 1.8

* Stimulus
Vin vin 0 pulse(0 1.8 1u 1n 1n 5u 10u) AC 1

* Circuit
XMn vout vin 0 0 sky130_fd_pr__nfet_01v8 w={{W_n}} l={{L}}
XMp vout vin vdd vdd sky130_fd_pr__pfet_01v8 w={{W_p}} l={{L}}

* Load
Cload vout 0 {cload}f

* Analysis
.dc Vin 0 1.8 0.01
.ac dec 50 10 10G
.tran 1n 20u
.end
"""
    return netlist
