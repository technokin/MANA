"""Extensible comparative anatomy catalogue and per-entity body-model binding.

The catalogue is reference data, not a medical diagnosis engine. Numerical trait
priors are game defaults. Real species summaries are approximate; fictional species
are explicitly labelled editable design templates.
"""
from __future__ import annotations

import copy
from collections import Counter
import math
import re
from typing import Any

from ..errors import MagicErrorML, PhysicsErrorML, TypeErrorML
from .anatomy_data import (HUMAN_BONES, HUMAN_BONE_RECORDS, ORGAN_SEARCH_TEXT, ORGANS,
                           MAX_BODY_STRUCTURES, SPECIES, SPECIES_ALIASES, SPECIES_SEARCH_TEXT, SYSTEMS)

_NAME = re.compile(r"[A-Za-z][A-Za-z0-9_ -]{0,63}\Z")
_VALID_SKELETONS = {"endoskeleton", "exoskeleton", "hydrostatic", "hybrid", "none", "custom"}
_VALID_MOVEMENT = {"terrestrial", "flight-capable", "swim-capable", "slither-capable", "amphibious", "burrowing", "climbing", "gliding", "cursorial", "brachiation", "stationary", "custom"}
_MOVEMENT_TEXT = re.compile(r"[A-Za-z][A-Za-z0-9 _/,-]{0,119}\Z")
_TRAITS = {"strength", "speed", "endurance", "durability", "senses", "reflexes", "regeneration", "recovery"}

_TISSUES: dict[str, dict[str, Any]] = {
    "epithelial": {"role": "covers external and internal surfaces; forms glands and exchange barriers", "subtypes": ["simple squamous", "simple cuboidal", "simple columnar", "pseudostratified columnar", "stratified squamous", "transitional", "glandular"]},
    "connective": {"role": "supports, connects, separates, stores energy and transmits force", "subtypes": ["loose connective", "dense regular", "dense irregular", "adipose", "reticular", "elastic", "cartilage", "bone", "blood"]},
    "skeletal_muscle": {"role": "voluntary force generation and posture in vertebrate skeletal muscles", "subtypes": ["slow oxidative", "fast oxidative-glycolytic", "fast glycolytic", "tendon junction", "motor unit"]},
    "cardiac_muscle": {"role": "rhythmic contraction of a vertebrate heart", "subtypes": ["cardiomyocytes", "intercalated discs", "conduction tissue"]},
    "smooth_muscle": {"role": "involuntary contraction in vessels, airway, gut and other hollow structures", "subtypes": ["visceral", "multi-unit", "vascular smooth muscle"]},
    "nervous": {"role": "signal generation, transmission and support", "subtypes": ["neurons", "astrocytes", "oligodendrocytes or clade analogues", "microglia or immune analogues", "Schwann cells or peripheral glia"]},
    "blood": {"role": "circulating transport and defence tissue; cellular composition varies by lineage", "subtypes": ["plasma", "erythrocytes or oxygen carriers", "leukocytes or immune cells", "platelets/thrombocytes or clotting analogues"]},
    "lymphoid": {"role": "immune surveillance, cell maturation and immune-cell traffic", "subtypes": ["lymphocytes", "antigen-presenting cells", "stromal cells", "lymph"]},
    "bone_marrow": {"role": "blood-cell production and marrow niches in many vertebrates", "subtypes": ["hematopoietic stem/progenitor cells", "myeloid lineages", "lymphoid lineages", "stromal cells", "vascular sinusoids", "fatty marrow"]},
    "cartilage": {"role": "resilient flexible support and low-friction bearing surfaces", "subtypes": ["hyaline", "elastic", "fibrocartilage"]},
    "keratinised": {"role": "tough external or distal appendage structures", "subtypes": ["hair", "feather", "claw/nail", "hoof", "beak", "scale sheath"]},
    "cuticle": {"role": "external non-vertebrate body covering; composition depends on clade", "subtypes": ["epidermis", "secreted surface matrix", "sensory openings"]},
    "germinal": {"role": "reproduction and lineage continuity", "subtypes": ["germ cells", "supporting gonadal cells", "reproductive ducts or clade-specific equivalents"]},
    "fluid_compartment": {"role": "fluid-filled spaces which support exchange, pressure or hydrostatic mechanics", "subtypes": ["interstitial fluid", "coelomic fluid", "lymph", "serous fluid", "synovial fluid"]},
}

_CELL_TYPES: dict[str, dict[str, Any]] = {
    "erythrocyte": {"system": "circulatory", "role": "oxygen and carbon-dioxide transport in many vertebrates; mature mammalian examples are anucleate"},
    "leukocyte": {"system": "immune", "role": "umbrella label for immune cells; subdivide into species-appropriate lineages for detailed simulation"},
    "thrombocyte": {"system": "circulatory", "role": "nucleated clotting cell in birds, reptiles and many non-mammalian vertebrates"},
    "platelet": {"system": "circulatory", "role": "small anucleate clotting fragment in mammals"},
    "neuron": {"system": "nervous", "role": "electrical and chemical signalling cell"},
    "astrocyte": {"system": "nervous", "role": "central nervous-system support, homeostasis and neurovascular coupling in mammals"},
    "oligodendrocyte": {"system": "nervous", "role": "myelination of central nervous-system axons in mammals"},
    "schwann_cell": {"system": "nervous", "role": "support and myelination of many peripheral axons in vertebrates"},
    "cardiomyocyte": {"system": "circulatory", "role": "contractile heart-muscle cell"},
    "smooth_muscle_cell": {"system": "muscular", "role": "involuntary contraction in hollow organs and vessels"},
    "skeletal_muscle_fibre": {"system": "muscular", "role": "multinucleate contractile fibre in typical vertebrate skeletal muscle"},
    "osteoblast": {"system": "skeletal", "role": "bone-matrix formation"},
    "osteocyte": {"system": "skeletal", "role": "mature embedded bone cell involved in maintenance and load sensing"},
    "osteoclast": {"system": "skeletal", "role": "bone resorption and remodeling"},
    "chondrocyte": {"system": "skeletal", "role": "cartilage matrix maintenance"},
    "keratinocyte": {"system": "integumentary", "role": "main epidermal cell; forms barrier keratin in mammals"},
    "melanocyte": {"system": "integumentary", "role": "pigment production and transfer in many vertebrates"},
    "adipocyte": {"system": "metabolic", "role": "energy storage, insulation and endocrine signalling"},
    "hepatocyte": {"system": "metabolic", "role": "major liver cell responsible for many synthetic, metabolic and detoxification tasks"},
    "podocyte": {"system": "renal", "role": "specialised filtration-barrier cell in vertebrate kidney glomeruli"},
    "enterocyte": {"system": "digestive", "role": "intestinal epithelial absorption cell"},
    "goblet_cell": {"system": "digestive", "role": "mucus-secreting epithelial cell at many mucosal surfaces"},
    "pancreatic_beta_cell": {"system": "endocrine", "role": "insulin-secreting cell in mammalian pancreatic islets"},
    "fibroblast": {"system": "connective", "role": "extracellular matrix production and repair"},
    "endothelial_cell": {"system": "circulatory", "role": "lining cell of blood and lymphatic vessels"},
    "macrophage": {"system": "immune", "role": "phagocytosis, innate defence and tissue signalling; biology varies by lineage"},
    "mast_cell": {"system": "immune", "role": "tissue immune signalling and mediator release in many vertebrates"},
    "earthworm_coelomocyte": {"system": "immune", "role": "invertebrate coelomic immune cell analogue; categories vary among annelids"},
    "earthworm_epidermal_cell": {"system": "integumentary", "role": "surface cell involved in a moist cuticle interface and gas exchange"},
}


def _key(value: Any, what: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise TypeErrorML(f"anatomy.{what} expects non-empty text")
    return "_".join(value.strip().casefold().replace("-", " ").split())


def _profile(runtime: Any, species: Any) -> dict[str, Any]:
    key = _key(species, "species")
    custom = getattr(runtime, "custom_anatomy_species", {})
    if key in custom:
        return copy.deepcopy(custom[key])
    canonical = SPECIES_ALIASES.get(key, SPECIES_ALIASES.get(key.replace("_", " "), key))
    if canonical not in SPECIES:
        available = ", ".join(sorted(SPECIES))
        raise MagicErrorML(f"unknown anatomy species '{species}'; use anatomy.species() or anatomy.search() ({available})")
    result = copy.deepcopy(SPECIES[canonical])
    result.setdefault("name", canonical)
    return result


def _organ_record(runtime: Any, name: str, species_profile: dict[str, Any] | None = None) -> dict[str, Any]:
    custom = getattr(runtime, "custom_anatomy_organs", {})
    key = _key(name, "organ")
    if key in custom:
        return copy.deepcopy(custom[key])
    if key in ORGANS:
        return copy.deepcopy(ORGANS[key])
    # Species-only named structure (e.g. a bird air-sac diverticulum). Its
    # detailed form remains editable, and absence from the common catalogue is
    # explicitly reported rather than pretending to know a universal anatomy.
    profile = species_profile or {}
    special = set(profile.get("special_organs", []))
    if key in special or key in profile.get("organ_names", []):
        systems = profile.get("systems", {})
        system = next((system for system, names in systems.items() if key in names), "magical_specialisation")
        return {"name": key, "system": system, "kind": "species_specific_structure", "role": f"Species-specific structure listed by the {profile.get('label', 'selected')} profile.", "substructures": [], "tissues": [], "dependencies": [], "notes": "This reference profile does not claim a complete histological subdivision for this structure."}
    raise MagicErrorML(f"unknown anatomical structure '{name}'; use anatomy.organs(species) or anatomy.define_organ()")


def _all_profiles(runtime: Any) -> dict[str, dict[str, Any]]:
    """Return an internal read-only view of profile mappings.

    Callers must copy only the selected result they expose to user code. Older
    code deep-copied every stock profile for every list/search operation, which
    made common catalogue browsing needlessly expensive as the data grew.
    """
    result = dict(SPECIES)
    result.update(getattr(runtime, "custom_anatomy_species", {}))
    return result



def _movement_capabilities(profile: dict[str, Any]) -> list[str]:
    """Return general movement capabilities inferred from a body template.

    These are declarations for composition and inspection, not claims that each
    gait already has a dedicated locomotion solver.
    """
    explicit = profile.get("movement_capabilities")
    if isinstance(explicit, list) and explicit:
        return list(dict.fromkeys(str(item).casefold() for item in explicit if isinstance(item, str)))
    mode = str(profile.get("movement_mode", "")).casefold()
    clade = str(profile.get("clade", "")).casefold()
    organs = set(profile.get("organ_names", []))
    caps: list[str] = []
    def add(*values: str) -> None:
        for value in values:
            if value not in caps:
                caps.append(value)
    if any(token in mode for token in ("flight", "fly", "flying", "winged")) or "wings" in organs:
        add("fly", "glide")
    if any(token in mode for token in ("swim", "aquatic", "water", "marine")) or any(x in organs for x in ("fins", "gills", "flippers", "tail_flukes")):
        add("swim", "dive")
    if any(token in mode for token in ("slither", "serpentine", "undulation")) or "snake" in clade:
        add("slither")
    if any(token in mode for token in ("burrow", "peristaltic")) or "earthworm" in clade or "annelid" in clade:
        add("crawl", "burrow")
    if any(token in mode for token in ("climb", "arboreal", "scansorial")) or any(x in organs for x in ("pedipalps", "large_claws", "spinnerets")):
        add("climb")
    if any(token in mode for token in ("terrestrial", "quadruped", "biped", "plantigrade", "digitigrade", "cursorial", "walk")):
        add("walk", "run", "jump")
    if any(x in organs for x in ("silk_glands", "spinnerets")):
        add("web")
    if "arms" in organs and any(x in organs for x in ("siphon", "gills")):
        add("jet-propel")
    if any(token in mode for token in ("stationary",)) and not caps:
        add("stationary")
    if not caps and "custom" in mode:
        add("custom")
    return caps


def _human_bone_records() -> list[dict[str, Any]]:
    """Return the documented 206-element typical adult human bone inventory."""
    return copy.deepcopy(HUMAN_BONE_RECORDS)


def _entity_profile(runtime: Any, target: Any) -> dict[str, Any]:
    """Resolve the bound species or an active generic transfiguration template."""
    props = getattr(target, "properties", {})
    species_id = props.get("anatomy_species_id")
    if isinstance(species_id, str):
        try:
            return _profile(runtime, species_id)
        except MagicErrorML:
            pass
    base = _profile(runtime, "human")
    active_names = props.get("body_model_organs", [])
    active_systems = props.get("body_systems", {})
    if isinstance(active_names, list) and active_names:
        base["organ_names"] = list(active_names[:MAX_BODY_STRUCTURES])
    if isinstance(active_systems, dict):
        base["systems"] = copy.deepcopy(active_systems)
    base["label"] = str(props.get("species", props.get("body_form", "Transfigured Being")))
    base["name"] = str(props.get("body_form", "custom_form"))
    base["classification"] = props.get("anatomy_classification", "transfigured-form")
    base["special_organs"] = [name for name in base["organ_names"] if name not in _profile(runtime, "human").get("organ_names", [])]
    return base

def build_library(runtime: Any) -> dict[str, Any]:
    def species() -> list[dict[str, Any]]:
        profiles = _all_profiles(runtime)
        return [{"name": key, "label": value.get("label", key.title()),
                 "classification": value.get("classification", "custom"),
                 "clade": value.get("clade", "custom"),
                 "skeleton_type": value.get("skeleton", {}).get("type", "unknown"),
                 "organ_count": len(value.get("organ_names", [])),
                 "systems": sorted(value.get("systems", {})),
                 "components": list(value.get("components", [key])),
                 "movement_mode": value.get("movement_mode", "custom"),
                 "movement_capabilities": _movement_capabilities(value),
                 "evidence": value.get("evidence", "user-defined")}
                for key, value in sorted(profiles.items())]

    def search(query: Any) -> list[dict[str, Any]]:
        if not isinstance(query, str) or not query.strip():
            raise TypeErrorML("anatomy.search() expects non-empty search text")
        needle = " ".join(query.strip().casefold().replace("-", " ").split())
        found = []
        # Static stock search text is built once in anatomy_data.py. Custom
        # profiles are few and remain live so additions are searchable immediately.
        for name, haystack in SPECIES_SEARCH_TEXT.items():
            if needle in haystack:
                profile = SPECIES[name]
                found.append({"name": name, "label": profile.get("label", name.title()),
                              "classification": profile.get("classification"), "clade": profile.get("clade")})
        for name, profile in getattr(runtime, "custom_anatomy_species", {}).items():
            haystack = " ".join([name, str(profile.get("label", "")), str(profile.get("clade", "")),
                                  " ".join(profile.get("senses", [])), " ".join(profile.get("special_organs", [])),
                                  " ".join(profile.get("organ_names", [])), " ".join(profile.get("components", []))]).casefold()
            if needle in haystack:
                found.append({"name": name, "label": profile.get("label", name.title()),
                              "classification": profile.get("classification"), "clade": profile.get("clade")})
        # Return matching shared structure records too, enabling queries such as
        # `anatomy.search("aorta")` without scanning hundreds of structures anew.
        for name, haystack in ORGAN_SEARCH_TEXT.items():
            if needle in haystack:
                record = ORGANS[name]
                found.append({"name": name, "label": record.get("name", name),
                              "kind": "organ", "system": record.get("system")})
        for name, record in getattr(runtime, "custom_anatomy_organs", {}).items():
            if needle in (name + " " + str(record.get("role", ""))).casefold():
                found.append({"name": name, "label": record.get("name", name), "kind": "organ", "system": record.get("system")})
        # Stable deduplication matters when an organ appears in several profile maps.
        unique = []
        seen = set()
        for item in found:
            identity = (item.get("kind", "species"), item.get("name"))
            if identity not in seen:
                seen.add(identity)
                unique.append(item)
            if len(unique) >= 200:
                break
        return unique

    def profile(species: Any = "human") -> dict[str, Any]:
        selected = _profile(runtime, species)
        selected["movement_capabilities"] = _movement_capabilities(selected)
        return selected

    def systems(species: Any = "human") -> dict[str, Any]:
        selected = _profile(runtime, species)
        result: dict[str, Any] = {}
        for key, organ_names in selected.get("systems", {}).items():
            meta = copy.deepcopy(SYSTEMS.get(key, {"label": key.replace("_", " ").title(), "purpose": "User-defined or clade-specific biological system.", "dependencies": [], "functions": []}))
            meta["organs"] = list(organ_names)
            result[key] = meta
        for custom_key, custom_meta in getattr(runtime, "custom_anatomy_systems", {}).items():
            if custom_key not in result:
                meta = copy.deepcopy(custom_meta)
                # The profile is authoritative about which structures exist in this
                # body; catalogue-wide custom-system entries remain discoverable.
                meta["organs"] = [name for name in meta.get("organs", []) if name in selected.get("organ_names", [])]
                result[custom_key] = meta
        return result

    def organs(species: Any = "human", system: Any = None) -> list[dict[str, Any]]:
        selected = _profile(runtime, species)
        chosen_system = _key(system, "system") if system is not None else None
        output = []
        for name in selected.get("organ_names", []):
            record = _organ_record(runtime, name, selected)
            if chosen_system and record.get("system") != chosen_system:
                continue
            output.append(record)
        return output

    def organ(name: Any, species: Any = "human") -> dict[str, Any]:
        return _organ_record(runtime, _key(name, "organ"), _profile(runtime, species))

    def bones(species: Any = "human", region: Any = None) -> dict[str, Any] | list[dict[str, Any]]:
        selected = _profile(runtime, species)
        if selected.get("name", "").casefold() == "human" or selected.get("skeleton", {}).get("inventory") == "human_adult":
            data = copy.deepcopy(HUMAN_BONES)
            if region is None:
                return data
            requested = _key(region, "bone_region")
            if requested in {"axial", "appendicular"}:
                return copy.deepcopy(data[requested])
            for region_name in ("axial", "appendicular"):
                for group, record in data[region_name].items():
                    if requested in {group, group.replace("_", " ")}:
                        return copy.deepcopy(record)
            raise MagicErrorML("unknown human bone region; use axial, appendicular, cranial_bones, facial_bones, vertebral_column, thoracic_cage, upper_limbs, lower_limbs, or a named girdle")
        inventory = copy.deepcopy(selected.get("bones", selected.get("skeleton", {})))
        if region is None:
            inventory["classification"] = selected.get("classification")
            inventory["species"] = selected.get("label")
            inventory["structures"] = copy.deepcopy(selected.get("skeletal_structures", inventory.get("regions", [])))
            inventory["counting_note"] = (
                "Individually enumerated, typical adult reference inventory; variation exists."
                if selected.get("classification") == "real" and selected.get("skeleton", {}).get("inventory") == "human_adult"
                else "Counts are unspecified unless a species-specific vetted inventory is supplied."
            )
            return inventory
        requested = _key(region, "bone_region").replace("_", " ")
        regions = selected.get("skeletal_structures", inventory.get("regions", []))
        matched = [item for item in regions if requested in str(item).casefold()]
        if not matched:
            raise MagicErrorML(f"'{region}' is not a known region in the {selected.get('label', species)} skeletal inventory")
        return [{"name": item, "classification": selected.get("classification"), "inventory": inventory.get("inventory"), "count": None, "count_status": "not specified; use species-specific osteology data"} for item in matched]

    def bone_list(species: Any = "human", region: Any = None) -> list[dict[str, Any]]:
        selected = _profile(runtime, species)
        if selected.get("name") == "human" or selected.get("skeleton", {}).get("inventory") == "human_adult":
            data = _human_bone_records()
            if region is not None:
                requested = _key(region, "bone_region")
                if requested not in {"axial", "appendicular"}:
                    group_matches = [record["group"] for record in data if record["group"] == requested]
                    if not group_matches:
                        raise MagicErrorML("unknown human bone region; use axial, appendicular, or a named bone group")
                    data = [record for record in data if record["group"] == requested]
                else:
                    data = [record for record in data if record["region"] == requested]
            return data
        # `bone_list` lists bones/skeletal elements only where an endoskeleton or
        # explicitly hybrid skeleton makes that interpretation meaningful. A
        # hydrostatic worm, arthropod exoskeleton, cnidarian, or cartilaginous fish
        # must not acquire an invented vertebrate-style bone inventory. Their
        # support structures remain available through anatomy.bones()/profile().
        inventory = selected.get("bones", selected.get("skeleton", {}))
        skeleton_type = str(selected.get("skeleton", {}).get("type", inventory.get("type", ""))).casefold()
        if "endoskeleton" not in skeleton_type and skeleton_type != "hybrid":
            return []
        requested = _key(region, "bone_region").replace("_", " ") if region is not None else None
        regions = selected.get("skeletal_structures", inventory.get("regions", []))
        if requested is not None:
            regions = [item for item in regions if requested in str(item).casefold()]
            if not regions:
                raise MagicErrorML(f"unknown bone region for {selected.get('label', species)}")
        return [{"name": str(item), "region": "species_specific", "group": "skeletal_region",
                 "classification": selected.get("classification"), "inventory": inventory.get("inventory"),
                 "count": None, "counting_note": "No species-specific itemised bone count is provided in this reference profile."} for item in regions]

    def bone(name: Any, species: Any = "human") -> dict[str, Any]:
        if not isinstance(name, str) or not name.strip():
            raise TypeErrorML("anatomy.bone() expects a bone name")
        needle = _key(name, "bone")
        candidates = bone_list(species)
        for record in candidates:
            if needle in {record["name"], record["name"].replace("_", " ")}:
                return copy.deepcopy(record)
        raise MagicErrorML(f"unknown individually catalogued bone '{name}' for {species}; use anatomy.bone_list(species)")

    def tissues(species: Any = "human") -> list[dict[str, Any]]:
        selected = _profile(runtime, species)
        names = list(_TISSUES)
        if selected.get("clade", "").startswith("annelid") or selected.get("base") == "annelid":
            names = [name for name in names if name not in {"bone_marrow", "cartilage", "keratinised"}] + ["cuticle", "fluid_compartment"]
        return [{"name": name, **copy.deepcopy(_TISSUES[name])} for name in dict.fromkeys(names)]

    def cell_types(system: Any = None) -> list[dict[str, Any]]:
        chosen = _key(system, "system") if system is not None else None
        return [{"name": name, **copy.deepcopy(record)} for name, record in _CELL_TYPES.items() if chosen is None or record.get("system") == chosen]

    def blood(species: Any = "human") -> dict[str, Any]:
        selected = _profile(runtime, species)
        return {"species": selected.get("label", species), "profile": copy.deepcopy(selected.get("blood", {})),
                "circulation": copy.deepcopy(selected.get("circulation", {})),
                "modeling_note": "Species reference, not a clinical diagnostic range. Use physiology for simulated state. Fictional profiles require explicit design decisions."}

    def define_organ(name: Any, *, system: Any, role: Any, substructures: Any = None,
                     tissues: Any = None, dependencies: Any = None, notes: Any = "") -> dict[str, Any]:
        if getattr(runtime, "_pure_call_depth", 0):
            raise MagicErrorML("anatomy.define_organ() changes the anatomy catalogue; use it in a committed spell")
        if not isinstance(name, str) or not _NAME.fullmatch(name.strip()):
            raise TypeErrorML("anatomy.define_organ() name must be 1–64 letters, digits, spaces, underscores or hyphens, starting with a letter")
        key = _key(name, "define_organ")
        if key in ORGANS or key in getattr(runtime, "custom_anatomy_organs", {}):
            raise MagicErrorML(f"anatomical structure '{key}' already exists")
        if len(runtime.custom_anatomy_organs) >= 512:
            raise PhysicsErrorML("a runtime can define at most 512 custom anatomical structures")
        if not isinstance(system, str) or not _NAME.fullmatch(system.strip()):
            raise TypeErrorML("anatomy.define_organ() system must be a named system")
        sys_key = _key(system, "define_organ")
        if not isinstance(role, str) or not role.strip() or len(role) > 500:
            raise TypeErrorML("anatomy.define_organ() role must be 1–500 characters")
        def text_list(raw: Any, label: str, max_items: int) -> list[str]:
            if raw is None:
                return []
            if not isinstance(raw, list) or len(raw) > max_items or any(not isinstance(x, str) or not x.strip() or len(x) > 160 for x in raw):
                raise TypeErrorML(f"anatomy.define_organ() {label} must be a list of up to {max_items} non-empty strings of at most 160 characters")
            return list(dict.fromkeys(x.strip() for x in raw))
        if not isinstance(notes, str) or len(notes) > 1000:
            raise TypeErrorML("anatomy.define_organ() notes must be text no longer than 1000 characters")
        record = {"name": key, "system": sys_key, "kind": "user_defined_structure", "role": role.strip(),
                  "substructures": text_list(substructures, "substructures", 128),
                  "tissues": text_list(tissues, "tissues", 64),
                  "dependencies": text_list(dependencies, "dependencies", 64), "notes": notes.strip()}
        runtime.custom_anatomy_organs[key] = record
        if sys_key not in SYSTEMS and sys_key not in runtime.custom_anatomy_systems:
            runtime.custom_anatomy_systems[sys_key] = {"label": sys_key.replace("_", " ").title(), "purpose": "User-defined anatomy system.", "dependencies": [], "functions": [], "organs": []}
        if sys_key in runtime.custom_anatomy_systems:
            bucket = runtime.custom_anatomy_systems[sys_key].setdefault("organs", [])
            if key not in bucket:
                bucket.append(key)
        runtime._observe("world.changed", operation="anatomy_organ_defined", organ=key, system=sys_key)
        return copy.deepcopy(record)

    def define_system(name: Any, *, purpose: Any, dependencies: Any = None,
                      functions: Any = None, notes: Any = "") -> dict[str, Any]:
        """Register an extensible biological or fictional body system."""
        if getattr(runtime, "_pure_call_depth", 0):
            raise MagicErrorML("anatomy.define_system() changes the anatomy catalogue; use it in a committed spell")
        if not isinstance(name, str) or not _NAME.fullmatch(name.strip()):
            raise TypeErrorML("anatomy.define_system() name must be 1–64 valid characters")
        key = _key(name, "define_system")
        custom_systems = getattr(runtime, "custom_anatomy_systems", {})
        if key in SYSTEMS or key in custom_systems:
            raise MagicErrorML(f"anatomy system '{key}' already exists")
        if len(custom_systems) >= 128:
            raise PhysicsErrorML("a runtime can define at most 128 custom anatomy systems")
        if not isinstance(purpose, str) or not purpose.strip() or len(purpose) > 1000:
            raise TypeErrorML("anatomy.define_system() purpose must be 1–1000 characters")
        if not isinstance(notes, str) or len(notes) > 2000:
            raise TypeErrorML("anatomy.define_system() notes must be text up to 2000 characters")
        def text_list(raw: Any, label: str) -> list[str]:
            if raw is None:
                return []
            if not isinstance(raw, list) or len(raw) > 64 or any(not isinstance(x, str) or not x.strip() or len(x) > 160 for x in raw):
                raise TypeErrorML(f"anatomy.define_system() {label} must be a list of up to 64 non-empty strings of at most 160 characters")
            return list(dict.fromkeys(x.strip() for x in raw))
        record = {"label": name.strip(), "purpose": purpose.strip(),
                  "dependencies": text_list(dependencies, "dependencies"),
                  "functions": text_list(functions, "functions"), "notes": notes.strip(), "organs": []}
        custom_systems[key] = record
        runtime._observe("world.changed", operation="anatomy_system_defined", system=key)
        return copy.deepcopy(record)

    def define_species(name: Any, *, base: Any = "human", components: Any = None,
                       trait_merge: Any = "primary", append_organs: Any = None,
                       remove_organs: Any = None, skeleton_type: Any = None,
                       movement_mode: Any = None, movement_capabilities: Any = None,
                       remove_movement_capabilities: Any = None,
                       thermoregulation: Any = None, notes: Any = None,
                       body_mass_kg: Any = None, body_length_m: Any = None,
                       body_width_m: Any = None, body_height_m: Any = None,
                       collision_radius_m: Any = None,
                       strength: Any = None, speed: Any = None, endurance: Any = None,
                       durability: Any = None, senses: Any = None, reflexes: Any = None,
                       regeneration: Any = None, recovery: Any = None) -> dict[str, Any]:
        """Define a species or chimera from reusable, validated body templates.

        ``base`` supplies the primary body plan. ``components`` supplies optional
        donor species whose structures and systems may be integrated. This combines
        anatomy as a template only; incompatible physiological systems are reported
        so the designer can make explicit choices instead of pretending all donors
        are automatically biologically compatible.
        """
        if getattr(runtime, "_pure_call_depth", 0):
            raise MagicErrorML("anatomy.define_species() changes the species catalogue; use it in a committed spell")
        if not isinstance(name, str) or not _NAME.fullmatch(name.strip()):
            raise TypeErrorML("anatomy.define_species() name must be valid non-empty text")
        key = _key(name, "define_species")
        if key in SPECIES or key in SPECIES_ALIASES or key.replace("_", " ") in SPECIES_ALIASES or key in runtime.custom_anatomy_species:
            raise MagicErrorML(f"species '{key}' already exists or is a reserved alias")
        if len(runtime.custom_anatomy_species) >= 128:
            raise PhysicsErrorML("a runtime can define at most 128 custom species profiles")
        primary = _profile(runtime, base)
        source_profiles = [primary]
        source_names = [str(primary.get("name", _key(base, "base")))]
        if components is not None:
            if not isinstance(components, list) or len(components) > 16:
                raise TypeErrorML("anatomy.define_species() components must be a list of up to 16 donor species")
            for component in components:
                candidate = _profile(runtime, component)
                component_key = str(candidate.get("name", _key(component, "component")))
                if component_key in source_names:
                    continue
                source_names.append(component_key)
                source_profiles.append(candidate)
        if not isinstance(trait_merge, str) or trait_merge.casefold() not in {"primary", "max", "mean"}:
            raise MagicErrorML("anatomy.define_species() trait_merge must be primary, max, or mean")
        trait_merge = trait_merge.casefold()

        all_source_organs: list[str] = []
        organ_sources: dict[str, list[str]] = {}
        systems_map: dict[str, list[str]] = {}
        for source_name, source in zip(source_names, source_profiles):
            for organ_name in source.get("organ_names", []):
                if organ_name not in all_source_organs:
                    all_source_organs.append(organ_name)
                organ_sources.setdefault(organ_name, [])
                if source_name not in organ_sources[organ_name]:
                    organ_sources[organ_name].append(source_name)
            for sys_name, members in source.get("systems", {}).items():
                bucket = systems_map.setdefault(sys_name, [])
                for organ_name in members:
                    if organ_name in source.get("organ_names", []) and organ_name not in bucket:
                        bucket.append(organ_name)

        def names(raw: Any, label: str, allowed: set[str]) -> list[str]:
            if raw is None:
                return []
            if not isinstance(raw, list) or len(raw) > MAX_BODY_STRUCTURES:
                raise TypeErrorML(f"anatomy.define_species() {label} must be a list of up to 1024 organ names")
            result = []
            for value in raw:
                if not isinstance(value, str):
                    raise TypeErrorML(f"anatomy.define_species() {label} entries must be text")
                organ_key = _key(value, "define_species")
                if organ_key not in ORGANS and organ_key not in runtime.custom_anatomy_organs and organ_key not in allowed:
                    raise MagicErrorML(f"unknown organ '{value}'; define it with anatomy.define_organ() first")
                if organ_key not in result:
                    result.append(organ_key)
            return result

        available_organs = set(all_source_organs)
        additions = names(append_organs, "append_organs", available_organs)
        removals = set(names(remove_organs, "remove_organs", available_organs))
        organ_names = [x for x in all_source_organs if x not in removals]
        for item in additions:
            if item not in organ_names:
                organ_names.append(item)
        if len(organ_names) > MAX_BODY_STRUCTURES:
            raise PhysicsErrorML("a species profile can include at most 1024 addressable anatomical structures")
        if not organ_names:
            raise MagicErrorML("a custom species must retain at least one anatomical structure")
        organ_sources = {organ: sources for organ, sources in organ_sources.items() if organ in organ_names}
        for item in additions:
            organ_sources.setdefault(item, [])
            if key not in organ_sources[item]:
                organ_sources[item].append(key)
            meta = runtime.custom_anatomy_organs.get(item, ORGANS.get(item, {}))
            bucket = systems_map.setdefault(meta.get("system", "magical_specialisation"), [])
            if item not in bucket:
                bucket.append(item)
        systems_map = {sys_name: [organ for organ in members if organ in organ_names]
                       for sys_name, members in systems_map.items()
                       if any(organ in organ_names for organ in members)}

        skeleton_types = [str(source.get("skeleton", {}).get("type", "unknown")) for source in source_profiles]
        skel = copy.deepcopy(primary.get("skeleton", {}))
        if skeleton_type is not None:
            if not isinstance(skeleton_type, str) or skeleton_type.casefold() not in _VALID_SKELETONS:
                raise MagicErrorML("skeleton_type must be endoskeleton, exoskeleton, hydrostatic, hybrid, none, or custom")
            skel["type"] = skeleton_type.casefold()
        elif len(set(skeleton_types)) > 1:
            skel["type"] = "hybrid"
        skel["component_types"] = list(dict.fromkeys(skeleton_types))
        skel["regions"] = list(dict.fromkeys(
            region for source in source_profiles
            for region in source.get("skeleton", {}).get("regions", [])
        ))
        if skel.get("type") != "endoskeleton" or len(set(skeleton_types)) > 1:
            skel["inventory"] = "composite_or_species_specific"
            skel["count"] = None

        if movement_mode is not None:
            if not isinstance(movement_mode, str) or not movement_mode.strip() or not _MOVEMENT_TEXT.fullmatch(movement_mode.strip()):
                raise TypeErrorML("movement_mode must be a supported category or a descriptive gait label up to 120 characters")
            move = movement_mode.strip().casefold()
        else:
            move = primary.get("movement_mode", "terrestrial")

        def infer_capabilities(source: dict[str, Any]) -> list[str]:
            return _movement_capabilities(source)

        caps: list[str] = []
        for source in source_profiles:
            for capability in infer_capabilities(source):
                if capability not in caps:
                    caps.append(capability)
        def capability_list(raw: Any, label: str) -> list[str]:
            if raw is None:
                return []
            if not isinstance(raw, list) or len(raw) > 64:
                raise TypeErrorML(f"anatomy.define_species() {label} must be a list of up to 64 capability names")
            output = []
            for item in raw:
                if not isinstance(item, str) or not item.strip() or len(item.strip()) > 64:
                    raise TypeErrorML(f"anatomy.define_species() {label} entries must be non-empty text up to 64 characters")
                item_key = _key(item, "movement_capabilities")
                if item_key not in output:
                    output.append(item_key)
            return output
        for capability in capability_list(movement_capabilities, "movement_capabilities"):
            if capability not in caps:
                caps.append(capability)
        for capability in capability_list(remove_movement_capabilities, "remove_movement_capabilities"):
            caps = [existing for existing in caps if existing != capability]

        if thermoregulation is not None and (not isinstance(thermoregulation, str) or not thermoregulation.strip() or len(thermoregulation) > 240):
            raise TypeErrorML("thermoregulation must be non-empty text up to 240 characters")
        if notes is not None and (not isinstance(notes, str) or len(notes) > 2000):
            raise TypeErrorML("notes must be text up to 2000 characters")

        parent_traits = copy.deepcopy(primary.get("traits", {}))
        if trait_merge in {"max", "mean"}:
            trait_names = set().union(*(source.get("traits", {}).keys() for source in source_profiles))
            for trait_name in trait_names:
                vals = [float(source.get("traits", {}).get(trait_name, 1.0)) for source in source_profiles]
                parent_traits[trait_name] = max(vals) if trait_merge == "max" else sum(vals) / len(vals)
        requested = {"strength": strength, "speed": speed, "endurance": endurance, "durability": durability,
                     "senses": senses, "reflexes": reflexes, "regeneration": regeneration, "recovery": recovery}
        traits = parent_traits
        for trait, raw in requested.items():
            if raw is not None:
                if isinstance(raw, bool) or not isinstance(raw, (int, float)) or not math.isfinite(float(raw)) or not 0.05 <= float(raw) <= 10.0:
                    raise PhysicsErrorML(f"anatomy.define_species() {trait} must be between 0.05 and 10")
                traits[trait] = float(raw)

        component_profiles = []
        for source_name, source in zip(source_names, source_profiles):
            component_profiles.append({
                "species": source_name, "label": source.get("label", source_name.title()),
                "clade": source.get("clade", "custom"),
                "skeleton_type": source.get("skeleton", {}).get("type", "unknown"),
                "movement_mode": source.get("movement_mode", "custom"),
                "circulation": copy.deepcopy(source.get("circulation", {})),
                "respiration": copy.deepcopy(source.get("respiration", {})),
                "digestion": copy.deepcopy(source.get("digestion", {})),
            })
        warnings = []
        for aspect in ("circulation", "respiration", "digestion"):
            descriptions = []
            for source_name, source in zip(source_names, source_profiles):
                data = source.get(aspect)
                if isinstance(data, dict):
                    label = data.get("type") or data.get("mode") or data.get("description") or data.get("strategy")
                    if label:
                        descriptions.append((source_name, str(label)))
            distinct = {label.casefold() for _, label in descriptions}
            if len(distinct) > 1:
                warnings.append({"aspect": aspect, "detail": f"Source templates differ in {aspect}; define compatibility or magical support before claiming functional integration.", "sources": descriptions})

        thermo = thermoregulation if thermoregulation is not None else primary.get("thermoregulation")
        special = list(dict.fromkeys([x for source in source_profiles for x in source.get("special_organs", []) if x in organ_names]))
        special.extend(x for x in additions if x not in special)

        # Carry a real physical envelope into the new species. For a hybrid that
        # does not declare its own mass, use a conservative composition estimate
        # rather than inheriting the primary species' mass unchanged. The template
        # remains editable; users creating radically new bodies should set these
        # values explicitly.
        simulation = copy.deepcopy(primary.get("simulation", {}))
        if not isinstance(simulation, dict):
            simulation = {}
        source_simulations = [source.get("simulation", {}) if isinstance(source.get("simulation", {}), dict) else {}
                              for source in source_profiles]
        base_mass = float(source_simulations[0].get("body_mass_kg", 70.0))
        estimated_mass = base_mass + sum(max(0.0, float(sim.get("body_mass_kg", 0.0))) * 0.35
                                         for sim in source_simulations[1:])
        numeric_fields = {
            "body_mass_kg": body_mass_kg,
            "body_length_m": body_length_m,
            "body_width_m": body_width_m,
            "body_height_m": body_height_m,
            "collision_radius_m": collision_radius_m,
        }
        for field_name, raw in numeric_fields.items():
            if raw is None:
                continue
            if isinstance(raw, bool) or not isinstance(raw, (int, float)) or not math.isfinite(float(raw)) or float(raw) <= 0:
                raise PhysicsErrorML(f"anatomy.define_species() {field_name} must be a positive finite number")
            upper = 1e12 if field_name == "body_mass_kg" else 1e5
            if float(raw) > upper:
                raise PhysicsErrorML(f"anatomy.define_species() {field_name} must not exceed {upper:g}")
            simulation[field_name] = float(raw)
        if len(source_profiles) > 1 and body_mass_kg is None:
            simulation["body_mass_kg"] = estimated_mass
            simulation["physical_model_note"] = "Estimated hybrid mass: primary body mass plus 35% of each additional component; set body_mass_kg explicitly for a designed chimera."
        for field_name in ("body_length_m", "body_width_m", "body_height_m", "collision_radius_m"):
            if field_name not in simulation or len(source_profiles) > 1 and numeric_fields[field_name] is None:
                values = [float(sim.get(field_name, simulation.get(field_name, 0.0)))
                          for sim in source_simulations if isinstance(sim.get(field_name), (int, float)) and sim.get(field_name, 0.0) > 0]
                if values:
                    simulation[field_name] = max(values)
        density = simulation.get("body_density_kg_m3", 990.0)
        if not isinstance(density, (int, float)) or isinstance(density, bool) or not math.isfinite(float(density)) or float(density) <= 0:
            density = 990.0
        simulation["body_density_kg_m3"] = float(density)
        if body_mass_kg is not None or (len(source_profiles) > 1 and body_mass_kg is None):
            simulation["body_volume_m3"] = float(simulation["body_mass_kg"]) / float(density)
        simulation.setdefault("body_mass_kg", base_mass)
        simulation.setdefault("body_volume_m3", float(simulation["body_mass_kg"]) / float(density))
        simulation.setdefault("physical_model_note", "Approximate game-scale baseline; the 2D collider is a circle proxy, not an articulated body or exact species measurement.")

        result = copy.deepcopy(primary)
        result.update({"name": key, "label": name.strip(), "classification": "user-defined-species",
                       "clade": "composite" if len(source_profiles) > 1 else f"custom derivative of {primary.get('label', base)}",
                       "base_species": str(primary.get("name", _key(base, "base"))),
                       "components": source_names, "component_profiles": component_profiles,
                       "component_sources": organ_sources, "composition_warnings": warnings,
                       "trait_merge": trait_merge, "skeleton": skel,
                       "bones": {"type": skel.get("type", "unknown"), "inventory": skel.get("inventory", key), "regions": list(skel.get("regions", [])), "count": skel.get("count")},
                       "movement_mode": move, "movement_capabilities": caps,
                       "thermoregulation": thermo, "traits": traits, "organ_names": organ_names,
                       "systems": systems_map, "special_organs": special, "simulation": simulation,
                       "circulation": (copy.deepcopy(primary.get("circulation", {})) if len(source_profiles) == 1 else
                                       {"type": "composite design assumption", "components": [copy.deepcopy(source.get("circulation", {})) for source in source_profiles], "integration_required": True}),
                       "respiration": (copy.deepcopy(primary.get("respiration", {})) if len(source_profiles) == 1 else
                                       {"type": "composite design assumption", "components": [copy.deepcopy(source.get("respiration", {})) for source in source_profiles], "integration_required": True}),
                       "digestion": (copy.deepcopy(primary.get("digestion", {})) if len(source_profiles) == 1 else
                                     {"type": "composite design assumption", "components": [copy.deepcopy(source.get("digestion", {})) for source in source_profiles], "integration_required": True}),
                       "blood": copy.deepcopy(primary.get("blood", {})),
                       "integument": copy.deepcopy(primary.get("integument", {})),
                       "reproduction": copy.deepcopy(primary.get("reproduction", {})),
                       "evidence": "user-defined composition; inherited biological values are template assumptions"})
        if notes is not None:
            prior_notes = list(primary.get("notes", []))
            result["notes"] = prior_notes + [notes]
        runtime.custom_anatomy_species[key] = copy.deepcopy(result)
        runtime._observe("world.changed", operation="anatomy_species_defined", species=key,
                         base=result["base_species"], components=source_names,
                         organ_count=len(organ_names), movement_capability_count=len(caps),
                         composition_warning_count=len(warnings))
        return copy.deepcopy(result)

    def bind(target: Any, species: Any = "human", *, preserve_injuries: Any = True,
             body_mass_kg: Any = None) -> dict[str, Any]:
        from ..runtime import MagicObject
        if not isinstance(target, MagicObject):
            raise TypeErrorML("anatomy.bind() expects a MANA world object")
        if not (target.properties.get("living") or target.properties.get("is_being") or target.properties.get("is_summoned") or target.properties.get("targetable")):
            raise MagicErrorML("anatomy.bind() requires a living being or target profile, not an ordinary physical object")
        if not target.properties.get("active", True):
            raise MagicErrorML("anatomy.bind() cannot change an inactive entity")
        if getattr(runtime, "_pure_call_depth", 0):
            raise MagicErrorML("anatomy.bind() changes an entity body model; use it in a committed spell")
        if not isinstance(preserve_injuries, bool):
            raise TypeErrorML("anatomy.bind() preserve_injuries must be true or false")
        if body_mass_kg is not None and (isinstance(body_mass_kg, bool) or not isinstance(body_mass_kg, (int, float)) or not math.isfinite(float(body_mass_kg)) or not 0 < float(body_mass_kg) <= 1e12):
            raise PhysicsErrorML("anatomy.bind() body_mass_kg must be positive, finite, and no greater than 1e12")
        selected = _profile(runtime, species)
        props = target.properties
        previous_species_id = props.get("anatomy_species_id")
        previous_blood_max = props.get("blood_volume_max_l")
        previous_blood_current = props.get("blood_volume_l")
        old_anatomy = props.get("anatomy", {})
        if not isinstance(old_anatomy, dict):
            old_anatomy = {}
        current_organs: dict[str, dict[str, Any]] = {}
        for name in selected.get("organ_names", []):
            meta = _organ_record(runtime, name, selected)
            previous = old_anatomy.get(name, {})
            integrity = previous.get("integrity", 1.0) if preserve_injuries and isinstance(previous, dict) else 1.0
            try:
                integrity = float(integrity)
            except (ValueError, TypeError, OverflowError):
                integrity = 1.0
            if not math.isfinite(integrity):
                integrity = 1.0
            entry = {"system": meta.get("system", "magical_specialisation"), "role": meta.get("role", "Species anatomical structure"), "integrity": min(1.0, max(0.0, integrity))}
            for field in ("kind", "bone_region", "bone_group"):
                if field in meta:
                    entry[field] = meta[field]
            if isinstance(previous, dict) and preserve_injuries:
                for field in ("injury_tags", "condition", "notes"):
                    if field in previous:
                        entry[field] = copy.deepcopy(previous[field])
            current_organs[name] = entry
        props["anatomy"] = current_organs
        props["body_model_organs"] = list(selected.get("organ_names", []))
        props["body_systems"] = copy.deepcopy(selected.get("systems", {}))
        props["body_components"] = list(selected.get("components", [selected.get("name", _key(species, "species"))]))
        props["body_component_profiles"] = copy.deepcopy(selected.get("component_profiles", []))
        props["body_component_sources"] = copy.deepcopy(selected.get("component_sources", {}))
        props["body_composition_warnings"] = copy.deepcopy(selected.get("composition_warnings", []))
        props["movement_capabilities"] = _movement_capabilities(selected)
        props["anatomy_species_id"] = selected.get("name", _key(species, "species"))
        props["anatomy_classification"] = selected.get("classification", "custom")
        props["skeleton_type"] = selected.get("skeleton", {}).get("type", "unknown")
        props["movement_mode"] = selected.get("movement_mode", "terrestrial")
        thermo = str(selected.get("thermoregulation", "endothermic")).casefold()
        props["body_thermal_mode"] = "ectothermic" if "ectotherm" in thermo else "endothermic" if "endotherm" in thermo else "custom"
        props.setdefault("body_traits", {"strength": 1.0, "speed": 1.0, "endurance": 1.0, "durability": 1.0,
                                           "senses": 1.0, "reflexes": 1.0, "regeneration": 0.0, "recovery": 1.0})
        props["body_form_traits"] = copy.deepcopy(selected.get("traits", {}))
        props["species"] = selected.get("label", str(species))
        props["body_form"] = selected.get("name", _key(species, "species"))
        props["body_type"] = props["body_form"]
        sim = selected.get("simulation", {})
        # Make clade-specific system models available to physiology extensions; these
        # descriptions do not imply that every organ has a dedicated dynamic solver.
        for source_key, target_key in (("circulation", "body_circulation_model"),
                                       ("respiration", "body_respiration_model"),
                                       ("digestion", "body_digestion_model"),
                                       ("blood", "body_blood_model"),
                                       ("integument", "body_integument_model"),
                                       ("reproduction", "body_reproduction_model")):
            props[target_key] = copy.deepcopy(selected.get(source_key, {}))
        props["body_simulation_profile"] = copy.deepcopy(sim if isinstance(sim, dict) else {})
        if isinstance(sim, dict) and sim.get("body_mass_kg") is not None:
            physical = runtime.apply_body_physical_profile(target, sim, body_mass_kg=float(body_mass_kg) if body_mass_kg is not None else None,
                                                           reset_temperature=(not previous_species_id or previous_species_id != selected.get("name")))
            if body_mass_kg is not None:
                props["body_simulation_profile"]["body_mass_kg"] = float(body_mass_kg)
                props["body_simulation_profile"]["body_volume_m3"] = physical["volume_m3"]
        if isinstance(sim.get("blood_volume_l"), (int, float)) and sim["blood_volume_l"] > 0:
            # Switching an unbound entity to a species is initialisation, not blood loss.
            # Preserve the old relative volume only when there was a real prior body model.
            try:
                old_max = max(0.01, float(previous_blood_max))
                old_current = max(0.0, float(previous_blood_current))
                had_previous_body = isinstance(previous_species_id, str) and bool(previous_species_id.strip())
                remaining_fraction = min(1.0, old_current / old_max) if preserve_injuries and had_previous_body else 1.0
            except (TypeError, ValueError, OverflowError):
                remaining_fraction = 1.0
            props["blood_volume_max_l"] = float(sim["blood_volume_l"])
            props["blood_volume_l"] = float(sim["blood_volume_l"]) * remaining_fraction
        if isinstance(sim.get("body_temperature_c"), (int, float)):
            props["body_temperature_c"] = float(sim["body_temperature_c"])
        props["body_model_initialized"] = True
        runtime._observe("entity.changed", entity=runtime._visual_entity(target), operation="anatomy_bound", species=props["anatomy_species_id"], organ_count=len(current_organs))
        return {"entity": runtime._visual_entity(target), "species": props["species"], "classification": props["anatomy_classification"], "organs_tracked": len(current_organs), "systems": sorted(props["body_systems"]), "skeleton_type": props["skeleton_type"], "components": list(props["body_components"]), "movement_capabilities": list(props["movement_capabilities"]), "body_mass_kg": props.get("body_mass_kg"), "body_volume_m3": props.get("body_volume_m3"), "body_dimensions_m": copy.deepcopy(props.get("body_dimensions_m", {})), "composition_warnings": copy.deepcopy(props["body_composition_warnings"])}

    def track(target: Any, organ_name: Any) -> dict[str, Any]:
        from ..runtime import MagicObject
        if not isinstance(target, MagicObject):
            raise TypeErrorML("anatomy.track() expects a MANA world object")
        props = target.properties
        if not (props.get("living") or props.get("is_being") or props.get("is_summoned") or props.get("targetable") or props.get("life_state") in {"dead", "undead"}):
            raise MagicErrorML("anatomy.track() requires a living being or target profile, not an ordinary physical object")
        if not props.get("active", True):
            raise MagicErrorML("anatomy.track() cannot change an inactive entity")
        if getattr(runtime, "_pure_call_depth", 0):
            raise MagicErrorML("anatomy.track() changes the entity body model; use it in a committed spell")
        name = _key(organ_name, "track")
        selected_profile = _entity_profile(runtime, target)
        meta = _organ_record(runtime, name, selected_profile)
        anatomy_state = props.get("anatomy")
        if not isinstance(anatomy_state, dict):
            anatomy_state = props["anatomy"] = {}
        if name not in anatomy_state and len(anatomy_state) >= MAX_BODY_STRUCTURES:
            raise PhysicsErrorML("an entity can track at most 1024 individual anatomical structures")
        current_names = props.get("body_model_organs")
        if not isinstance(current_names, list):
            current_names = props["body_model_organs"] = []
        if name not in current_names and len(current_names) >= MAX_BODY_STRUCTURES:
            raise PhysicsErrorML("an entity can track at most 1024 individual anatomical structures")
        systems = props.get("body_systems")
        if not isinstance(systems, dict):
            systems = props["body_systems"] = {}
        system = meta.get("system", "magical_specialisation")
        members = systems.get(system)
        if not isinstance(members, list):
            members = systems[system] = []
        if name not in members and len(members) >= MAX_BODY_STRUCTURES:
            raise PhysicsErrorML("a body system can track at most 1024 anatomical structures")
        # All validation above is completed before mutating the entity.
        anatomy_state.setdefault(name, {"system": system, "role": meta.get("role", "Tracked structure"), "integrity": 1.0})
        if name not in current_names:
            current_names.append(name)
        if name not in members:
            members.append(name)
        runtime._observe("entity.changed", entity=runtime._visual_entity(target), operation="anatomical_structure_tracked", organ=name)
        return copy.deepcopy(anatomy_state[name])

    def audit(species: Any = "human") -> dict[str, Any]:
        """Check a body template's internal references and report design cautions.

        The audit is non-blocking: unusual fictional biology is allowed. Structural
        catalogue errors are separated from warnings that need a designer's decision.
        """
        selected = _profile(runtime, species)
        organ_names = selected.get("organ_names", [])
        systems_map = selected.get("systems", {})
        errors: list[str] = []
        warnings: list[str] = []
        if not isinstance(organ_names, list):
            errors.append("organ_names is not a list")
            organ_names = []
        if len(organ_names) > MAX_BODY_STRUCTURES:
            errors.append("profile exceeds the 1024 addressable-structure limit")
        _counts = Counter(name for name in organ_names if isinstance(name, str))
        duplicates = sorted(name for name, count in _counts.items() if count > 1)
        if duplicates:
            errors.append("duplicate structure ids: " + ", ".join(duplicates[:16]))
        known = set(organ_names)
        if isinstance(systems_map, dict):
            for system_name, members in systems_map.items():
                if not isinstance(members, list):
                    errors.append(f"system '{system_name}' members are not a list")
                    continue
                for member in members:
                    if member not in known:
                        errors.append(f"system '{system_name}' references absent structure '{member}'")
        for item in selected.get("composition_warnings", []):
            if isinstance(item, dict):
                warnings.append(str(item.get("detail", item)))
            else:
                warnings.append(str(item))
        simulation = selected.get("simulation", {})
        if not isinstance(simulation, dict) or not isinstance(simulation.get("body_mass_kg"), (int, float)) or simulation.get("body_mass_kg", 0) <= 0:
            warnings.append("No valid body-mass baseline is declared; movement physics will need an explicit mass or template update.")
        capabilities = _movement_capabilities(selected)
        movement_text = str(selected.get("movement_mode", "")).casefold()
        # Recognise clade-specific flight structures, including insect wing bars,
        # scales, and beetle elytra, not only bird-like wings.
        organs = set(organ_names)
        special_organs = selected.get("special_organs", [])
        if isinstance(special_organs, list):
            organs.update(item for item in special_organs if isinstance(item, str))
        if any(token in movement_text for token in ("flight", "flying", "powered flight")) or "fly" in capabilities:
            flight_structures = {
                "wings", "wing_membrane", "flight_muscles", "air_sacs", "bird_keel",
                "wing_bars", "wingscales", "elytra", "forewings", "hindwings",
                "flight_wings", "flight_feathers", "hummingbird_hover_muscles",
            }
            if not (organs & flight_structures):
                warnings.append("Flight is declared without a recognised anatomical flight structure; this may be intentional magical flight.")
        if selected.get("circulation", {}).get("integration_required"):
            warnings.append("Composite circulation is unresolved. Choose how the donor systems join or are replaced by a magical equivalent.")
        if selected.get("respiration", {}).get("integration_required"):
            warnings.append("Composite respiration is unresolved. Choose a compatible breathing/gas-exchange model or explicit magical support.")
        if selected.get("digestion", {}).get("integration_required"):
            warnings.append("Composite digestion is unresolved. Pick a coherent feeding/digestive path for this creature.")
        return {"species": selected.get("name", _key(species, "audit")),
                "label": selected.get("label", str(species)),
                "valid": not errors, "errors": list(dict.fromkeys(errors)),
                "warnings": list(dict.fromkeys(warnings)),
                "organ_count": len(organ_names), "system_count": len(systems_map) if isinstance(systems_map, dict) else 0,
                "components": copy.deepcopy(selected.get("components", [selected.get("name", _key(species, "audit"))])),
                "movement_capabilities": capabilities,
                "physical_profile": copy.deepcopy(simulation if isinstance(simulation, dict) else {})}

    def inspect(target: Any, organ_name: Any = None) -> dict[str, Any]:
        from ..runtime import MagicObject
        if not isinstance(target, MagicObject):
            raise TypeErrorML("anatomy.inspect() expects a MANA world object")
        props = target.properties
        selected_profile = _entity_profile(runtime, target)
        active = props.get("anatomy", {})
        if not isinstance(active, dict):
            active = {}
        if organ_name is not None:
            key = _key(organ_name, "inspect")
            meta = _organ_record(runtime, key, selected_profile)
            state = copy.deepcopy(active.get(key, {}))
            return {"reference": meta, "state": state, "tracked": bool(state)}
        return {"species": selected_profile.get("label", props.get("species", "being")),
                "classification": props.get("anatomy_classification", selected_profile.get("classification")),
                "body_form": props.get("body_form"), "skeleton_type": props.get("skeleton_type"),
                "tracked_structures": {key: copy.deepcopy(value) for key, value in active.items()},
                "tracked_count": len(active), "systems": copy.deepcopy(props.get("body_systems", selected_profile.get("systems", {})))}

    define_organ.__mana_runtime_operation__ = True
    define_system.__mana_runtime_operation__ = True
    define_species.__mana_runtime_operation__ = True
    bind.__mana_runtime_operation__ = True
    track.__mana_runtime_operation__ = True

    return {
        "species": species,
        "search": search,
        "profile": profile,
        "audit": audit,
        "systems": systems,
        "organs": organs,
        "organ": organ,
        "bones": bones,
        "bone_list": bone_list,
        "bone": bone,
        "tissues": tissues,
        "cell_types": cell_types,
        "blood": blood,
        "define_organ": define_organ,
        "define_system": define_system,
        "define_species": define_species,
        "bind": bind,
        "track": track,
        "inspect": inspect,
    }

