"""
Sky130 Telescopic Cascode OTA - Netlist Generator

True differential telescopic cascode operational transconductance amplifier.
High-gain single-stage OTA with stacked cascode devices for high output impedance.
"""

import os

def generate_netlist(w_diff: float = 10.0, w_cascode: float = 5.0,
                     w_load: float = 20.0, w_bias: float = 2.0,
                     l_diff: float = 0.5, l_cascode: float = 0.5,
                     i_tail: float = 20.0, vbias_n: float = 1.1,
                     vbias_p: float = 0.7) -> str:
    """
    Parametric netlist generator for a Telescopic Cascode OTA.
    Optimized for high-gain DC transition and Sky130 PDK compatibility.
    """
    pdk = os.environ.get("SKY130_PDK", "/opt/sky130_pdk/sky130A")

    netlist = f"""* Sky130 Telescopic Cascode OTA
* Generator: cascode_amplifier.py
* @AC_SOURCE: Vin_p
* @AC_EXPR: vdb(vout)
* @TRAN_EXPR: v(vout)
* @DC_EXPR: v(vout)

* -----------------------------------------------------------------------
* Supply & Reference Bias
* -----------------------------------------------------------------------
Vdd vdd 0 1.8
Vcm vcm 0 0.9

* Cascode Bias Voltages (Standard for 1.8V supply)
Vbn vbias_n 0 1.1
Vbp vbias_p 0 0.7

* -----------------------------------------------------------------------
* Differential Input Stimulus
* Vin_p is swept for DC, pulsed for TRAN, and AC excited.
* -----------------------------------------------------------------------
Vin_p vin_p vcm DC 0 AC 0.5 pulse(-0.01 0.01 1u 100n 100n 2u 5u)
Vin_n vin_n vcm DC 0 AC -0.5

* -----------------------------------------------------------------------
* Tail Current Source
* -----------------------------------------------------------------------
Ibias_tail tail 0 DC {i_tail}u

* -----------------------------------------------------------------------
* Telescopic Cascode Core Implementation
* -----------------------------------------------------------------------

* --- NMOS Input Stage ---
XM1 node1 vin_n tail 0 sky130_fd_pr__nfet_01v8 w={w_diff} l={l_diff}
XM2 node2 vin_p tail 0 sky130_fd_pr__nfet_01v8 w={w_diff} l={l_diff}

* --- NMOS Cascode Stage ---
XM3 out_n vbias_n node1 0 sky130_fd_pr__nfet_01v8 w={w_cascode} l={l_cascode}
XM4 vout  vbias_n node2 0 sky130_fd_pr__nfet_01v8 w={w_cascode} l={l_cascode}

* --- PMOS Cascode Stage ---
XM7 out_n vbias_p p_load_n vdd sky130_fd_pr__pfet_01v8 w={w_load} l={l_cascode}
XM8 vout  vbias_p p_load_p vdd sky130_fd_pr__pfet_01v8 w={w_load} l={l_cascode}

* --- PMOS Active Mirror Load ---
* Tie gates to out_n to create a differential-to-single-ended converter
XM5 p_load_n out_n vdd vdd sky130_fd_pr__pfet_01v8 w={w_load} l={l_cascode}
XM6 p_load_p out_n vdd vdd sky130_fd_pr__pfet_01v8 w={w_load} l={l_cascode}

* Output Load Capacitor
CL vout 0 0.5p

* -----------------------------------------------------------------------
* Analysis Commands (Stripped and re-injected by orchestrator)
* -----------------------------------------------------------------------
.dc Vin_p -0.01 0.01 0.0001
.ac dec 100 10 100Meg
.tran 1n 20u
.end
"""
    return netlist
