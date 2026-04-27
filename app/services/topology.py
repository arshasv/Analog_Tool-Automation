"""
Topology Role System for Analog Architecture Search

Defines:
  - Role enums (INPUT, GAIN, LOAD, BIAS, COMP, OUTPUT)
  - Valid option sets per role
  - Constraint rules between roles
  - Topology enumeration with constraint filtering
"""
from enum import Enum
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field
import itertools
import logging
import importlib
import inspect
from pydantic import BaseModel

logger = logging.getLogger(__name__)


# ── Role option sets ──────────────────────────────────────────────────

INPUT_OPTIONS = ["diff_n", "diff_p", "rail2rail"]
GAIN_OPTIONS = ["common_source", "telescopic", "folded", "two_stage"]
LOAD_OPTIONS = ["resistive", "mirror", "cascode", "wilson"]
BIAS_OPTIONS = ["simple", "wide_swing"]
COMP_OPTIONS = ["none", "miller", "feedforward"]
OUTPUT_OPTIONS = ["direct", "source_follower", "classAB"]


@dataclass
class Topology:
    """A complete topology specification"""
    input: str
    gain: str
    load: str
    bias: str
    comp: str
    output: str

    def as_dict(self) -> Dict[str, str]:
        return {
            "input": self.input,
            "gain": self.gain,
            "load": self.load,
            "bias": self.bias,
            "comp": self.comp,
            "output": self.output,
        }

    @property
    def key(self) -> str:
        return f"{self.input}_{self.gain}_{self.load}_{self.bias}_{self.comp}_{self.output}"

    def __hash__(self):
        return hash(self.key)

    def __eq__(self, other):
        return isinstance(other, Topology) and self.key == other.key

    def __repr__(self):
        return (
            f"Topology(input={self.input}, gain={self.gain}, "
            f"load={self.load}, bias={self.bias}, "
            f"comp={self.comp}, output={self.output})"
        )


# ── Constraint rules ─────────────────────────────────────────────────

def _check_constraints(t: Topology) -> Tuple[bool, str]:
    """Return (valid, reason). Enforces analog design rules."""

    # Rule 1: telescopic cannot use rail2rail input (headroom)
    if t.gain == "telescopic" and t.input == "rail2rail":
        return False, "telescopic requires stacked devices; incompatible with rail2rail input"

    # Rule 2: two_stage requires miller or feedforward compensation
    if t.gain == "two_stage" and t.comp == "none":
        return False, "two_stage amplifier requires compensation (miller or feedforward)"

    # Rule 3: classAB output needs at minimum a two_stage or folded gain
    if t.output == "classAB" and t.gain in ("common_source", "telescopic"):
        return False, "classAB output requires two_stage or folded gain for biasing"

    # Rule 4: folded cascode prefers cascode or mirror load, not resistive
    if t.gain == "folded" and t.load == "resistive":
        return False, "folded cascode needs active load (mirror/cascode), not resistive"

    # Rule 5: telescopic prefers wide_swing bias for maximizing swing
    if t.gain == "telescopic" and t.bias == "simple":
        return False, "telescopic cascode benefits from wide_swing bias for output swing"

    # Rule 6: common_source single stage doesn't need miller compensation
    if t.gain == "common_source" and t.comp == "miller":
        return False, "common_source single-stage doesn't need miller compensation"

    # Rule 7: wilson load is overkill for common_source
    if t.gain == "common_source" and t.load == "wilson":
        return False, "wilson mirror is unnecessarily complex for a CS stage"

    # Rule 8: feedforward comp only makes sense with two_stage
    if t.comp == "feedforward" and t.gain != "two_stage":
        return False, "feedforward compensation only applies to two_stage"

    return True, "ok"


def enumerate_valid_topologies() -> List[Topology]:
    """Generate all valid topology combinations respecting constraints."""
    valid = []
    for inp, gain, load, bias, comp, out in itertools.product(
        INPUT_OPTIONS, GAIN_OPTIONS, LOAD_OPTIONS,
        BIAS_OPTIONS, COMP_OPTIONS, OUTPUT_OPTIONS
    ):
        t = Topology(inp, gain, load, bias, comp, out)
        ok, reason = _check_constraints(t)
        if ok:
            valid.append(t)
    logger.info(f"Enumerated {len(valid)} valid topologies")
    return valid


def get_topology_complexity(t: Topology) -> int:
    """Return a rough complexity score (lower = simpler)."""
    score = 0
    score += {"common_source": 1, "telescopic": 3, "folded": 4, "two_stage": 5}[t.gain]
    score += {"resistive": 1, "mirror": 2, "cascode": 3, "wilson": 4}[t.load]
    score += {"diff_n": 1, "diff_p": 1, "rail2rail": 3}[t.input]
    score += {"simple": 1, "wide_swing": 2}[t.bias]
    score += {"none": 0, "miller": 2, "feedforward": 3}[t.comp]
    score += {"direct": 0, "source_follower": 2, "classAB": 4}[t.output]
    return score


def get_circuit_parameters(circuit_name: str) -> Dict[str, Any]:
    """
    Dynamically imports a circuit class, inspects its model, and returns
    a JSON-serializable dictionary of its parameters and their defaults.
    """
    module_name = f"app.circuits.{circuit_name}"
    module = importlib.import_module(module_name)
    
    for name, obj in inspect.getmembers(module):
        if inspect.isclass(obj) and hasattr(obj, 'Design') and issubclass(obj.Design, BaseModel):
            design_model = obj.Design
            
            # Extract parameters and their defaults from the Pydantic model
            schema = design_model.model_json_schema()
            parameters = {}
            if 'properties' in schema:
                for param_name, details in schema['properties'].items():
                    parameters[param_name] = details.get('default', 'No default value')
            
            return {
                "circuit": obj.__name__,
                "parameters": parameters
            }
            
    raise AttributeError(f"No suitable class with a 'Design' Pydantic model found in {module_name}")
