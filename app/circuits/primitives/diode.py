"""Sky130 Diode Primitive Wrapper"""

ROLE = "DEVICE"
PORTS = ["a", "c"]
DEFAULT_PARAMS = {"area": 1.0}

def generate_netlist(params: dict) -> str:
    area = params.get("area", 1.0)
    return f"D1 {{a}} {{c}} sky130_fd_pr__diode_pw2nd_05v5 area={area}"
