"""
Sky130 Folded Cascode OTA - Netlist Generator

Standardized with scale=1u compatibility and high-fidelity analysis hints.
"""

import os

def generate_netlist(w_diff: float = 5.0, w_casc: float = 5.0,
                     w_bias: float = 2.0, l: float = 1.0,
                     itail: float = 100e-6) -> str:
    pdk = os.environ.get("SKY130_PDK", "/opt/sky130_pdk/sky130A")

    netlist = f"""* Sky130 Folded Cascode OTA
* Generator: folded_cascode_ota.py
* @AC_SOURCE: Vinp
* @AC_EXPR: vdb(vout)
* @TRAN_EXPR: v(vout)
* @DC_EXPR: v(vout)

* Parameters (scale=1u is applied by orchestrator)
.param W_diff = {w_diff}
.param W_casc = {w_casc}
.param W_bias = {w_bias}
.param L = {l}

* Supply & Stimulus
Vdd vdd 0 1.8
Vcm vcm 0 DC 0.9
Vinp vinp vcm DC 0 AC 0.5 pulse(-0.01 0.01 1u 1n 1n 5u 10u)
Vinn vinn vcm DC 0 AC -0.5

* Bias voltages
Vbn vbn 0 0.7
Vbp vbp 0 1.1
Vbcn vbcn 0 0.9
Vbcp vbcp 0 0.9

* NMOS Differential Pair
Itail vs 0 {itail}
XM1 d1 vinp vs 0 sky130_fd_pr__nfet_01v8 w={{W_diff}} l={{L}}
XM2 d2 vinn vs 0 sky130_fd_pr__nfet_01v8 w={{W_diff}} l={{L}}

* Folding Current Sources (PMOS)
XM3 x1 vbp vdd vdd sky130_fd_pr__pfet_01v8 w={{W_bias}} l={{L}}
XM4 x2 vbp vdd vdd sky130_fd_pr__pfet_01v8 w={{W_bias}} l={{L}}

* Connection between diff pair and folding nodes
V1 d1 x1 0
V2 d2 x2 0

* PMOS Cascode Load
XM5 out_n vbcp x1 vdd sky130_fd_pr__pfet_01v8 w={{W_casc}} l={{L}}
XM6 vout  vbcp x2 vdd sky130_fd_pr__pfet_01v8 w={{W_casc}} l={{L}}

* NMOS Cascode Current Mirror Load
XM7 out_n vbcn s1 0 sky130_fd_pr__nfet_01v8 w={{W_casc}} l={{L}}
XM8 vout  vbcn s2 0 sky130_fd_pr__nfet_01v8 w={{W_casc}} l={{L}}
XM9 s1 out_n 0 0 sky130_fd_pr__nfet_01v8 w={{W_bias}} l={{L}}
XM10 s2 out_n 0 0 sky130_fd_pr__nfet_01v8 w={{W_bias}} l={{L}}

* Output load
CL vout 0 5p

* Analysis
.dc Vinp -0.01 0.01 0.0001
.ac dec 100 10 1G
.tran 1n 20u
.end
"""
    return netlist
