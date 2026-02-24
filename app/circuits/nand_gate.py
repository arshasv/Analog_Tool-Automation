"""
Sky130 CMOS NAND Gate - Netlist Generator

Standardized with scale=1u compatibility and high-fidelity analysis hints.
"""

import os

def generate_netlist(w_n: float = 2.0, w_p: float = 2.0,
                     l: float = 0.15) -> str:
    pdk = os.environ.get("SKY130_PDK", "/opt/sky130_pdk/sky130A")

    netlist = f"""* Sky130 CMOS 2-Input NAND Gate
* Generator: nand_gate.py
* @AC_SOURCE: Va
* @AC_EXPR: vdb(vout)
* @TRAN_EXPR: v(vout)
* @DC_EXPR: v(vout)

* Parameters (scale=1u is applied by orchestrator)
.param W_n = {w_n}
.param W_p = {w_p}
.param L = {l}

* Supply & Stimulus
Vdd vdd 0 1.8
Va a 0 DC 0.9 pulse(0 1.8 1u 1n 1n 5u 10u) AC 1
Vb b 0 DC 1.8 pulse(0 1.8 1u 1n 1n 10u 20u)

* Circuit Implementation
* Series NMOS pull-down
XM1 vout a mid 0 sky130_fd_pr__nfet_01v8 w={{W_n}} l={{L}}
XM2 mid b 0 0 sky130_fd_pr__nfet_01v8 w={{W_n}} l={{L}}
* Parallel PMOS pull-up
XM3 vout a vdd vdd sky130_fd_pr__pfet_01v8 w={{W_p}} l={{L}}
XM4 vout b vdd vdd sky130_fd_pr__pfet_01v8 w={{W_p}} l={{L}}

* Load
Cload vout 0 10f

* Analysis
.dc Va 0 1.8 0.01
.ac dec 100 10 10G
.tran 1n 40u
.end
"""
    return netlist
