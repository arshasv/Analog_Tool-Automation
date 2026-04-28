"""Minimal circuit data models"""
from pydantic import BaseModel
from enum import Enum
from typing import Optional, Dict, Any, List
from datetime import datetime


class ProcessStatus(str, Enum):
    """Process execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class CircuitRequest(BaseModel):
    """Circuit execution request"""
    circuit_type: str  # "current_mirror", "rc_circuit", etc.
    parameters: Dict[str, Any]  # Circuit parameters


class ProcessState(BaseModel):
    """Process execution state"""
    process_id: str
    status: ProcessStatus
    progress: int  # 0-100
    created_at: datetime
    updated_at: datetime
    results: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class ParameterSpec(BaseModel):
    """Specification for a single parameter extracted from a circuit file"""
    name: str
    type: str = "string"
    default: Optional[Any] = None
    description: Optional[str] = None


class RunResponse(BaseModel):
    """Response from unified /run endpoint"""
    process_id: str
    filename: str
    status: ProcessStatus
    parameters: Dict[str, Any]
    mode: str = "simulate"
    message: Optional[str] = None


class StatusResponse(BaseModel):
    """Status response with optional results"""
    process_id: str
    filename: Optional[str] = None
    status: ProcessStatus
    progress: int = 0
    parameters: Optional[Dict[str, Any]] = None
    mode: str = "simulate"
    results: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class OptimizationParams(BaseModel):
    I_target: float = 0.0
    gain_target: float = 0.0
    power_max: Optional[float] = None
    w_current: float = 1.0
    w_gain: float = 1.0
    w_power: float = 1.0
    epochs: Optional[int] = 100


class OptimizeRequest(BaseModel):
    process_id: str
    circuit_name: str
    netlist: str
    parameters: dict
    optimization: OptimizationParams

