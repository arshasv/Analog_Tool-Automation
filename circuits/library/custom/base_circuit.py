from typing import Dict, List, Any
from abc import ABC, abstractmethod
from ai_engine.optimizers.base_optimizer import ParameterSpace, ObjectiveSpec

class OptimizableCircuit(ABC):
    """
    Standard interface for any circuit that wants to use
    the Automated Design Optimization factory.
    """
    
    @abstractmethod
    def get_parameter_space(self) -> List[ParameterSpace]:
        """Define which 'knobs' the AI is allowed to turn"""
        pass
    
    @abstractmethod
    def get_objectives(self) -> List[ObjectiveSpec]:
        """Define the 'targets' (e.g., gain, error, power)"""
        pass
    
    @abstractmethod
    def simulate(self, params: Dict[str, float]) -> Dict[str, float]:
        """
        1. Update design with new params
        2. Generate netlist
        3. Run SPICE
        4. Return measurements
        """
        pass
