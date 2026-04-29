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
import re
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

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

    _sky130_model_include_cache: Dict[str, Tuple[str, str]] = {}

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
    def _validate_sky130_compatibility(netlist_path: str) -> bool:
        """Validate that .options compat=ps is first directive for Sky130 compatibility."""
        try:
            with open(netlist_path, "r") as f:
                lines = f.readlines()
            
            # Find first non-comment, non-empty line
            for line in lines:
                stripped = line.strip()
                if stripped and not stripped.startswith("*"):
                    if stripped.startswith(".options compat=ps"):
                        return True
                    else:
                        logger.error(f"Sky130 validation failed: First directive is '{stripped}', expected '.options compat=ps'")
                        return False
            logger.error("Sky130 validation failed: No directives found in netlist")
            return False
        except Exception as e:
            logger.error(f"Sky130 validation error: {e}")
            return False

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
        in_control = False
        
        # Identify parameters that we will be injecting so we can filter them out of the source
        # to avoid duplicate definition overrides.
        params_to_filter = {k.lower() for k in parameters.keys()}
        # Standard names to always filter if they appear in source but we have them in params
        if "width" in params_to_filter: params_to_filter.add("w")
        if "length" in params_to_filter: params_to_filter.add("l")

        for line in lines:
            stripped = line.strip().lower()
            if stripped.startswith(".control"):
                in_control = True
                continue
            if stripped.startswith(".endc"):
                in_control = False
                continue
            if in_control:
                continue
            if stripped.startswith((".tran", ".dc ", ".ac ", ".op", ".plot", ".end")):
                continue
            
            # Filter out .param definitions for variables we are about to inject
            if stripped.startswith(".param"):
                parts = re.split(r"[\s=]+", stripped)
                if len(parts) > 1 and parts[1] in params_to_filter:
                    logger.info(f"Filtering duplicate .param {parts[1]} from source netlist")
                    continue

            filtered.append(line)
        
        # Extract hints
        meta = AnalysisOrchestrator._extract_metadata(circuit_netlist)

        # Force PDK path consistency
        fixed_lines = [AnalysisOrchestrator._fix_pdk_paths(l) for l in filtered]
        # Only inject Sky130 subcircuit includes if using Sky130 subcircuit models
        has_sky130_subckt = any("sky130_fd_pr__" in l.lower() for l in filtered)
        if has_sky130_subckt:
            fixed_lines = AnalysisOrchestrator._inject_explicit_sky130_model_includes(fixed_lines)

        # 1. Detect if the original netlist already has a .dc sweep
        dc_sweep_line = ""
        for line in lines:
            if line.strip().lower().startswith(".dc "):
                dc_sweep_line = line.strip()
                break

        with open(netlist_path, "w") as f:
            # CRITICAL: Sky130 compatibility mode must be FIRST directive
            f.write(f"* Parametric DC Analysis for {circuit_name}\n")
            f.write(".options compat=ps\n")
            f.write(".options reltol=1e-3 gmin=1e-12 scale=1u\n")
            f.write(".lib \"/opt/sky130_pdk/sky130A/libs.tech/ngspice/sky130.lib.spice\" tt\n")
            f.write(".temp 27\n")
            f.write(AnalysisOrchestrator._get_parametric_header())
            
            f.write("\n* Computed Parameters\n")
            for k, v in parameters.items():
                if not isinstance(v, (int, float)):
                    continue
                # If it's W or L, wrap in clamp
                if k.lower().startswith("w_") or k.lower() == "width":
                    f.write(f".param {k} = {{clampW({v})}}\n")
                elif k.lower().startswith("l_") or k.lower() == "length":
                    f.write(f".param {k} = {{clampL({v})}}\n")
                else:
                    f.write(f".param {k} = {v}\n")
            
            f.write("\n* Circuit Implementation\n")
            f.write("\n".join(fixed_lines))
            
            if dc_sweep_line:
                f.write(f"\n\n* DC Sweep Analysis (Extracted)\n")
                # Top-level .dc — auto-runs before .control executes in ngspice batch mode.
                # DO NOT call 'run' inside .control (double-run bug).
                f.write(f"{dc_sweep_line}\n")
                f.write(".control\n")
                f.write("set ngbehavior=hs\n")
                # Debug: verify optimized parameters
                f.write("print width length w l\n")
                f.write("set filetype=ascii\n")
                sweep_var = ""
                m_sweep = re.search(r"\.dc\s+([^\s]+)", dc_sweep_line, re.IGNORECASE)
                if m_sweep: sweep_var = m_sweep.group(1)

                # Determine plot variable
                if "dc_expr" in meta:
                    plot_var = meta["dc_expr"]
                else:
                    # Attempt to find the plotted variable from the original plot command if any
                    plot_var = "v(vout)"
                    if "mirror" in circuit_name.lower():
                        if "vmeas" in circuit_netlist.lower(): plot_var = "i(vmeas)"
                        elif "rload" in circuit_netlist.lower(): plot_var = "i(rload)"
                    
                    for line in lines:
                        if "plot " in line.lower():
                            # Simple extraction of the first thing after plot
                            m = re.search(r"plot\s+([^\s]+)", line, re.IGNORECASE)
                            if m: plot_var = m.group(1)
                            # Check if it has a 'vs' part
                            if " vs " in line.lower():
                                 # plot Y vs X
                                 m_vs = re.search(r"plot\s+([^\s]+)\s+vs\s+([^\s]+)", line, re.IGNORECASE)
                                 if m_vs:
                                     plot_var = m_vs.group(1)
                                     sweep_var = m_vs.group(2).replace("@", "").replace("[dc]", "")

                            break
                
                f.write("run\n")
                f.write(f"wrdata {process_id}_dc_sweep.csv {plot_var}\n")
                f.write(".endc\n")
            else:
                f.write("\n\n* DC Operating Point Analysis\n")
                # Top-level .op — auto-runs before .control in ngspice batch mode.
                f.write(".op\n")
                f.write(".control\n")
                f.write("set ngbehavior=hs\n")
                f.write("run\n")
                f.write("print all\n")
                f.write(".endc\n")
            f.write(".end\n")

        # Validate Sky130 compatibility before returning
        if not AnalysisOrchestrator._validate_sky130_compatibility(netlist_path):
            raise RuntimeError(f"Sky130 compatibility validation failed for {netlist_path}")

        return str(netlist_path)

    @staticmethod
    def _fix_pdk_paths(line: str) -> str:
        """Force replace any wrong PDK paths with the correct container standard path."""
        # Standardize on /opt/sky130_pdk/sky130A
        # Common variations used by users or in old configs
        wrong_paths = ["/opt/pdk/sky130A", "/usr/local/share/pdk/sky130A", "/opt/pdk", "/opt/sky130_pdk"]
        # We replace the longest first to avoid partial matches
        sorted_wrong = sorted(wrong_paths, key=len, reverse=True)
        standard = "/opt/sky130_pdk/sky130A"
        
        # Only replace if it looks like a spice .lib path
        if ".lib" in line:
            for wp in sorted_wrong:
                if wp in line:
                    # Special case: don't replace if it's already exactly the standard or starts with it
                    if line.count(standard) > 0 and line.index(standard) <= line.index(wp):
                         continue
                    return line.replace(wp, standard)
        return line

    @staticmethod
    def _extract_lib_path_from_line(line: str) -> Optional[Path]:
        """Extract .lib file path from a SPICE .lib line."""
        m = re.search(r"\.lib\s+\"([^\"]+)\"", line, re.IGNORECASE)
        if not m:
            m = re.search(r"\.lib\s+(\S+)", line, re.IGNORECASE)
            if not m:
                return None
        raw = m.group(1).strip()
        if raw.lower() in {"tt", "ss", "ff"}:
            return None
        return Path(raw)

    @staticmethod
    def _find_first_matching_file(root: Path, patterns: List[str]) -> Optional[Path]:
        """Find the first file matching one of the patterns under root."""
        if not root.exists():
            return None
        for pattern in patterns:
            for candidate in sorted(root.rglob(pattern)):
                if candidate.is_file():
                    return candidate
        return None

    @staticmethod
    def _resolve_explicit_sky130_tt_models(lib_path: Path) -> Optional[Tuple[Path, Path]]:
        """Resolve TT nfet/pfet include files for full Sky130 installs."""
        cache_key = str(lib_path)
        if cache_key in AnalysisOrchestrator._sky130_model_include_cache:
            nfet, pfet = AnalysisOrchestrator._sky130_model_include_cache[cache_key]
            return Path(nfet), Path(pfet)

        if not lib_path.exists():
            return None

        pdk_root = lib_path
        if lib_path.parent.name == "ngspice" and lib_path.parent.parent.name == "libs.tech":
            pdk_root = lib_path.parent.parent.parent

        search_roots = [
            pdk_root / "models",
            pdk_root / "libs.ref" / "sky130_fd_pr" / "spice",
            pdk_root / "libs.tech" / "ngspice",
        ]

        nfet_patterns = [
            "sky130_fd_pr__nfet_01v8__tt*.spice",
            "*nfet*01v8*tt*.spice",
            "sky130_fd_pr__nfet_01v8*.spice",
        ]
        pfet_patterns = [
            "sky130_fd_pr__pfet_01v8__tt*.spice",
            "*pfet*01v8*tt*.spice",
            "sky130_fd_pr__pfet_01v8*.spice",
        ]

        nfet_file = None
        pfet_file = None
        for root in search_roots:
            if nfet_file is None:
                nfet_file = AnalysisOrchestrator._find_first_matching_file(root, nfet_patterns)
            if pfet_file is None:
                pfet_file = AnalysisOrchestrator._find_first_matching_file(root, pfet_patterns)
            if nfet_file and pfet_file:
                break

        if not (nfet_file and pfet_file):
            return None

        AnalysisOrchestrator._sky130_model_include_cache[cache_key] = (str(nfet_file), str(pfet_file))
        return nfet_file, pfet_file

    @staticmethod
    def _inject_explicit_sky130_model_includes(lines: List[str]) -> List[str]:
        """Insert explicit TT nfet/pfet includes when full-PDK model files are available."""
        already_has_nfet = any("nfet_01v8" in l.lower() and ".include" in l.lower() for l in lines)
        already_has_pfet = any("pfet_01v8" in l.lower() and ".include" in l.lower() for l in lines)
        if already_has_nfet and already_has_pfet:
            return lines

        out_lines: List[str] = []
        injected = False
        for line in lines:
            out_lines.append(line)
            if injected:
                continue

            l_lower = line.lower()
            if ".lib" not in l_lower or "sky130.lib.spice" not in l_lower:
                continue

            lib_path = AnalysisOrchestrator._extract_lib_path_from_line(line)
            if lib_path is None:
                continue

            resolved = AnalysisOrchestrator._resolve_explicit_sky130_tt_models(lib_path)
            if not resolved:
                logger.info(
                    "No explicit sky130 nfet/pfet TT model files found near %s; using .lib corner only.",
                    lib_path,
                )
                continue

            nfet_file, pfet_file = resolved
            out_lines.append(f'.include "{nfet_file}"')
            out_lines.append(f'.include "{pfet_file}"')
            injected = True

        return out_lines

    @staticmethod
    def _extract_metadata(netlist: str) -> Dict[str, str]:
        """Extract metadata hints from SPICE comments like * @AC_EXPR: db(i(rload))"""
        meta = {}
        for line in netlist.splitlines():
            line = line.strip()
            if not (line.startswith("*") or line.startswith("#")):
                continue
            if "@AC_EXPR:" in line:
                meta["ac_expr"] = line.split("@AC_EXPR:")[1].strip()
            if "@TRAN_EXPR:" in line:
                meta["tran_expr"] = line.split("@TRAN_EXPR:")[1].strip()
            if "@DC_EXPR:" in line:
                meta["dc_expr"] = line.split("@DC_EXPR:")[1].strip()
            if "@AC_SOURCE:" in line:
                meta["ac_source"] = line.split("@AC_SOURCE:")[1].strip()
        return meta

    @staticmethod
    def _normalize_ac_vector_expr(expr: str) -> str:
        """Convert AC expression wrappers (db/vdb/mag/vm) to the underlying complex vector."""
        if not expr:
            return "v(vout)"
        raw = expr.strip()
        m = re.match(r"^(?:vdb|db|mag|vm)\((.+)\)$", raw, re.IGNORECASE)
        if m:
            return m.group(1).strip()
        return raw

    @staticmethod
    def generate_ac_netlist(
        process_id: str,
        circuit_name: str,
        parameters: Dict[str, Any],
        dc_bias_point: Dict[str, float],
        output_dir: Path = Path("data/designs"),
        circuit_netlist: str = "",
        circuit_type: str = "unknown",
    ) -> str:
        output_dir.mkdir(parents=True, exist_ok=True)
        netlist_path = output_dir / f"{process_id}_ac.spice"

        # Extract hints
        meta = AnalysisOrchestrator._extract_metadata(circuit_netlist)

        # Remove existing analysis, .control/.endc blocks, and .end
        lines = circuit_netlist.splitlines()
        filtered = []
        in_control = False
        
        # Identify parameters that we will be injecting so we can filter them out of the source
        params_to_filter = {k.lower() for k in parameters.keys()}
        if "width" in params_to_filter: params_to_filter.add("w")
        if "length" in params_to_filter: params_to_filter.add("l")

        for line in lines:
            stripped = line.strip().lower()
            if stripped.startswith(".control"):
                in_control = True
                continue
            if stripped.startswith(".endc"):
                in_control = False
                continue
            if in_control:
                continue
            if stripped.startswith((".tran", ".dc ", ".ac ", ".plot", ".end")):
                continue

            # Filter out .param definitions for variables we are about to inject
            if stripped.startswith(".param"):
                parts = re.split(r"[\s=]+", stripped)
                if len(parts) > 1 and parts[1] in params_to_filter:
                    logger.info(f"Filtering duplicate .param {parts[1]} from source netlist")
                    continue

            filtered.append(line)
            
        # Force PDK path consistency
        fixed_lines = [AnalysisOrchestrator._fix_pdk_paths(l) for l in filtered]
        # Only inject Sky130 subcircuit includes if using Sky130 subcircuit models
        has_sky130_subckt = any("sky130_fd_pr__" in l.lower() for l in filtered)
        if has_sky130_subckt:
            fixed_lines = AnalysisOrchestrator._inject_explicit_sky130_model_includes(fixed_lines)

        # Ensure an AC source exists for Bode plots
        ac_source = meta.get("ac_source")
        has_ac_in_netlist = any(" ac " in l.lower() for l in fixed_lines)
        
        if not has_ac_in_netlist:
             found_source = False
             for i, line in enumerate(fixed_lines):
                 l_lower = line.strip().lower()
                 if ac_source and l_lower.startswith(ac_source.lower()):
                     fixed_lines[i] = line.strip() + " ac 1"
                     found_source = True
                     break
                 
             if not found_source:
                 # Fallback: add ac 1 to any likely input source
                 for i, line in enumerate(fixed_lines):
                     l_lower = line.strip().lower()
                     if l_lower.startswith(("i", "v")) and any(x in l_lower for x in ["ref", "in", "sig", "source", "1"]):
                         fixed_lines[i] = line.strip() + " ac 1"
                         found_source = True
                         break

        # AC sweep configuration
        start_freq = 100.0
        stop_freq = 100e6
        points_per_dec = 50
        ac_csv_name = f"{process_id}_ac.csv"
        
        # Determine expression to export and plot
        if "ac_expr" in meta:
            ac_expr = meta["ac_expr"]
        elif circuit_type == "current_mirror":
            ac_expr = "i(rload)" if "rload" in circuit_netlist.lower() else "v(vout)"
        else:
            ac_expr = "v(vout)"
        ac_raw_expr = AnalysisOrchestrator._normalize_ac_vector_expr(ac_expr)
        ac_db_expr = f"db({ac_raw_expr})"
        
        with open(netlist_path, "w") as f:
            # CRITICAL: Sky130 compatibility mode must be FIRST directive
            f.write(f"* Parametric AC Analysis for {circuit_name}\n")
            f.write(".options compat=ps\n")
            f.write(".options reltol=1e-3 gmin=1e-12 scale=1u\n")
            f.write(".lib \"/opt/sky130_pdk/sky130A/libs.tech/ngspice/sky130.lib.spice\" tt\n")
            f.write(".temp 27\n")
            f.write(AnalysisOrchestrator._get_parametric_header())
            
            f.write("\n* Computed Parameters\n")
            for k, v in parameters.items():
                if not isinstance(v, (int, float)):
                    continue
                if k.lower().startswith("w_") or k.lower() == "width":
                    f.write(f".param {k} = {{clampW({v})}}\n")
                elif k.lower().startswith("l_") or k.lower() == "length":
                    f.write(f".param {k} = {{clampL({v})}}\n")
                else:
                    f.write(f".param {k} = {v}\n")
            
            f.write("\n* Circuit Implementation\n")
            f.write("\n".join(fixed_lines))
            f.write("\n\n* AC Analysis\n")
            # Top-level .ac directive — ngspice batch mode auto-runs this before .control executes.
            # DO NOT call 'run' inside .control: that triggers a second AC sweep which fails
            # ("no data saved for A.C.") and wipes the first run's data before wrdata can export it.
            f.write(f".ac dec {points_per_dec} {int(start_freq)} {int(stop_freq)}\n")
            f.write(".control\n")
            f.write("set ngbehavior=hs\n")
            # Debug: verify optimized parameters
            f.write("print width length w l\n")
            f.write("run\n")
            f.write("set filetype=ascii\n")
            f.write(f"wrdata {ac_csv_name} {ac_raw_expr}\n")
            f.write(".endc\n")
            f.write(".end\n")

        # Validate Sky130 compatibility before returning
        if not AnalysisOrchestrator._validate_sky130_compatibility(netlist_path):
            raise RuntimeError(f"Sky130 compatibility validation failed for {netlist_path}")

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

        # Extract hints
        meta = AnalysisOrchestrator._extract_metadata(circuit_netlist)

        lines = circuit_netlist.splitlines()
        filtered = []
        in_control = False
        
        # Identify parameters that we will be injecting so we can filter them out of the source
        params_to_filter = {k.lower() for k in parameters.keys()}
        if "width" in params_to_filter: params_to_filter.add("w")
        if "length" in params_to_filter: params_to_filter.add("l")

        for line in lines:
            stripped = line.strip().lower()
            if stripped.startswith(".control"):
                in_control = True
                continue
            if stripped.startswith(".endc"):
                in_control = False
                continue
            if in_control:
                continue
            if stripped.startswith((".tran", ".dc ", ".ac ", ".plot", ".end")):
                continue

            # Filter out .param definitions for variables we are about to inject
            if stripped.startswith(".param"):
                parts = re.split(r"[\s=]+", stripped)
                if len(parts) > 1 and parts[1] in params_to_filter:
                    logger.info(f"Filtering duplicate .param {parts[1]} from source netlist")
                    continue

            filtered.append(line)
            
        # Force PDK path consistency
        fixed_lines = [AnalysisOrchestrator._fix_pdk_paths(l) for l in filtered]
        # Only inject Sky130 subcircuit includes if using Sky130 subcircuit models
        has_sky130_subckt = any("sky130_fd_pr__" in l.lower() for l in filtered)
        if has_sky130_subckt:
            fixed_lines = AnalysisOrchestrator._inject_explicit_sky130_model_includes(fixed_lines)
        
        tran_csv_name = f"{process_id}_tran.csv"

        # Determine expression to plot
        if "tran_expr" in meta:
            tran_expr = meta["tran_expr"]
        elif "mirror" in circuit_name.lower():
            tran_expr = "i(rload)" if "rload" in circuit_netlist.lower() else "v(vout)"
        else:
            tran_expr = "v(vout)"

        with open(netlist_path, "w") as f:
            # CRITICAL: Sky130 compatibility mode must be FIRST directive
            f.write(f"* Parametric Transient Analysis for {circuit_name}\n")
            f.write(".options compat=ps\n")
            f.write(".options reltol=1e-3 gmin=1e-12 scale=1u\n")
            f.write(".lib \"/opt/sky130_pdk/sky130A/libs.tech/ngspice/sky130.lib.spice\" tt\n")
            f.write(".temp 27\n")
            f.write(AnalysisOrchestrator._get_parametric_header())
            
            f.write("\n* Computed Parameters\n")
            for k, v in parameters.items():
                if not isinstance(v, (int, float)):
                    continue
                if k.lower().startswith("w_") or k.lower() == "width":
                    f.write(f".param {k} = {{clampW({v})}}\n")
                elif k.lower().startswith("l_") or k.lower() == "length":
                    f.write(f".param {k} = {{clampL({v})}}\n")
                else:
                    f.write(f".param {k} = {v}\n")
            
            f.write("\n* Circuit Implementation\n")
            f.write("\n".join(fixed_lines))
            f.write("\n\n* Transient Analysis\n")
            # Top-level .tran — auto-runs in ngspice batch mode before .control executes.
            # DO NOT call 'run' inside .control: same double-run problem as AC analysis.
            f.write(".tran 1n 30u\n")
            f.write(".control\n")
            f.write("set ngbehavior=hs\n")
            f.write("run\n")
            # Export real transient waveform for Python plotting
            f.write("set filetype=ascii\n")
            f.write(f"wrdata {tran_csv_name} {tran_expr}\n")
            f.write(".endc\n")
            f.write(".end\n")

        # Validate Sky130 compatibility before returning
        if not AnalysisOrchestrator._validate_sky130_compatibility(netlist_path):
            raise RuntimeError(f"Sky130 compatibility validation failed for {netlist_path}")

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
            # Inject process_id into parameters so generator functions can use it for filenames
            params_with_id = {**parameters, "process_id": process_id}
            circuit_netlist = AnalysisOrchestrator._get_circuit_netlist(
                file_path, params_with_id
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
        circuit_type = get_circuit_type_from_filename(circuit_name)

        ac_path = AnalysisOrchestrator.generate_ac_netlist(
            process_id, circuit_name, parameters, dc_bias, output_dir,
            circuit_netlist=circuit_netlist,
            circuit_type=circuit_type,
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
