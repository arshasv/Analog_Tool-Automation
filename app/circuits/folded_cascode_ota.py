"""
Sky130 Folded Cascode OTA - Netlist Generator

Single-stage high-gain OTA with wide input common-mode range.
Folds the signal current from NMOS diff pair into PMOS cascode
load, achieving high gain without stacking constraints.

Upload via POST /api/v1/run with optional parameters:
  - w_diff (float): Diff pair NMOS width in um (default: 5.0)
  - w_casc (float): Cascode device width in um (default: 5.0)
  - w_bias (float): Bias transistor width in um (default: 2.0)
  - l (float): Channel length in um (default: 1.0)
  - itail (float): Tail current in A (default: 100e-6)
"""

import os


def generate_netlist(w_diff: float = 5.0, w_casc: float = 5.0,
                     w_bias: float = 2.0, l: float = 1.0,
                     itail: float = 100e-6) -> str:
    pdk = os.environ.get("SKY130_PDK", "/opt/sky130_pdk/sky130A")
    lib_path = f"{pdk}/libs.tech/ngspice/sky130.lib.spice"

    netlist = f"""* Sky130 Folded Cascode OTA
* @AC_SOURCE: Vinp
* @AC_EXPR: vdb(vout)
* @TRAN_EXPR: v(vout)
* @DC_EXPR: v(vout)
.lib "{lib_path}" tt

* Parameters
.param W_diff = {w_diff}u
.param W_casc = {w_casc}u
.param W_bias = {w_bias}u
.param L = {l}u

* Supply
Vdd vdd 0 1.8

* Inputs
Vcm vcm 0 DC 0.9
Vinp vinp vcm pulse(-0.01 0.01 1u 1n 1n 5u 10u) AC 0.5
Vinn vinn vcm AC -0.5

* Bias voltages
Vbn vbn 0 0.7
Vbp vbp 0 1.1
Vbcn vbcn 0 0.9
Vbcp vbcp 0 0.9

* === NMOS Differential Pair ===
Itail vs 0 {itail}
XM1 d1 vinp vs 0 sky130_fd_pr__nfet_01v8 w={{W_diff}} l={{L}}
XM2 d2 vinn vs 0 sky130_fd_pr__nfet_01v8 w={{W_diff}} l={{L}}

* === Folding Current Sources (PMOS) ===
XM3 d1 vbp vdd vdd sky130_fd_pr__pfet_01v8 w={{W_bias}} l={{L}}
XM4 d2 vbp vdd vdd sky130_fd_pr__pfet_01v8 w={{W_bias}} l={{L}}

* === PMOS Cascode Load ===
XM5 cas_p1 vbcp d1 vdd sky130_fd_pr__pfet_01v8 w={{W_casc}} l={{L}}
XM6 cas_p2 vbcp d2 vdd sky130_fd_pr__pfet_01v8 w={{W_casc}} l={{L}}

* === NMOS Cascode (output) ===
XM7 vout vbcn cas_n1 0 sky130_fd_pr__nfet_01v8 w={{W_casc}} l={{L}}
XM8 cas_p1 vbn 0 0 sky130_fd_pr__nfet_01v8 w={{W_bias}} l={{L}}
XM9 cas_n1 vbn 0 0 sky130_fd_pr__nfet_01v8 w={{W_bias}} l={{L}}

* Output node is at the drain of M7 = drain of M6
XM10 vout vbcn cas_p2 0 sky130_fd_pr__nfet_01v8 w={{W_casc}} l={{L}}

* Output load
CL vout 0 5p

* Analysis
.dc Vinp 0.85 0.95 0.001
.ac dec 50 10 1G
.tran 10n 20u
.end
"""
    return netlist
