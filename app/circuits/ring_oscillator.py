"""
Sky130 Ring Oscillator (VCO) - Netlist Generator

Standardized with scale=1u compatibility and high-fidelity analysis hints.
"""

import os

def generate_netlist(stages: int = 5, w_n: float = 1.0,
                     w_p: float = 2.0, l: float = 0.15) -> str:
    pdk = os.environ.get("SKY130_PDK", "/opt/sky130_pdk/sky130A")

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
* Generator: ring_oscillator.py
* @AC_SOURCE: Vdd
* @AC_EXPR: vdb(n0)
* @TRAN_EXPR: v(n0)
* @DC_EXPR: v(n0)

* Parameters (scale=1u is applied by orchestrator)
.param W_n = {w_n}
.param W_p = {w_p}
.param L = {l}

* Supply (Kickstart pulse to ensure start)
Vdd vdd 0 DC 1.8 pulse(0 1.8 1n 1n 1n 100u 200u) AC 1

* Initial condition to break symmetry
.ic v(n0)=0

* Circuit Implementation
{inverter_block}

* Analysis
.dc Vdd 1.0 1.8 0.01
.ac dec 100 10 10G
.tran 0.05n 5u
.end
"""
    return netlist
