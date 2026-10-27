"""Physical material catalogue and per-world alloy definitions."""
from __future__ import annotations

import copy
import math
import re
from typing import Any

from ..errors import MagicErrorML, PhysicsErrorML, TypeErrorML, UnitErrorML
from ..materials import _complete_material_profile, composition_for_material, physical_material_profile, registered_materials, resolve_element, resolve_material
from ..units import DENSITY, Quantity


_STATES = {"solid", "liquid", "gas", "plasma", "powder"}


def build_library(runtime: Any) -> dict[str, Any]:
    # Capture a single stock snapshot for this Runtime. Public APIs return copies,
    # but search/category/recommend paths scan these private records without deep-
    # copying the full catalogue on every query.
    from .periodic import build_library as build_periodic_library
    periodic_table = build_periodic_library()
    stock_records = registered_materials()
    def _normalise(value: str) -> str:
        return " ".join(value.casefold().replace("_", " ").replace("-", " ").split())

    stock_by_key = {_normalise(str(record.get("name", ""))): record for record in stock_records}
    stock_by_state: dict[str, list[dict[str, Any]]] = {state: [] for state in _STATES}
    stock_by_category: dict[str, list[dict[str, Any]]] = {}
    stock_by_family: dict[str, list[dict[str, Any]]] = {}
    stock_by_subcategory: dict[str, list[dict[str, Any]]] = {}
    stock_by_microstructure: dict[str, list[dict[str, Any]]] = {}
    stock_by_tag: dict[str, list[dict[str, Any]]] = {}
    for _record in stock_records:
        _state = str(_record.get("state", "solid")).casefold()
        if _state in stock_by_state:
            stock_by_state[_state].append(_record)
        _category_key = _normalise(str(_record.get("category", "uncategorised")))
        stock_by_category.setdefault(_category_key, []).append(_record)
        _family_key = _normalise(str(_record.get("family", "other materials")))
        stock_by_family.setdefault(_family_key, []).append(_record)
        _subcategory_key = _normalise(str(_record.get("subcategory", _record.get("category", ""))))
        stock_by_subcategory.setdefault(_subcategory_key, []).append(_record)
        _microstructure_key = _normalise(str(_record.get("microstructure", "")))
        stock_by_microstructure.setdefault(_microstructure_key, []).append(_record)
        for _tag in _record.get("tags", []):
            if isinstance(_tag, str):
                stock_by_tag.setdefault(_normalise(_tag), []).append(_record)
    stock_search_records = []
    for _record in stock_records:
        _haystack = " ".join([
            str(_record.get("name", "")), str(_record.get("category", "")), str(_record.get("family", "")),
            str(_record.get("subcategory", "")), str(_record.get("symbol", "")), str(_record.get("microstructure", "")),
            " ".join(_record.get("tags", [])), " ".join(_record.get("common_uses", [])),
            " ".join(_record.get("aliases", [])),
        ]).casefold()
        stock_search_records.append((_record, _haystack))

    def _internal_records() -> list[dict[str, Any]]:
        return [*stock_records, *runtime.custom_material_profiles.values()]

    def profile(value: Any) -> dict[str, Any]:
        if not isinstance(value, str) or not value.strip():
            raise TypeErrorML("materials.profile() expects a non-empty material name or element symbol")
        key = _normalise(value)
        custom = runtime.custom_material_profiles.get(key)
        indexed = stock_by_key.get(key)
        result = copy.deepcopy(custom) if custom else copy.deepcopy(indexed) if indexed else physical_material_profile(value)
        if result is None:
            raise MagicErrorML(f"unknown physical material '{value}'; check materials.search() or periodic.lookup()")
        element = resolve_element(value)
        result["composition_record"] = copy.deepcopy(result.get("composition_record") or composition_for_material(value, element))
        result["estimated"] = bool(result.get("estimated", False) or result.get("estimated_density", False)
                                   or result.get("estimated_atomic_mass", False))
        return result

    def search(query: Any) -> list[dict[str, Any]]:
        if not isinstance(query, str) or not query.strip():
            raise TypeErrorML("materials.search() expects a non-empty text query")
        key = _normalise(query.strip())
        found: list[dict[str, Any]] = [copy.deepcopy(record) for record, haystack in stock_search_records if key in haystack]
        for record in runtime.custom_material_profiles.values():
            haystack = _normalise(" ".join([str(record.get("name", "")), str(record.get("category", "")), str(record.get("family", "")),
                                  str(record.get("subcategory", "")), str(record.get("symbol", "")), str(record.get("microstructure", "")),
                                  " ".join(record.get("tags", [])), " ".join(record.get("common_uses", [])),
                                  " ".join(record.get("aliases", []))]))
            if key in haystack:
                found.append(copy.deepcopy(record))
        # Exact aliases resolve even when no descriptive field contains the alias.
        if not found:
            canonical = resolve_material(key)
            if canonical is not None:
                result = profile(canonical)
                if result is not None:
                    found.append(result)
        return found[:200]

    def all_profiles() -> list[dict[str, Any]]:
        # Custom names cannot shadow stock materials; sorting a lightweight list
        # of private refs is cheaper than cloning/sorting all records first.
        records = _internal_records()
        records.sort(key=lambda item: str(item.get("name", "")).casefold())
        return [copy.deepcopy(record) for record in records]

    def by_category(category: Any) -> list[dict[str, Any]]:
        if not isinstance(category, str) or not category.strip():
            raise TypeErrorML("materials.by_category() expects a non-empty category")
        needle = _normalise(category)
        if needle in {"", "all", "material"}:
            candidates = list(stock_records)
        else:
            candidate_ids = set()
            candidates = []
            mappings = (stock_by_family, stock_by_category, stock_by_subcategory,
                        stock_by_microstructure, stock_by_tag)
            for mapping in mappings:
                for key, entries in mapping.items():
                    if needle in key:
                        for record in entries:
                            identity = id(record)
                            if identity not in candidate_ids:
                                candidate_ids.add(identity)
                                candidates.append(record)
        def matches(record: dict[str, Any]) -> bool:
            search_fields = [record.get("family", ""), record.get("category", ""),
                             record.get("subcategory", ""), record.get("microstructure", ""),
                             *record.get("tags", [])]
            return any(needle in _normalise(str(field)) for field in search_fields)
        if needle in {"", "all", "material"}:
            custom_candidates = list(runtime.custom_material_profiles.values())
        else:
            custom_candidates = [record for record in runtime.custom_material_profiles.values() if matches(record)]
        return [copy.deepcopy(record) for record in (*candidates, *custom_candidates) if matches(record) or needle in {"", "all", "material"}]

    def by_state(state: Any) -> list[dict[str, Any]]:
        if not isinstance(state, str) or state.casefold().strip() not in _STATES:
            raise MagicErrorML("materials.by_state() state must be solid, liquid, gas, plasma, or powder")
        requested = state.casefold().strip()
        custom_records = [record for record in runtime.custom_material_profiles.values() if record.get("state") == requested]
        return [copy.deepcopy(record) for record in (*stock_by_state[requested], *custom_records)]

    def categories() -> list[str]:
        """Return consolidated top-level families, not hundreds of detailed labels."""
        return sorted({str(record.get("family", "other materials")) for record in _internal_records()}, key=str.casefold)

    def summary() -> dict[str, Any]:
        records = _internal_records()
        by_state_count = {phase: sum(1 for record in records if record.get("state") == phase) for phase in sorted(_STATES)}
        by_family_count: dict[str, int] = {}
        by_subcategory_count: dict[str, int] = {}
        for record in records:
            family = str(record.get("family", "other materials"))
            by_family_count[family] = by_family_count.get(family, 0) + 1
            category = str(record.get("subcategory", record.get("category", "uncategorised")))
            by_subcategory_count[category] = by_subcategory_count.get(category, 0) + 1
        return {"count": len(records), "stock_count": len(stock_records),
                "custom_count": len(runtime.custom_material_profiles),
                "category_count": len(by_family_count), "family_count": len(by_family_count),
                "subcategory_count": len(by_subcategory_count), "state_counts": by_state_count,
                "category_counts": dict(sorted(by_family_count.items(), key=lambda item: item[0].casefold())),
                "subcategory_counts": dict(sorted(by_subcategory_count.items(), key=lambda item: item[0].casefold()))}

    def compare(first: Any, second: Any) -> dict[str, Any]:
        a = profile(first)
        b = profile(second)
        numeric_fields = ("density_kg_m3", "hardness_index", "toughness_index", "strength_mpa",
                          "magnetic_response", "electrical_conductivity", "thermal_conductivity",
                          "corrosion_resistance", "elastic_modulus_gpa", "specific_heat_j_kg_k",
                          "melting_point_k", "boiling_point_k", "thermal_expansion_per_k",
                          "porosity_index", "toxicity_index", "optical_transparency_index",
                          "magical_resonance_index")
        differences = {}
        for field in numeric_fields:
            av, bv = a.get(field), b.get(field)
            if isinstance(av, (int, float)) and not isinstance(av, bool) and isinstance(bv, (int, float)) and not isinstance(bv, bool):
                differences[field] = float(bv) - float(av)
            else:
                differences[field] = None
        return {"first": a, "second": b, "difference_second_minus_first": differences,
                "equal_state": a.get("state") == b.get("state"),
                "estimated_comparison": bool(a.get("estimated", False) or b.get("estimated", False))}

    def recommend(purpose: Any, *, limit: Any = 10) -> list[dict[str, Any]]:
        if not isinstance(purpose, str) or not purpose.strip():
            raise TypeErrorML("materials.recommend() expects a non-empty purpose")
        if isinstance(limit, bool) or not isinstance(limit, int) or not 1 <= limit <= 50:
            raise PhysicsErrorML("materials.recommend() limit must be an integer from 1 to 50")
        words = [word for word in re.findall(r"[a-z0-9]+", purpose.casefold()) if len(word) > 1]
        if not words:
            raise TypeErrorML("materials.recommend() purpose must contain searchable words")
        scored = []
        for record in _internal_records():
            text = " ".join([str(record.get("name", "")), str(record.get("family", "")), str(record.get("category", "")),
                              str(record.get("subcategory", "")), str(record.get("microstructure", "")), " ".join(record.get("tags", [])),
                              " ".join(record.get("common_uses", []))]).casefold()
            score = sum(2 if word in str(record.get("name", "")).casefold() else 1 for word in words if word in text)
            if score:
                scored.append((score, str(record.get("name", "")).casefold(), record))
        scored.sort(key=lambda item: (-item[0], item[1]))
        return [{"score": score, "material": copy.deepcopy(record)} for score, _, record in scored[:limit]]

    def exists(value: Any) -> bool:
        if not isinstance(value, str):
            return False
        return _normalise(value) in runtime.custom_material_profiles or resolve_material(value) is not None

    def define(name: Any, *, density: Any, state: Any = "solid", category: Any = "custom alloy",
               hardness: Any = 0.5, toughness: Any = 0.5, strength: Any = 250.0,
               magnetic_response: Any = 0.0, electrical_conductivity: Any = 0.25,
               thermal_conductivity: Any = 0.25, combustible: Any = False,
               brittle: Any = False, corrosion_resistance: Any = 0.5,
               composition: Any = None, elastic_modulus_gpa: Any = 0.1,
               specific_heat_j_kg_k: Any = 1000.0, melting_point_k: Any = None,
               boiling_point_k: Any = None, thermal_expansion_per_k: Any = 0.00002,
               porosity_index: Any = 0.0, toxicity_index: Any = 0.0,
               optical_transparency_index: Any = 0.0, magical_resonance_index: Any = 0.0,
               tags: Any = None, common_uses: Any = None) -> dict[str, Any]:
        """Register a custom alloy/material in this Runtime only.

        ``composition`` is an optional mass-fraction string like ``"Fe:0.96,C:0.04"``.
        Atomic fractions are derived from the catalogue's representative atomic masses;
        for short-lived elements those masses are approximate game-data estimates.
        Mechanical coefficients are simulation parameters, not certified material data.
        """
        if not isinstance(name, str) or not name.strip():
            raise TypeErrorML("materials.define() name must be non-empty text")
        if getattr(runtime, "_pure_call_depth", 0):
            raise MagicErrorML("materials.define() changes the world catalogue; call it inside an executable spell")
        display_name = " ".join(name.strip().replace("_", " ").split())
        key = _normalise(display_name)
        if len(display_name) > 64 or not re.fullmatch(r"[A-Za-z][A-Za-z0-9 -]*", display_name):
            raise MagicErrorML("materials.define() name must be 1–64 letters, digits, spaces, or hyphens and start with a letter")
        if resolve_element(display_name) or resolve_material(display_name):
            raise MagicErrorML(f"'{display_name}' is already registered; custom materials cannot shadow catalogue entries")
        if key in runtime.custom_material_profiles:
            raise MagicErrorML(f"custom material '{display_name}' is already defined in this world")
        if not isinstance(density, Quantity) or density.dimension != DENSITY:
            raise UnitErrorML("materials.define() density must use density units, e.g. 7800 kg/m^3")
        density_value = float(density.value)
        if not math.isfinite(density_value) or not 0.01 <= density_value <= 100_000:
            raise PhysicsErrorML("materials.define() density must be between 0.01 and 100000 kg/m^3")
        if not isinstance(state, str) or state.casefold() not in _STATES:
            raise MagicErrorML("materials.define() state must be solid, liquid, gas, plasma, or powder")
        if not isinstance(category, str) or not category.strip() or len(category) > 80:
            raise TypeErrorML("materials.define() category must be non-empty text no longer than 80 characters")

        numeric: dict[str, tuple[Any, float, float]] = {
            "hardness_index": (hardness, 0.0, 1.0),
            "toughness_index": (toughness, 0.0, 1.0),
            "strength_mpa": (strength, 0.0, 100_000.0),
            "magnetic_response": (magnetic_response, 0.0, 1.0),
            "electrical_conductivity": (electrical_conductivity, 0.0, 1.0),
            "thermal_conductivity": (thermal_conductivity, 0.0, 1.0),
            "corrosion_resistance": (corrosion_resistance, 0.0, 1.0),
        }
        values: dict[str, float] = {}
        for field_name, (raw, lower, upper) in numeric.items():
            if isinstance(raw, bool) or not isinstance(raw, (int, float)):
                raise TypeErrorML(f"materials.define() {field_name} must be a number")
            number = float(raw)
            if not math.isfinite(number) or not lower <= number <= upper:
                raise PhysicsErrorML(f"materials.define() {field_name} must be between {lower:g} and {upper:g}")
            values[field_name] = number
        extended_numeric: dict[str, tuple[Any, float, float]] = {
            "elastic_modulus_gpa": (elastic_modulus_gpa, 0.0, 2000.0),
            "specific_heat_j_kg_k": (specific_heat_j_kg_k, 0.0, 100000.0),
            "thermal_expansion_per_k": (thermal_expansion_per_k, 0.0, 1.0),
            "porosity_index": (porosity_index, 0.0, 1.0),
            "toxicity_index": (toxicity_index, 0.0, 1.0),
            "optical_transparency_index": (optical_transparency_index, 0.0, 1.0),
            "magical_resonance_index": (magical_resonance_index, 0.0, 1.0),
        }
        for field_name, (raw, lower, upper) in extended_numeric.items():
            if isinstance(raw, bool) or not isinstance(raw, (int, float)):
                raise TypeErrorML(f"materials.define() {field_name} must be a number")
            number = float(raw)
            if not math.isfinite(number) or not lower <= number <= upper:
                raise PhysicsErrorML(f"materials.define() {field_name} must be between {lower:g} and {upper:g}")
            values[field_name] = number
        phase_values = {"melting_point_k": melting_point_k, "boiling_point_k": boiling_point_k}
        for field_name, raw in phase_values.items():
            if raw is None:
                values[field_name] = None
                continue
            if isinstance(raw, bool) or not isinstance(raw, (int, float)) or not math.isfinite(float(raw)) or not 0 <= float(raw) <= 1_000_000:
                raise PhysicsErrorML(f"materials.define() {field_name} must be null or a finite Kelvin value from 0 to 1000000")
            values[field_name] = float(raw)
        if values["melting_point_k"] is not None and values["boiling_point_k"] is not None and values["boiling_point_k"] < values["melting_point_k"]:
            raise PhysicsErrorML("materials.define() boiling_point_k cannot be lower than melting_point_k")
        def validate_labels(raw: Any, label: str) -> list[str]:
            if raw is None:
                return []
            if not isinstance(raw, list) or len(raw) > 32:
                raise TypeErrorML(f"materials.define() {label} must be a list of up to 32 text labels")
            output = []
            for item in raw:
                if not isinstance(item, str) or not item.strip() or len(item.strip()) > 80:
                    raise TypeErrorML(f"materials.define() {label} entries must be non-empty text up to 80 characters")
                normal = item.strip()
                if normal.casefold() not in {value.casefold() for value in output}:
                    output.append(normal)
            return output
        clean_tags = validate_labels(tags, "tags")
        clean_uses = validate_labels(common_uses, "common_uses")
        if not isinstance(combustible, bool) or not isinstance(brittle, bool):
            raise TypeErrorML("materials.define() combustible and brittle must be true or false")

        composition_record = None
        if composition is not None:
            if not isinstance(composition, str) or len(composition) > 512:
                raise TypeErrorML("materials.define() composition must be text such as 'Fe:0.96,C:0.04'")
            entries = []
            seen_symbols = set()
            for part in composition.split(","):
                bits = part.strip().split(":")
                if len(bits) != 2:
                    raise MagicErrorML("composition entries must use Symbol:mass_fraction, separated by commas")
                element = resolve_element(bits[0].strip())
                if element is None:
                    raise MagicErrorML(f"unknown element symbol/name in custom composition: '{bits[0].strip()}'")
                if element.symbol in seen_symbols:
                    raise MagicErrorML(f"element {element.symbol} appears more than once in custom composition")
                try:
                    fraction = float(bits[1].strip())
                except ValueError as exc:
                    raise TypeErrorML("composition mass fractions must be numeric") from exc
                if not math.isfinite(fraction) or fraction <= 0 or fraction > 1:
                    raise PhysicsErrorML("composition mass fractions must be greater than 0 and at most 1")
                seen_symbols.add(element.symbol)
                atomic_mass = element.atomic_mass_u
                if atomic_mass is None or not math.isfinite(float(atomic_mass)) or atomic_mass <= 0:
                    raise MagicErrorML(f"periodic data for {element.symbol} has no usable atomic mass")
                entries.append({"symbol": element.symbol, "atomic_number": element.atomic_number,
                                "atomic_mass_u": float(atomic_mass),
                                "estimated_atomic_mass": bool(element.estimated_atomic_mass),
                                "mass_fraction": fraction, "atomic_fraction": None})
                if len(entries) > 20:
                    raise PhysicsErrorML("custom compositions may contain at most 20 elements")
            total = sum(item["mass_fraction"] for item in entries)
            if abs(total - 1.0) > 0.02:
                raise PhysicsErrorML("custom composition mass fractions must sum to 1.0 (within 0.02)")
            for item in entries:
                item["mass_fraction"] /= total
                item["mole_proportion"] = item["mass_fraction"] / item["atomic_mass_u"]
            mole_total = sum(item["mole_proportion"] for item in entries)
            for item in entries:
                item["atomic_fraction"] = item["mole_proportion"] / mole_total
                item.pop("mole_proportion", None)
            composition_record = {"kind": "custom_alloy", "name": display_name,
                                  "formula": None, "proportion_basis": "mass_fraction_input; atomic_fraction_derived",
                                  "elements": entries, "estimated": True}

        result = {
            "name": display_name, "density_kg_m3": density_value,
            "state": state.casefold(), "category": category.strip(), **values,
            "combustible": combustible, "brittle": brittle, "estimated": True,
            "source": "runtime-defined-game-material",
            "thermal_expansion_per_k": values["thermal_expansion_per_k"],
            "porosity_index": values["porosity_index"], "toxicity_index": values["toxicity_index"],
            "optical_transparency_index": values["optical_transparency_index"],
            "magical_resonance_index": values["magical_resonance_index"],
            "microstructure": category.strip(), "property_scope": "user-defined gameplay coefficient; not certified engineering data",
            "tags": clean_tags or [category.strip().casefold(), state.casefold()],
            "common_uses": clean_uses or ["user-defined crafting", "world simulation"],
        }
        result = _complete_material_profile(result)
        if composition_record is not None:
            result["composition_record"] = composition_record
        runtime.custom_material_profiles[key] = copy.deepcopy(result)
        runtime._observe("world.changed", operation="material_defined", material={k: v for k, v in result.items() if k != "composition_record"})
        return copy.deepcopy(result)

    define.__mana_runtime_operation__ = True

    def count() -> int:
        return len(stock_records) + len(runtime.custom_material_profiles)

    return {
        "profile": profile,
        "search": search,
        "all": all_profiles,
        "by_category": by_category,
        "by_state": by_state,
        "categories": categories,
        "summary": summary,
        "compare": compare,
        "recommend": recommend,
        "exists": exists,
        "define": define,
        "count": count,
        "periodic": periodic_table,
        "elements": periodic_table,
    }
