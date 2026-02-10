"""Minimal circuit pipeline executor with file parsing"""
import asyncio
import logging
import ast
import os
from pathlib import Path
from datetime import datetime
import hashlib
from app.models.circuit import CircuitRequest, ProcessState, ProcessStatus
from app.services.analysis_orchestrator import AnalysisOrchestrator, get_circuit_type_from_filename
from app.services.ngspice_executor import NgSpiceExecutor, OptimizationObjectives

logger = logging.getLogger(__name__)


class PipelineExecutor:
    """Execute circuit pipeline and provide simple file parsing for parameters"""
    
    # In-memory process storage
    processes = {}
    
    @staticmethod
    async def run_circuit(process_id: str, request: CircuitRequest):
        """Run circuit simulation (existing JSON-based request)"""
        
        if process_id in PipelineExecutor.processes:
            PipelineExecutor.processes[process_id]["status"] = ProcessStatus.RUNNING
            PipelineExecutor.processes[process_id]["progress"] = 10
        
        try:
            await asyncio.sleep(1)
            sim_results = {
                "operating_point": {
                    "vdd": 1.8,
                    "id": request.parameters.get("iref", 10e-6),
                    "vgs": 0.65,
                    "vout": 0.9
                },
                "ac_analysis": {
                    "gain_db": 45.2,
                    "bandwidth_hz": 1e6,
                    "phase_deg": -85.5
                }
            }

            if process_id in PipelineExecutor.processes:
                PipelineExecutor.processes[process_id]["status"] = ProcessStatus.COMPLETED
                PipelineExecutor.processes[process_id]["progress"] = 100
                PipelineExecutor.processes[process_id]["results"] = {
                    "netlist_path": f"data/designs/{process_id}.spice",
                    "simulation_output": sim_results
                }
                PipelineExecutor.processes[process_id]["updated_at"] = datetime.now()

        except Exception as e:
            logger.error(f"Pipeline error: {e}")
            if process_id in PipelineExecutor.processes:
                PipelineExecutor.processes[process_id]["status"] = ProcessStatus.FAILED
                PipelineExecutor.processes[process_id]["error"] = str(e)

    @staticmethod
    def parse_parameters_from_file(file_path: str):
        """Parse a Python circuit file to extract a PARAMETERS dict or build_circuit signature.

        Returns a list of dicts: {name,type,default}
        """
        params = []
        try:
            with open(file_path, "r") as fh:
                src = fh.read()
            mod = ast.parse(src)
        except Exception:
            return params

        for node in mod.body:
            # Look for PARAMETERS = { 'iref': 1e-5, ... }
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id in ("PARAMETERS", "DEFAULT_PARAMS"):
                        if isinstance(node.value, ast.Dict):
                            keys = node.value.keys
                            values = node.value.values
                            for k, v in zip(keys, values):
                                try:
                                    name = ast.literal_eval(k)
                                except Exception:
                                    continue
                                try:
                                    default = ast.literal_eval(v)
                                except Exception:
                                    default = None
                                ptype = type(default).__name__ if default is not None else "string"
                                params.append({"name": name, "type": ptype, "default": default})
                            if params:
                                return params
            # Look for build_circuit(a, b=1e-6)
            if isinstance(node, ast.FunctionDef) and node.name == "build_circuit":
                arg_names = [a.arg for a in node.args.args]
                defaults = node.args.defaults
                num_args = len(arg_names)
                num_defaults = len(defaults)
                for i, name in enumerate(arg_names):
                    default = None
                    if i >= num_args - num_defaults:
                        try:
                            default = ast.literal_eval(defaults[i - (num_args - num_defaults)])
                        except Exception:
                            default = None
                    ptype = type(default).__name__ if default is not None else "string"
                    params.append({"name": name, "type": ptype, "default": default})
                if params:
                    return params

        return params

    @staticmethod
    async def run_circuit_from_file(process_id: str, file_path: str, parameters: dict):
        """Run pipeline using an uploaded python circuit file and parameter dict."""
        if process_id in PipelineExecutor.processes:
            PipelineExecutor.processes[process_id]["status"] = ProcessStatus.RUNNING
            PipelineExecutor.processes[process_id]["progress"] = 5

        try:
            # Small simulated pipeline: 1) validate, 2) generate separate analyses, 3) simulate
            await asyncio.sleep(1)
            PipelineExecutor.processes[process_id]["progress"] = 30

            # Extract circuit type and name
            circuit_type = get_circuit_type_from_filename(file_path)
            circuit_name = Path(file_path).stem
            
            # Generate separate netlists for DC, AC, and transient analyses
            out_dir = Path("data/designs")
            analysis_paths = AnalysisOrchestrator.create_analysis_sequence(
                process_id, circuit_name, parameters, out_dir,
                file_path=file_path,
            )

            await asyncio.sleep(0.5)
            PipelineExecutor.processes[process_id]["progress"] = 50

            # Execute netlists with ngspice
            logger.info(f"Executing ngspice analyses for {process_id}")
            analysis_results = NgSpiceExecutor.run_analysis_sequence(
                analysis_paths["dc"],
                analysis_paths["ac"],
                analysis_paths["transient"],
                out_dir
            )
            
            await asyncio.sleep(0.5)
            PipelineExecutor.processes[process_id]["progress"] = 80

            # Create optimization objectives from analysis results
            optimization_objectives = OptimizationObjectives.create_objectives_from_analysis(
                analysis_results,
                circuit_type
            )
            
            # Compute fitness score
            actual_metrics = {
                **analysis_results.get("ac_analysis", {}),
                **analysis_results.get("transient_analysis", {})
            }
            fitness = OptimizationObjectives.compute_fitness(
                optimization_objectives,
                actual_metrics
            )

            # Combine results
            sim_results = {
                "circuit_type": circuit_type,
                "analysis_netlists": analysis_paths,
                "analysis_success": analysis_results.get("success", False),
                "analysis_errors": analysis_results.get("errors", []),
                "operating_point": analysis_results.get("operating_point", {}),
                "ac_analysis": analysis_results.get("ac_analysis", {}),
                "transient_analysis": analysis_results.get("transient_analysis", {}),
                "optimization_objectives": optimization_objectives,
                "fitness_score": float(fitness)
            }

            PipelineExecutor.processes[process_id]["status"] = ProcessStatus.COMPLETED
            PipelineExecutor.processes[process_id]["progress"] = 100
            PipelineExecutor.processes[process_id]["results"] = {
                "netlist_paths": analysis_paths,
                "primary_netlist": analysis_paths["dc"],
                "simulation_output": sim_results
            }
            PipelineExecutor.processes[process_id]["updated_at"] = datetime.now()

        except Exception as e:
            logger.exception("Error running circuit from file")
            if process_id in PipelineExecutor.processes:
                PipelineExecutor.processes[process_id]["status"] = ProcessStatus.FAILED
                PipelineExecutor.processes[process_id]["error"] = str(e)
