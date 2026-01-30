"""
AI Design Agent - Current Mirror Optimization Demo
This script demonstrates how to use the AI Engine to optimize a Sky130 Current Mirror.
"""
import os
import sys
import numpy as np
from typing import Dict

# Add project root to path
sys.path.append('/home/user/Desktop/Adnan/Analog_Tool-Automation')

from circuits.library.current_mirror.sky130_current_mirror import Sky130CurrentMirror
from ai_engine.optimizers.base_optimizer import create_optimizer, OptimizationMethod, ParameterSpace, ObjectiveSpec
# Note: ngspice_wrapper might need the environment to be set up, 
# but we can at least define the objective function.

def objective_function(params: Dict[str, float]) -> Dict[str, float]:
    """
    Simulates the circuit with given parameters and returns performance metrics.
    For this demo (while Docker is building), we'll use a surrogate model or a mock.
    In a real run, this would call NgspiceSimulator.
    """
    w = params.get('width', 1.0)
    l = params.get('length', 0.5)
    
    # Mocking behavior:
    # Error decreases if L is larger (better matching)
    # Output resistance increases with L
    mirror_error = 2.0 / (l + 0.1) + np.random.normal(0, 0.1)
    rout = 100e3 * l / (w + 0.1)
    
    return {
        "mirror_error": mirror_error,
        "rout": rout
    }

def run_optimization_demo():
    print("🚀 Starting AI-Driven Circuit Optimization...")
    
    # 1. Define Search Space
    params = [
        ParameterSpace(name="width", min_value=0.5, max_value=10.0, step=0.1, discrete=True),
        ParameterSpace(name="length", min_value=0.15, max_value=2.0, step=0.05, discrete=True)
    ]
    
    # 2. Define Objectives
    objectives = [
        ObjectiveSpec(name="mirror_error", target=0.0, weight=1.0, minimize=True),
        ObjectiveSpec(name="rout", target=1e6, weight=0.5, minimize=False)
    ]
    
    # 3. Create Optimizer (Using Particle Swarm for efficiency)
    optimizer = create_optimizer(
        method=OptimizationMethod.PARTICLE_SWARM,
        parameter_spaces=params,
        objectives=objectives,
        max_iterations=20
    )
    
    # 4. Run Optimization
    result = optimizer.optimize(objective_function)
    
    if result.success:
        print("\n✅ Optimization Successful!")
        print(f"Best Parameters: {result.best_parameters}")
        print(f"Best Score (Error): {result.best_score:.4f}")
        print(f"Total Evaluations: {result.evaluation_count}")
    else:
        print("\n❌ Optimization Failed.")

if __name__ == "__main__":
    run_optimization_demo()
