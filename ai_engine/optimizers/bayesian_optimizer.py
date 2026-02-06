"""
Bayesian Optimization for Analog Circuit Design
Uses Gaussian Process-like surrogate with uncertainty-aware candidate selection.
More sample-efficient than random search or grid search.
"""
import numpy as np
from typing import Dict, Callable, Tuple
from scipy.stats import norm
from datetime import datetime
import logging

from ai_engine.optimizers.base_optimizer import (
    BaseOptimizer, OptimizationResult, ParameterSpace, ObjectiveSpec
)
from ai_engine.surrogates.mlp import CircuitMLPSurrogate

logger = logging.getLogger(__name__)


class BayesianOptimizer(BaseOptimizer):
    """
    Bayesian Optimization for efficient analog circuit design space exploration.
    Uses neural surrogate with uncertainty quantification and Expected Improvement acquisition.
    
    This is a drop-in replacement for other optimizers, designed to reduce total evaluations
    while maintaining design quality.
    """
    
    def __init__(
        self,
        parameter_spaces: list,
        objectives: list,
        max_iterations: int = 50,
        initial_samples: int = 10,
        acquisition_type: str = "ei",  # "ei" (Expected Improvement) or "ucb"
        exploration_factor: float = 2.0,  # For UCB
        **kwargs
    ):
        """
        Args:
            parameter_spaces: List of ParameterSpace objects
            objectives: List of ObjectiveSpec objects
            max_iterations: Number of optimization iterations (after initial sampling)
            initial_samples: Number of initial random samples for warm-start
            acquisition_type: "ei" (Expected Improvement) or "ucb" (Upper Confidence Bound)
            exploration_factor: Beta for UCB (higher = more exploration)
        """
        super().__init__(parameter_spaces, objectives, max_iterations)
        self.initial_samples = initial_samples
        self.acquisition_type = acquisition_type
        self.exploration_factor = exploration_factor
        
        self.surrogate = None
        self.X_data = []
        self.y_data = []
        self.best_y = float('inf')
        self.best_x = None
    
    def optimize(
        self,
        objective_function: Callable[[Dict[str, float]], Dict[str, float]]
    ) -> OptimizationResult:
        """
        Run Bayesian optimization.
        
        Process:
        1. Warm-start with random samples
        2. Train surrogate on collected data
        3. Find next candidate using acquisition function
        4. Evaluate candidate
        5. Repeat until max_iterations
        """
        start_time = datetime.now()
        
        logger.info(f"🔵 Bayesian Optimization Starting")
        logger.info(f"   Initial samples: {self.initial_samples}")
        logger.info(f"   Max iterations: {self.max_iterations}")
        logger.info(f"   Acquisition: {self.acquisition_type}")
        
        # Phase 1: Warm-start with random samples
        logger.info(f"\n📊 Phase 1: Warm-start with {self.initial_samples} random samples")
        for i in range(self.initial_samples):
            params = self._sample_random()
            results = objective_function(params)
            score = self.evaluate_objectives(params, results)
            
            self._add_data(params, results, score)
            self.evaluation_count += 1
            
            if (i + 1) % max(1, self.initial_samples // 3) == 0:
                logger.info(f"   Sampled {i + 1}/{self.initial_samples} — Best score: {self.best_y:.4f}")
        
        # Phase 2: Bayesian optimization loop
        logger.info(f"\n🔄 Phase 2: Bayesian optimization")
        
        for iteration in range(self.max_iterations):
            # Train surrogate on all data collected so far
            self._train_surrogate()
            
            # Find next candidate using acquisition function
            candidate_x, acq_value = self._find_next_candidate()
            
            # Evaluate candidate
            candidate_params = self._x_to_params(candidate_x)
            results = objective_function(candidate_params)
            score = self.evaluate_objectives(candidate_params, results)
            
            self._add_data(candidate_params, results, score)
            self.evaluation_count += 1
            
            improvement = self.best_y - score if score < float('inf') else 0
            
            logger.info(
                f"  Iter {iteration + 1:3d}: Score {score:8.4f} | "
                f"Improvement {improvement:8.4f} | Acq {acq_value:8.4f}"
            )
            
            self.convergence_history.append(score)
        
        # Finalize
        execution_time = (datetime.now() - start_time).total_seconds()
        
        return OptimizationResult(
            success=self.best_x is not None,
            best_parameters=self._x_to_params(self.best_x) if self.best_x is not None else {},
            best_score=self.best_y,
            iteration_count=self.initial_samples + self.max_iterations,
            evaluation_count=self.evaluation_count,
            execution_time=execution_time,
            convergence_history=self.convergence_history,
            parameter_history=self.parameter_history,
            message=f"Bayesian Optimization: {self.evaluation_count} evaluations in {execution_time:.1f}s"
        )
    
    def _sample_random(self) -> Dict[str, float]:
        """Random sample from parameter space"""
        return {
            name: space.random_sample(1)[0]
            for name, space in self.parameter_spaces.items()
        }
    
    def _add_data(self, params: Dict[str, float], results: Dict[str, float], score: float):
        """Add evaluation to dataset"""
        x = self._params_to_x(params)
        y = [results.get(obj.name, 1e6) for obj in self.objectives]
        
        self.X_data.append(x)
        self.y_data.append(y)
        self.parameter_history.append(params.copy())
        
        # Track best
        if score < self.best_y:
            self.best_y = score
            self.best_x = x.copy()
    
    def _params_to_x(self, params: Dict[str, float]) -> np.ndarray:
        """Convert parameter dict to feature vector"""
        return np.array([params[name] for name in self.parameter_spaces.keys()])
    
    def _x_to_params(self, x: np.ndarray) -> Dict[str, float]:
        """Convert feature vector to parameter dict"""
        return {name: x[i] for i, name in enumerate(self.parameter_spaces.keys())}
    
    def _train_surrogate(self):
        """Train or re-train surrogate"""
        input_dim = len(self.parameter_spaces)
        output_dim = len(self.objectives)
        
        if self.surrogate is None:
            # Create new surrogate with larger hidden dims for better expressiveness
            self.surrogate = CircuitMLPSurrogate(
                input_dim,
                output_dim,
                hidden_dims=[128, 64],
                use_ensemble=True
            )
        
        # Train on collected data
        X = np.array(self.X_data)
        y = np.array(self.y_data)
        
        # Normalize inputs
        X_mean = X.mean(axis=0)
        X_std = X.std(axis=0) + 1e-6
        X_norm = (X - X_mean) / X_std
        
        self.surrogate.train_model(X_norm, y, epochs=50, lr=0.01)
    
    def _find_next_candidate(self) -> Tuple[np.ndarray, float]:
        """
        Find the next candidate to evaluate using acquisition function.
        
        Uses Expected Improvement (EI) or Upper Confidence Bound (UCB).
        """
        best_acq_value = -np.inf
        best_candidate = None
        
        # Search over dense grid in parameter space
        n_candidates = 200
        candidates = self._generate_candidate_pool(n_candidates)
        
        for candidate_x in candidates:
            candidate_x_tensor = np.array([candidate_x])
            
            # Get prediction with uncertainty
            mean, std = self.surrogate.predict(candidate_x_tensor, return_uncertainty=True)
            mean = mean[0]
            std = std[0]
            
            # Compute acquisition value
            if self.acquisition_type == "ei":
                acq_value = self._expected_improvement(mean, std)
            else:  # ucb
                acq_value = self._upper_confidence_bound(mean, std)
            
            if acq_value > best_acq_value:
                best_acq_value = acq_value
                best_candidate = candidate_x.copy()
        
        return best_candidate, best_acq_value
    
    def _generate_candidate_pool(self, n_candidates: int) -> list:
        """Generate pool of candidate points"""
        candidates = []
        
        for _ in range(n_candidates):
            x = np.array([
                space.random_sample(1)[0]
                for space in self.parameter_spaces.values()
            ])
            candidates.append(x)
        
        return candidates
    
    def _expected_improvement(self, mean: np.ndarray, std: np.ndarray, epsilon: float = 0.0) -> float:
        """
        Expected Improvement acquisition function.
        
        EI(x) = E[max(f_best - f(x), 0)]
        """
        # Average across objectives
        mean_val = np.mean(mean)
        std_val = np.mean(std) if std.sum() > 0 else 1e-6
        
        # Improvement over best known
        improvement = self.best_y - mean_val - epsilon
        
        # Avoid division by zero
        if std_val < 1e-8:
            return 0.0
        
        # Standard normal CDF and PDF
        z = improvement / std_val
        ei = improvement * norm.cdf(z) + std_val * norm.pdf(z)
        
        return float(np.clip(ei, 0, 1e6))
    
    def _upper_confidence_bound(self, mean: np.ndarray, std: np.ndarray) -> float:
        """
        Upper Confidence Bound acquisition function.
        
        UCB(x) = mean(f) - beta * std(f)
        Lower is better, so we want to explore where mean is low but uncertainty is high.
        """
        mean_val = np.mean(mean)
        std_val = np.mean(std) if std.sum() > 0 else 0.0
        
        ucb = self.best_y - mean_val + self.exploration_factor * std_val
        
        return float(ucb)
