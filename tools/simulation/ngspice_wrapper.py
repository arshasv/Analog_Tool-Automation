"""
Ngspice Simulation Service
Handles SPICE simulation execution and result parsing
"""
import subprocess
import asyncio
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import re
import numpy as np
from datetime import datetime

from app.core.config import settings


@dataclass
class SimulationResult:
    """Simulation result container"""
    success: bool
    status: str
    netlist_file: str
    output_file: Optional[str] = None
    data_file: Optional[str] = None
    stdout: str = ""
    stderr: str = ""
    execution_time: float = 0.0
    measurements: Dict[str, float] = None
    
    def __post_init__(self):
        if self.measurements is None:
            self.measurements = {}


class NgspiceSimulator:
    """Ngspice simulation wrapper"""
    
    def __init__(self, ngspice_bin: str = None):
        """Initialize simulator"""
        self.ngspice_bin = ngspice_bin or settings.NGSPICE_BIN
        self._verify_installation()
    
    def _verify_installation(self) -> bool:
        """Verify Ngspice installation"""
        try:
            result = subprocess.run(
                [self.ngspice_bin, "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                return True
            else:
                raise RuntimeError(f"Ngspice not found at {self.ngspice_bin}")
        except Exception as e:
            raise RuntimeError(f"Ngspice verification failed: {e}")
    
    async def simulate_async(
        self,
        netlist_file: str,
        output_dir: Optional[str] = None,
        timeout: int = None
    ) -> SimulationResult:
        """Run simulation asynchronously"""
        return await asyncio.to_thread(
            self.simulate,
            netlist_file,
            output_dir,
            timeout
        )
    
    def simulate(
        self,
        netlist_file: str,
        output_dir: Optional[str] = None,
        timeout: int = None
    ) -> SimulationResult:
        """
        Run Ngspice simulation
        
        Args:
            netlist_file: Path to SPICE netlist
            output_dir: Output directory for results
            timeout: Simulation timeout in seconds
            
        Returns:
            SimulationResult object
        """
        start_time = datetime.now()
        timeout = timeout or settings.SIMULATION_TIMEOUT
        
        # Validate netlist file
        netlist_path = Path(netlist_file)
        if not netlist_path.exists():
            return SimulationResult(
                success=False,
                status="error",
                netlist_file=netlist_file,
                stderr=f"Netlist file not found: {netlist_file}"
            )
        
        # Set output directory
        if output_dir is None:
            output_dir = netlist_path.parent
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Prepare output files
        base_name = netlist_path.stem
        output_file = output_path / f"{base_name}_output.log"
        
        try:
            # Run Ngspice in batch mode
            cmd = [
                self.ngspice_bin,
                "-b",  # Batch mode
                "-o", str(output_file),  # Output file
                str(netlist_file)
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=str(output_path)
            )
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            # Parse output for errors
            success = result.returncode == 0
            status = "completed" if success else "failed"
            
            # Check for common errors
            if "Error" in result.stderr or "error" in result.stdout.lower():
                success = False
                status = "error"
            
            # Parse measurements from output
            measurements = self._parse_measurements(result.stdout)
            
            # Find data files (CSV output)
            data_files = list(output_path.glob(f"{base_name}*.csv"))
            data_file = str(data_files[0]) if data_files else None
            
            return SimulationResult(
                success=success,
                status=status,
                netlist_file=str(netlist_file),
                output_file=str(output_file),
                data_file=data_file,
                stdout=result.stdout,
                stderr=result.stderr,
                execution_time=execution_time,
                measurements=measurements
            )
            
        except subprocess.TimeoutExpired:
            return SimulationResult(
                success=False,
                status="timeout",
                netlist_file=str(netlist_file),
                stderr=f"Simulation timeout after {timeout}s",
                execution_time=timeout
            )
        except Exception as e:
            return SimulationResult(
                success=False,
                status="error",
                netlist_file=str(netlist_file),
                stderr=str(e),
                execution_time=(datetime.now() - start_time).total_seconds()
            )
    
    def _parse_measurements(self, output: str) -> Dict[str, float]:
        """Parse measurement results from Ngspice output"""
        measurements = {}
        
        # Pattern: meas_name = value
        pattern = r"(\w+)\s*=\s*([-+]?[0-9]*\.?[0-9]+(?:[eE][-+]?[0-9]+)?)"
        
        for match in re.finditer(pattern, output):
            name, value = match.groups()
            try:
                measurements[name] = float(value)
            except ValueError:
                continue
        
        return measurements
    
    def load_csv_data(self, csv_file: str) -> Dict[str, np.ndarray]:
        """Load simulation data from CSV file"""
        try:
            data = np.loadtxt(csv_file, skiprows=1)
            
            # Read header to get variable names
            with open(csv_file, 'r') as f:
                header = f.readline().strip().split()
            
            # Create dictionary of arrays
            result = {}
            for i, name in enumerate(header):
                if i < data.shape[1]:
                    result[name] = data[:, i] if data.ndim > 1 else data
            
            return result
            
        except Exception as e:
            raise RuntimeError(f"Failed to load CSV data: {e}")
    
    def get_version(self) -> str:
        """Get Ngspice version"""
        try:
            result = subprocess.run(
                [self.ngspice_bin, "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            # Parse version from output
            match = re.search(r"ngspice-(\d+)", result.stdout)
            if match:
                return match.group(1)
            return "unknown"
        except:
            return "unknown"


# ============================================================================
# Convenience Functions
# ============================================================================

async def run_simulation(netlist_file: str, **kwargs) -> SimulationResult:
    """Convenience function to run simulation"""
    simulator = NgspiceSimulator()
    return await simulator.simulate_async(netlist_file, **kwargs)


def run_simulation_sync(netlist_file: str, **kwargs) -> SimulationResult:
    """Synchronous simulation"""
    simulator = NgspiceSimulator()
    return simulator.simulate(netlist_file, **kwargs)
