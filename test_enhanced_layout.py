#!/usr/bin/env python3
"""
Standalone test script for regenerating VCO layout
"""
import sys
import os

# Add project root to path
sys.path.insert(0, '/home/user/Desktop/Adnan/Analog_Tool-Automation')

from circuits.library.custom.smart_vco import SmartVCO
from tools.layout.magic_wrapper import MagicLayoutGenerator
from tools.layout.layout_agent import LayoutIntelligenceAgent
from pathlib import Path

def test_vco_layout():
    print("="*80)
    print("🚀 Testing Enhanced VCO Layout Generation")
    print("="*80)
    
    # Create VCO circuit
    vco = SmartVCO()
    
    # Use sample optimized parameters
    best_params = {
        "w_n": 3.5,
        "l_n": 0.18,
        "w_p": 8.75,
        "num_stages": 5
    }
    
    print("\n📊 Using parameters:")
    for key, val in best_params.items():
        print(f"   • {key}: {val:.4f}")
    
    # Generate layout TCL
    print("\n🎨 Generating layout TCL script...")
    tcl = vco.generate_layout(best_params)
    lines = len(tcl.split('\n'))
    print(f"✅ Generated {lines} lines of Magic TCL")
    
    # Show sample of TCL
    print("\n📝 TCL Preview (first 20 lines):")
    print("-" * 60)
    for i, line in enumerate(tcl.split('\n')[:20], 1):
        print(f"{i:3d}: {line}")
    print("-" * 60)
    
    # Apply layout intelligence
    print("\n🤖 Applying Layout Intelligence Agent...")
    agent = LayoutIntelligenceAgent("smart_vco_test")
    refined_tcl = agent.refine_layout(tcl, max_attempts=1)
    
    refined_lines = len(refined_tcl.split('\n'))
    print(f"✅ Refined to {refined_lines} lines")
    
    # Save to file
    output_dir = Path("/home/user/Desktop/Adnan/Analog_Tool-Automation/data/results")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    tcl_file = output_dir / "vco_layout_test.tcl"
    with open(tcl_file, 'w') as f:
        f.write(refined_tcl)
        f.write("\nsave vco_test.mag\nexit\n")
    
    print(f"\n💾 Layout TCL script saved to: {tcl_file}")
    print(f"   File size: {os.path.getsize(tcl_file)} bytes")
    
    # Generate the actual layout
    print("\n🔨 Generating Magic layout file...")
    gen = MagicLayoutGenerator()
    
    final_tcl = refined_tcl + "\nselect top cell\nsave vco_test.mag\nexit\n"
    
    os.chdir(output_dir)
    if gen.create_layout("vco_test", final_tcl):
        print("✅ Layout generation SUCCESSFUL!")
        if os.path.exists("vco_test.mag"):
            print(f"   vco_test.mag size: {os.path.getsize('vco_test.mag')} bytes")
        
        # Try to generate GDS
        print("\n📦 Generating GDSII...")
        gds = gen.generate_gds("vco_test")
        if gds:
            print(f"✅ GDSII generation SUCCESSFUL!")
            print(f"   {gds} size: {os.path.getsize(gds)} bytes")
    else:
        print("❌ Layout generation failed")
    
    print("\n" + "="*80)
    print("🎉 Test Complete!")
    print("="*80)
    print(f"\nGenerated files in: {output_dir}")
    print("  - vco_layout_test.tcl  (TCL script)")
    print("  - vco_test.mag         (Magic layout)")
    print("  - vco_test.gds         (GDSII file)")

if __name__ == "__main__":
    test_vco_layout()
