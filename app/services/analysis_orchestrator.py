"""
Analysis Orchestrator: Manages DC, AC, and Transient analyses with proper sequencing.

Now dynamically imports the uploaded Python circuit file and calls its
`generate_netlist()` function so that each circuit type produces its own
unique, correct SPICE netlist.
"""
import os
import importlib
import importlib.util
import logging
from pathlib import Path
from typing import Dict, Any

logger = logging.getLogger(__name__)


def _load_generate_netlist(file_path: str):
    """Dynamically import a Python file and return its generate_netlist function.
    Uses a unique module name to avoid sys.modules caching collisions.
    """
    try:
        import hashlib
        logger.info(f"Attempting to load module from {file_path}")
        module_name = f"circuit_{hashlib.md5(file_path.encode()).hexdigest()}"
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        if spec is None:
            logger.warning(f"spec_from_file_location returned None for {file_path} (exists={os.path.exists(file_path)})")
            return None
        if spec.loader is None:
            logger.warning(f"spec.loader is None for {file_path}")
            return None
        
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        fn = getattr(mod, "generate_netlist", None)
        if fn is None:
            logger.warning(f"generate_netlist not found in module {module_name}")
        return fn
    except Exception as e:
        logger.warning(f"Could not load generate_netlist from {file_path}: {e}")
        return None


class AnalysisOrchestrator:
    """Orchestrate separate, properly-sequenced circuit analyses"""

    @staticmethod
    def _get_circuit_netlist(file_path: str, parameters: Dict[str, Any]) -> str:
        """Try to get the circuit netlist from the uploaded file.
        Robustly handles both (params: dict) and keyword argument signatures.
        """
        logger.info(f"_get_circuit_netlist called for {file_path}")
        fn = _load_generate_netlist(file_path)
        if fn is not None:
            import inspect
            sig = inspect.signature(fn)
            try:
                # 1. If it takes a single dict named 'params' (modular block style)
                if 'params' in sig.parameters and len(sig.parameters) == 1:
                    logger.info(f"Generating netlist using params dict from {file_path}")
                    return fn(params=parameters)
                
                # 2. If it takes specific keyword arguments
                # Filter parameters to only those in the signature
                valid_params = {k: v for k, v in parameters.items() if k in sig.parameters}
                logger.info(f"Generating netlist using kwargs {valid_params.keys()} from {file_path}")
                if valid_params:
                    return fn(**valid_params)
                
                # 3. Fallback to just calling it (defaults)
                logger.info(f"Generating netlist using defaults from {file_path}")
                return fn()
            except Exception as e:
                logger.error(f"generate_netlist execution failed: {e}")

        # Fallback: treat the file content itself as SPICE
        try:
            with open(file_path, "r") as fh:
                return fh.read()
        except Exception:
            return ""

    # -----------------------------------------------------------------
    #  Individual analysis netlist generators
    # -----------------------------------------------------------------

    @staticmethod
    def _get_parametric_header() -> str:
        """Returns standard SPICE functions for DRC-safe parameter clamping."""
        return """
* Sky130 DRC Safe Clamps
.func clampW(x) = {max(0.42u, min(x, 50u))}
.func clampL(x) = {max(0.15u, min(x, 5u))}
"""

    @staticmethod
    def generate_dc_netlist(
        process_id: str,
        circuit_name: str,
        parameters: Dict[str, Any],
        output_dir: Path = Path("data/designs"),
        circuit_netlist: str = "",
    ) -> str:
        output_dir.mkdir(parents=True, exist_ok=True)
        netlist_path = output_dir / f"{process_id}_dc.spice"

        # Remove existing analysis, .control/.endc blocks, and .end
        lines = circuit_netlist.splitlines()
        filtered = []
        for line in lines:
            stripped = line.strip().lower()
            if stripped.startswith((".tran", ".dc ", ".ac ", ".op", ".control", ".endc", "run", "plot", ".end")):
                continue
            filtered.append(line)

        with open(netlist_path, "w") as f:
            f.write(f"* Parametric DC Analysis for {circuit_name}\n")
            f.write(AnalysisOrchestrator._get_parametric_header())
            
            f.write("\n* Computed Parameters\n")
            for k, v in parameters.items():
                # If it's W or L, wrap in clamp
                if k.lower().startswith("w_"):
                    f.write(f".param {k} = {{clampW({v}u)}}\n")
                elif k.lower().startswith("l_"):
                    f.write(f".param {k} = {{clampL({v}u)}}\n")
                else:
                    f.write(f".param {k} = {v}\n")
            
            f.write("\n* Circuit Implementation\n")
            f.write("\n".join(filtered))
            
            f.write("\n\n* DC Operating Point Analysis\n")
            f.write(".op\n")
            f.write(".control\n")
            f.write("run\n")
            f.write("print all\n")
            f.write(".endc\n")
            f.write(".end\n")

        return str(netlist_path)

    @staticmethod
    def generate_ac_netlist(
        process_id: str,
        circuit_name: str,
        parameters: Dict[str, Any],
        dc_bias_point: Dict[str, float],
        output_dir: Path = Path("data/designs"),
        circuit_netlist: str = "",
    ) -> str:
        output_dir.mkdir(parents=True, exist_ok=True)
        netlist_path = output_dir / f"{process_id}_ac.spice"

        # Remove existing analysis, .control/.endc blocks, and .end
        lines = circuit_netlist.splitlines()
        filtered = []
        for line in lines:
            stripped = line.strip().lower()
            if stripped.startswith((".tran", ".dc ", ".ac ", ".control", ".endc", "run", "plot", ".end")):
                continue
            filtered.append(line)
        # AC sweep configuration
        start_freq = 100.0
        stop_freq = 100e6
        points_per_dec = 50
        ac_csv_name = f"{process_id}_ac.csv"
        
        with open(netlist_path, "w") as f:
            f.write(f"* Parametric AC Analysis for {circuit_name}\n")
            f.write(AnalysisOrchestrator._get_parametric_header())
            
            f.write("\n* Computed Parameters\n")
            for k, v in parameters.items():
                if k.lower().startswith("w_"):
                    f.write(f".param {k} = {{clampW({v}u)}}\n")
                elif k.lower().startswith("l_"):
                    f.write(f".param {k} = {{clampL({v}u)}}\n")
                else:
                    f.write(f".param {k} = {v}\n")
            
            f.write("\n* Circuit Implementation\n")
            f.write("\n".join(filtered))
            f.write("\n\n* AC Analysis\n")
            f.write(f".ac dec {points_per_dec} {start_freq} {stop_freq}\n")
            f.write(".control\n")
            f.write("run\n")
            # Export real frequency response data for Python plotting
            f.write("set filetype=ascii\n")
            f.write(f"wrdata {ac_csv_name} frequency vdb(vout)\n")
            # Keep a simple print for debugging in case parsing is needed
            f.write("print vdb(vout)\n")
            f.write(".endc\n")
            f.write(".end\n")

        return str(netlist_path)

    @staticmethod
    def generate_transient_netlist(
        process_id: str,
        circuit_name: str,
        parameters: Dict[str, Any],
        output_dir: Path = Path("data/designs"),
        circuit_netlist: str = "",
    ) -> str:
        output_dir.mkdir(parents=True, exist_ok=True)
        netlist_path = output_dir / f"{process_id}_tran.spice"

        lines = circuit_netlist.splitlines()
        filtered = []
        for line in lines:
            stripped = line.strip().lower()
            if stripped.startswith((".tran", ".dc ", ".ac ", ".control", ".endc", "run", "plot", ".end")):
                continue
            filtered.append(line)
        tran_csv_name = f"{process_id}_tran.csv"

        with open(netlist_path, "w") as f:
            f.write(f"* Parametric Transient Analysis for {circuit_name}\n")
            f.write(AnalysisOrchestrator._get_parametric_header())
            
            f.write("\n* Computed Parameters\n")
            for k, v in parameters.items():
                if k.lower().startswith("w_"):
                    f.write(f".param {k} = {{clampW({v}u)}}\n")
                elif k.lower().startswith("l_"):
                    f.write(f".param {k} = {{clampL({v}u)}}\n")
                else:
                    f.write(f".param {k} = {v}\n")
            
            f.write("\n* Circuit Implementation\n")
            f.write("\n".join(filtered))
            f.write("\n\n* Transient Analysis\n")
            f.write(".tran 1n 10u\n")
            f.write(".control\n")
            f.write("run\n")
            # Export real transient waveform for Python plotting
            f.write("set filetype=ascii\n")
            f.write(f"wrdata {tran_csv_name} time v(vout)\n")
            # Keep a simple print for debugging
            f.write("print v(vout)\n")
            f.write(".endc\n")
            f.write(".end\n")

        return str(netlist_path)

    # -----------------------------------------------------------------
    #  Main entry point
    # -----------------------------------------------------------------

    @staticmethod
    def create_analysis_sequence(
        process_id: str,
        circuit_name: str,
        parameters: Dict[str, Any],
        output_dir: Path = Path("data/designs"),
        file_path: str = "",
        circuit_netlist: str = "",
    ) -> Dict[str, str]:
        """Create all three analysis netlists in proper sequence.
        Returns dict: {"dc": path, "ac": path, "transient": path}
        """
        output_dir.mkdir(parents=True, exist_ok=True)

        # Get the real circuit netlist from the uploaded file if not provided
        if not circuit_netlist and file_path:
            circuit_netlist = AnalysisOrchestrator._get_circuit_netlist(
                file_path, parameters
            )

        if not circuit_netlist:
            logger.warning(
                f"Could not extract netlist from {file_path}; "
                "using empty placeholder."
            )

        dc_path = AnalysisOrchestrator.generate_dc_netlist(
            process_id, circuit_name, parameters, output_dir,
            circuit_netlist=circuit_netlist,
        )

        dc_bias = {"vout": 0.9, "vin": 1.0, "vdd": 1.8}

        ac_path = AnalysisOrchestrator.generate_ac_netlist(
            process_id, circuit_name, parameters, dc_bias, output_dir,
            circuit_netlist=circuit_netlist,
        )

        transient_path = AnalysisOrchestrator.generate_transient_netlist(
            process_id, circuit_name, parameters, output_dir,
            circuit_netlist=circuit_netlist,
        )

        return {
            "dc": dc_path,
            "ac": ac_path,
            "transient": transient_path,
        }


def get_circuit_type_from_filename(filename: str) -> str:
    """Infer circuit type from filename"""
    filename_lower = filename.lower()
    if "ldo" in filename_lower:
        return "ldo"
    elif "vco" in filename_lower:
        return "vco"
    elif "mirror" in filename_lower:
        return "current_mirror"
    elif "diff" in filename_lower:
        return "differential_pair"
    elif "common" in filename_lower or "cs_amp" in filename_lower:
        return "common_source"
    elif "opamp" in filename_lower:
        return "opamp"
    elif "bandgap" in filename_lower:
        return "bandgap"
    else:
        return "unknown"
