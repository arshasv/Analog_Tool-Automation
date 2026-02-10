"""
Sky130 Two-Stage Miller-Compensated Op-Amp - Netlist Generator

Classic two-stage operational amplifier:
  Stage 1: Differential pair with PMOS active load
  Stage 2: Common-source gain stage
  Compensation: Miller capacitor (Cc) for frequency stability

Upload via POST /api/v1/run with optional parameters:
  - w_diff (float): Diff pair NMOS width in um (default: 5.0)
  - w_load (float): PMOS load width in um (default: 10.0)
  - w_out (float): Output stage NMOS width in um (default: 20.0)
  - l (float): Channel length in um (default: 0.5)
  - cc (float): Miller compensation cap in pF (default: 1.0)
  - itail (float): Tail current in A (default: 50e-6)
"""

import os


def generate_netlist(w_diff: float = 5.0, w_load: float = 10.0,
                     w_out: float = 20.0, l: float = 0.5,
                     cc: float = 1.0, itail: float = 50e-6) -> str:
    pdk = os.environ.get("SKY130_PDK", "/opt/sky130_pdk/sky130A")
    lib_path = f"{pdk}/libs.tech/ngspice/sky130.lib.spice"

    netlist = f"""* Sky130 Two-Stage Miller-Compensated Op-Amp
.lib "{lib_path}" tt

* Parameters
.param W_diff = {w_diff}u
.param W_load = {w_load}u
.param W_out = {w_out}u
.param L = {l}u
.param Cc_val = {cc}p

* Supply
Vdd vdd 0 1.8

* Inputs
Vcm vcm 0 DC 0.9
Vinp vinp vcm AC 1
Vinn vinn vcm DC 0

* === Stage 1: Differential Pair with PMOS Active Load ===
* Tail current source
Itail vs 0 {itail}

* NMOS differential pair
XM1 d1 vinp vs 0 sky130_fd_pr__nfet_01v8 w={{W_diff}} l={{L}}
XM2 d2 vinn vs 0 sky130_fd_pr__nfet_01v8 w={{W_diff}} l={{L}}

* PMOS active load (current mirror)
XM3 d1 d1 vdd vdd sky130_fd_pr__pfet_01v8 w={{W_load}} l={{L}}
XM4 d2 d1 vdd vdd sky130_fd_pr__pfet_01v8 w={{W_load}} l={{L}}

* === Stage 2: Common-Source Output Stage ===
XM5 vout d2 0 0 sky130_fd_pr__nfet_01v8 w={{W_out}} l={{L}}
XM6 vout vbias2 vdd vdd sky130_fd_pr__pfet_01v8 w={{W_out}} l={{L}}

* Bias for output stage PMOS load (diode-connected)
Vbias2 vbias2 0 1.0

* === Miller Compensation ===
Cc d2 vout {{Cc_val}}

* Output load
CL vout 0 5p
RL vout 0 100k

* Analysis
.ac dec 100 1 1G
.control
run
plot vdb(vout) vp(vout)
.endc
.end
"""
    return netlist
