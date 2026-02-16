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
.lib "{lib_path}" tt

* Supply (Defaults)
Vdd vdd 0 1.8
Vcm vcm 0 0.9
* Differential small-signal excitation around common-mode
Vinp vinp vcm AC 0.5
Vinn vinn vcm AC -0.5

* Current Bias (use i_tail_A in A; set by pipeline from i_tail in uA)
Itail vs 0 {{i_tail_A}}

* Stage 1: Diff Pair with Active Load
XM1 d1 vinp vs 0 sky130_fd_pr__nfet_01v8 w={{w_diff}} l={{l_diff}}
XM2 d2 vinn vs 0 sky130_fd_pr__nfet_01v8 w={{w_diff}} l={{l_diff}}
XM3 d1 d1 vdd vdd sky130_fd_pr__pfet_01v8 w={{w_load}} l={{l_load}}
XM4 d2 d1 vdd vdd sky130_fd_pr__pfet_01v8 w={{w_load}} l={{l_load}}

* Stage 2: Common Source Gain Stage
XM5 vout d2 0 0 sky130_fd_pr__nfet_01v8 w={{w_out}} l={{l_out}}
XM6 vout vbias2 vdd vdd sky130_fd_pr__pfet_01v8 w={{w_out}} l={{l_out}}
Vbias2 vbias2 0 1.0

* Miller Compensation (cc in pF -> use cc_F in F)
Cc d2 vout {{cc_F}}

* Load
CL vout 0 2p
.end
"""
    return netlist
