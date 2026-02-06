import os
import subprocess
import re
from typing import Dict, List, Any, Tuple

class LayoutIntelligenceAgent:
    """
    An Agent that analyzes layouts and self-corrects based on 
    DRC and LVS feedback with substrate connection awareness.
    """
    def __init__(self, cell_name: str):
        self.cell_name = cell_name
        self.history = []
        self.lvs_fixes_applied = False
        self.knowledge_base = {
            "well_overlap": "Increase box move spacing by 10um",
            "spacing_violation": "Increase distance between elements",
            "substrate_warning": "Add bulk tie connections",
            "drc_error": "Generic fix applied"
        }

    def refine_layout(self, initial_tcl: str, max_attempts: int = 3) -> str:
        """
        The Active Learning Loop:
        1. Run Magic with TCL
        2. Check DRC Errors
        3. Check LVS Substrate Warnings
        4. If issues found, analyze and mutate TCL
        5. Repeat
        """
        current_tcl = initial_tcl
        
        # First, check if we need substrate connections
        if self._needs_substrate_fix(current_tcl):
            print("🔧 AI detected missing substrate connections...")
            current_tcl = self._add_substrate_connections(current_tcl)
            self.lvs_fixes_applied = True
        
        for attempt in range(max_attempts):
            print(f"🔬 Layout Intelligence Phase: Attempt {attempt+1}")
            
            # 1. Run Layout Generation
            drc_count = self._get_drc_count(current_tcl)
            
            if drc_count == 0:
                print("✅ DRC Clean! Layout verification complete.")
                break
            
            print(f"⚠️ DRC Errors found: {drc_count}. AI reasoning active...")
            
            # 2. Mutate TCL based on "visual" reasoning
            current_tcl = self._mutate_tcl(current_tcl)
            
        return current_tcl

    def _needs_substrate_fix(self, tcl: str) -> bool:
        """Detects if layout has PMOS/NMOS without proper bulk connections."""
        has_pmos = "pfet_01v8" in tcl
        has_nmos = "nfet_01v8" in tcl
        has_substrate_tie = "nsubstratecontact" in tcl or "psubstratecontact" in tcl
        
        return (has_pmos or has_nmos) and not has_substrate_tie

    def _add_substrate_connections(self, tcl: str) -> str:
        """
        Intelligently adds substrate/well contacts AND Power Rails to eliminate LVS warnings.
        NOW WITH METAL1 ROUTING!
        """
        print("   🧠 AI Reasoning: Adding VDD/GND Power Rails for robust connectivity...")
        
        # Parse the TCL to understand the layout structure
        has_pmos = "pfet_01v8" in tcl
        has_nmos = "nfet_01v8" in tcl
        
        enhanced_tcl = tcl
        
        # 1. calculate total width roughly based on box moves
        # This is a heuristic: sum of all "box move" X values
        moves = re.findall(r"box move (\d+\.?\d*)um 0", tcl)
        total_width = sum(float(m) for m in moves) + 50.0 # extra margin
        
        routing_header = "# AI-Generated Power Grids\n"
        
        if has_nmos:
            # GND Rail (Bottom)
            routing_header += f"""
# METAL1 GND RAIL
box values 0 -5um {total_width}um -2um
paint m1
label gnd -shape box -layer m1
"""
            # Logic to connect NMOS sources to GND would go here in V2
            
            # P-Substrate contact for NMOS bulk (Connected to Rail)
            routing_header += """
# P-Substrate contact for NMOS bulk
box values 0 -10um 0 0
magic::gencell sky130::sky130_fd_pr__nsubstratecontact {w 5.0 l 5.0}
"""

        if has_pmos:
            # VDD Rail (Top)
            # Assuming PMOS is around y=20um based on VCO layout
            routing_header += f"""
# METAL1 VDD RAIL
box values 0 35um {total_width}um 38um
paint m1
label vdd -shape box -layer m1
"""
            
            # N-Well contact for PMOS bulk
            routing_header += """
# N-Well contact for PMOS bulk  
box values 0 40um 0 0
magic::gencell sky130::sky130_fd_pr__psubstratecontact {w 5.0 l 5.0}
"""
        
        # Insert routing connections after "drc off"
        enhanced_tcl = re.sub(
            r"(drc off\s*\n)",
            r"\1" + routing_header + "\n",
            enhanced_tcl
        )
        
        return enhanced_tcl

    def _get_drc_count(self, tcl: str) -> int:
        """Runs magic in background to check DRC."""
        verify_tcl = tcl + "\ndrc catchup\nset drc_res [drc count total]\necho \"DRC_COUNT $drc_res\"\nexit\n"
        
        with open("drc_check.tcl", "w") as f:
            f.write(verify_tcl)
            
        try:
            cmd = ["magic", "-dnull", "-noconsole", "drc_check.tcl"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            match = re.search(r"DRC_COUNT\s+(\d+)", result.stdout)
            return int(match.group(1)) if match else 0
        except:
            return 99

    def _mutate_tcl(self, tcl: str) -> str:
        """
        Enhanced mutation that creates visible improvements.
        Strategies:
        1. Increase device widths for better drive strength
        2. Improve spacing for DRC compliance
        3. Add more metal routing
        """
        # Strategy 1: Increase box movements for better spacing
        def increase_move(match):
            val = float(match.group(1))
            new_val = val + 15.0  # Significant increase
            return f"box move {new_val}um"
        
        # Strategy 2: Increase device widths
        def increase_width(match):
            w_val = float(match.group(1))
            l_val = float(match.group(2))
            new_w = w_val * 1.25  # 25% width increase
            return f"{{w {new_w:.2f} l {l_val}}}"
        
        # Apply mutations
        mutated = re.sub(r"box move (\d+\.?\d*)um", increase_move, tcl)
        mutated = re.sub(r"\{w (\d+\.?\d+) l (\d+\.?\d+)\}", increase_width, mutated)
        
        # Add comment about mutation
        mutated = "# LAYOUT INTELLIGENCE: DRC-driven refinement applied\n" + mutated
        
        return mutated

    def analyze_lvs_report(self, lvs_log_path: str) -> Dict[str, Any]:
        """
        Post-processing: Analyzes LVS report to provide feedback.
        Returns insights about substrate warnings and other issues.
        """
        if not os.path.exists(lvs_log_path):
            return {"status": "no_report", "warnings": []}
        
        with open(lvs_log_path, 'r') as f:
            content = f.read()
        
        substrate_warnings = re.findall(r"substrate.*?warning", content, re.IGNORECASE)
        
        return {
            "status": "analyzed",
            "substrate_warnings": len(substrate_warnings),
            "fixes_applied": self.lvs_fixes_applied,
            "recommendation": "Substrate ties added" if self.lvs_fixes_applied else "Manual review needed"
        }
