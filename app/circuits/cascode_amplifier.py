"""
Sky130 Telescopic Cascode Amplifier - Netlist Generator

High-gain single-stage amplifier. Stacked NMOS cascode provides
high output impedance → high voltage gain (60-80 dB typical).

Upload via POST /api/v1/run with optional parameters:
  - w_input (float): Input transistor width in um (default: 5.0)
  - w_cascode (float): Cascode transistor width in um (default: 5.0)
  - l (float): Channel length in um (default: 0.5)
  - vbias (float): Cascode gate bias voltage (default: 1.2)
"""

import os


def generate_netlist(w_input: float = 5.0, w_cascode: float = 5.0,
                     l: float = 0.5, vbias: float = 1.2) -> str:
    pdk = os.environ.get("SKY130_PDK", "/opt/sky130_pdk/sky130A")
    lib_path = f"{pdk}/libs.tech/ngspice/sky130.lib.spice"

    netlist = f"""* Sky130 Telescopic Cascode Amplifier
* @AC_SOURCE: Vin
* @AC_EXPR: vdb(vout)
* @TRAN_EXPR: v(vout)
* @DC_EXPR: v(vout)
.lib "{lib_path}" tt

* Parameters
.param W_in = {w_input}u
.param W_cas = {w_cascode}u
.param L = {l}u

* Supply
Vdd vdd 0 1.8

* Bias and Stimulus
Vbias vbias 0 {vbias}
Vin vin 0 pulse(0.85 0.95 1u 1n 1n 5u 10u) DC 0.9 AC 1

* Circuit — Telescopic Cascode
* Input transistor M1
XM1 mid vin 0 0 sky130_fd_pr__nfet_01v8 w={{W_in}} l={{L}}
* Cascode transistor M2
XM2 vout vbias mid 0 sky130_fd_pr__nfet_01v8 w={{W_cas}} l={{L}}
* PMOS load (diode-connected)
XM3 vout vout vdd vdd sky130_fd_pr__pfet_01v8 w={{W_in}} l={{L}}

* Load Capacitor
CL vout 0 0.5p

* Analysis
.dc Vin 0.6 1.2 0.01
.ac dec 50 10 1G
.tran 10n 20u
.end
"""
    return netlist
