"""
Netgen LVS Automation Wrapper
Handles comparison between Layout-extracted netlists and Schematic netlists.
"""
import subprocess
import os
import re
from typing import Dict, Any

class LVSVerifier:
    """Wrapper for Netgen to perform Layout vs Schematic verification."""
    
    def __init__(self, netgen_bin: str = "netgen"):
        self.netgen_bin = netgen_bin
        self.pdk_setup = "/usr/local/share/pdk/sky130A/libs.tech/netgen/sky130A_setup.tcl"

    def run_lvs(self, layout_netlist: str, schematic_netlist: str, cell_name: str) -> Dict[str, Any]:
        """
        Runs LVS comparison.
        Args:
            layout_netlist: Path to file extracted from layout (.spy or .spice)
            schematic_netlist: Path to source schematic .spice file
            cell_name: Name of the top-level cell to compare
        """
        report_file = f"{cell_name}_lvs.log"
        
        # Netgen batch command
        # "lvs {netlist1 cell} {netlist2 cell} {setup_file} {report_file}"
        lvs_cmd = f"lvs {{ {layout_netlist} {cell_name} }} {{ {schematic_netlist} {cell_name} }} {self.pdk_setup} {report_file} -batch"
        
        try:
            result = subprocess.run(
                [self.netgen_bin, "-batch", "lvs", 
                 f"{layout_netlist} {cell_name}", 
                 f"{schematic_netlist} {cell_name}", 
                 self.pdk_setup, 
                 report_file],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            # Parse report for result
            success = False
            if os.path.exists(report_file):
                with open(report_file, "r") as f:
                    content = f.read()
                    if "Circuits match uniquely" in content:
                        success = True
            
            return {
                "success": success,
                "log": result.stdout,
                "error": result.stderr,
                "report_file": report_file
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}

if __name__ == "__main__":
    v = LVSVerifier()
    print("LVS Wrapper initialized.")
