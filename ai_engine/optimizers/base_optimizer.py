"""
AI-Driven Circuit Parameter Optimizer
Uses various optimization algorithms to size analog circuits
"""
from typing import Dict, List, Callable, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import numpy as np
from abc import ABC, abstractmethod
import time


class OptimizationMethod(str, Enum):
    """Supported optimization methods"""
    GRID_SEARCH = "grid_search"
    RANDOM_SEARCH = "random_search"
    GRADIENT_FREE = "gradient_free"
    GENETIC_ALGORITHM = "genetic_algorithm"
    BAYESIAN = "bayesian"
    PARTICLE_SWARM = "particle_swarm"
    NEURAL_TURBO = "neural_turbo"
    BAYESIAN_NN = "bayesian_nn"  # New: Bayesian with neural surrogate


@dataclass
class ParameterSpace:
    """Parameter search space definition"""
    name: str
    min_value: float
    max_value: float
    step: Optional[float] = None
    log_scale: bool = False
    discrete: bool = False
    
    def sample(self, n: int = 1) -> np.ndarray:
        """Sample n values from parameter space"""
        if self.log_scale:
            samples = np.logspace(
                np.log10(self.min_value),
                np.log10(self.max_value),
                n
            )
        else:
            samples = np.linspace(self.min_value, self.max_value, n)
        
        if self.discrete and self.step:
            samples = np.round(samples / self.step) * self.step
        
        return samples
    
    def random_sample(self, n: int = 1) -> np.ndarray:
        """Random sample from parameter space"""
        if self.log_scale:
            log_min = np.log10(self.min_value)
            log_max = np.log10(self.max_value)
            samples = 10 ** np.random.uniform(log_min, log_max, n)
        else:
            samples = np.random.uniform(self.min_value, self.max_value, n)
        
        if self.discrete and self.step:
            samples = np.round(samples / self.step) * self.step
        
        return samples


@dataclass
class ObjectiveSpec:
    """Optimization objective specification"""
    name: str
    target: float
    weight: float = 1.0
    minimize: bool = True
    tolerance: float = 0.1  # 10% tolerance
    
    # NEW: Constraint support
    constraint_type: Optional[str] = None  # None, ">=", "<=", "=="
    is_hard_constraint: bool = False  # If True, violation = infeasible design
    
    def calculate_error(self, actual: float) -> float:
        """Calculate weighted error"""
        if self.target == 0:
            error = actual
        elif self.minimize:
            error = (actual - self.target) / self.target
        else:
            error = (self.target - actual) / self.target
        
        return abs(error) * self.weight
    
    def check_constraint(self, actual: float) -> bool:
        """Check if constraint is satisfied"""
        if self.constraint_type is None:
            return True  # Not a constraint
        
        # Check with tolerance
        threshold = self.target * (1.0 + self.tolerance)
        
        if self.constraint_type == ">=":
            return actual >= self.target * (1 - self.tolerance)
        elif self.constraint_type == "<=":
            return actual <= threshold
        elif self.constraint_type == "==":
            return abs(actual - self.target) <= abs(self.target) * self.tolerance
        else:
            return True


@dataclass
class OptimizationResult:
    """Optimization result container"""
    success: bool
    best_parameters: Dict[str, float]
    best_score: float
    iteration_count: int
    evaluation_count: int
    execution_time: float
    convergence_history: List[float]
    parameter_history: List[Dict[str, float]]
    message: str = ""


class BaseOptimizer(ABC):
    """Base class for all optimizers"""
    
    def __init__(
        self,
        parameter_spaces: List[ParameterSpace],
        objectives: List[ObjectiveSpec],
        max_iterations: int = 100
    ):
        self.parameter_spaces = {ps.name: ps for ps in parameter_spaces}
        self.objectives = objectives
        self.max_iterations = max_iterations
        
        self.evaluation_count = 0
        self.convergence_history = []
        self.parameter_history = []
    
    @abstractmethod
    def optimize(
        self,
        objective_function: Callable[[Dict[str, float]], Dict[str, float]]
    ) -> OptimizationResult:
        """Run optimization"""
        pass
    
    def evaluate_objectives(
        self,
        parameters: Dict[str, float],
        results: Dict[str, float]
    ) -> float:
        """Evaluate multi-objective function"""
        total_error = 0.0
        
        for obj in self.objectives:
            if obj.name in results:
                error = obj.calculate_error(results[obj.name])
                total_error += error
            else:
                # Penalty for missing objectives
                total_error += 1e6
        
        return total_error


class GridSearchOptimizer(BaseOptimizer):
    """Grid search over parameter space"""
    
    def __init__(self, *args, grid_points: int = 5, **kwargs):
        super().__init__(*args, **kwargs)
        self.grid_points = grid_points
    
    def optimize(
        self,
        objective_function: Callable[[Dict[str, float]], Dict[str, float]]
    ) -> OptimizationResult:
        """Run grid search optimization"""
        start_time = time.time()
        
        # Generate grid
        param_names = list(self.parameter_spaces.keys())
        param_grids = [
            self.parameter_spaces[name].sample(self.grid_points)
            for name in param_names
        ]
        
        # Create meshgrid
        grids = np.meshgrid(*param_grids, indexing='ij')
        
        best_score = float('inf')
        best_params = None
        
        # Evaluate all grid points
        total_points = self.grid_points ** len(param_names)
        
        for i in range(total_points):
            # Get parameter values for this grid point
            indices = np.unravel_index(i, tuple([self.grid_points] * len(param_names)))
            
            params = {
                name: grids[j][indices]
                for j, name in enumerate(param_names)
            }
            
            # Evaluate
            try:
                results = objective_function(params)
                score = self.evaluate_objectives(params, results)
                
                self.evaluation_count += 1
                self.convergence_history.append(score)
                self.parameter_history.append(params.copy())
                
                if score < best_score:
                    best_score = score
                    best_params = params.copy()
                
            except Exception as e:
                # Skip failed evaluations
                continue
        
        execution_time = time.time() - start_time
        
        return OptimizationResult(
            success=best_params is not None,
            best_parameters=best_params or {},
            best_score=best_score,
            iteration_count=total_points,
            evaluation_count=self.evaluation_count,
            execution_time=execution_time,
            convergence_history=self.convergence_history,
            parameter_history=self.parameter_history,
            message=f"Grid search completed: {total_points} evaluations"
        )


class RandomSearchOptimizer(BaseOptimizer):
    """Random search optimizer"""
    
    def optimize(
        self,
        objective_function: Callable[[Dict[str, float]], Dict[str, float]]
    ) -> OptimizationResult:
        """Run random search"""
        start_time = time.time()
        
        best_score = float('inf')
        best_params = None
        
        for iteration in range(self.max_iterations):
            # Random sample from parameter spaces
            params = {
                name: space.random_sample(1)[0]
                for name, space in self.parameter_spaces.items()
            }
            
            try:
                results = objective_function(params)
                score = self.evaluate_objectives(params, results)
                
                self.evaluation_count += 1
                self.convergence_history.append(score)
                self.parameter_history.append(params.copy())
                
                if score < best_score:
                    best_score = score
                    best_params = params.copy()
                
            except Exception as e:
                continue
        
        execution_time = time.time() - start_time
        
        return OptimizationResult(
            success=best_params is not None,
            best_parameters=best_params or {},
            best_score=best_score,
            iteration_count=self.max_iterations,
            evaluation_count=self.evaluation_count,
            execution_time=execution_time,
            convergence_history=self.convergence_history,
            parameter_history=self.parameter_history,
            message=f"Random search completed: {self.max_iterations} iterations"
        )


class ParticleSwarmOptimizer(BaseOptimizer):
    """Particle Swarm Optimization for circuit sizing"""
    
    def __init__(
        self,
        *args,
        n_particles: int = 20,
        inertia: float = 0.7,
        cognitive: float = 1.5,
        social: float = 1.5,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.n_particles = n_particles
        self.w = inertia
        self.c1 = cognitive
        self.c2 = social
    
    def optimize(
        self,
        objective_function: Callable[[Dict[str, float]], Dict[str, float]]
    ) -> OptimizationResult:
        """Run PSO optimization"""
        start_time = time.time()
        
        param_names = list(self.parameter_spaces.keys())
        n_dims = len(param_names)
        
        # Initialize particles
        particles = np.array([
            [space.random_sample(1)[0] for space in self.parameter_spaces.values()]
            for _ in range(self.n_particles)
        ])
        
        velocities = np.zeros((self.n_particles, n_dims))
        personal_best_positions = particles.copy()
        personal_best_scores = np.full(self.n_particles, float('inf'))
        
        global_best_position = None
        global_best_score = float('inf')
        
        # Main PSO loop
        for iteration in range(self.max_iterations):
            for i in range(self.n_particles):
                # Create parameter dictionary
                params = {name: particles[i, j] for j, name in enumerate(param_names)}
                
                try:
                    results = objective_function(params)
                    score = self.evaluate_objectives(params, results)
                    
                    self.evaluation_count += 1
                    
                    # Update personal best
                    if score < personal_best_scores[i]:
                        personal_best_scores[i] = score
                        personal_best_positions[i] = particles[i].copy()
                    
                    # Update global best
                    if score < global_best_score:
                        global_best_score = score
                        global_best_position = particles[i].copy()
                
                except:
                    continue
            
            # Update velocities and positions
            r1, r2 = np.random.rand(2)
            
            if global_best_position is not None:
                for i in range(self.n_particles):
                    velocities[i] = (
                        self.w * velocities[i] +
                        self.c1 * r1 * (personal_best_positions[i] - particles[i]) +
                        self.c2 * r2 * (global_best_position - particles[i])
                    )
                    
                    particles[i] += velocities[i]
                    
                    # Enforce bounds
                    for j, (name, space) in enumerate(self.parameter_spaces.items()):
                        particles[i, j] = np.clip(
                            particles[i, j],
                            space.min_value,
                            space.max_value
                        )
            
            self.convergence_history.append(global_best_score)
        
        execution_time = time.time() - start_time
        
        best_params = {
            name: global_best_position[j]
            for j, name in enumerate(param_names)
        } if global_best_position is not None else {}
        
        return OptimizationResult(
            success=global_best_position is not None,
            best_parameters=best_params,
            best_score=global_best_score,
            iteration_count=self.max_iterations,
            evaluation_count=self.evaluation_count,
            execution_time=execution_time,
            convergence_history=self.convergence_history,
            parameter_history=self.parameter_history,
            message=f"PSO completed: {self.evaluation_count} evaluations"
        )


# ============================================================================
# Factory Function
# ============================================================================

def create_optimizer(
    method: OptimizationMethod,
    parameter_spaces: List[ParameterSpace],
    objectives: List[ObjectiveSpec],
    **kwargs
) -> BaseOptimizer:
    """Factory function to create optimizer"""
    
    if method == OptimizationMethod.GRID_SEARCH:
        return GridSearchOptimizer(parameter_spaces, objectives, **kwargs)
    elif method == OptimizationMethod.RANDOM_SEARCH:
        return RandomSearchOptimizer(parameter_spaces, objectives, **kwargs)
    elif method == OptimizationMethod.PARTICLE_SWARM:
        return ParticleSwarmOptimizer(parameter_spaces, objectives, **kwargs)
    elif method == OptimizationMethod.NEURAL_TURBO:
        from ai_engine.optimizers.neural_turbo import NeuralTurboOptimizer
        return NeuralTurboOptimizer(parameter_spaces, objectives, **kwargs)
    elif method == OptimizationMethod.BAYESIAN_NN:
        from ai_engine.optimizers.bayesian_optimizer import BayesianOptimizer
        return BayesianOptimizer(parameter_spaces, objectives, **kwargs)
    else:
        raise ValueError(f"Unsupported optimization method: {method}")
