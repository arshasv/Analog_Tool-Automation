"""
Test Suite for AI Engine Improvements
Validates that new features work without breaking existing functionality.
"""
import numpy as np
from pathlib import Path
import sys

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from ai_engine.optimizers.base_optimizer import ParameterSpace, ObjectiveSpec, OptimizationMethod, create_optimizer
from ai_engine.surrogates.mlp import CircuitMLPSurrogate
from ai_engine.reasoners.analog_reasoner import AnalogReasoner, CircuitSpecs
from ai_engine.cache.design_cache import DesignCache
from ai_engine.optimizers.bayesian_optimizer import BayesianOptimizer


def test_mlp_ensemble():
    """Test MLP with ensemble and uncertainty"""
    print("\n✅ TEST 1: MLP Ensemble + Uncertainty")
    
    # Create surrogate
    surrogate = CircuitMLPSurrogate(
        input_dim=2,
        output_dim=2,
        use_ensemble=True
    )
    
    # Generate dummy training data
    X = np.random.randn(20, 2)
    y = np.random.randn(20, 2)
    
    # Train
    surrogate.train_model(X, y, epochs=10)
    
    # Predict with uncertainty
    X_test = np.array([[0.5, 0.5]])
    
    # Old interface (backward compat)
    pred_old = surrogate.predict(X_test)
    print(f"  Backward compat (no uncertainty): {pred_old.shape} — ✓")
    
    # New interface with uncertainty
    pred_mean, pred_std = surrogate.predict(X_test, return_uncertainty=True)
    print(f"  With uncertainty: mean {pred_mean.shape}, std {pred_std.shape} — ✓")
    print(f"  Mean: {pred_mean}, Std: {pred_std}")
    
    assert pred_mean.shape == (1, 2), "Mean shape mismatch"
    assert pred_std.shape == (1, 2), "Std shape mismatch"
    assert np.all(pred_std >= 0), "Std should be non-negative"
    print("  ✅ MLP ensemble test PASSED\n")


def test_analog_reasoner():
    """Test AnalogReasoner heuristics"""
    print("✅ TEST 2: Analog Reasoner")
    
    # Test gain estimation
    gain = AnalogReasoner.estimate_gain_from_gm_id(W=5.0, L=0.5, gm_id=10)
    print(f"  Estimated gain (W=5, L=0.5): {gain:.2f} V/V — ✓")
    assert gain > 0, "Gain must be positive"
    
    # Test bandwidth estimation
    bw = AnalogReasoner.estimate_bandwidth(L=0.5, C_load=1e-12)
    print(f"  Estimated bandwidth (L=0.5): {bw:.2e} Hz — ✓")
    assert bw > 0, "Bandwidth must be positive"
    
    # Test initial parameters for current mirror
    specs = CircuitSpecs(target_current=10e-6)
    init_params = AnalogReasoner.suggest_initial_parameters("current_mirror", specs)
    print(f"  Initial params for current_mirror: {init_params} — ✓")
    
    # Test constraint validation
    is_valid, issues = AnalogReasoner.validate_design_constraints(init_params)
    print(f"  Design valid: {is_valid}, Issues: {len(issues)} — ✓")
    
    # Test optimization hints
    hints = AnalogReasoner.suggest_optimization_hints("opamp", init_params)
    print(f"  Got {len(hints)} optimization hints — ✓")
    
    print("  ✅ Analog reasoner test PASSED\n")


def test_bayesian_optimizer():
    """Test Bayesian Optimizer"""
    print("✅ TEST 3: Bayesian Optimizer")
    
    # Define search space
    param_spaces = [
        ParameterSpace("W", min_value=1.0, max_value=20.0),
        ParameterSpace("L", min_value=0.15, max_value=2.0)
    ]
    
    objectives = [
        ObjectiveSpec("gain", target=45, weight=1.0, minimize=False),
        ObjectiveSpec("bw", target=1e6, weight=1.0, minimize=False)
    ]
    
    # Simple objective function
    def dummy_objective(params):
        W = params["W"]
        L = params["L"]
        gain = 30 + 5 * (W / L) ** 0.5
        bw = 1e6 * (L / W) ** 0.3
        return {"gain": gain, "bw": bw}
    
    # Create optimizer
    optimizer = BayesianOptimizer(
        param_spaces,
        objectives,
        max_iterations=5,  # Short test
        initial_samples=3
    )
    
    # Run optimization
    result = optimizer.optimize(dummy_objective)
    
    print(f"  Best score: {result.best_score:.4f}")
    print(f"  Total evals: {result.evaluation_count}")
    print(f"  Best params: {result.best_parameters}")
    print(f"  Execution time: {result.execution_time:.2f}s")
    
    assert result.success, "Optimizer should succeed"
    assert result.evaluation_count == 3 + 5, "Should have initial + iterations"
    print("  ✅ Bayesian optimizer test PASSED\n")


def test_design_cache():
    """Test Design Cache"""
    print("✅ TEST 4: Design Cache")
    
    cache = DesignCache(cache_dir="data/cache/designs_test")
    
    # Test put/get
    params = {"W": 5.0, "L": 0.5}
    result = {"gain": 45.2, "bw": 1e6}
    
    cache.put("current_mirror", params, result)
    
    retrieved = cache.get("current_mirror", params)
    assert retrieved == result, "Cache retrieval mismatch"
    print(f"  Cache store/retrieve: ✓")
    
    # Check stats
    stats = cache.stats()
    print(f"  Cache stats: {stats}")
    assert stats["hits"] > 0, "Should have cache hit"
    
    # Cleanup
    cache.clear()
    print("  ✅ Cache test PASSED\n")


def test_constraint_support():
    """Test ObjectiveSpec constraint support"""
    print("✅ TEST 5: Constraint Support")
    
    # Create specs with constraints
    gain_spec = ObjectiveSpec(
        "gain",
        target=40,
        constraint_type=">=",
        is_hard_constraint=True
    )
    
    bw_spec = ObjectiveSpec(
        "bw",
        target=1e6,
        constraint_type=">=",
        is_hard_constraint=True
    )
    
    # Test constraint checking
    assert gain_spec.check_constraint(45) == True, "45dB should satisfy >= 40"
    assert gain_spec.check_constraint(35) == False, "35dB should violate >= 40"
    
    assert bw_spec.check_constraint(2e6) == True, "2MHz should satisfy >= 1MHz"
    assert bw_spec.check_constraint(0.5e6) == False, "0.5MHz should violate >= 1MHz"
    
    print(f"  Constraint checking: ✓")
    print("  ✅ Constraint test PASSED\n")


def test_factory_creates_bayesian():
    """Test that factory creates Bayesian optimizer"""
    print("✅ TEST 6: Factory Creates Bayesian Optimizer")
    
    param_spaces = [ParameterSpace("W", 1, 20)]
    objectives = [ObjectiveSpec("gain", 45)]
    
    optimizer = create_optimizer(
        OptimizationMethod.BAYESIAN_NN,
        param_spaces,
        objectives
    )
    
    assert isinstance(optimizer, BayesianOptimizer), "Should create BayesianOptimizer"
    print("  Factory creates BAYESIAN_NN: ✓")
    print("  ✅ Factory test PASSED\n")


def test_existing_optimizers_still_work():
    """Verify existing optimizers still work (no regression)"""
    print("✅ TEST 7: Backward Compatibility (Existing Optimizers)")
    
    param_spaces = [ParameterSpace("W", 1, 20)]
    objectives = [ObjectiveSpec("gain", 45)]
    
    def dummy_obj(params):
        return {"gain": 40 + params["W"]}
    
    # Test each existing method
    methods = [
        OptimizationMethod.RANDOM_SEARCH,
        OptimizationMethod.PARTICLE_SWARM,
    ]
    
    for method in methods:
        optimizer = create_optimizer(method, param_spaces, objectives, max_iterations=3)
        result = optimizer.optimize(dummy_obj)
        assert result.success, f"{method} should succeed"
        print(f"  {method.value}: ✓")
    
    print("  ✅ Backward compatibility test PASSED\n")


def run_all_tests():
    """Run all tests"""
    print("\n" + "="*60)
    print("🧪 AI ENGINE IMPROVEMENTS TEST SUITE")
    print("="*60)
    
    try:
        test_mlp_ensemble()
        test_analog_reasoner()
        test_bayesian_optimizer()
        test_design_cache()
        test_constraint_support()
        test_factory_creates_bayesian()
        test_existing_optimizers_still_work()
        
        print("="*60)
        print("✅ ALL TESTS PASSED!")
        print("="*60)
        print("\nSummary:")
        print("  ✓ MLP with ensemble + uncertainty quantification")
        print("  ✓ Analog design heuristics and reasoner")
        print("  ✓ Bayesian optimization with EI acquisition")
        print("  ✓ Design caching for memoization")
        print("  ✓ Constraint support in objectives")
        print("  ✓ Factory pattern extended")
        print("  ✓ Backward compatibility maintained")
        print("\n🚀 Ready for production use!\n")
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
