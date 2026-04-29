# Optimization Parameters & Circuit Reference

This document provides the standard optimization targets and initial values for the built-in circuit templates. Use these as a baseline for your optimization workflows.

## Current Mirrors

### Standard Current Mirror (`current_mirror.py`)
- **Free Variables**: `width`, `length`
- **Initial Values**: `width=2.0`, `length=0.5`
- **Recommended Targets**:
  - `target_current`: `100u` (Reference dependent)
  - `target_gain`: `-0.1` (Unity current gain)

### PMOS Current Mirror (`pmos_current_mirror.py`)
- **Free Variables**: `width`, `length`
- **Initial Values**: `width=5.0`, `length=1.0`
- **Recommended Targets**:
  - `target_current`: `50u`

### Wilson Current Mirror (`wilson_current_mirror.py`)
- **Free Variables**: `width`, `length` (matched across M1-M3)
- **Initial Values**: `width=3.0`, `length=0.5`
- **Recommended Targets**:
  - `target_current`: `100u`

---

## Amplifiers

### Common Source (`common_source.py`)
- **Free Variables**: `w_n`, `l_n`, `r_load`
- **Initial Values**: `w_n=10.0`, `l_n=0.18`, `r_load=5k`
- **Recommended Targets**:
  - `target_gain`: `20` (dB)
  - `target_current`: `500u`

### Common Gate (`common_gate.py`)
- **Free Variables**: `w_n`, `l_n`
- **Initial Values**: `w_n=5.0`, `l_n=0.5`
- **Recommended Targets**:
  - `target_gain`: `15` (dB)

### Two-Stage Op-Amp (`two_stage_opamp.py`)
- **Free Variables**: `w_diff`, `w_load`, `w_out`, `cc`, `i_tail`
- **Initial Values**: `w_diff=5.0`, `w_load=10.0`, `w_out=20.0`, `cc=1.0`, `i_tail=50.0`
- **Recommended Targets**:
  - `target_gain`: `60` (dB)
  - `target_current`: `100u` (output stage bias)

### Folded Cascode OTA (`folded_cascode_ota.py`)
- **Free Variables**: `w_in`, `w_casc`, `l_in`, `l_casc`
- **Initial Values**: `w_in=20.0`, `w_casc=10.0`
- **Recommended Targets**:
  - `target_gain`: `50` (dB)

---

## Logic & Mixed Signal

### Inverter (`inverter.py`)
- **Free Variables**: `wn`, `wp`
- **Initial Values**: `wn=1.0`, `wp=2.0`
- **Recommended Targets**:
  - `target_current`: `Switching threshold balance`

### Ring Oscillator (`ring_oscillator.py`)
- **Free Variables**: `wn`, `wp`, `stages`
- **Recommended Targets**:
  - `target_current`: `Freq optimization`

### Bandgap Reference (`bandgap_reference.py`)
- **Free Variables**: `r1`, `r2`, `n_ratio`
- **Recommended Targets**:
  - `target_current`: `Temp-independent voltage`

---

## Optimization Engine Settings
- **Global Epochs**: Default `100` (Use `200` for complex circuits like Op-Amps)
- **Coarse Search**: 30% of Epochs (Random sampling phase)
- **Local Search**: Nelder-Mead simplex refinement
