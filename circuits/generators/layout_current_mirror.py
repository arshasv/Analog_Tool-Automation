"""
Auto-Layout Generator for Current Mirror
Translates optimized parameters into a Magic VLSI layout.
"""
import sys
import os
from tools.layout.magic_wrapper import MagicLayoutGenerator
from tools.verification.physical_verification import PhysicalVerificationFlow

def generate_optimized_layout(cell_name, width, length):
    print(f"🛠️ Generating Layout for {cell_name} (W={width}u, L={length}u)...")
    
    gen = MagicLayoutGenerator()
    # Use the generator's internal setup to copy magicrc
    magicrc_path = "/usr/local/share/pdk/sky130A/libs.tech/magic/sky130A.magicrc"
    if os.path.exists(magicrc_path):
        import shutil
        shutil.copy(magicrc_path, ".magicrc")

    # Create Tcl for a simple current mirror (2 transistors)
    # Create Tcl for a simple current mirror (2 transistors)
    tcl = f"""
# Magic layout for {cell_name}
drc off

# Place M1 (Reference)
magic::gencell sky130::sky130_fd_pr__nfet_01v8 {{w {width} l {length}}}

# Place M2 (Mirror)
# Move the cursor to place next one
box move 10um 0
magic::gencell sky130::sky130_fd_pr__nfet_01v8 {{w {width} l {length}}}

# Flatten the design to avoid subcell issues
select top cell
expand
flatten {cell_name}_flat
load {cell_name}_flat
save {cell_name}.mag
exit
"""
    # Fix the \$ back to $ for Tcl after f-string. Wait, no, f-string with \$ might fail.
    tcl = tcl.replace("\\$", "$")
    
    if gen.create_layout(cell_name, tcl):
        print(f"✨ Layout saved to {cell_name}.mag")
        
        # Create a dummy schematic spice to allow LVS to run (or at least check DRC/Ext)
        schematic_spice = f"{cell_name}_schematic.spice"
        with open(schematic_spice, "w") as f:
            f.write(f"* {cell_name} schematic\n.end\n")

        # Now run verification
        pv = PhysicalVerificationFlow()
        pv.verify_design(cell_name, schematic_spice)

        # Final Step: Export GDSII
        print(f"📦 Exporting GDSII for {cell_name}...")
        gen.generate_gds(cell_name)
    else:
        print("❌ Layout generation failed.")

if __name__ == "__main__":
    # Example using optimized values we found earlier
    generate_optimized_layout("cm_optimized", 19.13, 1.73)
