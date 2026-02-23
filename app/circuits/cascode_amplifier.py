"""
Sky130 Telescopic Cascode OTA - Netlist Generator

True differential telescopic cascode operational transconductance amplifier.
High-gain single-stage OTA with stacked cascode devices for high output impedance.

Upload via POST /api/v1/run with optional parameters:
  - w_diff    (float): Differential pair width in um (default: 10.0)
  - w_cascode (float): Cascode transistor width in um (default: 5.0)
  - w_load    (float): Active load width in um (default: 20.0)
  - w_bias    (float): Bias transistor width in um (default: 2.0)
  - l_diff    (float): Diff pair length in um (default: 1.0)
  - l_cascode (float): Cascode length in um (default: 1.0)
  - i_tail    (float): Tail current in uA (default: 20.0)
  - vbias_n   (float): NMOS cascode bias voltage (default: 1.1)
  - vbias_p   (float): PMOS cascode bias voltage (default: 0.7)
"""

import os


def generate_netlist(w_diff: float = 10.0, w_cascode: float = 5.0,
                     w_load: float = 20.0, w_bias: float = 2.0,
                     l_diff: float = 1.0, l_cascode: float = 1.0,
                     i_tail: float = 20.0, vbias_n: float = 1.1,
                     vbias_p: float = 0.7) -> str:

    pdk = os.environ.get("SKY130_PDK", "/opt/sky130_pdk/sky130A")

    netlist = f"""* Sky130 Telescopic Cascode OTA
* Generator: cascode_amplifier.py
* @AC_SOURCE: Vin_p
* @AC_EXPR: vdb(vout)
* @TRAN_EXPR: v(vout)
* @DC_EXPR: v(vout)

* -----------------------------------------------------------------------
* Supply
* -----------------------------------------------------------------------
Vdd vdd 0 1.8

* -----------------------------------------------------------------------
* Bias voltages
* -----------------------------------------------------------------------
Vbias_n vbias_n 0 {vbias_n}
Vbias_p vbias_p 0 {vbias_p}

* -----------------------------------------------------------------------
* Differential input
* -----------------------------------------------------------------------
Vin_p vin_p 0 DC 0.9 pulse(0.89 0.91 1u 100n 100n 2u 5u) AC 0.5
Vin_n vin_n 0 DC 0.9 AC -0.5

* -----------------------------------------------------------------------
* Tail current source
* -----------------------------------------------------------------------
Ibias_tail tail 0 DC {i_tail}u

* -----------------------------------------------------------------------
* Telescopic Cascode OTA
* -----------------------------------------------------------------------

* --- NMOS input diff pair ---
XM1 node1 vin_n tail 0 sky130_fd_pr__nfet_01v8 w={w_diff}u l={l_diff}u
XM2 node2 vin_p tail 0 sky130_fd_pr__nfet_01v8 w={w_diff}u l={l_diff}u

* --- NMOS cascode devices ---
XM3 out_n vbias_n node1 0 sky130_fd_pr__nfet_01v8 w={w_cascode}u l={l_cascode}u
XM4 vout  vbias_n node2 0 sky130_fd_pr__nfet_01v8 w={w_cascode}u l={l_cascode}u

* --- PMOS cascode devices ---
XM7 out_n vbias_p cm_n vdd sky130_fd_pr__pfet_01v8 w={w_load}u l={l_cascode}u
XM8 vout  vbias_p v_load_p vdd sky130_fd_pr__pfet_01v8 w={w_load}u l={l_cascode}u

* --- PMOS active-load current mirror (Top level) ---
XM5 cm_n     cm_n vdd vdd sky130_fd_pr__pfet_01v8 w={w_load}u l={l_cascode}u
XM6 v_load_p cm_n vdd vdd sky130_fd_pr__pfet_01v8 w={w_load}u l={l_cascode}u

* -----------------------------------------------------------------------
* Output load capacitor
* -----------------------------------------------------------------------
CL vout 0 0.5p

* -----------------------------------------------------------------------
* Analyses (stripped and re-injected by the orchestrator)
* -----------------------------------------------------------------------
.dc Vin_p 0.8 1.0 0.002
.ac dec 50 10 100Meg
.tran 1n 30u
.end
"""
    return netlist
