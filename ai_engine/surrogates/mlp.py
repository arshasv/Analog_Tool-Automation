import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
from typing import List, Dict, Tuple, Optional

class CircuitMLPHead(nn.Module):
    """Single neural network head for ensemble"""
    def __init__(self, input_dim: int, output_dim: int, hidden_dims: List[int] = [128, 64]):
        super().__init__()
        layers = []
        last_dim = input_dim
        
        for h in hidden_dims:
            layers.append(nn.Linear(last_dim, h))
            layers.append(nn.ReLU())
            last_dim = h
            
        layers.append(nn.Linear(last_dim, output_dim))
        self.model = nn.Sequential(*layers)

    def forward(self, x):
        return self.model(x)


class CircuitMLPSurrogate(nn.Module):
    """
    Enhanced Neural Network surrogate with ensemble for uncertainty quantification.
    Learns the mapping: [Parameters] -> [Objectives]
    
    Now includes 5-network ensemble for uncertainty estimates while maintaining
    backward compatibility with existing code.
    """
    def __init__(self, input_dim: int, output_dim: int, hidden_dims: List[int] = [128, 64], 
                 ensemble_size: int = 5, use_ensemble: bool = True):
        super().__init__()
        self.input_dim = input_dim
        self.output_dim = output_dim
        self.hidden_dims = hidden_dims
        self.use_ensemble = use_ensemble
        
        # Single network (for backward compatibility)
        self.model = CircuitMLPHead(input_dim, output_dim, hidden_dims)
        
        # Ensemble for uncertainty (new feature)
        if use_ensemble:
            self.ensemble = nn.ModuleList([
                CircuitMLPHead(input_dim, output_dim, hidden_dims)
                for _ in range(ensemble_size)
            ])
        else:
            self.ensemble = None
        
        self.input_mean = None
        self.input_std = None
        self.output_mean = None
        self.output_std = None

    def forward(self, x):
        """Forward pass using primary model"""
        return self.model(x)
    
    def forward_ensemble(self, x):
        """Forward pass through all ensemble members"""
        if self.ensemble is None:
            return [self.forward(x)]
        return [model(x) for model in self.ensemble]

    def train_model(self, X, y, epochs=100, lr=0.01):
        """Train the surrogate on simulation data.
        
        Now trains both primary model and ensemble (if enabled) for better generalization.
        """
        X_tensor = torch.FloatTensor(X)
        y_tensor = torch.FloatTensor(y)
        
        # Normalize
        self.input_mean = X_tensor.mean(dim=0)
        self.input_std = X_tensor.std(dim=0) + 1e-6
        self.output_mean = y_tensor.mean(dim=0)
        self.output_std = y_tensor.std(dim=0) + 1e-6
        
        X_norm = (X_tensor - self.input_mean) / self.input_std
        y_norm = (y_tensor - self.output_mean) / self.output_std
        
        # Train primary model
        self._train_single_model(self.model, X_norm, y_norm, epochs, lr)
        
        # Train ensemble members
        if self.use_ensemble:
            for ensemble_model in self.ensemble:
                self._train_single_model(ensemble_model, X_norm, y_norm, epochs, lr)
    
    @staticmethod
    def _train_single_model(model, X_norm, y_norm, epochs=100, lr=0.01):
        """Train a single model (primary or ensemble member)"""
        optimizer = optim.Adam(model.parameters(), lr=lr)
        criterion = nn.MSELoss()
        
        model.train()
        for epoch in range(epochs):
            optimizer.zero_grad()
            output = model(X_norm)
            loss = criterion(output, y_norm)
            loss.backward()
            optimizer.step()

    def predict(self, X, return_uncertainty: bool = False) -> Tuple[np.ndarray, Optional[np.ndarray]]:
        """Predict objectives for given parameters.
        
        Args:
            X: Input parameters
            return_uncertainty: If True, return (mean, std) tuple. Otherwise just mean (backward compat).
        
        Returns:
            If return_uncertainty=False: predictions (backward compatible)
            If return_uncertainty=True: (mean, std) tuple for Bayesian optimization
        """
        self.eval()
        with torch.no_grad():
            X_tensor = torch.FloatTensor(X)
            X_norm = (X_tensor - self.input_mean) / self.input_std
            
            if self.use_ensemble and return_uncertainty:
                # Get predictions from all ensemble members
                predictions_norm = torch.stack([
                    model(X_norm) for model in self.ensemble
                ])  # Shape: [ensemble_size, batch, output_dim]
                
                # Denormalize
                predictions = (predictions_norm * self.output_std) + self.output_mean
                
                # Compute mean and std
                mean = predictions.mean(dim=0).numpy()
                std = predictions.std(dim=0).numpy()
                
                return mean, std
            else:
                # Use primary model only (backward compatible)
                prediction_norm = self.model(X_norm)
                prediction = (prediction_norm * self.output_std) + self.output_mean
                
                if return_uncertainty:
                    # Return zero uncertainty if ensemble disabled
                    return prediction.numpy(), np.zeros_like(prediction.numpy())
                else:
                    return prediction.numpy()
