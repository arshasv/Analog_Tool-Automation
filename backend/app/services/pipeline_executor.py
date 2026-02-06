"""Minimal circuit pipeline executor with file parsing"""
import asyncio
import logging
import ast
import os
from pathlib import Path
from datetime import datetime
from app.models.circuit import CircuitRequest, ProcessState, ProcessStatus

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
            # Small simulated pipeline: 1) validate, 2) generate netlist placeholder, 3) simulate
            await asyncio.sleep(1)
            PipelineExecutor.processes[process_id]["progress"] = 30

            # Create output netlist file referencing uploaded file
            out_dir = Path("data/designs")
            out_dir.mkdir(parents=True, exist_ok=True)
            netlist_path = out_dir / f"{process_id}.spice"
            with open(netlist_path, "w") as nf:
                nf.write(f"* Generated netlist for {process_id}\n")
                nf.write(f"* Source: {file_path}\n")
                nf.write(".include /opt/open_pdks/sky130/sky130A/libs.tech/ngspice/sky130.lib.spice\n")
                nf.write("* Parameters:\n")
                for k, v in parameters.items():
                    nf.write(f"* {k} = {v}\n")
                nf.write(".op\n.end\n")

            await asyncio.sleep(1)
            PipelineExecutor.processes[process_id]["progress"] = 80

            # Simulated results
            sim_results = {
                "operating_point": {"vdd": 1.8, "id": parameters.get("iref", 1e-5)},
                "ac_analysis": {"gain_db": 42.0, "bandwidth_hz": 9e5}
            }

            PipelineExecutor.processes[process_id]["status"] = ProcessStatus.COMPLETED
            PipelineExecutor.processes[process_id]["progress"] = 100
            PipelineExecutor.processes[process_id]["results"] = {
                "netlist_path": str(netlist_path),
                "simulation_output": sim_results
            }
            PipelineExecutor.processes[process_id]["updated_at"] = datetime.now()

        except Exception as e:
            logger.exception("Error running circuit from file")
            if process_id in PipelineExecutor.processes:
                PipelineExecutor.processes[process_id]["status"] = ProcessStatus.FAILED
                PipelineExecutor.processes[process_id]["error"] = str(e)
