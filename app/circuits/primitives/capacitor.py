"""Sky130 Capacitor Primitive Wrapper"""

ROLE = "PASSIVE"
PORTS = ["n1", "n2"]
DEFAULT_PARAMS = {"c": 1e-12}

def generate_netlist(params: dict) -> str:
    c = params.get("c", 1e-12)
    name = params.get("name", "C1")
    # c is in Farads, SPICE takes 1p style or raw 1e-12
    return f"{name} {{n1}} {{n2}} {c}"
