
"""Test circuit"""
PARAMETERS = {
    "iref": 1e-5,
    "vdd": 1.8,
}

def build_circuit(**kwargs):
    return {"netlist": "minimal circuit"}
