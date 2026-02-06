"""Simple current mirror circuit"""

PARAMETERS = {
    'iref': 10e-6,
    'w': 2.0,
    'L': 0.5
}

def build_circuit():
    return f"""
* Current Mirror
.include /opt/open_pdks/sky130/sky130A/libs.tech/ngspice/sky130.lib.spice
Vdd vdd 0 DC 1.8
.end
"""
