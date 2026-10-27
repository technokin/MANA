from __future__ import annotations

import json
from pathlib import Path
import shutil
import subprocess

import pytest

from magiclang.errors import MagicErrorML, RuntimeErrorML
from magiclang.lexer import Lexer
from magiclang.parser import Parser
from magiclang.runner import run_file
from magiclang.runtime import MagicObject, Runtime

ROOT = Path(__file__).resolve().parents[1]


def execute(source: str, *, record: Path | None = None) -> Runtime:
    runtime = Runtime(project_root=ROOT, observe_file=record)
    runtime.execute(Parser(Lexer(source, "visualiser-test.mana").tokenize(), "visualiser-test.mana").parse())
    return runtime


def read_recording(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def run_webview_harness(recording: Path, *, inspect_motion: bool = False, test_visual_lab: bool = False, huge_viewport: bool = False, test_motion_policy: bool = False, prefers_reduced_motion: bool = False, saved_reduce_motion: bool = False) -> dict:
    node = shutil.which("node")
    if node is None:
        pytest.skip("Node.js is required for the headless Visualiser webview integration test")
    harness = ROOT / "tests" / "visualiser_webview_harness.js"
    viewer = ROOT / "tools" / "mana-visualiser-extension" / "media" / "viewer.js"
    command = [node, str(harness), str(recording), str(viewer)]
    if inspect_motion:
        command.append("--inspect-motion")
    if test_visual_lab:
        command.append("--test-visual-lab")
    if huge_viewport:
        command.append("--huge-viewport")
    if test_motion_policy:
        command.append("--test-motion-policy")
    if prefers_reduced_motion:
        command.append("--prefers-reduced-motion")
    if saved_reduce_motion:
        command.append("--saved-reduce-motion")
    completed = subprocess.run(
        command,
        cwd=ROOT, capture_output=True, text=True, timeout=30,
    )
    assert completed.returncode == 0, completed.stderr or completed.stdout
    lines = [line for line in completed.stdout.splitlines() if line.strip()]
    return json.loads(lines[-1])


def test_recording_contains_scene_events_and_real_contact(tmp_path):
    recording = tmp_path / "fireball.jsonl"
    runtime = Runtime(project_root=ROOT, observe_file=recording)
    try:
        source = (ROOT / "examples" / "fireball_contact.mana").read_text(encoding="utf-8")
        runtime.execute(Parser(Lexer(source, "fireball_contact.mana").tokenize(), "fireball_contact.mana").parse())
    finally:
        runtime.close_observer()

    events = read_recording(recording)
    assert events[0]["type"] == "recording"
    assert all(event["schema"] == 1 for event in events)
    assert any(event["type"] == "entity.created" for event in events)
    assert any(event["type"] == "spell.result" and event["committed"] for event in events)
    contacts = [event for event in events if event["type"] == "contact.begin"]
    assert len(contacts) == 1
    assert set(contacts[0]["names"]) == {"training_knight", "ember"}
    assert contacts[0]["distance_m"] == 0
    assert len(contacts[0]["position"]) == 2
    # The flash uses the contact point at collision time, not the entities' later positions.
    assert contacts[0]["position"][0] == pytest.approx(5.675, abs=0.02)
    assert any(event["type"] == "scene.snapshot" for event in events)


def test_preview_text_is_recorded_as_preview_not_as_a_release(tmp_path, capsys):
    recording = tmp_path / "preview.jsonl"
    runtime = execute('''
spldef try_spell():
    show("A little spark")
    incant 1
post(try_spell)
''', record=recording)
    try:
        output = capsys.readouterr().out
        assert "A little spark" in output
    finally:
        runtime.close_observer()

    events = read_recording(recording)
    preview = [event for event in events if event["type"] == "preview.output"]
    assert preview and preview[0]["label"] == "PREVIEW"
    results = [event for event in events if event["type"] == "spell.result"]
    assert results[-1]["mode"] == "post"
    assert results[-1]["committed"] is False


def test_observation_does_not_change_spell_outcome_or_final_state(tmp_path):
    source = '''
load geometry2d
stone = tgset:
    material = "Rock"
    mass = 1 kg
    volume = 0.001 m3
    pos = geometry2d.point(0 m, 0 m)
velocity(stone, 3 m/s)
advance_time(0.2 s)
'''
    plain = execute(source)
    observed_path = tmp_path / "parity.jsonl"
    observed = execute(source, record=observed_path)
    try:
        plain_stone = plain.global_env.get("stone")
        observed_stone = observed.global_env.get("stone")
        assert observed_stone.properties["pos"].x == pytest.approx(plain_stone.properties["pos"].x)
        assert observed_stone.properties["pos"].y == pytest.approx(plain_stone.properties["pos"].y)
        assert observed_stone.properties["energy"].value == pytest.approx(plain_stone.properties["energy"].value)
    finally:
        observed.close_observer()
    assert read_recording(observed_path)


def test_recording_runner_closes_file_after_execution_error(tmp_path):
    source = tmp_path / "bad.mana"
    recording = tmp_path / "bad.jsonl"
    source.write_text('missing_name\n', encoding="utf-8")
    with pytest.raises(RuntimeErrorML):
        run_file(str(source), observe_file=recording)
    assert recording.is_file()
    with recording.open("a", encoding="utf-8") as stream:
        stream.write("\n")


def test_weave_rejects_unknown_shapes_and_shared_mana_api_uses_same_shape_list():
    with pytest.raises(MagicErrorML, match="unsupported mana construct shape"):
        execute('orb = weave mana:\n    shape = made_up_shape\n')
    with pytest.raises(MagicErrorML, match="unsupported mana construct shape"):
        execute('orb = mana.form("made_up_shape")\n')


def test_build_script_packages_required_visualiser_files():
    script = ROOT / "tools" / "vscode" / "build_mana_visualiser_vsix.py"
    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    output = ROOT / "installers" / "vscode" / f"mana-magic-visualiser-{version}.vsix"
    assert script.is_file()
    assert output.is_file()
    import zipfile
    with zipfile.ZipFile(output) as archive:
        assert archive.testzip() is None
        names = set(archive.namelist())
    assert "extension/extension.js" in names
    assert "extension/media/viewer.js" in names
    assert "extension/media/viewer.css" in names


def test_visualiser_start_maximised_setting_defaults_on_and_can_be_disabled():
    package = json.loads((ROOT / "tools" / "mana-visualiser-extension" / "package.json").read_text(encoding="utf-8"))
    settings = package["contributes"]["configuration"]["properties"]
    assert settings["manaVisualiser.startMaximised"]["default"] is True
    assert "expanded editor group" in settings["manaVisualiser.startMaximised"]["description"]
    extension = (ROOT / "tools" / "mana-visualiser-extension" / "extension.js").read_text(encoding="utf-8")
    assert "config.get('startMaximised', true) !== false" in extension


def test_visualiser_can_fit_large_worlds_without_forcing_close_zoom():
    viewer = (ROOT / "tools" / "mana-visualiser-extension" / "media" / "viewer.js").read_text(encoding="utf-8")
    assert "const MIN_SCENE_SCALE = 1e-12" in viewer
    assert "camera.baseScale = Math.max(MIN_SCENE_SCALE" in viewer
    assert "const scale = Math.max(MIN_SCENE_SCALE" in viewer
    assert "Math.max(12,Math.min((w*.42)/spanX" not in viewer


def test_visualiser_survives_malformed_event_shapes_in_imported_recording(tmp_path):
    """Hand-crafted recordings must not crash the scene while they are replayed."""
    recording = tmp_path / "hostile-shapes.jsonl"
    records = [
        {"schema": 1, "type": "recording", "time": 0},
        {"schema": 1, "type": "contact.begin", "time": 0, "names": None, "entities": {}},
        {"schema": 1, "type": "contact.begin", "time": 0, "names": {}, "entities": []},
        {"schema": 1, "type": "entity.created", "time": 0, "entity": {
            "id": {}, "name": [], "position": {}, "velocity": {}, "mass_kg": {},
            "material": {}, "kind": [], "radius_m": {},
        }},
        {"schema": 1, "type": "entity.changed", "time": 0, "entity": {
            "id": "odd", "position": [{}, None, "not a number"], "velocity": {},
            "mass_kg": [], "name": {}, "material": {}, "kind": "being",
        }, "operation": {}},
        {"schema": 1, "type": "scene.snapshot", "time": 0, "entities": {}, "world": [], "settings": {}},
        {"schema": 1, "type": "mana.event", "time": 0, "name": "being_summoned", "args": {}},
        {"schema": 1, "type": "spell.result", "time": 0, "errors": {}, "mode": []},
        {"schema": 1, "type": "weather.changed", "time": 0, "weather": []},
        {"schema": 1, "type": "weather.changed", "time": 0, "weather": None, "environment": None},
        {"schema": 1, "type": "magic.effect", "time": 0, "effect": "construct_formed", "entity": []},
    ]
    recording.write_text("".join(json.dumps(record) + "\n" for record in records), encoding="utf-8")

    result = run_webview_harness(recording)
    assert result["inputRecords"] == len(records)
    assert result["sceneNoticeVisible"] is False
    assert result["timelineMax"] == len(records) - 2




def test_visualiser_fits_valid_extreme_worlds_below_the_old_zoom_floor(tmp_path):
    recording = tmp_path / "large-valid-world.jsonl"
    records = [
        {"schema": 1, "type": "recording", "time": 0},
        {"schema": 1, "type": "scene.snapshot", "time": 0, "entity_count": 2, "entities": [
            {"id": "west", "name": "West marker", "position": [-1e12, 0], "radius_m": 1, "active": True},
            {"id": "east", "name": "East marker", "position": [1e12, 0], "radius_m": 1, "active": True},
        ]},
    ]
    recording.write_text("".join(json.dumps(record) + "\n" for record in records), encoding="utf-8")

    result = run_webview_harness(recording, inspect_motion=True)

    assert result["sceneBounds"]["maxX"] - result["sceneBounds"]["minX"] > 1.9e12
    assert 0 < result["cameraScale"] < 0.0001
    assert result["renderedObjectCount"] == 2

def test_visualiser_ignores_malformed_and_out_of_range_world_positions(tmp_path):
    """Imported coordinates must not distort scene fitting or expose dead object rows."""
    recording = tmp_path / "out-of-range-coordinates.jsonl"
    records = [
        {"schema": 1, "type": "recording", "time": 0},
        {"schema": 1, "type": "scene.snapshot", "time": 0, "entity_count": 4, "entities": [
            {"id": "normal", "name": "Normal", "position": [7, 4], "radius_m": 0.22, "active": True},
            {"id": "null-coordinates", "name": "Null coordinates", "position": [None, None], "radius_m": 0.22, "active": True},
            {"id": "outside-world", "name": "Outside world", "position": [1e30, -1e30], "radius_m": 0.22, "active": True},
            {"id": "text-coordinate", "name": "String coordinate", "position": ["10", 1], "radius_m": 0.22, "active": True},
        ]},
    ]
    recording.write_text("".join(json.dumps(record) + "\n" for record in records), encoding="utf-8")

    result = run_webview_harness(recording, inspect_motion=True)
    assert result["renderedObjectCount"] == 1
    assert result["selectedDetailName"] == "Normal"
    assert result["sceneBounds"]["maxX"] < 10
    assert result["sceneBounds"]["minY"] > -2
    assert all(__import__("math").isfinite(value) for value in result["sceneBounds"].values())

def test_observer_advance_buffer_is_bounded_and_reports_dropped_events(tmp_path, monkeypatch):
    import magiclang.runtime as runtime_module

    monkeypatch.setattr(runtime_module, "MAX_OBSERVER_BUFFER_RECORDS", 2)
    recording = tmp_path / "bounded.jsonl"
    runtime = Runtime(project_root=ROOT, observe_file=recording)
    try:
        buffer = []
        runtime._observer_buffers.append(buffer)
        runtime._observer_buffer_drops.append(0)
        runtime._observe("activity", label="one")
        runtime._observe("activity", label="two")
        runtime._observe("activity", label="three")
        assert len(buffer) == 2
        dropped = runtime._observer_buffer_drops.pop()
        runtime._observer_buffers.pop()
        runtime._finish_observer_buffer(buffer, commit=True, dropped=dropped)
    finally:
        runtime.close_observer()

    events = read_recording(recording)
    notice = [event for event in events if event["type"] == "recording.notice"]
    assert len(notice) == 1
    assert notice[0]["dropped_events"] == 1


def test_failed_release_recording_does_not_show_uncommitted_entities(tmp_path):
    recording = tmp_path / "failed-release.jsonl"
    runtime = execute('''
spldef broken_spell():
    ember = create Fire
    heat(ember, -5 K)
    incant ember
release(broken_spell)
''', record=recording)
    try:
        assert runtime.global_env.get("broken_spell") is not None
        assert not runtime.active_objects
    finally:
        runtime.close_observer()

    events = read_recording(recording)
    results = [event for event in events if event["type"] == "spell.result"]
    assert results and results[-1]["ok"] is False
    assert results[-1]["committed"] is False
    assert not [event for event in events if event["type"] == "entity.created"]
    snapshots = [event for event in events if event["type"] == "scene.snapshot"]
    assert snapshots and snapshots[-1]["entity_count"] == 0


def test_scene_snapshot_bounds_entity_walk_and_marks_lower_bound(tmp_path):
    recording = tmp_path / "large-scene.jsonl"
    runtime = Runtime(project_root=ROOT, observe_file=recording)
    try:
        runtime.active_objects.extend(MagicObject("Earth") for _ in range(350))
        runtime._observe_scene("test")
    finally:
        runtime.close_observer()

    snapshots = [event for event in read_recording(recording) if event["type"] == "scene.snapshot"]
    assert len(snapshots) == 1
    assert len(snapshots[0]["entities"]) == 300
    assert snapshots[0]["truncated"] is True
    assert snapshots[0]["entity_count_exact"] is False
    assert snapshots[0]["entity_count"] == 301

    # The notice must remain visible in the real replay UI when the scene limit is reached.
    ui = run_webview_harness(recording)
    assert ui["sceneNoticeVisible"] is True
    assert ui["sceneNotice"] == "Showing 300 of 301+ magical objects"


def test_post_visual_records_hypothetical_scene_but_does_not_commit(tmp_path):
    recording = tmp_path / "visual-preview.jsonl"
    runtime = execute('''
load geometry2d
spldef blue_flare():
    orb = weave mana:
        shape = disc
        radius = 0.5 m
        energy = 1400 J
        position = geometry2d.point(2 m, 0 m)
    mana.burst(energy = 700 J, radius = 1 m, position = geometry2d.point(2 m, 0 m))
    incant orb
post(blue_flare, visual)
''', record=recording)
    try:
        assert runtime.active_objects == []
        assert runtime.global_env.get("blue_flare") is not None
    finally:
        runtime.close_observer()

    events = read_recording(recording)
    previews = [event for event in events if event.get("mode") == "post"]
    assert previews
    assert all(event.get("presentation") == "visual" for event in previews if "presentation" in event)
    assert any(event["type"] == "entity.created" for event in previews)
    effect_events = [event for event in previews if event["type"] == "magic.effect"]
    assert any(event.get("effect") == "burst" for event in effect_events)
    assert all(event.get("spell") == "blue_flare" for event in effect_events)
    created = [event for event in previews if event["type"] == "entity.created"]
    assert created and created[-1]["entity"]["name"] == "orb"
    results = [event for event in events if event["type"] == "spell.result"]
    assert results[-1]["presentation"] == "visual"
    assert results[-1]["committed"] is False
    snapshots = [event for event in events if event["type"] == "scene.snapshot"]
    preview_snapshot = next(snapshot for snapshot in snapshots if snapshot["reason"] == "after_post")
    assert preview_snapshot["entity_count"] == 0
    assert preview_snapshot["mode"] == "post"
    assert preview_snapshot["presentation"] == "visual"


def test_post_text_does_not_record_hypothetical_world_animation(tmp_path):
    recording = tmp_path / "text-preview.jsonl"
    runtime = execute('''
spldef text_flare():
    orb = weave mana
    show("This is only a text preview")
    incant orb
post(text_flare)
''', record=recording)
    try:
        assert runtime.active_objects == []
    finally:
        runtime.close_observer()
    events = read_recording(recording)
    assert any(event["type"] == "preview.output" for event in events)
    assert not [event for event in events if event["type"] == "entity.created" and event.get("mode") == "post"]
    assert not [event for event in events if event["type"] == "magic.effect" and event.get("mode") == "post"]
    result = [event for event in events if event["type"] == "spell.result"][-1]
    assert result["presentation"] == "text"
    assert result["committed"] is False


def test_energy_aura_intensity_responds_to_kinetic_energy_not_only_temperature():
    from magiclang.physics import Vector3
    from magiclang.units import VELOCITY

    runtime = Runtime(project_root=ROOT)
    stone = MagicObject("Earth")
    cold_glow = runtime._visual_entity(stone)["energy_glow"]
    stone.properties["vel"] = Vector3(1000, 0, 0, VELOCITY)
    runtime.update_energy(stone)
    moving_glow = runtime._visual_entity(stone)["energy_glow"]
    assert cold_glow == 0
    assert moving_glow > 0.3
    assert stone.properties["temp"].value == pytest.approx(293.15)


def test_tgset_target_profiles_are_anchored_by_default_and_can_be_unanchored():
    runtime = execute('''
fixed = tgset:
    hp = 100
    distance = 6 m
movable = tgset:
    hp = 100
    distance = 8 m
    anchored = false
''')
    try:
        fixed = runtime.global_env.get("fixed")
        movable = runtime.global_env.get("movable")
        assert fixed.properties["anchored"] is True
        assert fixed.properties["anchor_pos"].x == pytest.approx(6)
        assert fixed.properties["targetable"] is True
        assert movable.properties["anchored"] is False
        assert movable.properties["anchor_pos"].x == pytest.approx(8)
    finally:
        runtime.close_observer()


def test_visualiser_exposes_element_palette_shapes_hover_and_playback_modes():
    viewer_source = (ROOT / "tools" / "mana-visualiser-extension" / "media" / "viewer.js").read_text(encoding="utf-8")
    extension_source = (ROOT / "tools" / "mana-visualiser-extension" / "extension.js").read_text(encoding="utf-8")
    for element in ("fire", "water", "earth", "air", "ice", "thunder", "life", "death", "mana", "void", "metal"):
        assert element in viewer_source.lower()
    for shape in ("polygon", "ring", "beam", "cone", "field", "cage", "spiral", "tendril"):
        assert shape in viewer_source.lower()
    assert "mousemove" in viewer_source and "canvas.title" in viewer_source
    assert "effectNames" in viewer_source and "bestEffect.spell" in viewer_source
    assert "Slow motion" in extension_source and "Normal" in extension_source and "Very fast" in extension_source
    assert "Replay" in extension_source and "no portal or plane view" in extension_source
    assert "id=\"focusMode\"" in extension_source and "toggleCharacterView" in viewer_source
    for creature in ("drawHumanoid", "drawDragon", "drawDinosaur", "drawAnt", "drawSlime"):
        assert creature in viewer_source
    assert "zoomBy" in viewer_source and "fitScene" in viewer_source and "pointerDrag" in viewer_source
    assert "drawWizard" in viewer_source and "drawKnight" in viewer_source and "trackProgress" in viewer_source
    assert "weatherFromSpell" not in viewer_source  # weather comes from world state, never spell-name guesses
    assert "function drawWeather" in viewer_source and "weather.changed" in viewer_source
    assert "closeScene" in extension_source and "maximizeScene" in extension_source


def test_visualiser_records_the_full_256_summon_scene_within_viewer_capacity(tmp_path):
    recording = tmp_path / "summon-limit.jsonl"
    source = '''
load planes
load summoning
planes.open_path("Wild Realm", "Mortal Plane")
spldef summon_army():
    for i in span(0, 256):
        last = summoning.bring("Griffin")
    incant 1
release(summon_army)
'''
    runtime = execute(source, record=recording)
    try:
        assert len(runtime.active_objects) == 256
    finally:
        runtime.close_observer()

    events = read_recording(recording)
    results = [event for event in events if event["type"] == "spell.result"]
    snapshots = [event for event in events if event["type"] == "scene.snapshot"]
    contacts = [event for event in events if event["type"] == "contact.begin"]
    assert results and results[-1]["ok"] is True and results[-1]["committed"] is True
    assert len([event for event in events if event["type"] == "entity.created"]) == 256
    final = next(event for event in snapshots if event["reason"] == "after_release")
    assert final["entity_count"] == 256
    assert final["truncated"] is False
    assert len(final["entities"]) == 256
    assert all(entity["summoned"] for entity in final["entities"])
    assert not contacts  # They manifest in place; the runtime must not invent collisions.

    ui = run_webview_harness(recording)
    assert ui["resultBadge"] == "RELEASED"
    assert ui["entityLabelsDrawn"] == 256
    assert ui["finalSpellOK"] is True and ui["finalSpellCommitted"] is True


def test_visualiser_records_summoning_limit_failure_without_partial_army(tmp_path):
    recording = tmp_path / "summon-over-limit.jsonl"
    source = '''
load planes
load summoning
planes.open_path("Wild Realm", "Mortal Plane")
spldef summon_too_many():
    for i in span(0, 257):
        last = summoning.bring("Griffin")
    incant 1
release(summon_too_many)
'''
    runtime = execute(source, record=recording)
    try:
        assert runtime.active_objects == []
    finally:
        runtime.close_observer()

    events = read_recording(recording)
    results = [event for event in events if event["type"] == "spell.result"]
    snapshots = [event for event in events if event["type"] == "scene.snapshot"]
    assert results and results[-1]["ok"] is False and results[-1]["committed"] is False
    assert any("active summoned-being limit (256) reached" in error for error in results[-1]["errors"])
    assert not [event for event in events if event["type"] == "entity.created"]
    final = next(event for event in snapshots if event["reason"] == "after_release")
    assert final["entity_count"] == 0
    assert final["entities"] == []

    ui = run_webview_harness(recording)
    assert ui["resultBadge"] == "FAILED"
    assert ui["entityLabelsDrawn"] == 0
    assert ui["activityContainsLimit"] is True
    assert ui["activityContainsFailure"] is True
    assert ui["finalSpellOK"] is False and ui["finalSpellCommitted"] is False


def test_visualiser_recording_limit_and_large_summon_names_are_bounded(tmp_path):
    from magiclang.observe import MAX_RECORDING_BYTES, MAX_RECORDS, ObservationRecorder

    recording = tmp_path / "bounded-summon-activity.jsonl"
    recorder = ObservationRecorder(recording)
    # More records than the cap should disable recording safely without crashing.
    try:
        for index in range(MAX_RECORDS + 25):
            recorder.write("mana.event", 0, {"name": "being_summoned", "args": [f"Griffin {index}"]})
    finally:
        recorder.close()
    events = read_recording(recording)
    assert len(events) <= MAX_RECORDS + 1  # One header plus at most MAX_RECORDS accepted events.
    assert any("safety limit" in str(event.get("message", "")) for event in events if event["type"] == "recording.notice") or len(events) == MAX_RECORDS + 1
    assert recording.stat().st_size <= MAX_RECORDING_BYTES
    assert all(len(event.get("args", [""])[0]) < 2000 for event in events if event.get("args"))


def test_activity_event_has_nonempty_fallback_label():
    """Avoid blank rows when a recorded event has no human label."""
    viewer = (ROOT / "tools" / "mana-visualiser-extension" / "media" / "viewer.js").read_text(encoding="utf-8")
    assert "text(event.label || 'Activity')" in viewer


def test_shape_operation_uses_the_shared_supported_shape_catalogue():
    runtime = execute('stone = create Earth\nshape(stone, \"circle\")\n')
    assert runtime.global_env.get("stone").properties["shape"] == "circle"
    with pytest.raises(MagicErrorML, match="unsupported shape"):
        execute('stone = create Earth\nshape(stone, \"nonexistent-shape\")\n')


def test_observer_payload_cannot_override_structural_record_fields(tmp_path):
    from magiclang.observe import ObservationRecorder

    path = tmp_path / "fields.jsonl"
    recorder = ObservationRecorder(path)
    recorder.write("world.state", 2.5, {"type": "spoofed", "schema": 999, "time": -100, "ok": True})
    recorder.close()
    event = read_recording(path)[1]
    assert event["type"] == "world.state"
    assert event["schema"] == 1
    assert event["time"] == pytest.approx(2.5)
    assert event["ok"] is True


def test_observer_sanitizer_bounds_dictionary_and_avoids_host_overrides():
    from magiclang.observe import _clean

    cleaned = _clean({str(i): i for i in range(10_000)})
    assert len(cleaned) == 2000

    class HostileDict(dict):
        def items(self):
            raise AssertionError("must not invoke user-defined methods during recording")

    omitted = _clean(HostileDict(value=7))
    assert omitted == "<HostileDict omitted>"


def test_observer_concurrent_writes_keep_record_and_byte_limits_atomic(tmp_path, monkeypatch):
    from concurrent.futures import ThreadPoolExecutor
    import magiclang.observe as observe_module

    monkeypatch.setattr(observe_module, "MAX_RECORDS", 150)
    monkeypatch.setattr(observe_module, "MAX_RECORDING_BYTES", 1024 * 1024)
    path = tmp_path / "parallel.jsonl"
    recorder = observe_module.ObservationRecorder(path)
    try:
        with ThreadPoolExecutor(max_workers=16) as pool:
            futures = [
                pool.submit(recorder.write, "stress.event", float(index), {"sequence": index, "payload": "x" * 30})
                for index in range(2000)
            ]
            for future in futures:
                future.result(timeout=10)
        assert recorder._record_count <= observe_module.MAX_RECORDS
        assert recorder._bytes_written <= observe_module.MAX_RECORDING_BYTES
    finally:
        recorder.close()
    lines = [line for line in path.read_text(encoding="utf-8").splitlines() if line]
    assert len(lines) - 1 <= observe_module.MAX_RECORDS
    assert all(json.loads(line)["type"] == "stress.event" for line in lines[1:])


def test_observer_omits_pathological_integer_from_recording(tmp_path):
    from magiclang.observe import ObservationRecorder

    path = tmp_path / "large-int.jsonl"
    recorder = ObservationRecorder(path)
    try:
        recorder.write("world.state", 0, {"quantity": 10 ** 5000})
    finally:
        recorder.close()
    event = read_recording(path)[1]
    assert event["quantity"] == "[integer omitted: exceeds recording limit]"


def test_observer_sanitizer_bounds_nested_breadth_and_handles_cycles():
    from magiclang.observe import MAX_CLEAN_NODES, _clean

    cyclic = []
    cyclic.extend([cyclic] * 2000)
    cleaned_cycle = _clean(cyclic)
    assert len(cleaned_cycle) == 2000
    assert cleaned_cycle[0] == "[cycle]"

    branch = [0] * 2000
    nested = [branch] * 2000
    cleaned_nested = _clean(nested)
    # A recursive sanitizer must stop at the shared aggregate node budget rather
    # than expanding the nested fan-out toward 2000**2 objects or worse.
    assert cleaned_nested[0][-1] in (0, "[truncated: recording value budget]")
    assert MAX_CLEAN_NODES == 20_000


def test_visualiser_explorer_layers_filters_and_world_summary_work_in_webview_harness(tmp_path):
    recording = tmp_path / "visualiser-ui.mana.jsonl"
    runtime = Runtime(project_root=ROOT, observe_file=recording)
    try:
        source = (ROOT / "examples" / "fireball_contact.mana").read_text(encoding="utf-8")
        runtime.execute(Parser(Lexer(source, "fireball_contact.mana").tokenize(), "fireball_contact.mana").parse())
    finally:
        runtime.close_observer()
    ui = run_webview_harness(recording)
    assert ui["gridInitiallyPressed"] == "true"
    assert ui["gridToggleWorks"] is True
    assert ui["objectNoMatchWorks"] is True
    assert ui["activityNoMatchWorks"] is True
    assert ui["activityJumpWorks"] is True
    assert ui["renderedObjectCount"] >= 1
    assert ui["objectListSemantics"] is True
    assert ui["worldSummaryPresent"] is True


def test_visualiser_does_not_show_raw_coordinates_in_object_explorer():
    viewer = (ROOT / "tools" / "mana-visualiser-extension" / "media" / "viewer.js").read_text(encoding="utf-8")
    assert "object coordinates" not in viewer.lower()
    assert "toFixed(2)}, ${safeNumber(e.position[1]).toFixed(2)}" not in viewer
    assert "physics-enabled" in viewer
    assert "isLivingEntity(entity)" in viewer


def test_visualiser_magic_first_docs_and_accessible_controls_are_linked():
    intro = (ROOT / "MANA_INTRO.md").read_text(encoding="utf-8")
    compendium = ROOT / "docs" / "current" / "foundations" / "MAGIC_SYSTEM_COMPENDIUM.md"
    index = (ROOT / "docs" / "current" / "INDEX.md").read_text(encoding="utf-8")
    viewer = (ROOT / "tools" / "mana-visualiser-extension" / "extension.js").read_text(encoding="utf-8")
    assert "What is a spell?" in intro
    assert "What is summoning?" in intro
    assert "What is a plane?" in intro
    assert compendium.is_file() and compendium.stat().st_size > 20000
    assert "MANA Magic System Compendium" in index
    assert 'aria-label="Scene display controls"' in viewer
    assert 'id="objectSearch"' in viewer and 'id="activitySearch"' in viewer


def test_visualiser_tracks_real_curved_projectile_waypoints(tmp_path):
    """A steering spell must follow recorded bends, not a straight chord."""
    recording = tmp_path / "steering-firebolt.jsonl"
    run_file(str(ROOT / "examples" / "visualiser_steering_firebolt.mana"), observe_file=recording)
    events = read_recording(recording)
    snapshots = [event for event in events if event["type"] == "scene.snapshot"]
    assert len(snapshots) >= 3, "the runtime should record intermediate positions while time advances"

    result = run_webview_harness(recording, inspect_motion=True)
    tracks = result.get("motionTracks") or []
    projectile = next((track for track in tracks if not track["isActor"]), None)
    assert projectile is not None, "the moving Fire object should have a replay track"
    points = projectile["points"]
    assert len(points) >= 4, "the path should preserve intermediate recorded positions"
    directions = []
    for left, right in zip(points, points[1:]):
        dx, dy = right["x"] - left["x"], right["y"] - left["y"]
        if abs(dx) + abs(dy) > .005:
            directions.append(round(__import__("math").atan2(dy, dx), 2))
    assert len(set(directions)) >= 3, "the path should contain several distinct headings"
    sampled = projectile["samplesAtSegments"]
    assert sampled
    assert abs(sampled[len(sampled)//2]["x"] - points[0]["x"]) > .1


def test_visualiser_interpolates_moving_character_and_turns_to_travel_direction(tmp_path):
    recording = tmp_path / "walking-character.jsonl"
    records = [
        {"schema": 1, "type": "recording", "time": 0},
        {"schema": 1, "type": "entity.created", "time": 0, "entity": {
            "id": "npc-1", "name": "Scout", "kind": "being", "visual_form": "humanoid",
            "position": [0, 0], "radius_m": .4, "active": True, "living": True,
        }},
        {"schema": 1, "type": "scene.snapshot", "time": .1, "entities": [{
            "id": "npc-1", "name": "Scout", "kind": "being", "visual_form": "humanoid",
            "position": [1, 0], "radius_m": .4, "active": True, "living": True,
        }]},
        {"schema": 1, "type": "scene.snapshot", "time": .2, "entities": [{
            "id": "npc-1", "name": "Scout", "kind": "being", "visual_form": "humanoid",
            "position": [1.5, .5], "radius_m": .4, "active": True, "living": True,
        }]},
        {"schema": 1, "type": "scene.snapshot", "time": .3, "entities": [{
            "id": "npc-1", "name": "Scout", "kind": "being", "visual_form": "humanoid",
            "position": [1.5, 1.5], "radius_m": .4, "active": True, "living": True,
        }]},
    ]
    recording.write_text("\n".join(json.dumps(event) for event in records) + "\n", encoding="utf-8")
    result = run_webview_harness(recording, inspect_motion=True)
    actor = next((track for track in result.get("motionTracks", []) if track["isActor"]), None)
    assert actor is not None, "characters should have their own motion path"
    assert len(actor["points"]) >= 3
    headings = [sample["angle"] for sample in actor["samplesAtSegments"] if sample.get("moving")]
    assert len(headings) >= 2
    assert any(abs(left - right) > .2 for left, right in zip(headings, headings[1:])), "character facing should respond to a direction change"


def test_visualiser_draws_distinct_effect_shapes_for_supported_magic_events(tmp_path):
    """Real recorded magic events should produce geometry, not just a generic glow."""
    recording = tmp_path / "magic-effects.jsonl"
    records = [
        {"schema": 1, "type": "recording", "time": 0},
        {"schema": 1, "type": "scene.snapshot", "time": 0, "entities": [], "world": {}},
        {"schema": 1, "type": "magic.effect", "time": 0.1, "effect": "beam", "position": [1, 2], "direction": [1, 0], "range_m": 5, "radius_m": 0.2},
        {"schema": 1, "type": "magic.effect", "time": 0.2, "effect": "burst", "position": [3, 2], "radius_m": 2, "element": "Fire"},
        {"schema": 1, "type": "magic.effect", "time": 0.3, "effect": "construct_formed", "entity": {"id": "sigil", "kind": "mana_construct", "name": "Spiral seal", "position": [5, 0], "radius_m": 1, "shape": "spiral", "element": "Mana"}, "shape": "spiral"},
        {"schema": 1, "type": "world.effect", "time": 0.4, "effect": "smoke", "center_m": [2, 3], "radius_m": 1, "duration_s": 4},
        {"schema": 1, "type": "world.effect", "time": 0.5, "effect": "flare", "center_m": [4, 3], "radius_m": 1, "duration_s": 4},
        {"schema": 1, "type": "magic.effect", "time": 0.6, "effect": "transformation", "entity": {"id": "target", "kind": "being", "name": "Transformed target", "position": [4, 2], "material": "crystal", "element": "Earth", "radius_m": 0.5}},
        {"schema": 1, "type": "world.changed", "time": 0.7, "operation": "magnetic_field_created", "field": {"center_m": [3, 3], "radius_m": 2, "strength": 1}},
        {"schema": 1, "type": "contact.begin", "time": 0.8, "position": [3.5, 2], "names": ["target", "sigil"], "entities": []},
    ]
    recording.write_text("".join(json.dumps(item) + "\n" for item in records), encoding="utf-8")
    result = run_webview_harness(recording)
    operations = result["canvasOps"]
    # Beams and ribbons use curves, impacts use radial gradients/rings, and
    # construct seals use explicit geometry. Require several classes of drawing.
    assert operations.get("quadraticCurveTo", 0) > 0
    assert operations.get("createRadialGradient", 0) >= 2
    assert operations.get("arc", 0) > 10
    assert operations.get("lineTo", 0) > 20
    assert operations.get("stroke", 0) > 100


def test_motion_interpolation_uses_world_time_when_snapshot_intervals_are_uneven(tmp_path):
    recording = tmp_path / "uneven-time.jsonl"
    records = [
        {"schema": 1, "type": "recording", "time": 0},
        {"schema": 1, "type": "entity.created", "time": 0, "entity": {"id": "npc", "kind": "being", "name": "walker", "position": [0, 0], "visual_form": "humanoid"}},
        {"schema": 1, "type": "activity", "time": 1, "label": "long wait"},
        {"schema": 1, "type": "scene.snapshot", "time": 1, "entities": [{"id": "npc", "kind": "being", "name": "walker", "position": [1, 0], "visual_form": "humanoid"}]},
        {"schema": 1, "type": "activity", "time": 1.5, "label": "short wait"},
        {"schema": 1, "type": "activity", "time": 2, "label": "short wait"},
        {"schema": 1, "type": "scene.snapshot", "time": 4, "entities": [{"id": "npc", "kind": "being", "name": "walker", "position": [1, 4], "visual_form": "humanoid"}]},
    ]
    recording.write_text("".join(json.dumps(item) + "\n" for item in records), encoding="utf-8")
    result = run_webview_harness(recording, inspect_motion=True)
    track = next(track for track in result["motionTracks"] if track["id"] == "npc")
    final_segment_midpoint = track["samplesAtSegments"][-1]
    # At this log-index midpoint the world clock is t=1.75s, one quarter of
    # the way from t=1 to t=4. Index-only interpolation would incorrectly yield y=2.
    assert final_segment_midpoint["y"] == pytest.approx(1.0, abs=0.02)
    assert final_segment_midpoint["angle"] == pytest.approx(-1.570796, abs=0.02)


def test_long_motion_tracks_keep_recent_steering_and_cap_path_memory(tmp_path):
    recording = tmp_path / "long-curved-path.jsonl"
    records = [{"schema": 1, "type": "recording", "time": 0},
               {"schema": 1, "type": "entity.created", "time": 0,
                "entity": {"id": "bolt", "kind": "object", "name": "Steering bolt", "element": "Fire", "position": [0, 0], "radius_m": 0.1}}]
    for i in range(1, 401):
        if i <= 280:
            x, y = i * .01, 0
        elif i <= 320:
            x, y = 2.8 + (i - 280) * .01, (i - 280) * .01
        else:
            x, y = 3.2, .4 + (i - 320) * .02
        records.append({"schema": 1, "type": "scene.snapshot", "time": i * .1,
                        "entities": [{"id": "bolt", "kind": "object", "name": "Steering bolt", "element": "Fire", "position": [x, y], "radius_m": .1}]})
    recording.write_text("".join(json.dumps(item) + "\n" for item in records), encoding="utf-8")
    result = run_webview_harness(recording, inspect_motion=True)
    track = next(track for track in result["motionTracks"] if track["id"] == "bolt")
    points = track["points"]
    assert len(points) <= 256
    assert points[-1]["x"] == pytest.approx(3.2)
    assert points[-1]["y"] == pytest.approx(2.0)
    # The bend into the final vertical segment must survive history compaction.
    assert any(point["x"] == pytest.approx(3.2) and point["y"] < 1.0 for point in points[-128:])


def test_character_staggers_only_when_recording_contains_a_real_contact(tmp_path):
    base_entity = {"id": "npc", "kind": "being", "name": "Guard", "position": [2, 0], "visual_form": "humanoid", "radius_m": .4}
    plain = tmp_path / "no-contact.jsonl"
    hit = tmp_path / "with-contact.jsonl"
    common = [
        {"schema": 1, "type": "recording", "time": 0},
        {"schema": 1, "type": "entity.created", "time": 0, "entity": base_entity},
    ]
    final_scene = {"schema": 1, "type": "scene.snapshot", "time": .3, "entities": [base_entity]}
    plain.write_text("".join(json.dumps(item) + "\n" for item in [*common, final_scene]), encoding="utf-8")
    contact = {"schema": 1, "type": "contact.begin", "time": .2, "position": [2.1, 0],
               "names": ["Guard", "bolt"], "entities": [base_entity]}
    hit.write_text("".join(json.dumps(item) + "\n" for item in [*common, contact, final_scene]), encoding="utf-8")
    without_hit = run_webview_harness(plain)
    with_hit = run_webview_harness(hit)
    assert with_hit["canvasOps"].get("rotate", 0) > without_hit["canvasOps"].get("rotate", 0)



def test_spell_first_visualiser_shows_spell_body_and_replayable_lifecycle(tmp_path):
    """The spell's silhouette and operation sequence must be visible independently of impact FX."""
    recording = tmp_path / "spell-first.jsonl"
    records = [
        {"schema": 1, "type": "recording", "time": 0},
        {"schema": 1, "type": "spell.started", "time": 0, "spell": "ember_lance", "mode": "release", "presentation": "visual"},
        {"schema": 1, "type": "entity.created", "time": 0.02, "spell": "ember_lance", "entity": {
            "id": "ember-1", "name": "Ember lance", "kind": "projectile", "element": "Fire", "spell_shape": "lance",
            "position": [0, 0], "radius_m": 0.22, "active": True}},
        {"schema": 1, "type": "entity.changed", "time": 0.06, "operation": "velocity", "spell": "ember_lance", "entity": {
            "id": "ember-1", "name": "Ember lance", "kind": "projectile", "element": "Fire", "spell_shape": "lance",
            "position": [1.2, 0.2], "radius_m": 0.22, "active": True}},
        {"schema": 1, "type": "scene.snapshot", "time": 0.12, "entities": [{
            "id": "ember-1", "name": "Ember lance", "kind": "projectile", "element": "Fire", "spell_shape": "lance",
            "position": [2.6, 0.4], "radius_m": 0.22, "active": True}]},
        {"schema": 1, "type": "magic.effect", "time": 0.14, "effect": "beam", "spell": "ember_lance", "position": [2.6, 0.4], "direction": [1, 0.12], "range_m": 4, "radius_m": 0.3, "element": "Fire"},
        {"schema": 1, "type": "contact.begin", "time": 0.2, "position": [4.5, 0.5], "names": ["Ember lance", "training target"], "entities": []},
        {"schema": 1, "type": "spell.result", "time": 0.22, "spell": "ember_lance", "mode": "release", "ok": True, "committed": True},
    ]
    recording.write_text("".join(json.dumps(item) + "\n" for item in records), encoding="utf-8")
    result = run_webview_harness(recording, inspect_motion=True)
    assert result["spellPanelTitle"] == "ember_lance"
    assert result["spellPanelStageCount"] >= 4
    assert result["spellPanelHasHero"] is True
    assert result["spellToggleInitiallyPressed"] == "true"
    assert result["spellToggleWorks"] is True
    assert result["castRecords"] == 1
    assert result["spellTraceRecords"] >= 5
    assert "Casting begins" in result["spellTraceLabels"]
    assert "Directed spell body released" in result["spellTraceLabels"]
    assert result["canvasOps"].get("lineTo", 0) > 80
    assert result["canvasOps"].get("arc", 0) > 20
    assert any(track["spellName"] == "ember_lance" for track in result["motionTracks"])
    assert any("ember lance" in label.lower() for label in result["spellNameLabels"])
    assert result["initialRenderMetrics"]["detailedSpellBodies"] == 1
    assert result["initialRenderMetrics"]["visibleProjectileHeads"] == 1
    assert result["renderMetrics"]["detailedSpellBodies"] <= 96
    assert result["archetypes"] == {"firebolt": "bolt", "iceShield": "field", "waterStream": "wave", "summons": "sigil"}


def test_spell_body_detail_budget_caps_dense_scene_without_discarding_tracks(tmp_path):
    """High-detail spell silhouettes have a per-frame cap in dense recordings."""
    recording = tmp_path / "dense-spell-bodies.jsonl"
    records = [
        {"schema": 1, "type": "recording", "time": 0},
        {"schema": 1, "type": "spell.started", "time": 0, "spell": "dense_firebolts", "mode": "release"},
    ]
    body_count = 130
    for i in range(body_count):
        records.append({"schema": 1, "type": "entity.created", "time": 0.01 + i * .001,
                        "spell": "dense_firebolts", "entity": {
                            "id": f"bolt-{i}", "name": "bolt", "kind": "projectile", "element": "Fire",
                            "shape": "point", "position": [0, 0], "radius_m": .22, "active": True}})
    for i in range(body_count):
        records.append({"schema": 1, "type": "entity.changed", "time": .2 + i * .001,
                        "operation": "velocity", "spell": "dense_firebolts", "entity": {
                            "id": f"bolt-{i}", "name": "bolt", "kind": "projectile", "element": "Fire",
                            "shape": "point", "position": [1, .05], "radius_m": .22, "active": True}})
    records.append({"schema": 1, "type": "spell.result", "time": 1, "spell": "dense_firebolts",
                    "mode": "release", "ok": True, "committed": True})
    recording.write_text("".join(json.dumps(item) + "\n" for item in records), encoding="utf-8")
    result = run_webview_harness(recording, inspect_motion=True)
    metrics = result["initialRenderMetrics"]
    assert metrics["movingTracks"] == body_count
    assert metrics["visibleProjectileHeads"] == body_count
    assert metrics["detailedSpellBodies"] == 96
    assert len(result["motionTracks"]) == body_count


def test_visual_lab_settings_presets_custom_colours_and_accessibility(tmp_path):
    recording = tmp_path / "visual-lab.jsonl"
    records = [
        {"schema": 1, "type": "recording", "time": 0},
        {"schema": 1, "type": "spell.started", "time": 0.1, "spell": "ember_lance", "mode": "release"},
        {"schema": 1, "type": "entity.created", "time": 0.12, "operation": "weave mana", "spell": "ember_lance", "entity": {"id": "visual-lab-bolt", "name": "bolt", "kind": "projectile", "element": "fire", "shape": "point", "position": [1, 1], "radius_m": .22, "active": True}},
        {"schema": 1, "type": "entity.changed", "time": 0.28, "operation": "velocity", "spell": "ember_lance", "entity": {"id": "visual-lab-bolt", "name": "bolt", "kind": "projectile", "element": "fire", "shape": "point", "position": [2, 1.3], "radius_m": .22, "active": True}},
        {"schema": 1, "type": "entity.changed", "time": 0.45, "operation": "velocity", "spell": "ember_lance", "entity": {"id": "visual-lab-bolt", "name": "bolt", "kind": "projectile", "element": "fire", "shape": "point", "position": [3, .8], "radius_m": .22, "active": True}},
        {"schema": 1, "type": "magic.effect", "time": 0.5, "effect": "beam", "spell": "arcane_ray", "element": "mana", "position": [0, 0], "direction": [1, 0], "range_m": 4, "radius_m": .3},
        {"schema": 1, "type": "spell.result", "time": 0.8, "spell": "ember_lance", "mode": "release", "ok": True, "committed": True},
    ]
    recording.write_text("".join(json.dumps(item) + "\n" for item in records), encoding="utf-8")
    result = run_webview_harness(recording, inspect_motion=True, test_visual_lab=True)
    controls = result["visualLabTests"]
    assert controls["panelOpened"] is True
    assert controls["recipeApplied"] is True
    assert controls["drawingModesExercised"] is True
    assert controls["adaptiveBounds"] is True
    assert controls["fxCoreApplied"] is True
    assert controls["paletteThemeCount"] >= 30
    assert controls["spellStyleCount"] >= 12
    assert controls["trailStyleCount"] >= 10
    assert controls["glyphStyleCount"] >= 10
    assert controls["fxColorChannelCount"] == 7
    assert controls["fullPresetApplied"] is True
    assert controls["numericSettingApplied"] is True
    assert controls["accessibilityTogglesApplied"] is True
    assert controls["customColorApplied"] is True
    assert controls["exportMessageSent"] is True
    assert controls["saveMessageSent"] is True
    assert controls["customColorTargetCount"] >= 30
    assert controls["paletteCount"] >= 30


def test_visualiser_uses_adaptive_graphics_without_manual_tiers():
    viewer = (ROOT / "tools" / "mana-visualiser-extension" / "media" / "viewer.js").read_text(encoding="utf-8")
    extension = (ROOT / "tools" / "mana-visualiser-extension" / "extension.js").read_text(encoding="utf-8")
    docs = (ROOT / "docs" / "current" / "tooling" / "MAGIC_VISUALISER.md").read_text(encoding="utf-8")
    assert "const MAX_CANVAS_PIXELS = 4_000_000" in viewer
    assert "MAX_EVENT_CACHE_ENTRIES = 512" in viewer
    assert "MIN_DETAIL_BODIES = 32" in viewer and "MAX_DETAIL_BODIES = 128" in viewer
    assert "delete out.quality" in extension
    assert 'id="quality"' not in extension
    assert "## Automatic resource protection" in docs
    assert "no user-facing graphics tiers" in docs


def test_visualiser_canvas_backing_store_stays_under_pixel_budget_for_extreme_viewport(tmp_path):
    recording = tmp_path / "empty-recording.jsonl"
    recording.write_text(json.dumps({"schema": 1, "type": "recording", "time": 0}) + "\n", encoding="utf-8")
    result = run_webview_harness(recording, inspect_motion=True, huge_viewport=True)
    metrics = result["renderMetrics"]
    assert result["canvasBackingWidth"] * result["canvasBackingHeight"] <= 4_000_000
    assert metrics["canvasPixels"] <= 4_000_000
    assert metrics["estimatedCanvasBytes"] <= 16_000_000


def test_visualiser_caches_motion_path_bounds_across_frames_and_interactions(tmp_path):
    recording = tmp_path / "bounds-cache.jsonl"
    run_file(str(ROOT / "examples" / "visualiser_steering_firebolt.mana"), observe_file=recording)
    result = run_webview_harness(recording, inspect_motion=True, test_visual_lab=True)
    assert result["motionBoundsBuildCount"] == 1
    assert result["motionBoundsCacheStable"] is True


def test_visualiser_resumes_idle_animation_when_reduce_motion_is_disabled(tmp_path):
    recording = tmp_path / "motion-policy.jsonl"
    recording.write_text(json.dumps({"schema": 1, "type": "recording", "time": 0}) + "\n", encoding="utf-8")
    result = run_webview_harness(recording, inspect_motion=True, test_motion_policy=True)
    assert result["motionPolicyTests"]["pausedSettingStopsIdle"] is True
    assert result["motionPolicyTests"]["idleResumesAfterToggle"] is True



def test_visualiser_keeps_saved_reduced_motion_setting_when_recording_loads(tmp_path):
    recording = tmp_path / "saved-reduce-motion.jsonl"
    recording.write_text(json.dumps({"schema": 1, "type": "recording", "time": 0}) + "\n", encoding="utf-8")

    result = run_webview_harness(recording, inspect_motion=True, saved_reduce_motion=True)

    assert result["effectiveReduceMotion"] is True
    assert result["idleAnimationScheduled"] is False

def test_visualiser_respects_os_reduced_motion_after_palette_changes(tmp_path):
    recording = tmp_path / "system-motion-policy.jsonl"
    recording.write_text(json.dumps({"schema": 1, "type": "recording", "time": 0}) + "\n", encoding="utf-8")
    result = run_webview_harness(recording, inspect_motion=True, test_motion_policy=True, prefers_reduced_motion=True)
    assert result["motionPolicyTests"]["pausedSettingStopsIdle"] is True
    assert result["motionPolicyTests"]["systemPreferencePreserved"] is True
