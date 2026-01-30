import sys
import os
import importlib.util
from pathlib import Path
from ai_engine.optimizers.base_optimizer import create_optimizer, OptimizationMethod

# Add project root to path
sys.path.append("/home/eda")

def get_latest_circuit_class():
    """Finds the newest circuit design in the custom folder"""
    custom_dir = Path("/home/eda/circuits/library/custom")
    py_files = [f for f in custom_dir.glob("*.py") if f.name not in ["optimizer.py", "runner.py", "base_circuit.py", "__init__.py"]]
    
    if not py_files:
        return None
        
    latest_file = max(py_files, key=os.path.getmtime)
    
    # Load module dynamically
    spec = importlib.util.spec_from_file_location("dynamic_circuit", latest_file)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    
    # Find a class that inherits from OptimizableCircuit (or just has the right methods)
    for name, obj in module.__dict__.items():
        if isinstance(obj, type) and name != "OptimizableCircuit":
            # Check for required methods
            if hasattr(obj, "get_parameter_space") and hasattr(obj, "simulate"):
                return obj(), latest_file.name
                
    return None, None

def run_agentic_optimization():
    print("🧠 Initializing AI Design Agent...")
    circuit, filename = get_latest_circuit_class()
    
    if not circuit:
        print("❌ Could not find a valid circuit class in the custom folder.")
        return

    print(f"🎯 Target Design: {filename}")
    print(f"🔄 Starting Closed-Loop Optimization...")
    print("━" * 60)

    # 1. Get Specs from the Circuit
    params = circuit.get_parameter_space()
    objectives = circuit.get_objectives()
    
    # 2. Create the Optimizer (using Particle Swarm for efficiency)
    optimizer = create_optimizer(
        method=OptimizationMethod.PARTICLE_SWARM,
        parameter_spaces=params,
        objectives=objectives,
        max_iterations=10,
        n_particles=5 # Reduced for safer/faster demo
    )

    best_so_far = {"score": float('inf'), "params": None}

    # 3. Define the "Closed Loop" function
    def agent_step(current_params):
        results = circuit.simulate(current_params)
        # Calculate error (score) for this attempt
        score = 0
        for obj in objectives:
            if obj.name in results:
                score += obj.calculate_error(results[obj.name])
        
        if score < best_so_far["score"]:
            best_so_far["score"] = score
            best_so_far["params"] = current_params
            print(f"\n✨ New Best Found! Score: {score:.5f}", flush=True)
            print(f"   ➜ {current_params}", flush=True)
        else:
            print(".", end="", flush=True)
            
        return results

    # 4. Run the Engine
    print("Optimization in progress (each '.' is a simulation):")
    result = optimizer.optimize(agent_step)

    # 5. Final Report
    print("\n" + "━" * 60)
    print("✅ OPTIMIZATION COMPLETE")
    print(f"Best Score: {result.best_score:.4f} (Lower is better)")
    print(f"Best Parameters found:")
    for name, val in result.best_parameters.items():
        print(f"  ➜ {name}: {val:.4f}")
    
    print("\n🚀 Verifying Final Design...")
    final_metrics = circuit.simulate(result.best_parameters)
    print(f"Final Performance: {final_metrics}")
    print("━" * 60)

if __name__ == "__main__":
    run_agentic_optimization()
