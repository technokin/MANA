"""Bounded body, anatomy, blood, life-state, and enhancement mechanics.

This is a fictional game simulation model. It makes organs and biological
systems mechanically addressable without claiming to be a medical simulator.
Magical spells compose these operations; this module is the body-state model.
"""
from __future__ import annotations

import copy
import math
from typing import Any

from ..errors import MagicErrorML, PhysicsErrorML, TypeErrorML
from ..units import DIMENSIONLESS, ENERGY, K, S, VELOCITY, Quantity
from ..physics import C, Vector3, kinetic_energy, require_2d_world_vector
from .anatomy_data import MAX_BODY_STRUCTURES, ORGANS as _ANATOMY_ORGANS, SPECIES as _ANATOMY_SPECIES, SYSTEMS as _ANATOMY_SYSTEMS

_ORGANS: dict[str, dict[str, str]] = {
    "brain": {"system": "nervous", "role": "awareness, memory hooks, and reflex integration"},
    "brainstem": {"system": "nervous", "role": "breathing, wakefulness, and autonomic reflexes"},
    "cerebellum": {"system": "nervous", "role": "coordination, balance, and motor learning"},
    "autonomic_nerves": {"system": "nervous", "role": "automatic control of circulation, breathing, and digestion"},
    "spinal_cord": {"system": "nervous", "role": "signal relay between brain and body"},
    "peripheral_nerves": {"system": "nervous", "role": "movement and sensory signalling"},
    "heart": {"system": "circulatory", "role": "circulation and sustained exertion"},
    "heart_valves": {"system": "circulatory", "role": "one-way control of blood flow through the heart"},
    "blood_plasma": {"system": "circulatory", "role": "fluid phase of blood for transport and volume balance"},
    "red_blood_cells": {"system": "circulatory", "role": "oxygen transport capacity"},
    "arteries": {"system": "circulatory", "role": "blood delivery away from the heart"},
    "veins": {"system": "circulatory", "role": "blood return toward the heart"},
    "capillaries": {"system": "circulatory", "role": "exchange between blood and tissues"},
    "blood": {"system": "circulatory", "role": "oxygen and nutrient transport; magical blood operations"},
    "lungs": {"system": "respiratory", "role": "gas exchange and endurance"},
    "diaphragm": {"system": "respiratory", "role": "breathing mechanics"},
    "air_sacs": {"system": "respiratory", "role": "specialised airflow structures in avian forms"},
    "liver": {"system": "metabolic", "role": "metabolism and toxin handling"},
    "kidneys": {"system": "excretory", "role": "fluid balance and waste filtering"},
    "bladder": {"system": "excretory", "role": "fluid storage"},
    "stomach": {"system": "digestive", "role": "initial digestion"},
    "intestines": {"system": "digestive", "role": "nutrient and fluid absorption"},
    "pancreas": {"system": "digestive", "role": "digestive and metabolic regulation"},
    "spleen": {"system": "immune", "role": "blood filtering and immune support"},
    "bone_marrow": {"system": "blood_production", "role": "blood-cell production"},
    "immune_system": {"system": "immune", "role": "resistance and recovery from biological threats"},
    "lymphatic_system": {"system": "lymphatic", "role": "fluid return and immune transport"},
    "lymph_nodes": {"system": "immune", "role": "filtering lymph and supporting immune responses"},
    "tendons": {"system": "musculoskeletal", "role": "transfer force from muscles to skeleton"},
    "ligaments": {"system": "musculoskeletal", "role": "stabilise joints and constrain movement"},
    "connective_tissue": {"system": "musculoskeletal", "role": "support and connect organs and tissues"},
    "stem_cells": {"system": "blood_production", "role": "abstract repair reserve used by regeneration spells"},
    "endocrine_system": {"system": "endocrine", "role": "slow chemical regulation"},
    "thyroid": {"system": "endocrine", "role": "metabolic regulation"},
    "adrenal_glands": {"system": "endocrine", "role": "stress response"},
    "skeletal_muscles": {"system": "musculoskeletal", "role": "force production and movement"},
    "skeleton": {"system": "musculoskeletal", "role": "structural support and load transfer"},
    "cartilage": {"system": "musculoskeletal", "role": "joint support and flexible structure"},
    "skin": {"system": "integumentary", "role": "outer protection and temperature interface"},
    "eyes": {"system": "sensory", "role": "visual perception"},
    "ears": {"system": "sensory", "role": "hearing"},
    "inner_ear": {"system": "sensory", "role": "balance and orientation"},
    "tongue": {"system": "sensory", "role": "taste and speech articulation"},
    "wings": {"system": "locomotion", "role": "flight surface in compatible body forms"},
    "tail": {"system": "locomotion", "role": "balance or locomotion in compatible forms"},
    "gills": {"system": "respiratory", "role": "underwater gas exchange in compatible forms"},
    "fins": {"system": "locomotion", "role": "underwater movement in compatible forms"},
    "venom_gland": {"system": "specialised", "role": "fictional species-specific toxin generation"},
    "reproductive_system": {"system": "reproductive", "role": "species-specific reproduction; not needed by most combat calculations"},
}

_BODY_SYSTEMS: dict[str, tuple[str, ...]] = {
    "nervous": ("brain", "brainstem", "cerebellum", "spinal_cord", "peripheral_nerves", "autonomic_nerves"),
    "circulatory": ("heart", "heart_valves", "arteries", "veins", "capillaries", "blood", "blood_plasma", "red_blood_cells"),
    "respiratory": ("lungs", "diaphragm", "air_sacs", "gills"),
    "digestive": ("stomach", "intestines", "pancreas", "liver"),
    "excretory": ("kidneys", "bladder", "liver"),
    "musculoskeletal": ("skeletal_muscles", "skeleton", "cartilage", "tendons", "ligaments", "connective_tissue"),
    "integumentary": ("skin",),
    "sensory": ("eyes", "ears", "inner_ear", "tongue"),
    "immune": ("immune_system", "spleen", "lymphatic_system", "lymph_nodes"),
    "lymphatic": ("lymphatic_system", "lymph_nodes", "spleen"),
    "endocrine": ("endocrine_system", "thyroid", "adrenal_glands", "pancreas"),
    "blood_production": ("bone_marrow", "stem_cells", "blood", "red_blood_cells"),
    "locomotion": ("skeletal_muscles", "skeleton", "wings", "tail", "fins"),
    "reproductive": ("reproductive_system",),
}

_CORE_ORGANS = tuple(name for name in _ORGANS if name not in {"wings", "tail", "air_sacs", "gills", "fins", "venom_gland"})
_FORM_ORGANS: dict[str, tuple[str, ...]] = {
    "human": _CORE_ORGANS,
    "humanoid": _CORE_ORGANS,
    "knight": _CORE_ORGANS,
    "beast": _CORE_ORGANS + ("tail",),
    "bird": _CORE_ORGANS + ("wings", "air_sacs"),
    "serpent": tuple(name for name in _CORE_ORGANS if name not in {"skeletal_muscles", "skeleton"}) + ("skeletal_muscles", "skeleton", "tail", "venom_gland"),
    "aquatic": _CORE_ORGANS + ("gills", "fins"),
}
_TRAITS = {"strength", "speed", "endurance", "durability", "senses", "reflexes", "regeneration", "recovery"}
_BLOOD_MODES = {"bind", "draw", "clot", "restore", "purge"}
_MAX_ENHANCEMENTS = 16
_MAX_BLOOD_VOLUME_L = 8.0


def _marked(function):
    function.__mana_runtime_operation__ = True
    return function


def _living(value: Any, operation: str):
    from ..runtime import MagicObject
    if not isinstance(value, MagicObject):
        raise TypeErrorML(f"physiology.{operation}() expects a MANA world object")
    props = value.properties
    if not (props.get("living") or props.get("is_being") or props.get("is_summoned") or props.get("targetable") or props.get("life_state") in {"dead", "undead"}):
        raise MagicErrorML(f"physiology.{operation}() requires a living being or target profile")
    if not props.get("active", True):
        raise MagicErrorML(f"physiology.{operation}() cannot affect an inactive being")
    return value


def _check_mutation(runtime: Any, operation: str) -> None:
    if getattr(runtime, "_pure_call_depth", 0):
        raise MagicErrorML(f"physiology.{operation}() changes body state; call it inside an executable spell")


def _require_alive(obj: Any, operation: str) -> None:
    state = str(obj.properties.get("life_state", "alive")).casefold()
    if state != "alive" or float(obj.properties.get("hp", 1.0) or 0.0) <= 0:
        raise MagicErrorML(f"physiology.{operation}() requires a living, conscious-capable body; current state is {state}")


def _finite_range(value: Any, label: str, low: float, high: float) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeErrorML(f"physiology.{label} must be a finite number")
    number = float(value)
    if not math.isfinite(number) or not low <= number <= high:
        raise PhysicsErrorML(f"physiology.{label} must be between {low:g} and {high:g}")
    return number


# Species-only anatomy names are indexed once at import time. This used to scan
# every stock template each time physiology inspected an unshared structure; with
# hundreds of structures across many clades that cost grew with both catalogue
# size and spell activity. Preserve first-template precedence and its system choice.
_SPECIES_STRUCTURE_METADATA: dict[str, dict[str, str]] = {}
for _profile_name, _species_profile in _ANATOMY_SPECIES.items():
    _systems_for_profile = _species_profile.get("systems", {})
    for _structure_name in (*_species_profile.get("organ_names", []), *_species_profile.get("special_organs", [])):
        if _structure_name in _SPECIES_STRUCTURE_METADATA:
            continue
        _system_name = next((sys for sys, entries in _systems_for_profile.items() if _structure_name in entries), "magical_specialisation")
        _SPECIES_STRUCTURE_METADATA[_structure_name] = {
            "system": _system_name,
            "label": str(_species_profile.get("label", "selected")),
        }


def _organ_metadata(name: str, obj: Any = None) -> dict[str, Any]:
    """Resolve a structure from legacy physiology, the rich anatomy catalogue,
    or existing per-entity metadata without inventing an arbitrary organ.
    """
    if name in _ORGANS:
        return dict(_ORGANS[name])
    if name in _ANATOMY_ORGANS:
        return dict(_ANATOMY_ORGANS[name])
    # Species-only entries stay addressable, but use the precomputed stock index
    # instead of traversing the entire species catalogue on each physiology call.
    indexed = _SPECIES_STRUCTURE_METADATA.get(name)
    if indexed is not None:
        return {"name": name, "system": indexed["system"],
                "role": f"Species-specific structure in the {indexed['label']} anatomy profile"}
    if obj is not None:
        anatomy = getattr(obj, "properties", {}).get("anatomy", {})
        if isinstance(anatomy, dict) and isinstance(anatomy.get(name), dict):
            entry = anatomy[name]
            return {"name": name, "system": entry.get("system", "magical_specialisation"),
                    "role": entry.get("role", "User-defined anatomical structure")}
    return {"name": name, "system": "magical_specialisation", "role": "User-defined anatomical structure"}


def _initialize(obj: Any) -> None:
    """Initialise only the selected species structures when anatomy has been bound.

    Legacy objects retain the original standard organ set. Catalogue-bound animals
    no longer acquire mammalian organs (for example, a diaphragm in a snake) merely
    because physiology first inspects them.
    """
    props = obj.properties
    anatomy = props.get("anatomy")
    if not isinstance(anatomy, dict):
        anatomy = {}
    requested = props.get("body_model_organs")
    if isinstance(requested, list) and requested:
        names = list(dict.fromkeys(name for name in requested[:MAX_BODY_STRUCTURES] if isinstance(name, str) and name))
        # Keep explicitly tracked structures in the selected body model. Old data
        # may have an injury on one of these even if it has since been removed.
        names.extend(name for name in anatomy if isinstance(name, str) and name not in names and len(names) < MAX_BODY_STRUCTURES)
    else:
        names = list(_ORGANS)
    for name in names:
        meta = _organ_metadata(name, obj)
        entry = anatomy.get(name)
        if not isinstance(entry, dict):
            entry = {"system": meta.get("system", "magical_specialisation"),
                     "role": meta.get("role", "Anatomical structure"), "integrity": 1.0}
            for field in ("kind", "bone_region", "bone_group"):
                if field in meta:
                    entry[field] = meta[field]
            anatomy[name] = entry
        else:
            entry.setdefault("system", meta.get("system", "magical_specialisation"))
            entry.setdefault("role", meta.get("role", "Anatomical structure"))
            for field in ("kind", "bone_region", "bone_group"):
                if field in meta:
                    entry.setdefault(field, meta[field])
            raw = entry.get("integrity", 1.0)
            try:
                number = float(raw)
                entry["integrity"] = min(1.0, max(0.0, number)) if math.isfinite(number) else 1.0
            except (TypeError, ValueError, OverflowError):
                entry["integrity"] = 1.0
    props["anatomy"] = anatomy
    traits = props.get("body_traits")
    if not isinstance(traits, dict):
        traits = {"strength": 1.0, "speed": 1.0, "endurance": 1.0, "durability": 1.0,
                  "senses": 1.0, "reflexes": 1.0, "regeneration": 0.0, "recovery": 1.0}
    else:
        defaults = {"strength": 1.0, "speed": 1.0, "endurance": 1.0, "durability": 1.0,
                    "senses": 1.0, "reflexes": 1.0, "regeneration": 0.0, "recovery": 1.0}
        for key, value in defaults.items():
            traits.setdefault(key, value)
    props["body_traits"] = traits
    props.setdefault("body_enhancements", [])
    hp = props.get("hp", 100.0)
    max_hp = props.get("max_hp", 100.0)
    try:
        max_hp = float(max_hp if max_hp is not None else 100.0)
        hp = float(hp if hp is not None else max_hp)
    except (TypeError, ValueError, OverflowError):
        hp, max_hp = 100.0, 100.0
    if not math.isfinite(max_hp) or max_hp <= 0:
        max_hp = 100.0
    if not math.isfinite(hp):
        hp = max_hp
    props.setdefault("max_hp", max_hp)
    props.setdefault("hp", min(max_hp, max(0.0, hp)))
    props.setdefault("life_state", "undead" if props.get("is_undead") else ("dead" if hp <= 0 else "alive"))
    props.setdefault("is_dead", props.get("life_state") == "dead")
    props.setdefault("consciousness", "awake" if props.get("life_state") == "alive" else str(props.get("life_state")))
    props.setdefault("body_form", "human")
    props.setdefault("body_form_traits", {"strength": 1.0, "speed": 1.0, "endurance": 1.0, "durability": 1.0, "senses": 1.0, "reflexes": 1.0, "regeneration": 1.0, "recovery": 1.0})
    props.setdefault("blood_volume_l", 5.0)
    props.setdefault("blood_volume_max_l", 5.0)
    props.setdefault("blood_loss_rate_lps", 0.0)
    props.setdefault("externalized_blood_l", 0.0)
    props.setdefault("oxygen_saturation", 0.98)
    props.setdefault("body_temperature_c", 37.0)
    props.setdefault("stamina", 100.0)
    props.setdefault("max_stamina", 100.0)
    props.setdefault("toxicity", 0.0)
    props.setdefault("blood_control", None)
    props.setdefault("blood_clotted", False)
    props.setdefault("soul_state", "present")
    props.setdefault("revival_count", 0)
    props.setdefault("death_count", 0)
    props.setdefault("body_model_initialized", True)


def _ensure_organ_tracked(obj: Any, name: str) -> None:
    """Create a validated organ-state slot so newly catalogued structures can be targeted."""
    props = obj.properties
    anatomy = props.setdefault("anatomy", {})
    if name not in anatomy:
        if len(anatomy) >= MAX_BODY_STRUCTURES:
            raise PhysicsErrorML("an entity can track at most 1024 anatomical structures")
        meta = _organ_metadata(name, obj)
        anatomy[name] = {"system": meta.get("system", "magical_specialisation"),
                         "role": meta.get("role", "Anatomical structure"), "integrity": 1.0}
    names = props.setdefault("body_model_organs", [])
    if isinstance(names, list) and name not in names and len(names) < MAX_BODY_STRUCTURES:
        names.append(name)
    system = anatomy[name].get("system", "magical_specialisation")
    systems = props.setdefault("body_systems", {})
    if isinstance(systems, dict):
        members = systems.setdefault(system, [])
        if isinstance(members, list) and name not in members and len(members) < 256:
            members.append(name)


def _organ_integrity(obj: Any, name: str) -> float:
    entry = obj.properties.get("anatomy", {}).get(name, {})
    try:
        number = float(entry.get("integrity", 1.0))
        return min(1.0, max(0.0, number)) if math.isfinite(number) else 1.0
    except (TypeError, ValueError, AttributeError):
        return 1.0




def _mean_structure_integrity(obj: Any, names: tuple[str, ...] | list[str]) -> float | None:
    """Mean integrity of structures present in this creature; None means absent."""
    anatomy = obj.properties.get("anatomy", {})
    if not isinstance(anatomy, dict):
        return None
    values = []
    for name in names:
        if name in anatomy:
            values.append(_organ_integrity(obj, name))
    return sum(values) / len(values) if values else None


def _body_health_structure(obj: Any, *candidates: str, default: float = 1.0) -> float:
    """Use the first anatomical alternatives actually present in this body model."""
    anatomy = obj.properties.get("anatomy", {})
    if isinstance(anatomy, dict):
        for name in candidates:
            if name in anatomy:
                return _organ_integrity(obj, name)
    return default


def _body_health_group(obj: Any, candidates: tuple[str, ...], *, default: float = 1.0) -> float:
    """Aggregate integrity over whichever clade-specific structures exist."""
    anatomy = obj.properties.get("anatomy", {})
    if not isinstance(anatomy, dict):
        return default
    values = [_organ_integrity(obj, name) for name in candidates if name in anatomy]
    return min(values) if values else default


def _named_bone_integrity(obj: Any) -> float | None:
    anatomy = obj.properties.get("anatomy", {})
    if not isinstance(anatomy, dict):
        return None
    values = [
        _bounded_integrity(entry.get("integrity", 1.0))
        for entry in anatomy.values()
        if isinstance(entry, dict) and entry.get("kind") == "individual_bone"
    ]
    return sum(values) / len(values) if values else None

def refresh_effective_properties(obj: Any, now: float) -> None:
    """Recalculate trait multipliers from active enhancements and organ integrity."""
    props = obj.properties
    effects = props.get("body_enhancements")
    if not isinstance(effects, list):
        return
    effects[:] = [entry for entry in effects if float(entry.get("until", 0)) > now]
    props.setdefault("strength_multiplier_base", float(props.get("strength_multiplier", 1.0)))
    props.setdefault("body_damage_reduction_base", float(props.get("body_damage_reduction", 0.0)))
    props.setdefault("regeneration_rate_hp_s_base", float(props.get("regeneration_rate_hp_s", 0.0)))
    props.setdefault("movement_speed_multiplier_base", float(props.get("movement_speed_multiplier", 1.0)))
    props.setdefault("endurance_multiplier_base", float(props.get("endurance_multiplier", 1.0)))
    props.setdefault("sense_multiplier_base", float(props.get("sense_multiplier", 1.0)))
    props.setdefault("reflex_multiplier_base", float(props.get("reflex_multiplier", 1.0)))
    props.setdefault("recovery_multiplier_base", float(props.get("recovery_multiplier", 1.0)))

    factors = {trait: 1.0 for trait in _TRAITS}
    regen_bonus = 0.0
    for effect in effects:
        trait, factor = effect.get("trait"), float(effect.get("factor", 1.0))
        if trait in factors:
            factors[trait] = min(10.0, factors[trait] * factor)
        if trait == "regeneration":
            regen_bonus += 0.35 * max(0.0, factor - 1.0)
    anatomy = props.get("anatomy", {})
    # Different body plans transmit force through different structures. Resolve
    # an actually present analogue rather than making worms, spiders, or sharks
    # depend on a missing mammalian skeleton/muscle key.
    muscle_health = max(0.1, _body_health_structure(
        obj, "skeletal_muscles", "muscle_tissue", "body_wall_muscles",
        "longitudinal_muscles", "circular_muscles", "mantle", default=1.0))
    skeleton_health = max(0.1, _body_health_structure(
        obj, "skeleton", "cartilaginous_skeleton", "exoskeleton",
        "hydrostatic_skeleton", "carapace", "vertebral_column", default=1.0))
    named_bone_health = _named_bone_integrity(obj)
    if named_bone_health is not None:
        # Individual fractures affect durability in aggregate without making a single
        # bone injury behave like destruction of the entire skeleton.
        skeleton_health *= 0.75 + 0.25 * named_bone_health
    nerve_health = max(0.1, _body_health_group(
        obj, ("spinal_cord", "ventral_nerve_cord", "distributed_ganglia", "cerebral_ganglia",
              "peripheral_nerves", "autonomic_nervous_system"), default=1.0))
    brain_health = max(0.1, _body_health_structure(
        obj, "brain", "cerebral_ganglia", "distributed_ganglia", "ganglia", default=1.0))
    sense_health = max(0.1, _body_health_group(
        obj, ("eyes", "simple_eyes", "lateral_line", "olfactory_epithelium",
              "vomeronasal_organ", "statocysts", "sensory_epithelium"), default=1.0))
    circulation_health = _body_health_group(
        obj, ("heart", "systemic_heart", "branchial_hearts", "aortic_arches",
              "dorsal_vessel", "hemolymph", "blood"), default=1.0)
    respiration_health = _body_health_group(
        obj, ("lungs", "gills", "skin_cuticle", "air_sacs", "metamorphic_gills",
              "book_lungs", "tracheae"), default=1.0)
    endurance_health = max(0.1, min(circulation_health, respiration_health))
    blood_control = props.get("blood_control")
    if isinstance(blood_control, dict) and blood_control.get("mode") == "bind" and float(blood_control.get("until", 0)) > now:
        intensity = min(1.0, max(0.0, float(blood_control.get("intensity", 0.5))))
        factors["speed"] *= max(0.1, 1.0 - intensity * 0.85)
    if float(props.get("oxygen_saturation", 0.98)) < 0.5:
        factors["endurance"] *= max(0.1, float(props.get("oxygen_saturation", 0.98)) * 2.0)
    durability_factor = max(0.1, factors["durability"] * skeleton_health)
    base_reduction = min(0.9, max(0.0, props["body_damage_reduction_base"]))
    form_traits = props.get("body_form_traits", {})
    if not isinstance(form_traits, dict):
        form_traits = {}
    for trait in factors:
        raw_form_factor = form_traits.get(trait, 1.0)
        try:
            form_factor = min(5.0, max(0.1, float(raw_form_factor))) if math.isfinite(float(raw_form_factor)) else 1.0
        except (TypeError, ValueError, OverflowError):
            form_factor = 1.0
        factors[trait] *= form_factor
    props["strength_multiplier"] = min(10.0, props["strength_multiplier_base"] * factors["strength"] * muscle_health)
    props["body_damage_reduction"] = min(0.9, max(0.0, 1.0 - (1.0 - base_reduction) / durability_factor))
    props["body_damage_taken_multiplier"] = min(5.0, max(0.2, 1.0 / durability_factor))
    props["regeneration_rate_hp_s"] = min(100.0, props["regeneration_rate_hp_s_base"] + regen_bonus)
    props["movement_speed_multiplier"] = min(10.0, props["movement_speed_multiplier_base"] * factors["speed"] * muscle_health * nerve_health)
    props["endurance_multiplier"] = min(10.0, props["endurance_multiplier_base"] * factors["endurance"] * endurance_health)
    props["sense_multiplier"] = min(10.0, props["sense_multiplier_base"] * factors["senses"] * sense_health)
    props["reflex_multiplier"] = min(10.0, props["reflex_multiplier_base"] * factors["reflexes"] * brain_health)
    props["recovery_multiplier"] = min(10.0, props["recovery_multiplier_base"] * factors["recovery"])


def apply_transfigured_form(obj: Any, form: str, *, now: float = 0.0, templates: dict[str, Any] | None = None) -> None:
    """Apply a supported body-form profile to a living entity during transfiguration.

    Shared organs retain their integrity. The previous form's anatomy is retained
    in a small archive so a spell can later restore it without erasing injuries.
    This is a bounded gameplay model, not anatomical reconstruction at cell level.
    """
    props = obj.properties
    life_state = str(props.get("life_state", "alive")).casefold()
    if life_state == "dead" or not (props.get("living") or props.get("is_being") or props.get("is_summoned") or life_state in {"alive", "undead"}):
        return
    normalized = " ".join(str(form).casefold().replace("_", " ").split())
    aliases = {"person": "human", "wizard": "human", "mage": "human", "humanoid": "human", "knight": "human",
               "wolf": "beast", "hound": "beast", "snake": "serpent", "raven": "bird", "eagle": "bird"}
    # Preserve an exact registered species/form name before applying legacy visual
    # aliases. In particular, the stock Eagle profile must not collapse to generic
    # `bird`, because that would discard its anatomy and physical baseline.
    custom_definition = (templates or {}).get(normalized) if isinstance(templates, dict) else None
    if not isinstance(custom_definition, dict):
        normalized = aliases.get(normalized, normalized)
        custom_definition = (templates or {}).get(normalized) if isinstance(templates, dict) else None
    if normalized not in _FORM_ORGANS and not isinstance(custom_definition, dict):
        return
    _initialize(obj)
    current = str(props.get("body_form", "human"))
    archive = props.setdefault("anatomy_form_archive", {})
    if isinstance(archive, dict) and current not in archive and len(archive) < 8:
        archive[current] = copy.deepcopy(props.get("anatomy", {}))
    old = props.get("anatomy", {})
    next_anatomy: dict[str, dict[str, Any]] = {}
    target_organs = tuple(custom_definition.get("organs", ())) if isinstance(custom_definition, dict) else _FORM_ORGANS[normalized]
    for name in target_organs:
        metadata = _organ_metadata(name, obj)
        previous = old.get(name, {}) if isinstance(old, dict) else {}
        next_anatomy[name] = {**metadata, "integrity": _organ_integrity(obj, name)}
        if isinstance(previous, dict):
            for key in ("injury_tags", "condition", "notes"):
                if key in previous:
                    next_anatomy[name][key] = copy.deepcopy(previous[key])
    # Restore a previous anatomy when returning to a cached form, keeping only
    # injuries that belong to the organs in that form.
    if isinstance(archive, dict) and normalized in archive and isinstance(archive[normalized], dict):
        saved = archive[normalized]
        for name in next_anatomy:
            if isinstance(saved.get(name), dict):
                next_anatomy[name]["integrity"] = min(next_anatomy[name]["integrity"], _bounded_integrity(saved[name].get("integrity", 1.0)))
    props["anatomy"] = next_anatomy
    props["body_model_organs"] = list(target_organs)[:MAX_BODY_STRUCTURES]
    new_systems: dict[str, list[str]] = {}
    for organ_name in props["body_model_organs"]:
        organ_meta = _organ_metadata(organ_name, obj)
        new_systems.setdefault(str(organ_meta.get("system", "magical_specialisation")), []).append(organ_name)
    props["body_systems"] = new_systems
    props["anatomy_species_id"] = normalized
    props["body_form"] = normalized
    props["body_type"] = normalized
    props["species"] = (str(custom_definition.get("label", normalized.title())) if isinstance(custom_definition, dict)
                        else (normalized.title() if normalized != "human" else str(props.get("species", "Human"))))
    if isinstance(custom_definition, dict):
        movement_mode = custom_definition.get("movement_mode", "terrestrial")
        trait_factors = custom_definition.get("trait_factors", {})
    else:
        movement_mode = {"bird": "flight-capable", "aquatic": "swim-capable", "serpent": "slither-capable", "beast": "terrestrial", "human": "terrestrial", "humanoid": "terrestrial", "knight": "terrestrial"}.get(normalized, "terrestrial")
        trait_factors = {
            "human": {"strength": 1.0, "speed": 1.0, "endurance": 1.0, "durability": 1.0, "senses": 1.0, "reflexes": 1.0, "regeneration": 1.0, "recovery": 1.0},
            "humanoid": {"strength": 1.0, "speed": 1.0, "endurance": 1.0, "durability": 1.0, "senses": 1.0, "reflexes": 1.0, "regeneration": 1.0, "recovery": 1.0},
            "knight": {"strength": 1.05, "speed": 0.95, "endurance": 1.1, "durability": 1.15, "senses": 1.0, "reflexes": 0.95, "regeneration": 1.0, "recovery": 1.0},
            "beast": {"strength": 1.25, "speed": 1.2, "endurance": 1.2, "durability": 1.15, "senses": 1.3, "reflexes": 1.15, "regeneration": 1.0, "recovery": 1.0},
            "bird": {"strength": 0.7, "speed": 1.4, "endurance": 0.95, "durability": 0.8, "senses": 1.3, "reflexes": 1.3, "regeneration": 1.0, "recovery": 1.0},
            "serpent": {"strength": 0.9, "speed": 1.1, "endurance": 1.0, "durability": 0.85, "senses": 1.25, "reflexes": 1.2, "regeneration": 1.05, "recovery": 1.0},
            "aquatic": {"strength": 1.0, "speed": 1.1, "endurance": 1.25, "durability": 0.95, "senses": 1.1, "reflexes": 1.0, "regeneration": 1.0, "recovery": 1.0},
        }.get(normalized, {})
    allowed_movement = {"terrestrial", "flight-capable", "swim-capable", "slither-capable", "amphibious", "burrowing", "climbing", "gliding", "custom", "stationary"}
    props["movement_mode"] = movement_mode if movement_mode in allowed_movement else "custom"
    if isinstance(custom_definition, dict):
        for field in ("movement_capabilities", "components", "component_profiles", "component_sources", "composition_warnings", "skeleton_type", "thermoregulation", "anatomy_species_id", "systems", "circulation", "respiration", "digestion", "blood", "integument", "reproduction", "simulation"):
            if field in custom_definition:
                value = copy.deepcopy(custom_definition[field])
                if field == "systems" and isinstance(value, dict):
                    value = {system: [name for name in names if name in props["body_model_organs"]]
                             for system, names in value.items() if isinstance(names, list) and any(name in props["body_model_organs"] for name in names)}
                target_field = {
                    "systems": "body_systems", "thermoregulation": "body_thermal_mode",
                    "circulation": "body_circulation_model", "respiration": "body_respiration_model",
                    "digestion": "body_digestion_model", "blood": "body_blood_model",
                    "integument": "body_integument_model", "reproduction": "body_reproduction_model",
                    "simulation": "body_simulation_profile",
                }.get(field, field)
                if field == "thermoregulation":
                    value = "ectothermic" if "ectotherm" in str(value).casefold() else "endothermic" if "endotherm" in str(value).casefold() else "custom"
                props[target_field] = value
    trait_archive = props.setdefault("body_form_traits_archive", {})
    if isinstance(trait_archive, dict):
        if current != normalized and current not in trait_archive and len(trait_archive) < 8:
            trait_archive[current] = copy.deepcopy(props.get("body_form_traits", {}))
        if normalized in trait_archive:
            trait_factors = trait_archive[normalized]
    props["body_form_traits"] = copy.deepcopy(trait_factors) if isinstance(trait_factors, dict) else {}
    props["last_body_transfiguration"] = normalized
    refresh_effective_properties(obj, now)


def _bounded_integrity(value: Any) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError, OverflowError):
        return 1.0
    return min(1.0, max(0.0, number)) if math.isfinite(number) else 1.0


def _system_map(obj: Any) -> dict[str, list[str]]:
    result = {name: list(entries) for name, entries in _BODY_SYSTEMS.items()}
    body_systems = obj.properties.get("body_systems", {})
    if isinstance(body_systems, dict):
        for name, entries in body_systems.items():
            if isinstance(name, str) and isinstance(entries, list):
                clean = [value for value in entries[:MAX_BODY_STRUCTURES] if isinstance(value, str)]
                if clean:
                    result[name] = clean
    return result


def _systems(obj: Any) -> dict[str, float]:
    anatomy = obj.properties.get("anatomy", {})
    if not isinstance(anatomy, dict):
        return {}
    result = {}
    for system, names in _system_map(obj).items():
        present = [name for name in names if name in anatomy]
        if present:
            result[system] = round(sum(_organ_integrity(obj, name) for name in present) / len(present), 4)
    return result


def _body_status(props: dict[str, Any]) -> str:
    state = str(props.get("life_state", "alive")).casefold()
    if state in {"dead", "undead"}:
        return state
    volume = max(0.0, float(props.get("blood_volume_l", 5.0)))
    maximum = max(0.01, float(props.get("blood_volume_max_l", 5.0)))
    remaining = volume / maximum
    oxygen = float(props.get("oxygen_saturation", 0.98))
    if remaining <= 0.24 or oxygen <= 0.2:
        return "critical"
    if remaining <= 0.48 or oxygen <= 0.5:
        return "unstable"
    if props.get("consciousness") == "unconscious":
        return "unconscious"
    return "stable"


def _die(runtime: Any, obj: Any, cause: str) -> dict[str, Any]:
    props = obj.properties
    if props.get("life_state") == "dead":
        return {"life_state": "dead", "already_dead": True}
    props["life_state"] = "dead"
    props["is_dead"] = True
    props["living"] = False
    props["consciousness"] = "dead"
    props["hp"] = 0.0
    props["death_cause"] = cause
    props["death_time"] = runtime.elapsed_virtual_time
    props["death_count"] = int(props.get("death_count", 0)) + 1
    props["body_present"] = True
    props["body_condition"] = "corpse"
    # Death removes voluntary biological control but retains the physical object
    # and body state for revival/necromancy operations.
    props["blood_control"] = None
    runtime._observe("entity.changed", entity=runtime._visual_entity(obj), operation="body_died", cause=cause)
    runtime._observe("magic.effect", effect="life_state_changed", state="dead", entity=runtime._visual_entity(obj), cause=cause)
    runtime.emit_event("being_died", obj, cause)
    return {"life_state": "dead", "cause": cause, "death_count": props["death_count"]}


def build_library(runtime: Any) -> dict[str, Any]:
    def organs() -> list[dict[str, str]]:
        return [{"name": name, **meta} for name, meta in _ORGANS.items()]

    def systems() -> dict[str, list[str]]:
        combined = {name: list(entries) for name, entries in _BODY_SYSTEMS.items()}
        for name, meta in _ANATOMY_SYSTEMS.items():
            combined.setdefault(name, [])
        for organ_name, meta in _ANATOMY_ORGANS.items():
            combined.setdefault(meta.get("system", "magical_specialisation"), [])
            if organ_name not in combined[meta.get("system", "magical_specialisation")]:
                combined[meta.get("system", "magical_specialisation")].append(organ_name)
        for organ_name, meta in runtime.custom_anatomy_organs.items():
            system_name = meta.get("system", "magical_specialisation")
            combined.setdefault(system_name, [])
            if organ_name not in combined[system_name]:
                combined[system_name].append(organ_name)
        return combined

    def define_form(name: Any, *, organs: Any, movement_mode: Any = "terrestrial",
                    trait_factors: Any = None, label: Any = None, vital_structures: Any = None,
                    strength: Any = None, speed: Any = None, endurance: Any = None,
                    durability: Any = None, senses: Any = None, reflexes: Any = None,
                    regeneration: Any = None, recovery: Any = None) -> dict[str, Any]:
        """Register a reusable body template. Named trait factors are MANA-friendly;
        ``trait_factors`` remains for Python callers that already provide a mapping.
        """
        _check_mutation(runtime, "define_form")
        if not isinstance(name, str) or not name.strip():
            raise TypeErrorML("physiology.define_form() name must be non-empty text")
        key = " ".join(name.strip().casefold().replace("_", " ").split())
        if len(key) > 48 or not key.replace(" ", "").isalnum() or not key[0].isalpha():
            raise MagicErrorML("physiology.define_form() name must be 1–48 letters, digits, or spaces and start with a letter")
        if key in _FORM_ORGANS or key in runtime.custom_body_forms:
            raise MagicErrorML(f"body form '{key}' is already registered")
        if len(runtime.custom_body_forms) >= 128:
            raise PhysicsErrorML("a runtime can register at most 128 custom body forms")
        if not isinstance(organs, list) or not 3 <= len(organs) <= MAX_BODY_STRUCTURES:
            raise TypeErrorML("physiology.define_form() organs must be a list of 3–1024 known organ names")
        clean_organs = []
        for entry in organs:
            organ = _organ_key(entry, "define_form", runtime=runtime)
            if organ in clean_organs:
                raise MagicErrorML(f"physiology.define_form() organ '{organ}' is duplicated")
            clean_organs.append(organ)
        if vital_structures is not None:
            if (not isinstance(vital_structures, list) or not 1 <= len(vital_structures) <= 16
                    or any(not isinstance(item, str) or not item.strip() for item in vital_structures)):
                raise TypeErrorML("physiology.define_form() vital_structures must be a list of 1–16 structure names")
            required_vitals = list(dict.fromkeys(_organ_key(item, "define_form", runtime=runtime) for item in vital_structures))
            missing_vitals = [item for item in required_vitals if item not in clean_organs]
            if missing_vitals:
                raise MagicErrorML("physiology.define_form() vital_structures must be included in organs")
        else:
            neural_support = {"brain", "brainstem", "cerebral_ganglia", "ventral_nerve_cord", "distributed_ganglia", "ganglia", "nervous_system", "nerve_cord"}
            transport_support = {"heart", "systemic_heart", "branchial_hearts", "aortic_arches", "dorsal_vessel", "hemolymph", "circulatory_vessels", "circulatory_system", "blood"}
            has_neural_support = bool(set(clean_organs) & neural_support)
            has_transport_support = bool(set(clean_organs) & transport_support)
            if not (has_neural_support and has_transport_support):
                raise MagicErrorML("a living body form must include brain and heart or appropriate clade-specific equivalents (such as ganglia and aortic arches/hemolymph); set vital_structures explicitly for a deliberately different fictional life-support model, or use a purpose-built construct for nonliving forms")
            required_vitals = sorted((set(clean_organs) & neural_support) | (set(clean_organs) & transport_support))
        if not isinstance(movement_mode, str) or movement_mode.casefold() not in {"terrestrial", "flight-capable", "swim-capable", "slither-capable", "amphibious", "stationary", "burrowing", "climbing", "gliding", "custom"}:
            raise MagicErrorML("physiology.define_form() movement_mode must be terrestrial, flight-capable, swim-capable, slither-capable, amphibious, stationary, burrowing, climbing, gliding, or custom")
        if label is None:
            display = key.title()
        elif isinstance(label, str) and label.strip() and len(label.strip()) <= 64:
            display = label.strip()
        else:
            raise TypeErrorML("physiology.define_form() label must be non-empty text up to 64 characters")
        defaults = {"strength": 1.0, "speed": 1.0, "endurance": 1.0, "durability": 1.0,
                    "senses": 1.0, "reflexes": 1.0, "regeneration": 1.0, "recovery": 1.0}
        requested: dict[str, Any] = {}
        if trait_factors is not None:
            if not isinstance(trait_factors, dict):
                raise TypeErrorML("physiology.define_form() trait_factors must be a dictionary when called from Python")
            for trait, factor in trait_factors.items():
                if not isinstance(trait, str) or trait.casefold() not in _TRAITS:
                    raise MagicErrorML(f"unknown body trait '{trait}' in physiology.define_form()")
                requested[trait.casefold()] = factor
        # These named arguments are deliberately exposed for MANA source: MANA
        # does not need Python dictionary literal syntax to describe a body form.
        for trait, factor in (("strength", strength), ("speed", speed), ("endurance", endurance),
                              ("durability", durability), ("senses", senses), ("reflexes", reflexes),
                              ("regeneration", regeneration), ("recovery", recovery)):
            if factor is not None:
                if trait in requested:
                    raise MagicErrorML(f"body trait '{trait}' was specified more than once")
                requested[trait] = factor
        for trait, factor in requested.items():
            defaults[trait] = _finite_range(factor, f"define_form() {trait}", 0.1, 5.0)
        record = {"name": key, "label": display, "organs": clean_organs,
                  "movement_mode": movement_mode.casefold(), "vital_structures": required_vitals,
                  "trait_factors": defaults,
                  "modeling_note": "A form template defines anatomy and trait priors; only physiology and movement rules implemented by the runtime are dynamically simulated."}
        runtime.custom_body_forms[key] = copy.deepcopy(record)
        runtime._observe("world.changed", operation="body_form_defined", form={"name": key, "organs": clean_organs, "movement_mode": record["movement_mode"], "vital_structures": required_vitals})
        return copy.deepcopy(record)

    def profile(target: Any) -> dict[str, Any]:
        obj = _living(target, "profile")
        _initialize(obj)
        props = obj.properties
        now = runtime.elapsed_virtual_time
        refresh_effective_properties(obj, now)
        effects = [dict(effect) for effect in props["body_enhancements"] if float(effect.get("until", 0)) > now]
        anatomy = copy.deepcopy(props["anatomy"])
        traits = copy.deepcopy(props["body_traits"])
        multipliers = {name: 1.0 for name in _TRAITS}
        for effect in effects:
            trait, factor = effect.get("trait"), float(effect.get("factor", 1.0))
            if trait in multipliers:
                multipliers[trait] = min(10.0, multipliers[trait] * factor)
        for trait, factor_key in (("strength", "strength_multiplier"), ("speed", "movement_speed_multiplier"),
                                  ("endurance", "endurance_multiplier"), ("durability", "body_damage_taken_multiplier"),
                                  ("senses", "sense_multiplier"), ("reflexes", "reflex_multiplier"),
                                  ("recovery", "recovery_multiplier")):
            if trait == "durability":
                multipliers[trait] *= min(10.0, max(0.1, 1.0 / float(props.get(factor_key, 1.0))))
            else:
                base = float(props.get(factor_key, 1.0))
                multipliers[trait] *= min(10.0, max(0.1, base / max(0.1, float(props.get(f"{factor_key}_base", 1.0)))))
        effective = {name: round(float(value) * multipliers[name], 4) for name, value in traits.items()}
        blood = {
            "volume_l": round(float(props.get("blood_volume_l", 5.0)), 4),
            "max_volume_l": round(float(props.get("blood_volume_max_l", 5.0)), 4),
            "oxygen_saturation": round(float(props.get("oxygen_saturation", 0.98)), 4),
            "loss_rate_lps": round(float(props.get("blood_loss_rate_lps", 0.0)), 4),
            "externalized_volume_l": round(float(props.get("externalized_blood_l", 0.0)), 4),
            "clotted": bool(props.get("blood_clotted", False)),
            "control": copy.deepcopy(props.get("blood_control")),
        }
        velocity = props.get("vel", Vector3(0.0, 0.0, 0.0, VELOCITY))
        if not isinstance(velocity, Vector3) or velocity.dimension != VELOCITY:
            velocity = Vector3(0.0, 0.0, 0.0, VELOCITY)
        movement = {"mode": props.get("movement_mode", "terrestrial"),
                    "motion_energy_mode": props.get("motion_energy_mode", "physical"),
                    "capabilities": list(props.get("movement_capabilities", [])),
                    "velocity_m_s": list(velocity.components),
                    "speed_m_s": round(velocity.magnitude(), 6),
                    "speed_limit_m_s": C,
                    "physics_dimension": "2D x-y world; z must be zero",
                    "strength_multiplier": round(float(props.get("strength_multiplier", 1.0)), 5),
                    "movement_speed_multiplier": round(float(props.get("movement_speed_multiplier", 1.0)), 5)}
        return {
            "name": props.get("display_name", props.get("species", "being")),
            "body_type": props.get("body_type", props.get("body_form", "humanoid")),
            "body_form": props.get("body_form", "human"),
            "body_components": copy.deepcopy(props.get("body_components", [props.get("body_form", "human")])),
            "movement": movement,
            "life_state": props.get("life_state", "alive"),
            "body_status": _body_status(props),
            "consciousness": props.get("consciousness", "awake"),
            "soul_state": props.get("soul_state", "present"),
            "organs": anatomy,
            "systems": _systems(obj),
            "base_traits": traits,
            "effective_traits": effective,
            "active_enhancements": effects,
            "blood": blood,
            "stamina": round(float(props.get("stamina", 100.0)), 3),
            "max_stamina": round(float(props.get("max_stamina", 100.0)), 3),
            "toxicity": round(float(props.get("toxicity", 0.0)), 3),
            "body_temperature_c": round(float(props.get("body_temperature_c", 37.0)), 3),
            "hp": props.get("hp"),
            "max_hp": props.get("max_hp"),
            "revival_count": int(props.get("revival_count", 0)),
            "undead_type": props.get("undead_type"),
        }

    def enhance(target: Any, trait: Any, factor: Any = 1.5, *, duration: Any = Quantity(10, S)) -> dict[str, Any]:
        obj = _living(target, "enhance")
        _require_alive(obj, "enhance")
        _check_mutation(runtime, "enhance")
        if not isinstance(trait, str) or trait.strip().casefold() not in _TRAITS:
            raise MagicErrorML("physiology.enhance() trait must be strength, speed, endurance, durability, senses, reflexes, regeneration, or recovery")
        trait_key = trait.strip().casefold()
        multiplier = _finite_range(factor, "enhance() factor", 1.0, 5.0)
        if not isinstance(duration, Quantity) or duration.dimension != S:
            raise TypeErrorML("physiology.enhance() duration must use seconds")
        seconds = float(duration.value)
        if not math.isfinite(seconds) or not 0 < seconds <= 60:
            raise PhysicsErrorML("physiology.enhance() duration must be greater than 0 and at most 60 seconds")
        _initialize(obj)
        effects = obj.properties["body_enhancements"]
        now = runtime.elapsed_virtual_time
        effects[:] = [entry for entry in effects if float(entry.get("until", 0)) > now]
        if len(effects) >= _MAX_ENHANCEMENTS:
            raise PhysicsErrorML(f"a being can have at most {_MAX_ENHANCEMENTS} concurrent body enhancements")
        props = obj.properties
        for source, base in (("strength_multiplier", "strength_multiplier_base"),
                             ("body_damage_reduction", "body_damage_reduction_base"),
                             ("regeneration_rate_hp_s", "regeneration_rate_hp_s_base"),
                             ("movement_speed_multiplier", "movement_speed_multiplier_base"),
                             ("endurance_multiplier", "endurance_multiplier_base"),
                             ("sense_multiplier", "sense_multiplier_base"),
                             ("reflex_multiplier", "reflex_multiplier_base"),
                             ("recovery_multiplier", "recovery_multiplier_base")):
            props.setdefault(base, float(props.get(source, 1.0)))
        effects.append({"trait": trait_key, "factor": multiplier, "started_at": now, "until": now + seconds})
        refresh_effective_properties(obj, now)
        runtime._observe("magic.effect", effect="body_enhancement", entity=runtime._visual_entity(obj), trait=trait_key, factor=multiplier, duration_s=seconds)
        return profile(obj)

    def propel(target: Any, direction: Any, speed: Any = Quantity(1.0, VELOCITY), *, mode: Any = "physical") -> dict[str, Any]:
        """Set a being's directional movement speed through a shared body primitive.

        This is a general movement operation, not a jump or sprint spell. The same
        call can describe a launch, run, take-off, swim, or other authored movement.
        ``physical`` mode obeys the current body-integrity energy threshold;
        ``arcane`` mode explicitly protects the carrier from its own bulk translational
        kinetic-energy stress while preserving its world velocity and collision path.
        It never makes an ordinary physical object reach c: the top endpoint remains
        just below c for a massive body.
        """
        obj = _living(target, "propel")
        _require_alive(obj, "propel")
        _check_mutation(runtime, "propel")
        if not isinstance(direction, Vector3) or direction.dimension != DIMENSIONLESS:
            raise TypeErrorML("physiology.propel() direction must be a dimensionless vector, e.g. vector3d.direction(0, 1, 0)")
        direction = require_2d_world_vector(direction, "physiology.propel() direction")
        unit_direction = direction.normalized()
        if not isinstance(speed, Quantity) or speed.dimension != VELOCITY:
            raise TypeErrorML("physiology.propel() speed must use velocity units such as 15 m/s")
        requested = float(speed.value)
        if not math.isfinite(requested) or requested <= 0 or requested > C:
            raise PhysicsErrorML("physiology.propel() speed must be greater than 0 and no greater than the speed of light")
        if mode not in {"physical", "arcane"}:
            raise MagicErrorML("physiology.propel() mode must be 'physical' or 'arcane'")
        if obj.properties.get("anchored", False):
            raise MagicErrorML("physiology.propel() cannot propel an anchored being; call unanchor() first")
        _initialize(obj)
        refresh_effective_properties(obj, runtime.elapsed_virtual_time)
        props = obj.properties
        if not isinstance(props.get("mass"), Quantity) or props["mass"].value <= 0:
            raise PhysicsErrorML("physiology.propel() requires a being with positive mass")
        # A massive being may approach but never reach c. Physical mode validates
        # the predicted structural energy before writing state; arcane mode is the
        # explicit opt-in for fictional high-speed travel that protects the carrier.
        speed_factor = min(10.0, max(0.1, float(props.get("movement_speed_multiplier", 1.0))))
        strength_factor = min(10.0, max(0.1, float(props.get("strength_multiplier", 1.0))))
        applied_speed = min(requested * speed_factor * math.sqrt(strength_factor), C * (1.0 - 1e-9))
        proposed = unit_direction * Quantity(applied_speed, VELOCITY)
        old_regime = props.get("motion_energy_mode")
        if mode == "physical":
            # Refresh the threshold without allowing a collapse during preflight.
            runtime.update_integrity(obj, allow_collapse=False)
            break_energy = props.get("integrity_break_energy")
            if isinstance(break_energy, Quantity):
                thermal = props.get("thermal_energy", Quantity(0.0, ENERGY))
                released = props.get("released_energy", Quantity(0.0, ENERGY))
                bound = props.get("bound_energy", Quantity(0.0, ENERGY))
                thermal_j = float(thermal.value) if isinstance(thermal, Quantity) else 0.0
                released_j = float(released.value) if isinstance(released, Quantity) else 0.0
                bound_j = float(bound.value) if isinstance(bound, Quantity) else 0.0
                predicted_k = kinetic_energy(props["mass"], proposed).value
                stabilizers = set(props.get("stabilizers", [])) if isinstance(props.get("stabilizers", []), list) else set()
                # Physical preflight is deliberately conservative: do not let a
                # movement request collapse the caster before reporting a clear error.
                predicted_score = thermal_j + predicted_k + released_j + bound_j
                if "Space" in stabilizers:
                    predicted_score *= 0.80
                if predicted_score >= float(break_energy.value):
                    raise PhysicsErrorML("requested physical movement exceeds this body's current integrity-energy threshold; enhance/reinforce the body or use physiology.propel(..., mode='arcane') for explicitly magical high-speed movement")
            props.pop("motion_energy_mode", None)
        else:
            props["motion_energy_mode"] = "arcane"
        try:
            # The runtime remains the one source of truth for speed validation,
            # momentum, energy ledger, collisions and observer events.
            runtime.op_velocity(obj, proposed)
        except Exception:
            if old_regime is None:
                props.pop("motion_energy_mode", None)
            else:
                props["motion_energy_mode"] = old_regime
            raise
        runtime._observe("entity.changed", entity=runtime._visual_entity(obj), operation="body_propelled",
                         direction=unit_direction.components, requested_speed_m_s=requested,
                         applied_speed_m_s=applied_speed, mode=mode,
                         velocity=proposed.components, speed_m_s=proposed.magnitude())
        return profile(obj)

    def injure(target: Any, organ: Any, severity: Any = 0.25) -> dict[str, Any]:
        obj = _living(target, "injure")
        _require_alive(obj, "injure")
        _check_mutation(runtime, "injure")
        key = _organ_key(organ, "injure", runtime=runtime, obj=obj)
        amount = _finite_range(severity, "injure() severity", 0.000001, 1.0)
        _initialize(obj)
        _ensure_organ_tracked(obj, key)
        organ_state = obj.properties["anatomy"][key]
        organ_state["integrity"] = max(0.0, float(organ_state.get("integrity", 1.0)) - amount)
        obj.properties.setdefault("injury_log", []).append({"organ": key, "severity": amount, "time": runtime.elapsed_virtual_time})
        # Keep the log bounded for long-running simulations.
        del obj.properties["injury_log"][:-128]
        refresh_effective_properties(obj, runtime.elapsed_virtual_time)
        runtime._observe("entity.changed", entity=runtime._visual_entity(obj), operation="organ_injury", organ=key, integrity=organ_state["integrity"])
        return profile(obj)

    def heal(target: Any, organ: Any, amount: Any = 0.25) -> dict[str, Any]:
        obj = _living(target, "heal")
        _check_mutation(runtime, "heal")
        if obj.properties.get("life_state") == "dead":
            raise MagicErrorML("physiology.heal() cannot restore a dead being; use physiology.revive() or necromancy")
        key = _organ_key(organ, "heal", runtime=runtime, obj=obj)
        recovery = _finite_range(amount, "heal() amount", 0.000001, 1.0)
        _initialize(obj)
        _ensure_organ_tracked(obj, key)
        organ_state = obj.properties["anatomy"][key]
        organ_state["integrity"] = min(1.0, float(organ_state.get("integrity", 1.0)) + recovery)
        refresh_effective_properties(obj, runtime.elapsed_virtual_time)
        runtime._observe("entity.changed", entity=runtime._visual_entity(obj), operation="organ_healed", organ=key, integrity=organ_state["integrity"])
        return profile(obj)

    def blood_state(target: Any) -> dict[str, Any]:
        return profile(target)["blood"]

    def manipulate_blood(target: Any, mode: Any = "bind", intensity: Any = 0.5, *,
                         duration: Any = Quantity(3, S), amount_l: Any = None) -> dict[str, Any]:
        """Apply a spell-authored blood-state operation to a living body.

        Modes are bind (temporarily slows voluntary movement), draw (moves blood
        into an externalised pool), clot (stops modelled blood loss), restore
        (restores a bounded volume), and purge (reduces fictional toxin load).
        These are game-world mechanics, not medical procedures.
        """
        obj = _living(target, "manipulate_blood")
        _require_alive(obj, "manipulate_blood")
        _check_mutation(runtime, "manipulate_blood")
        if not isinstance(mode, str) or mode.strip().casefold() not in _BLOOD_MODES:
            raise MagicErrorML("physiology.manipulate_blood() mode must be bind, draw, clot, restore, or purge")
        mode_key = mode.strip().casefold()
        power = _finite_range(intensity, "manipulate_blood() intensity", 0.0, 1.0)
        if not isinstance(duration, Quantity) or duration.dimension != S:
            raise TypeErrorML("physiology.manipulate_blood() duration must use seconds")
        duration_s = float(duration.value)
        if not math.isfinite(duration_s) or not 0 < duration_s <= 60:
            raise PhysicsErrorML("physiology.manipulate_blood() duration must be greater than 0 and no more than 60 seconds")
        _initialize(obj)
        props = obj.properties
        now = runtime.elapsed_virtual_time
        if mode_key == "bind":
            props["blood_control"] = {"mode": "bind", "intensity": power, "started_at": now, "until": now + duration_s}
            props["consciousness"] = "strained" if power > 0.7 else props.get("consciousness", "awake")
        elif mode_key == "draw":
            max_volume = max(0.01, float(props.get("blood_volume_max_l", 5.0)))
            volume = _finite_range(amount_l if amount_l is not None else 0.1 + power * 0.9,
                                   "manipulate_blood() amount_l", 0.01, min(1000.0, max(1.5, max_volume * 0.25)))
            actual = min(volume, float(props.get("blood_volume_l", 5.0)))
            props["blood_volume_l"] = max(0.0, float(props.get("blood_volume_l", 5.0)) - actual)
            external_cap = min(1000.0, max(8.0, max_volume * 1.5))
            props["externalized_blood_l"] = min(external_cap, float(props.get("externalized_blood_l", 0.0)) + actual)
            props["blood_clotted"] = False
            props["blood_loss_rate_lps"] = 0.0  # extraction is a discrete event in this model
            max_hp = float(props.get("max_hp", 100.0) or 100.0)
            props["hp"] = max(0.0, float(props.get("hp", max_hp)) - max_hp * min(0.4, actual / max(0.1, float(props.get("blood_volume_max_l", 5.0))) * 0.4))
            if props["blood_volume_l"] <= 2.0:
                props["consciousness"] = "unconscious"
            if props["blood_volume_l"] <= 0.8 or props["hp"] <= 0:
                _die(runtime, obj, "blood_loss")
            props["last_blood_operation"] = {"mode": mode_key, "amount_l": actual, "time": now}
        elif mode_key == "clot":
            props["blood_loss_rate_lps"] = 0.0
            props["blood_clotted"] = True
            props["blood_control"] = None
        elif mode_key == "restore":
            max_volume = max(0.01, float(props.get("blood_volume_max_l", 5.0)))
            volume = _finite_range(amount_l if amount_l is not None else max(0.1, power * 0.75),
                                   "manipulate_blood() amount_l", 0.01, min(1000.0, max(2.0, max_volume * 0.25)))
            room = max(0.0, float(props.get("blood_volume_max_l", 5.0)) - float(props.get("blood_volume_l", 5.0)))
            restored = min(volume, room)
            props["blood_volume_l"] = min(float(props.get("blood_volume_max_l", 5.0)), float(props.get("blood_volume_l", 5.0)) + restored)
            props["externalized_blood_l"] = max(0.0, float(props.get("externalized_blood_l", 0.0)) - restored)
            props["blood_clotted"] = True
            props["oxygen_saturation"] = min(0.98, float(props.get("oxygen_saturation", 0.98)) + restored * 0.05)
            props["last_blood_operation"] = {"mode": mode_key, "amount_l": restored, "time": now}
        elif mode_key == "purge":
            previous = max(0.0, float(props.get("toxicity", 0.0)))
            props["toxicity"] = max(0.0, previous * (1.0 - power))
        refresh_effective_properties(obj, now)
        runtime._observe("magic.effect", effect="blood_manipulation", entity=runtime._visual_entity(obj), mode=mode_key,
                         intensity=power, blood_volume_l=round(float(props.get("blood_volume_l", 5.0)), 4))
        runtime.emit_event("blood_changed", obj, mode_key, power)
        return profile(obj)

    def injure_system(target: Any, system: Any, severity: Any = 0.15) -> dict[str, Any]:
        """Reduce integrity of each organ participating in a named body system."""
        obj = _living(target, "injure_system")
        _require_alive(obj, "injure_system")
        _check_mutation(runtime, "injure_system")
        if not isinstance(system, str):
            raise TypeErrorML("physiology.injure_system() system must be text")
        key = "_".join(system.strip().casefold().replace("-", " ").split())
        system_map = _system_map(obj)
        if key not in system_map:
            raise MagicErrorML("unknown body system; use physiology.systems() or anatomy.systems(species) to inspect the catalogue")
        amount = _finite_range(severity, "injure_system() severity", 0.000001, 1.0)
        _initialize(obj)
        now = runtime.elapsed_virtual_time
        for organ in system_map[key]:
            if organ in obj.properties["anatomy"]:
                entry = obj.properties["anatomy"][organ]
                entry["integrity"] = max(0.0, float(entry.get("integrity", 1.0)) - amount)
        log = obj.properties.setdefault("injury_log", [])
        log.append({"system": key, "severity": amount, "time": now})
        del log[:-128]
        refresh_effective_properties(obj, now)
        runtime._observe("entity.changed", entity=runtime._visual_entity(obj), operation="body_system_injury", system=key)
        return profile(obj)

    def heal_system(target: Any, system: Any, amount: Any = 0.15) -> dict[str, Any]:
        """Restore integrity across a named system, without exceeding full integrity."""
        obj = _living(target, "heal_system")
        _check_mutation(runtime, "heal_system")
        if obj.properties.get("life_state") == "dead":
            raise MagicErrorML("physiology.heal_system() cannot restore a dead being; use physiology.revive() or necromancy")
        if not isinstance(system, str):
            raise TypeErrorML("physiology.heal_system() system must be text")
        key = "_".join(system.strip().casefold().replace("-", " ").split())
        system_map = _system_map(obj)
        if key not in system_map:
            raise MagicErrorML("unknown body system; use physiology.systems() or anatomy.systems(species) to inspect the catalogue")
        recovery = _finite_range(amount, "heal_system() amount", 0.000001, 1.0)
        _initialize(obj)
        now = runtime.elapsed_virtual_time
        for organ in system_map[key]:
            if organ in obj.properties["anatomy"]:
                entry = obj.properties["anatomy"][organ]
                entry["integrity"] = min(1.0, float(entry.get("integrity", 1.0)) + recovery)
        refresh_effective_properties(obj, now)
        runtime._observe("entity.changed", entity=runtime._visual_entity(obj), operation="body_system_healed", system=key)
        return profile(obj)

    def set_temperature(target: Any, temperature: Any) -> dict[str, Any]:
        """Set a body's simulated internal temperature from an absolute kelvin value."""
        obj = _living(target, "set_temperature")
        _require_alive(obj, "set_temperature")
        _check_mutation(runtime, "set_temperature")
        if not isinstance(temperature, Quantity) or temperature.dimension != K:
            raise TypeErrorML("physiology.set_temperature() temperature must use kelvin (K)")
        kelvin = float(temperature.value)
        if not math.isfinite(kelvin) or not 250.0 <= kelvin <= 400.0:
            raise PhysicsErrorML("physiology.set_temperature() must be between 250 K and 400 K")
        _initialize(obj)
        obj.properties["body_temperature_c"] = kelvin - 273.15
        obj.properties["last_body_temperature_change"] = runtime.elapsed_virtual_time
        runtime._observe("magic.effect", effect="body_temperature_changed", entity=runtime._visual_entity(obj), temperature_k=kelvin)
        return profile(obj)

    def set_toxicity(target: Any, toxicity: Any) -> dict[str, Any]:
        """Set the body's abstract toxin burden for spell effects and metabolism."""
        obj = _living(target, "set_toxicity")
        _require_alive(obj, "set_toxicity")
        _check_mutation(runtime, "set_toxicity")
        amount = _finite_range(toxicity, "set_toxicity() toxicity", 0.0, 1.0)
        _initialize(obj)
        obj.properties["toxicity"] = amount
        runtime._observe("magic.effect", effect="body_toxicity_changed", entity=runtime._visual_entity(obj), toxicity=amount)
        return profile(obj)

    def kill(target: Any, cause: Any = "spell") -> dict[str, Any]:
        obj = _living(target, "kill")
        _check_mutation(runtime, "kill")
        if not isinstance(cause, str) or not cause.strip() or len(cause) > 80:
            raise TypeErrorML("physiology.kill() cause must be non-empty text no longer than 80 characters")
        if obj.properties.get("life_state") in {"dead", "undead"}:
            raise MagicErrorML("physiology.kill() requires a living target; this target is already dead or undead")
        _initialize(obj)
        return _die(runtime, obj, cause.strip())

    def revive(target: Any, vitality: Any = 0.35, *, restore_organs: Any = 0.1) -> dict[str, Any]:
        """Bring a recoverable dead body back to life; this does not revive liches."""
        obj = _living(target, "revive")
        _check_mutation(runtime, "revive")
        props = obj.properties
        if props.get("life_state") != "dead" or props.get("body_present") is not True:
            raise MagicErrorML("physiology.revive() requires a dead body that still exists")
        if props.get("soul_state") in {"destroyed", "consumed", "bound_to_phylactery"}:
            raise MagicErrorML("physiology.revive() cannot reach this soul; resolve its soul binding first")
        count = int(props.get("revival_count", 0))
        if count >= 3:
            raise MagicErrorML("physiology.revive() body has reached the three-revival stability limit")
        vitality_value = _finite_range(vitality, "revive() vitality", 0.05, 1.0)
        restore_value = _finite_range(restore_organs, "revive() restore_organs", 0.0, 1.0)
        _initialize(obj)
        max_hp = float(props.get("max_hp", 100.0) or 100.0)
        props["life_state"] = "alive"
        props["is_dead"] = False
        props["living"] = True
        props["consciousness"] = "weak"
        props["hp"] = max(1.0, max_hp * vitality_value)
        props["body_present"] = False
        props["body_condition"] = "recovering"
        props["soul_state"] = "present"
        props["revival_count"] = count + 1
        props["blood_volume_l"] = max(float(props.get("blood_volume_l", 0.0)), float(props.get("blood_volume_max_l", 5.0)) * 0.65)
        props["oxygen_saturation"] = max(float(props.get("oxygen_saturation", 0.0)), 0.7)
        props["blood_loss_rate_lps"] = 0.0
        props["blood_clotted"] = True
        for state in props.get("anatomy", {}).values():
            if isinstance(state, dict):
                state["integrity"] = min(1.0, float(state.get("integrity", 1.0)) + restore_value)
        refresh_effective_properties(obj, runtime.elapsed_virtual_time)
        runtime._observe("magic.effect", effect="revival", entity=runtime._visual_entity(obj), vitality=vitality_value,
                         revival_count=props["revival_count"])
        runtime.emit_event("being_revived", obj, vitality_value)
        return profile(obj)

    def set_bleeding(target: Any, rate_lps: Any) -> dict[str, Any]:
        """Set a bounded ongoing bleed rate for simulation and spell reactions."""
        obj = _living(target, "set_bleeding")
        _require_alive(obj, "set_bleeding")
        _check_mutation(runtime, "set_bleeding")
        rate = _finite_range(rate_lps, "set_bleeding() rate_lps", 0.0, 1.0)
        _initialize(obj)
        obj.properties["blood_loss_rate_lps"] = rate
        obj.properties["blood_clotted"] = rate == 0
        runtime._observe("entity.changed", entity=runtime._visual_entity(obj), operation="blood_loss_rate_set", rate_lps=rate)
        return blood_state(obj)

    for operation in (profile, enhance, propel, injure, heal, injure_system, heal_system, set_temperature, set_toxicity,
                      blood_state, manipulate_blood, kill, revive, set_bleeding, systems):
        operation.__mana_runtime_operation__ = True
    return {
        "organs": organs,
        "systems": systems,
        "define_form": define_form,
        "forms": lambda: [{"name": name, "label": data.get("label"), "organs": list(data.get("organs", [])), "movement_mode": data.get("movement_mode"), "vital_structures": list(data.get("vital_structures", [])), "trait_factors": copy.deepcopy(data.get("trait_factors", {}))} for name, data in sorted({**{name: {"name": name, "label": name.title(), "organs": list(organs), "movement_mode": {"bird": "flight-capable", "aquatic": "swim-capable", "serpent": "slither-capable", "human": "terrestrial", "humanoid": "terrestrial", "knight": "terrestrial", "beast": "terrestrial"}.get(name, "terrestrial")} for name, organs in _FORM_ORGANS.items()}, **runtime.custom_body_forms}.items())],
        "profile": profile,
        "enhance": enhance,
        "propel": propel,
        "injure": injure,
        "heal": heal,
        "injure_system": injure_system,
        "heal_system": heal_system,
        "set_temperature": set_temperature,
        "set_toxicity": set_toxicity,
        "blood_state": blood_state,
        "manipulate_blood": manipulate_blood,
        "set_bleeding": set_bleeding,
        "kill": kill,
        "revive": revive,
    }


def _organ_key(organ: Any, operation: str, *, runtime: Any = None, obj: Any = None) -> str:
    if not isinstance(organ, str):
        raise TypeErrorML(f"physiology.{operation}() organ must be text")
    key = "_".join(organ.strip().casefold().replace("-", " ").split())
    custom = getattr(runtime, "custom_anatomy_organs", {}) if runtime is not None else {}
    custom_species = getattr(runtime, "custom_anatomy_species", {}) if runtime is not None else {}
    existing = getattr(obj, "properties", {}).get("anatomy", {}) if obj is not None else {}
    profile_structure = any(key in profile.get("organ_names", []) or key in profile.get("special_organs", [])
                            for profile in _ANATOMY_SPECIES.values())
    if not profile_structure:
        profile_structure = any(key in profile.get("organ_names", []) or key in profile.get("special_organs", [])
                                for profile in custom_species.values())
    if key not in _ORGANS and key not in _ANATOMY_ORGANS and key not in custom and not profile_structure and not (isinstance(existing, dict) and key in existing):
        raise MagicErrorML(f"physiology.{operation}() requires a known organ/structure; use anatomy.organs(species) or anatomy.define_organ() to inspect or define the catalogue")
    return key


def advance_runtime(runtime: Any, dt: float, objects: list[Any]) -> None:
    """Advance bounded biological state alongside world physics."""
    if not math.isfinite(dt) or dt <= 0:
        return
    now = runtime.elapsed_virtual_time
    for obj in objects:
        props = getattr(obj, "properties", None)
        if not isinstance(props, dict) or not props.get("active", True):
            continue
        if not props.get("body_model_initialized"):
            continue
        state = props.get("life_state", "alive")
        if state == "dead":
            continue
        control = props.get("blood_control")
        if isinstance(control, dict) and float(control.get("until", 0.0)) <= now:
            props["blood_control"] = None
            if props.get("consciousness") == "strained":
                props["consciousness"] = "awake"
            refresh_effective_properties(obj, now)
        if state == "undead":
            continue
        anatomy = props.get("anatomy", {})
        species_id = str(props.get("anatomy_species_id", "")).casefold()
        # Use the structures the selected clade actually owns. Invertebrates do not
        # fail merely because they lack vertebrate organs with familiar names.
        if species_id == "earthworm":
            heart = _body_health_structure(obj, "aortic_arches")
            brain = _body_health_structure(obj, "cerebral_ganglia", "ventral_nerve_cord")
            lungs = _body_health_structure(obj, "skin_cuticle")
            renal_health = _body_health_structure(obj, "nephridia")
            hepatic_health = 1.0  # no vertebrate-style liver in this profile
        else:
            heart = _body_health_structure(obj, "heart", "aortic_arches")
            brain = _body_health_structure(obj, "brain", "cerebral_ganglia", "ventral_nerve_cord")
            if species_id in {"eagle", "owl", "raven", "falcon", "parrot", "pigeon"}:
                lungs = min(_body_health_structure(obj, "lungs"), _body_health_structure(obj, "air_sacs"))
            else:
                lungs = _body_health_structure(obj, "lungs", "serpentine_lung", "skin_cuticle")
            renal_health = _body_health_structure(obj, "kidneys", "nephridia")
            hepatic_health = _body_health_structure(obj, "liver")
        blood_volume = max(0.0, float(props.get("blood_volume_l", 5.0)))
        bleed_rate = max(0.0, min(1.0, float(props.get("blood_loss_rate_lps", 0.0))))
        if bleed_rate > 0 and not props.get("blood_clotted", False):
            lost = min(blood_volume, bleed_rate * dt)
            props["blood_volume_l"] = blood_volume - lost
            blood_capacity = max(0.01, float(props.get("blood_volume_max_l", 5.0)))
            props["externalized_blood_l"] = min(blood_capacity * 1.5, float(props.get("externalized_blood_l", 0.0)) + lost)
            blood_volume -= lost
        oxygen = min(1.0, max(0.0, float(props.get("oxygen_saturation", 0.98))))
        blood_capacity = max(0.01, float(props.get("blood_volume_max_l", 5.0)))
        if lungs < 0.2 or heart < 0.2 or blood_volume / blood_capacity < 0.3:
            oxygen = max(0.0, oxygen - dt * (0.04 + max(0.0, 0.2 - min(lungs, heart)) * 0.1))
        else:
            oxygen = min(0.98, oxygen + dt * 0.025)
        props["oxygen_saturation"] = oxygen
        if oxygen < 0.25 or brain < 0.15:
            props["consciousness"] = "unconscious"
            max_hp = float(props.get("max_hp", 100.0) or 100.0)
            # Severe oxygen debt and brain trauma cause gradual collapse, not an
            # instantaneous full-health kill on the first simulation tick.
            severity = max(0.0, 0.25 - oxygen) * 0.08 + max(0.0, 0.15 - brain) * 0.04
            props["hp"] = max(0.0, float(props.get("hp", max_hp)) - max_hp * dt * severity)
        liver = hepatic_health
        kidneys = renal_health
        toxicity = max(0.0, float(props.get("toxicity", 0.0)))
        if toxicity > 0 and dt > 0:
            detox_rate = 0.01 * (liver + kidneys) * dt
            props["toxicity"] = max(0.0, toxicity - detox_rate)
            if toxicity > 0.8 and min(liver, kidneys) < 0.15:
                props["hp"] = max(0.0, float(props.get("hp", 100.0)) - float(props.get("max_hp", 100.0)) * dt * 0.005)
        body_temp = float(props.get("body_temperature_c", 37.0))
        # Endotherms weakly return toward a profile-specific set point. Ectotherms
        # exchange temperature with their environment instead of magically returning
        # to 37 C; the surrounding world may update their body temperature.
        endothermic = props.get("body_thermal_mode", "endothermic") != "ectothermic"
        setpoint = float(props.get("body_temperature_setpoint_c", 37.0))
        if endothermic:
            homeostatic_delta = min(0.05 * dt, abs(setpoint - body_temp))
            if body_temp < setpoint:
                body_temp += homeostatic_delta
            elif body_temp > setpoint:
                body_temp -= homeostatic_delta
            props["body_temperature_c"] = body_temp
        else:
            props["body_temperature_c"] = body_temp
        low_limit, high_limit = (28.0, 42.0) if endothermic else (5.0, 45.0)
        collapse_low, collapse_high = (25.0, 43.0) if endothermic else (2.0, 48.0)
        if body_temp < low_limit or body_temp > high_limit:
            temperature_severity = min(0.05, abs(body_temp - setpoint) * 0.001)
            props["hp"] = max(0.0, float(props.get("hp", 100.0)) - float(props.get("max_hp", 100.0)) * dt * temperature_severity)
            props["consciousness"] = "unconscious" if body_temp < collapse_low or body_temp > collapse_high else props.get("consciousness", "awake")
        if blood_volume / max(0.01, float(props.get("blood_volume_max_l", 5.0))) <= 0.16 or heart <= 0.01 or brain <= 0.01 or float(props.get("hp", 1.0) or 0.0) <= 0:
            _die(runtime, obj, "physiological_failure")
        refresh_effective_properties(obj, now)
