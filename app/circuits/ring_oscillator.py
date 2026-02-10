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
.lib "{lib_path}" tt

* Parameters
.param W_n = {w_n}u
.param W_p = {w_p}u
.param L = {l}u

* Supply
Vdd vdd 0 1.8

* Initial condition to kick-start oscillation
.ic v(n0)=0

* Circuit
{inverter_block}

* Analysis
.tran 0.01n 20n
.control
run
plot v(n0) v(n1)
.endc
.end
"""
    return netlist
