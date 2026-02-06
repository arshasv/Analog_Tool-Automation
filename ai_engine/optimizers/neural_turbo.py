import numpy as np
import torch
from typing import List, Dict, Callable
from ai_engine.optimizers.base_optimizer import BaseOptimizer, OptimizationResult, ParameterSpace, ObjectiveSpec
from ai_engine.surrogates.mlp import CircuitMLPSurrogate

class NeuralTurboOptimizer(BaseOptimizer):
    """
    State-of-the-Art Optimizer using Neural Surrogates and Trust Region (TuRBO) principles.
    Efficiently handles high-dimensional analog design spaces.
    """
    def __init__(self, parameter_spaces, objectives, max_iterations=50, batch_size=5, **kwargs):
        super().__init__(parameter_spaces, objectives, max_iterations)
        self.batch_size = batch_size
        self.surrogate = None
        self.X_data = []
        self.y_data = []

    def optimize(self, objective_func: Callable[[Dict[str, float]], Dict[str, float]]) -> OptimizationResult:
        print(f"🚀 Initializing Neural-TuRBO Design Agent...")
        
        # 1. Initialization: Latin Hypercube or Random Sampling
        init_samples = self.batch_size * 2
        print(f"📊 Phase 1: Warming up Surrogate ({init_samples} simulations)...")
        for _ in range(init_samples):
            params = self._sample_random()
            results = objective_func(params)
            self._add_data(params, results)

        # 2. TuRBO Parameters
        tr_length = 0.8  # Initial Trust Region size
        tr_min = 0.1
        tr_max = 1.6
        success_counter = 0
        failure_counter = 0
        success_threshold = 3
        failure_threshold = 5

        # 3. Main Optimization Loop
        for i in range(self.max_iterations):
            print(f"\n🔄 Iteration {i+1}/{self.max_iterations} [TR Size: {tr_length:.2f}]")
            
            # 3.1 Synchronize and Train Surrogate
            self._update_surrogate()
            
            # 3.2 Candidate Generation
            best_idx = np.argmin([sum(y) for y in self.y_data])
            center = np.array(self.X_data[best_idx])
            
            best_virtual_score = float('inf')
            best_candidate_x = None
            
            # 500 virtual sims on the surrogate
            for _ in range(500):
                candidate_x = self._sample_in_trust_region(center, tr_length)
                y_pred = self.surrogate.predict(np.array([candidate_x]))[0]
                score = sum(self.objectives[j].calculate_error(y_pred[j]) for j in range(len(self.objectives)))
                
                if score < best_virtual_score:
                    best_virtual_score = score
                    best_candidate_x = candidate_x

            # 3.3 Real SPICE Evaluation
            candidate_params = {name: best_candidate_x[j] for j, name in enumerate(self.parameter_spaces.keys())}
            results = objective_func(candidate_params)
            actual_score = sum(self.objectives[j].calculate_error(results.get(self.objectives[j].name, 1e6)) for j in range(len(self.objectives)))
            
            # 3.4 Trust Region Management
            min_score = min([sum(y) for y in self.y_data])
            if actual_score < min_score:
                success_counter += 1
                failure_counter = 0
            else:
                success_counter = 0
                failure_counter += 1
            
            if success_counter >= success_threshold:
                tr_length = min(tr_max, tr_length * 2.0)
                success_counter = 0
            elif failure_counter >= failure_threshold:
                tr_length = max(tr_min, tr_length / 2.0)
                failure_counter = 0

            self._add_data(candidate_params, results)
            
        return self._get_final_result()

    def _add_data(self, params, results):
        x = [params[name] for name in self.parameter_spaces.keys()]
        y = [results.get(o.name, 1e6) for o in self.objectives]
        self.X_data.append(x)
        self.y_data.append(y)

    def _update_surrogate(self):
        input_dim = len(self.parameter_spaces)
        output_dim = len(self.objectives)
        
        if self.surrogate is None:
            self.surrogate = CircuitMLPSurrogate(input_dim, output_dim)
            
        X = np.array(self.X_data)
        y = np.array(self.y_data)
        self.surrogate.train_model(X, y, epochs=100)

    def _sample_in_trust_region(self, center, length):
        x = []
        for i, p in enumerate(self.parameter_spaces.values()):
            domain_range = p.max_value - p.min_value
            lb = max(p.min_value, center[i] - (length * domain_range) / 2)
            ub = min(p.max_value, center[i] + (length * domain_range) / 2)
            x.append(np.random.uniform(lb, ub))
        return np.array(x)

    def _sample_random(self):
        return {p.name: np.random.uniform(p.min_value, p.max_value) for p in self.parameter_spaces.values()}

    def _get_final_result(self) -> OptimizationResult:
        X = np.array(self.X_data)
        y = np.array(self.y_data)
        
        scores = []
        for yi in y:
            s = sum(self.objectives[j].calculate_error(yi[j]) for j in range(len(self.objectives)))
            scores.append(s)
            
        best_idx = np.argmin(scores)
        best_params = {name: X[best_idx][j] for j, name in enumerate(self.parameter_spaces.keys())}
        
        return OptimizationResult(
            success=True,
            best_parameters=best_params,
            best_score=scores[best_idx],
            iteration_count=len(self.X_data),
            evaluation_count=len(self.X_data),
            execution_time=0.0,
            convergence_history=scores,
            parameter_history=[]
        )
