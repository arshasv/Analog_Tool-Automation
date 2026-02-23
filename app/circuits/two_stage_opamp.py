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
    Parametric netlist generator for a Two-Stage Op-Amp.
    Standardized for high-gain DC sweep and accurate AC/TRAN analysis.
    """
    pdk = os.environ.get("SKY130_PDK", "/opt/sky130_pdk/sky130A")

    netlist = f"""* Sky130 Parametric Two-Stage Op-Amp
* @AC_SOURCE: Vinp
* @AC_EXPR: vdb(vout)
* @TRAN_EXPR: v(vout)
* @DC_EXPR: v(vout)

* -----------------------------------------------------------------------
* Supply & Bias
* -----------------------------------------------------------------------
Vdd vdd 0 1.8
Vcm vcm 0 0.9

* -----------------------------------------------------------------------
* Stimulus
* Vinp has DC=0.9 for sweep, Pulse for TRAN, and AC for Bode.
* -----------------------------------------------------------------------
Vinp vinp vcm DC 0.9 pulse(-0.01 0.01 1u 1n 1n 5u 10u) AC 0.5
Vinn vinn vcm DC 0.9 AC -0.5

* -----------------------------------------------------------------------
* Tail Current Source
* -----------------------------------------------------------------------
Itail vs 0 DC {i_tail}u

* -----------------------------------------------------------------------
* Op-Amp Core
* -----------------------------------------------------------------------

* Stage 1: NMOS Differential Pair with PMOS Mirror Load
XM1 d1 vinp vs 0 sky130_fd_pr__nfet_01v8 w={w_diff} l={l_diff}
XM2 d2 vinn vs 0 sky130_fd_pr__nfet_01v8 w={w_diff} l={l_diff}
XM3 d1 d1 vdd vdd sky130_fd_pr__pfet_01v8 w={w_load} l={l_load}
XM4 d2 d1 vdd vdd sky130_fd_pr__pfet_01v8 w={w_load} l={l_load}

* Stage 2: PMOS Common Source with NMOS Current Source Load
* (Matched to user's stable configuration)
XM5 vout d2 0 0 sky130_fd_pr__nfet_01v8 w={w_out} l={l_out}
XM6 vout vbias2 vdd vdd sky130_fd_pr__pfet_01v8 w={w_out} l={l_out}
Vbias2 vbias2 0 1.0

* Miller Compensation & Output Load
Cc d2 vout {cc}p
CL vout 0 2p

* -----------------------------------------------------------------------
* Analysis (Stripped and re-injected by orchestrator)
* -----------------------------------------------------------------------
.dc Vinp 0.89 0.91 0.0001
.ac dec 100 10 100Meg
.tran 10n 20u
.end
"""
    return netlist
