"""
Physical Verification Flow
Orchestrates Layout Extraction, DRC, and LVS.
"""
import os
import subprocess
from tools.layout.magic_wrapper import MagicLayoutGenerator
from tools.verification.lvs_wrapper import LVSVerifier

class PhysicalVerificationFlow:
    def __init__(self):
        self.magic_bin = "magic"
        self.pdk_path = "/usr/local/share/pdk/sky130A"
        self.lvs_verifier = LVSVerifier()

    def _setup_magicrc(self):
        magicrc_path = f"{self.pdk_path}/libs.tech/magic/sky130A.magicrc"
        if os.path.exists(magicrc_path):
            import shutil
            shutil.copy(magicrc_path, ".magicrc")

    def run_drc(self, cell_name: str) -> bool:
        """Runs Design Rule Check using Magic."""
        self._setup_magicrc()
        tcl = f"""
load {cell_name}.mag
drc check
set drc_count [drc list count total]
puts "DRC_COUNT_RESULT: $drc_count"
exit
"""
        proc = subprocess.Popen([self.magic_bin, "-dnull", "-noconsole"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        stdout, stderr = proc.communicate(input=tcl, timeout=60)
        
        if os.path.exists(".magicrc"):
            os.remove(".magicrc")
            
        print(f"Magic DRC Output: {stdout}")
        if stderr: print(f"Magic DRC Error: {stderr}")

        if "DRC_COUNT_RESULT: 0" in stdout:
            print(f"✅ DRC Clean for {cell_name}")
            return True
        else:
            print(f"❌ DRC Violations found in {cell_name}")
            return False

    def extract_spice(self, cell_name: str) -> str:
        """Extracts SPICE netlist from a Magic layout."""
        self._setup_magicrc()
        output_spice = f"{cell_name}_extracted.spice"
        tcl = f"""
load {cell_name}.mag
extract all
ext2spice lvs
ext2spice -o {output_spice}
exit
"""
        proc = subprocess.Popen([self.magic_bin, "-dnull", "-noconsole"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        stdout, stderr = proc.communicate(input=tcl, timeout=60)
        
        if os.path.exists(".magicrc"):
            os.remove(".magicrc")
            
        print(f"Magic Extraction Output: {stdout}")
        if stderr: print(f"Magic Extraction Error: {stderr}")
            
        return output_spice

    def verify_design(self, cell_name: str, schematic_spice: str):
        """Full Verification: DRC -> Extraction -> LVS"""
        print(f"🚀 Starting Physical Verification for {cell_name}...")
        
        drc_clean = self.run_drc(cell_name)
        
        extracted_spice = self.extract_spice(cell_name)
        print(f"📦 Extracted netlist to {extracted_spice}")
        
        lvs_result = self.lvs_verifier.run_lvs(extracted_spice, schematic_spice, cell_name)
        
        if lvs_result['success']:
            print(f"✅ LVS PASSED! Layout matches Schematic.")
        else:
            print(f"❌ LVS FAILED. Check report: {lvs_result['report_file']}")
            
        return {
            "drc_clean": drc_clean,
            "lvs_passed": lvs_result['success'],
            "extracted_spice": extracted_spice
        }

if __name__ == "__main__":
    # Example usage
    pv = PhysicalVerificationFlow()
    # pv.verify_design("my_opamp", "schematic.spice")
