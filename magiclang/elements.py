from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True, slots=True)
class ElementProfile:
    name: str
    category: Literal["fundamental", "conceptual", "derived"]
    domains: tuple[str, ...]
    also_involved: tuple[str, ...] = ()


# Exactly four fundamental elemental constituents. The rest are built-in
# conceptual/specialized concepts, not extra members of the four-element core.
ELEMENTS: dict[str, ElementProfile] = {
    "Fire": ElementProfile("Fire", "fundamental", (
        "heat", "temperature", "thermal_change", "combustion", "anger", "passion",
    ), ("light", "expansion", "reaction")),
    "Water": ElementProfile("Water", "fundamental", (
        "fluidity", "flow", "adaptability", "coldness", "absorption", "purification",
    ), ("vitality", "pressure", "cooling")),
    "Earth": ElementProfile("Earth", "fundamental", (
        "strength", "defense", "stability", "structure", "density", "solidity", "gravity_effect",
    ), ("vitality", "pressure", "gravity_effect")),
    "Air": ElementProfile("Air", "fundamental", (
        "manipulation", "gas", "movement", "speed", "vibration", "pressure",
    ), ("flow", "sound")),

    "Light": ElementProfile("Light", "conceptual", ("light", "illumination", "radiation", "visibility", "reflection"), ("thermal_change",)),
    "Darkness": ElementProfile("Darkness", "conceptual", ("occlusion", "concealment", "light_absorption")),
    "Life": ElementProfile("Life", "conceptual", ("growth", "vitality", "regeneration", "biological_structure")),
    "Death": ElementProfile("Death", "conceptual", ("cessation", "degradation", "corpse_state"), ("decay",)),
    "Order": ElementProfile("Order", "conceptual", ("organization", "regularity", "pattern"), ("structure",)),
    "Entropy": ElementProfile("Entropy", "conceptual", ("dispersion", "disorder", "decay")),
    "Spirit": ElementProfile("Spirit", "conceptual", ("spirit", "will", "possession", "manifestation")),
    "Soul": ElementProfile("Soul", "conceptual", ("identity", "essence", "memory", "self")),
    "Space": ElementProfile("Space", "conceptual", ("position", "distance", "spatial_relation")),
    "Time": ElementProfile("Time", "conceptual", ("duration", "sequence", "rate", "temporal_relation")),
    "Void": ElementProfile("Void", "conceptual", ("separation", "absence", "vacuum_like_behavior")),

    "Lightning": ElementProfile("Lightning", "derived", ("charge", "current", "discharge", "electromagnetic_effect")),
    "Sound": ElementProfile("Sound", "derived", ("sound_wave", "resonance"), ("vibration", "pressure")),
    "Metal": ElementProfile("Metal", "derived", ("conductivity",), ("strength", "density", "structure")),
    "Nature": ElementProfile("Nature", "derived", ("ecosystem", "biological_interaction"), ("growth", "vitality")),
}

FUNDAMENTAL_ELEMENTS = {name for name, profile in ELEMENTS.items() if profile.category == "fundamental"}

# Every domain has one primary owner. Other related elements are recorded
# separately so overlap is explicit rather than accidentally duplicated.
DOMAIN_OWNER: dict[str, str] = {}
DOMAIN_INVOLVED: dict[str, tuple[str, ...]] = {}
for element_name, profile in ELEMENTS.items():
    for domain in profile.domains:
        if domain in DOMAIN_OWNER and DOMAIN_OWNER[domain] != element_name:
            raise RuntimeError(f"domain '{domain}' has multiple primary owners")
        DOMAIN_OWNER[domain] = element_name
    for domain in profile.also_involved:
        DOMAIN_INVOLVED[domain] = tuple(sorted(set(DOMAIN_INVOLVED.get(domain, ()) + (element_name,))))

# Explicit overrides make the intended overlap unambiguous.
DOMAIN_OWNER.update({
    "pressure": "Air",
    "vitality": "Life",
    "light": "Light",
    "flow": "Water",
    "strength": "Earth",
    "structure": "Earth",
    "temperature": "Fire",
    "thermal_change": "Fire",
})
DOMAIN_INVOLVED.update({
    "pressure": ("Water", "Earth"),
    "vitality": ("Water", "Earth", "Nature"),
    "light": ("Fire",),
    "flow": ("Air",),
    "strength": ("Metal",),
    "structure": ("Metal", "Order"),
    "thermal_change": ("Light",),
})


def can_influence(element: str, domain: str) -> bool:
    """Return whether an element owns or is explicitly involved in a domain."""
    return DOMAIN_OWNER.get(domain) == element or element in DOMAIN_INVOLVED.get(domain, ())


CANCELLATION_TOLERANCE = 0.01  # 1% of the larger input, deliberately named.


@dataclass(frozen=True, slots=True)
class InteractionResult:
    # kind is one of: element, material, compound
    kind: Literal["element", "material", "compound"]
    name: str
    mana: float
    ratio: float
    components: tuple[str, ...] = ()
    released_mana: float = 0.0
    note: str = ""
    energy_origin: str | None = None


def _cancel(a: str, a_mana: float, b: str, b_mana: float) -> InteractionResult:
    larger = max(a_mana, b_mana)
    diff = abs(a_mana - b_mana)
    matched = min(a_mana, b_mana)
    if larger == 0 or diff <= CANCELLATION_TOLERANCE * larger:
        # Mana is not annihilated: the interaction releases it as thermal energy.
        released = a_mana + b_mana
        return InteractionResult(
            "material", "ThermalRelease", 0.0, 0.0, (a, b), released,
            "balanced cancellation released as thermal energy/steam",
            energy_origin="mana_to_energy",
        )
    dominant = a if a_mana > b_mana else b
    remaining = diff
    return InteractionResult(
        "element", dominant, remaining, remaining / larger, (a, b), matched * 2,
        "matched mana released as thermal energy; dominant element remains",
        energy_origin="mana_to_energy",
    )


def interaction(a: str, a_mana: float, b: str, b_mana: float, *,
                available_heat: bool = False) -> InteractionResult:
    """Evaluate a defined interaction independent of argument order.

    The `a_mana`/`b_mana` values follow their corresponding object arguments;
    behavior looks up input quantities by element name before applying rules.
    """
    for label, amount in (("first", a_mana), ("second", b_mana)):
        if isinstance(amount, bool) or not isinstance(amount, (int, float)) or amount < 0:
            raise ValueError(f"{label} element mana must be a non-negative number")
    by_name = {a: float(a_mana), b: float(b_mana)}

    if a == b:
        amount = float(a_mana) + float(b_mana)
        return InteractionResult("element", a, amount, 1.0, (a, b), note="same-element reinforcement")

    if {a, b} == {"Fire", "Water"}:
        return _cancel("Fire", by_name["Fire"], "Water", by_name["Water"])

    if {a, b} == {"Light", "Darkness"}:
        return _cancel("Light", by_name["Light"], "Darkness", by_name["Darkness"])

    if {a, b} == {"Water", "Earth"}:
        return InteractionResult("material", "Mud", float(a_mana) + float(b_mana), 1.0, ("Water", "Earth"), note="Water + Earth")

    # Wood is deliberately staged: first Water + Earth -> Mud, then Mud + Life -> Wood.
    if {a, b} == {"Mud", "Life"}:
        return InteractionResult("material", "Wood", float(a_mana) + float(b_mana), 1.0, ("Mud", "Life"), note="Mud + Life")

    # Earth + Life alone is a compound, not Wood.
    if {a, b} == {"Earth", "Life"}:
        return InteractionResult("compound", "EarthLifeCompound", float(a_mana) + float(b_mana), 1.0, ("Earth", "Life"), note="requires Water + Earth -> Mud first")

    if {a, b} == {"Water", "Air"} and available_heat:
        return InteractionResult("material", "Ice", float(a_mana) + float(b_mana), 1.0, ("Water", "Air"), note="heat removed from the target")

    if {a, b} == {"Fire", "Air"}:
        amount = by_name["Fire"] + 0.5 * by_name["Air"]
        spent_air = 0.5 * by_name["Air"]
        return InteractionResult(
            "element", "Fire", amount, 1.0, ("Fire", "Air"), spent_air,
            "Air improves Fire's propagation; the used portion becomes released energy",
        )

    # Everything else is a structured compound. It is not a new fundamental element.
    return InteractionResult("compound", "Compound", float(a_mana) + float(b_mana), 1.0, (a, b), note="no special reaction is defined")
