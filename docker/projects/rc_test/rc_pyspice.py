from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *

circuit = Circuit("RC Transient (Auto)")

circuit.V('1', 'vin', circuit.gnd, 5@u_V)
circuit.R('1', 'vin', 'vout', 1@u_kOhm)
circuit.C('1', 'vout', circuit.gnd, 1@u_uF)

circuit.raw_spice += """
.tran 1u 10m
.control
run
wrdata rc_tran.csv time v(vout)
.endc
"""

with open("rc_auto.spice", "w") as f:
    f.write(str(circuit))

print("✔ Generated rc_auto.spice")
