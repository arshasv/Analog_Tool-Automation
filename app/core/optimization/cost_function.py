"""Cost function for W/L optimization.

Implements a flexible scalar cost used by the optimizer:

    cost = w1 * error_current + w2 * error_gain + w3 * power_penalty

All quantities are computed from simulation metrics and user targets.
"""

from typing import Dict, Any


def compute_cost(
    metrics: Dict[str, float],
    targets: Dict[str, float],
    weights: Dict[str, float],
    power_max: float | None = None,
) -> float:
    """Compute scalar cost from metrics and user-specified targets.

    Args:
        metrics: Dict with keys like "current", "gain", "power".
        targets: Dict with desired targets, keys "current", "gain".
        weights: Dict with weights "w1", "w2", "w3".
        power_max: Optional maximum power budget.

    Returns:
        Scalar cost (lower is better).
    """
    current_actual = float(metrics.get("current", 0.0))
    gain_actual = float(metrics.get("gain", 0.0))
    power_actual = float(metrics.get("power", 0.0))

    current_target = float(targets.get("current", 0.0))
    gain_target = float(targets.get("gain", 0.0))

    w1 = float(weights.get("w1", 1.0))
    w2 = float(weights.get("w2", 1.0))
    w3 = float(weights.get("w3", 1.0))

    error_current = abs(current_actual - current_target)
    error_gain = abs(gain_actual - gain_target)

    power_penalty = 0.0
    if power_max is not None:
        power_penalty = max(0.0, power_actual - float(power_max))

    cost = w1 * error_current + w2 * error_gain + w3 * power_penalty
    return float(cost)
