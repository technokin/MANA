"""Reusable physical equipment blueprints for MANA conjuration.

Blueprint dimensions and combat coefficients are gameplay defaults, not
manufacturing specifications. Users can override material, mass, shape, and
available dimensions when conjuring an item.
"""
from __future__ import annotations

from copy import deepcopy
from typing import Any

_BLUEPRINTS: dict[str, dict[str, Any]] = {
    "sword": {"slot": "weapon", "material": "steel", "mass_kg": 1.4, "shape": "polygon", "length_m": 0.90, "width_m": 0.08, "thickness_m": 0.006, "damage_multiplier": 1.8, "durability": 120.0, "attack_style": "slash", "description": "Balanced single-hand blade."},
    "greatsword": {"slot": "weapon", "material": "steel", "mass_kg": 3.2, "shape": "polygon", "length_m": 1.35, "width_m": 0.12, "thickness_m": 0.009, "damage_multiplier": 2.5, "durability": 150.0, "attack_style": "heavy_slash", "description": "Large two-hand blade; heavier and slower to accelerate."},
    "dagger": {"slot": "weapon", "material": "steel", "mass_kg": 0.45, "shape": "polygon", "length_m": 0.28, "width_m": 0.035, "thickness_m": 0.004, "damage_multiplier": 1.45, "durability": 70.0, "attack_style": "thrust", "description": "Short blade for close-range thrusts."},
    "axe": {"slot": "weapon", "material": "steel", "mass_kg": 2.0, "shape": "polygon", "length_m": 0.82, "width_m": 0.18, "thickness_m": 0.009, "damage_multiplier": 2.0, "durability": 115.0, "attack_style": "chop", "description": "Weighted cutting head on a haft."},
    "warhammer": {"slot": "weapon", "material": "steel", "mass_kg": 2.8, "shape": "polygon", "length_m": 0.92, "width_m": 0.15, "thickness_m": 0.03, "damage_multiplier": 2.2, "durability": 140.0, "attack_style": "blunt", "description": "Blunt impact weapon."},
    "mace": {"slot": "weapon", "material": "steel", "mass_kg": 1.7, "shape": "polygon", "length_m": 0.72, "width_m": 0.12, "thickness_m": 0.025, "damage_multiplier": 1.7, "durability": 110.0, "attack_style": "blunt", "description": "Compact weighted impact weapon."},
    "spear": {"slot": "weapon", "material": "steel", "mass_kg": 1.8, "shape": "segment", "length_m": 1.8, "width_m": 0.05, "thickness_m": 0.006, "damage_multiplier": 1.9, "durability": 100.0, "attack_style": "pierce", "description": "Long reach thrusting weapon."},
    "javelin": {"slot": "weapon", "material": "wood", "mass_kg": 0.8, "shape": "segment", "length_m": 1.7, "width_m": 0.035, "thickness_m": 0.004, "damage_multiplier": 1.6, "durability": 65.0, "attack_style": "thrown_pierce", "description": "Light throwing spear."},
    "staff": {"slot": "weapon", "material": "oak", "mass_kg": 1.0, "shape": "segment", "length_m": 1.5, "width_m": 0.035, "thickness_m": 0.035, "damage_multiplier": 1.15, "durability": 90.0, "attack_style": "blunt", "description": "Wooden staff; can be reshaped or imbued by a spell."},
    "bow": {"slot": "weapon", "material": "wood", "mass_kg": 0.75, "shape": "arc", "length_m": 1.25, "width_m": 0.06, "thickness_m": 0.025, "damage_multiplier": 1.0, "durability": 75.0, "attack_style": "ranged", "launch_speed_m_s": 55.0, "description": "General-purpose bow for launching conjured or crafted arrows."},
    "longbow": {"slot": "weapon", "material": "wood", "mass_kg": 1.1, "shape": "arc", "length_m": 1.8, "width_m": 0.065, "thickness_m": 0.03, "damage_multiplier": 1.15, "durability": 95.0, "attack_style": "ranged", "launch_speed_m_s": 75.0, "description": "Long-limbed bow with greater launch speed, requiring room to handle."},
    "crossbow": {"slot": "weapon", "material": "steel", "mass_kg": 2.4, "shape": "segment", "length_m": 0.72, "width_m": 0.48, "thickness_m": 0.05, "damage_multiplier": 1.2, "durability": 110.0, "attack_style": "ranged", "launch_speed_m_s": 85.0, "description": "Mechanical ranged launcher compatible with bolts and other projectiles."},
    "sling": {"slot": "weapon", "material": "leather", "mass_kg": 0.18, "shape": "segment", "length_m": 0.8, "width_m": 0.025, "thickness_m": 0.01, "damage_multiplier": 0.8, "durability": 45.0, "attack_style": "ranged", "launch_speed_m_s": 38.0, "description": "Lightweight launcher for small conjured stones and sling pellets."},
    "breastplate": {"slot": "body_armour", "material": "steel", "mass_kg": 5.5, "shape": "dome", "length_m": 0.62, "width_m": 0.48, "thickness_m": 0.005, "armour_rating": 16.0, "durability": 180.0, "description": "Torso armour blueprint; coverage is abstracted by the prototype."},
    "greaves": {"slot": "legs", "material": "steel", "mass_kg": 2.8, "shape": "segment", "length_m": 0.52, "width_m": 0.22, "thickness_m": 0.004, "armour_rating": 7.0, "durability": 105.0, "description": "Lower-leg armour."},
    "boots": {"slot": "legs", "material": "leather", "mass_kg": 1.2, "shape": "polygon", "length_m": 0.32, "width_m": 0.12, "thickness_m": 0.03, "armour_rating": 2.0, "durability": 65.0, "description": "Protective boots with low armour and mass."},
    "ingot": {"slot": "resource", "material": "iron", "mass_kg": 1.0, "shape": "polygon", "length_m": 0.16, "width_m": 0.045, "thickness_m": 0.025, "durability": 1.0e9, "description": "A standardised metal stock for forging or transmutation."},
    "metal rod": {"slot": "resource", "material": "iron", "mass_kg": 1.0, "shape": "segment", "length_m": 1.0, "width_m": 0.02, "thickness_m": 0.02, "durability": 1.0e9, "description": "A uniform metal stock for shaping into tools or structural parts."},
    "chain": {"slot": "tool", "material": "steel", "mass_kg": 2.0, "shape": "chain", "length_m": 2.0, "width_m": 0.025, "thickness_m": 0.012, "durability": 85.0, "description": "Conjured physical chain for restraint or utility use."},
    "grapple arrow": {"slot": "projectile", "material": "steel", "mass_kg": 0.075, "shape": "projectile", "length_m": 0.78, "width_m": 0.02, "thickness_m": 0.02, "damage_multiplier": 0.75, "durability": 14.0, "payload": "anchor", "attack_style": "restrain", "description": "Arrow with an anchoring payload for temporary restraint."},
    "net arrow": {"slot": "projectile", "material": "wood", "mass_kg": 0.11, "shape": "projectile", "length_m": 0.72, "width_m": 0.035, "thickness_m": 0.035, "damage_multiplier": 0.5, "durability": 10.0, "payload": "net", "attack_style": "binding", "description": "Low-damage arrow carrying a short-lived binding net effect."},
    "acid arrow": {"slot": "projectile", "material": "wood", "mass_kg": 0.09, "shape": "projectile", "length_m": 0.72, "width_m": 0.025, "thickness_m": 0.025, "damage_multiplier": 0.65, "durability": 9.0, "payload": "acid", "attack_style": "corrosion", "description": "Arrow that corrodes worn armour on impact in the game model."},
    "shield": {"slot": "shield", "material": "steel", "mass_kg": 4.5, "shape": "shield", "length_m": 0.65, "width_m": 0.48, "thickness_m": 0.008, "armour_rating": 16.0, "durability": 160.0, "description": "Hand-held defensive shield."},
    "buckler": {"slot": "shield", "material": "steel", "mass_kg": 1.6, "shape": "disc", "length_m": 0.34, "width_m": 0.34, "thickness_m": 0.006, "armour_rating": 8.0, "durability": 90.0, "description": "Small shield with low weight and coverage."},
    "armour": {"slot": "body_armour", "material": "steel", "mass_kg": 7.0, "shape": "polygon", "length_m": 0.9, "width_m": 0.55, "thickness_m": 0.004, "armour_rating": 18.0, "durability": 220.0, "description": "Generic wearable body armour; coverage is abstracted by the prototype."},
    "armor": {"slot": "body_armour", "material": "steel", "mass_kg": 7.0, "shape": "polygon", "length_m": 0.9, "width_m": 0.55, "thickness_m": 0.004, "armour_rating": 18.0, "durability": 220.0, "description": "Alias of armour."},
    "plate armour": {"slot": "body_armour", "material": "steel", "mass_kg": 16.0, "shape": "polygon", "length_m": 1.0, "width_m": 0.6, "thickness_m": 0.006, "armour_rating": 30.0, "durability": 330.0, "description": "Heavy plate protection with substantial weight."},
    "chainmail": {"slot": "body_armour", "material": "steel", "mass_kg": 9.0, "shape": "chain", "length_m": 0.95, "width_m": 0.55, "thickness_m": 0.004, "armour_rating": 21.0, "durability": 250.0, "description": "Flexible linked-metal armour."},
    "helmet": {"slot": "head", "material": "steel", "mass_kg": 1.8, "shape": "dome", "length_m": 0.28, "width_m": 0.24, "thickness_m": 0.004, "armour_rating": 8.0, "durability": 110.0, "description": "Head protection; coverage is abstracted."},
    "gauntlets": {"slot": "hands", "material": "steel", "mass_kg": 1.4, "shape": "polygon", "length_m": 0.32, "width_m": 0.15, "thickness_m": 0.004, "armour_rating": 4.0, "durability": 90.0, "description": "Hand and forearm protection."},
    "arrow": {"slot": "projectile", "material": "wood", "mass_kg": 0.035, "shape": "projectile", "length_m": 0.72, "width_m": 0.008, "thickness_m": 0.008, "damage_multiplier": 1.15, "durability": 12.0, "payload": "none", "attack_style": "pierce", "description": "Reusable basic arrow shaft."},
    "bolt": {"slot": "projectile", "material": "steel", "mass_kg": 0.025, "shape": "projectile", "length_m": 0.22, "width_m": 0.01, "thickness_m": 0.01, "damage_multiplier": 1.1, "durability": 10.0, "payload": "none", "attack_style": "pierce", "description": "Short crossbow bolt."},
    "bola arrow": {"slot": "projectile", "material": "wood", "mass_kg": 0.08, "shape": "projectile", "length_m": 0.72, "width_m": 0.02, "thickness_m": 0.02, "damage_multiplier": 0.75, "durability": 12.0, "payload": "binding", "attack_style": "binding", "description": "Arrow carrying a binding payload."},
    "shock arrow": {"slot": "projectile", "material": "copper", "mass_kg": 0.05, "shape": "projectile", "length_m": 0.72, "width_m": 0.012, "thickness_m": 0.012, "damage_multiplier": 1.0, "durability": 10.0, "payload": "shock", "attack_style": "pierce", "description": "Conductive arrow that applies a short shock effect on contact."},
    "smoke arrow": {"slot": "projectile", "material": "wood", "mass_kg": 0.09, "shape": "projectile", "length_m": 0.72, "width_m": 0.025, "thickness_m": 0.025, "damage_multiplier": 0.7, "durability": 10.0, "payload": "smoke", "attack_style": "obscurant", "description": "Arrow that creates a temporary obscurant marker on impact."},
    "flare arrow": {"slot": "projectile", "material": "wood", "mass_kg": 0.05, "shape": "projectile", "length_m": 0.72, "width_m": 0.012, "thickness_m": 0.012, "damage_multiplier": 0.8, "durability": 10.0, "payload": "flare", "attack_style": "illumination", "description": "Arrow that marks an area as illuminated for perception adapters."},
    "anchor arrow": {"slot": "projectile", "material": "wood", "mass_kg": 0.06, "shape": "projectile", "length_m": 0.72, "width_m": 0.014, "thickness_m": 0.014, "damage_multiplier": 0.9, "durability": 10.0, "payload": "anchor", "attack_style": "restrain", "description": "Arrow that briefly anchors a target in the world simulation."},
    "burst arrow": {"slot": "projectile", "material": "wood", "mass_kg": 0.12, "shape": "projectile", "length_m": 0.72, "width_m": 0.03, "thickness_m": 0.03, "damage_multiplier": 1.8, "durability": 8.0, "payload": "burst", "attack_style": "burst", "description": "Single-target high-impact payload; area splash is not modelled yet."},
}

_ALIASES = {
    "great sword": "greatsword", "battle axe": "axe", "war hammer": "warhammer",
    "plate armour": "plate armour", "plate armor": "plate armour", "body armour": "armour",
    "body armor": "armour", "mail": "chainmail", "arrows": "arrow", "crossbow bolt": "bolt",
    "binding arrow": "bola arrow", "electric arrow": "shock arrow", "shock bolt": "shock arrow",
    "body plate": "breastplate", "metal ingot": "ingot", "grappling arrow": "grapple arrow",
}


def canonical_item(value: str) -> str | None:
    if not isinstance(value, str):
        return None
    key = " ".join(value.casefold().replace("_", " ").split())
    key = _ALIASES.get(key, key)
    return key if key in _BLUEPRINTS else None


def blueprint(value: str) -> dict[str, Any] | None:
    key = canonical_item(value)
    if key is None:
        return None
    return {"name": key, **deepcopy(_BLUEPRINTS[key])}


def all_blueprints() -> list[dict[str, Any]]:
    return [blueprint(key) for key in sorted(_BLUEPRINTS)]
