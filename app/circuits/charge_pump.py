"""
Sky130 Charge Pump (PLL Building Block) - Netlist Generator

Upload via POST /api/v1/run with optional parameters:
  - w_up (float): PMOS UP switch width in um (default: 5.0)
  - w_dn (float): NMOS DN switch width in um (default: 2.5)
  - l (float): Channel length in um (default: 0.5)
  - icp (float): Charge pump current in A (default: 10e-6)
  - c_filter (float): Loop filter cap in pF (default: 50.0)
"""
import os

def generate_netlist(w_up: float = 5.0, w_dn: float = 2.5,
                     l: float = 0.5, icp: float = 10e-6,
                     c_filter: float = 50.0) -> str:
    pdk = os.environ.get("SKY130_PDK", "/opt/sky130_pdk/sky130A")
    lib_path = f"{pdk}/libs.tech/ngspice/sky130.lib.spice"
    c2 = c_filter / 10

    netlist = f"""* Sky130 Charge Pump
* @AC_SOURCE: Vdd
* @AC_EXPR: vdb(vctrl)
* @TRAN_EXPR: v(vctrl)
* @DC_EXPR: v(vctrl)
.lib "{lib_path}" tt

.param W_up = {w_up}u
.param W_dn = {w_dn}u
.param L = {l}u

Vdd vdd 0 1.8
Vup up 0 PULSE(0 1.8 5n 0.1n 0.1n 2n 20n)
Vdn dn 0 PULSE(0 1.8 15n 0.1n 0.1n 2n 20n)
Vup_b up_b 0 PULSE(1.8 0 5n 0.1n 0.1n 2n 20n)

XMp_bias p_src p_bias vdd vdd sky130_fd_pr__pfet_01v8 w={{W_up}} l={{L}}
XMp_sw vctrl up_b p_src vdd sky130_fd_pr__pfet_01v8 w={{W_up}} l={{L}}
XMn_bias n_src n_bias 0 0 sky130_fd_pr__nfet_01v8 w={{W_dn}} l={{L}}
XMn_sw vctrl dn n_src 0 sky130_fd_pr__nfet_01v8 w={{W_dn}} l={{L}}

Ibias_p vdd p_bias {icp}
XMp_diode p_bias p_bias vdd vdd sky130_fd_pr__pfet_01v8 w={{W_up}} l={{L}}
Ibias_n n_bias 0 {icp}
XMn_diode n_bias n_bias 0 0 sky130_fd_pr__nfet_01v8 w={{W_dn}} l={{L}}

C1 vctrl 0 {c_filter}p
R1 vctrl vctrl2 1k
C2 vctrl2 0 {c2}p

.tran 0.1n 100n
.end
"""
    return netlist
