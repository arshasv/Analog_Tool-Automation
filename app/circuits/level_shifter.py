"""
Sky130 Level Shifter - Netlist Generator

Standardized with scale=1u compatibility and high-fidelity analysis hints.
"""

import os

def generate_netlist(w_n: float = 1.0, w_p: float = 2.0,
                     l: float = 0.15, vddl: float = 1.0,
                     vddh: float = 1.8) -> str:
    pdk = os.environ.get("SKY130_PDK", "/opt/sky130_pdk/sky130A")

    netlist = f"""* Sky130 Cross-Coupled PMOS Level Shifter
* Generator: level_shifter.py
* @AC_SOURCE: Vin
* @AC_EXPR: vdb(vout)
* @TRAN_EXPR: v(vout)
* @DC_EXPR: v(vout)

* Parameters (scale=1u is applied by orchestrator)
.param W_n = {w_n}
.param W_p = {w_p}
.param L = {l}

* Supplies
Vddl vddl 0 {vddl}
Vddh vddh 0 {vddh}

* Input (low-voltage domain)
Vin in 0 DC {vddl/2} pulse(0 {vddl} 1u 1n 1n 5u 10u) AC 1

* Inverter to generate complementary input (low domain)
XMn_inv in_b in 0 0 sky130_fd_pr__nfet_01v8 w={{W_n}} l={{L}}
XMp_inv in_b in vddl vddl sky130_fd_pr__pfet_01v8 w={{W_p}} l={{L}}

* Circuit Implementation
* NMOS pull-down driven by low-voltage inputs
XMn1 out_b in 0 0 sky130_fd_pr__nfet_01v8 w={{W_n}} l={{L}}
XMn2 vout in_b 0 0 sky130_fd_pr__nfet_01v8 w={{W_n}} l={{L}}

* Cross-coupled PMOS pull-up (high-voltage domain)
XMp1 out_b vout vddh vddh sky130_fd_pr__pfet_01v8 w={{W_p}} l={{L}}
XMp2 vout out_b vddh vddh sky130_fd_pr__pfet_01v8 w={{W_p}} l={{L}}

* Load
Cload vout 0 10f

* Analysis
.dc Vin 0 {vddl} 0.01
.ac dec 100 10 10G
.tran 1n 20u
.end
"""
    return netlist
