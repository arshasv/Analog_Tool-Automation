"""
Sky130 Comparator - Netlist Generator

Open-loop differential comparator. Compares two analog voltages
and produces a rail-to-rail digital output.

Upload via POST /api/v1/run with optional parameters:
  - w_diff (float): Diff pair width in um (default: 2.0)
  - w_load (float): Load transistor width in um (default: 4.0)
  - l (float): Channel length in um (default: 0.5)
  - itail (float): Tail current in A (default: 20e-6)
"""

import os


def generate_netlist(w_diff: float = 2.0, w_load: float = 4.0,
                     l: float = 0.5, itail: float = 20e-6) -> str:
    pdk = os.environ.get("SKY130_PDK", "/opt/sky130_pdk/sky130A")
    lib_path = f"{pdk}/libs.tech/ngspice/sky130.lib.spice"

    netlist = f"""* Sky130 Comparator
* @AC_SOURCE: Vin
* @AC_EXPR: vdb(vout)
* @TRAN_EXPR: v(vout)
* @DC_EXPR: v(vout)
.lib "{lib_path}" tt

* Parameters
.param W_diff = {w_diff}u
.param W_load = {w_load}u
.param L = {l}u

* Supply
Vdd vdd 0 1.8

* Inputs
Vref vref 0 0.9
Vin vin 0 pulse(0.5 1.3 10u 1n 1n 40u 80u) DC 0.9 AC 1

* === Differential Pair ===
Itail vs 0 {itail}
XM1 d1 vin vs 0 sky130_fd_pr__nfet_01v8 w={{W_diff}} l={{L}}
XM2 d2 vref vs 0 sky130_fd_pr__nfet_01v8 w={{W_diff}} l={{L}}

* PMOS active load (current mirror)
XM3 d1 d1 vdd vdd sky130_fd_pr__pfet_01v8 w={{W_load}} l={{L}}
XM4 d2 d1 vdd vdd sky130_fd_pr__pfet_01v8 w={{W_load}} l={{L}}

* === Output Inverter (sharpens transition) ===
XM5 vout d2 0 0 sky130_fd_pr__nfet_01v8 w={{W_diff}} l={{L}}
XM6 vout d2 vdd vdd sky130_fd_pr__pfet_01v8 w={{W_load}} l={{L}}

* Load Capacitor
CL vout 0 0.1p

* Analysis
.dc Vin 0 1.8 0.01
.ac dec 50 10 100Meg
.tran 1n 150u
.end
"""
    return netlist
