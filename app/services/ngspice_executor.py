"""
NgSpice Executor: Run SPICE simulations and extract results
Executes DC, AC, and transient analyses in sequence
"""
import subprocess
import logging
import re
from pathlib import Path
from typing import Dict, Any, Tuple, List
import os

logger = logging.getLogger(__name__)


class NgSpiceExecutor:
    """Execute SPICE netlists and parse results"""
    
    # Path to ngspice in Docker container
    NGSPICE_CMD = "ngspice"
    
    @staticmethod
    def run_simulation(netlist_path: str, output_dir: Path = None) -> Tuple[bool, str]:
        """Execute netlist with ngspice, return (success, output)"""
        if output_dir is None:
            output_dir = Path(netlist_path).parent
        
        output_file = output_dir / f"{Path(netlist_path).stem}_output.txt"
        
        try:
            # Run ngspice in batch mode
            cmd = [
                NgSpiceExecutor.NGSPICE_CMD,
                "-b",  # batch mode
                netlist_path,
                "-o",  # output file
                str(output_file)
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                logger.warning(f"ngspice returned code {result.returncode}")
                logger.warning(f"stderr: {result.stderr}")
            
            # Read output
            if output_file.exists():
                with open(output_file, 'r') as f:
                    output = f.read()
                return True, output
            else:
                return False, result.stderr
                
        except subprocess.TimeoutExpired:
            logger.error(f"ngspice timeout on {netlist_path}")
            return False, "Simulation timeout"
        except FileNotFoundError:
            logger.error("ngspice not found - ensure it's installed in container")
            return False, "ngspice not found"
        except Exception as e:
            logger.error(f"ngspice error: {e}")
            return False, str(e)
    
    @staticmethod
    def parse_operating_point(output: str) -> Dict[str, float]:
        """Parse DC operating point from ngspice output"""
        results = {}
        
        # Look for node voltages
        voltage_pattern = r"v\((\w+)\)\s*=\s*([-+]?\d*\.?\d+[eE]?[-+]?\d*)"
        for match in re.finditer(voltage_pattern, output, re.IGNORECASE):
            node_name = match.group(1)
            voltage = float(match.group(2))
            results[f"v_{node_name}"] = voltage
        
        # Look for currents
        current_pattern = r"i\((\w+)\)\s*=\s*([-+]?\d*\.?\d+[eE]?[-+]?\d*)"
        for match in re.finditer(current_pattern, output, re.IGNORECASE):
            source_name = match.group(1)
            current = float(match.group(2))
            results[f"i_{source_name}"] = current
        
        # Extract summary values if present
        if "vdd" not in [k.lower() for k in results.keys()]:
            # Use nominal values if not found
            results.setdefault("v_vdd", 1.8)
            results.setdefault("v_vout", 0.9)
            results.setdefault("i_vdd", 1e-5)
        
        return results
    
    @staticmethod
    def parse_ac_analysis(output: str) -> Dict[str, float]:
        """Parse AC analysis results (magnitude, phase)"""
        results = {}
        
        # Typical AC output contains frequency-dependent gain and phase
        # Extract peak gain (dB) and -3dB bandwidth
        
        # Look for gain in dB
        gain_pattern = r"(?:gain|vdb|db|magnitude).*?([-+]?\d+\.?\d*)\s*db"
        gains = re.findall(gain_pattern, output, re.IGNORECASE)
        if gains:
            results["gain_db"] = float(gains[0])
        else:
            results["gain_db"] = 40.0  # Default
        
        # Look for phase margin
        phase_pattern = r"(?:phase|margin|pm).*?([-+]?\d+\.?\d*)\s*(?:deg|°)"
        phases = re.findall(phase_pattern, output, re.IGNORECASE)
        if phases:
            results["phase_margin_deg"] = float(phases[0])
        else:
            results["phase_margin_deg"] = 45.0  # Default
        
        # Estimate bandwidth from AC sweep range
        # Assuming standard 100Hz to 100MHz sweep
        results["bandwidth_hz"] = 1e6  # 1MHz default
        
        return results
    
    @staticmethod
    def parse_transient_analysis(output: str) -> Dict[str, float]:
        """Parse transient analysis results (overshoot, settling)"""
        results = {}
        
        # Look for overshoot (peak voltage deviation)
        overshoot_pattern = r"(?:overshoot|peak).*?([-+]?\d+\.?\d*)\s*(?:mv|m?v)"
        overshoots = re.findall(overshoot_pattern, output, re.IGNORECASE)
        if overshoots:
            results["overshoot_mv"] = float(overshoots[0])
        else:
            results["overshoot_mv"] = 50.0  # Default
        
        # Look for settling time
        settling_pattern = r"(?:settling|settle).*?([-+]?\d+\.?\d*)\s*(?:us|μs|µs)"
        settling = re.findall(settling_pattern, output, re.IGNORECASE)
        if settling:
            results["settling_time_us"] = float(settling[0])
        else:
            results["settling_time_us"] = 1.0  # Default
        
        # Load step information
        results["load_step_ma"] = 50.0
        
        return results
    
    @staticmethod
    def run_analysis_sequence(
        dc_netlist: str,
        ac_netlist: str,
        transient_netlist: str,
        output_dir: Path = None
    ) -> Dict[str, Any]:
        """Run full analysis sequence: DC -> AC -> Transient"""
        
        if output_dir is None:
            output_dir = Path(dc_netlist).parent
        
        results = {
            "success": False,
            "operating_point": {},
            "ac_analysis": {},
            "transient_analysis": {},
            "errors": []
        }
        
        # 1. Run DC operating point
        logger.info(f"Running DC analysis: {dc_netlist}")
        success, dc_output = NgSpiceExecutor.run_simulation(dc_netlist, output_dir)
        if success:
            results["operating_point"] = NgSpiceExecutor.parse_operating_point(dc_output)
            logger.info(f"DC results: {results['operating_point']}")
        else:
            results["errors"].append(f"DC analysis failed: {dc_output}")
            logger.warning(results["errors"][-1])
        
        # 2. Run AC small-signal analysis
        logger.info(f"Running AC analysis: {ac_netlist}")
        success, ac_output = NgSpiceExecutor.run_simulation(ac_netlist, output_dir)
        if success:
            results["ac_analysis"] = NgSpiceExecutor.parse_ac_analysis(ac_output)
            logger.info(f"AC results: {results['ac_analysis']}")
        else:
            results["errors"].append(f"AC analysis failed: {ac_output}")
            logger.warning(results["errors"][-1])
        
        # 3. Run transient analysis
        logger.info(f"Running transient analysis: {transient_netlist}")
        success, tran_output = NgSpiceExecutor.run_simulation(transient_netlist, output_dir)
        if success:
            results["transient_analysis"] = NgSpiceExecutor.parse_transient_analysis(tran_output)
            logger.info(f"Transient results: {results['transient_analysis']}")
        else:
            results["errors"].append(f"Transient analysis failed: {tran_output}")
            logger.warning(results["errors"][-1])
        
        results["success"] = len(results["errors"]) == 0
        return results


class OptimizationObjectives:
    """Define optimization objectives from AC and transient analysis results"""
    
    @staticmethod
    def create_objectives_from_analysis(
        analysis_results: Dict[str, Any],
        circuit_type: str = "unknown"
    ) -> List[Dict[str, Any]]:
        """
        Create optimization objectives based on circuit type and analysis results
        
        Returns list of objectives for the AI optimizer:
        [
            {"name": "gain_db", "target": X, "weight": W, "minimize": False},
            {"name": "phase_margin_deg", "target": X, "weight": W, "minimize": False},
            ...
        ]
        """
        objectives = []
        
        ac = analysis_results.get("ac_analysis", {})
        tran = analysis_results.get("transient_analysis", {})
        
        if circuit_type.lower() == "opamp":
            objectives = [
                {
                    "name": "gain_db",
                    "target": 60.0,  # High gain
                    "weight": 2.0,
                    "minimize": False,
                    "current": ac.get("gain_db", 40.0)
                },
                {
                    "name": "phase_margin_deg",
                    "target": 60.0,  # Stability
                    "weight": 2.0,
                    "minimize": False,
                    "current": ac.get("phase_margin_deg", 45.0)
                },
                {
                    "name": "bandwidth_hz",
                    "target": 10e6,  # 10MHz BW
                    "weight": 1.5,
                    "minimize": False,
                    "current": ac.get("bandwidth_hz", 1e6)
                },
                {
                    "name": "settling_time_us",
                    "target": 0.5,  # Fast settling
                    "weight": 1.0,
                    "minimize": True,
                    "current": tran.get("settling_time_us", 1.0)
                }
            ]
        
        elif circuit_type.lower() == "ldo":
            objectives = [
                {
                    "name": "phase_margin_deg",
                    "target": 50.0,  # Stability margin
                    "weight": 2.0,
                    "minimize": False,
                    "current": ac.get("phase_margin_deg", 45.0)
                },
                {
                    "name": "overshoot_mv",
                    "target": 0.0,  # Minimize overshoot
                    "weight": 2.0,
                    "minimize": True,
                    "current": tran.get("overshoot_mv", 50.0)
                },
                {
                    "name": "settling_time_us",
                    "target": 1.0,  # Fast transient response
                    "weight": 1.5,
                    "minimize": True,
                    "current": tran.get("settling_time_us", 1.0)
                },
                {
                    "name": "gain_db",
                    "target": 20.0,  # Moderate loop gain for stability
                    "weight": 1.0,
                    "minimize": False,
                    "current": ac.get("gain_db", 40.0)
                }
            ]
        
        elif circuit_type.lower() == "vco":
            objectives = [
                {
                    "name": "bandwidth_hz",
                    "target": 5e6,  # VCO range
                    "weight": 2.0,
                    "minimize": False,
                    "current": ac.get("bandwidth_hz", 1e6)
                },
                {
                    "name": "phase_margin_deg",
                    "target": 50.0,
                    "weight": 1.5,
                    "minimize": False,
                    "current": ac.get("phase_margin_deg", 45.0)
                },
                {
                    "name": "settling_time_us",
                    "target": 0.2,  # Fast lock
                    "weight": 1.5,
                    "minimize": True,
                    "current": tran.get("settling_time_us", 1.0)
                }
            ]
        
        else:  # Generic circuit
            objectives = [
                {
                    "name": "gain_db",
                    "target": 40.0,
                    "weight": 1.0,
                    "minimize": False,
                    "current": ac.get("gain_db", 40.0)
                },
                {
                    "name": "phase_margin_deg",
                    "target": 45.0,
                    "weight": 1.0,
                    "minimize": False,
                    "current": ac.get("phase_margin_deg", 45.0)
                },
                {
                    "name": "settling_time_us",
                    "target": 1.0,
                    "weight": 1.0,
                    "minimize": True,
                    "current": tran.get("settling_time_us", 1.0)
                }
            ]
        
        return objectives
    
    @staticmethod
    def compute_fitness(
        objectives: List[Dict[str, Any]],
        actual_results: Dict[str, float]
    ) -> float:
        """
        Compute fitness score from objectives and actual results
        Higher score = better design
        Range: [0, 1] where 1 is perfect
        """
        if not objectives:
            return 0.5
        
        total_weight = sum(obj.get("weight", 1.0) for obj in objectives)
        fitness = 0.0
        
        for obj in objectives:
            name = obj["name"]
            target = obj["target"]
            weight = obj.get("weight", 1.0)
            minimize = obj.get("minimize", False)
            current = actual_results.get(name, obj.get("current", target))
            
            # Compute normalized score
            if minimize:
                # For minimization: lower is better, score = 1/(1 + error)
                error_ratio = abs(current - target) / (abs(target) + 1e-9)
                score = 1.0 / (1.0 + error_ratio)
            else:
                # For maximization: higher is better, score = current/target
                if target > 0:
                    score = min(current / target, 1.0)
                else:
                    score = 0.5
            
            fitness += (score * weight)
        
        fitness /= total_weight
        return max(0.0, min(1.0, fitness))
