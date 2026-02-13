"""Sky130 NMOS Primitive Wrapper"""

ROLE = "DEVICE"
PORTS = ["d", "g", "s", "b"]
DEFAULT_PARAMS = {"w": 1.0, "l": 0.15, "nf": 1}

def generate_netlist(params: dict) -> str:
    w = params.get("w", 1.0)
    l = params.get("l", 0.15)
    nf = params.get("nf", 1)
    # Using Sky130 primitive
    return f"XM1 {{d}} {{g}} {{s}} {{b}} sky130_fd_pr__nfet_01v8 w={w}u l={l}u nf={nf}"
