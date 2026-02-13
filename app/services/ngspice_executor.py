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
import glob
from app.utils.plotting import (
    create_dc_plot,
    create_ac_plot,
    create_transient_plot,
    create_ac_plot_from_data,
    create_transient_plot_from_data,
)

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
        
        # Ensure stale output is removed
        if output_file.exists():
            output_file.unlink()
        
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
        """Parse DC operating point from tabular or list output."""
        results = {}
        
        # 1. Try to find values in a table (e.g. from print command)
        # Look for v(vout), v(vdd), etc.
        # Header: Index  node_name
        # Line:   0      0.90000
        
        # Simple heuristic: find lines with numbers
        lines = output.splitlines()
        for i, line in enumerate(lines):
            if "vout" in line.lower() and i + 2 < len(lines):
                # Try to get the value from the next formatted lines
                m = re.findall(r"[-+]?\d*\.?\d+[eE]?[-+]?\d*", lines[i+2])
                if len(m) >= 2: # Index, Value
                     results["v_vout"] = float(m[1])
        
        # 2. Fallback to direct assignment patterns v(node) = val
        voltage_pattern = r"v\(([\w\.\+]+)\)\s*=\s*([-+]?\d*\.?\d+[eE]?[-+]?\d*)"
        for match in re.finditer(voltage_pattern, output, re.IGNORECASE):
            node_name = match.group(1).lower()
            results[f"v_{node_name}"] = float(match.group(2))
            
        current_pattern = r"i\(([\w\.\+]+)\)\s*=\s*([-+]?\d*\.?\d+[eE]?[-+]?\d*)"
        for match in re.finditer(current_pattern, output, re.IGNORECASE):
            name = match.group(1).lower()
            results[f"i_{name}"] = float(match.group(2))
        
        return results

    @staticmethod
    def parse_ac_analysis(output: str) -> Dict[str, float]:
        """Parse AC analysis results from tabular 'print' output."""
        results = {"gain_db": 0.0, "phase_margin_deg": 0.0, "bandwidth_hz": 0.0}
        
        # Look for tabular data from 'print vdb(vout)'
        lines = output.splitlines()
        found_data = False
        vdb_values = []
        
        for i, line in enumerate(lines):
            if "vdb(vout)" in line.lower():
                found_data = True
                # Skip header and separator
                for data_line in lines[i+2:]:
                    parts = data_line.split()
                    if len(parts) >= 3: # Index, Freq, Value
                        try:
                            vdb_values.append(float(parts[2]))
                        except ValueError: break
                    else: break
                break
        
        if vdb_values:
            results["gain_db"] = max(vdb_values)
            # Rough bandwidth: where gain drops by 3dB from peak
            peak = results["gain_db"]
            results["bandwidth_hz"] = 1e6 # Placeholder unless we parse freq too
        
        # Extract Phase Margin if explicitly printed or searched for
        pm_match = re.search(r"(?:phase_margin|pm)\s*=\s*([-+]?\d*\.?\d+)", output, re.IGNORECASE)
        if pm_match:
            results["phase_margin_deg"] = float(pm_match.group(1))

        return results

    @staticmethod
    def parse_transient_analysis(output: str) -> Dict[str, float]:
        """Parse transient analysis results."""
        results = {"overshoot_mv": 0.0, "settling_time_us": 0.0}
        
        # Look for v(vout) peak in transient
        lines = output.splitlines()
        v_values = []
        for i, line in enumerate(lines):
             if "v(vout)" in line.lower():
                 for data_line in lines[i+2:]:
                    parts = data_line.split()
                    if len(parts) >= 3:
                        try: v_values.append(float(parts[2]))
                        except ValueError: break
                    else: break
                 break
        
        if v_values:
            v_max = max(v_values)
            v_final = v_values[-1]
            results["overshoot_mv"] = max(0.0, (v_max - v_final) * 1000)
            
        return results
    
    # ------------------------------------------------------------------
    # Helpers for reading raw vector data exported by ngspice (wrdata)
    # ------------------------------------------------------------------
    @staticmethod
    def _load_xy_from_ascii(path: Path) -> Tuple[List[float], List[float]]:
        """
        Load simple XY data from an ASCII file generated by:
            set filetype=ascii
            wrdata <file> x y
        
        Heuristic parser: skips non-numeric header lines and collects
        lines with at least 2 float values.
        """
        xs: List[float] = []
        ys: List[float] = []
        try:
            with open(path, "r") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    parts = line.split()
                    # Require at least two numeric columns
                    if len(parts) < 2:
                        continue
                    try:
                        x = float(parts[0])
                        y = float(parts[1])
                    except ValueError:
                        # Likely header or metadata line
                        continue
                    xs.append(x)
                    ys.append(y)
        except Exception as e:
            logger.warning(f"Failed to load XY data from {path}: {e}")
        return xs, ys
    
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
            "errors": [],
            "plots": []
        }
        
        # Extract process_id from dc_netlist filename (assumes {process_id}_dc.spice)
        process_id = Path(dc_netlist).stem.replace("_dc", "")
        
        # 1. Run DC operating point
        logger.info(f"Running DC analysis: {dc_netlist}")
        success, dc_output = NgSpiceExecutor.run_simulation(dc_netlist, output_dir)
        if success:
            results["operating_point"] = NgSpiceExecutor.parse_operating_point(dc_output)
            logger.info(f"DC results: {results['operating_point']}")
            
            # Generate DC plot
            try:
                png_bytes = create_dc_plot(results["operating_point"])
                if png_bytes:
                    plot_path = output_dir / f"{process_id}_dc.png"
                    with open(plot_path, "wb") as f:
                        f.write(png_bytes)
                    results["plots"].append(str(plot_path))
            except Exception as e:
                logger.warning(f"Failed to create DC plot: {e}")
        else:
            results["errors"].append(f"DC analysis failed: {dc_output}")
            logger.warning(results["errors"][-1])
        
        # 2. Run AC small-signal analysis
        logger.info(f"Running AC analysis: {ac_netlist}")
        success, ac_output = NgSpiceExecutor.run_simulation(ac_netlist, output_dir)
        if success:
            results["ac_analysis"] = NgSpiceExecutor.parse_ac_analysis(ac_output)
            logger.info(f"AC results: {results['ac_analysis']}")
            
            # Generate AC plot from raw sweep data if available
            try:
                ac_ascii = output_dir / f"{process_id}_ac.csv"
                if ac_ascii.exists():
                    freq, mag_db = NgSpiceExecutor._load_xy_from_ascii(ac_ascii)
                    png_bytes = create_ac_plot_from_data(freq, mag_db)
                else:
                    png_bytes = create_ac_plot(results["ac_analysis"])
                if png_bytes:
                    plot_path = output_dir / f"{process_id}_ac.png"
                    with open(plot_path, "wb") as f:
                        f.write(png_bytes)
                    results["plots"].append(str(plot_path))
            except Exception as e:
                logger.warning(f"Failed to create AC plot: {e}")
        else:
            results["errors"].append(f"AC analysis failed: {ac_output}")
            logger.warning(results["errors"][-1])
        
        # 3. Run transient analysis
        logger.info(f"Running transient analysis: {transient_netlist}")
        success, tran_output = NgSpiceExecutor.run_simulation(transient_netlist, output_dir)
        if success:
            results["transient_analysis"] = NgSpiceExecutor.parse_transient_analysis(tran_output)
            logger.info(f"Transient results: {results['transient_analysis']}")
            
            # Generate Transient plot from raw waveform if available
            try:
                tran_ascii = output_dir / f"{process_id}_tran.csv"
                if tran_ascii.exists():
                    t, v = NgSpiceExecutor._load_xy_from_ascii(tran_ascii)
                    png_bytes = create_transient_plot_from_data(t, v)
                else:
                    png_bytes = create_transient_plot(results["transient_analysis"])
                if png_bytes:
                    plot_path = output_dir / f"{process_id}_tran.png"
                    with open(plot_path, "wb") as f:
                        f.write(png_bytes)
                    results["plots"].append(str(plot_path))
            except Exception as e:
                logger.warning(f"Failed to create Transient plot: {e}")

        else:
            results["errors"].append(f"Transient analysis failed: {tran_output}")
            logger.warning(results["errors"][-1])
        
        # 4. Check for any extra plots generated by ngspice (e.g. from .control blocks)
        # Look for files starting with process_id and ending in .png, .ps, .svg in output_dir
        # that are NOT the ones we just created.
        try:
             # We already collected our standard plots. Now check specifically for others if any.
             # This assumes user generated plots follow naming convention or we assume all image files 
             # starting with process_id found now belong to this process.
             candidates = list(output_dir.glob(f"{process_id}*.*"))
             known_plots = set(results["plots"])
             for cand in candidates:
                 if cand.suffix.lower() in ['.png', '.ps', '.svg', '.pdf']:
                     if str(cand) not in known_plots:
                         results["plots"].append(str(cand))
        except Exception as e:
            logger.warning(f"Failed to collect extra plots: {e}")

        
        results["success"] = len(results["errors"]) == 0
        return results


class OptimizationObjectives:
    """Define optimization objectives from AC and transient analysis results"""
    
    @staticmethod
    def create_objectives_from_analysis(
        analysis_results: Dict[str, Any],
        circuit_type: str = "unknown"
    ) -> List[Dict[str, Any]]:
        """Create optimization objectives based on circuit type."""
        objectives = []
        ac = analysis_results.get("ac_analysis", {})
        tran = analysis_results.get("transient_analysis", {})
        
        # Helper to get current value or 0.0
        def g(d, k): return d.get(k, 0.0)

        if circuit_type.lower() == "opamp":
            objectives = [
                {"name": "gain_db", "target": 60.0, "weight": 2.0, "minimize": False, "current": g(ac, "gain_db")},
                {"name": "phase_margin_deg", "target": 60.0, "weight": 2.0, "minimize": False, "current": g(ac, "phase_margin_deg")},
                {"name": "bandwidth_hz", "target": 1e7, "weight": 1.5, "minimize": False, "current": g(ac, "bandwidth_hz")},
                {"name": "settling_time_us", "target": 0.5, "weight": 1.0, "minimize": True, "current": g(tran, "settling_time_us")}
            ]
        elif circuit_type.lower() == "ldo":
            objectives = [
                {"name": "phase_margin_deg", "target": 50.0, "weight": 2.0, "minimize": False, "current": g(ac, "phase_margin_deg")},
                {"name": "overshoot_mv", "target": 10.0, "weight": 2.0, "minimize": True, "current": g(tran, "overshoot_mv")},
                {"name": "settling_time_us", "target": 1.0, "weight": 1.5, "minimize": True, "current": g(tran, "settling_time_us")}
            ]
        else: # Generic
            objectives = [
                {"name": "gain_db", "target": 40.0, "weight": 1.0, "minimize": False, "current": g(ac, "gain_db")},
                {"name": "phase_margin_deg", "target": 45.0, "weight": 1.0, "minimize": False, "current": g(ac, "phase_margin_deg")}
            ]
        
        return objectives
    
    @staticmethod
    def compute_fitness(
        objectives: List[Dict[str, Any]],
        actual_results: Dict[str, float]
    ) -> Dict[str, Any]:
        """
        Compute fitness vector and aggregate score based on spec constraints.
        
        Returns:
            {
                "score": float (0.0 to 1.0),
                "metrics": { "name": value, ... },
                "checks": { "name": bool, ... }
            }
        """
        if not objectives:
            return {"score": 0.0, "metrics": {}, "checks": {}}
        
        checks = {}
        metrics_vector = {}
        count_met = 0
        total_weight = 0.0
        weighted_score = 0.0
        
        for obj in objectives:
            name = obj["name"]
            target = obj["target"]
            weight = obj.get("weight", 1.0)
            minimize = obj.get("minimize", False)
            # Default to target if missing to avoid division by zero or errors
            current = actual_results.get(name, 0.0)
            metrics_vector[name] = current
            total_weight += weight
            
            # Check if met
            if minimize:
                met = current <= target
                # Score component: 1.0 if met, otherwise decays with error
                comp_score = 1.0 if met else 1.0 / (1.0 + (current - target) / (abs(target) + 1e-12))
            else:
                met = current >= target
                comp_score = 1.0 if met else (current / (target + 1e-12)) if current > 0 else 0.0
                
            checks[name] = met
            if met:
                count_met += 1
            
            weighted_score += comp_score * weight
            
        # Overall score is a combination of percentage of specs met 
        # and how close we are on the ones not met
        met_ratio = count_met / len(objectives)
        avg_comp_score = weighted_score / total_weight
        
        # Final score prioritizing meeting specs over just being close
        final_score = (met_ratio * 0.7) + (avg_comp_score * 0.3)
        
        return {
            "score": float(final_score),
            "metrics": metrics_vector,
            "checks": checks
        }
