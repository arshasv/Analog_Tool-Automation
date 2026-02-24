"""
Sky130 Bandgap Voltage Reference (BGR) - Netlist Generator

Standardized with scale=1u compatibility and high-fidelity analysis hints.
"""

import os

def generate_netlist(w_mirror: float = 5.0, l_mirror: float = 1.0,
                     r1: float = 10000, r2: float = 30000) -> str:
    pdk = os.environ.get("SKY130_PDK", "/opt/sky130_pdk/sky130A")

    netlist = f"""* Sky130 Bandgap Voltage Reference
* Generator: bandgap_reference.py
* @AC_SOURCE: Vdd
* @AC_EXPR: vdb(vref)
* @TRAN_EXPR: v(vref)
* @DC_EXPR: v(vref)

* Parameters (scale=1u is applied by orchestrator)
.param W_m = {w_mirror}
.param L_m = {l_mirror}
.param R1_val = {r1}
.param R2_val = {r2}

* Supply
Vdd vdd 0 DC 1.8 pulse(0 1.8 1u 1n 1n 50u 100u) AC 1

* PMOS Current Mirror
XM1 branch1 branch1 vdd vdd sky130_fd_pr__pfet_01v8 w={{W_m}} l={{L_m}}
XM2 branch2 branch1 vdd vdd sky130_fd_pr__pfet_01v8 w={{W_m}} l={{L_m}}
XM3 vref branch1 vdd vdd sky130_fd_pr__pfet_01v8 w={{W_m}} l={{L_m}}

* Branch 1: Single BJT (1x area)
XQ1 branch1 0 0 0 sky130_fd_pr__pnp_05v5_W3p40L3p40

* Branch 2: PTAT generation
R1 branch2 e2 {{R1_val}}
XQ2a e2 0 0 0 sky130_fd_pr__pnp_05v5_W3p40L3p40
XQ2b e2 0 0 0 sky130_fd_pr__pnp_05v5_W3p40L3p40
XQ2c e2 0 0 0 sky130_fd_pr__pnp_05v5_W3p40L3p40
XQ2d e2 0 0 0 sky130_fd_pr__pnp_05v5_W3p40L3p40
XQ2e e2 0 0 0 sky130_fd_pr__pnp_05v5_W3p40L3p40
XQ2f e2 0 0 0 sky130_fd_pr__pnp_05v5_W3p40L3p40
XQ2g e2 0 0 0 sky130_fd_pr__pnp_05v5_W3p40L3p40
XQ2h e2 0 0 0 sky130_fd_pr__pnp_05v5_W3p40L3p40

* Output branch: summing Vbe + PTAT*R2
R2 vref e_out {{R2_val}}
XQ3 e_out 0 0 0 sky130_fd_pr__pnp_05v5_W3p40L3p40

* Load Capacitor
Cout vref 0 1p

* Analysis
.dc temp -40 125 1
.ac dec 100 10 100Meg
.tran 1n 20u
.end
"""
    return netlist
