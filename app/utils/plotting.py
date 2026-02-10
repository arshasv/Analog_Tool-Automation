"""Simple plotting helpers for simulation outputs using matplotlib.

Creates PNG plots for AC (Bode magnitude) or Transient (time response) based
on the parsed simulation outputs. If detailed arrays are unavailable, it
generates synthetic curves using the reported metrics (gain, bandwidth,
settling_time) so users get a visual summary in the ZIP download.
"""
from io import BytesIO
import math
from typing import Dict, Any
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np


def plot_simulation_output_png(simulation_output: Dict[str, Any]) -> bytes:
    """Return PNG bytes for given simulation_output dict.

    Prefers AC data if available, otherwise transient summary.
    """
    ac = simulation_output.get('ac_analysis', {}) or {}
    tran = simulation_output.get('transient_analysis', {}) or {}

    buf = BytesIO()

    if ac and ('gain_db' in ac or 'bandwidth_hz' in ac):
        # Create synthetic Bode magnitude plot
        gain_db = float(ac.get('gain_db', 40.0))
        bw = float(ac.get('bandwidth_hz', 1e6))

        f = np.logspace(1, 8, num=400)  # 10 Hz to 100 MHz
        # First-order roll-off around bandwidth: magnitude (linear)
        mag_lin = 10 ** (gain_db / 20.0) / np.sqrt(1.0 + (f / bw) ** 2)
        mag_db = 20.0 * np.log10(mag_lin + 1e-20)

        plt.figure(figsize=(6, 3.5))
        plt.semilogx(f, mag_db)
        plt.grid(True, which='both', linestyle='--', alpha=0.5)
        plt.title('AC Magnitude (approx)')
        plt.xlabel('Frequency (Hz)')
        plt.ylabel('Magnitude (dB)')
        plt.tight_layout()
        plt.savefig(buf, format='png', dpi=150)
        plt.close()

    else:
        # Fallback: transient-style synthetic response
        settling_us = float(tran.get('settling_time_us', 1.0))
        overshoot_mv = float(tran.get('overshoot_mv', 50.0))

        t = np.linspace(0, max(10.0 * settling_us, 10.0), num=400)
        # Simple step response: 1 - exp(-t/tau) with overshoot
        tau = settling_us / 3.0 if settling_us > 0 else 0.3
        step = 1.0 - np.exp(-t / (tau + 1e-9))
        # Add overshoot as a brief peak
        peak = overshoot_mv / 1000.0
        step = step + peak * np.exp(-((t - tau) ** 2) / (0.5 * tau ** 2))

        plt.figure(figsize=(6, 3.5))
        plt.plot(t, step)
        plt.grid(True, linestyle='--', alpha=0.5)
        plt.title('Transient Step Response (approx)')
        plt.xlabel('Time (us)')
        plt.ylabel('Normalized Output')
        plt.tight_layout()
        plt.savefig(buf, format='png', dpi=150)
        plt.close()

    buf.seek(0)
    return buf.read()
