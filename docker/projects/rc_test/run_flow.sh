#!/bin/bash
set -e

echo "▶ PySpice → SPICE"
python3 rc_pyspice.py

echo "▶ ngspice (batch)"
ngspice -b rc_auto.spice

echo "▶ CSV → Plot"
python3 plot_csv.py

echo "✅ Flow completed successfully"

