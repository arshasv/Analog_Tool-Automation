"""
Sky130 Level Shifter - Netlist Generator

Cross-coupled PMOS level shifter. Converts logic levels
from a low-voltage domain (VDDL) to a high-voltage domain (VDDH).
Essential in multi-voltage-domain SoCs.

Upload via POST /api/v1/run with optional parameters:
  - w_n (float): NMOS width in um (default: 1.0)
  - w_p (float): PMOS width in um (default: 2.0)
  - l (float): Channel length in um (default: 0.15)
  - vddl (float): Low-voltage supply in V (default: 1.0)
  - vddh (float): High-voltage supply in V (default: 1.8)
"""

import os


def generate_netlist(w_n: float = 1.0, w_p: float = 2.0,
                     l: float = 0.15, vddl: float = 1.0,
                     vddh: float = 1.8) -> str:
    pdk = os.environ.get("SKY130_PDK", "/opt/sky130_pdk/sky130A")
    lib_path = f"{pdk}/libs.tech/ngspice/sky130.lib.spice"

    netlist = f"""* Sky130 Cross-Coupled PMOS Level Shifter
* @AC_SOURCE: Vin
* @AC_EXPR: vdb(vout)
* @TRAN_EXPR: v(vout)
* @DC_EXPR: v(vout)
.lib "{lib_path}" tt

* Parameters
.param W_n = {w_n}u
.param W_p = {w_p}u
.param L = {l}u

* Supplies
Vddl vddl 0 {vddl}
Vddh vddh 0 {vddh}

* Input (low-voltage domain)
Vin in 0 pulse(0 {vddl} 1u 1n 1n 5u 10u) AC 1

* Inverter to generate complementary input (low domain)
XMn_inv in_b in 0 0 sky130_fd_pr__nfet_01v8 w={{W_n}} l={{L}}
XMp_inv in_b in vddl vddl sky130_fd_pr__pfet_01v8 w={{W_p}} l={{L}}

* === Cross-Coupled Level Shifter ===
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
.ac dec 50 10 10G
.tran 1n 20u
.end
"""
    return netlist
