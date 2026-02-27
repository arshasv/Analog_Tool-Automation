"""Sky130 Resistor Primitive Wrapper"""

ROLE = "PASSIVE"
PORTS = ["n1", "n2"]
DEFAULT_PARAMS = {"r": 1000}

def generate_netlist(params: dict) -> str:
    r = params.get("r", 1000)
    name = params.get("name", "R1")
    # Using high-sheet-rho poly resistor or ideal for now
    return f"{name} {{n1}} {{n2}} {r}"
