"""Plotting helpers for simulation outputs using matplotlib."""
from io import BytesIO
import logging
from typing import Dict, Sequence
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

logger = logging.getLogger(__name__)


def create_missing_data_plot(title: str, detail: str) -> bytes:
    """Create a non-deceptive placeholder plot when simulation waveform data is unavailable."""
    buf = BytesIO()
    plt.figure(figsize=(6.5, 2.8))
    plt.text(0.5, 0.58, title, ha='center', va='center', fontsize=11, fontweight='bold')
    plt.text(0.5, 0.35, detail, ha='center', va='center', fontsize=9)
    plt.axis('off')
    plt.tight_layout()
    plt.savefig(buf, format='png', dpi=150)
    plt.close()
    buf.seek(0)
    return buf.read()

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
    """Legacy entrypoint retained for compatibility; does not generate synthetic waveforms."""
    if ac_results:
        logger.warning("create_ac_plot called without AC sweep waveform; skipping synthetic fallback.")
    return b""


def create_ac_plot_from_data(freq: Sequence[float], mag_db: Sequence[float]) -> bytes:
    """Create Bode magnitude plot from raw AC sweep data."""
    buf = BytesIO()
    try:
        if not freq or not mag_db:
            return b""
        plt.figure(figsize=(6, 3.5))
        plt.semilogx(freq, mag_db, linewidth=1.5, color='blue')
        plt.grid(True, which='both', linestyle='--', alpha=0.5)
        plt.title('AC Magnitude (Simulated)')
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


def create_ac_bode_plot_from_complex(freq: Sequence[float], response: Sequence[complex]) -> bytes:
    """Create Bode magnitude + phase from complex AC response."""
    buf = BytesIO()
    try:
        if not freq or not response:
            return b""
        if len(freq) != len(response):
            logger.warning("AC plot data length mismatch: freq=%d response=%d", len(freq), len(response))
            return b""

        freq_arr = np.asarray(freq, dtype=float)
        resp_arr = np.asarray(response, dtype=complex)
        valid = np.isfinite(freq_arr) & np.isfinite(resp_arr.real) & np.isfinite(resp_arr.imag) & (freq_arr > 0.0)
        if not np.any(valid):
            return b""

        freq_arr = freq_arr[valid]
        resp_arr = resp_arr[valid]
        mag_db = 20.0 * np.log10(np.maximum(np.abs(resp_arr), 1e-30))
        phase_deg = np.unwrap(np.angle(resp_arr)) * 180.0 / np.pi

        fig, axes = plt.subplots(2, 1, figsize=(7, 5.2), sharex=True)
        axes[0].semilogx(freq_arr, mag_db, linewidth=1.4, color='blue')
        axes[0].set_ylabel('Magnitude (dB)')
        axes[0].set_title('AC Bode Plot (Simulated)')
        axes[0].grid(True, which='both', linestyle='--', alpha=0.5)

        axes[1].semilogx(freq_arr, phase_deg, linewidth=1.4, color='darkorange')
        axes[1].set_xlabel('Frequency (Hz)')
        axes[1].set_ylabel('Phase (deg)')
        axes[1].grid(True, which='both', linestyle='--', alpha=0.5)

        fig.tight_layout()
        fig.savefig(buf, format='png', dpi=150)
        plt.close(fig)
        buf.seek(0)
        return buf.read()
    except Exception as e:
        logger.warning(f"Failed to create AC bode plot from complex data: {e}")
        return b""

def create_transient_plot(tran_results: Dict[str, float]) -> bytes:
    """Legacy entrypoint retained for compatibility; does not generate synthetic waveforms."""
    if tran_results:
        logger.warning("create_transient_plot called without transient waveform; skipping synthetic fallback.")
    return b""


def create_transient_plot_from_data(time: Sequence[float], value: Sequence[float]) -> bytes:
    """Create transient response plot from raw time-domain waveform."""
    buf = BytesIO()
    try:
        if not time or not value:
            return b""
        plt.figure(figsize=(6, 3.5))
        plt.plot(time, value, linewidth=1.5, color='blue')
        plt.grid(True, linestyle='--', alpha=0.5)
        plt.title('Transient Response (Simulated)')
        plt.xlabel('Time (s)')
        plt.ylabel('Signal Value')
        plt.tight_layout()
        plt.savefig(buf, format='png', dpi=150)
        plt.close()
        buf.seek(0)
        return buf.read()
    except Exception as e:
        logger.warning(f"Failed to create transient plot from data: {e}")
        return b""

def create_dc_sweep_plot(x: Sequence[float], y: Sequence[float], x_label: str = "Input", y_label: str = "Output") -> bytes:
    """Create a plot for DC sweep data (e.g. I-V or V-V curves)."""
    buf = BytesIO()
    try:
        if not x or not y:
            return b""
        plt.figure(figsize=(6, 3.5))
        plt.plot(x, y, linewidth=1.5, color='green')
        plt.grid(True, linestyle='--', alpha=0.5)
        plt.title('DC Sweep Analysis (Simulated)')
        plt.xlabel(x_label)
        plt.ylabel(y_label)
        plt.tight_layout()
        plt.savefig(buf, format='png', dpi=150)
        plt.close()
        buf.seek(0)
        return buf.read()
    except Exception as e:
        logger.warning(f"Failed to create DC sweep plot: {e}")
        return b""
