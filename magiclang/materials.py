"""Material catalogue and periodic-table reference data for the MANA world engine.

Densities are kg/m³ near room temperature and ordinary pressure when known.
Several radioactive/superheavy-element densities are approximate simulation
estimates, not experimental measurements. Missing transition temperatures mean
that MANA does not attempt an automatic phase transition for that entry.
"""
from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
import copy
import re
from typing import Any


@dataclass(frozen=True, slots=True)
class ElementRecord:
    atomic_number: int
    symbol: str
    name: str
    density_kg_m3: float | None
    standard_state: str
    category: str
    estimated_density: bool = False
    atomic_mass_u: float | None = None
    estimated_atomic_mass: bool = False
    melting_point_k: float | None = None
    boiling_point_k: float | None = None

    def as_dict(self) -> dict[str, Any]:
        return {
            "atomic_number": self.atomic_number,
            "symbol": self.symbol,
            "name": self.name,
            "density_kg_m3": self.density_kg_m3,
            "standard_state": self.standard_state,
            "category": self.category,
            "estimated_density": self.estimated_density,
            "atomic_mass_u": self.atomic_mass_u,
            "estimated_atomic_mass": self.estimated_atomic_mass,
            "melting_point_k": self.melting_point_k,
            "boiling_point_k": self.boiling_point_k,
            "reference_temperature_k": 293.15,
            "reference_pressure_pa": 101325.0,
        }


# Z is assigned by row order. Density data intentionally has only the precision
# needed for plausible world simulation; real alloys and material conditions vary.
_RAW_ELEMENTS = r"""
H|Hydrogen|0.0899|gas|nonmetal
He|Helium|0.1785|gas|noble gas
Li|Lithium|534|solid|alkali metal
Be|Beryllium|1850|solid|alkaline earth metal
B|Boron|2340|solid|metalloid
C|Carbon|2267|solid|nonmetal
N|Nitrogen|1.2506|gas|nonmetal
O|Oxygen|1.429|gas|nonmetal
F|Fluorine|1.696|gas|halogen
Ne|Neon|0.9002|gas|noble gas
Na|Sodium|968|solid|alkali metal
Mg|Magnesium|1738|solid|alkaline earth metal
Al|Aluminum|2700|solid|post-transition metal
Si|Silicon|2329|solid|metalloid
P|Phosphorus|1823|solid|nonmetal
S|Sulfur|2070|solid|nonmetal
Cl|Chlorine|3.214|gas|halogen
Ar|Argon|1.784|gas|noble gas
K|Potassium|862|solid|alkali metal
Ca|Calcium|1550|solid|alkaline earth metal
Sc|Scandium|2985|solid|transition metal
Ti|Titanium|4507|solid|transition metal
V|Vanadium|6110|solid|transition metal
Cr|Chromium|7190|solid|transition metal
Mn|Manganese|7440|solid|transition metal
Fe|Iron|7874|solid|transition metal
Co|Cobalt|8860|solid|transition metal
Ni|Nickel|8908|solid|transition metal
Cu|Copper|8960|solid|transition metal
Zn|Zinc|7140|solid|transition metal
Ga|Gallium|5907|solid|post-transition metal
Ge|Germanium|5323|solid|metalloid
As|Arsenic|5727|solid|metalloid
Se|Selenium|4810|solid|nonmetal
Br|Bromine|3120|liquid|halogen
Kr|Krypton|3.75|gas|noble gas
Rb|Rubidium|1532|solid|alkali metal
Sr|Strontium|2630|solid|alkaline earth metal
Y|Yttrium|4472|solid|transition metal
Zr|Zirconium|6511|solid|transition metal
Nb|Niobium|8570|solid|transition metal
Mo|Molybdenum|10280|solid|transition metal
Tc|Technetium|11500|solid|transition metal
Ru|Ruthenium|12370|solid|transition metal
Rh|Rhodium|12410|solid|transition metal
Pd|Palladium|12023|solid|transition metal
Ag|Silver|10490|solid|transition metal
Cd|Cadmium|8650|solid|transition metal
In|Indium|7310|solid|post-transition metal
Sn|Tin|7310|solid|post-transition metal
Sb|Antimony|6697|solid|metalloid
Te|Tellurium|6240|solid|metalloid
I|Iodine|4930|solid|halogen
Xe|Xenon|5.894|gas|noble gas
Cs|Cesium|1873|solid|alkali metal
Ba|Barium|3620|solid|alkaline earth metal
La|Lanthanum|6145|solid|lanthanoid
Ce|Cerium|6770|solid|lanthanoid
Pr|Praseodymium|6773|solid|lanthanoid
Nd|Neodymium|7007|solid|lanthanoid
Pm|Promethium|7260|solid|lanthanoid
Sm|Samarium|7520|solid|lanthanoid
Eu|Europium|5240|solid|lanthanoid
Gd|Gadolinium|7900|solid|lanthanoid
Tb|Terbium|8230|solid|lanthanoid
Dy|Dysprosium|8550|solid|lanthanoid
Ho|Holmium|8790|solid|lanthanoid
Er|Erbium|9066|solid|lanthanoid
Tm|Thulium|9320|solid|lanthanoid
Yb|Ytterbium|6965|solid|lanthanoid
Lu|Lutetium|9840|solid|lanthanoid
Hf|Hafnium|13310|solid|transition metal
Ta|Tantalum|16650|solid|transition metal
W|Tungsten|19250|solid|transition metal
Re|Rhenium|21020|solid|transition metal
Os|Osmium|22590|solid|transition metal
Ir|Iridium|22650|solid|transition metal
Pt|Platinum|21450|solid|transition metal
Au|Gold|19300|solid|transition metal
Hg|Mercury|13534|liquid|transition metal
Tl|Thallium|11850|solid|post-transition metal
Pb|Lead|11340|solid|post-transition metal
Bi|Bismuth|9780|solid|post-transition metal
Po|Polonium|9196|solid|post-transition metal
At|Astatine|7000|solid|halogen|estimated
Rn|Radon|9.73|gas|noble gas
Fr|Francium|1870|solid|alkali metal|estimated
Ra|Radium|5500|solid|alkaline earth metal
Ac|Actinium|10070|solid|actinoid
Th|Thorium|11724|solid|actinoid
Pa|Protactinium|15370|solid|actinoid
U|Uranium|19050|solid|actinoid
Np|Neptunium|20450|solid|actinoid
Pu|Plutonium|19816|solid|actinoid
Am|Americium|13670|solid|actinoid
Cm|Curium|13510|solid|actinoid
Bk|Berkelium|14780|solid|actinoid
Cf|Californium|15100|solid|actinoid
Es|Einsteinium|8840|solid|actinoid|estimated
Fm|Fermium|9700|solid|actinoid|estimated
Md|Mendelevium|10000|solid|actinoid|estimated
No|Nobelium|9900|solid|actinoid|estimated
Lr|Lawrencium|15000|solid|actinoid|estimated
Rf|Rutherfordium|23000|solid|transition metal|estimated
Db|Dubnium|29000|solid|transition metal|estimated
Sg|Seaborgium|35000|solid|transition metal|estimated
Bh|Bohrium|37000|solid|transition metal|estimated
Hs|Hassium|41000|solid|transition metal|estimated
Mt|Meitnerium|37000|solid|transition metal|estimated
Ds|Darmstadtium|34000|solid|transition metal|estimated
Rg|Roentgenium|28000|solid|transition metal|estimated
Cn|Copernicium|14000|liquid|transition metal|estimated
Nh|Nihonium|16000|solid|post-transition metal|estimated
Fl|Flerovium|14000|solid|post-transition metal|estimated
Mc|Moscovium|13000|solid|post-transition metal|estimated
Lv|Livermorium|12000|solid|post-transition metal|estimated
Ts|Tennessine|7000|solid|halogen|estimated
Og|Oganesson|7000|gas|noble gas|estimated
"""

# Standard atomic weights in unified atomic mass units (u). For elements without
# a standard atomic weight, a representative long-lived isotope mass number is
# used and flagged as an estimate. Sources: NIST SP 966 / NIST atomic weights
# and isotopic compositions; these values support approximate alloy bookkeeping,
# not isotope-resolved chemistry.
_ATOMIC_MASSES_U = {
    "H": 1.008, "He": 4.002602, "Li": 6.94, "Be": 9.0121831, "B": 10.81,
    "C": 12.011, "N": 14.007, "O": 15.999, "F": 18.998403, "Ne": 20.1797,
    "Na": 22.989769, "Mg": 24.305, "Al": 26.9815385, "Si": 28.085, "P": 30.973762,
    "S": 32.06, "Cl": 35.45, "Ar": 39.948, "K": 39.0983, "Ca": 40.078,
    "Sc": 44.955908, "Ti": 47.867, "V": 50.9415, "Cr": 51.9961, "Mn": 54.938044,
    "Fe": 55.845, "Co": 58.933194, "Ni": 58.6934, "Cu": 63.546, "Zn": 65.38,
    "Ga": 69.723, "Ge": 72.630, "As": 74.921595, "Se": 78.971, "Br": 79.904,
    "Kr": 83.798, "Rb": 85.4678, "Sr": 87.62, "Y": 88.90584, "Zr": 91.224,
    "Nb": 92.90637, "Mo": 95.95, "Tc": 98.0, "Ru": 101.07, "Rh": 102.9055,
    "Pd": 106.42, "Ag": 107.8682, "Cd": 112.414, "In": 114.818, "Sn": 118.710,
    "Sb": 121.760, "Te": 127.60, "I": 126.90447, "Xe": 131.293, "Cs": 132.90545196,
    "Ba": 137.327, "La": 138.90547, "Ce": 140.116, "Pr": 140.90766, "Nd": 144.242,
    "Pm": 145.0, "Sm": 150.36, "Eu": 151.964, "Gd": 157.25, "Tb": 158.92535,
    "Dy": 162.500, "Ho": 164.93033, "Er": 167.259, "Tm": 168.93422, "Yb": 173.045,
    "Lu": 174.9668, "Hf": 178.49, "Ta": 180.94788, "W": 183.84, "Re": 186.207,
    "Os": 190.23, "Ir": 192.217, "Pt": 195.084, "Au": 196.966569, "Hg": 200.592,
    "Tl": 204.38, "Pb": 207.2, "Bi": 208.98040, "Po": 209.0, "At": 210.0,
    "Rn": 222.0, "Fr": 223.0, "Ra": 226.0, "Ac": 227.0, "Th": 232.0377,
    "Pa": 231.03588, "U": 238.02891, "Np": 237.0, "Pu": 244.0, "Am": 243.0,
    "Cm": 247.0, "Bk": 247.0, "Cf": 251.0, "Es": 252.0, "Fm": 257.0,
    "Md": 258.0, "No": 259.0, "Lr": 266.0, "Rf": 267.0, "Db": 268.0,
    "Sg": 269.0, "Bh": 270.0, "Hs": 269.0, "Mt": 278.0, "Ds": 281.0,
    "Rg": 282.0, "Cn": 285.0, "Nh": 286.0, "Fl": 289.0, "Mc": 290.0,
    "Lv": 293.0, "Ts": 294.0, "Og": 294.0,
}
_ESTIMATED_ATOMIC_MASS = frozenset({"Tc", "Pm", "Po", "At", "Rn", "Fr", "Ra", "Ac", "Np", "Pu", "Am", "Cm", "Bk", "Cf", "Es", "Fm", "Md", "No", "Lr", "Rf", "Db", "Sg", "Bh", "Hs", "Mt", "Ds", "Rg", "Cn", "Nh", "Fl", "Mc", "Lv", "Ts", "Og"})

# Known approximate temperatures (kelvin). This is a practical phase-change
# subset, with values at roughly 1 atm; the full table still supports lookup.
_PHASE_POINTS = {
    "hydrogen": (13.99, 20.27), "helium": (0.95, 4.22), "lithium": (453.65, 1603),
    "beryllium": (1560, 2742), "boron": (2349, 4200), "carbon": (3823, 4300),
    "nitrogen": (63.15, 77.36), "oxygen": (54.36, 90.19), "fluorine": (53.53, 85.03),
    "neon": (24.56, 27.07), "sodium": (370.87, 1156), "magnesium": (923, 1363),
    "aluminum": (933.47, 2792), "silicon": (1687, 3538), "phosphorus": (317.3, 553),
    "sulfur": (388.36, 717.8), "chlorine": (171.6, 239.11), "argon": (83.8, 87.3),
    "potassium": (336.53, 1032), "calcium": (1115, 1757), "iron": (1811, 3134),
    "copper": (1357.77, 2835), "zinc": (692.68, 1180), "gallium": (302.91, 2477),
    "bromine": (265.8, 332.0), "silver": (1234.93, 2435), "tin": (505.08, 2875),
    "iodine": (386.85, 457.4), "cesium": (301.59, 944), "gold": (1337.33, 3129),
    "mercury": (234.32, 629.88), "lead": (600.61, 2022), "bismuth": (544.7, 1837),
    "water": (273.15, 373.15), "ice": (273.15, 373.15),
}

ELEMENTS: tuple[ElementRecord, ...] = tuple(
    ElementRecord(
        atomic_number=index,
        symbol=parts[0],
        name=parts[1],
        density_kg_m3=None if parts[2] == "-" else float(parts[2]),
        standard_state=parts[3],
        category=parts[4],
        estimated_density=len(parts) > 5 and parts[5] == "estimated",
        atomic_mass_u=_ATOMIC_MASSES_U.get(parts[0]),
        estimated_atomic_mass=parts[0] in _ESTIMATED_ATOMIC_MASS,
        melting_point_k=_PHASE_POINTS.get(parts[1].casefold(), (None, None))[0],
        boiling_point_k=_PHASE_POINTS.get(parts[1].casefold(), (None, None))[1],
    )
    for index, row in enumerate(_RAW_ELEMENTS.strip().splitlines(), start=1)
    if (parts := [part.strip() for part in row.split("|")])
)

ELEMENT_BY_NAME = {item.name.casefold(): item for item in ELEMENTS}
ELEMENT_BY_SYMBOL = {item.symbol.casefold(): item for item in ELEMENTS}
ELEMENT_ALIASES = {
    "aluminium": "aluminum", "sulphur": "sulfur", "caesium": "cesium",
}

# The periodic table is also the source of truth for pure-element matter density.
ELEMENTAL_DENSITIES_KG_M3 = {
    item.name.casefold(): item.density_kg_m3 for item in ELEMENTS if item.density_kg_m3 is not None
}
for _element in ELEMENTS:
    if _element.density_kg_m3 is not None:
        ELEMENTAL_DENSITIES_KG_M3[_element.symbol.casefold()] = _element.density_kg_m3
for _alias, _canonical in ELEMENT_ALIASES.items():
    if _canonical in ELEMENTAL_DENSITIES_KG_M3:
        ELEMENTAL_DENSITIES_KG_M3[_alias] = ELEMENTAL_DENSITIES_KG_M3[_canonical]


def resolve_element(value: str) -> ElementRecord | None:
    """Find a chemical element by full name or symbol, case-insensitively."""
    if not isinstance(value, str):
        return None
    key = " ".join(value.strip().casefold().split())
    key = ELEMENT_ALIASES.get(key, key)
    return ELEMENT_BY_NAME.get(key) or ELEMENT_BY_SYMBOL.get(key)


def material_profile(value: str) -> dict[str, Any] | None:
    """Resolve periodic metadata for a pure element, if the name is an element."""
    item = resolve_element(value)
    return item.as_dict() if item else None


def phase_for_temperature(material: str, temperature_k: float, current_state: str | None = None) -> str | None:
    """Return a known equilibrium phase for supported simple materials, if any.

    This deliberately handles only a curated 1-atm subset; it is not a chemical
    equilibrium solver. A missing return value means preserve the current phase.
    """
    key = " ".join(str(material).strip().casefold().split())
    key = ELEMENT_ALIASES.get(key, key)
    points = _PHASE_POINTS.get(key)
    if points is None:
        item = resolve_element(key)
        points = (item.melting_point_k, item.boiling_point_k) if item else None
    if not points or temperature_k < 0:
        return None
    melting, boiling = points
    if boiling is not None and temperature_k >= boiling:
        return "gas"
    if melting is not None and temperature_k < melting:
        return "solid"
    if melting is not None:
        return "liquid"
    return None


# Compact composition estimates for common compound/alloy names. Fractions are
# approximate mass fractions for simulation and display; users can define a
# custom material model for a particular grade or recipe.
_MATERIAL_COMPOSITIONS: dict[str, dict[str, Any]] = {
    "water": {"kind": "compound", "formula": "H₂O", "elements": [
        {"symbol": "H", "atomic_number": 1, "atomic_fraction": 2 / 3, "mass_fraction": 0.1119},
        {"symbol": "O", "atomic_number": 8, "atomic_fraction": 1 / 3, "mass_fraction": 0.8881},
    ]},
    "steel": {"kind": "alloy", "name": "Steel (generic estimate)", "elements": [
        {"symbol": "Fe", "atomic_number": 26, "mass_fraction": 0.985},
        {"symbol": "C", "atomic_number": 6, "mass_fraction": 0.015},
    ], "estimated": True},
    "stainless steel": {"kind": "alloy", "name": "Stainless steel (generic estimate)", "elements": [
        {"symbol": "Fe", "atomic_number": 26, "mass_fraction": 0.72},
        {"symbol": "Cr", "atomic_number": 24, "mass_fraction": 0.18},
        {"symbol": "Ni", "atomic_number": 28, "mass_fraction": 0.10},
    ], "estimated": True},
    "brass": {"kind": "alloy", "name": "Brass (generic estimate)", "elements": [
        {"symbol": "Cu", "atomic_number": 29, "mass_fraction": 0.67},
        {"symbol": "Zn", "atomic_number": 30, "mass_fraction": 0.33},
    ], "estimated": True},
    "bronze": {"kind": "alloy", "name": "Bronze (generic estimate)", "elements": [
        {"symbol": "Cu", "atomic_number": 29, "mass_fraction": 0.88},
        {"symbol": "Sn", "atomic_number": 50, "mass_fraction": 0.12},
    ], "estimated": True},
}


def composition_for_material(material: str, element: ElementRecord | None = None) -> dict[str, Any]:
    """Return a JSON-compatible composition descriptor for visualisation/debugging."""
    if element is not None:
        return {"kind": "element", "name": element.name, "symbol": element.symbol,
                "atomic_number": element.atomic_number, "fraction": 1.0}
    key = " ".join(str(material).strip().casefold().replace("_", " ").split())
    key = MATERIAL_ALIASES.get(key, key)
    if key in _MATERIAL_COMPOSITIONS:
        # Return independent nested structures so callers cannot mutate catalogue data.
        return copy.deepcopy(_MATERIAL_COMPOSITIONS[key])
    return {"kind": "material", "name": str(material)}

# The shared physical-material catalogue is the single source of truth used by
# conjuration, transmutation, equipment crafting, and the materials namespace.
# Values marked as indices are game/simulation coefficients, not engineering
# specifications. Elemental density and phase data still come from ELEMENTS.
_BASE_MATERIAL_PROFILES: dict[str, dict[str, Any]] = {
    "metal": {"density_kg_m3": 7800.0, "state": "solid", "category": "generic metal", "hardness_index": 0.52, "toughness_index": 0.58, "strength_mpa": 320.0, "magnetic_response": 0.35, "electrical_conductivity": 0.65, "thermal_conductivity": 0.55, "combustible": False, "brittle": False, "corrosion_resistance": 0.45, "estimated": True},
    "iron": {"density_kg_m3": 7870.0, "state": "solid", "category": "ferrous metal", "hardness_index": 0.48, "toughness_index": 0.62, "strength_mpa": 250.0, "magnetic_response": 1.0, "electrical_conductivity": 0.60, "thermal_conductivity": 0.62, "combustible": False, "brittle": False, "corrosion_resistance": 0.25},
    "steel": {"density_kg_m3": 7850.0, "state": "solid", "category": "alloy", "hardness_index": 0.68, "toughness_index": 0.76, "strength_mpa": 550.0, "magnetic_response": 0.85, "electrical_conductivity": 0.58, "thermal_conductivity": 0.48, "combustible": False, "brittle": False, "corrosion_resistance": 0.42, "estimated": True},
    "stainless steel": {"density_kg_m3": 8000.0, "state": "solid", "category": "alloy", "hardness_index": 0.70, "toughness_index": 0.74, "strength_mpa": 620.0, "magnetic_response": 0.25, "electrical_conductivity": 0.30, "thermal_conductivity": 0.22, "combustible": False, "brittle": False, "corrosion_resistance": 0.92, "estimated": True},
    "gold": {"density_kg_m3": 19300.0, "state": "solid", "category": "noble metal", "hardness_index": 0.22, "toughness_index": 0.56, "strength_mpa": 120.0, "magnetic_response": 0.0, "electrical_conductivity": 0.95, "thermal_conductivity": 0.95, "combustible": False, "brittle": False, "corrosion_resistance": 0.99},
    "silver": {"density_kg_m3": 10490.0, "state": "solid", "category": "noble metal", "hardness_index": 0.24, "toughness_index": 0.54, "strength_mpa": 170.0, "magnetic_response": 0.0, "electrical_conductivity": 1.0, "thermal_conductivity": 1.0, "combustible": False, "brittle": False, "corrosion_resistance": 0.95},
    "copper": {"density_kg_m3": 8960.0, "state": "solid", "category": "conductive metal", "hardness_index": 0.30, "toughness_index": 0.58, "strength_mpa": 210.0, "magnetic_response": 0.0, "electrical_conductivity": 0.98, "thermal_conductivity": 0.98, "combustible": False, "brittle": False, "corrosion_resistance": 0.68},
    "aluminum": {"density_kg_m3": 2700.0, "state": "solid", "category": "light metal", "hardness_index": 0.30, "toughness_index": 0.52, "strength_mpa": 310.0, "magnetic_response": 0.0, "electrical_conductivity": 0.61, "thermal_conductivity": 0.80, "combustible": False, "brittle": False, "corrosion_resistance": 0.82, "estimated": True},
    "bronze": {"density_kg_m3": 8800.0, "state": "solid", "category": "alloy", "hardness_index": 0.50, "toughness_index": 0.63, "strength_mpa": 350.0, "magnetic_response": 0.0, "electrical_conductivity": 0.35, "thermal_conductivity": 0.32, "combustible": False, "brittle": False, "corrosion_resistance": 0.78, "estimated": True},
    "brass": {"density_kg_m3": 8500.0, "state": "solid", "category": "alloy", "hardness_index": 0.40, "toughness_index": 0.58, "strength_mpa": 300.0, "magnetic_response": 0.0, "electrical_conductivity": 0.38, "thermal_conductivity": 0.34, "combustible": False, "brittle": False, "corrosion_resistance": 0.70, "estimated": True},
    "lead": {"density_kg_m3": 11340.0, "state": "solid", "category": "soft heavy metal", "hardness_index": 0.12, "toughness_index": 0.28, "strength_mpa": 18.0, "magnetic_response": 0.0, "electrical_conductivity": 0.25, "thermal_conductivity": 0.18, "combustible": False, "brittle": False, "corrosion_resistance": 0.42},
    "tin": {"density_kg_m3": 7310.0, "state": "solid", "category": "post-transition metal", "hardness_index": 0.18, "toughness_index": 0.35, "strength_mpa": 25.0, "magnetic_response": 0.0, "electrical_conductivity": 0.22, "thermal_conductivity": 0.20, "combustible": False, "brittle": False, "corrosion_resistance": 0.72},
    "titanium": {"density_kg_m3": 4500.0, "state": "solid", "category": "light structural metal", "hardness_index": 0.62, "toughness_index": 0.83, "strength_mpa": 900.0, "magnetic_response": 0.0, "electrical_conductivity": 0.12, "thermal_conductivity": 0.10, "combustible": False, "brittle": False, "corrosion_resistance": 0.96, "estimated": True},
    "platinum": {"density_kg_m3": 21450.0, "state": "solid", "category": "noble metal", "hardness_index": 0.48, "toughness_index": 0.62, "strength_mpa": 240.0, "magnetic_response": 0.0, "electrical_conductivity": 0.16, "thermal_conductivity": 0.16, "combustible": False, "brittle": False, "corrosion_resistance": 0.99},
    "mithril": {"density_kg_m3": 5000.0, "state": "solid", "category": "fictional alloy", "hardness_index": 0.88, "toughness_index": 0.95, "strength_mpa": 1800.0, "magnetic_response": 0.18, "electrical_conductivity": 0.45, "thermal_conductivity": 0.40, "combustible": False, "brittle": False, "corrosion_resistance": 0.98, "estimated": True},
    "adamant": {"density_kg_m3": 7800.0, "state": "solid", "category": "fictional alloy", "hardness_index": 0.99, "toughness_index": 0.82, "strength_mpa": 2400.0, "magnetic_response": 0.50, "electrical_conductivity": 0.30, "thermal_conductivity": 0.32, "combustible": False, "brittle": False, "corrosion_resistance": 0.99, "estimated": True},
    "stone": {"density_kg_m3": 2600.0, "state": "solid", "category": "mineral aggregate", "hardness_index": 0.56, "toughness_index": 0.30, "strength_mpa": 100.0, "magnetic_response": 0.0, "electrical_conductivity": 0.02, "thermal_conductivity": 0.10, "combustible": False, "brittle": True, "corrosion_resistance": 0.80},
    "granite": {"density_kg_m3": 2700.0, "state": "solid", "category": "igneous rock", "hardness_index": 0.62, "toughness_index": 0.28, "strength_mpa": 130.0, "magnetic_response": 0.02, "electrical_conductivity": 0.02, "thermal_conductivity": 0.12, "combustible": False, "brittle": True, "corrosion_resistance": 0.85},
    "marble": {"density_kg_m3": 2700.0, "state": "solid", "category": "metamorphic rock", "hardness_index": 0.42, "toughness_index": 0.25, "strength_mpa": 70.0, "magnetic_response": 0.0, "electrical_conductivity": 0.02, "thermal_conductivity": 0.08, "combustible": False, "brittle": True, "corrosion_resistance": 0.78},
    "wood": {"density_kg_m3": 700.0, "state": "solid", "category": "organic material", "hardness_index": 0.22, "toughness_index": 0.42, "strength_mpa": 55.0, "magnetic_response": 0.0, "electrical_conductivity": 0.01, "thermal_conductivity": 0.035, "combustible": True, "brittle": False, "corrosion_resistance": 0.35, "estimated": True},
    "oak": {"density_kg_m3": 750.0, "state": "solid", "category": "hardwood", "hardness_index": 0.30, "toughness_index": 0.55, "strength_mpa": 90.0, "magnetic_response": 0.0, "electrical_conductivity": 0.01, "thermal_conductivity": 0.035, "combustible": True, "brittle": False, "corrosion_resistance": 0.40, "estimated": True},
    "pine": {"density_kg_m3": 500.0, "state": "solid", "category": "softwood", "hardness_index": 0.18, "toughness_index": 0.35, "strength_mpa": 45.0, "magnetic_response": 0.0, "electrical_conductivity": 0.01, "thermal_conductivity": 0.035, "combustible": True, "brittle": False, "corrosion_resistance": 0.30, "estimated": True},
    "glass": {"density_kg_m3": 2500.0, "state": "solid", "category": "amorphous solid", "hardness_index": 0.62, "toughness_index": 0.10, "strength_mpa": 45.0, "magnetic_response": 0.0, "electrical_conductivity": 0.01, "thermal_conductivity": 0.05, "combustible": False, "brittle": True, "corrosion_resistance": 0.96},
    "crystal": {"density_kg_m3": 2700.0, "state": "solid", "category": "crystalline material", "hardness_index": 0.72, "toughness_index": 0.16, "strength_mpa": 90.0, "magnetic_response": 0.0, "electrical_conductivity": 0.03, "thermal_conductivity": 0.10, "combustible": False, "brittle": True, "corrosion_resistance": 0.90, "estimated": True},
    "sand": {"density_kg_m3": 1600.0, "state": "powder", "category": "granular mineral", "hardness_index": 0.45, "toughness_index": 0.12, "strength_mpa": 5.0, "magnetic_response": 0.0, "electrical_conductivity": 0.01, "thermal_conductivity": 0.08, "combustible": False, "brittle": False, "corrosion_resistance": 0.70, "estimated": True},
    "clay": {"density_kg_m3": 1800.0, "state": "solid", "category": "fine mineral", "hardness_index": 0.18, "toughness_index": 0.20, "strength_mpa": 8.0, "magnetic_response": 0.0, "electrical_conductivity": 0.01, "thermal_conductivity": 0.06, "combustible": False, "brittle": False, "corrosion_resistance": 0.60, "estimated": True},
    "bone": {"density_kg_m3": 1900.0, "state": "solid", "category": "biological material", "hardness_index": 0.45, "toughness_index": 0.34, "strength_mpa": 170.0, "magnetic_response": 0.0, "electrical_conductivity": 0.01, "thermal_conductivity": 0.03, "combustible": True, "brittle": True, "corrosion_resistance": 0.30, "estimated": True},
    "ice": {"density_kg_m3": 917.0, "state": "solid", "category": "frozen water", "hardness_index": 0.12, "toughness_index": 0.12, "strength_mpa": 3.0, "magnetic_response": 0.0, "electrical_conductivity": 0.01, "thermal_conductivity": 0.09, "combustible": False, "brittle": True, "corrosion_resistance": 0.20},
    "water": {"density_kg_m3": 1000.0, "state": "liquid", "category": "compound", "hardness_index": 0.0, "toughness_index": 0.0, "strength_mpa": 0.0, "magnetic_response": 0.0, "electrical_conductivity": 0.02, "thermal_conductivity": 0.025, "combustible": False, "brittle": False, "corrosion_resistance": 0.0},
    "coal": {"density_kg_m3": 1300.0, "state": "solid", "category": "carbon-rich mineral", "hardness_index": 0.25, "toughness_index": 0.20, "strength_mpa": 20.0, "magnetic_response": 0.0, "electrical_conductivity": 0.04, "thermal_conductivity": 0.04, "combustible": True, "brittle": True, "corrosion_resistance": 0.15},
    "obsidian": {"density_kg_m3": 2600.0, "state": "solid", "category": "volcanic glass", "hardness_index": 0.72, "toughness_index": 0.08, "strength_mpa": 50.0, "magnetic_response": 0.0, "electrical_conductivity": 0.01, "thermal_conductivity": 0.06, "combustible": False, "brittle": True, "corrosion_resistance": 0.88},
    "ceramic": {"density_kg_m3": 2400.0, "state": "solid", "category": "ceramic", "hardness_index": 0.82, "toughness_index": 0.16, "strength_mpa": 250.0, "magnetic_response": 0.0, "electrical_conductivity": 0.01, "thermal_conductivity": 0.10, "combustible": False, "brittle": True, "corrosion_resistance": 0.98},
    "rubber": {"density_kg_m3": 1100.0, "state": "solid", "category": "elastomer", "hardness_index": 0.15, "toughness_index": 0.72, "strength_mpa": 20.0, "magnetic_response": 0.0, "electrical_conductivity": 0.005, "thermal_conductivity": 0.025, "combustible": True, "brittle": False, "corrosion_resistance": 0.70},
    "leather": {"density_kg_m3": 860.0, "state": "solid", "category": "organic material", "hardness_index": 0.18, "toughness_index": 0.45, "strength_mpa": 35.0, "magnetic_response": 0.0, "electrical_conductivity": 0.01, "thermal_conductivity": 0.03, "combustible": True, "brittle": False, "corrosion_resistance": 0.40},
    "cloth": {"density_kg_m3": 350.0, "state": "solid", "category": "fabric", "hardness_index": 0.03, "toughness_index": 0.28, "strength_mpa": 10.0, "magnetic_response": 0.0, "electrical_conductivity": 0.005, "thermal_conductivity": 0.03, "combustible": True, "brittle": False, "corrosion_resistance": 0.25},
    "paper": {"density_kg_m3": 800.0, "state": "solid", "category": "cellulose material", "hardness_index": 0.02, "toughness_index": 0.06, "strength_mpa": 5.0, "magnetic_response": 0.0, "electrical_conductivity": 0.005, "thermal_conductivity": 0.03, "combustible": True, "brittle": True, "corrosion_resistance": 0.10},
    "brick": {"density_kg_m3": 1900.0, "state": "solid", "category": "ceramic masonry", "hardness_index": 0.44, "toughness_index": 0.18, "strength_mpa": 20.0, "magnetic_response": 0.0, "electrical_conductivity": 0.01, "thermal_conductivity": 0.05, "combustible": False, "brittle": True, "corrosion_resistance": 0.72},
}

# Expanded, consolidated physical catalogue. Each profile is an editable game
# model with explicit uncertainty rather than a promise of engineering-grade data.
# Numeric mechanical values use consistent 0..1 indices where named `*_index`.
_EXTRA_MATERIAL_PROFILES: dict[str, dict[str, Any]] = {
    # Ferrous and non-ferrous metals / alloys
    "cast iron": {"density_kg_m3":7200,"state":"solid","category":"ferrous alloy","hardness_index":0.60,"toughness_index":0.28,"strength_mpa":250,"magnetic_response":0.95,"electrical_conductivity":0.12,"thermal_conductivity":0.28,"combustible":False,"brittle":True,"corrosion_resistance":0.28,"estimated":True},
    "wrought iron": {"density_kg_m3":7800,"state":"solid","category":"ferrous alloy","hardness_index":0.42,"toughness_index":0.70,"strength_mpa":300,"magnetic_response":0.98,"electrical_conductivity":0.55,"thermal_conductivity":0.55,"combustible":False,"brittle":False,"corrosion_resistance":0.22,"estimated":True},
    "tool steel": {"density_kg_m3":7850,"state":"solid","category":"high-performance alloy","hardness_index":0.88,"toughness_index":0.56,"strength_mpa":1500,"magnetic_response":0.82,"electrical_conductivity":0.18,"thermal_conductivity":0.25,"combustible":False,"brittle":False,"corrosion_resistance":0.38,"estimated":True},
    "high carbon steel": {"density_kg_m3":7850,"state":"solid","category":"ferrous alloy","hardness_index":0.78,"toughness_index":0.52,"strength_mpa":900,"magnetic_response":0.85,"electrical_conductivity":0.30,"thermal_conductivity":0.35,"combustible":False,"brittle":False,"corrosion_resistance":0.32,"estimated":True},
    "spring steel": {"density_kg_m3":7850,"state":"solid","category":"elastic ferrous alloy","hardness_index":0.72,"toughness_index":0.82,"strength_mpa":1400,"magnetic_response":0.82,"electrical_conductivity":0.30,"thermal_conductivity":0.35,"combustible":False,"brittle":False,"corrosion_resistance":0.30,"estimated":True},
    "tungsten carbide": {"density_kg_m3":14500,"state":"solid","category":"cemented carbide","hardness_index":0.97,"toughness_index":0.42,"strength_mpa":1800,"magnetic_response":0.05,"electrical_conductivity":0.10,"thermal_conductivity":0.25,"combustible":False,"brittle":True,"corrosion_resistance":0.82,"estimated":True},
    "titanium alloy": {"density_kg_m3":4430,"state":"solid","category":"light structural alloy","hardness_index":0.72,"toughness_index":0.80,"strength_mpa":1100,"magnetic_response":0.0,"electrical_conductivity":0.10,"thermal_conductivity":0.09,"combustible":False,"brittle":False,"corrosion_resistance":0.95,"estimated":True},
    "magnesium alloy": {"density_kg_m3":1800,"state":"solid","category":"light structural alloy","hardness_index":0.38,"toughness_index":0.44,"strength_mpa":300,"magnetic_response":0.0,"electrical_conductivity":0.20,"thermal_conductivity":0.45,"combustible":True,"brittle":False,"corrosion_resistance":0.58,"estimated":True},
    "duralumin": {"density_kg_m3":2780,"state":"solid","category":"aluminium alloy","hardness_index":0.46,"toughness_index":0.58,"strength_mpa":450,"magnetic_response":0.0,"electrical_conductivity":0.32,"thermal_conductivity":0.48,"combustible":False,"brittle":False,"corrosion_resistance":0.62,"estimated":True},
    "inconel": {"density_kg_m3":8190,"state":"solid","category":"nickel superalloy","hardness_index":0.68,"toughness_index":0.80,"strength_mpa":1000,"magnetic_response":0.10,"electrical_conductivity":0.08,"thermal_conductivity":0.11,"combustible":False,"brittle":False,"corrosion_resistance":0.96,"estimated":True},
    "nichrome": {"density_kg_m3":8400,"state":"solid","category":"resistance alloy","hardness_index":0.38,"toughness_index":0.55,"strength_mpa":600,"magnetic_response":0.0,"electrical_conductivity":0.08,"thermal_conductivity":0.12,"combustible":False,"brittle":False,"corrosion_resistance":0.82,"estimated":True},
    "cupronickel": {"density_kg_m3":8900,"state":"solid","category":"copper-nickel alloy","hardness_index":0.34,"toughness_index":0.62,"strength_mpa":350,"magnetic_response":0.04,"electrical_conductivity":0.12,"thermal_conductivity":0.18,"combustible":False,"brittle":False,"corrosion_resistance":0.90,"estimated":True},
    "sterling silver": {"density_kg_m3":10400,"state":"solid","category":"silver alloy","hardness_index":0.32,"toughness_index":0.56,"strength_mpa":300,"magnetic_response":0.0,"electrical_conductivity":0.82,"thermal_conductivity":0.76,"combustible":False,"brittle":False,"corrosion_resistance":0.82,"estimated":True},
    "electrum": {"density_kg_m3":15000,"state":"solid","category":"gold-silver alloy","hardness_index":0.30,"toughness_index":0.56,"strength_mpa":180,"magnetic_response":0.0,"electrical_conductivity":0.70,"thermal_conductivity":0.70,"combustible":False,"brittle":False,"corrosion_resistance":0.95,"estimated":True},
    "pewter": {"density_kg_m3":7300,"state":"solid","category":"tin alloy","hardness_index":0.15,"toughness_index":0.32,"strength_mpa":35,"magnetic_response":0.0,"electrical_conductivity":0.12,"thermal_conductivity":0.18,"combustible":False,"brittle":False,"corrosion_resistance":0.68,"estimated":True},
    "solder": {"density_kg_m3":8500,"state":"solid","category":"low-melting alloy","hardness_index":0.12,"toughness_index":0.24,"strength_mpa":45,"magnetic_response":0.0,"electrical_conductivity":0.18,"thermal_conductivity":0.20,"combustible":False,"brittle":False,"corrosion_resistance":0.45,"estimated":True},
    "cobalt alloy": {"density_kg_m3":8800,"state":"solid","category":"cobalt alloy","hardness_index":0.66,"toughness_index":0.70,"strength_mpa":900,"magnetic_response":0.65,"electrical_conductivity":0.12,"thermal_conductivity":0.14,"combustible":False,"brittle":False,"corrosion_resistance":0.90,"estimated":True},
    # Stone, soil, minerals and building materials
    "limestone": {"density_kg_m3":2600,"state":"solid","category":"sedimentary rock","hardness_index":0.42,"toughness_index":0.24,"strength_mpa":70,"magnetic_response":0.0,"electrical_conductivity":0.02,"thermal_conductivity":0.09,"combustible":False,"brittle":True,"corrosion_resistance":0.50,"estimated":True},
    "sandstone": {"density_kg_m3":2300,"state":"solid","category":"sedimentary rock","hardness_index":0.42,"toughness_index":0.25,"strength_mpa":60,"magnetic_response":0.0,"electrical_conductivity":0.015,"thermal_conductivity":0.08,"combustible":False,"brittle":True,"corrosion_resistance":0.55,"estimated":True},
    "basalt": {"density_kg_m3":2950,"state":"solid","category":"igneous rock","hardness_index":0.70,"toughness_index":0.38,"strength_mpa":180,"magnetic_response":0.06,"electrical_conductivity":0.02,"thermal_conductivity":0.12,"combustible":False,"brittle":True,"corrosion_resistance":0.86,"estimated":True},
    "slate": {"density_kg_m3":2750,"state":"solid","category":"metamorphic rock","hardness_index":0.56,"toughness_index":0.20,"strength_mpa":90,"magnetic_response":0.0,"electrical_conductivity":0.02,"thermal_conductivity":0.09,"combustible":False,"brittle":True,"corrosion_resistance":0.82,"estimated":True},
    "quartz": {"density_kg_m3":2650,"state":"solid","category":"silicate mineral","hardness_index":0.78,"toughness_index":0.14,"strength_mpa":80,"magnetic_response":0.0,"electrical_conductivity":0.005,"thermal_conductivity":0.08,"combustible":False,"brittle":True,"corrosion_resistance":0.96,"estimated":True},
    "gypsum": {"density_kg_m3":2300,"state":"solid","category":"sulfate mineral","hardness_index":0.12,"toughness_index":0.10,"strength_mpa":12,"magnetic_response":0.0,"electrical_conductivity":0.01,"thermal_conductivity":0.06,"combustible":False,"brittle":True,"corrosion_resistance":0.42,"estimated":True},
    "chalk": {"density_kg_m3":1800,"state":"solid","category":"soft carbonate rock","hardness_index":0.08,"toughness_index":0.08,"strength_mpa":5,"magnetic_response":0.0,"electrical_conductivity":0.01,"thermal_conductivity":0.05,"combustible":False,"brittle":True,"corrosion_resistance":0.32,"estimated":True},
    "concrete": {"density_kg_m3":2400,"state":"solid","category":"cementitious composite","hardness_index":0.60,"toughness_index":0.22,"strength_mpa":35,"magnetic_response":0.0,"electrical_conductivity":0.02,"thermal_conductivity":0.08,"combustible":False,"brittle":True,"corrosion_resistance":0.65,"estimated":True},
    "reinforced concrete": {"density_kg_m3":2500,"state":"solid","category":"reinforced composite","hardness_index":0.62,"toughness_index":0.50,"strength_mpa":45,"magnetic_response":0.12,"electrical_conductivity":0.03,"thermal_conductivity":0.12,"combustible":False,"brittle":False,"corrosion_resistance":0.64,"estimated":True},
    "mortar": {"density_kg_m3":2100,"state":"solid","category":"cementitious composite","hardness_index":0.35,"toughness_index":0.15,"strength_mpa":15,"magnetic_response":0.0,"electrical_conductivity":0.015,"thermal_conductivity":0.06,"combustible":False,"brittle":True,"corrosion_resistance":0.60,"estimated":True},
    "cement": {"density_kg_m3":3150,"state":"powder","category":"hydraulic binder","hardness_index":0.10,"toughness_index":0.05,"strength_mpa":2,"magnetic_response":0.0,"electrical_conductivity":0.01,"thermal_conductivity":0.05,"combustible":False,"brittle":False,"corrosion_resistance":0.5,"estimated":True},
    "asphalt": {"density_kg_m3":2300,"state":"solid","category":"bituminous composite","hardness_index":0.22,"toughness_index":0.50,"strength_mpa":8,"magnetic_response":0.0,"electrical_conductivity":0.01,"thermal_conductivity":0.07,"combustible":True,"brittle":False,"corrosion_resistance":0.70,"estimated":True},
    "gravel": {"density_kg_m3":1700,"state":"powder","category":"granular aggregate","hardness_index":0.45,"toughness_index":0.10,"strength_mpa":3,"magnetic_response":0.0,"electrical_conductivity":0.01,"thermal_conductivity":0.07,"combustible":False,"brittle":False,"corrosion_resistance":0.75,"estimated":True},
    "soil": {"density_kg_m3":1400,"state":"powder","category":"granular organic-mineral mixture","hardness_index":0.10,"toughness_index":0.05,"strength_mpa":1,"magnetic_response":0.0,"electrical_conductivity":0.02,"thermal_conductivity":0.06,"combustible":False,"brittle":False,"corrosion_resistance":0.25,"estimated":True},
    # Woods, bamboo, engineered timber and carbonaceous solids
    "birch wood": {"density_kg_m3":670,"state":"solid","category":"wood","hardness_index":0.27,"toughness_index":0.46,"strength_mpa":80,"magnetic_response":0.0,"electrical_conductivity":0.005,"thermal_conductivity":0.035,"combustible":True,"brittle":False,"corrosion_resistance":0.30,"estimated":True},
    "cedar wood": {"density_kg_m3":450,"state":"solid","category":"wood","hardness_index":0.18,"toughness_index":0.42,"strength_mpa":45,"magnetic_response":0.0,"electrical_conductivity":0.005,"thermal_conductivity":0.03,"combustible":True,"brittle":False,"corrosion_resistance":0.55,"estimated":True},
    "ash wood": {"density_kg_m3":680,"state":"solid","category":"wood","hardness_index":0.35,"toughness_index":0.58,"strength_mpa":95,"magnetic_response":0.0,"electrical_conductivity":0.005,"thermal_conductivity":0.04,"combustible":True,"brittle":False,"corrosion_resistance":0.28,"estimated":True},
    "bamboo": {"density_kg_m3":700,"state":"solid","category":"natural fibre composite","hardness_index":0.28,"toughness_index":0.65,"strength_mpa":120,"magnetic_response":0.0,"electrical_conductivity":0.006,"thermal_conductivity":0.045,"combustible":True,"brittle":False,"corrosion_resistance":0.35,"estimated":True},
    "plywood": {"density_kg_m3":600,"state":"solid","category":"engineered wood","hardness_index":0.20,"toughness_index":0.46,"strength_mpa":45,"magnetic_response":0.0,"electrical_conductivity":0.01,"thermal_conductivity":0.035,"combustible":True,"brittle":False,"corrosion_resistance":0.30,"estimated":True},
    "charcoal": {"density_kg_m3":500,"state":"solid","category":"porous carbon","hardness_index":0.16,"toughness_index":0.08,"strength_mpa":8,"magnetic_response":0.0,"electrical_conductivity":0.06,"thermal_conductivity":0.035,"combustible":True,"brittle":True,"corrosion_resistance":0.1,"estimated":True},
    "graphite": {"density_kg_m3":2200,"state":"solid","category":"carbon allotrope","hardness_index":0.08,"toughness_index":0.08,"strength_mpa":25,"magnetic_response":0.0,"electrical_conductivity":0.65,"thermal_conductivity":0.75,"combustible":True,"brittle":True,"corrosion_resistance":0.82,"estimated":True},
    # Glass, technical ceramics and mineral composites
    "borosilicate glass": {"density_kg_m3":2230,"state":"solid","category":"technical glass","hardness_index":0.62,"toughness_index":0.13,"strength_mpa":55,"magnetic_response":0.0,"electrical_conductivity":0.005,"thermal_conductivity":0.04,"combustible":False,"brittle":True,"corrosion_resistance":0.98,"estimated":True},
    "tempered glass": {"density_kg_m3":2500,"state":"solid","category":"strengthened glass","hardness_index":0.62,"toughness_index":0.28,"strength_mpa":120,"magnetic_response":0.0,"electrical_conductivity":0.005,"thermal_conductivity":0.05,"combustible":False,"brittle":True,"corrosion_resistance":0.96,"estimated":True},
    "porcelain": {"density_kg_m3":2400,"state":"solid","category":"technical ceramic","hardness_index":0.84,"toughness_index":0.12,"strength_mpa":100,"magnetic_response":0.0,"electrical_conductivity":0.005,"thermal_conductivity":0.08,"combustible":False,"brittle":True,"corrosion_resistance":0.98,"estimated":True},
    "alumina ceramic": {"density_kg_m3":3900,"state":"solid","category":"technical ceramic","hardness_index":0.92,"toughness_index":0.20,"strength_mpa":350,"magnetic_response":0.0,"electrical_conductivity":0.001,"thermal_conductivity":0.32,"combustible":False,"brittle":True,"corrosion_resistance":0.98,"estimated":True},
    "silicon carbide": {"density_kg_m3":3210,"state":"solid","category":"technical ceramic","hardness_index":0.98,"toughness_index":0.28,"strength_mpa":400,"magnetic_response":0.0,"electrical_conductivity":0.05,"thermal_conductivity":0.65,"combustible":False,"brittle":True,"corrosion_resistance":0.98,"estimated":True},
    "fiberglass": {"density_kg_m3":1900,"state":"solid","category":"glass-fibre composite","hardness_index":0.42,"toughness_index":0.68,"strength_mpa":500,"magnetic_response":0.0,"electrical_conductivity":0.005,"thermal_conductivity":0.06,"combustible":False,"brittle":False,"corrosion_resistance":0.88,"estimated":True},
    "ceramic tile": {"density_kg_m3":2200,"state":"solid","category":"ceramic building material","hardness_index":0.72,"toughness_index":0.12,"strength_mpa":80,"magnetic_response":0.0,"electrical_conductivity":0.005,"thermal_conductivity":0.08,"combustible":False,"brittle":True,"corrosion_resistance":0.95,"estimated":True},
    # Polymers, textile fibres and engineered composites
    "polyethylene": {"density_kg_m3":950,"state":"solid","category":"thermoplastic polymer","hardness_index":0.08,"toughness_index":0.68,"strength_mpa":25,"magnetic_response":0.0,"electrical_conductivity":0.001,"thermal_conductivity":0.035,"combustible":True,"brittle":False,"corrosion_resistance":0.92,"estimated":True},
    "polypropylene": {"density_kg_m3":905,"state":"solid","category":"thermoplastic polymer","hardness_index":0.10,"toughness_index":0.62,"strength_mpa":35,"magnetic_response":0.0,"electrical_conductivity":0.001,"thermal_conductivity":0.035,"combustible":True,"brittle":False,"corrosion_resistance":0.90,"estimated":True},
    "pvc": {"density_kg_m3":1400,"state":"solid","category":"thermoplastic polymer","hardness_index":0.22,"toughness_index":0.32,"strength_mpa":50,"magnetic_response":0.0,"electrical_conductivity":0.001,"thermal_conductivity":0.03,"combustible":False,"brittle":False,"corrosion_resistance":0.90,"estimated":True},
    "acrylic": {"density_kg_m3":1180,"state":"solid","category":"transparent polymer","hardness_index":0.18,"toughness_index":0.25,"strength_mpa":70,"magnetic_response":0.0,"electrical_conductivity":0.001,"thermal_conductivity":0.035,"combustible":True,"brittle":True,"corrosion_resistance":0.82,"estimated":True},
    "ptfe": {"density_kg_m3":2200,"state":"solid","category":"fluoropolymer","hardness_index":0.06,"toughness_index":0.25,"strength_mpa":25,"magnetic_response":0.0,"electrical_conductivity":0.001,"thermal_conductivity":0.025,"combustible":False,"brittle":False,"corrosion_resistance":0.99,"estimated":True},
    "nylon": {"density_kg_m3":1150,"state":"solid","category":"polyamide fibre/polymer","hardness_index":0.16,"toughness_index":0.65,"strength_mpa":80,"magnetic_response":0.0,"electrical_conductivity":0.001,"thermal_conductivity":0.03,"combustible":True,"brittle":False,"corrosion_resistance":0.76,"estimated":True},
    "polyester": {"density_kg_m3":1380,"state":"solid","category":"synthetic textile fibre","hardness_index":0.08,"toughness_index":0.45,"strength_mpa":60,"magnetic_response":0.0,"electrical_conductivity":0.001,"thermal_conductivity":0.03,"combustible":True,"brittle":False,"corrosion_resistance":0.72,"estimated":True},
    "aramid fibre": {"density_kg_m3":1440,"state":"solid","category":"high-strength polymer fibre","hardness_index":0.10,"toughness_index":0.88,"strength_mpa":3000,"magnetic_response":0.0,"electrical_conductivity":0.001,"thermal_conductivity":0.02,"combustible":False,"brittle":False,"corrosion_resistance":0.68,"estimated":True},
    "carbon fibre composite": {"density_kg_m3":1600,"state":"solid","category":"fibre-reinforced composite","hardness_index":0.66,"toughness_index":0.70,"strength_mpa":900,"magnetic_response":0.0,"electrical_conductivity":0.25,"thermal_conductivity":0.20,"combustible":False,"brittle":False,"corrosion_resistance":0.92,"estimated":True},
    "epoxy resin": {"density_kg_m3":1150,"state":"solid","category":"thermoset polymer","hardness_index":0.32,"toughness_index":0.30,"strength_mpa":80,"magnetic_response":0.0,"electrical_conductivity":0.001,"thermal_conductivity":0.025,"combustible":True,"brittle":True,"corrosion_resistance":0.72,"estimated":True},
    "silicone rubber": {"density_kg_m3":1100,"state":"solid","category":"elastomer","hardness_index":0.08,"toughness_index":0.78,"strength_mpa":12,"magnetic_response":0.0,"electrical_conductivity":0.001,"thermal_conductivity":0.02,"combustible":False,"brittle":False,"corrosion_resistance":0.90,"estimated":True},
    "polyurethane foam": {"density_kg_m3":80,"state":"solid","category":"polymer foam","hardness_index":0.02,"toughness_index":0.22,"strength_mpa":1,"magnetic_response":0.0,"electrical_conductivity":0.001,"thermal_conductivity":0.025,"combustible":True,"brittle":False,"corrosion_resistance":0.45,"estimated":True},
    "expanded polystyrene": {"density_kg_m3":25,"state":"solid","category":"polymer foam","hardness_index":0.01,"toughness_index":0.08,"strength_mpa":0.3,"magnetic_response":0.0,"electrical_conductivity":0.001,"thermal_conductivity":0.03,"combustible":True,"brittle":True,"corrosion_resistance":0.25,"estimated":True},
    "cotton fibre": {"density_kg_m3":1540,"state":"solid","category":"natural textile fibre","hardness_index":0.02,"toughness_index":0.18,"strength_mpa":400,"magnetic_response":0.0,"electrical_conductivity":0.001,"thermal_conductivity":0.035,"combustible":True,"brittle":False,"corrosion_resistance":0.2,"estimated":True},
    "wool fibre": {"density_kg_m3":1310,"state":"solid","category":"natural textile fibre","hardness_index":0.02,"toughness_index":0.25,"strength_mpa":150,"magnetic_response":0.0,"electrical_conductivity":0.001,"thermal_conductivity":0.03,"combustible":True,"brittle":False,"corrosion_resistance":0.28,"estimated":True},
    "silk fibre": {"density_kg_m3":1300,"state":"solid","category":"natural protein fibre","hardness_index":0.02,"toughness_index":0.55,"strength_mpa":500,"magnetic_response":0.0,"electrical_conductivity":0.001,"thermal_conductivity":0.025,"combustible":True,"brittle":False,"corrosion_resistance":0.22,"estimated":True},
    "linen fibre": {"density_kg_m3":1500,"state":"solid","category":"natural textile fibre","hardness_index":0.02,"toughness_index":0.30,"strength_mpa":500,"magnetic_response":0.0,"electrical_conductivity":0.001,"thermal_conductivity":0.035,"combustible":True,"brittle":False,"corrosion_resistance":0.2,"estimated":True},
    # Biological/natural body-plan materials
    "chitin": {"density_kg_m3":1400,"state":"solid","category":"biological structural polymer","hardness_index":0.32,"toughness_index":0.42,"strength_mpa":120,"magnetic_response":0.0,"electrical_conductivity":0.005,"thermal_conductivity":0.03,"combustible":True,"brittle":False,"corrosion_resistance":0.45,"estimated":True},
    "horn": {"density_kg_m3":1250,"state":"solid","category":"biological keratin composite","hardness_index":0.28,"toughness_index":0.48,"strength_mpa":80,"magnetic_response":0.0,"electrical_conductivity":0.001,"thermal_conductivity":0.03,"combustible":True,"brittle":False,"corrosion_resistance":0.28,"estimated":True},
    "shell": {"density_kg_m3":2700,"state":"solid","category":"biomineral composite","hardness_index":0.60,"toughness_index":0.25,"strength_mpa":120,"magnetic_response":0.0,"electrical_conductivity":0.005,"thermal_conductivity":0.12,"combustible":False,"brittle":True,"corrosion_resistance":0.6,"estimated":True},
    "cartilage": {"density_kg_m3":1100,"state":"solid","category":"biological connective tissue","hardness_index":0.08,"toughness_index":0.58,"strength_mpa":25,"magnetic_response":0.0,"electrical_conductivity":0.001,"thermal_conductivity":0.025,"combustible":True,"brittle":False,"corrosion_resistance":0.2,"estimated":True},
    "cork": {"density_kg_m3":240,"state":"solid","category":"porous plant tissue","hardness_index":0.05,"toughness_index":0.25,"strength_mpa":5,"magnetic_response":0.0,"electrical_conductivity":0.001,"thermal_conductivity":0.035,"combustible":True,"brittle":False,"corrosion_resistance":0.35,"estimated":True},
    "blood": {"density_kg_m3":1060,"state":"liquid","category":"biological fluid","hardness_index":0.0,"toughness_index":0.0,"strength_mpa":0.0,"magnetic_response":0.0,"electrical_conductivity":0.015,"thermal_conductivity":0.5,"combustible":False,"brittle":False,"corrosion_resistance":0.0,"estimated":True},
    "brine": {"density_kg_m3":1200,"state":"liquid","category":"aqueous solution","hardness_index":0.0,"toughness_index":0.0,"strength_mpa":0.0,"magnetic_response":0.0,"electrical_conductivity":0.20,"thermal_conductivity":0.60,"combustible":False,"brittle":False,"corrosion_resistance":0.0,"estimated":True},
    "ethanol": {"density_kg_m3":789,"state":"liquid","category":"organic solvent","hardness_index":0.0,"toughness_index":0.0,"strength_mpa":0.0,"magnetic_response":0.0,"electrical_conductivity":0.001,"thermal_conductivity":0.17,"combustible":True,"brittle":False,"corrosion_resistance":0.0,"estimated":True},
    "glycerol": {"density_kg_m3":1260,"state":"liquid","category":"viscous organic liquid","hardness_index":0.0,"toughness_index":0.0,"strength_mpa":0.0,"magnetic_response":0.0,"electrical_conductivity":0.001,"thermal_conductivity":0.29,"combustible":True,"brittle":False,"corrosion_resistance":0.0,"estimated":True},
    "lava": {"density_kg_m3":2700,"state":"liquid","category":"molten silicate rock","hardness_index":0.0,"toughness_index":0.0,"strength_mpa":0.0,"magnetic_response":0.0,"electrical_conductivity":0.02,"thermal_conductivity":0.9,"combustible":False,"brittle":False,"corrosion_resistance":0.0,"estimated":True},
    "steam": {"density_kg_m3":0.6,"state":"gas","category":"water vapour","hardness_index":0.0,"toughness_index":0.0,"strength_mpa":0.0,"magnetic_response":0.0,"electrical_conductivity":0.0,"thermal_conductivity":0.03,"combustible":False,"brittle":False,"corrosion_resistance":0.0,"estimated":True},
    "smoke": {"density_kg_m3":0.8,"state":"gas","category":"aerosol / gas mixture","hardness_index":0.0,"toughness_index":0.0,"strength_mpa":0.0,"magnetic_response":0.0,"electrical_conductivity":0.0,"thermal_conductivity":0.03,"combustible":False,"brittle":False,"corrosion_resistance":0.0,"estimated":True},
    # Fictional materials are clearly labelled as setting data, not scientific substances
    "orichalcum": {"density_kg_m3":6200,"state":"solid","category":"fictional alloy","hardness_index":0.82,"toughness_index":0.90,"strength_mpa":1500,"magnetic_response":0.18,"electrical_conductivity":0.55,"thermal_conductivity":0.44,"combustible":False,"brittle":False,"corrosion_resistance":0.97,"estimated":True},
    "star iron": {"density_kg_m3":8100,"state":"solid","category":"fictional meteoric alloy","hardness_index":0.76,"toughness_index":0.82,"strength_mpa":1300,"magnetic_response":0.72,"electrical_conductivity":0.45,"thermal_conductivity":0.52,"combustible":False,"brittle":False,"corrosion_resistance":0.78,"estimated":True},
    "sky iron": {"density_kg_m3":4200,"state":"solid","category":"fictional lightweight alloy","hardness_index":0.74,"toughness_index":0.82,"strength_mpa":1150,"magnetic_response":0.32,"electrical_conductivity":0.36,"thermal_conductivity":0.30,"combustible":False,"brittle":False,"corrosion_resistance":0.92,"estimated":True},
    "orichalcum bronze": {"density_kg_m3":7000,"state":"solid","category":"fictional enchanted alloy","hardness_index":0.78,"toughness_index":0.88,"strength_mpa":1200,"magnetic_response":0.12,"electrical_conductivity":0.48,"thermal_conductivity":0.40,"combustible":False,"brittle":False,"corrosion_resistance":0.95,"estimated":True},
    "dragonbone": {"density_kg_m3":1700,"state":"solid","category":"fictional biological composite","hardness_index":0.72,"toughness_index":0.78,"strength_mpa":320,"magnetic_response":0.0,"electrical_conductivity":0.04,"thermal_conductivity":0.06,"combustible":True,"brittle":False,"corrosion_resistance":0.62,"estimated":True},
    "dragon scale": {"density_kg_m3":2200,"state":"solid","category":"fictional keratin-mineral composite","hardness_index":0.82,"toughness_index":0.76,"strength_mpa":650,"magnetic_response":0.02,"electrical_conductivity":0.02,"thermal_conductivity":0.08,"combustible":False,"brittle":False,"corrosion_resistance":0.90,"estimated":True},
    "voidglass": {"density_kg_m3":2450,"state":"solid","category":"fictional glass","hardness_index":0.86,"toughness_index":0.42,"strength_mpa":260,"magnetic_response":0.0,"electrical_conductivity":0.015,"thermal_conductivity":0.05,"combustible":False,"brittle":False,"corrosion_resistance":0.99,"estimated":True},
    "spellglass": {"density_kg_m3":2500,"state":"solid","category":"fictional resonant glass","hardness_index":0.70,"toughness_index":0.36,"strength_mpa":140,"magnetic_response":0.0,"electrical_conductivity":0.03,"thermal_conductivity":0.08,"combustible":False,"brittle":True,"corrosion_resistance":0.96,"estimated":True},
    "rune bronze": {"density_kg_m3":8700,"state":"solid","category":"fictional conductive alloy","hardness_index":0.58,"toughness_index":0.72,"strength_mpa":480,"magnetic_response":0.05,"electrical_conductivity":0.48,"thermal_conductivity":0.42,"combustible":False,"brittle":False,"corrosion_resistance":0.82,"estimated":True},
    "obsidian steel": {"density_kg_m3":7400,"state":"solid","category":"fictional metal-ceramic composite","hardness_index":0.91,"toughness_index":0.54,"strength_mpa":950,"magnetic_response":0.22,"electrical_conductivity":0.22,"thermal_conductivity":0.21,"combustible":False,"brittle":True,"corrosion_resistance":0.91,"estimated":True},
    "enchanted crystal": {"density_kg_m3":2800,"state":"solid","category":"fictional crystalline composite","hardness_index":0.88,"toughness_index":0.44,"strength_mpa":280,"magnetic_response":0.0,"electrical_conductivity":0.08,"thermal_conductivity":0.16,"combustible":False,"brittle":True,"corrosion_resistance":0.96,"estimated":True},
    "aetherite": {"density_kg_m3":1600,"state":"solid","category":"fictional resonant mineral","hardness_index":0.60,"toughness_index":0.66,"strength_mpa":240,"magnetic_response":0.0,"electrical_conductivity":0.18,"thermal_conductivity":0.15,"combustible":False,"brittle":False,"corrosion_resistance":0.95,"estimated":True},
}
for _material_name, _material_profile in _EXTRA_MATERIAL_PROFILES.items():
    if _material_name not in _BASE_MATERIAL_PROFILES:
        _BASE_MATERIAL_PROFILES[_material_name] = _material_profile

# MATERIALS_EXPANSION_WAVE_2: consolidated engineering, natural, construction,
# fluid, biological and fictional-setting profiles. These are deliberately coarse
# world-simulation coefficients; profiles are not certified technical datasheets.
def _material_row(density, state, category, hardness, toughness, strength,
                 magnetic=0.0, electrical=0.05, thermal=0.08, combustible=False,
                 brittle=False, corrosion=0.5, *, modulus=1.0, heat=900.0,
                 melting=None, boiling=None, expansion=2e-5, porosity=0.05,
                 toxicity=0.0, transparency=0.0, resonance=0.0, tags=None,
                 uses=None, microstructure=None, fictional=False):
    return {
        "density_kg_m3": float(density), "state": state, "category": category,
        "hardness_index": float(hardness), "toughness_index": float(toughness),
        "strength_mpa": float(strength), "magnetic_response": float(magnetic),
        "electrical_conductivity": float(electrical), "thermal_conductivity": float(thermal),
        "combustible": bool(combustible), "brittle": bool(brittle),
        "corrosion_resistance": float(corrosion), "elastic_modulus_gpa": float(modulus),
        "specific_heat_j_kg_k": float(heat), "melting_point_k": melting,
        "boiling_point_k": boiling, "thermal_expansion_per_k": float(expansion),
        "porosity_index": float(porosity), "toxicity_index": float(toxicity),
        "optical_transparency_index": float(transparency), "magical_resonance_index": float(resonance),
        "tags": list(tags or [category.casefold(), state]),
        "common_uses": list(uses or ["world simulation", "crafting reference"]),
        "microstructure": microstructure or category,
        "property_scope": "estimated simulation profile; not certified engineering data",
        "estimated": True,
        **({"source": "fictional-setting-material"} if fictional else {}),
    }

_MATERIALS_EXPANSION_WAVE_2 = {
    # Pure metals and practical alloys (element-specific chemistry remains in periodic.*)
    "zinc": _material_row(7140,"solid","non-ferrous metal",0.22,0.30,120,electrical=0.25,thermal=0.25,corrosion=0.72,modulus=108,heat=388,melting=692.7,boiling=1180,uses=["galvanising", "die casting", "sacrificial coatings"]),
    "nickel": _material_row(8908,"solid","transition metal",0.42,0.55,460,magnetic=0.72,electrical=0.22,thermal=0.20,corrosion=0.88,modulus=200,heat=444,melting=1728,boiling=3186,uses=["alloying", "corrosion-resistant components", "electroplating"]),
    "cobalt": _material_row(8860,"solid","transition metal",0.48,0.52,700,magnetic=0.80,electrical=0.18,thermal=0.16,corrosion=0.78,modulus=210,heat=420,melting=1768,boiling=3200,uses=["superalloys", "hard-metal binders", "magnetic materials"]),
    "chromium": _material_row(7190,"solid","transition metal",0.72,0.25,500,magnetic=0.10,electrical=0.16,thermal=0.16,corrosion=0.90,modulus=279,heat=449,melting=2180,boiling=2944,uses=["plating", "stainless alloys", "wear-resistant finishes"]),
    "tungsten": _material_row(19300,"solid","refractory metal",0.78,0.42,900,magnetic=0.02,electrical=0.20,thermal=0.25,corrosion=0.65,modulus=400,heat=134,melting=3695,boiling=5828,uses=["high-temperature parts", "counterweights", "dense components"]),
    "molybdenum": _material_row(10280,"solid","refractory metal",0.60,0.48,650,magnetic=0.01,electrical=0.18,thermal=0.24,corrosion=0.60,modulus=329,heat=251,melting=2896,boiling=4912,uses=["high-temperature alloys", "furnace parts"]),
    "zirconium metal": _material_row(6520,"solid","reactive structural metal",0.48,0.62,330,electrical=0.08,thermal=0.12,corrosion=0.92,modulus=88,heat=278,melting=2128,boiling=4682,uses=["corrosion-resistant equipment", "specialised components"]),
    "tantalum": _material_row(16650,"solid","refractory metal",0.42,0.72,350,electrical=0.12,thermal=0.13,corrosion=0.98,modulus=186,heat=140,melting=3290,boiling=5731,uses=["corrosion-resistant linings", "electronic components"]),
    "niobium": _material_row(8570,"solid","refractory metal",0.35,0.65,300,electrical=0.12,thermal=0.13,corrosion=0.92,modulus=105,heat=265,melting=2750,boiling=5017,uses=["superalloys", "specialised steel alloying"]),
    "galvanized steel": _material_row(7850,"solid","zinc-coated steel",0.68,0.70,500,magnetic=0.7,electrical=0.50,thermal=0.40,corrosion=0.78,modulus=200,heat=500,melting=1700,uses=["outdoor frames", "ducts", "fasteners"],tags=["steel", "coated", "corrosion-resistant"]),
    "weathering steel": _material_row(7850,"solid","atmospheric-corrosion alloy",0.70,0.68,520,magnetic=0.72,electrical=0.5,thermal=0.42,corrosion=0.82,modulus=200,heat=500,melting=1700,uses=["bridges", "architectural structures"],tags=["steel", "structural", "weathering"]),
    "maraging steel": _material_row(8000,"solid","age-hardened high-strength alloy",0.82,0.78,1900,magnetic=0.55,electrical=0.26,thermal=0.30,corrosion=0.55,modulus=190,heat=460,melting=1700,uses=["high-strength tooling", "precision components"],tags=["steel", "high-strength", "heat-treated"]),
    "silicon steel": _material_row(7650,"solid","electrical steel alloy",0.45,0.42,420,magnetic=0.96,electrical=0.30,thermal=0.45,corrosion=0.45,modulus=180,heat=470,melting=1700,uses=["transformer cores", "electric motors"],tags=["ferromagnetic", "electrical", "laminated"]),
    "manganese steel": _material_row(7800,"solid","work-hardening steel alloy",0.48,0.92,700,magnetic=0.55,electrical=0.5,thermal=0.42,corrosion=0.40,modulus=200,heat=500,melting=1650,uses=["impact-resistant wear parts", "track components"],tags=["steel", "work-hardening", "tough"]),
    "phosphor bronze": _material_row(8800,"solid","copper-tin-phosphorus alloy",0.48,0.66,500,electrical=0.30,thermal=0.28,corrosion=0.86,modulus=110,heat=380,melting=1200,uses=["springs", "electrical contacts", "marine fittings"]),
    "aluminum bronze": _material_row(7700,"solid","copper-aluminium alloy",0.56,0.70,650,electrical=0.25,thermal=0.24,corrosion=0.92,modulus=115,heat=410,melting=1250,uses=["marine components", "bearings", "valves"]),
    "beryllium copper": _material_row(8250,"solid","copper-beryllium alloy",0.55,0.66,1100,electrical=0.55,thermal=0.50,corrosion=0.72,modulus=130,heat=420,melting=1250,toxicity=0.25,uses=["spring contacts", "non-sparking tools"],tags=["copper alloy", "spring", "conductive", "beryllium-containing"]),
    "nickel silver": _material_row(8700,"solid","copper-nickel-zinc alloy",0.38,0.55,400,electrical=0.18,thermal=0.20,corrosion=0.78,modulus=125,heat=380,melting=1250,uses=["decorative hardware", "instrument fittings"]),
    "magnesium metal": _material_row(1740,"solid","light reactive metal",0.22,0.36,220,electrical=0.20,thermal=0.32,combustible=True,corrosion=0.45,modulus=45,heat=102,melting=923,boiling=1363,uses=["lightweight alloys", "sacrificial components"],tags=["lightweight", "reactive", "combustible chips"]),
    "bismuth metal": _material_row(9780,"solid","brittle post-transition metal",0.15,0.18,45,electrical=0.08,thermal=0.07,corrosion=0.55,modulus=32,heat=122,melting=545,boiling=1837,uses=["low-melting alloys", "specialised castings"]),
    "cast steel": _material_row(7850,"solid","cast ferrous alloy",0.58,0.50,420,magnetic=0.68,electrical=0.48,thermal=0.40,corrosion=0.40,modulus=190,heat=490,melting=1700,uses=["machine housings", "structural castings"]),
    # Rocks, soils and geologic materials
    "pumice": _material_row(650,"solid","vesicular volcanic rock",0.45,0.12,8,brittle=True,corrosion=0.95,modulus=4,heat=850,porosity=0.72,uses=["abrasives", "lightweight aggregate", "filtration"]),
    "tuff": _material_row(1750,"solid","consolidated volcanic ash rock",0.38,0.22,35,brittle=True,corrosion=0.55,modulus=12,heat=850,porosity=0.28,uses=["masonry", "carved blocks"]),
    "gneiss": _material_row(2700,"solid","banded metamorphic rock",0.62,0.28,150,brittle=True,corrosion=0.82,modulus=60,heat=790,porosity=0.03,uses=["dimension stone", "aggregate"]),
    "schist": _material_row(2750,"solid","foliated metamorphic rock",0.48,0.22,85,brittle=True,corrosion=0.68,modulus=35,heat=800,porosity=0.08,uses=["decorative stone", "landscaping"]),
    "travertine": _material_row(2450,"solid","porous carbonate rock",0.35,0.20,45,brittle=True,corrosion=0.40,modulus=28,heat=850,porosity=0.18,uses=["flooring", "facade stone"]),
    "soapstone": _material_row(2800,"solid","talc-rich metamorphic rock",0.28,0.26,40,brittle=False,corrosion=0.78,modulus=18,heat=900,porosity=0.06,uses=["carving", "countertops", "heat-retaining vessels"]),
    "diorite": _material_row(2850,"solid","coarse-grained igneous rock",0.66,0.32,170,brittle=True,corrosion=0.82,modulus=58,heat=800,porosity=0.03,uses=["aggregate", "masonry"]),
    "andesite": _material_row(2650,"solid","intermediate volcanic rock",0.58,0.28,120,brittle=True,corrosion=0.78,modulus=45,heat=820,porosity=0.06,uses=["paving", "construction aggregate"]),
    "loam": _material_row(1350,"solid","mixed mineral-organic soil",0.06,0.05,0.3,combustible=False,brittle=False,corrosion=0.3,modulus=0.03,heat=1200,porosity=0.45,uses=["soil model", "gardening", "terrain"]),
    "topsoil": _material_row(1200,"solid","organic-rich surface soil",0.04,0.04,0.2,combustible=True,brittle=False,corrosion=0.25,modulus=0.02,heat=1350,porosity=0.50,uses=["terrain", "plant growth substrate"]),
    "peat": _material_row(450,"solid","partially decomposed organic soil",0.03,0.06,1.0,combustible=True,brittle=False,corrosion=0.18,modulus=0.01,heat=1500,porosity=0.60,uses=["wetland terrain", "soil substrate"],tags=["organic", "porous", "combustible"]),
    "adobe": _material_row(1650,"solid","earthen construction composite",0.22,0.18,4,brittle=True,corrosion=0.28,modulus=2,heat=900,porosity=0.22,uses=["walls", "low-rise construction"]),
    "rammed earth": _material_row(1950,"solid","compacted earth composite",0.32,0.20,8,brittle=True,corrosion=0.35,modulus=5,heat=850,porosity=0.16,uses=["walls", "thermal-mass construction"]),
    "gypsum board": _material_row(800,"solid","paper-faced gypsum panel",0.08,0.10,8,brittle=True,corrosion=0.28,modulus=2.5,heat=1090,porosity=0.18,uses=["interior walls", "ceiling panels"]),
    "plaster": _material_row(1200,"solid","gypsum or lime-based finish",0.10,0.12,12,brittle=True,corrosion=0.25,modulus=4,heat=1000,porosity=0.22,uses=["wall finish", "moulding"]),
    "refractory brick": _material_row(2200,"solid","high-temperature ceramic masonry",0.62,0.22,45,brittle=True,corrosion=0.82,modulus=18,heat=900,melting=1800,porosity=0.18,uses=["kilns", "furnace linings"]),
    "foamed glass": _material_row(180,"solid","closed-cell glass insulation",0.22,0.12,3,brittle=True,corrosion=0.96,modulus=1.2,heat=840,melting=1100,porosity=0.82,transparency=0.05,uses=["insulation", "lightweight fill"]),
    "silica aerogel": _material_row(120,"solid","ultra-porous silica solid",0.04,0.025,0.5,brittle=True,corrosion=0.88,modulus=0.02,heat=1000,porosity=0.96,uses=["thermal insulation", "lightweight panels"]),
    # Wood and engineered plant-based materials
    "walnut wood": _material_row(640,"solid","hardwood",0.28,0.48,75,combustible=True,brittle=False,corrosion=0.32,modulus=11,heat=1700,porosity=0.28,uses=["furniture", "carving", "interior joinery"]),
    "maple wood": _material_row(700,"solid","hardwood",0.34,0.50,95,combustible=True,brittle=False,corrosion=0.32,modulus=12,heat=1650,porosity=0.22,uses=["flooring", "furniture", "handles"]),
    "teak wood": _material_row(650,"solid","oil-rich hardwood",0.32,0.62,90,combustible=True,brittle=False,corrosion=0.55,modulus=13,heat=1600,porosity=0.18,uses=["marine joinery", "outdoor furniture"]),
    "mahogany wood": _material_row(600,"solid","hardwood",0.26,0.45,70,combustible=True,brittle=False,corrosion=0.35,modulus=10,heat=1650,porosity=0.25,uses=["furniture", "instruments", "interior joinery"]),
    "spruce wood": _material_row(430,"solid","softwood",0.16,0.38,45,combustible=True,brittle=False,corrosion=0.28,modulus=9,heat=1650,porosity=0.35,uses=["framing", "soundboards", "light structures"]),
    "balsa wood": _material_row(160,"solid","ultra-light hardwood",0.04,0.16,8,combustible=True,brittle=False,corrosion=0.18,modulus=3,heat=1700,porosity=0.58,uses=["light models", "core material", "buoyant structures"]),
    "oriented strand board": _material_row(650,"solid","engineered wood panel",0.24,0.36,25,combustible=True,brittle=False,corrosion=0.25,modulus=5,heat=1500,porosity=0.12,uses=["sheathing", "subfloor panels"]),
    "particleboard": _material_row(680,"solid","wood-particle composite",0.12,0.18,12,combustible=True,brittle=True,corrosion=0.22,modulus=3,heat=1500,porosity=0.14,uses=["furniture cores", "interior panels"]),
    # Technical ceramics, crystals and glass-ceramics
    "zirconia ceramic": _material_row(6000,"solid","technical oxide ceramic",0.78,0.38,900,brittle=True,corrosion=0.98,modulus=210,heat=460,melting=2970,porosity=0.01,uses=["wear parts", "thermal barriers", "ceramic components"]),
    "silicon nitride": _material_row(3200,"solid","technical nitride ceramic",0.84,0.42,900,brittle=True,corrosion=0.96,modulus=300,heat=700,melting=2173,porosity=0.02,uses=["bearings", "high-temperature components"]),
    "boron carbide": _material_row(2520,"solid","ultra-hard ceramic",0.97,0.24,350,brittle=True,corrosion=0.96,modulus=450,heat=950,melting=2723,porosity=0.02,uses=["abrasives", "wear parts", "protective ceramic"]),
    "titanium carbide": _material_row(4930,"solid","refractory carbide ceramic",0.94,0.34,700,brittle=True,corrosion=0.92,modulus=450,heat=600,melting=3440,porosity=0.02,uses=["hard coatings", "cutting tools"]),
    "glass ceramic": _material_row(2500,"solid","controlled-crystallisation glass ceramic",0.62,0.46,180,brittle=True,corrosion=0.96,modulus=90,heat=850,melting=1500,porosity=0.01,transparency=0.35,uses=["cookware", "precision panels", "thermal-shock-resistant parts"]),
    "fused silica": _material_row(2200,"solid","high-purity silica glass",0.50,0.25,50,brittle=True,corrosion=0.98,modulus=72,heat=740,melting=1986,expansion=5.5e-7,porosity=0.0,transparency=0.98,uses=["optics", "laboratory ware", "thermal-shock-resistant components"]),
    "sapphire crystal": _material_row(3980,"solid","single-crystal alumina",0.92,0.24,400,brittle=True,corrosion=0.99,modulus=345,heat=750,melting=2323,porosity=0.0,transparency=0.98,uses=["optical windows", "scratch-resistant surfaces"]),
    "ruby crystal": _material_row(3990,"solid","chromium-doped alumina crystal",0.90,0.22,380,brittle=True,corrosion=0.99,modulus=340,heat=750,melting=2323,porosity=0.0,transparency=0.82,uses=["optical components", "decorative crystal"]),
    # Polymers, elastomers, technical fibres and composites
    "polycarbonate": _material_row(1200,"solid","engineering thermoplastic",0.25,0.78,65,electrical=0.001,thermal=0.19,combustible=True,corrosion=0.82,modulus=2.4,heat=1200,melting=540,porosity=0.0,transparency=0.88,uses=["impact-resistant glazing", "protective housings"]),
    "abs plastic": _material_row(1040,"solid","engineering thermoplastic",0.20,0.55,45,electrical=0.001,thermal=0.18,combustible=True,corrosion=0.75,modulus=2.1,heat=1400,melting=500,porosity=0.0,uses=["enclosures", "consumer products", "printed prototypes"]),
    "pet polymer": _material_row(1380,"solid","polyester thermoplastic",0.28,0.44,55,electrical=0.001,thermal=0.20,combustible=True,corrosion=0.82,modulus=2.8,heat=1200,melting=528,porosity=0.0,uses=["bottles", "films", "fibres"]),
    "hdpe": _material_row(960,"solid","high-density polyethylene",0.12,0.55,28,electrical=0.001,thermal=0.42,combustible=True,corrosion=0.95,modulus=1.0,heat=1900,melting=403,porosity=0.0,uses=["pipes", "containers", "chemical tanks"]),
    "ldpe": _material_row(920,"solid","low-density polyethylene",0.08,0.60,12,electrical=0.001,thermal=0.33,combustible=True,corrosion=0.92,modulus=0.25,heat=2200,melting=388,porosity=0.0,uses=["films", "bags", "flexible tubing"]),
    "peek polymer": _material_row(1300,"solid","high-performance thermoplastic",0.50,0.62,100,electrical=0.001,thermal=0.25,combustible=True,corrosion=0.95,modulus=3.8,heat=1300,melting=616,uses=["hot-fluid components", "precision parts"]),
    "acetal polymer": _material_row(1410,"solid","engineering thermoplastic",0.32,0.50,65,electrical=0.001,thermal=0.28,combustible=True,corrosion=0.82,modulus=2.8,heat=1450,melting=449,uses=["gears", "bearings", "low-friction parts"]),
    "pbt polymer": _material_row(1310,"solid","engineering polyester",0.30,0.46,55,electrical=0.001,thermal=0.20,combustible=True,corrosion=0.82,modulus=2.4,heat=1200,melting=498,uses=["electrical housings", "connectors"]),
    "pps polymer": _material_row(1350,"solid","chemical-resistant thermoplastic",0.48,0.38,80,electrical=0.001,thermal=0.22,combustible=False,corrosion=0.96,modulus=4.0,heat=1000,melting=558,uses=["chemical equipment", "high-temperature housings"]),
    "thermoplastic polyurethane": _material_row(1200,"solid","thermoplastic elastomer",0.14,0.82,35,electrical=0.001,thermal=0.18,combustible=True,corrosion=0.75,modulus=0.08,heat=1500,melting=460,uses=["flexible guards", "wheels", "cable jackets"]),
    "neoprene rubber": _material_row(1230,"solid","chloroprene elastomer",0.08,0.78,18,electrical=0.001,thermal=0.14,combustible=True,corrosion=0.82,modulus=0.01,heat=1500,uses=["gaskets", "wetsuits", "vibration isolation"]),
    "epdm rubber": _material_row(1150,"solid","weather-resistant elastomer",0.05,0.82,12,electrical=0.001,thermal=0.13,combustible=True,corrosion=0.90,modulus=0.008,heat=1800,uses=["weather seals", "roof membranes", "hoses"]),
    "butyl rubber": _material_row(920,"solid","low-permeability elastomer",0.04,0.78,10,electrical=0.001,thermal=0.12,combustible=True,corrosion=0.76,modulus=0.006,heat=1750,uses=["air barriers", "inner tubes", "seals"]),
    "nitrile rubber": _material_row(1180,"solid","oil-resistant elastomer",0.08,0.76,18,electrical=0.001,thermal=0.14,combustible=True,corrosion=0.72,modulus=0.012,heat=1550,uses=["oil seals", "fuel hoses", "gloves"]),
    "uhmw polyethylene": _material_row(940,"solid","ultra-high-molecular-weight polyethylene",0.12,0.82,40,electrical=0.001,thermal=0.40,combustible=True,corrosion=0.96,modulus=0.8,heat=1900,melting=408,uses=["wear strips", "low-friction bearings", "impact panels"]),
    "jute fibre": _material_row(1300,"solid","natural bast fibre",0.15,0.34,450,combustible=True,brittle=False,corrosion=0.22,modulus=25,heat=1500,porosity=0.4,uses=["sacking", "cordage", "reinforcement"]),
    "hemp fibre": _material_row(1480,"solid","natural bast fibre",0.18,0.40,550,combustible=True,brittle=False,corrosion=0.25,modulus=35,heat=1500,porosity=0.35,uses=["rope", "textile", "biocomposites"]),
    "canvas fabric": _material_row(500,"solid","heavy woven textile",0.06,0.32,20,combustible=True,brittle=False,corrosion=0.20,modulus=0.6,heat=1400,porosity=0.38,uses=["sails", "tents", "covers"]),
    "denim fabric": _material_row(600,"solid","cotton twill textile",0.07,0.35,28,combustible=True,brittle=False,corrosion=0.18,modulus=0.7,heat=1400,porosity=0.26,uses=["clothing", "durable covers"]),
    "felt fabric": _material_row(300,"solid","compressed fibre textile",0.04,0.22,8,combustible=True,brittle=False,corrosion=0.15,modulus=0.15,heat=1500,porosity=0.5,uses=["padding", "sound absorption", "insulation"]),
    "aramid composite": _material_row(1450,"solid","aramid-fibre polymer composite",0.35,0.88,900,electrical=0.02,thermal=0.08,combustible=False,brittle=False,corrosion=0.88,modulus=80,heat=1000,uses=["impact panels", "lightweight structures"],tags=["composite", "high-strength fibre", "lightweight"]),
    "laminated safety glass": _material_row(2500,"solid","glass-polymer laminate",0.58,0.55,100,electrical=0.01,thermal=0.08,brittle=False,corrosion=0.95,modulus=65,heat=840,melting=1500,porosity=0.0,transparency=0.86,uses=["safety glazing", "transparent barriers"]),
    "basalt fibre composite": _material_row(2000,"solid","basalt fibre reinforced polymer",0.36,0.62,500,electrical=0.03,thermal=0.08,combustible=True,brittle=False,corrosion=0.88,modulus=45,heat=1000,uses=["panels", "rebar", "corrosion-resistant structures"]),
    # Fluids, fuels and chemical-like world substances. Toxicity is a game index.
    "mercury": _material_row(13534,"liquid","liquid metal",0.0,0.0,0,magnetic=0.0,electrical=0.95,thermal=0.08,corrosion=0.25,modulus=0.0,heat=140,melting=234.3,boiling=629.9,toxicity=0.95,uses=["reference fluid", "sealed scientific apparatus"],tags=["liquid metal", "conductive", "toxic"]),
    "seawater": _material_row(1025,"liquid","saline aqueous solution",0.0,0.0,0,electrical=0.28,thermal=0.60,corrosion=0.0,modulus=0.0,heat=3990,melting=271,boiling=374,toxicity=0.0,uses=["ocean environment", "fluid simulation"],tags=["fluid", "saline", "conductive"]),
    "heavy water": _material_row(1105,"liquid","deuterium oxide fluid",0.0,0.0,0,electrical=0.005,thermal=0.5,corrosion=0.0,modulus=0.0,heat=4200,melting=276.97,boiling=374.4,uses=["scientific reference", "specialised fluid"]),
    "liquid nitrogen": _material_row(807,"liquid","cryogenic fluid",0.0,0.0,0,electrical=0.0,thermal=0.14,corrosion=0.0,modulus=0.0,heat=204,melting=63.15,boiling=77.36,uses=["cryogenic environment", "phase-change simulation"],tags=["cryogenic", "gas-forming"]),
    "liquid oxygen": _material_row(1141,"liquid","cryogenic oxidising fluid",0.0,0.0,0,electrical=0.0,thermal=0.15,corrosion=0.0,modulus=0.0,heat=170,melting=54.36,boiling=90.19,toxicity=0.0,uses=["oxidiser reference", "cryogenic phase model"],tags=["cryogenic", "oxidiser"]),
    "liquid ammonia": _material_row(682,"liquid","pressurised or cryogenic reactive fluid",0.0,0.0,0,electrical=0.03,thermal=0.50,corrosion=0.0,modulus=0.0,heat=4700,melting=195.4,boiling=239.8,toxicity=0.85,uses=["industrial-fluid reference", "chemical simulation"],tags=["fluid", "toxic", "reactive"]),
    "gasoline": _material_row(745,"liquid","volatile hydrocarbon fuel",0.0,0.0,0,electrical=0.0,thermal=0.12,combustible=True,corrosion=0.0,modulus=0.0,heat=2200,melting=180,boiling=450,toxicity=0.45,uses=["fuel-state simulation", "combustion scenario"],tags=["fuel", "volatile", "combustible"]),
    "diesel fuel": _material_row(835,"liquid","hydrocarbon fuel",0.0,0.0,0,electrical=0.0,thermal=0.12,combustible=True,corrosion=0.0,modulus=0.0,heat=2000,melting=220,boiling=640,toxicity=0.30,uses=["fuel-state simulation", "combustion scenario"],tags=["fuel", "combustible"]),
    "kerosene": _material_row(800,"liquid","hydrocarbon distillate",0.0,0.0,0,electrical=0.0,thermal=0.12,combustible=True,corrosion=0.0,modulus=0.0,heat=2100,melting=190,boiling=550,toxicity=0.25,uses=["fuel-state simulation", "solvent-like liquid reference"],tags=["fuel", "combustible"]),
    "crude oil": _material_row(900,"liquid","variable petroleum mixture",0.0,0.0,0,electrical=0.0,thermal=0.12,combustible=True,corrosion=0.0,modulus=0.0,heat=1900,melting=220,boiling=700,toxicity=0.25,uses=["fluid environment", "fuel-state simulation"]),
    "hydraulic oil": _material_row(870,"liquid","industrial lubricating fluid",0.0,0.0,0,electrical=0.0,thermal=0.13,combustible=True,corrosion=0.0,modulus=0.0,heat=1900,melting=210,boiling=600,toxicity=0.12,uses=["hydraulic systems", "lubrication reference"]),
    "molten iron": _material_row(6980,"liquid","molten elemental metal",0.0,0.0,0,magnetic=0.20,electrical=0.45,thermal=0.60,corrosion=0.0,modulus=0.0,heat=820,melting=1811,boiling=3134,uses=["foundry environment", "phase-change test"],tags=["molten", "hot fluid", "metal"]),
    "molten salt": _material_row(1900,"liquid","high-temperature ionic melt",0.0,0.0,0,electrical=0.35,thermal=0.4,corrosion=0.0,modulus=0.0,heat=1500,melting=650,boiling=1500,uses=["high-temperature process model", "thermal-storage reference"]),
    "nitric acid solution": _material_row(1250,"liquid","corrosive aqueous solution",0.0,0.0,0,electrical=0.40,thermal=0.55,corrosion=0.0,modulus=0.0,heat=3000,melting=230,boiling=380,toxicity=0.9,uses=["corrosion scenario", "chemical-state simulation"],tags=["corrosive", "toxic", "aqueous"]),
    "alkaline solution": _material_row(1100,"liquid","aqueous alkaline solution",0.0,0.0,0,electrical=0.20,thermal=0.58,corrosion=0.0,modulus=0.0,heat=3700,melting=260,boiling=380,toxicity=0.65,uses=["chemical-state simulation", "surface reaction scenario"],tags=["aqueous", "caustic"]),
    # Biological materials intended for fictional body/material interactions
    "muscle tissue": _material_row(1060,"solid","biological contractile tissue",0.10,0.44,0.5,combustible=True,brittle=False,corrosion=0.15,modulus=0.03,heat=3500,porosity=0.18,uses=["anatomical material reference", "body-state modelling"],tags=["biological", "soft tissue"]),
    "skin tissue": _material_row(1100,"solid","layered biological barrier tissue",0.12,0.38,5,combustible=True,brittle=False,corrosion=0.18,modulus=0.05,heat=3300,porosity=0.15,uses=["anatomical material reference", "protective tissue modelling"],tags=["biological", "barrier"]),
    "tendon tissue": _material_row(1120,"solid","collagen-rich connective tissue",0.10,0.60,80,combustible=True,brittle=False,corrosion=0.18,modulus=1.0,heat=3000,porosity=0.12,uses=["force-transmission modelling", "anatomy reference"],tags=["biological", "fibrous", "anisotropic"]),
    "ligament tissue": _material_row(1120,"solid","elastic collagen connective tissue",0.08,0.56,35,combustible=True,brittle=False,corrosion=0.18,modulus=0.5,heat=3000,porosity=0.15,uses=["joint-stability modelling", "anatomy reference"],tags=["biological", "fibrous", "anisotropic"]),
    "collagen matrix": _material_row(1350,"solid","structural protein fibre matrix",0.15,0.45,65,combustible=True,brittle=False,corrosion=0.15,modulus=2.0,heat=1600,porosity=0.20,uses=["biomaterials", "fictional tissue scaffolds"],tags=["biological", "protein", "fibrous"]),
    "adipose tissue": _material_row(920,"solid","biological lipid-rich tissue",0.04,0.12,0.2,combustible=True,brittle=False,corrosion=0.10,modulus=0.01,heat=2300,porosity=0.08,uses=["anatomical material reference", "insulation model"],tags=["biological", "soft tissue", "lipid-rich"]),
    "plant cellulose": _material_row(1500,"solid","cellulose-rich plant fibre",0.20,0.40,150,combustible=True,brittle=False,corrosion=0.18,modulus=25,heat=1400,porosity=0.3,uses=["paper", "plant-fibre composites", "biological structure reference"]),
    "keratin": _material_row(1300,"solid","structural fibrous protein",0.30,0.40,180,combustible=True,brittle=False,corrosion=0.25,modulus=3.0,heat=1600,porosity=0.08,uses=["hair", "claw", "hoof", "scale-sheath reference"]),
    # Fictional-setting materials: each has explicit trade-offs, not universal superiority.
    "demonsteel": _material_row(8200,"solid","fictional abyssal alloy",0.88,0.74,1450,magnetic=0.42,electrical=0.18,thermal=0.20,corrosion=0.94,modulus=230,heat=520,melting=1900,expansion=1e-5,resonance=0.72,uses=["fictional heavy armour", "warded structural components"],tags=["fictional", "dense", "resonant"],fictional=True),
    "dwarven steel": _material_row(7900,"solid","fictional forged alloy",0.84,0.90,1350,magnetic=0.72,electrical=0.28,thermal=0.30,corrosion=0.82,modulus=220,heat=500,melting=1800,resonance=0.18,uses=["fictional tools", "heavy armour", "load-bearing structures"],tags=["fictional", "forged", "tough"],fictional=True),
    "elvenwood": _material_row(520,"solid","fictional living wood composite",0.55,0.78,220,combustible=True,brittle=False,corrosion=0.72,modulus=18,heat=1600,porosity=0.20,resonance=0.62,uses=["fictional bows", "living structures", "light frames"],tags=["fictional", "organic", "lightweight", "resonant"],fictional=True),
    "moonstone": _material_row(2850,"solid","fictional lunar crystalline mineral",0.72,0.32,280,brittle=True,corrosion=0.98,modulus=100,heat=760,porosity=0.01,transparency=0.55,resonance=0.70,uses=["fictional lenses", "lunar wards", "ornaments"],tags=["fictional", "crystal", "lunar"],fictional=True),
    "sunstone": _material_row(3200,"solid","fictional heat-responsive mineral",0.70,0.44,350,brittle=True,corrosion=0.94,modulus=115,heat=820,porosity=0.02,resonance=0.78,uses=["fictional heat stores", "signal beacons", "solar relics"],tags=["fictional", "mineral", "heat-responsive"],fictional=True),
    "stormglass": _material_row(2450,"solid","fictional conductive glass",0.76,0.38,230,electrical=0.55,thermal=0.12,brittle=True,corrosion=0.96,modulus=68,heat=850,melting=1500,porosity=0.0,transparency=0.75,resonance=0.86,uses=["fictional lightning channels", "weather instruments"],tags=["fictional", "glass", "conductive", "resonant"],fictional=True),
    "void alloy": _material_row(6000,"solid","fictional low-inertia alloy",0.72,0.66,900,magnetic=0.12,electrical=0.22,thermal=0.18,corrosion=0.98,modulus=90,heat=750,expansion=4e-6,resonance=0.95,uses=["fictional spatial anchors", "dimensional containment frames"],tags=["fictional", "spatial", "low-inertia claim is setting-defined"],fictional=True),
    "celestial bronze": _material_row(7600,"solid","fictional divine copper alloy",0.72,0.78,780,magnetic=0.04,electrical=0.48,thermal=0.42,corrosion=0.96,modulus=125,heat=430,melting=1400,resonance=0.72,uses=["fictional enchanted equipment", "ritual fittings"],tags=["fictional", "copper alloy", "resonant"],fictional=True),
    "aether crystal": _material_row(2400,"solid","fictional mana-responsive crystal",0.70,0.40,260,brittle=True,corrosion=0.98,modulus=80,heat=800,porosity=0.0,transparency=0.80,resonance=1.0,uses=["fictional spell foci", "construct interfaces", "resonant instruments"],tags=["fictional", "crystal", "mana-responsive"],fictional=True),
    "mana-conductive crystal": _material_row(2600,"solid","fictional energy-coupling crystal",0.68,0.45,240,electrical=0.24,thermal=0.12,brittle=True,corrosion=0.97,modulus=65,heat=850,transparency=0.72,resonance=0.98,uses=["fictional energy routing", "magic circuit substrates"],tags=["fictional", "crystal", "conductive to configured magic"],fictional=True),
    "gravity crystal": _material_row(4100,"solid","fictional inertial-field mineral",0.82,0.50,720,brittle=True,corrosion=0.98,modulus=160,heat=650,transparency=0.2,resonance=0.91,uses=["fictional gravitic anchors", "mass-sensing devices"],tags=["fictional", "mineral", "gravity-attuned"],fictional=True),
    "nullstone": _material_row(3100,"solid","fictional magic-dampening stone",0.92,0.20,190,brittle=True,corrosion=0.99,modulus=95,heat=760,porosity=0.01,resonance=0.02,uses=["fictional containment cells", "anti-enchantment barriers"],tags=["fictional", "mineral", "low magical response"],fictional=True),
    "frostglass": _material_row(2550,"solid","fictional cold-stable silicate glass",0.72,0.42,250,brittle=True,corrosion=0.98,modulus=75,heat=760,melting=1450,transparency=0.82,resonance=0.42,uses=["fictional cold chambers", "ice-resistant lenses"],tags=["fictional", "glass", "cold-stable"],fictional=True),
    "phoenix ash": _material_row(450,"powder","fictional reactive mineral-organic ash",0.05,0.02,0,combustible=False,brittle=False,corrosion=0.75,modulus=0.01,heat=950,porosity=0.65,resonance=0.85,uses=["fictional rebirth rituals", "rare catalyst in setting lore"],tags=["fictional", "powder", "reactive by setting rules"],fictional=True),
    "leviathan hide": _material_row(1100,"solid","fictional marine biological composite",0.62,0.88,350,combustible=True,brittle=False,corrosion=0.94,modulus=1.8,heat=3200,porosity=0.18,resonance=0.35,uses=["fictional flexible armour", "pressure-resistant coverings"],tags=["fictional", "biological composite", "flexible"],fictional=True),
    "basilisk scale": _material_row(2600,"solid","fictional keratin-mineral biocomposite",0.88,0.72,680,combustible=False,brittle=False,corrosion=0.92,modulus=28,heat=1100,porosity=0.05,resonance=0.25,uses=["fictional scale armour", "protective plates"],tags=["fictional", "biological composite", "armour"],fictional=True),
    "thunderstone": _material_row(3500,"solid","fictional piezoelectric-like mineral",0.74,0.35,300,electrical=0.42,thermal=0.18,brittle=True,corrosion=0.95,modulus=110,heat=760,porosity=0.01,resonance=0.82,uses=["fictional charge triggers", "storm instruments"],tags=["fictional", "mineral", "electro-responsive"],fictional=True),
    "planar glass": _material_row(2480,"solid","fictional boundary-responsive glass",0.76,0.40,245,brittle=True,corrosion=0.99,modulus=72,heat=800,transparency=0.94,resonance=0.92,uses=["fictional plane instruments", "boundary markers"],tags=["fictional", "glass", "plane-attuned"],fictional=True),
    "dreamsilk": _material_row(900,"solid","fictional adaptive filament textile",0.42,0.86,620,combustible=True,brittle=False,corrosion=0.75,modulus=12,heat=1300,porosity=0.12,resonance=0.78,uses=["fictional adaptive garments", "soft restraints", "illusion foci"],tags=["fictional", "fibre", "adaptive"],fictional=True),
    "living wood": _material_row(600,"solid","fictional responsive plant composite",0.58,0.75,180,combustible=True,brittle=False,corrosion=0.65,modulus=15,heat=1600,porosity=0.22,resonance=0.64,uses=["fictional growing structures", "adaptive tools"],tags=["fictional", "organic", "responsive"],fictional=True),
    "runic titanium": _material_row(4550,"solid","fictional inscribed titanium alloy",0.70,0.78,1050,magnetic=0.02,electrical=0.18,thermal=0.14,corrosion=0.96,modulus=115,heat=520,melting=1850,resonance=0.68,uses=["fictional rune-bearing components", "light armour"],tags=["fictional", "metal", "rune-compatible"],fictional=True),
    "dragonhide": _material_row(1250,"solid","fictional layered biological hide",0.70,0.82,400,combustible=True,brittle=False,corrosion=0.88,modulus=3.2,heat=3000,porosity=0.12,resonance=0.36,uses=["fictional flexible armour", "protective wraps"],tags=["fictional", "biological composite", "dragon"],fictional=True),
}
for _name, _profile in _MATERIALS_EXPANSION_WAVE_2.items():
    if _name not in _BASE_MATERIAL_PROFILES:
        _BASE_MATERIAL_PROFILES[_name] = _profile

# MATERIALS_EXPANSION_WAVE_3: consolidated specialist materials and fabrication
# feedstocks. Numeric fields remain approximate world-engine priors. They are
# deliberately not represented as certified engineering data or chemistry.
_MATERIALS_EXPANSION_WAVE_3 = {
    # Structural, high-temperature, corrosion-resistant and specialist alloys
    "tool steel": _material_row(7800,"solid","tool steel alloy",0.84,0.52,1100,magnetic=0.68,electrical=0.42,thermal=0.34,corrosion=0.48,modulus=210,heat=460,melting=1650,uses=["cutting tools", "dies", "wear surfaces"]),
    "spring steel": _material_row(7850,"solid","spring steel alloy",0.62,0.82,1500,magnetic=0.70,electrical=0.45,thermal=0.36,corrosion=0.42,modulus=205,heat=480,melting=1650,uses=["springs", "clips", "flexible load-bearing parts"]),
    "high-strength low-alloy steel": _material_row(7850,"solid","low-alloy structural steel",0.58,0.76,650,magnetic=0.70,electrical=0.46,thermal=0.40,corrosion=0.55,modulus=205,heat=480,melting=1660,uses=["bridges", "vehicles", "structural frames"]),
    "inconel 718": _material_row(8190,"solid","nickel superalloy",0.64,0.74,1250,magnetic=0.06,electrical=0.08,thermal=0.12,corrosion=0.94,modulus=200,heat=435,melting=1600,uses=["hot-section parts", "turbines", "high-temperature fasteners"]),
    "hastelloy c276": _material_row(8890,"solid","corrosion-resistant nickel alloy",0.48,0.68,800,magnetic=0.02,electrical=0.08,thermal=0.10,corrosion=0.99,modulus=205,heat=425,melting=1600,uses=["chemical-process equipment", "corrosive environments"]),
    "monel 400": _material_row(8800,"solid","nickel copper alloy",0.40,0.68,550,magnetic=0.02,electrical=0.12,thermal=0.18,corrosion=0.96,modulus=180,heat=430,melting=1580,uses=["marine fittings", "valves", "chemical equipment"]),
    "cupronickel": _material_row(8900,"solid","copper nickel alloy",0.28,0.68,350,electrical=0.10,thermal=0.18,corrosion=0.97,modulus=150,heat=380,melting=1250,uses=["marine piping", "heat exchangers", "coinage"]),
    "ti-6al-4v titanium alloy": _material_row(4430,"solid","alpha beta titanium alloy",0.55,0.72,950,magnetic=0.01,electrical=0.04,thermal=0.08,corrosion=0.96,modulus=114,heat=560,melting=1900,uses=["lightweight structural parts", "medical components", "aerospace"]),
    "aluminium lithium alloy": _material_row(2600,"solid","light structural aluminium alloy",0.42,0.62,500,magnetic=0.0,electrical=0.28,thermal=0.32,corrosion=0.75,modulus=78,heat=900,melting=850,uses=["light structures", "aerospace panels"]),
    "sterling silver": _material_row(10360,"solid","silver copper alloy",0.24,0.36,220,magnetic=0.0,electrical=0.88,thermal=0.82,corrosion=0.72,modulus=82,heat=230,melting=1200,uses=["jewellery", "tableware", "decorative fittings"]),
    "electrum": _material_row(13500,"solid","gold silver alloy",0.30,0.30,180,magnetic=0.0,electrical=0.66,thermal=0.62,corrosion=0.96,modulus=80,heat=180,melting=1200,uses=["historic coinage", "ornaments", "decorative inlays"]),
    "lead free solder": _material_row(7400,"solid","low melting solder alloy",0.10,0.22,65,magnetic=0.0,electrical=0.45,thermal=0.38,corrosion=0.30,modulus=45,heat=230,melting=490,uses=["electronic joints", "small metal connections"]),
    "pewter": _material_row(7300,"solid","tin based casting alloy",0.08,0.18,60,magnetic=0.0,electrical=0.12,thermal=0.18,corrosion=0.72,modulus=45,heat=230,melting=520,uses=["decorative castings", "ornaments", "small vessels"]),
    "white gold": _material_row(15000,"solid","gold based jewellery alloy",0.35,0.40,300,magnetic=0.02,electrical=0.32,thermal=0.25,corrosion=0.92,modulus=95,heat=200,melting=1400,uses=["jewellery", "fine decorative components"]),
    "babbitt metal": _material_row(7300,"solid","tin or lead bearing bearing alloy",0.06,0.36,90,magnetic=0.0,electrical=0.14,thermal=0.22,corrosion=0.44,modulus=48,heat=230,melting=620,uses=["bearing linings", "low-friction supports"]),
    "zamak alloy": _material_row(6700,"solid","zinc aluminium casting alloy",0.28,0.38,280,magnetic=0.0,electrical=0.16,thermal=0.24,corrosion=0.70,modulus=85,heat=390,melting=660,uses=["die cast housings", "hardware", "small mechanical parts"]),
    # Geology, granular terrain and mineral feedstocks
    "basalt": _material_row(2950,"solid","mafic igneous rock",0.70,0.30,180,brittle=True,corrosion=0.88,modulus=75,heat=840,porosity=0.02,uses=["aggregate", "paving", "stone wool feedstock"]),
    "gabbro": _material_row(3000,"solid","coarse mafic igneous rock",0.72,0.30,190,brittle=True,corrosion=0.86,modulus=78,heat=820,porosity=0.02,uses=["dimension stone", "aggregate"]),
    "obsidian": _material_row(2400,"solid","volcanic glass",0.74,0.08,45,brittle=True,corrosion=0.94,modulus=65,heat=800,porosity=0.01,transparency=0.16,uses=["ornaments", "sharp-edged fracture examples", "decorative stone"]),
    "slate": _material_row(2750,"solid","foliated metamorphic rock",0.48,0.22,90,brittle=True,corrosion=0.76,modulus=35,heat=850,porosity=0.04,uses=["roofing", "flooring", "writing surfaces"]),
    "marble": _material_row(2700,"solid","recrystallised carbonate rock",0.58,0.26,120,brittle=True,corrosion=0.45,modulus=55,heat=880,porosity=0.02,uses=["sculpture", "flooring", "architectural stone"]),
    "limestone": _material_row(2600,"solid","carbonate sedimentary rock",0.38,0.23,75,brittle=True,corrosion=0.35,modulus=40,heat=900,porosity=0.12,uses=["cement feedstock", "aggregate", "masonry"]),
    "chalk": _material_row(1700,"solid","soft porous carbonate rock",0.05,0.04,5,brittle=True,corrosion=0.15,modulus=3,heat=900,porosity=0.45,uses=["marking", "soil amendment", "chalkboard material"]),
    "gypsum": _material_row(2300,"solid","hydrated calcium sulfate mineral",0.14,0.08,20,brittle=True,corrosion=0.30,modulus=20,heat=1090,porosity=0.05,uses=["plaster", "wallboard core", "moulds"]),
    "halite": _material_row(2160,"solid","sodium chloride mineral",0.12,0.08,25,brittle=True,corrosion=0.05,modulus=35,heat=850,porosity=0.01,uses=["salt feedstock", "mineral reference"]),
    "fluorite": _material_row(3180,"solid","calcium fluoride mineral",0.22,0.10,35,brittle=True,corrosion=0.88,modulus=75,heat=850,porosity=0.01,transparency=0.40,uses=["optical mineral reference", "ornaments"]),
    "feldspar": _material_row(2600,"solid","aluminosilicate mineral group",0.48,0.14,95,brittle=True,corrosion=0.88,modulus=65,heat=800,porosity=0.01,uses=["ceramic feedstock", "glass feedstock"]),
    "mica": _material_row(2850,"solid","sheet silicate mineral group",0.22,0.32,70,brittle=False,corrosion=0.82,modulus=45,heat=850,porosity=0.02,uses=["electrical insulation", "thermal insulation", "mineral reference"]),
    "talc": _material_row(2750,"solid","soft sheet silicate mineral",0.03,0.08,8,brittle=False,corrosion=0.85,modulus=12,heat=900,porosity=0.02,uses=["fillers", "ceramics", "soft mineral reference"]),
    "graphite block": _material_row(1800,"solid","layered carbon solid",0.18,0.25,40,magnetic=0.0,electrical=0.58,thermal=0.54,corrosion=0.82,modulus=12,heat=700,melting=3900,uses=["electrodes", "lubricating surfaces", "thermal fixtures"]),
    "coal": _material_row(1300,"solid","carbonaceous sedimentary material",0.20,0.12,30,combustible=True,brittle=True,corrosion=0.15,modulus=6,heat=1200,porosity=0.18,uses=["fuel reference", "carbon feedstock"]),
    "coke": _material_row(900,"solid","porous carbon fuel",0.16,0.12,20,combustible=True,brittle=True,corrosion=0.10,modulus=4,heat=1000,porosity=0.48,uses=["metallurgical carbon", "high-temperature process reference"]),
    "charcoal": _material_row(300,"solid","porous carbonised biomass",0.08,0.06,8,combustible=True,brittle=True,corrosion=0.08,modulus=1,heat=700,porosity=0.68,uses=["fuel reference", "adsorbent feedstock"]),
    "silica sand": _material_row(1600,"solid","granular silicate mineral",0.18,0.06,0.0,brittle=False,corrosion=0.90,modulus=0.01,heat=800,porosity=0.38,uses=["glass feedstock", "terrain", "foundry moulds"]),
    "gravel": _material_row(1750,"solid","granular rock aggregate",0.22,0.08,0.0,brittle=False,corrosion=0.84,modulus=0.01,heat=800,porosity=0.32,uses=["drainage", "concrete aggregate", "terrain"]),
    "silt": _material_row(1450,"solid","fine mineral sediment",0.04,0.03,0.1,brittle=False,corrosion=0.22,modulus=0.01,heat=1100,porosity=0.48,uses=["terrain", "sediment", "soil profile"]),
    "laterite": _material_row(2100,"solid","iron and aluminium rich tropical soil-rock",0.32,0.16,35,brittle=True,corrosion=0.58,modulus=18,heat=900,porosity=0.18,uses=["masonry", "terrain", "soil profile"]),
    "asphalt": _material_row(2350,"solid","bituminous paving composite",0.18,0.32,8,combustible=True,brittle=False,corrosion=0.52,modulus=5,heat=920,porosity=0.04,uses=["roads", "roofing", "paving"]),
    "bitumen": _material_row(1050,"solid","viscoelastic hydrocarbon binder",0.03,0.42,2,combustible=True,brittle=False,corrosion=0.45,modulus=0.3,heat=1700,uses=["waterproofing", "paving binder", "sealing"]),
    "snow": _material_row(300,"solid","granular frozen water aggregate",0.03,0.04,0.3,brittle=False,corrosion=0.08,modulus=0.02,heat=2100,melting=273.15,porosity=0.72,uses=["terrain", "insulation", "weather state proxy"]),
    "dry ice": _material_row(1560,"solid","solid carbon dioxide",0.15,0.08,2,brittle=True,corrosion=0.18,modulus=2,heat=850,melting=194.7,uses=["cooling reference", "phase-state example"]),
    # Technical ceramics, glass and advanced carbon materials
    "borosilicate glass": _material_row(2230,"solid","low-expansion glass",0.60,0.16,70,brittle=True,corrosion=0.98,modulus=64,heat=830,melting=1700,expansion=3.3e-6,transparency=0.92,uses=["laboratory vessels", "thermal-shock resistant glassware"]),
    "fused silica": _material_row(2200,"solid","high-purity silica glass",0.66,0.18,60,brittle=True,corrosion=0.99,modulus=72,heat=740,melting=1900,expansion=5e-7,transparency=0.98,uses=["optical components", "thermal windows", "laboratory parts"]),
    "sapphire crystal": _material_row(3980,"solid","single-crystal alumina",0.98,0.18,400,brittle=True,corrosion=0.99,modulus=400,heat=760,melting=2320,transparency=0.88,uses=["scratch-resistant windows", "optical components"]),
    "ruby crystal": _material_row(3990,"solid","chromium-doped alumina crystal",0.98,0.16,390,brittle=True,corrosion=0.99,modulus=390,heat=760,melting=2320,transparency=0.72,uses=["optical components", "jewellery", "fictional laser focus reference"]),
    "zirconia ceramic": _material_row(6000,"solid","zirconium oxide ceramic",0.91,0.50,900,brittle=True,corrosion=0.99,modulus=205,heat=470,melting=2950,uses=["wear components", "thermal barriers", "dental ceramics"]),
    "tungsten carbide": _material_row(15600,"solid","cemented carbide composite",0.98,0.30,1800,brittle=True,corrosion=0.82,modulus=550,heat=210,melting=2870,uses=["cutting inserts", "abrasion-resistant tooling"]),
    "cubic boron nitride": _material_row(3480,"solid","superhard synthetic ceramic",0.98,0.20,1200,brittle=True,corrosion=0.94,modulus=700,heat=800,melting=3000,uses=["hard-material cutting", "abrasive tools"]),
    "graphene sheet stack": _material_row(2200,"solid","layered carbon nanomaterial proxy",0.90,0.45,800,magnetic=0.0,electrical=0.88,thermal=0.96,corrosion=0.92,modulus=800,heat=700,melting=3900,uses=["conductive film proxy", "composite reinforcement"],tags=["carbon", "nanomaterial", "anisotropic", "estimated bulk proxy"]),
    "graphite foam": _material_row(450,"solid","porous carbon thermal scaffold",0.10,0.12,12,electrical=0.28,thermal=0.70,corrosion=0.72,modulus=0.8,heat=700,porosity=0.78,uses=["thermal management", "lightweight conductive scaffold"]),
    "zirconia toughened alumina": _material_row(4300,"solid","composite technical ceramic",0.88,0.42,700,brittle=True,corrosion=0.99,modulus=280,heat=700,melting=2200,uses=["wear parts", "precision ceramic components"]),
    "stoneware": _material_row(2300,"solid","fired ceramic body",0.48,0.18,90,brittle=True,corrosion=0.94,modulus=60,heat=850,porosity=0.08,uses=["vessels", "tiles", "sanitary ware"]),
    "porcelain": _material_row(2400,"solid","vitrified ceramic body",0.62,0.14,100,brittle=True,corrosion=0.98,modulus=70,heat=900,porosity=0.02,uses=["insulators", "vessels", "tiles"]),
    "firebrick": _material_row(2100,"solid","refractory brick",0.40,0.12,30,brittle=True,corrosion=0.90,modulus=20,heat=1000,melting=1800,porosity=0.22,uses=["furnace linings", "kilns", "fireplaces"]),
    # High-performance plastics, foams, elastomers and fibres
    "hdpe": _material_row(955,"solid","high-density polyethylene",0.12,0.78,30,combustible=True,brittle=False,corrosion=0.97,modulus=1.1,heat=1900,melting=405,porosity=0.0,uses=["pipes", "tanks", "cutting boards"]),
    "ldpe": _material_row(920,"solid","low-density polyethylene",0.06,0.62,12,combustible=True,brittle=False,corrosion=0.96,modulus=0.25,heat=2200,melting=385,porosity=0.0,uses=["films", "bags", "flexible packaging"]),
    "pet polymer": _material_row(1380,"solid","polyester thermoplastic",0.18,0.42,65,combustible=True,brittle=False,corrosion=0.80,modulus=2.8,heat=1200,melting=530,uses=["bottles", "textile fibres", "films"]),
    "polycarbonate": _material_row(1200,"solid","impact-resistant transparent polymer",0.18,0.82,65,combustible=True,brittle=False,corrosion=0.75,modulus=2.4,heat=1200,transparency=0.86,uses=["impact panels", "protective glazing", "equipment housings"]),
    "peek polymer": _material_row(1300,"solid","high-performance engineering thermoplastic",0.25,0.52,100,combustible=False,brittle=False,corrosion=0.95,modulus=3.8,heat=1300,melting=615,uses=["high-temperature components", "chemical equipment"]),
    "uhmwpe": _material_row(940,"solid","ultra-high-molecular-weight polyethylene",0.08,0.92,45,combustible=True,brittle=False,corrosion=0.98,modulus=0.8,heat=1900,melting=410,uses=["wear strips", "impact protection", "low-friction bearings"]),
    "pom acetal": _material_row(1410,"solid","engineering acetal polymer",0.18,0.42,70,combustible=True,brittle=False,corrosion=0.88,modulus=2.8,heat=1500,melting=450,uses=["gears", "precision moving parts", "low-friction components"]),
    "epdm rubber": _material_row(1150,"solid","weather-resistant elastomer",0.06,0.78,18,combustible=True,brittle=False,corrosion=0.88,modulus=0.02,heat=2000,uses=["seals", "roofing membranes", "hoses"]),
    "neoprene rubber": _material_row(1230,"solid","chloroprene elastomer",0.08,0.70,24,combustible=False,brittle=False,corrosion=0.82,modulus=0.01,heat=1500,uses=["gaskets", "protective suits", "vibration pads"]),
    "nitrile rubber": _material_row(1200,"solid","oil-resistant elastomer",0.06,0.74,18,combustible=True,brittle=False,corrosion=0.72,modulus=0.01,heat=1500,uses=["oil seals", "gloves", "fuel hoses"]),
    "butyl rubber": _material_row(920,"solid","low-gas-permeability elastomer",0.04,0.68,12,combustible=True,brittle=False,corrosion=0.82,modulus=0.008,heat=1800,uses=["inner tubes", "air barriers", "sealants"]),
    "natural rubber": _material_row(930,"solid","natural polyisoprene elastomer",0.05,0.90,25,combustible=True,brittle=False,corrosion=0.52,modulus=0.005,heat=1900,uses=["elastic bands", "tyres", "vibration isolation"]),
    "latex": _material_row(950,"solid","natural rubber dispersion solid proxy",0.04,0.86,18,combustible=True,brittle=False,corrosion=0.38,modulus=0.003,heat=1800,uses=["elastic film", "gloves", "flexible casting"]),
    "melamine laminate": _material_row(1400,"solid","resin impregnated decorative laminate",0.28,0.32,80,combustible=False,brittle=True,corrosion=0.72,modulus=8,heat=1200,uses=["worktop surfacing", "cabinet panels"]),
    "phenolic resin": _material_row(1300,"solid","thermoset phenolic polymer",0.35,0.22,65,combustible=False,brittle=True,corrosion=0.75,modulus=6,heat=1200,uses=["electrical insulation", "heat-resistant handles"]),
    "polyimide film": _material_row(1420,"solid","high-temperature polymer film",0.12,0.52,180,combustible=False,brittle=False,corrosion=0.90,modulus=2.5,heat=1100,uses=["flexible circuits", "thermal insulation"]),
    "silica fiber": _material_row(2200,"solid","high-purity glass fibre",0.15,0.42,2000,brittle=False,corrosion=0.95,modulus=72,heat=740,uses=["thermal textiles", "reinforcement", "insulation"]),
    "basalt fiber composite": _material_row(1950,"solid","basalt fibre reinforced composite",0.46,0.70,650,combustible=False,brittle=False,corrosion=0.85,modulus=45,heat=850,uses=["reinforced panels", "thermal-resistant parts"]),
    "aramid honeycomb composite": _material_row(180,"solid","aramid core sandwich composite",0.38,0.62,120,combustible=False,brittle=False,corrosion=0.72,modulus=4,heat=1100,porosity=0.58,uses=["light panels", "impact-energy management"]),
    # Natural/biological materials useful in body and creature descriptions
    "cellulose": _material_row(1500,"solid","plant structural polysaccharide",0.03,0.16,150,combustible=True,brittle=False,corrosion=0.18,modulus=8,heat=1400,porosity=0.22,uses=["paper feedstock", "plant structure reference"]),
    "collagen": _material_row(1350,"solid","fibrous structural protein",0.04,0.75,70,combustible=True,brittle=False,corrosion=0.22,modulus=0.8,heat=1600,uses=["connective tissue reference", "biomaterials"]),
    "keratin": _material_row(1300,"solid","structural protein polymer",0.08,0.46,90,combustible=True,brittle=False,corrosion=0.25,modulus=2.0,heat=1600,uses=["hair", "feathers", "claws", "horn-like structures"]),
    "bone tissue": _material_row(1900,"solid","mineralised collagen composite",0.62,0.40,170,combustible=False,brittle=True,corrosion=0.28,modulus=17,heat=1300,porosity=0.12,uses=["anatomy reference", "bone-like construct material"]),
    "tooth enamel": _material_row(2900,"solid","highly mineralised biological tissue",0.92,0.08,350,brittle=True,corrosion=0.28,modulus=80,heat=900,uses=["anatomy reference", "hard biological surface proxy"]),
    "beeswax": _material_row(960,"solid","natural wax ester mixture",0.02,0.16,2,combustible=True,brittle=False,corrosion=0.15,modulus=0.05,heat=2100,melting=335,uses=["seals", "candles", "casting patterns"]),
    "shellac": _material_row(1200,"solid","natural resin coating",0.12,0.18,45,combustible=True,brittle=True,corrosion=0.62,modulus=2.5,heat=1200,uses=["coatings", "traditional insulation", "surface finish"]),
    "wood pulp": _material_row(500,"solid","fibrous processed wood feedstock",0.03,0.06,1,combustible=True,brittle=False,corrosion=0.10,modulus=0.02,heat=1400,porosity=0.62,uses=["paper", "moulded fibre", "composite feedstock"]),
    "paper": _material_row(800,"solid","cellulose fibre sheet",0.02,0.08,8,combustible=True,brittle=False,corrosion=0.08,modulus=0.8,heat=1300,porosity=0.48,uses=["writing", "packaging", "insulation"]),
    "cardboard": _material_row(650,"solid","layered cellulose sheet composite",0.02,0.12,5,combustible=True,brittle=False,corrosion=0.06,modulus=0.4,heat=1300,porosity=0.38,uses=["packaging", "light mock-ups", "temporary structures"]),
    "plywood": _material_row(600,"solid","cross-laminated wood veneer composite",0.18,0.54,45,combustible=True,brittle=False,corrosion=0.28,modulus=8,heat=1500,porosity=0.12,uses=["panels", "furniture", "structural sheathing"]),
    "mdf": _material_row(750,"solid","medium density fibreboard",0.12,0.20,25,combustible=True,brittle=False,corrosion=0.18,modulus=3.5,heat=1400,porosity=0.16,uses=["interior panels", "furniture", "machining"]),
    "particle board": _material_row(680,"solid","wood particle resin composite",0.08,0.12,15,combustible=True,brittle=True,corrosion=0.12,modulus=2.5,heat=1450,porosity=0.22,uses=["cabinet carcasses", "furniture cores"]),
    "bamboo composite": _material_row(800,"solid","aligned lignocellulosic composite",0.34,0.60,90,combustible=True,brittle=False,corrosion=0.32,modulus=12,heat=1500,porosity=0.16,uses=["light structural parts", "panels", "furniture"]),
    # Fluids, process media and state-bearing world materials
    "liquid helium": _material_row(125,"liquid","cryogenic noble fluid",0.0,0.0,0.0,corrosion=0.0,modulus=0.0,heat=5200,boiling=4.22,uses=["cryogenic state example"],tags=["cryogenic", "noble gas", "liquid"]),
    "liquid oxygen": _material_row(1140,"liquid","cryogenic oxidising fluid",0.0,0.0,0.0,corrosion=0.0,modulus=0.0,heat=1700,boiling=90.2,uses=["cryogenic state example"],tags=["cryogenic", "oxidiser", "liquid"]),
    "liquid argon": _material_row(1390,"liquid","cryogenic noble fluid",0.0,0.0,0.0,corrosion=0.0,modulus=0.0,heat=1100,boiling=87.3,uses=["cryogenic state example"],tags=["cryogenic", "noble gas", "liquid"]),
    "hydrogen peroxide solution": _material_row(1110,"liquid","aqueous oxidising solution",0.0,0.0,0.0,electrical=0.03,thermal=0.55,corrosion=0.0,modulus=0.0,heat=3300,boiling=423,uses=["material-state reference"],tags=["solution", "oxidising", "estimated" ]),
    "liquid ammonia": _material_row(680,"liquid","volatile alkaline fluid",0.0,0.0,0.0,electrical=0.01,thermal=0.48,corrosion=0.0,modulus=0.0,heat=4700,boiling=240,uses=["process-fluid reference"],tags=["fluid", "volatile", "estimated"]),
    "hydraulic oil": _material_row(870,"liquid","mineral hydraulic fluid",0.0,0.0,0.0,electrical=0.001,thermal=0.12,combustible=True,corrosion=0.0,modulus=0.0,heat=1900,uses=["hydraulic systems", "lubrication"]),
    "silicone oil": _material_row(970,"liquid","siloxane fluid",0.0,0.0,0.0,electrical=0.001,thermal=0.13,combustible=False,corrosion=0.0,modulus=0.0,heat=1500,uses=["damping", "thermal media", "lubrication"]),
    "molten aluminium": _material_row(2370,"liquid","molten elemental metal",0.0,0.0,0.0,electrical=0.35,thermal=0.65,corrosion=0.0,modulus=0.0,heat=1180,melting=933.5,uses=["phase-state demonstration"],tags=["molten", "metal", "hot liquid"]),
    "molten iron": _material_row(7000,"liquid","molten elemental metal",0.0,0.0,0.0,magnetic=0.3,electrical=0.25,thermal=0.55,corrosion=0.0,modulus=0.0,heat=820,melting=1811,uses=["phase-state demonstration"],tags=["molten", "metal", "hot liquid"]),
    "molten glass": _material_row(2300,"liquid","molten silicate mixture",0.0,0.0,0.0,electrical=0.01,thermal=0.70,corrosion=0.0,modulus=0.0,heat=1200,melting=1400,uses=["glass forming state reference"],tags=["molten", "silicate", "hot liquid"]),
    # Explicitly fictional materials remain tagged as fictional setting concepts
    "mythril": _material_row(4200,"solid","fictional lightweight resonant alloy",0.66,0.82,980,magnetic=0.02,electrical=0.35,thermal=0.28,corrosion=0.99,modulus=92,heat=560,melting=1900,resonance=0.86,uses=["fictional light armour", "resonance-sensitive tools", "magical construct fittings"],tags=["fictional", "alloy", "lightweight", "resonant"],fictional=True),
    "adamantine": _material_row(11500,"solid","fictional extremely hard alloy",0.99,0.62,2400,magnetic=0.25,electrical=0.22,thermal=0.18,corrosion=0.99,modulus=310,heat=380,melting=3200,resonance=0.22,uses=["fictional heavy armour", "durable construct frames", "mythic tools"],tags=["fictional", "alloy", "hard", "dense"],fictional=True),
    "star iron": _material_row(9200,"solid","fictional celestial ferrous material",0.74,0.78,1350,magnetic=0.82,electrical=0.25,thermal=0.30,corrosion=0.92,modulus=205,heat=470,melting=2200,resonance=0.75,uses=["fictional weapons", "astral instruments", "heavy frame parts"],tags=["fictional", "ferrous", "celestial"],fictional=True),
    "dragonbone": _material_row(1750,"solid","fictional mineralised biological composite",0.78,0.58,390,brittle=False,corrosion=0.60,modulus=26,heat=1100,porosity=0.10,resonance=0.42,uses=["fictional structural braces", "creature-derived composite reference"],tags=["fictional", "biological composite", "dragon"],fictional=True),
    "phoenix feather": _material_row(120,"solid","fictional heat-tolerant keratin composite",0.18,0.55,35,combustible=False,brittle=False,corrosion=0.72,modulus=0.8,heat=2400,porosity=0.42,resonance=0.95,uses=["fictional insulation", "ritual focus", "lightweight fletching"],tags=["fictional", "feather", "heat-resistant by setting rule"],fictional=True),
    "voidglass": _material_row(2450,"solid","fictional dark boundary-sensitive glass",0.80,0.24,300,brittle=True,corrosion=0.99,modulus=78,heat=760,transparency=0.12,resonance=0.92,uses=["fictional observation panels", "sealed reliquaries", "boundary instruments"],tags=["fictional", "glass", "void-attuned"],fictional=True),
    "shadow silk": _material_row(650,"solid","fictional low-mass adaptive filament",0.42,0.88,500,combustible=False,brittle=False,corrosion=0.84,modulus=8,heat=1700,porosity=0.15,resonance=0.90,uses=["fictional stealth textile", "flexible bindings", "adaptive cloth"],tags=["fictional", "fibre", "shadow-attuned"],fictional=True),
    "worldroot wood": _material_row(900,"solid","fictional living woody composite",0.66,0.85,360,combustible=True,brittle=False,corrosion=0.75,modulus=24,heat=2000,porosity=0.18,resonance=0.78,uses=["fictional living buildings", "self-adjusting tools", "root networks"],tags=["fictional", "organic", "living material"],fictional=True),
    "spellstone": _material_row(3300,"solid","fictional patterned resonant mineral",0.76,0.34,460,brittle=True,corrosion=0.99,modulus=125,heat=730,porosity=0.02,resonance=1.0,uses=["fictional spell inscription", "construct anchors", "ritual apparatus"],tags=["fictional", "mineral", "resonant"],fictional=True),
    "froststeel": _material_row(7900,"solid","fictional cold-stable steel alloy",0.72,0.78,1050,magnetic=0.65,electrical=0.38,thermal=0.33,corrosion=0.90,modulus=205,heat=480,melting=1750,expansion=8e-6,resonance=0.58,uses=["fictional cold-region tools", "stable ice-contact fittings"],tags=["fictional", "steel alloy", "cold-stable"],fictional=True),
}
for _name, _profile in _MATERIALS_EXPANSION_WAVE_3.items():
    if _name not in _BASE_MATERIAL_PROFILES:
        _BASE_MATERIAL_PROFILES[_name] = _profile

# Material-level metadata for crafting, world laws, visualisation and queries.
# These are intentionally coarse simulation descriptors, not certified data.
_MATERIAL_AUXILIARY: dict[str, dict[str, Any]] = {
    "steel": {"melting_point_k": 1700.0, "specific_heat_j_kg_k": 480.0, "elastic_modulus_gpa": 200.0, "common_uses":["tools", "structures", "weapons", "machines"], "tags":["structural", "workable", "conductive"]},
    "stainless steel": {"melting_point_k": 1700.0, "specific_heat_j_kg_k": 500.0, "elastic_modulus_gpa": 190.0, "common_uses":["corrosion-resistant structures", "kitchenware", "medical equipment"], "tags":["structural", "corrosion-resistant"]},
    "iron": {"melting_point_k": 1811.0, "specific_heat_j_kg_k": 449.0, "elastic_modulus_gpa": 211.0, "common_uses":["structures", "tools", "forging"], "tags":["ferrous", "magnetic", "conductive"]},
    "copper": {"melting_point_k": 1357.77, "specific_heat_j_kg_k": 385.0, "elastic_modulus_gpa": 117.0, "common_uses":["wiring", "pipes", "heat exchangers"], "tags":["conductive", "malleable"]},
    "aluminum": {"melting_point_k": 933.47, "specific_heat_j_kg_k": 897.0, "elastic_modulus_gpa": 69.0, "common_uses":["light structures", "vehicles", "containers"], "tags":["lightweight", "corrosion-resistant"]},
    "gold": {"melting_point_k": 1337.33, "specific_heat_j_kg_k": 129.0, "elastic_modulus_gpa": 79.0, "common_uses":["electronics", "jewellery", "corrosion-resistant contacts"], "tags":["noble", "conductive", "dense"]},
    "silver": {"melting_point_k": 1234.93, "specific_heat_j_kg_k": 235.0, "elastic_modulus_gpa": 83.0, "common_uses":["electronics", "mirrors", "jewellery"], "tags":["noble", "high-conductivity"]},
    "wood": {"elastic_modulus_gpa": 10.0, "specific_heat_j_kg_k": 1700.0, "porosity_index":0.35, "optical_transparency_index":0.0, "common_uses":["frames", "furniture", "fuel", "handles"], "tags":["organic", "anisotropic", "combustible"]},
    "stone": {"elastic_modulus_gpa": 45.0, "specific_heat_j_kg_k": 790.0, "porosity_index":0.10, "common_uses":["walls", "foundations", "sculpture", "terrain"], "tags":["mineral", "brittle"]},
    "granite": {"elastic_modulus_gpa": 55.0, "specific_heat_j_kg_k": 790.0, "porosity_index":0.04, "common_uses":["countertops", "monuments", "building stone"], "tags":["igneous", "hard", "brittle"]},
    "glass": {"elastic_modulus_gpa": 70.0, "specific_heat_j_kg_k": 840.0, "optical_transparency_index":0.9, "common_uses":["windows", "vessels", "lenses"], "tags":["transparent", "brittle"]},
    "water": {"specific_heat_j_kg_k":4182.0, "boiling_point_k":373.15, "melting_point_k":273.15, "electrical_conductivity":0.02, "common_uses":["cooling", "transport", "fluid medium"], "tags":["fluid", "heat-capacity"]},
    "ice": {"specific_heat_j_kg_k":2100.0, "melting_point_k":273.15, "optical_transparency_index":0.45, "common_uses":["cooling", "temporary structures"], "tags":["frozen", "brittle"]},
    "concrete": {"elastic_modulus_gpa":28.0,"specific_heat_j_kg_k":880.0,"porosity_index":0.16,"common_uses":["foundations", "walls", "roads"],"tags":["construction", "compressive"]},
    "reinforced concrete": {"elastic_modulus_gpa":32.0,"specific_heat_j_kg_k":900.0,"porosity_index":0.12,"common_uses":["beams", "columns", "bridges", "foundations"],"tags":["construction", "composite", "reinforced"]},
    "blood": {"specific_heat_j_kg_k":3600.0,"toxicity_index":0.0,"common_uses":["biological fluid modelling"],"tags":["biological", "fluid"]},
    "lava": {"specific_heat_j_kg_k":1200.0,"melting_point_k":1000.0,"toxicity_index":0.15,"common_uses":["volcanic environment simulation"],"tags":["hot", "molten", "hazardous"]},
    "ethanol": {"specific_heat_j_kg_k":2440.0,"melting_point_k":159.0,"boiling_point_k":351.5,"toxicity_index":0.25,"common_uses":["solvent", "laboratory fluid"],"tags":["volatile", "flammable"]},
    "polyethylene": {"elastic_modulus_gpa":0.8,"specific_heat_j_kg_k":1900.0,"melting_point_k":400.0,"common_uses":["containers", "films", "insulation"],"tags":["polymer", "insulator", "corrosion-resistant"]},
    "ptfe": {"elastic_modulus_gpa":0.5,"specific_heat_j_kg_k":1000.0,"melting_point_k":600.0,"common_uses":["low-friction liners", "chemical seals", "insulation"],"tags":["polymer", "low-friction", "chemical-resistant"]},
    "aramid fibre": {"elastic_modulus_gpa":70.0,"specific_heat_j_kg_k":1400.0,"common_uses":["protective textiles", "ropes", "reinforcement"],"tags":["high-tensile", "fibre", "reinforcement"]},
    "carbon fibre composite": {"elastic_modulus_gpa":100.0,"specific_heat_j_kg_k":800.0,"common_uses":["lightweight structures", "vehicle panels", "reinforcement"],"tags":["composite", "lightweight", "anisotropic"]},
    "mithril": {"elastic_modulus_gpa":150.0,"specific_heat_j_kg_k":500.0,"magical_resonance_index":0.55,"common_uses":["fantasy armour", "lightweight tools", "enchanted structures"],"tags":["fictional", "lightweight", "enchanted"]},
    "adamant": {"elastic_modulus_gpa":250.0,"specific_heat_j_kg_k":450.0,"magical_resonance_index":0.35,"common_uses":["fantasy fortifications", "high-durability tools"],"tags":["fictional", "extremely-hard", "enchanted"]},
    "orichalcum": {"elastic_modulus_gpa":160.0,"specific_heat_j_kg_k":520.0,"magical_resonance_index":0.65,"common_uses":["fictional arcane circuits", "ornamental armour", "construct frames"],"tags":["fictional", "resonant", "alloy"]},
    "star iron": {"elastic_modulus_gpa":210.0,"specific_heat_j_kg_k":480.0,"magical_resonance_index":0.45,"common_uses":["fictional forging", "construct cores", "durable tools"],"tags":["fictional", "meteoric", "magnetic"]},
    "sky iron": {"elastic_modulus_gpa":120.0,"specific_heat_j_kg_k":520.0,"magical_resonance_index":0.60,"common_uses":["fictional lightweight armour", "flight equipment"],"tags":["fictional", "lightweight", "resonant"]},
    "dragonbone": {"elastic_modulus_gpa":22.0,"specific_heat_j_kg_k":1200.0,"magical_resonance_index":0.35,"common_uses":["fictional biological tools", "reinforcement", "relic crafting"],"tags":["fictional", "biological", "composite"]},
    "dragon scale": {"elastic_modulus_gpa":35.0,"specific_heat_j_kg_k":900.0,"magical_resonance_index":0.5,"common_uses":["fictional armour", "heat-resistant plating"],"tags":["fictional", "protective", "heat-resistant"]},
    "voidglass": {"elastic_modulus_gpa":80.0,"specific_heat_j_kg_k":750.0,"optical_transparency_index":0.75,"magical_resonance_index":0.8,"common_uses":["fictional containment", "dimensional instruments as lore-only material"],"tags":["fictional", "glass", "resonant"]},
    "spellglass": {"elastic_modulus_gpa":65.0,"specific_heat_j_kg_k":780.0,"optical_transparency_index":0.85,"magical_resonance_index":0.9,"common_uses":["fictional focusing lenses", "rune windows", "construct interfaces"],"tags":["fictional", "transparent", "resonant"]},
    "aetherite": {"elastic_modulus_gpa":40.0,"specific_heat_j_kg_k":700.0,"magical_resonance_index":1.0,"common_uses":["fictional arcane instruments", "resonant structures"],"tags":["fictional", "resonant", "mineral"]},
}

_MATERIAL_USE_HINTS: dict[str, list[str]] = {
    "steel": ["tool", "beam", "armour", "blade", "machine"], "iron": ["forging", "structure", "tool"],
    "copper": ["wire", "conductor", "pipe", "heat exchanger"], "aluminum": ["lightweight structure", "vehicle", "container"],
    "stone": ["terrain", "wall", "foundation", "sculpture"], "wood": ["frame", "handle", "furniture", "fuel"],
    "glass": ["window", "lens", "vessel"], "concrete": ["wall", "road", "foundation"],
    "reinforced concrete": ["bridge", "beam", "column", "foundation"], "rubber": ["seal", "grip", "shock absorber"],
    "leather": ["strap", "flexible covering", "protective gear"], "cloth": ["garment", "covering", "flexible fabric"],
    "paper": ["sheet", "insulation", "writing"], "chitin": ["biological armour", "exoskeleton"],
}
for _material_name, _profile in _BASE_MATERIAL_PROFILES.items():
    _category = str(_profile.get("category", "material"))
    _state = str(_profile.get("state", "solid"))
    _is_metal = any(term in _category.casefold() for term in ("metal", "alloy", "ferrous", "steel", "copper", "gold", "silver", "carbide"))
    _is_organic = any(term in _category.casefold() for term in ("organic", "wood", "biological", "polymer", "fibre", "fiber", "elastomer", "fabric"))
    _profile.setdefault("elastic_modulus_gpa", 100.0 if _is_metal else (12.0 if "mineral" in _category or "rock" in _category else (1.0 if _is_organic else 0.1)))
    _profile.setdefault("specific_heat_j_kg_k", 500.0 if _is_metal else (800.0 if "mineral" in _category or "rock" in _category else (1500.0 if _is_organic else 1000.0)))
    _profile.setdefault("melting_point_k", _PHASE_POINTS.get(_material_name, (None, None))[0])
    _profile.setdefault("boiling_point_k", _PHASE_POINTS.get(_material_name, (None, None))[1])
    _profile.setdefault("thermal_expansion_per_k", 1.2e-5 if _is_metal else (8e-6 if "mineral" in _category or "rock" in _category else (5e-5 if _is_organic else 2e-5)))
    _profile.setdefault("porosity_index", 0.04 if _is_metal else (0.12 if "mineral" in _category or "rock" in _category else (0.25 if _is_organic else 0.08)))
    _profile.setdefault("toxicity_index", 0.0)
    _profile.setdefault("optical_transparency_index", 0.85 if "glass" in _category or "crystal" in _category else 0.0)
    _profile.setdefault("magical_resonance_index", 0.0)
    _profile.setdefault("tags", list(dict.fromkeys([_category.casefold(), _state, *( ["combustible"] if _profile.get("combustible") else []), *( ["brittle"] if _profile.get("brittle") else []), *( ["magnetic"] if float(_profile.get("magnetic_response",0)) > 0.5 else []), *( ["conductive"] if float(_profile.get("electrical_conductivity",0)) >= 0.3 else [])])))
    _profile.setdefault("common_uses", _MATERIAL_USE_HINTS.get(_material_name, ["general world simulation", "crafting reference"]))
    _profile.setdefault("microstructure", _category)
    _profile.setdefault("property_scope", "estimated gameplay coefficient; not certified engineering data")
    _profile.update(copy.deepcopy(_MATERIAL_AUXILIARY.get(_material_name, {})))
    # Alias-friendly catalog identity and explicit uncertainty are kept separate.
    if _material_name in {"mithril", "adamant", "orichalcum", "star iron", "sky iron", "orichalcum bronze", "dragonbone", "dragon scale", "voidglass", "spellglass", "rune bronze", "obsidian steel", "enchanted crystal", "aetherite"}:
        _profile["source"] = "fictional-setting-material"
        _profile["estimated"] = True

MATERIAL_ALIASES = {
    "aluminium": "aluminum", "stainless": "stainless steel", "carbon steel": "steel", "wooden": "wood",
    "stonework": "stone", "rock": "stone", "silver metal": "silver",
    "aluminium alloy": "aluminum", "aluminium foil": "aluminum",
    "carbon fiber": "carbon fibre composite", "carbon fibre": "carbon fibre composite", "fibreglass": "fiberglass",
    "pvc plastic": "pvc", "teflon": "ptfe", "kevlar": "aramid fibre",
    "oakwood": "oak", "pine wood": "pine", "wood plank": "wood",
    "dragon scales": "dragon scale", "dragon bone": "dragonbone",
    "polycarbonate plastic": "polycarbonate", "abs": "abs plastic", "pet": "pet polymer",
    "high density polyethylene": "hdpe", "low density polyethylene": "ldpe", "peek": "peek polymer",
    "pbt": "pbt polymer", "pps": "pps polymer", "uhmwpe": "uhmw polyethylene",
    "mythril": "mithril", "adamantine": "adamant",
    "eastern dragon scale": "dragon scale", "moon stone": "moonstone", "dream silk": "dreamsilk",
}

MATERIAL_DENSITIES_KG_M3: dict[str, float] = {
    name: float(profile["density_kg_m3"]) for name, profile in _BASE_MATERIAL_PROFILES.items()
}
MATERIAL_DEFAULT_STATES: dict[str, str] = {
    name: str(profile["state"]) for name, profile in _BASE_MATERIAL_PROFILES.items()
}
# Common world substances without a complete composition/mechanical model yet.
# They use explicit density + phase values rather than a silent density fallback.
MATERIAL_DENSITIES_KG_M3.update({"air": 1.225, "steam": 0.6, "smoke": 0.8, "ash": 700.0, "oil": 850.0})
MATERIAL_DEFAULT_STATES.update({"air": "gas", "steam": "gas", "smoke": "gas", "ash": "powder", "oil": "liquid"})
MATERIAL_DENSITIES_KG_M3.update(ELEMENTAL_DENSITIES_KG_M3)
for _element in ELEMENTS:
    if _element.density_kg_m3 is not None:
        MATERIAL_DENSITIES_KG_M3[_element.name.casefold()] = _element.density_kg_m3
        MATERIAL_DENSITIES_KG_M3[_element.symbol.casefold()] = _element.density_kg_m3
        if _element.standard_state != "solid":
            MATERIAL_DEFAULT_STATES[_element.name.casefold()] = _element.standard_state
            MATERIAL_DEFAULT_STATES[_element.symbol.casefold()] = _element.standard_state
for _alias, _canonical in ELEMENT_ALIASES.items():
    if _canonical in MATERIAL_DENSITIES_KG_M3:
        MATERIAL_DENSITIES_KG_M3[_alias] = MATERIAL_DENSITIES_KG_M3[_canonical]
    if _canonical in MATERIAL_DEFAULT_STATES:
        MATERIAL_DEFAULT_STATES[_alias] = MATERIAL_DEFAULT_STATES[_canonical]
for _alias, _canonical in MATERIAL_ALIASES.items():
    if _canonical in MATERIAL_DENSITIES_KG_M3:
        MATERIAL_DENSITIES_KG_M3[_alias] = MATERIAL_DENSITIES_KG_M3[_canonical]
    if _canonical in MATERIAL_DEFAULT_STATES:
        MATERIAL_DEFAULT_STATES[_alias] = MATERIAL_DEFAULT_STATES[_canonical]


def resolve_material(value: str) -> str | None:
    """Return the canonical name for a registered material or pure element."""
    if not isinstance(value, str):
        return None
    key = " ".join(value.strip().casefold().replace("_", " ").split())
    key = MATERIAL_ALIASES.get(key, key)
    if key in _BASE_MATERIAL_PROFILES:
        return key
    element = resolve_element(key)
    if element is not None:
        return element.name
    # Periodic density names also cover elements whose physical profile is approximate.
    if key in MATERIAL_DENSITIES_KG_M3:
        return key.title()
    return None


def _material_family(profile: dict[str, Any]) -> str:
    """Map detailed labels to a compact top-level material family."""
    category = str(profile.get("category", "material")).casefold()
    state = str(profile.get("state", "solid")).casefold()
    tags = {str(item).casefold() for item in profile.get("tags", []) if isinstance(item, str)}
    name = str(profile.get("name", "")).casefold()
    source = str(profile.get("source", "")).casefold()
    if "fictional" in tags or "fictional" in source or "fictional" in category:
        return "fictional materials"
    if any(token in category for token in ("biological", "organic", "wood", "protein", "tissue", "plant", "animal", "wax", "cellulose")) or tags & {"biological", "organic", "biomaterial"}:
        return "biological and organic materials"
    if any(token in category for token in ("metal", "alloy", "steel", "ferrous", "copper", "bronze", "brass", "nickel", "titanium", "solder", "carbide", "noble metal", "refractory")):
        return "metals and alloys"
    if any(token in category for token in ("glass", "ceramic", "silicate", "porcelain", "refractory brick")):
        return "glass and ceramics"
    if any(token in category for token in ("polymer", "plastic", "elastomer", "composite", "resin", "foam", "fibre", "fiber", "textile", "laminate")):
        return "polymers and composites"
    if any(token in category for token in ("rock", "mineral", "stone", "soil", "sediment", "granular", "aggregate", "clay", "carbonate", "geologic")):
        return "rocks, minerals and terrain"
    if state == "powder":
        return "granular and powdered materials"
    if state in {"liquid", "gas", "plasma"}:
        return "fluids and gases"
    if any(token in name for token in ("fabric", "fibre", "fiber", "cloth", "silk", "linen", "wool")):
        return "fibres and textiles"
    return "other materials"


def _complete_material_profile(profile: dict[str, Any]) -> dict[str, Any]:
    """Add one consistent public schema and broad family to material profiles.

    Detailed historical `category` values are preserved for compatibility and
    runtime metal checks; `family` gives queries and reports a consolidated taxonomy.
    """
    name = str(profile.get("name", "Material"))
    key = " ".join(name.strip().casefold().replace("_", " ").split())
    profile.setdefault("elastic_modulus_gpa", 0.1)
    profile.setdefault("specific_heat_j_kg_k", 1000.0)
    profile.setdefault("melting_point_k", None)
    profile.setdefault("boiling_point_k", None)
    profile.setdefault("thermal_expansion_per_k", 2e-5)
    profile.setdefault("porosity_index", 0.0)
    profile.setdefault("toxicity_index", 0.0)
    profile.setdefault("optical_transparency_index", 0.0)
    profile.setdefault("magical_resonance_index", 0.0)
    profile.setdefault("tags", [str(profile.get("category", "material")).casefold(), str(profile.get("state", "solid"))])
    profile.setdefault("common_uses", ["general world simulation", "crafting reference"])
    profile.setdefault("microstructure", profile.get("category", "material"))
    profile.setdefault("subcategory", profile.get("category", "material"))
    profile["family"] = _material_family(profile)
    profile.setdefault("property_scope", "estimated gameplay coefficient; not certified engineering data")
    element = resolve_element(name)
    if element is not None:
        profile.setdefault("atomic_number", element.atomic_number)
        profile.setdefault("symbol", element.symbol)
        profile.setdefault("atomic_mass_u", element.atomic_mass_u)
        profile.setdefault("estimated_atomic_mass", element.estimated_atomic_mass)
        profile.setdefault("melting_point_k", element.melting_point_k)
        profile.setdefault("boiling_point_k", element.boiling_point_k)
    if key in MATERIAL_ALIASES:
        profile.setdefault("aliases", [])
        if MATERIAL_ALIASES[key] not in profile["aliases"]:
            profile["aliases"].append(MATERIAL_ALIASES[key])
    return profile


def physical_material_profile(value: str) -> dict[str, Any] | None:
    """Return an independent, schema-complete profile for a known physical material."""
    canonical = resolve_material(value)
    if canonical is None:
        return None
    key = canonical.casefold()
    base = _BASE_MATERIAL_PROFILES.get(key)
    if base is not None:
        result = copy.deepcopy(base)
        result["name"] = canonical
        result["source"] = result.get("source", "estimated-material-profile" if result.get("estimated") else "material-profile")
        return _complete_material_profile(result)
    element = resolve_element(canonical)
    if element is None:
        result = {"name": canonical, "density_kg_m3": MATERIAL_DENSITIES_KG_M3.get(key),
                  "state": MATERIAL_DEFAULT_STATES.get(key, "solid"), "category": "registered material",
                  "hardness_index": 0.35, "toughness_index": 0.40, "strength_mpa": 100.0,
                  "magnetic_response": 1.0 if key in {"iron", "fe", "nickel", "ni", "cobalt", "co"} else 0.0,
                  "electrical_conductivity": 0.35, "thermal_conductivity": 0.3,
                  "combustible": False, "brittle": False, "corrosion_resistance": 0.5,
                  "estimated": True, "source": "fallback-material-profile"}
        return _complete_material_profile(result)
    magnetic = element.symbol in {"Fe", "Co", "Ni"}
    result = {
        **element.as_dict(), "density_kg_m3": element.density_kg_m3,
        "state": element.standard_state, "category": element.category,
        "hardness_index": 0.38 if "metal" in element.category else 0.3,
        "toughness_index": 0.4 if "metal" in element.category else 0.25,
        "strength_mpa": 180.0 if "metal" in element.category else 30.0,
        "magnetic_response": 1.0 if magnetic else 0.0,
        "electrical_conductivity": 0.5 if "metal" in element.category else 0.05,
        "thermal_conductivity": 0.45 if "metal" in element.category else 0.08,
        "combustible": element.symbol in {"C", "P", "S"},
        "brittle": element.category in {"metalloid", "noble gas", "halogen"},
        "corrosion_resistance": 0.45, "estimated": bool(element.estimated_density),
        "source": "periodic-estimate",
    }
    return _complete_material_profile(result)


@lru_cache(maxsize=1)
def _registered_material_snapshot() -> tuple[dict[str, Any], ...]:
    """Cached stock catalogue snapshot. Returned records are copied at API edges."""
    records: list[dict[str, Any]] = []
    seen: set[str] = set()
    for name in _BASE_MATERIAL_PROFILES:
        requested_key = " ".join(name.casefold().replace("_", " ").split())
        record = physical_material_profile(name)
        if record is None:
            continue
        # Aliases can themselves have a compatibility profile entry. Deduplicate
        # by the returned canonical name, not merely the spelling iterated here.
        canonical_key = " ".join(str(record.get("name", requested_key)).casefold().replace("_", " ").split())
        if canonical_key in seen:
            continue
        records.append(record)
        seen.add(canonical_key)
    # Keep one record per canonical material name. The physical profile for a
    # pure element also includes periodic chemistry, so duplicate rows for the
    # base element and the periodic table are redundant.
    for element in ELEMENTS:
        record = physical_material_profile(element.name)
        if record is None:
            continue
        canonical_key = " ".join(str(record.get("name", element.name)).casefold().replace("_", " ").split())
        if canonical_key in seen:
            continue
        records.append(record)
        seen.add(canonical_key)
    return tuple(records)

def registered_materials() -> list[dict[str, Any]]:
    """Return independent, sorted material summaries with duplicate names consolidated."""
    return sorted(copy.deepcopy(list(_registered_material_snapshot())), key=lambda item: str(item.get("name", "")).casefold())

