"""
Architecture Synthesizer — Modular netlist assembly from topology roles.

Assembles a complete SPICE netlist string by combining modular blocks:
  - Input stage
  - Gain stage
  - Active load
  - Bias network
  - Output stage
  - Compensation
"""
import os
from typing import Dict, Any
from app.services.topology import Topology

import os
from typing import Dict, Any
from app.services.topology import Topology
from app.circuits.primitives import nmos, pmos, capacitor
from app.circuits.bricks import diff_pair_nmos, diff_pair_pmos, current_mirror_simple, cascode_stage
from app.circuits.macros import opamp_two_stage, opamp_folded

class ArchitectureSynthesizer:
    
    @staticmethod
    def generate_netlist_string(topology: Topology, parameters: Dict[str, Any]) -> str:
        """Assembles a full SPICE netlist using modular building blocks."""
        pdk = os.environ.get("SKY130_PDK", "/opt/sky130_pdk/sky130A")
        lib_path = f"{pdk}/libs.tech/ngspice/sky130.lib.spice"
        
        netlist = [f"* Topology Search Node: {topology.key}", f'.lib "{lib_path}" tt', ""]
        
        # 1. Global Parameters (already handled by Orchestrator's .param injection, 
        # but we use placeholders here that Orchestrator will fill)
        netlist.append("* Power and Stimulus")
        netlist.append("Vdd vdd 0 {vdd}")
        netlist.append("Vcm vcm 0 0.9")
        netlist.append("Vinp vinp vcm AC 1")
        netlist.append("Vinn vinn vcm DC 0")
        netlist.append("")
        
        # 2. Input Stage Selection
        if topology.input == "diff_n":
            block = diff_pair_nmos.generate_netlist(parameters)
            netlist.append(block.format(d1="d1", d2="d2", in1="vinp", in2="vinn", tail="tail", sub="0"))
        elif topology.input == "diff_p":
            block = diff_pair_pmos.generate_netlist(parameters)
            netlist.append(block.format(d1="d1", d2="d2", in1="vinp", in2="vinn", tail="tail", sub="vdd"))
            
        # 3. Gain & Load Integration
        if topology.gain == "two_stage":
            # In architecture search, we might instantiate a macro directly if it matches the gain role
            # For synthesis from pieces:
            # Load for stage 1
            l_block = current_mirror_simple.generate_netlist(parameters)
            fmt_map = {"in": "d1", "out": "d2", "gnd": "vdd" if topology.input=="diff_n" else "0"}
            netlist.append(l_block.format(**fmt_map))
            
            # Stage 2
            netlist.append("* Second Stage")
            if topology.input == "diff_n":
                m2n = nmos.generate_netlist({"w": parameters.get("w_out", 20.0), "l": 0.5})
                netlist.append(m2n.format(d="vout", g="d2", s="0", b="0"))
                m2p = pmos.generate_netlist({"w": parameters.get("w_out", 20.0), "l": 0.5})
                netlist.append(m2p.format(d="vout", g="p_bias", s="vdd", b="vdd"))
            
        elif topology.gain == "folded":
            # Assemble folded cascode from bricks/primitives
            netlist.append("* Folded Cascode Assembly")
            # This is complex, but we have a macro for it or we can build it here
            pass
            
        # 4. Compensation
        if topology.comp == "miller":
            c_block = capacitor.generate_netlist({"c": parameters.get("cc", 1e-12)})
            netlist.append(c_block.format(n1="d2", n2="vout"))
            
        netlist.append("\n.end")
        return "\n".join(netlist)
