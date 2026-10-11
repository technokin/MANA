from __future__ import annotations

import pytest

from magiclang.errors import MagicErrorML, PhysicsErrorML, RuntimeErrorML, TypeErrorML, UnitErrorML
from magiclang.lexer import Lexer
from magiclang.parser import Parser
from magiclang.runtime import Runtime
from magiclang.units import ENERGY


def run(source: str, *, root=None, filename="<input>") -> Runtime:
    runtime = Runtime(project_root=root)
    runtime.execute(Parser(Lexer(source, filename).tokenize(), filename).parse())
    return runtime


def test_plane_catalogue_contains_thirteen_elemental_and_seven_other_planes():
    runtime = run('load planes\nall = planes.all_planes()\n')
    names = runtime.global_env.get("all")
    assert len(names) == 20
    assert names[:13] == [
        "Fire", "Water", "Earth", "Air", "Ice", "Metal", "Thunder", "Life", "Death",
        "Underworld", "Holy", "Shadow", "Void",
    ]
    assert names[13:] == [
        "Mortal Plane", "Hell", "Heaven", "Atlantis", "Fae Paradise", "Lineage Halls", "Wild Realm",
    ]


def test_identify_supports_names_aliases_and_lazy_hell_regions():
    runtime = run('\nload planes\nfire = planes.identify("Fire Plane")\nnaraka = planes.identify("Hell.Naraka")\nother_name = planes.identify("Naraka")\n')
    assert runtime.global_env.get("fire").name == "Fire"
    assert runtime.global_env.get("fire").category == "elemental"
    assert runtime.global_env.get("naraka").qualified_name == "Hell.Naraka"
    assert runtime.global_env.get("other_name").id == "hell.naraka"
    assert "hell" in runtime._library_namespaces
    with pytest.raises(RuntimeErrorML, match="unknown plane or region"):
        run('load planes\nmissing = planes.identify("no such plane")\n')


def test_exists_checks_known_and_unknown_names_and_identity_record_is_compact():
    runtime = run('\nload planes\nfire_exists = planes.exists("Fire")\nregion_exists = planes.exists("Hell.Naraka")\nmissing_exists = planes.exists("No Such Plane")\nfire = planes.identify("Fire")\n')
    assert runtime.global_env.get("fire_exists") is True
    assert runtime.global_env.get("region_exists") is True
    assert runtime.global_env.get("missing_exists") is False
    fire = runtime.global_env.get("fire")
    assert fire.data_library == "elemental_planes"
    assert fire.category == "elemental"
    assert not hasattr(fire, "element")
    assert not hasattr(fire, "spirit_name")
    with pytest.raises(TypeErrorML, match="expects a plane or region name"):
        run('load planes\nplanes.exists(3)\n')


def test_categories_and_same_category_include_region_parent_category():
    runtime = run('\nload planes\nfire_category = planes.category_of("Fire")\nhell_category = planes.category_of("Hell")\nnaraka_category = planes.category_of("Hell.Naraka")\nothers = planes.planes_in("living realm")\nsame = planes.same_category("Hell", "Hell.Naraka")\n')
    assert runtime.global_env.get("fire_category") == "elemental"
    assert runtime.global_env.get("hell_category") == "afterlife"
    assert runtime.global_env.get("naraka_category") == "afterlife"
    assert runtime.global_env.get("others") == ["Atlantis", "Fae Paradise", "Wild Realm"]
    assert runtime.global_env.get("same") is True
    assert run('load planes\nx = planes.planes_in("unknown")\n').global_env.get("x") == []


def test_regions_of_and_parent_of_load_only_the_requested_plane_data():
    runtime = run('\nload planes\nregions = planes.regions_of("Hell")\nnaraka = planes.identify("Hell.Naraka")\nparent = planes.parent_of(naraka)\n')
    assert runtime.global_env.get("regions") == [
        "Hell.Naraka", "Hell.The Ten Courts", "Hell.Yomi Hollows",
    ]
    assert runtime.global_env.get("parent").name == "Hell"
    assert set(runtime._library_namespaces) == {"planes", "hell"}
    with pytest.raises(RuntimeErrorML, match="expects a region"):
        run('load planes\nparent = planes.parent_of("Hell")\n')


def test_one_plane_data_import_does_not_import_other_plane_data_modules():
    import subprocess
    import sys
    from pathlib import Path

    root = Path(__file__).resolve().parents[1]
    code = '\nimport sys\nfrom magiclang.lexer import Lexer\nfrom magiclang.parser import Parser\nfrom magiclang.runtime import Runtime\nruntime = Runtime(project_root=\'\'\'.\'\'\')\nruntime.execute(Parser(Lexer("load planes\\nload atlantis\\n").tokenize()).parse())\nassert "magiclang.libraries.plane_data.atlantis" in sys.modules\nassert "magiclang.libraries.plane_data.wild_realm" not in sys.modules\nassert "magiclang.libraries.plane_data.heaven" not in sys.modules\n'
    result = subprocess.run([sys.executable, "-c", code], cwd=root, text=True, capture_output=True)
    assert result.returncode == 0, result.stderr


def test_drafter_dependency_is_checked_and_library_is_implemented():
    with pytest.raises(RuntimeErrorML, match="drafter needs planes loaded first"):
        run('load drafter\n')
    runtime = run('load planes\nload drafter\n')
    assert "begin" in runtime.global_env.get("drafter").values
    assert "create" in runtime.global_env.get("drafter").values


def test_plane_data_libraries_load_independently_and_dependency_is_enforced():
    with pytest.raises(RuntimeErrorML, match="hell needs planes loaded first"):
        run('load hell\n')
    runtime = run('\nload planes\nload atlantis\nmermaid = atlantis.beings[0]\n')
    assert set(runtime._library_namespaces) == {"planes", "atlantis"}
    mermaid = runtime.global_env.get("mermaid")
    assert mermaid.name == "Mermaid"
    assert mermaid.home_plane == "Atlantis"
    assert mermaid.resistance["Fire"] == 0.0
    assert len(mermaid.resistance) == 24


def test_builtin_beings_have_initial_combat_stats_and_resistance_defaults_to_zero():
    runtime = run('\nload planes\nload atlantis\nmermaid = atlantis.beings[0]\n')
    mermaid = runtime.global_env.get("mermaid")
    assert mermaid.hp == 90
    assert mermaid.max_hp == 90
    assert mermaid.defence == 5
    assert mermaid.attack == 8
    assert all(value == 0.0 for value in mermaid.resistance.values())


def test_plane_data_records_are_isolated_between_runtime_instances():
    first = run('load planes\nload atlantis\nmermaid = atlantis.beings[0]\n')
    second = run('load planes\nload atlantis\nmermaid = atlantis.beings[0]\n')
    first_mermaid = first.global_env.get("mermaid")
    second_mermaid = second.global_env.get("mermaid")
    first_mermaid.resistance["Fire"] = 0.75
    assert second_mermaid.resistance["Fire"] == 0.0


def test_elemental_plane_data_has_one_spirit_per_plane_and_full_resistance_records():
    runtime = run('\nload planes\nload elemental_planes\nspirit = planes.spirit_of("Fire")\nelement = planes.element_of("Thunder")\npermission = planes.has_permission("Fire")\n')
    lib = runtime.global_env.get("elemental_planes")
    assert len(lib.values["planes"]) == 13
    assert len(lib.values["spirits"]) == 13
    spirit = runtime.global_env.get("spirit")
    assert spirit.name == "Fire Spirit"
    assert spirit.kind == "elemental"
    assert spirit.home_plane == "Fire"
    assert len(spirit.resistance) == 24
    assert runtime.global_env.get("element") == "Thunder"
    assert runtime.global_env.get("permission") is True
    assert set(runtime._library_namespaces) == {"planes", "elemental_planes"}


def test_plane_of_returns_beings_home_and_mortal_plane_for_everything_else():
    runtime = run('\nload planes\nload wild_realm\ngr = wild_realm.beings[0]\ncreature_home = planes.plane_of(gr)\nnumber_home = planes.plane_of(5)\nstone = create Earth\nobject_home = planes.plane_of(stone)\n')
    assert runtime.global_env.get("creature_home").name == "Wild Realm"
    assert runtime.global_env.get("number_home").name == "Mortal Plane"
    assert runtime.global_env.get("object_home").name == "Mortal Plane"
    assert "plane" not in runtime.global_env.get("stone").properties


def test_plane_of_rejects_plane_names_and_plane_references():
    with pytest.raises(TypeErrorML, match="not a plane name or plane reference"):
        run('load planes\nhome = planes.plane_of("Fire")\n')
    with pytest.raises(TypeErrorML, match="not a plane name or plane reference"):
        run('load planes\nhome = planes.plane_of(planes.identify("Fire"))\n')


def test_all_non_elemental_plane_data_libraries_hold_only_their_defined_beings():
    runtime = run('\nload planes\nload fae_paradise\nload wild_realm\nelf = fae_paradise.beings[0]\nbeasts = wild_realm.beings\n')
    assert runtime.global_env.get("elf").name == "Elf"
    assert runtime.global_env.get("elf").home_plane == "Fae Paradise"
    names = [being.name for being in runtime.global_env.get("beasts")]
    assert names == ["Griffin", "Werewolf", "Vampire", "Chimera", "Giant", "Orc"]
    assert set(runtime._library_namespaces) == {"planes", "fae_paradise", "wild_realm"}


def test_pathways_are_bidirectional_by_default_and_regions_are_valid_endpoints():
    runtime = run('\nload planes\nopened = planes.open_path("Mortal Plane", "Hell.Naraka")\nforward = planes.is_open("Mortal", "Naraka")\nreverse = planes.is_open("Naraka", "Mortal")\nneighbors = planes.neighbors("Mortal")\n')
    assert runtime.global_env.get("opened") is True
    assert runtime.global_env.get("forward") is True
    assert runtime.global_env.get("reverse") is True
    assert runtime.global_env.get("neighbors") == ["Hell.Naraka"]


def test_one_way_pathways_open_close_and_state_are_deterministic():
    runtime = run('\nload planes\nfirst = planes.open_path("Fire", "Water", one_way=true)\nreverse_before = planes.is_open("Water", "Fire")\nforward = planes.is_open("Fire", "Water")\npaths = planes.paths_of("Fire")\nclosed = planes.close_path("Fire", "Water")\nreverse_after = planes.is_open("Water", "Fire")\nforward_after = planes.is_open("Fire", "Water")\n')
    assert runtime.global_env.get("first") is True
    assert runtime.global_env.get("reverse_before") is False
    assert runtime.global_env.get("forward") is True
    path = runtime.global_env.get("paths")[0]
    assert path["state"] == "open"
    assert path["one_way"] is True
    assert runtime.global_env.get("closed") is True
    assert runtime.global_env.get("reverse_after") is False
    assert runtime.global_env.get("forward_after") is False


def test_pathway_is_stored_as_one_endpoint_direction_state_record():
    runtime = run('\nload planes\nplanes.open_path("Fire", "Water", one_way=true)\n')
    paths = list(runtime._planar_registry.pathways.values())
    assert len(paths) == 1
    path = paths[0]
    assert path.source_id == "fire"
    assert path.destination_id == "water"
    assert path.one_way is True
    assert path.state == "open"
    runtime.execute(Parser(Lexer('load planes\nplanes.close_path("Fire", "Water")\n').tokenize()).parse())
    assert list(runtime._planar_registry.pathways.values())[0].state == "closed"


def test_closing_bidirectional_path_closes_both_directions():
    runtime = run('\nload planes\nplanes.open_path("Fire", "Water")\nclosed = planes.close_path("Fire", "Water")\nleft = planes.is_open("Fire", "Water")\nright = planes.is_open("Water", "Fire")\n')
    assert runtime.global_env.get("closed") is True
    assert runtime.global_env.get("left") is False
    assert runtime.global_env.get("right") is False


def test_find_route_returns_shortest_open_route_and_errors_if_unreachable():
    runtime = run('\nload planes\nplanes.open_path("Mortal Plane", "Air")\nplanes.open_path("Mortal Plane", "Earth")\nplanes.open_path("Air", "Ice")\nplanes.open_path("Earth", "Ice")\nroute = planes.find_route("Mortal", "Ice")\nreach = planes.reachable("Mortal")\n')
    assert runtime.global_env.get("route") == ["Mortal Plane", "Air", "Ice"]
    assert runtime.global_env.get("reach") == ["Air", "Earth", "Ice"]
    with pytest.raises(RuntimeErrorML, match="no open route"):
        run('load planes\nroute = planes.find_route("Mortal", "Ice")\n')


def test_path_events_are_usable_from_when_handlers():
    runtime = run('\nload planes\nopened_events = 0\nclosed_events = 0\nwhen path_opened:\n    opened_events = opened_events + 1\nwhen path_closed:\n    closed_events = closed_events + 1\nplanes.open_path("Mortal", "Fire")\nplanes.close_path("Mortal", "Fire")\n')
    assert runtime.global_env.get("opened_events") == 1
    assert runtime.global_env.get("closed_events") == 1


def test_base_elements_need_no_invocation_and_non_base_elements_do():
    runtime = run('\nload planes\nfire_permission = planes.has_permission("Fire")\nbase_invocation = planes.invoke("Fire")\nunderworld_before = planes.has_permission("Underworld")\ninvoked = planes.invoke("Underworld")\nunderworld_after = planes.has_permission("Underworld")\nrevoked = planes.revoke("Underworld")\nunderworld_final = planes.has_permission("Underworld")\n')
    assert runtime.global_env.get("fire_permission") is True
    assert runtime.global_env.get("base_invocation") is True
    assert runtime.global_env.get("underworld_before") is False
    assert runtime.global_env.get("invoked") is True
    assert runtime.global_env.get("underworld_after") is True
    assert runtime.global_env.get("revoked") is True
    assert runtime.global_env.get("underworld_final") is False
    with pytest.raises(RuntimeErrorML, match="not an elemental plane"):
        run('load planes\nplanes.invoke("Hell")\n')
    with pytest.raises(RuntimeErrorML, match="not an elemental plane"):
        run('load planes\nplanes.element_of("Hell")\n')
    with pytest.raises(RuntimeErrorML, match="not an elemental plane"):
        run('load planes\nplanes.spirit_of("Hell")\n')


def test_send_energy_requires_known_route_units_and_non_base_permission():
    with pytest.raises(MagicErrorML, match="must be invoked"):
        run('\nload planes\nplanes.open_path("Underworld", "Mortal Plane")\nplanes.send_energy(10 J, "Underworld", "Mortal Plane", "Death")\n')
    with pytest.raises(UnitErrorML, match="energy quantity"):
        run('\nload planes\nplanes.open_path("Fire", "Mortal Plane")\nplanes.send_energy(10, "Fire", "Mortal Plane")\n')
    with pytest.raises(RuntimeErrorML, match="no open route"):
        run('\nload planes\nplanes.send_energy(10 J, "Fire", "Mortal Plane")\n')
    with pytest.raises(PhysicsErrorML, match="different source and destination"):
        run('load planes\nplanes.send_energy(10 J, "Fire", "Fire")\n')
    with pytest.raises(PhysicsErrorML, match="finite and non-negative"):
        run('\nload planes\nplanes.open_path("Fire", "Mortal Plane")\nplanes.send_energy(-1 J, "Fire", "Mortal Plane")\n')
    with pytest.raises(TypeErrorML, match="kind must be non-empty text"):
        run('\nload planes\nplanes.open_path("Fire", "Mortal Plane")\nplanes.send_energy(1 J, "Fire", "Mortal Plane", "")\n')
    with pytest.raises(TypeErrorML, match="known elemental energy label"):
        run('\nload planes\nplanes.open_path("Fire", "Mortal Plane")\nplanes.send_energy(1 J, "Fire", "Mortal Plane", "deth")\n')


def test_send_energy_is_balanced_in_the_existing_ledger_and_energy_arrives():
    runtime = run('\nload planes\narrivals = 0\nwhen energy_arrived:\n    arrivals = arrivals + 1\nplanes.open_path("Underworld", "Mortal Plane")\nplanes.invoke("Underworld")\nreceipt = planes.send_energy(500 J, "Underworld", "Mortal Plane", "Death")\ntotal = planes.energy_sent("Underworld", "Mortal Plane")\n')
    receipt = runtime.global_env.get("receipt")
    assert receipt["source"] == "Underworld"
    assert receipt["destination"] == "Mortal Plane"
    assert receipt["amount_j"] == pytest.approx(500)
    assert receipt["kind"] == "Death"
    assert receipt["path"] == ["Underworld", "Mortal Plane"]
    assert runtime.global_env.get("total").dimension == ENERGY
    assert runtime.global_env.get("total").value == pytest.approx(500)
    entry = next(entry for entry in runtime.energy_ledger if entry.get("operation") == "planar_transfer")
    assert entry["source_delta_j"] == pytest.approx(-500)
    assert entry["target_delta_j"] == pytest.approx(500)
    assert entry["delta_j"] == 0
    assert entry["kind"] == "Death"
    assert runtime.energy_input_j == 0
    assert runtime.energy_output_j == 0
    assert runtime.global_env.get("arrivals") == 1


def test_channels_transfer_watts_over_virtual_time_and_stop_when_closed():
    runtime = run('\nload planes\nplanes.open_path("Fire", "Mortal Plane")\nopened = planes.open_channel("Fire", "Mortal Plane", 10 W)\nadvance_time(1 s)\nbefore = planes.energy_sent("Fire", "Mortal Plane")\nstopped = planes.close_channel("Fire", "Mortal Plane")\nadvance_time(1 s)\nfinal_total = planes.energy_sent("Fire", "Mortal Plane")\n')
    assert runtime.global_env.get("opened") is True
    assert runtime.global_env.get("before").value == pytest.approx(10)
    assert runtime.global_env.get("stopped") is True
    assert runtime.global_env.get("final_total").value == pytest.approx(10)


def test_channel_requires_route_power_units_and_non_base_permission():
    with pytest.raises(RuntimeErrorML, match="no open route"):
        run('load planes\nplanes.open_channel("Fire", "Mortal Plane", 1 W)\n')
    with pytest.raises(UnitErrorML, match="measured in watts"):
        run('\nload planes\nplanes.open_path("Fire", "Mortal Plane")\nplanes.open_channel("Fire", "Mortal Plane", 1 J)\n')
    with pytest.raises(MagicErrorML, match="must be invoked"):
        run('\nload planes\nplanes.open_path("Underworld", "Mortal Plane")\nplanes.open_channel("Underworld", "Mortal Plane", 1 W)\n')


def test_invocation_revoke_closes_channels_from_the_non_base_plane():
    runtime = run('\nload planes\nplanes.open_path("Underworld", "Mortal Plane")\nplanes.invoke("Underworld")\nplanes.open_channel("Underworld", "Mortal Plane", 10 W)\nrevoked = planes.revoke("Underworld")\nadvance_time(1 s)\ntotal = planes.energy_sent("Underworld", "Mortal Plane")\n')
    assert runtime.global_env.get("revoked") is True
    assert runtime.global_env.get("total").value == 0


def test_failed_release_rolls_back_pathways_permissions_and_energy_ledger():
    runtime = run('\nload planes\nspldef test_spell():\n    planes.open_path("Mortal", "Fire")\n    planes.send_energy(10 J, "Mortal", "Fire")\n    incant 1 / 0\nrelease(test_spell)\n')
    # release failure must be rolled back; pathway and ledger stay unchanged
    namespace = runtime.global_env.get("planes")
    assert namespace.values["is_open"]("Mortal", "Fire") is False
    assert not [entry for entry in runtime.energy_ledger if entry.get("operation") == "planar_transfer"]


def test_failed_release_rolls_back_lazy_region_registration_and_data_library_cache():
    runtime = run('\nload planes\nspldef fail_after_loading_region():\n    region = planes.identify("Hell.Naraka")\n    incant 1 / 0\nrelease(fail_after_loading_region)\n')
    assert "hell" not in runtime._library_namespaces
    assert not runtime._planar_registry.regions
    runtime.execute(Parser(Lexer('region = planes.identify("Naraka")\n').tokenize()).parse())
    assert runtime.global_env.get("region").qualified_name == "Hell.Naraka"
    assert "hell" in runtime._library_namespaces


def test_plane_and_region_errors_include_file_and_line():
    with pytest.raises(RuntimeErrorML) as exc:
        run('load planes\nroute = planes.identify("unknown")\n', filename="bad_plane.mana")
    assert "bad_plane.mana:2:" in str(exc.value)


def test_every_exported_planes_api_is_documented():
    from pathlib import Path
    from magiclang.libraries.planes import build_library
    doc = (Path(__file__).resolve().parents[1] / "docs" / "current" / "libraries" / "PLANES_LIBRARY.md").read_text(encoding="utf-8")
    api = build_library(Runtime())
    for name in api:
        assert f"planes.{name}(" in doc, name


def test_plane_api_rejects_invalid_region_category_and_path_inputs():
    with pytest.raises(RuntimeErrorML, match=r"regions_of\(\) expects a plane"):
        run('load planes\nplanes.regions_of("Hell.Naraka")\n')
    with pytest.raises(RuntimeErrorML, match="unknown plane or region"):
        run('load planes\nplanes.category_of("Unknown")\n')
    assert run('load planes\nfound = planes.planes_in("not a category")\n').global_env.get("found") == []
    with pytest.raises(RuntimeErrorML, match="unknown plane or region"):
        run('load planes\nplanes.same_category("Fire", "Unknown")\n')
    with pytest.raises(PhysicsErrorML, match="cannot connect.*to itself"):
        run('load planes\nplanes.open_path("Fire", "Fire")\n')
    with pytest.raises(TypeErrorML, match="one_way must be true or false"):
        run('load planes\nplanes.open_path("Fire", "Water", one_way=1)\n')
    with pytest.raises(RuntimeErrorML, match="unknown plane or region"):
        run('load planes\nplanes.is_open("Fire", "Unknown")\n')
    with pytest.raises(RuntimeErrorML, match="unknown plane or region"):
        run('load planes\nplanes.paths_of("Unknown")\n')
    with pytest.raises(RuntimeErrorML, match="unknown plane or region"):
        run('load planes\nplanes.reachable("Unknown")\n')


def test_permission_checks_and_channel_closing_validate_their_inputs():
    with pytest.raises(RuntimeErrorML, match="not an elemental plane"):
        run('load planes\nplanes.has_permission("Hell")\n')
    with pytest.raises(RuntimeErrorML, match="not an elemental plane"):
        run('load planes\nplanes.revoke("Hell")\n')
    runtime = run('load planes\nclosed = planes.close_channel("Fire", "Water")\n')
    assert runtime.global_env.get("closed") is False
    with pytest.raises(PhysicsErrorML, match="finite and positive"):
        run('load planes\nplanes.open_path("Fire", "Water")\nplanes.open_channel("Fire", "Water", 0 W)\n')


def test_all_builtin_beings_have_initial_combat_stats():
    runtime = run('\nload planes\nload elemental_planes\nload atlantis\nload fae_paradise\nload wild_realm\nbeings = elemental_planes.beings + atlantis.beings + fae_paradise.beings + wild_realm.beings\n')
    beings = runtime.global_env.get("beings")
    assert beings
    for being in beings:
        assert being.hp is not None and being.hp >= 0, being.name
        assert being.max_hp is not None and being.max_hp >= being.hp, being.name
        assert being.defence is not None and being.defence >= 0, being.name
        assert being.attack is not None and being.attack >= 0, being.name
        assert all(0.0 <= resistance <= 1.0 for resistance in being.resistance.values()), being.name


def test_randomized_planar_transfers_keep_source_and_destination_deltas_balanced():
    import random

    rng = random.Random(20261011)
    amounts = [round(rng.uniform(0.01, 5000.0), 3) for _ in range(50)]
    source = [
        "load planes",
        'planes.open_path("Underworld", "Mortal Plane")',
        'planes.invoke("Underworld")',
    ]
    source.extend(
        f'planes.send_energy({amount} J, "Underworld", "Mortal Plane", "Death")'
        for amount in amounts
    )
    runtime = run("\n".join(source) + "\n")
    transfers = [entry for entry in runtime.energy_ledger if entry.get("operation") == "planar_transfer"]
    assert len(transfers) == len(amounts)
    for expected, entry in zip(amounts, transfers):
        assert entry["source_delta_j"] == pytest.approx(-expected)
        assert entry["target_delta_j"] == pytest.approx(expected)
        assert entry["delta_j"] == pytest.approx(0.0)
