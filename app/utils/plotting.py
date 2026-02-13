"""Simple plotting helpers for simulation outputs using matplotlib.

Creates PNG plots for DC (Operating Point), AC (Bode magnitude), and Transient (time response).
"""
from io import BytesIO
import logging
from typing import Dict, Any, List, Sequence
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

logger = logging.getLogger(__name__)

def create_dc_plot(op_results: Dict[str, float]) -> bytes:
    """Create a bar chart for DC operating point results."""
    buf = BytesIO()
    
    if not op_results:
        # Create a placeholder plot indicating no data found
        plt.figure(figsize=(6, 2))
        plt.text(0.5, 0.5, "No DC Operating Point Data Found\n(Check Simulation Logs)", 
                 ha='center', va='center')
        plt.axis('off')
        plt.tight_layout()
        plt.savefig(buf, format='png', dpi=150)
        plt.close()
        buf.seek(0)
        return buf.read()

    # Filter generic items if needed, mostly we have v_node, i_node
    filtered = {k: v for k, v in op_results.items() if k.lower() != 'v_vinp'}
    labels = list(filtered.keys())
    values = list(filtered.values())
    
    # Sort for consistent display
    sorted_pairs = sorted(zip(labels, values), key=lambda x: x[0])
    labels = [x[0] for x in sorted_pairs]
    values = [x[1] for x in sorted_pairs]

    plt.figure(figsize=(8, 4))
    bars = plt.bar(labels, values)
    plt.title('DC Operating Point')
    plt.ylabel('Value (V or A)')
    plt.xticks(rotation=45, ha='right')
    plt.grid(True, axis='y', linestyle='--', alpha=0.5)
    
    # Add value labels
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.2g}',
                ha='center', va='bottom', rotation=90 if len(labels) > 10 else 0)

    plt.tight_layout()
    plt.savefig(buf, format='png', dpi=150)
    plt.close()
    
    buf.seek(0)
    return buf.read()

def create_ac_plot(ac_results: Dict[str, float]) -> bytes:
    """Create synthetic Bode magnitude plot from AC results."""
    buf = BytesIO()
    
    if not ac_results:
        return b""

    gain_db = float(ac_results.get('gain_db', 0.0))
    bw = float(ac_results.get('bandwidth_hz', 1e6))
    
    # If practically no gain, just return empty or simple flat line
    # if gain_db == 0.0 and bw == 0.0:
    #     return b""

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

    buf.seek(0)
    return buf.read()


def create_ac_plot_from_data(freq: Sequence[float], mag_db: Sequence[float]) -> bytes:
    """Create Bode magnitude plot from raw AC sweep data."""
    buf = BytesIO()
    try:
        if not freq or not mag_db:
            return b""
        plt.figure(figsize=(6, 3.5))
        plt.semilogx(freq, mag_db)
        plt.grid(True, which='both', linestyle='--', alpha=0.5)
        plt.title('AC Magnitude')
        plt.xlabel('Frequency (Hz)')
        plt.ylabel('Magnitude (dB)')
        plt.tight_layout()
        plt.savefig(buf, format='png', dpi=150)
        plt.close()
        buf.seek(0)
        return buf.read()
    except Exception as e:
        logger.warning(f"Failed to create AC plot from data: {e}")
        return b""

def create_transient_plot(tran_results: Dict[str, float]) -> bytes:
    """Create synthetic transient step response plot."""
    buf = BytesIO()
    
    if not tran_results:
        return b""

    settling_us = float(tran_results.get('settling_time_us', 1.0))
    overshoot_mv = float(tran_results.get('overshoot_mv', 0.0))

    t = np.linspace(0, max(10.0 * settling_us, 1.0), num=400)
    # Simple step response: 1 - exp(-t/tau) with overshoot
    tau = settling_us / 3.0 if settling_us > 0 else 0.1
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


def create_transient_plot_from_data(time: Sequence[float], value: Sequence[float]) -> bytes:
    """Create transient response plot from raw time-domain waveform."""
    buf = BytesIO()
    try:
        if not time or not value:
            return b""
        plt.figure(figsize=(6, 3.5))
        plt.plot(time, value)
        plt.grid(True, linestyle='--', alpha=0.5)
        plt.title('Transient Response')
        plt.xlabel('Time (s)')
        plt.ylabel('V(vout)')
        plt.tight_layout()
        plt.savefig(buf, format='png', dpi=150)
        plt.close()
        buf.seek(0)
        return buf.read()
    except Exception as e:
        logger.warning(f"Failed to create transient plot from data: {e}")
        return b""
