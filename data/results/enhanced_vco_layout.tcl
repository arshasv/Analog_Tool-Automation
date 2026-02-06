# AI-Optimized VCO Ring Oscillator Layout
drc off
box 0 0 0 0
snap internal

# Substrate contacts
magic::gencell sky130::sky130_fd_pr__nfet_01v8 {w 5.0 l 0.15}
select top cell
box move 0 70um

# === STAGE 0 (Wn=3.50um, Wp=8.75um) ===
magic::gencell sky130::sky130_fd_pr__nfet_01v8 {w 3.5 l 0.18}
select top cell
identify stage0_nmos
box grow n 2um
box move 0 35um
magic::gencell sky130::sky130_fd_pr__pfet_01v8 {w 8.75 l 0.18}
select top cell
identify stage0_pmos
box move 0 5um
paint metal1
box width 1um
box height 3um
label VOUT_0 FreeSans metal1
box move 60um -40um

# === STAGE 1 (Wn=3.68um, Wp=9.19um) ===
magic::gencell sky130::sky130_fd_pr__nfet_01v8 {w 3.6750000000000003 l 0.18}
select top cell
identify stage1_nmos
box grow n 2um
box move 0 35um
magic::gencell sky130::sky130_fd_pr__pfet_01v8 {w 9.1875 l 0.18}
select top cell
identify stage1_pmos
box move 0 5um
paint metal1
box width 1um
box height 3um
label VOUT_1 FreeSans metal1
box move 60um -40um

# === STAGE 2 (Wn=3.85um, Wp=9.62um) ===
magic::gencell sky130::sky130_fd_pr__nfet_01v8 {w 3.8500000000000005 l 0.18}
select top cell
identify stage2_nmos
box grow n 2um
box move 0 35um
magic::gencell sky130::sky130_fd_pr__pfet_01v8 {w 9.625 l 0.18}
select top cell
identify stage2_pmos
box move 0 5um
paint metal1
box width 1um
box height 3um
label VOUT_2 FreeSans metal1
box move 60um -40um

# === STAGE 3 (Wn=3.50um, Wp=8.75um) ===
magic::gencell sky130::sky130_fd_pr__nfet_01v8 {w 3.5 l 0.18}
select top cell
identify stage3_nmos
box grow n 2um
box move 0 35um
magic::gencell sky130::sky130_fd_pr__pfet_01v8 {w 8.75 l 0.18}
select top cell
identify stage3_pmos
box move 0 5um
paint metal1
box width 1um
box height 3um
label VOUT_3 FreeSans metal1
box move 60um -40um

# === STAGE 4 (Wn=3.68um, Wp=9.19um) ===
magic::gencell sky130::sky130_fd_pr__nfet_01v8 {w 3.6750000000000003 l 0.18}
select top cell
identify stage4_nmos
box grow n 2um
box move 0 35um
magic::gencell sky130::sky130_fd_pr__pfet_01v8 {w 9.1875 l 0.18}
select top cell
identify stage4_pmos
box move 0 5um
paint metal1
box width 1um
box height 3um
label VOUT_4 FreeSans metal1
box move 60um -40um

# Ring feedback path
box 0 0 20um 2um
paint metal2
label FEEDBACK FreeSans metal2

# Power Rails
box 0 -35um 300um -32um
paint metal1
label VSS FreeSans metal1
box 0 70um 300um 73um
paint metal1
label VDD FreeSans metal1


select top cell
save enhanced_vco.mag
exit
