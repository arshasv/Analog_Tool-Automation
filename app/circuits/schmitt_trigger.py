"""
Sky130 Schmitt Trigger - Netlist Generator

CMOS Schmitt trigger with hysteresis. Provides noise immunity
by having different switching thresholds for rising and falling
edges. Used in clock cleanup, button debouncing, and
noisy-signal conditioning.

Upload via POST /api/v1/run with optional parameters:
  - w_n (float): NMOS main width in um (default: 1.0)
  - w_p (float): PMOS main width in um (default: 2.0)
  - w_nfb (float): NMOS feedback width in um (default: 0.5)
  - w_pfb (float): PMOS feedback width in um (default: 1.0)
  - l (float): Channel length in um (default: 0.15)
"""

import os


def generate_netlist(w_n: float = 1.0, w_p: float = 2.0,
                     w_nfb: float = 0.5, w_pfb: float = 1.0,
                     l: float = 0.15) -> str:
    pdk = os.environ.get("SKY130_PDK", "/opt/sky130_pdk/sky130A")
    lib_path = f"{pdk}/libs.tech/ngspice/sky130.lib.spice"

    netlist = f"""* Sky130 CMOS Schmitt Trigger
* @AC_SOURCE: Vin
* @AC_EXPR: vdb(vout)
* @TRAN_EXPR: v(vout)
* @DC_EXPR: v(vout)
.lib "{lib_path}" tt

* Parameters
.param W_n = {w_n}u
.param W_p = {w_p}u
.param W_nfb = {w_nfb}u
.param W_pfb = {w_pfb}u
.param L = {l}u

* Supply
Vdd vdd 0 1.8

* Input: Slow triangular pulse to see hysteresis
Vin vin 0 pulse(0 1.8 1u 5u 5u 1u 12u) AC 1

* === Schmitt Trigger ===
XM1 vout vin vdd vdd sky130_fd_pr__pfet_01v8 w={{W_p}} l={{L}}
XM2 n1 vout vdd vdd sky130_fd_pr__pfet_01v8 w={{W_pfb}} l={{L}}
XM3 vout vin n2 0 sky130_fd_pr__nfet_01v8 w={{W_n}} l={{L}}
XM4 n2 vout 0 0 sky130_fd_pr__nfet_01v8 w={{W_nfb}} l={{L}}

* Load
Cload vout 0 10f

* Analysis
.dc Vin 0 1.8 0.001
.ac dec 50 10 10G
.tran 10n 20u
.end
"""
    return netlist
