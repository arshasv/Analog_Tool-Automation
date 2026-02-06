# AI-Optimized LDO Regulator Layout
drc off
box 0 0 0 0
snap internal

# Pass Transistor (W=1500.0um, L=0.35um)
magic::gencell sky130::sky130_fd_pr__pfet_01v8 {w 1500.0 l 0.35}
select top cell
identify pass_transistor
box grow n 5um

box move 0 60um
# Error Amplifier NMOS
magic::gencell sky130::sky130_fd_pr__nfet_01v8 {w 5.0 l 0.5}
select top cell
identify error_amp_n

box move 0 20um
# Error Amplifier PMOS
magic::gencell sky130::sky130_fd_pr__pfet_01v8 {w 10.0 l 0.5}
select top cell
identify error_amp_p

box move 40um -40um
# Feedback Network (symbolic)
box 0 0 15um 40um
paint metal1
label R_FEEDBACK FreeSans metal1

box move 30um 0um
box 0 0 25.0um 25.0um
paint metal2
label COUT_250pF FreeSans metal2

box -10um -20um 150um -17um
paint metal1
label VIN FreeSans metal1

box -10um -30um 150um -27um
paint metal1
label VOUT FreeSans metal1

box -10um -40um 150um -37um
paint metal1
label GND FreeSans metal1


select top cell
save enhanced_ldo.mag
exit
