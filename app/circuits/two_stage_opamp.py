"""
Sky130 Parametric Two-Stage Op-Amp — Architecture Synthesis Version

TOPOLOGY = {
  "input": "diff_n",
  "gain": "two_stage",
  "load": "mirror",
  "comp": "miller"
}
"""

import os

def generate_netlist(w_diff: float = 5.0, w_load: float = 10.0,
                     w_out: float = 20.0, l_diff: float = 0.5,
                     l_load: float = 0.5, l_out: float = 0.5,
                     cc: float = 1.0, i_tail: float = 50.0) -> str:
    """
    Parametric netlist generator.
    Note: Values passed from orchestrator are in um (for W/L) or uA (for current).
    """
    pdk = os.environ.get("SKY130_PDK", "/opt/sky130_pdk/sky130A")
    lib_path = f"{pdk}/libs.tech/ngspice/sky130.lib.spice"

    netlist = f"""* Sky130 Parametric Two-Stage Op-Amp
* @AC_SOURCE: Vinp
* @AC_EXPR: vdb(vout)
* @TRAN_EXPR: v(vout)
* @DC_EXPR: v(vout)
.lib "{lib_path}" tt

* Supply
Vdd vdd 0 1.8
Vcm vcm 0 0.9

* Balanced Stimulus: DC bias + AC + Pulse
Vinp vinp vcm pulse(-0.01 0.01 1u 1n 1n 5u 10u) AC 0.5
Vinn vinn vcm AC -0.5

* Current Bias
Itail vs 0 {i_tail}u

* Stage 1: Diff Pair with Active Load
XM1 d1 vinp vs 0 sky130_fd_pr__nfet_01v8 w={w_diff}u l={l_diff}u
XM2 d2 vinn vs 0 sky130_fd_pr__nfet_01v8 w={w_diff}u l={l_diff}u
XM3 d1 d1 vdd vdd sky130_fd_pr__pfet_01v8 w={w_load}u l={l_load}u
XM4 d2 d1 vdd vdd sky130_fd_pr__pfet_01v8 w={w_load}u l={l_load}u

* Stage 2: Common Source Gain Stage
XM5 vout d2 0 0 sky130_fd_pr__nfet_01v8 w={w_out}u l={l_out}u
XM6 vout vbias2 vdd vdd sky130_fd_pr__pfet_01v8 w={w_out}u l={l_out}u
Vbias2 vbias2 0 1.0

* Miller Compensation
Cc d2 vout {cc}p

* Load
CL vout 0 2p

* Analysis
.dc Vinp 0.8 1.0 0.001
.ac dec 50 10 100Meg
.tran 10n 20u
.end
"""
    return netlist
