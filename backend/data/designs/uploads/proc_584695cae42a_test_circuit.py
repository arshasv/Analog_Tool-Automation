"""Simple test circuit for API"""
def build_circuit(w=2.0, l=0.5, iref=10e-6):
    return {
        "netlist": f"* Test Circuit\n.param W={w} L={l} IREF={iref}",
        "parameters": {"w": w, "l": l, "iref": iref}
    }

PARAMETERS = {
    "w": {"type": "float", "default": 2.0, "description": "Width"},
    "l": {"type": "float", "default": 0.5, "description": "Length"},
    "iref": {"type": "float", "default": 10e-6, "description": "Reference Current"}
}
