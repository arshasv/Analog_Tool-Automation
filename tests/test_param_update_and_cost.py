"""Lightweight tests for optimization helper modules.

These tests do not invoke ngspice; they only validate that the
parameter parsing / update logic and cost function behave sensibly.
"""

from app.core.optimization.param_update import extract_wl_variables, apply_wl_assignment
from app.core.optimization.cost_function import compute_cost


def test_extract_and_apply_wl_parameters_roundtrip():
    base = """* Simple netlist\n.param W_n = 2.0\n.param L = 0.5\nXM1 d g s b sky130_fd_pr__nfet_01v8 w={W_n} l={L}\n.end\n"""

    vars_ = extract_wl_variables(base)
    assert "W_n" in vars_
    assert "L" in vars_

    assignment = {"W_n": 4.0, "L": 1.0}
    updated = apply_wl_assignment(base, assignment)

    assert ".param W_n = 4.0" in updated
    assert ".param L = 1.0" in updated


def test_compute_cost_basic():
    metrics = {"current": 100e-6, "gain": 40.0, "power": 1e-3}
    targets = {"current": 100e-6, "gain": 40.0}
    weights = {"w1": 1.0, "w2": 1.0, "w3": 1.0}

    c = compute_cost(metrics, targets, weights, power_max=2e-3)
    # Perfect tracking, under power budget -> near zero cost
    assert c >= 0.0
    assert c < 1e-6
