"""
Sky130 Low Dropout Regulator (LDO) - Netlist Generator

Standardized with scale=1u compatibility and high-fidelity analysis hints.
"""

import os

def generate_netlist(w_pass: float = 100.0, l_pass: float = 0.5,
                     w_ea: float = 5.0, l_ea: float = 1.0,
                     r1: float = 100000, r2: float = 100000,
                     cl: float = 1.0) -> str:
    pdk = os.environ.get("SKY130_PDK", "/opt/sky130_pdk/sky130A")

    netlist = f"""* Sky130 Low Dropout Regulator (LDO)
* Generator: ldo_regulator.py
* @AC_SOURCE: Vdd
* @AC_EXPR: vdb(vout)
* @TRAN_EXPR: v(vout)
* @DC_EXPR: v(vout)

* Parameters (scale=1u is applied by orchestrator)
.param W_pass = {w_pass}
.param L_pass = {l_pass}
.param W_ea = {w_ea}
.param L_ea = {l_ea}

* Unregulated supply
Vdd vdd 0 DC 3.3 pulse(3.0 3.6 10u 1n 1n 40u 80u) AC 1
Vref vref 0 1.2

* Error Amplifier (simple diff pair)
Itail ea_tail 0 50u
XM1 ea_out1 vref ea_tail 0 sky130_fd_pr__nfet_01v8 w={{W_ea}} l={{L_ea}}
XM2 ea_out vfb ea_tail 0 sky130_fd_pr__nfet_01v8 w={{W_ea}} l={{L_ea}}
XM3 ea_out1 ea_out1 vdd vdd sky130_fd_pr__pfet_01v8 w={{W_ea}} l={{L_ea}}
XM4 ea_out ea_out1 vdd vdd sky130_fd_pr__pfet_01v8 w={{W_ea}} l={{L_ea}}

* Pass Transistor (PMOS)
XM_pass vout ea_out vdd vdd sky130_fd_pr__pfet_01v8 w={{W_pass}} l={{L_pass}}

* Feedback Network
R1 vout vfb {r1}
R2 vfb 0 {r2}

* Output Capacitor & Load
CL vout 0 {cl}u
Rload vout 0 100

* Analysis
.dc Vdd 2.0 5.0 0.1
.ac dec 100 1 100Meg
.tran 10n 150u
.end
"""
    return netlist
