# 02 Research

## Purpose
This document captures the product and UX research baseline for xEDA. It defines who the platform is for, what problems it solves, and which workflows the interface should optimize.

## Product Context
xEDA is an analog circuit design automation platform that combines:
- Circuit simulation with NGSpice
- Parameter synthesis and optimization
- Circuit template inspection and reuse
- A dashboard-style frontend for monitoring jobs and results

## Primary Users
- Analog IC designers exploring topologies and transistor sizing
- Researchers comparing circuit behaviors across analyses
- Students or lab users learning analog blocks through simulation

## Key User Goals
- Submit a circuit quickly and see if it works
- Understand the current status of a simulation or optimization job
- Tune parameters with enough feedback to make informed design decisions
- Inspect outputs without switching tools

## Core Workflows
1. Choose or upload a circuit template
2. Inspect or edit parameters
3. Run simulation or optimization
4. Monitor status and progress
5. Review metrics, plots, and generated artifacts

## UX Implications
- The interface should prioritize clarity over density on first load
- Status, progress, and results should remain visible at all times
- Parameter editing should reduce ambiguity through labels, defaults, and validation
- Complex results should be summarized first, with raw data available on demand

## Research Constraints
- Engineering users need high information density, but not at the cost of legibility
- The system must support technical language without over-simplifying circuit concepts
- The UI should reflect the precision and seriousness of analog design tools
