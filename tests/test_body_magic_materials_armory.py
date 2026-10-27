from __future__ import annotations

import pytest

from magiclang.errors import MagicErrorML, PhysicsErrorML, TypeErrorML
from magiclang.lexer import Lexer
from magiclang.parser import Parser
from magiclang.physics import Vector3
from magiclang.runtime import Runtime
from magiclang.units import DENSITY, FORCE, KG, M, Quantity, S


def execute(source: str, runtime: Runtime | None = None) -> Runtime:
    runtime = runtime or Runtime()
    program = Parser(Lexer(source, "<body-material-test>").tokenize(), "<body-material-test>").parse()
    runtime.execute(program)
    return runtime


def summoned_being() -> tuple[Runtime, object]:
    runtime = execute('''load planes
planes.open_path("Wild Realm", "Mortal Plane")
spell call_griffin():
    griffin = summon "Griffin" from "Wild Realm"
    incant griffin

cast call_griffin
''')
    beings = [obj for obj in runtime.active_objects if obj.properties.get("is_summoned")]
    assert len(beings) == 1
    return runtime, beings[0]


def test_periodic_catalogue_and_custom_alloy_keep_composition_explicit():
    runtime = Runtime()
    materials = runtime._load_library("materials").values
    periodic = runtime._load_library("periodic").values
    assert periodic["count"] == 118
    iron = periodic["lookup"]("Fe")
    assert iron["atomic_number"] == 26
    assert iron["symbol"] == "Fe"

    alloy = materials["define"](
        "Starforged Steel", density=Quantity(7900, DENSITY),
        category="custom alloy", hardness=0.8, toughness=0.75,
        strength=1200, magnetic_response=0.35,
        composition="Fe:0.94,C:0.06",
    )
    composition = alloy["composition_record"]
    assert composition["kind"] == "custom_alloy"
    assert sum(part["mass_fraction"] for part in composition["elements"]) == pytest.approx(1.0)
    assert sum(part["atomic_fraction"] for part in composition["elements"]) == pytest.approx(1.0)
    assert materials["profile"]("starforged steel")["density_kg_m3"] == pytest.approx(7900)
    with pytest.raises(PhysicsErrorML, match="sum to 1.0"):
        materials["define"]("Bad Alloy", density=Quantity(5000, DENSITY), composition="Fe:0.5,C:0.2")


def test_custom_equipment_blueprint_conjures_real_matter_with_slot_and_mass():
    runtime = Runtime()
    materials = runtime._load_library("materials").values
    armory = runtime._load_library("armory").values
    materials["define"]("Moonsteel", density=Quantity(7900, DENSITY),
                         category="custom alloy", magnetic_response=0.4,
                         composition="Fe:0.94,C:0.06")
    known = {item["name"] for item in armory["blueprints"]()}
    assert {"sword", "axe", "spear", "shield", "arrow", "armour"}.issubset(known)

    blueprint = armory["define"](
        "Moonsteel Axe", slot="weapon", material="Moonsteel",
        mass=Quantity(2, KG), shape="polygon", length=Quantity(0.9, M),
        width=Quantity(0.16, M), thickness=Quantity(0.01, M),
        damage_multiplier=2.2, durability=140,
        description="User-defined test axe",
    )
    assert blueprint["custom"] is True
    item = runtime.op_conjure("Moonsteel Axe", name="Test Axe")
    assert item.properties["created_by_conjure"] is True
    assert item.properties["equipment_slot"] == "weapon"
    assert item.properties["material"] == "Moonsteel"
    assert item.properties["mass"].value == pytest.approx(2)
    assert item.properties["durability"] > 0
    assert armory["inspect"](item)["name"] == "Test Axe"


def test_transmutation_updates_material_properties_and_preserves_mass_by_default():
    runtime = Runtime()
    materials = runtime._load_library("materials").values
    materials["define"]("Dense Fantasy Alloy", density=Quantity(9500, DENSITY),
                         category="custom alloy", hardness=0.9, toughness=0.85,
                         magnetic_response=0.6, composition="Fe:0.8,Ni:0.2")
    obj = runtime.op_conjure("Dense Fantasy Alloy", mass=Quantity(4, KG), shape="sphere")
    original_id = obj.object_id
    original_volume = obj.properties["volume"].value
    original_mass = obj.properties["mass"].value

    runtime.op_transmute(obj, "gold")
    assert obj.object_id == original_id
    assert obj.properties["mass"].value == pytest.approx(original_mass)
    assert obj.properties["volume"].value < original_volume
    assert obj.properties["material"] == "Gold"
    assert obj.properties["atomic_number"] == 79
    assert obj.properties["magnetic_response"] == pytest.approx(0.0)


def test_magnetic_field_is_a_bounded_world_record_not_a_visual_spell_name():
    runtime = Runtime()
    metals = runtime._load_library("metals").values
    center = Vector3(0, 0, 0, M)
    record = metals["field"](center, Quantity(1500, FORCE), Quantity(25, M),
                             polarity="attract", duration=Quantity(4, S))
    assert record["radius_m"] == pytest.approx(25)
    assert record["strength_n"] == pytest.approx(1500)
    fields = metals["active_fields"]()
    assert len(fields) == 1
    fields[0]["radius_m"] = 0
    assert metals["active_fields"]()[0]["radius_m"] == pytest.approx(25)
    with pytest.raises(TypeErrorML, match="polarity"):
        metals["field"](center, Quantity(100, FORCE), Quantity(2, M), polarity="sideways")


def test_custom_body_form_transfigures_same_being_and_preserves_body_state():
    runtime, being = summoned_being()
    physiology = runtime._load_library("physiology").values
    initial_id = being.object_id
    physiology["injure"](being, "eyes", 0.2)
    form = physiology["define_form"](
        "Winged Scout",
        organs=["brain", "brainstem", "heart", "blood", "lungs", "skeleton",
                "skeletal_muscles", "skin", "eyes", "wings", "air_sacs"],
        movement_mode="flight-capable",
        trait_factors={"speed": 1.6, "senses": 1.3},
    )
    assert form["movement_mode"] == "flight-capable"
    runtime.op_transfigure(being, "Winged Scout")
    profile = physiology["profile"](being)
    assert being.object_id == initial_id
    assert profile["body_form"] == "winged scout"
    assert being.properties["visual_form"] == "winged scout"
    assert profile["organs"]["eyes"]["integrity"] == pytest.approx(0.8)
    assert "wings" in profile["organs"]


def test_blood_magic_and_death_revival_are_distinct_state_transitions():
    runtime, being = summoned_being()
    physiology = runtime._load_library("physiology").values
    before = physiology["blood_state"](being)
    assert before["volume_l"] > 0

    drawn = physiology["manipulate_blood"](being, "draw", 0.4, amount_l=0.5)
    assert drawn["blood"]["volume_l"] == pytest.approx(before["volume_l"] - 0.5)
    restored = physiology["manipulate_blood"](being, "restore", 0.4, amount_l=0.25)
    assert restored["blood"]["volume_l"] == pytest.approx(before["volume_l"] - 0.25)
    clotted = physiology["manipulate_blood"](being, "clot", 1.0)
    assert clotted["blood"]["loss_rate_lps"] == pytest.approx(0)

    death = physiology["kill"](being, "test spell")
    assert death["life_state"] == "dead"
    assert being.properties["hp"] == 0
    with pytest.raises(MagicErrorML, match="already dead or undead"):
        physiology["kill"](being, "second attempt")
    revived = physiology["revive"](being, vitality=0.5, restore_organs=0.2)
    assert revived["life_state"] == "alive"
    assert revived["hp"] == pytest.approx(being.properties["max_hp"] * 0.5)
    assert being.properties["revival_count"] == 1


def test_body_form_registry_rejects_missing_core_organs_and_invalid_factors():
    runtime = Runtime()
    physiology = runtime._load_library("physiology").values
    with pytest.raises(MagicErrorML, match="brain and heart"):
        physiology["define_form"]("Empty Puppet", organs=["skin", "eyes", "skeleton"])
    with pytest.raises(PhysicsErrorML):
        physiology["define_form"]("Too Fast", organs=["brain", "heart", "skin"],
                                  trait_factors={"speed": 9.0})


def test_body_form_accepts_clade_specific_life_support_instead_of_vertebrate_organs():
    runtime = Runtime()
    physiology = runtime._load_library("physiology").values
    form = physiology["define_form"](
        "Burrowing Annelid",
        organs=["cerebral_ganglia", "ventral_nerve_cord", "aortic_arches",
                "hydrostatic_skeleton", "skin_cuticle", "nephridia"],
        movement_mode="burrowing",
    )
    assert "cerebral_ganglia" in form["vital_structures"]
    assert "aortic_arches" in form["vital_structures"]
    assert "brain" not in form["organs"]
    assert "heart" not in form["organs"]


def test_custom_material_names_normalise_across_materials_and_armory():
    runtime = Runtime()
    materials = runtime._load_library("materials").values
    armory = runtime._load_library("armory").values

    materials["define"]("Moon-Metal", density=Quantity(7200, DENSITY), category="fantasy alloy")

    # Spaces, hyphens, and underscores are interchangeable in lookup names.
    for alias in ("Moon-Metal", "moon metal", "MOON_METAL"):
        assert materials["profile"](alias)["density_kg_m3"] == pytest.approx(7200)
        assert materials["exists"](alias) is True

    assert any(item["name"] == "Moon-Metal" for item in materials["search"]("moon-metal"))
    assert any(item["name"] == "Moon-Metal" for item in materials["by_category"]("all"))
    blueprint = armory["define"]("Moon-Metal Blade", slot="weapon", material="moon_metal")
    assert blueprint["material"] == "Moon-Metal"
    assert armory["inspect"]("moon_metal_blade")["name"] == "moon metal blade"
    created = runtime.op_conjure("Moon-Metal Blade")
    assert created.properties["material"] == "Moon-Metal"


def test_custom_hyphenated_material_is_usable_by_world_creation_and_transmutation():
    runtime = Runtime()
    materials = runtime._load_library("materials").values
    materials["define"]("Moon-Metal", density=Quantity(7200, DENSITY), category="fantasy alloy")

    obj = runtime.op_conjure("Moon-Metal", mass=Quantity(2, KG), name="Moon-Metal Test")
    assert obj.properties["material"] == "Moon-Metal"
    assert obj.properties["density"].value == pytest.approx(7200)

    runtime.op_transmute(obj, "moon_metal")
    assert obj.properties["material"].casefold().replace("-", " ") == "moon metal"
    assert obj.properties["density"].value == pytest.approx(7200)
