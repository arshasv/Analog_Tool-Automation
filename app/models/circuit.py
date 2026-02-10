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
    message: Optional[str] = None


class StatusResponse(BaseModel):
    """Status response with optional results"""
    process_id: str
    filename: Optional[str] = None
    status: ProcessStatus
    progress: int = 0
    parameters: Optional[Dict[str, Any]] = None
    results: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

