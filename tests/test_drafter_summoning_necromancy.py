from __future__ import annotations

import pytest

from magiclang.errors import MagicErrorML, PhysicsErrorML, RuntimeErrorML, TypeErrorML, UnitErrorML
from magiclang.lexer import Lexer
from magiclang.parser import Parser
from magiclang.runtime import Runtime
from magiclang.units import ENERGY, M, Quantity


def run(source: str, *, filename: str = "<input>") -> Runtime:
    runtime = Runtime()
    runtime.execute(Parser(Lexer(source, filename).tokenize(), filename).parse())
    return runtime


def test_drafter_creates_custom_plane_properties_regions_and_beings():
    runtime = run('\nload planes\nload drafter\ndraft = drafter.begin("Crystal Reach", "ordinary", plane_id="crystal_reach")\ndrafter.alias(draft, "Crystal Domain")\ndrafter.set_value(draft, "gravity_factor", 0.5)\ndrafter.set_value(draft, "mana_density", 3)\ndrafter.add_being(draft, "Crystal Drake", "beast", element="Earth", hp=100, max_hp=100, defence=5, attack=20, requirements=["crystal heart"])\ndrafter.set_being(draft, "Crystal Drake", "resistance.Fire", 0.75)\nsub = drafter.add_region(draft, "Lower Reach")\ndrafter.set_value(sub, "pressure_factor", 2)\ndrafter.add_being(sub, "Cavern Wisp", "spirit")\ncrystal = drafter.create(draft)\nexists = planes.exists("Crystal Domain")\ncategory = planes.category_of(crystal)\nprops = drafter.properties_of(crystal)\nbeings = drafter.beings_of(crystal)\nregion = planes.identify("Crystal Reach.Lower Reach")\nregion_props = drafter.properties_of(region)\nregion_beings = drafter.beings_of(region)\n')
    assert runtime.global_env.get("exists") is True
    assert runtime.global_env.get("category") == "ordinary"
    assert runtime.global_env.get("props") == {"gravity_factor": 0.5, "mana_density": 3}
    assert len(runtime.global_env.get("beings")) == 2
    assert runtime.global_env.get("region").qualified_name == "Crystal Reach.Lower Reach"
    assert runtime.global_env.get("region_props") == {"pressure_factor": 2}
    assert len(runtime.global_env.get("region_beings")) == 1
    drake = next(b for b in runtime.global_env.get("beings") if b.name == "Crystal Drake")
    assert drake.home_plane == "Crystal Reach"
    assert drake.resistance["Fire"] == 0.75
    assert runtime.global_env.get("drafter").values["get_value"]("Crystal Reach", "mana_density") == 3
    assert runtime.global_env.get("planes").values["plane_of"](drake).name == "Crystal Reach"
    assert runtime.global_env.get("planes").values["planes_in"]("ordinary") == ["Crystal Reach"]


def test_drafter_is_creator_not_editor_and_closes_a_draft_after_create():
    runtime = run('\nload planes\nload drafter\ndraft = drafter.begin("New Plane")\ndrafter.set_value(draft, "signal", 4)\ncreated = drafter.create(draft)\n')
    with pytest.raises(RuntimeErrorML, match="already been created"):
        runtime.global_env.get("drafter").values["set_value"](runtime.global_env.get("draft"), "signal", 5)
    with pytest.raises(RuntimeErrorML, match="already registered"):
        run('\nload planes\nload drafter\na = drafter.begin("Same Plane", plane_id="same_plane")\nb = drafter.begin("Same Plane", plane_id="same_plane_2")\ndrafter.create(a)\ndrafter.create(b)\n')


def test_drafter_event_failure_rolls_back_registry_data_and_draft_state():
    runtime = Runtime()
    source = '\nload planes\nload drafter\nwhen plane_created:\n    x = 1 / 0\ndraft = drafter.begin("Temporary Plane", plane_id="temporary_plane")\ndrafter.set_value(draft, "value", 2)\ndrafter.create(draft)\n'
    with pytest.raises(PhysicsErrorML):
        runtime.execute(Parser(Lexer(source, "create_failure.mana").tokenize(), "create_failure.mana").parse())
    namespace = runtime.global_env.get("planes")
    assert namespace.values["exists"]("Temporary Plane") is False
    assert runtime._custom_plane_data.get("temporary_plane") is None
    assert runtime.global_env.get("draft").created is False


def test_drafter_validates_custom_values_and_being_resistance():
    with pytest.raises(TypeErrorML, match="custom property name"):
        run('\nload planes\nload drafter\nd = drafter.begin("X")\ndrafter.set_value(d, "not valid", 1)\n')
    with pytest.raises(TypeErrorML, match="from 0 to 1"):
        run('\nload planes\nload drafter\nd = drafter.begin("X")\ndrafter.add_being(d, "B")\ndrafter.set_being(d, "B", "resistance.Fire", 1.5)\n')


def test_summoning_requires_planes_dependency_and_open_route():
    with pytest.raises(RuntimeErrorML, match="summoning needs planes loaded first"):
        run('load summoning\n')
    with pytest.raises(RuntimeErrorML, match="no open route"):
        run('\nload planes\nload summoning\nsummoning.bring("Griffin", "Wild Realm")\n')


def test_summoning_moves_being_record_through_path_and_sets_home_plane():
    runtime = run('\nload planes\nload summoning\nplanes.open_path("Wild Realm", "Mortal Plane")\ngriffin = summoning.bring("Griffin", "Wild Realm")\nhome = planes.plane_of(griffin)\n')
    griffin = runtime.global_env.get("griffin")
    assert griffin.properties["is_being"] is True
    assert griffin.properties["is_summoned"] is True
    assert griffin.properties["home_plane"] == "Wild Realm"
    assert runtime.global_env.get("home").name == "Wild Realm"
    assert "plane" not in griffin.properties
    transfers = [entry for entry in runtime.energy_ledger if entry.get("operation") == "planar_transfer"]
    assert len(transfers) == 1
    assert transfers[0]["source"] == "Wild Realm"
    assert transfers[0]["target"] == "Mortal Plane"
    assert transfers[0]["delta_j"] == 0
    assert runtime.energy_input_j == 0
    assert runtime.energy_output_j == 0


def test_summoning_checks_custom_requirements_and_uses_same_physics_object():
    with pytest.raises(MagicErrorML, match="missing required conditions"):
        run('\nload planes\nload drafter\nload summoning\nd = drafter.begin("Glass World", "ordinary")\ndrafter.add_being(d, "Glass Hound", requirements=["glass token"])\nref = drafter.create(d)\nplanes.open_path(ref, "Mortal Plane")\nsummoning.bring("Glass Hound", ref)\n')
    runtime = run('\nload planes\nload drafter\nload summoning\nload vector3d\nd = drafter.begin("Glass World", "ordinary")\ndrafter.add_being(d, "Glass Hound", requirements=["glass token"])\nref = drafter.create(d)\nplanes.open_path(ref, "Mortal Plane")\npoint3 = vector3d.position(3 m, 4 m, 0 m)\npoint2 = vector3d.planar(point3)\nhound = summoning.bring("Glass Hound", ref, position=point2, requirements=["glass token"])\nobject_position = vector3d.object_vector(hound)\n')
    hound = runtime.global_env.get("hound")
    assert hound.properties["is_being"] is True
    assert hound.properties["home_plane"] == "Glass World"
    pos = runtime.global_env.get("object_position")
    assert (pos.x, pos.y, pos.z) == (3, 4, 0)
    assert "summoning" in runtime._library_namespaces
    assert "vector3d" in runtime._library_namespaces


def test_summoning_rejects_non_planar_3d_world_position():
    with pytest.raises(PhysicsErrorML, match="2D x-y world"):
        run('\nload planes\nload summoning\nload vector3d\nplanes.open_path("Wild Realm", "Mortal Plane")\nposition3 = vector3d.position(1 m, 2 m, 3 m)\nsummoning.bring("Griffin", "Wild Realm", position=position3)\n')


def test_necromancy_requires_planes_but_not_summoning():
    with pytest.raises(RuntimeErrorML, match="necromancy needs planes loaded first"):
        run('load necromancy\n')
    runtime = run('load planes\nload necromancy\n')
    assert "necromancy" in runtime._library_namespaces
    assert "summoning" not in runtime._library_namespaces


def test_necromancy_uses_underworld_energy_to_reanimate_a_local_bone_object():
    runtime = run('\nload planes\nload necromancy\nplanes.open_path("Underworld", "Mortal Plane")\nplanes.invoke("Necro")\nbone = tgset:\n    material = "Bone"\n    state = "solid"\nskeleton = necromancy.reanimate(bone)\nundead = necromancy.is_undead(skeleton)\nhome = planes.plane_of(skeleton)\n')
    skeleton = runtime.global_env.get("skeleton")
    assert runtime.global_env.get("undead") is True
    assert runtime.global_env.get("home").name == "Mortal Plane"
    assert skeleton.properties["is_undead"] is True
    assert skeleton.properties["bound_energy"] == Quantity(0, ENERGY)
    assert skeleton.properties["animation_state"] == "reanimated"
    assert "summoning" not in runtime._library_namespaces
    transfer = [entry for entry in runtime.energy_ledger if entry.get("kind", "").startswith("Necro:")][-1]
    assert transfer["source"] == "Underworld"
    assert transfer["target"] == "Mortal Plane"
    assert transfer["amount_j"] == 100
    assert transfer["delta_j"] == 0


def test_necromancy_requires_an_open_underworld_path_and_does_not_half_reanimate():
    with pytest.raises(RuntimeErrorML, match="no open route"):
        run('\nload planes\nload necromancy\nplanes.invoke("Necro")\nbone = tgset:\n    material = "Bone"\n    state = "solid"\nnecromancy.reanimate(bone)\n')


def test_reanimate_many_validates_duplicates_and_transfers_once():
    runtime = run('\nload planes\nload necromancy\nplanes.open_path("Underworld", "Mortal Plane")\nplanes.invoke("Necro")\na = tgset:\n    material = "Bone"\n    state = "solid"\nb = tgset:\n    material = "Bone"\n    state = "solid"\nskeletons = necromancy.reanimate_many([a, b], name="Guard")\n')
    skeletons = runtime.global_env.get("skeletons")
    assert len(skeletons) == 2
    assert [s.properties["display_name"] for s in skeletons] == ["Guard 1", "Guard 2"]
    transfers = [entry for entry in runtime.energy_ledger if entry.get("kind", "").startswith("Necro:")]
    assert len(transfers) == 1
    assert transfers[0]["amount_j"] == 200
    assert [s.properties["bound_energy"].value for s in skeletons] == [0, 0]
    with pytest.raises(MagicErrorML, match="same body more than once"):
        run('\nload planes\nload necromancy\nplanes.open_path("Underworld", "Mortal Plane")\nplanes.invoke("Necro")\na = tgset:\n    material = "Bone"\n    state = "solid"\nnecromancy.reanimate_many([a, a])\n')


def test_3d_library_documents_and_bridges_vectors_to_shared_2d_objects():
    runtime = run('\nload planes\nload summoning\nload vector3d\nplanes.open_path("Wild Realm", "Mortal Plane")\ngriffin = summoning.bring("Griffin", "Wild Realm", position=vector3d.planar(vector3d.position(2 m, 5 m, 0 m)))\nposition = vector3d.object_vector(griffin)\nplanar_check = vector3d.is_planar(position)\n')
    assert runtime.global_env.get("position").dimension == M
    assert runtime.global_env.get("planar_check") is True


def test_summoning_destination_is_implicit_and_cannot_be_overridden():
    with pytest.raises(TypeErrorML):
        run('\nload planes\nload summoning\nplanes.open_path("Wild Realm", "Mortal Plane")\nsummoning.bring("Griffin", destination="Heaven")\n')


def test_summoning_event_failure_rolls_back_entity_and_energy_ledger():
    runtime = Runtime()
    source = '\nload planes\nload summoning\nplanes.open_path("Wild Realm", "Mortal Plane")\nwhen being_summoned:\n    failure = 1 / 0\nsummoning.bring("Griffin", "Wild Realm")\n'
    with pytest.raises(PhysicsErrorML):
        runtime.execute(Parser(Lexer(source, "summon_failure.mana").tokenize(), "summon_failure.mana").parse())
    assert runtime.active_objects == []
    assert not [entry for entry in runtime.energy_ledger if entry.get("operation") == "planar_transfer"]


def test_necromancy_energy_arrived_failure_rolls_back_transfer_and_body():
    runtime = Runtime()
    source = '\nload planes\nload necromancy\nplanes.open_path("Underworld", "Mortal Plane")\nplanes.invoke("Necro")\nwhen energy_arrived:\n    failure = 1 / 0\nbone = tgset:\n    material = "Bone"\n    state = "solid"\nnecromancy.reanimate(bone)\n'
    with pytest.raises(PhysicsErrorML):
        runtime.execute(Parser(Lexer(source, "necromancy_failure.mana").tokenize(), "necromancy_failure.mana").parse())
    bone = runtime.global_env.get("bone")
    assert bone.properties.get("is_undead", False) is False
    assert bone.properties["bound_energy"] == Quantity(0, ENERGY)
    assert not [entry for entry in runtime.energy_ledger if entry.get("kind", "").startswith("Necro:")]


def test_post_summoning_rolls_back_entity_and_internal_transfer():
    runtime = run('\nload planes\nload summoning\nplanes.open_path("Wild Realm", "Mortal Plane")\nspldef trial_griffin():\n    incant summoning.bring("Griffin", "Wild Realm")\npost(trial_griffin)\n')
    assert runtime.active_objects == []
    assert not [entry for entry in runtime.energy_ledger if entry.get("operation") == "planar_transfer"]


def test_post_reanimation_rolls_back_bound_energy_and_undead_state():
    runtime = run('\nload planes\nload necromancy\nplanes.open_path("Underworld", "Mortal Plane")\nplanes.invoke("Necro")\nbone = tgset:\n    material = "Bone"\n    state = "solid"\nspldef trial_reanimation():\n    incant necromancy.reanimate(bone)\npost(trial_reanimation)\n')
    bone = runtime.global_env.get("bone")
    assert bone.properties.get("is_undead", False) is False
    assert bone.properties["bound_energy"] == Quantity(0, ENERGY)
    assert not [entry for entry in runtime.energy_ledger if entry.get("kind", "").startswith("Necro:")]



def test_cross_plane_api_is_bring_not_summon_and_construct_animation_is_not_builtin():
    runtime = run('load planes\nload summoning\nload necromancy\n')
    summoning_values = runtime.global_env.get("summoning").values
    necromancy_values = runtime.global_env.get("necromancy").values
    assert "bring" in summoning_values
    assert "summon" not in summoning_values
    assert "reanimate" in necromancy_values
    assert "animate_construct" not in necromancy_values


def test_summon_skeleton_is_a_normal_mana_spell_not_a_builtin():
    from pathlib import Path
    root = Path(__file__).resolve().parents[1]
    source = (root / "examples" / "summon_skeleton_spell.mana").read_text(encoding="utf-8")
    runtime = run(source, filename="summon_skeleton_spell.mana")
    skeletons = [obj for obj in runtime.active_objects if obj.properties.get("species") == "Skeleton"]
    assert len(skeletons) == 1
    skeleton = skeletons[0]
    assert skeleton.properties["is_undead"] is True
    assert skeleton.properties["necromantic_mana_type"] == "Necro"
    assert skeleton.properties["material"] == "Bone"
    # The body was formed by the spell, not introduced as pre-existing remains.
    assert skeleton.properties.get("body_present", False) is False


def test_earth_relabelled_as_bone_is_not_a_reanimation_source():
    source = "\n".join([
        'load planes', 'load necromancy',
        'planes.open_path("Underworld", "Mortal Plane")',
        'planes.invoke("Necro")',
        "stone = create Earth", 'stone.material = "Bone"',
        "necromancy.reanimate(stone)",
    ])
    with pytest.raises(MagicErrorML, match="requires an existing object identified"):
        run(source)
