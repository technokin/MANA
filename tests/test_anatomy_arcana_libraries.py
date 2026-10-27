from __future__ import annotations

import pytest

from magiclang.errors import MagicErrorML, PhysicsErrorML
from magiclang.lexer import Lexer
from magiclang.parser import Parser
from magiclang.runtime import Runtime
from magiclang.libraries.anatomy_data import HUMAN_BONE_RECORDS, ORGANS, SPECIES, SYSTEMS
from magiclang.libraries.physiology import advance_runtime


def execute(source: str, runtime: Runtime | None = None) -> Runtime:
    runtime = runtime or Runtime()
    tree = Parser(Lexer(source, "<anatomy-arcana-test>").tokenize(), "<anatomy-arcana-test>").parse()
    runtime.execute(tree)
    return runtime


def summoned_being() -> tuple[Runtime, object]:
    runtime = execute('''load planes
planes.open_path("Wild Realm", "Mortal Plane")
spell call_griffin():
    griffin = summon "Griffin" from "Wild Realm"
    incant griffin
cast call_griffin
''')
    target = next(obj for obj in runtime.active_objects if obj.properties.get("is_summoned"))
    return runtime, target


def test_anatomy_catalogue_has_expected_scope_and_individually_named_human_bones():
    runtime = Runtime()
    anatomy = runtime._load_library("anatomy").values
    assert len(SYSTEMS) >= 23
    assert len(SPECIES) >= 73
    assert len(ORGANS) >= 616
    records = anatomy["bone_list"]("human")
    assert len(records) == 206
    assert len({item["name"] for item in records}) == 206
    assert sum(item["region"] == "axial" for item in records) == 80
    assert sum(item["region"] == "appendicular" for item in records) == 126
    assert anatomy["bone"]("left_humerus", "human")["group"] == "upper_limbs"
    assert len(HUMAN_BONE_RECORDS) == 206


def test_all_stock_species_have_physical_profiles_and_structurally_valid_anatomy():
    runtime = Runtime()
    anatomy = runtime._load_library("anatomy").values
    for species in SPECIES:
        profile = anatomy["profile"](species)
        simulation = profile["simulation"]
        for field in ("body_mass_kg", "body_length_m", "body_width_m", "body_height_m",
                      "body_density_kg_m3", "body_volume_m3", "collision_radius_m"):
            assert isinstance(simulation[field], (int, float)) and simulation[field] > 0, (species, field)
        audit = anatomy["audit"](species)
        assert audit["valid"], (species, audit["errors"])
    for species in ("bee", "butterfly", "beetle"):
        assert not any("Flight is declared" in item for item in anatomy["audit"](species)["warnings"])


def test_nonhuman_skeletal_catalogue_does_not_invent_bone_counts():
    anatomy = Runtime()._load_library("anatomy").values
    snake = anatomy["bone_list"]("snake")
    bird = anatomy["bone_list"]("eagle")
    worm = anatomy["bone_list"]("earthworm")
    assert len(snake) >= 10 and all(row["count"] is None for row in snake)
    assert "air_sacs" in anatomy["profile"]("eagle")["special_organs"]
    assert len(bird) >= 30 and all(row["count"] is None for row in bird)
    assert worm == []
    assert anatomy["bones"]("eagle")["structures"] == anatomy["profile"]("eagle")["skeletal_structures"]


def test_clade_specific_anatomy_is_not_flattened_into_mammalian_defaults():
    anatomy = Runtime()._load_library("anatomy").values
    cow_names = {row["name"] for row in anatomy["organs"]("cow")}
    worm = anatomy["profile"]("earthworm")
    worm_names = set(worm["organ_names"])
    snake_names = set(anatomy["profile"]("snake")["organ_names"])
    eagle_names = set(anatomy["profile"]("eagle")["organ_names"])
    assert {"rumen", "reticulum", "omasum", "abomasum"} <= cow_names
    assert "tusks" not in anatomy["profile"]("cow")["special_organs"]
    assert {"cerebral_ganglia", "ventral_nerve_cord", "nephridia", "skin_cuticle", "hydrostatic_skeleton"} <= worm_names
    assert "brain" not in worm_names
    assert "diaphragm" not in snake_names
    assert {"lungs", "air_sacs"} <= eagle_names


def test_species_binding_initialises_full_profile_blood_then_preserves_fraction_on_switch():
    runtime, being = summoned_being()
    anatomy = runtime._load_library("anatomy").values
    anatomy["bind"](being, "cow")
    assert being.properties["blood_volume_l"] == pytest.approx(25.0)
    assert being.properties["blood_volume_max_l"] == pytest.approx(25.0)
    being.properties["blood_volume_l"] = 10.0
    anatomy["bind"](being, "human")
    assert being.properties["blood_volume_l"] == pytest.approx(2.0)
    assert being.properties["blood_volume_max_l"] == pytest.approx(5.0)
    anatomy["bind"](being, "cow", preserve_injuries=False)
    assert being.properties["blood_volume_l"] == pytest.approx(25.0)


def test_named_bone_injury_is_tracked_and_affects_body_state():
    runtime, being = summoned_being()
    anatomy = runtime._load_library("anatomy").values
    physiology = runtime._load_library("physiology").values
    anatomy["bind"](being, "human")
    physiology["profile"](being)  # initialise the effective-property state before measuring it
    assert being.properties["anatomy"]["left_humerus"]["kind"] == "individual_bone"
    before = being.properties["body_damage_taken_multiplier"]
    physiology["injure"](being, "left_humerus", 0.8)
    after = being.properties["body_damage_taken_multiplier"]
    assert being.properties["anatomy"]["left_humerus"]["integrity"] == pytest.approx(0.2)
    assert after >= before
    physiology["heal"](being, "left_humerus", 0.3)
    assert being.properties["anatomy"]["left_humerus"]["integrity"] == pytest.approx(0.5)


def test_earthworm_physiology_uses_annelid_structures_not_missing_vertebrate_organs():
    runtime, being = summoned_being()
    anatomy = runtime._load_library("anatomy").values
    physiology = runtime._load_library("physiology").values
    anatomy["bind"](being, "earthworm")
    assert being.properties["body_thermal_mode"] == "ectothermic"
    assert being.properties["body_temperature_c"] == pytest.approx(18.0)
    assert "heart" not in being.properties["anatomy"]
    assert "lungs" not in being.properties["anatomy"]
    physiology["injure"](being, "cerebral_ganglia", 0.25)
    physiology["injure"](being, "skin_cuticle", 0.2)
    advance_runtime(runtime, 0.25, [being])
    assert being.properties["anatomy"]["cerebral_ganglia"]["integrity"] == pytest.approx(0.75)
    assert being.properties["anatomy"]["skin_cuticle"]["integrity"] == pytest.approx(0.8)


def test_custom_species_and_custom_anatomy_are_runtime_local_and_bounded():
    first, _ = summoned_being()
    second = Runtime()
    a = first._load_library("anatomy").values
    a["define_organ"]("aetheric_lobe", system="magical_specialisation", role="A fictional energy-routing organ", substructures=["inner chamber"])
    created = a["define_species"]("Aetherborn", base="human", append_organs=["aetheric_lobe"], strength=1.5, notes="setting-specific")
    assert "aetheric_lobe" in created["organ_names"]
    assert a["profile"]("aetherborn")["traits"]["strength"] == pytest.approx(1.5)
    assert "aetherborn" not in {item["name"] for item in second._load_library("anatomy").values["species"]()}
    with pytest.raises(PhysicsErrorML, match="at most 512"):
        # Avoid writing hundreds of entries; the cap is exercised with a directly prefilled registry.
        first.custom_anatomy_organs.update({f"custom_{i}": {"name": f"custom_{i}"} for i in range(512)})
        a["define_organ"]("too_many_organs", system="custom", role="should be rejected")


def test_arcana_catalogue_has_mystic_and_chaos_magic_aliases_and_world_local_custom_schools():
    first = Runtime()
    second = Runtime()
    arcana = first._load_library("arcana").values
    assert arcana["count"]() >= 24
    assert arcana["school"]("Mystic Magic")["domain"] == "structured spellcraft"
    assert arcana["school"]("Chaos Magic")["domain"] == "probability and unstable rule alteration"
    assert arcana["school"]("mysticism")["name"] == "mystic_magic"
    assert arcana["search"]("reality")
    arcana["define"]("star-threading", label="Star Threading", domain="celestial alignment",
                     description="A local custom school", patterns=["align", "anchor"],
                     limits=["needs a star reference"], counters=["break alignment"], status="user-defined")
    assert arcana["school"]("star threading")["status"] == "user-defined"
    assert second._load_library("arcana").values["count"]() == 24


def test_materials_owns_periodic_table_but_legacy_periodic_alias_still_works():
    runtime = Runtime()
    materials = runtime._load_library("materials").values
    periodic = runtime._load_library("periodic").values
    assert materials["periodic"]["count"] == 118
    assert materials["elements"]["lookup"]("Fe")["name"] == "Iron"
    assert periodic["lookup"]("Fe")["atomic_number"] == 26


def test_native_mana_can_bind_injure_and_inspect_a_species_body():
    source = '''load planes
load anatomy
load physiology
planes.open_path("Wild Realm", "Mortal Plane")
spell bind_and_examine():
    griffin = summon "Griffin" from "Wild Realm"
    anatomy.bind(griffin, "griffin")
    physiology.injure(griffin, "left_humerus", 0.2)
    physiology.injure(griffin, "beak", 0.1)
    anatomy.inspect(griffin, "beak")
    incant griffin
cast bind_and_examine
'''
    runtime = execute(source)
    griffin = next(obj for obj in runtime.active_objects if obj.properties.get("is_summoned"))
    assert griffin.properties["anatomy_species_id"] == "griffin"
    assert griffin.properties["anatomy"]["left_humerus"]["integrity"] == pytest.approx(0.8)
    assert griffin.properties["anatomy"]["beak"]["integrity"] == pytest.approx(0.9)


def test_anatomy_and_arcana_catalogue_mutations_roll_back_after_appraisal():
    source = '''load anatomy
load arcana
spell prepare():
    anatomy.define_organ("temporary_sensor", system="sensory", role="temporary test structure")
    arcana.define("temporary_path", label="Temporary Path", domain="test", description="temporary", patterns=["test"], limits=["bounded"], counters=["stop"], status="temporary")
    incant true
appraise prepare
'''
    runtime = execute(source)
    with pytest.raises(MagicErrorML, match="unknown anatomical structure"):
        runtime._load_library("anatomy").values["organ"]("temporary_sensor", "human")
    with pytest.raises(MagicErrorML, match="unknown magical discipline"):
        runtime._load_library("arcana").values["school"]("temporary_path")


def test_every_stock_species_profile_binds_and_advances_without_host_errors():
    from magiclang.runtime import MagicObject

    runtime = Runtime()
    anatomy = runtime._load_library("anatomy").values
    physiology = runtime._load_library("physiology").values
    profiles = anatomy["species"]()
    assert len(profiles) >= 51
    for profile in profiles:
        being = MagicObject("Being", {"is_being": True, "is_summoned": True, "active": True})
        bound = anatomy["bind"](being, profile["name"])
        assert bound["organs_tracked"] == len(being.properties["anatomy"])
        assert bound["organs_tracked"] <= 1024
        state = physiology["profile"](being)
        assert state["life_state"] == "alive"
        advance_runtime(runtime, 0.05, [being])
        assert 0.0 <= being.properties["oxygen_saturation"] <= 1.0
        assert being.properties["anatomy_species_id"] == profile["name"]


def test_anatomy_track_rejects_inanimate_inactive_and_over_limit_targets_atomically():
    from magiclang.runtime import MagicObject

    runtime = Runtime()
    anatomy = runtime._load_library("anatomy").values
    stone = MagicObject("Earth", {"active": True})
    with pytest.raises(MagicErrorML, match="ordinary physical object"):
        anatomy["track"](stone, "heart")
    inactive = MagicObject("Being", {"is_being": True, "active": False})
    with pytest.raises(MagicErrorML, match="inactive entity"):
        anatomy["track"](inactive, "heart")
    from magiclang.libraries.anatomy_data import MAX_BODY_STRUCTURES
    crowded = MagicObject("Being", {
        "is_being": True,
        "active": True,
        "body_model_organs": [f"existing_{index}" for index in range(MAX_BODY_STRUCTURES)],
        "anatomy": {},
        "body_systems": {},
    })
    with pytest.raises(PhysicsErrorML, match=f"at most {MAX_BODY_STRUCTURES}"):
        anatomy["track"](crowded, "heart")
    assert crowded.properties["anatomy"] == {}
    assert len(crowded.properties["body_model_organs"]) == MAX_BODY_STRUCTURES
    assert crowded.properties["body_systems"] == {}


def test_body_physical_profiles_set_mass_dimensions_and_species_specific_collider():
    runtime, being = summoned_being()
    anatomy = runtime._load_library("anatomy").values
    human = anatomy["bind"](being, "human")
    assert human["body_mass_kg"] == pytest.approx(70.0)
    assert being.properties["mass"].value == pytest.approx(70.0)
    assert being.properties["body_dimensions_m"]["height"] == pytest.approx(1.75)
    assert being.properties["collision_radius"].value == pytest.approx(0.36)
    assert being.properties["volume"].value == pytest.approx(70.0 / 985.0)

    worm = anatomy["bind"](being, "earthworm")
    assert worm["body_mass_kg"] == pytest.approx(0.005)
    assert being.properties["mass"].value == pytest.approx(0.005)
    assert being.properties["collision_radius"].value == pytest.approx(0.004)
    assert "brain" not in being.properties["anatomy"]
    assert being.properties["body_respiration_model"]["type"] != "alveolar_lungs"


def test_composite_species_keeps_component_provenance_and_can_be_physically_customised():
    runtime, being = summoned_being()
    anatomy = runtime._load_library("anatomy").values
    hybrid = anatomy["define_species"](
        "Sky Serpent Chimera", base="human", components=["eagle", "snake"],
        movement_mode="flying / slithering / climbing",
        body_mass_kg=100.0, body_length_m=2.4, body_width_m=1.8,
        body_height_m=2.0, collision_radius_m=0.55,
        append_organs=["aetheric_core"] if "aetheric_core" in ORGANS else None,
        strength=1.8, speed=1.7)
    assert hybrid["components"] == ["human", "eagle", "snake"]
    assert {"wings", "air_sacs", "trunk_vertebrae"} <= set(hybrid["organ_names"])
    assert hybrid["simulation"]["body_mass_kg"] == pytest.approx(100.0)
    assert hybrid["simulation"]["body_height_m"] == pytest.approx(2.0)
    assert hybrid["component_sources"]["air_sacs"] == ["eagle"]
    assert hybrid["composition_warnings"]  # incompatible donor systems remain visible

    report = anatomy["audit"]("Sky Serpent Chimera")
    assert report["valid"] is True
    assert report["errors"] == []
    assert any("respiration" in warning.casefold() for warning in report["warnings"])

    anatomy["bind"](being, "Sky Serpent Chimera")
    assert being.properties["mass"].value == pytest.approx(100.0)
    assert being.properties["body_components"] == ["human", "eagle", "snake"]
    assert "fly" in being.properties["movement_capabilities"]
    assert "slither" in being.properties["movement_capabilities"]


def test_anatomy_binding_and_transfiguration_apply_stock_body_physics():
    runtime, being = summoned_being()
    anatomy = runtime._load_library("anatomy").values
    anatomy["bind"](being, "human")
    assert being.properties["mass"].value == pytest.approx(70.0)
    runtime.op_transfigure(being, "eagle", scale=1.0)
    assert being.properties["anatomy_species_id"] == "eagle"
    assert being.properties["mass"].value == pytest.approx(5.0)
    assert being.properties["movement_mode"] == "flight-capable"
    assert "air_sacs" in being.properties["body_model_organs"]


def test_expanded_anatomy_catalogue_covers_added_dinosaurs_and_fantasy_body_plans():
    runtime = Runtime()
    anatomy = runtime._load_library("anatomy").values
    expected = {
        "spinosaurus", "diplodocus", "parasaurolophus", "pachycephalosaurus",
        "pteranodon", "mosasaurus", "western_dragon", "eastern_dragon",
        "minotaur", "ant_worker", "ant_soldier", "ant_queen", "slime",
    }
    profiles = {record["name"]: record for record in anatomy["species"]()}
    assert expected <= set(profiles)
    assert profiles["western_dragon"]["movement_mode"] != profiles["eastern_dragon"]["movement_mode"]
    assert profiles["pteranodon"]["classification"] == "real-species-template"
    assert anatomy["profile"]("slime")["skeleton"]["type"] in {"none", "hydrostatic", "custom"}
    assert anatomy["audit"]()["valid"] is True


def test_every_stock_anatomy_template_audits_without_structural_errors():
    runtime = Runtime()
    anatomy = runtime._load_library("anatomy").values
    profiles = anatomy["species"]()
    assert len(profiles) == len(SPECIES) >= 90
    errors = {
        profile["name"]: anatomy["audit"](profile["name"])["errors"]
        for profile in profiles
        if anatomy["audit"](profile["name"])["errors"]
    }
    assert errors == {}


def test_human_profile_has_deep_regional_anatomy_and_can_exceed_legacy_512_limit():
    from magiclang.libraries.anatomy_data import MAX_BODY_STRUCTURES, SPECIES
    runtime = Runtime()
    anatomy = runtime._load_library("anatomy").values
    human = anatomy["profile"]("human")
    assert len(human["organ_names"]) > 650
    assert len(human["organ_names"]) <= MAX_BODY_STRUCTURES
    required = {
        "prefrontal_cortex", "primary_motor_cortex", "pulmonary_capillary_network",
        "proximal_convoluted_tubules", "brachial_arteries", "masseter",
        "gastric_mucosa", "thyroid_follicles", "left_humerus", "right_femur",
    }
    assert required <= set(human["organ_names"])
    assert len({item.casefold() for item in human["organ_names"]}) == len(human["organ_names"])
    assert len(SPECIES["human"]["organ_names"]) == len(human["organ_names"])


def test_expanded_material_catalogue_search_compare_and_state_indexes():
    runtime = Runtime()
    materials = runtime._load_library("materials").values
    stats = materials["summary"]()
    assert stats["count"] >= 330
    assert stats["stock_count"] >= 330
    for material in ("silica aerogel", "titanium carbide", "liquid nitrogen", "demonsteel", "dragonhide", "carbon fiber"):
        record = materials["profile"](material)
        assert record["name"]
        assert record["density_kg_m3"] > 0
        assert isinstance(record["category"], str) and record["category"]
    assert materials["by_state"]("liquid")
    comparison = materials["compare"]("iron", "aluminium")
    assert "density_kg_m3" in comparison["difference_second_minus_first"]
    assert materials["search"]("fictional")

    # Catalogue consolidation: aliases resolve to canonical profiles rather
    # than inflating the inventory with duplicate material rows.
    all_records = materials["all"]()
    all_names = [str(record["name"]).casefold() for record in all_records]
    assert len(all_names) == len(set(all_names))
    assert stats["count"] == len(all_records)
    families = set(materials["categories"]())
    assert {"metals and alloys", "fictional materials", "rocks, minerals and terrain"} <= families
    assert materials["by_category"]("metals and alloys")
    assert materials["profile"]("mythril")["name"].casefold() == "mithril"
    assert materials["profile"]("adamantine")["name"].casefold() == "adamant"
