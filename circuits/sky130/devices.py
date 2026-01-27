"""
Sky130 Device Primitives Library
Provides Python interfaces to Sky130 PDK devices
"""
from dataclasses import dataclass
from typing import Optional, Dict, Any
from enum import Enum


class DeviceType(str, Enum):
    """Sky130 device types"""
    NMOS = "nfet_01v8"
    NMOS_LVT = "nfet_01v8_lvt"
    PMOS = "pfet_01v8"
    PMOS_HVT = "pfet_01v8_hvt"
    NMOS_HV = "nfet_g5v0d10v5"
    PMOS_HV = "pfet_g5v0d10v5"
    RES_HIGH_PO = "res_high_po"
    RES_GENERIC_PO = "res_generic_po"
    CAP_MIM = "cap_mim_m3_1"
    CAP_MIM_M4 = "cap_mim_m3_2"


@dataclass
class Sky130Device:
    """Base class for Sky130 devices"""
    name: str
    device_type: DeviceType
    model: str
    parameters: Dict[str, Any]
    
    def to_spice(self, node_plus: str, node_minus: str, **kwargs) -> str:
        """Generate SPICE netlist line - to be overridden"""
        raise NotImplementedError


@dataclass
class Sky130MOSFET(Sky130Device):
    """Sky130 MOSFET device"""
    width: float  # in micrometers
    length: float  # in micrometers
    nf: int = 1  # number of fingers
    mult: int = 1  # multiplier
    
    def __post_init__(self):
        """Set model based on device type"""
        self.model = self.device_type.value
        self.parameters = {
            "w": self.width,
            "l": self.length,
            "nf": self.nf,
            "mult": self.mult,
        }
    
    def to_spice(self, drain: str, gate: str, source: str, body: str) -> str:
        """Generate SPICE netlist for MOSFET"""
        params = " ".join([f"{k}={v}" for k, v in self.parameters.items()])
        return f"M{self.name} {drain} {gate} {source} {body} {self.model} {params}"
    
    def area(self) -> float:
        """Calculate total device area in um²"""
        return self.width * self.length * self.nf * self.mult
    
    def gm_id_estimate(self, vgs: float, vds: float, vth: float = 0.4) -> float:
        """Rough gm/ID estimation (simplified model)"""
        if vgs < vth:
            return 0.0
        # Simplified strong inversion approximation
        return 2 / (vgs - vth)


@dataclass
class Sky130Resistor(Sky130Device):
    """Sky130 Resistor device"""
    resistance: float  # in ohms
    width: float = 1.0  # in micrometers
    length: Optional[float] = None
    
    def __post_init__(self):
        """Calculate dimensions based on resistance"""
        # Sky130 high-po resistor: ~350 ohm/square
        sheet_resistance = 350.0
        
        if self.device_type == DeviceType.RES_GENERIC_PO:
            sheet_resistance = 48.2
        
        if self.length is None:
            # Calculate length for given width
            num_squares = self.resistance / sheet_resistance
            self.length = num_squares * self.width
        
        self.model = self.device_type.value
        self.parameters = {
            "r": self.resistance,
            "w": self.width,
            "l": self.length,
        }
    
    def to_spice(self, node_plus: str, node_minus: str) -> str:
        """Generate SPICE netlist for resistor"""
        return f"R{self.name} {node_plus} {node_minus} {self.resistance}"
    
    def area(self) -> float:
        """Calculate resistor area in um²"""
        return self.width * self.length


@dataclass
class Sky130Capacitor(Sky130Device):
    """Sky130 MIM Capacitor device"""
    capacitance: float  # in farads
    width: Optional[float] = None
    length: Optional[float] = None
    
    def __post_init__(self):
        """Calculate dimensions based on capacitance"""
        # Sky130 MIM cap: ~2 fF/um²
        cap_density = 2e-15  # F/um²
        
        if self.device_type == DeviceType.CAP_MIM_M4:
            cap_density = 2e-15  # Same for M3_2
        
        area = self.capacitance / cap_density
        
        if self.width is None and self.length is None:
            # Square capacitor
            self.width = self.length = area ** 0.5
        elif self.width is not None and self.length is None:
            self.length = area / self.width
        
        self.model = self.device_type.value
        self.parameters = {
            "c": self.capacitance,
            "w": self.width,
            "l": self.length,
        }
    
    def to_spice(self, node_plus: str, node_minus: str) -> str:
        """Generate SPICE netlist for capacitor"""
        # Convert to more readable units
        if self.capacitance >= 1e-6:
            cap_str = f"{self.capacitance*1e6}u"
        elif self.capacitance >= 1e-9:
            cap_str = f"{self.capacitance*1e9}n"
        elif self.capacitance >= 1e-12:
            cap_str = f"{self.capacitance*1e12}p"
        else:
            cap_str = f"{self.capacitance*1e15}f"
        
        return f"C{self.name} {node_plus} {node_minus} {cap_str}"
    
    def area(self) -> float:
        """Calculate capacitor area in um²"""
        return self.width * self.length


# ============================================================================
# Device Factory Functions
# ============================================================================

def nmos(name: str, width: float, length: float, nf: int = 1, mult: int = 1) -> Sky130MOSFET:
    """Create Sky130 NMOS transistor"""
    return Sky130MOSFET(
        name=name,
        device_type=DeviceType.NMOS,
        model=DeviceType.NMOS.value,
        parameters={},
        width=width,
        length=length,
        nf=nf,
        mult=mult
    )


def pmos(name: str, width: float, length: float, nf: int = 1, mult: int = 1) -> Sky130MOSFET:
    """Create Sky130 PMOS transistor"""
    return Sky130MOSFET(
        name=name,
        device_type=DeviceType.PMOS,
        model=DeviceType.PMOS.value,
        parameters={},
        width=width,
        length=length,
        nf=nf,
        mult=mult
    )


def resistor(name: str, resistance: float, width: float = 1.0) -> Sky130Resistor:
    """Create Sky130 high-poly resistor"""
    return Sky130Resistor(
        name=name,
        device_type=DeviceType.RES_HIGH_PO,
        model=DeviceType.RES_HIGH_PO.value,
        parameters={},
        resistance=resistance,
        width=width
    )


def capacitor(name: str, capacitance: float) -> Sky130Capacitor:
    """Create Sky130 MIM capacitor"""
    return Sky130Capacitor(
        name=name,
        device_type=DeviceType.CAP_MIM,
        model=DeviceType.CAP_MIM.value,
        parameters={},
        capacitance=capacitance
    )


# ============================================================================
# Constants
# ============================================================================

class Sky130Constants:
    """Sky130 PDK constants and design rules"""
    
    # Technology node
    TECHNOLOGY_NODE = 130  # nm
    
    # Minimum dimensions (um)
    MIN_NMOS_L = 0.15
    MIN_PMOS_L = 0.15
    MIN_NMOS_W = 0.42
    MIN_PMOS_W = 0.42
    
    # Typical threshold voltages (V)
    VTH_NMOS = 0.4
    VTH_PMOS = -0.4
    
    # Supply voltages
    VDD_NOMINAL = 1.8
    VDD_HV = 5.0
    
    # Process parameters
    TOX = 4.1e-9  # Gate oxide thickness (m)
    UO_N = 420  # Electron mobility (cm²/V·s)
    UO_P = 120  # Hole mobility (cm²/V·s)
    
    # Temperature
    TEMP_NOMINAL = 25  # Celsius
    
    # Corners
    CORNERS = ["tt", "ff", "ss", "fs", "sf"]
