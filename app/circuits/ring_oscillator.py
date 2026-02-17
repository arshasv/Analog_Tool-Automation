"""
Sky130 Ring Oscillator (VCO) - Netlist Generator

Odd-number chain of CMOS inverters connected in a ring.
Oscillation frequency depends on gate delay, which is
controlled by supply voltage or transistor sizing.

Upload via POST /api/v1/run with optional parameters:
  - stages (int): Number of inverter stages, must be odd (default: 5)
  - w_n (float): NMOS width in um (default: 1.0)
  - w_p (float): PMOS width in um (default: 2.0)
  - l (float): Channel length in um (default: 0.15)
"""

import os


def generate_netlist(stages: int = 5, w_n: float = 1.0,
                     w_p: float = 2.0, l: float = 0.15) -> str:
    pdk = os.environ.get("SKY130_PDK", "/opt/sky130_pdk/sky130A")
    lib_path = f"{pdk}/libs.tech/ngspice/sky130.lib.spice"

    if stages % 2 == 0:
        stages += 1  # Force odd

    # Build inverter chain
    inv_lines = []
    for i in range(stages):
        in_node = f"n{i}"
        out_node = f"n{(i + 1) % stages}"
        inv_lines.append(f"* Inverter stage {i}")
        inv_lines.append(
            f"XMn{i} {out_node} {in_node} 0 0 "
            f"sky130_fd_pr__nfet_01v8 w={{W_n}} l={{L}}"
        )
        inv_lines.append(
            f"XMp{i} {out_node} {in_node} vdd vdd "
            f"sky130_fd_pr__pfet_01v8 w={{W_p}} l={{L}}"
        )
    inverter_block = "\n".join(inv_lines)

    netlist = f"""* Sky130 {stages}-Stage Ring Oscillator
* @AC_SOURCE: Vdd
* @AC_EXPR: vdb(n0)
* @TRAN_EXPR: v(n0)
* @DC_EXPR: v(n0)
.lib "{lib_path}" tt

* Parameters
.param W_n = {w_n}u
.param W_p = {w_p}u
.param L = {l}u

* Supply (Pulse kickstart)
Vdd vdd 0 pulse(0 1.8 1u 1n 1n 50u 100u) AC 1

* Initial condition
.ic v(n0)=0

* Circuit
{inverter_block}

* Analysis
.dc Vdd 1.2 1.8 0.01
.ac dec 50 10 10G
.tran 0.1n 10u
.end
"""
    return netlist
