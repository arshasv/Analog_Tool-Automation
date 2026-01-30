import os
import glob
import subprocess
import sys
from pathlib import Path

def run_automation():
    custom_dir = Path("/home/eda/circuits/library/custom")
    
    # 1. Find all Python files except the runner itself
    py_files = [f for f in glob.glob(str(custom_dir / "*.py")) if "runner.py" not in f]
    
    if not py_files:
        print("❌ No circuit files found in circuits/library/custom/")
        print("Please add a .py circuit file to start the automation.")
        return

    # 2. Get the latest file by modification time
    latest_file = max(py_files, key=os.path.getmtime)
    print(f"🚀 Detected latest design: {os.path.basename(latest_file)}")
    print("━" * 60)

    # 3. Run the Python generator
    print(f"🛠️ Generating netlist...")
    result = subprocess.run(["python3", latest_file], capture_output=True, text=True)
    print(result.stdout)
    
    if result.returncode != 0:
        print(f"❌ Error generating netlist:\n{result.stderr}")
        return

    # 4. Find the generated .spice file
    # Most scripts print "Generated <filename>.spice"
    spice_files = glob.glob(str(custom_dir / "*.spice"))
    if not spice_files:
        # Check current directory just in case
        spice_files = glob.glob("*.spice")
        
    if not spice_files:
         print("❌ No .spice file was generated.")
         return
         
    # Pick the newest spice file
    latest_spice = max(spice_files, key=os.path.getmtime)
    print(f"⚡ Running simulation for: {os.path.basename(latest_spice)}")
    print("━" * 60)

    # 5. Run Ngspice
    # Using -b for batch mode
    sim_result = subprocess.run(["ngspice", "-b", latest_spice], capture_output=True, text=True)
    
    # 6. Final Output
    print(sim_result.stdout)
    
    if sim_result.returncode == 0:
        print("✅ Automation Completed Successfully!")
    else:
        print(f"❌ Simulation Failed:\n{sim_result.stderr}")

if __name__ == "__main__":
    run_automation()
