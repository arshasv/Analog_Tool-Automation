"""Netlist W/L parameter extraction and update utilities.

This module operates on a SPICE netlist *string* and only modifies the
values of width/length-related parameters (e.g. .param W, .param L,
.param W_M1, explicit "w="/"l=" tokens), leaving the rest of the
netlist untouched.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple
import re


@dataclass
class WLVariable:
    """Represents a single optimization variable bound to W or L.

    name: parameter or symbolic name inside the netlist (e.g. "W_n").
    kind: either "W" or "L".
    value: initial value in micrometers.
    min_value: minimum legal value (DRC / tech constraint).
    max_value: maximum legal value.
    """

    name: str
    kind: str
    value: float
    min_value: float
    max_value: float


_PARAM_RE = re.compile(r"^\s*\.param\s+([A-Za-z_][A-Za-z0-9_]*)\s*=\s*([^\n]+)", re.IGNORECASE)
_W_TOKEN_RE = re.compile(r"(\bw\s*=\s*)([^\s]+)", re.IGNORECASE)
_L_TOKEN_RE = re.compile(r"(\bl\s*=\s*)([^\s]+)", re.IGNORECASE)


def _parse_numeric_with_suffix(token: str) -> float | None:
    """Parse a SPICE numeric with optional unit suffix into micrometers.

    Only a subset of suffixes is supported; unrecognised tokens return None.
    """
    token = token.strip()
    # Strip enclosing braces used for parameter references: {w}
    if token.startswith("{") and token.endswith("}"):
        token = token[1:-1].strip()

    # If token is a plain float, assume it's already in micrometers.
    try:
        return float(token)
    except ValueError:
        pass

    # Extract numeric part and suffix (very simple parser).
    m = re.match(r"([-+]?\d*\.??\d+(?:[eE][-+]?\d+)?)([a-zA-Z]+)", token)
    if not m:
        return None

    value = float(m.group(1))
    suffix = m.group(2).lower()

    scale = {
        "m": 1e6,   # meters -> um
        "u": 1.0,   # um
        "n": 1e-3,  # nm -> um
    }.get(suffix)
    if scale is None:
        return None
    return value * scale


def extract_wl_variables(netlist: str) -> Dict[str, WLVariable]:
    """Scan a netlist string and infer W/L optimization variables.

    We prioritise .param definitions whose names look width/length-like
    (start with "w"/"l" or contain "_w"/"_l"), but also fall back to
    explicit "w="/"l=" tokens on MOS lines.
    """
    variables: Dict[str, WLVariable] = {}

    # Defaults based on Sky130 clamps used in AnalysisOrchestrator.
    W_MIN, W_MAX = 0.42, 50.0   # um
    L_MIN, L_MAX = 0.15, 5.0    # um

    for line in netlist.splitlines():
        m = _PARAM_RE.match(line)
        if not m:
            continue
        name, val_str = m.group(1), m.group(2)
        name_l = name.lower()
        kind: str | None = None
        if name_l.startswith("w") or "_w" in name_l or name_l in {"width", "w"}:
            kind = "W"
        elif name_l.startswith("l") or "_l" in name_l or name_l in {"length", "l"}:
            kind = "L"
        if not kind:
            continue
        parsed = _parse_numeric_with_suffix(val_str)
        if parsed is None:
            continue
        # Clamp into reasonable tech bounds immediately.
        if kind == "W":
            parsed = min(max(parsed, W_MIN), W_MAX)
            min_v, max_v = W_MIN, W_MAX
        else:
            parsed = min(max(parsed, L_MIN), L_MAX)
            min_v, max_v = L_MIN, L_MAX
        variables[name] = WLVariable(name=name, kind=kind, value=parsed, min_value=min_v, max_value=max_v)

    # Fallback: try to infer from explicit w=/l= tokens if no params found.
    if not variables:
        for line in netlist.splitlines():
            m_w = _W_TOKEN_RE.search(line)
            if m_w and "w_explicit" not in variables:
                parsed = _parse_numeric_with_suffix(m_w.group(2))
                if parsed is not None:
                    variables["w_explicit"] = WLVariable(
                        name="w_explicit", kind="W", value=parsed,
                        min_value=W_MIN, max_value=W_MAX,
                    )
            m_l = _L_TOKEN_RE.search(line)
            if m_l and "l_explicit" not in variables:
                parsed = _parse_numeric_with_suffix(m_l.group(2))
                if parsed is not None:
                    variables["l_explicit"] = WLVariable(
                        name="l_explicit", kind="L", value=parsed,
                        min_value=L_MIN, max_value=L_MAX,
                    )

    return variables


def apply_wl_assignment(netlist: str, assignment: Dict[str, float]) -> str:
    """Return a new netlist string with updated W/L values.

    Only .param lines and explicit w=/l= tokens whose names appear in
    ``assignment`` are updated; other content is preserved verbatim.
    """
    lines: List[str] = []

    for line in netlist.splitlines():
        original = line

        # Update .param lines first
        m = _PARAM_RE.match(line)
        if m:
            name, val_str = m.group(1), m.group(2)
            if name in assignment:
                # Preserve any comments after the value
                parts = val_str.split(";", 1)
                comment = f";{parts[1]}" if len(parts) == 2 else ""
                new_val = assignment[name]
                line = f".param {name} = {new_val}{comment}"
        else:
            # Update explicit w=/l= tokens if we have synthetic names.
            # If the user provided multiple width variables, we do not
            # try to distinguish between devices here; instead we only
            # touch synthetic fallback names.
            if "w_explicit" in assignment:
                line = _W_TOKEN_RE.sub(rf"\g<1>{assignment['w_explicit']}", line)
            if "l_explicit" in assignment:
                line = _L_TOKEN_RE.sub(rf"\g<1>{assignment['l_explicit']}", line)

        lines.append(line if line is not None else original)

    return "\n".join(lines) + "\n"


def assignment_from_vector(variables: Dict[str, WLVariable], vector: List[float]) -> Dict[str, float]:
    """Clamp a numeric vector into variable bounds and map to a dict.

    The order of entries is the order of ``variables.values()``.
    """
    names = list(variables.keys())
    if len(vector) != len(names):
        raise ValueError("Vector length does not match number of variables")

    assignment: Dict[str, float] = {}
    for (name, var), val in zip(variables.items(), vector):
        v = float(val)
        v = max(var.min_value, min(var.max_value, v))
        assignment[name] = v
    return assignment


def vector_from_assignment(variables: Dict[str, WLVariable], assignment: Dict[str, float]) -> List[float]:
    """Create a vector (ordered list) from an assignment dict."""
    vec: List[float] = []
    for name, var in variables.items():
        vec.append(float(assignment.get(name, var.value)))
    return vec
