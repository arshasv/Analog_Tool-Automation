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

    Returns None if the file does not define generate_netlist().
    """
    try:
        spec = importlib.util.spec_from_file_location("_uploaded_circuit", file_path)
        if spec is None or spec.loader is None:
            return None
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        fn = getattr(mod, "generate_netlist", None)
        return fn
    except Exception as e:
        logger.warning(f"Could not load generate_netlist from {file_path}: {e}")
        return None


class AnalysisOrchestrator:
    """Orchestrate separate, properly-sequenced circuit analyses"""

    @staticmethod
    def _get_circuit_netlist(file_path: str, parameters: Dict[str, Any]) -> str:
        """Try to get the circuit netlist from the uploaded file.

        1. Dynamically import the file and call generate_netlist(**parameters).
        2. If the file doesn't define generate_netlist, fall back to reading
           the raw file content (in case it is already a SPICE netlist).
        """
        fn = _load_generate_netlist(file_path)
        if fn is not None:
            try:
                return fn(**parameters)
            except TypeError:
                # parameters may not match signature – try without
                try:
                    return fn()
                except Exception as e:
                    logger.error(f"generate_netlist() failed: {e}")

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
    def generate_dc_netlist(
        process_id: str,
        circuit_name: str,
        parameters: Dict[str, Any],
        output_dir: Path = Path("data/designs"),
        circuit_netlist: str = "",
    ) -> str:
        """Write the circuit's own netlist as the DC analysis file.

        The uploaded circuit files already contain complete netlists with
        .lib, supplies, device instantiations, and an analysis command.
        We save it directly so ngspice can run it.
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        netlist_path = output_dir / f"{process_id}_dc.spice"

        with open(netlist_path, "w") as f:
            f.write(circuit_netlist)

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
        """Generate an AC analysis variant of the circuit netlist.

        Takes the original netlist and replaces / appends an AC analysis
        command so ngspice produces frequency-domain data.
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        netlist_path = output_dir / f"{process_id}_ac.spice"

        # Strip trailing .end so we can append AC commands
        base = circuit_netlist
        # Remove existing analysis commands but keep circuit
        lines = base.splitlines()
        filtered = []
        for line in lines:
            stripped = line.strip().lower()
            # Skip existing analysis, .control/.endc blocks, and .end
            if stripped.startswith((".tran", ".dc ", ".ac ", ".control", ".endc", "run", "plot", ".end")):
                continue
            filtered.append(line)

        with open(netlist_path, "w") as f:
            f.write("\n".join(filtered))
            f.write("\n\n* AC Small-Signal Analysis\n")
            f.write(".ac dec 50 100Hz 100MHz\n")
            f.write(".control\n")
            f.write("run\n")
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
        """Generate a transient analysis variant of the circuit netlist."""
        output_dir.mkdir(parents=True, exist_ok=True)
        netlist_path = output_dir / f"{process_id}_tran.spice"

        # Strip trailing analysis commands
        lines = circuit_netlist.splitlines()
        filtered = []
        for line in lines:
            stripped = line.strip().lower()
            if stripped.startswith((".tran", ".dc ", ".ac ", ".control", ".endc", "run", "plot", ".end")):
                continue
            filtered.append(line)

        with open(netlist_path, "w") as f:
            f.write("\n".join(filtered))
            f.write("\n\n* Transient Analysis\n")
            f.write(".tran 1n 10u\n")
            f.write(".control\n")
            f.write("run\n")
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
    ) -> Dict[str, str]:
        """Create all three analysis netlists in proper sequence.

        If file_path is given, we dynamically call its generate_netlist()
        to produce the actual circuit-specific SPICE.

        Returns dict: {"dc": path, "ac": path, "transient": path}
        """
        # Get the real circuit netlist from the uploaded file
        circuit_netlist = ""
        if file_path:
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
            "sequence": ["dc", "ac", "transient"],
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
