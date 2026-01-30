"""
Magic VLSI Layout Automation Wrapper
Handles automated layout generation using Magic Tcl scripting.
"""
import subprocess
import os
from pathlib import Path
from typing import Dict, Any

class MagicLayoutGenerator:
    """Wrapper for Magic VLSI to generate layouts from parameters."""
    
    def __init__(self, magic_bin: str = "magic"):
        self.magic_bin = magic_bin
        self.pdk_path = "/usr/local/share/pdk/sky130A"

    def generate_mos_tcl(self, name: str, width: float, length: float, device_type: str = "nfet_01v8") -> str:
        """Creates a Tcl script for Magic to place a MOSFET."""
        tcl = f"""
# Magic layout generation for {name}
drc off
box 0 0 0 0

# Instantiate the device from the library
magic::gencell sky130::sky130_fd_pr__{device_type} {{w {width} l {length}}}

# Select and save
select top cell
save {name}.mag
exit
"""
        return tcl

    def create_layout(self, cell_name: str, tcl_script: str) -> bool:
        """Executes Magic to generate a .mag file."""
        magicrc_path = f"{self.pdk_path}/libs.tech/magic/sky130A.magicrc"
        
        if os.path.exists(magicrc_path):
            import shutil
            shutil.copy(magicrc_path, ".magicrc")

        try:
            # Run magic in non-graphics mode with stdin pipe
            cmd = [
                self.magic_bin,
                "-dnull",
                "-noconsole"
            ]
            
            # Start process
            proc = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Send script and close stdin
            stdout, stderr = proc.communicate(input=tcl_script, timeout=60)
            
            if os.path.exists(".magicrc"):
                os.remove(".magicrc")

            if proc.returncode == 0:
                if os.path.exists(f"{cell_name}.mag"):
                    print(f"✓ Layout {cell_name}.mag generated successfully.")
                    return True
                else:
                    print(f"⚠️ Magic exited normally but {cell_name}.mag was not found.")
                    print(f"Magic Output (STDOUT):\n{stdout}")
                    print(f"Magic Output (STDERR):\n{stderr}")
                    return False
            else:
                print(f"❌ Magic Layout Generation Failed.")
                print(f"Magic Output (STDOUT):\n{stdout}")
                print(f"Magic Output (STDERR):\n{stderr}")
                return False
        except Exception as e:
            print(f"❌ Error running Magic: {e}")
            return False

    def generate_gds(self, cell_name: str) -> str:
        """Exports a .mag file to GDSII format."""
        gds_file = f"{cell_name}.gds"
        tcl = f"""
load {cell_name}.mag
gds write {gds_file}
exit
"""
        magicrc_path = f"{self.pdk_path}/libs.tech/magic/sky130A.magicrc"
        if os.path.exists(magicrc_path):
            import shutil
            shutil.copy(magicrc_path, ".magicrc")

        proc = subprocess.Popen([self.magic_bin, "-dnull", "-noconsole"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        stdout, stderr = proc.communicate(input=tcl, timeout=60)
        
        if os.path.exists(".magicrc"):
            os.remove(".magicrc")
            
        if os.path.exists(gds_file):
            print(f"✅ GDSII exported successfully to {gds_file}")
            return gds_file
        else:
            print(f"❌ GDSII Export Failed.")
            print(f"Magic Output: {stdout}")
            return ""

if __name__ == "__main__":
    # Test generation
    gen = MagicLayoutGenerator()
    script = gen.generate_mos_tcl("test_nmos", 2.0, 0.15)
    print("Tcl Script Preview:")
    print(script)
