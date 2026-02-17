"""
Sky130 Bandgap Voltage Reference (BGR) - Netlist Generator

Generates a temperature-independent ~1.2V reference using the
complementary-to-absolute-temperature (CTAT) of Vbe and
proportional-to-absolute-temperature (PTAT) of delta-Vbe.

Uses Sky130 PNP BJTs (sky130_fd_pr__pnp_05v5_W3p40L3p40)
and PMOS current mirror for biasing.

Upload via POST /api/v1/run with optional parameters:
  - w_mirror (float): PMOS mirror width in um (default: 5.0)
  - l_mirror (float): PMOS mirror length in um (default: 1.0)
  - r1 (float): PTAT resistor in Ohms (default: 10000)
  - r2 (float): Output summing resistor in Ohms (default: 30000)
"""

import os


def generate_netlist(w_mirror: float = 5.0, l_mirror: float = 1.0,
                     r1: float = 10000, r2: float = 30000) -> str:
    pdk = os.environ.get("SKY130_PDK", "/opt/sky130_pdk/sky130A")
    lib_path = f"{pdk}/libs.tech/ngspice/sky130.lib.spice"

    netlist = f"""* Sky130 Bandgap Voltage Reference
* @AC_SOURCE: Vdd
* @AC_EXPR: vdb(vref)
* @TRAN_EXPR: v(vref)
* @DC_EXPR: v(vref)
.lib "{lib_path}" tt

* Parameters
.param W_m = {w_mirror}u
.param L_m = {l_mirror}u
.param R1_val = {r1}
.param R2_val = {r2}

* Supply (Pulse for Transient power-on)
Vdd vdd 0 pulse(0 1.8 1u 1n 1n 50u 100u) AC 1

* === PMOS Current Mirror (forces equal currents in both branches) ===
XM1 branch1 branch1 vdd vdd sky130_fd_pr__pfet_01v8 w={{W_m}} l={{L_m}}
XM2 branch2 branch1 vdd vdd sky130_fd_pr__pfet_01v8 w={{W_m}} l={{L_m}}
XM3 vref branch1 vdd vdd sky130_fd_pr__pfet_01v8 w={{W_m}} l={{L_m}}

* === Branch 1: Single BJT (1x area) ===
XQ1 branch1 0 0 0 sky130_fd_pr__pnp_05v5_W3p40L3p40

* === Branch 2: PTAT generation ===
R1 branch2 e2 {{R1_val}}
XQ2a e2 0 0 0 sky130_fd_pr__pnp_05v5_W3p40L3p40
XQ2b e2 0 0 0 sky130_fd_pr__pnp_05v5_W3p40L3p40
XQ2c e2 0 0 0 sky130_fd_pr__pnp_05v5_W3p40L3p40
XQ2d e2 0 0 0 sky130_fd_pr__pnp_05v5_W3p40L3p40
XQ2e e2 0 0 0 sky130_fd_pr__pnp_05v5_W3p40L3p40
XQ2f e2 0 0 0 sky130_fd_pr__pnp_05v5_W3p40L3p40
XQ2g e2 0 0 0 sky130_fd_pr__pnp_05v5_W3p40L3p40
XQ2h e2 0 0 0 sky130_fd_pr__pnp_05v5_W3p40L3p40

* === Output branch: summing Vbe + PTAT*R2 ===
R2 vref e_out {{R2_val}}
XQ3 e_out 0 0 0 sky130_fd_pr__pnp_05v5_W3p40L3p40

* Load Capacitor for realistic transient
Cout vref 0 1p

* Analysis
.dc temp -40 125 1
.ac dec 50 10 100Meg
.tran 10n 20u
.end
"""
    return netlist
