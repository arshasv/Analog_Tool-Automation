"""W/L optimization core module.

Provides cost evaluation and gradient-free optimization utilities for
MOS width/length tuning while reusing the existing ngspice pipeline.
"""

from .optimizer import WLOptimizer  # noqa: F401
