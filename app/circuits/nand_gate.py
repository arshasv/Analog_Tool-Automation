"""
Sky130 CMOS NAND Gate - Netlist Generator

Two-input NAND gate. Universal gate — any logic function
can be built from NANDs. Series NMOS, parallel PMOS.

Upload via POST /api/v1/run with optional parameters:
  - w_n (float): NMOS width in um (default: 2.0)
  - w_p (float): PMOS width in um (default: 2.0)
  - l (float): Channel length in um (default: 0.15)
"""

import os


def generate_netlist(w_n: float = 2.0, w_p: float = 2.0,
                     l: float = 0.15) -> str:
    pdk = os.environ.get("SKY130_PDK", "/opt/sky130_pdk/sky130A")
    lib_path = f"{pdk}/libs.tech/ngspice/sky130.lib.spice"

    netlist = f"""* Sky130 CMOS 2-Input NAND Gate
* @AC_SOURCE: Va
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

* Inputs (staggered pulses)
Va a 0 pulse(0 1.8 1u 1n 1n 5u 10u) AC 1
Vb b 0 pulse(0 1.8 1u 1n 1n 10u 20u)

* Circuit — NAND: series NMOS pull-down, parallel PMOS pull-up
XM1 vout a mid 0 sky130_fd_pr__nfet_01v8 w={{W_n}} l={{L}}
XM2 mid b 0 0 sky130_fd_pr__nfet_01v8 w={{W_n}} l={{L}}
XM3 vout a vdd vdd sky130_fd_pr__pfet_01v8 w={{W_p}} l={{L}}
XM4 vout b vdd vdd sky130_fd_pr__pfet_01v8 w={{W_p}} l={{L}}

* Load
Cload vout 0 10f

* Analysis
.dc Va 0 1.8 0.01
.ac dec 50 10 10G
.tran 1n 40u
.end
"""
    return netlist
