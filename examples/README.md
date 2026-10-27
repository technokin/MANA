# MANA runnable examples

These 67 programs are intended to be run from the repository root. They use only MANA and its included runtime; normal MANA execution needs no third-party Python packages.

```powershell
python mana.py examples/fireball.mana
python mana.py --check examples/fireball.mana
```

On Windows, `py` can replace `python` if that is how Python is installed.

## Language basics

| File | What to look for |
|---|---|
| `standalone_release.mana` | Smallest basic program. |
| `helper_functions.mana` | An ordinary helper function using `incant`. |
| `conditional_magic.mana` | Conditions around magical operations. |
| `timed_spell.mana` | Virtual-time statements. |
| `event_reactions.mana` | A handler responding to a runtime-reported impact. |
| `spell_modes.mana` | Preview versus release. |
| `preview_then_release.mana` | Text preview, visual preview, and committed release. |
| `visual_preview.mana` | A focused `post(spell, visual)` example. |
| `advanced_operations.mana` | A collection of supported operations. |

## Objects, targets and physics

| File | What to look for |
|---|---|
| `target_profiles.mana` | A `tgset` target profile. |
| `target_resistance.mana` | Target resistances and defence values. |
| `fireball.mana` | Spell templates, tuning, preview and release. |
| `fireball_contact.mana` | A projectile and real contact in the 2D world. |
| `targeted_fireball.mana` | Selecting a target outside the spell body. |
| `collision_demo.mana` | Impact damage and collision records. |
| `physics_demo.mana` | Velocity, motion and physical quantities. |
| `motion_control.mana` | Setting velocity and advancing time. |
| `anchored_object.mana` | Anchoring, unanchoring and movement. |
| `earth_barrier.mana` | An anchored barrier shape. |
| `distance_check.mana` | A distance calculation in `geometry2d`. |
| `geometry_rotation.mana` | Rotating a direction before applying motion. |
| `visualiser_steering_firebolt.mana` | A firebolt whose recorded path changes direction over time; useful for checking 2D playback. |
| `scatter_stones.mana` | Creating a small group in a loop. |

## Elements and pure mana

| File | What to look for |
|---|---|
| `elements_demo.mana` | The four fundamental elements. |
| `elemental_cancellation.mana` | The implemented Fire/Water cancellation. |
| `ice_creation.mana` | The current Water/Air-to-Ice interaction. |
| `wood_from_elements.mana` | Mud and Wood interaction chain. |
| `life_and_wood.mana` | The same interaction with explicit Life invocation. |
| `heating_and_cooling.mana` | Temperature-delta operations. |
| `mana_constructs.mana` | Woven constructs with `weave mana`. |
| `mana_shield.mana` | A shaped and anchored pure-mana shield. |
| `mana_burst.mana` | A radial magical burst. |
| `mana_beam.mana` | A directed beam. |
| `shape_gallery.mana` | Different semantic/visual shape labels. |

## Beings, planes and libraries

| File | What to look for |
|---|---|
| `planes_navigation.mana` | Plane identities, routes and permissions. |
| `drafter_define_plane.mana` | Custom plane data in memory. |
| `summoning_example.mana` | Summon, name, return and recall a being. |
| `return_recall.mana` | The return/recall cycle in a smaller example. |
| `necromancy_example.mana` | Reanimating existing remains. |
| `summon_skeleton_spell.mana` | A user-authored necromancy spell. |
| `drafter_summoning_necromancy_3d_bridge.mana` | Several library features together. |
| `vector3d_planning.mana` | 3D calculations without 3D world simulation. |

## Visualiser

Install the optional `installers/vscode/mana-magic-visualiser-2.0.0.vsix` package. The eye-shaped **MANA: Visual** action records and replays a scene; ordinary **Run** does not open the viewer. The viewer shows magical effects, named entities and real contacts, not coordinates, energy-flow diagrams, portals or plane routes.

Every example has been syntax-checked. The smoke test also runs the public examples in a fresh runtime. The steering example specifically checks that the Visualiser follows recorded positions instead of inventing a straight path. An example is evidence for the specific operations it demonstrates, not proof that MANA has a full 3D engine, terrain system, creature AI, or a complete rule for every element pair.

## New focused examples

| File | What it demonstrates |
|---|---|
| `water_cooling.mana` | Cooling by a temperature difference. |
| `air_current.mana` | Motion of an Air object in the 2D world. |
| `earth_boulder.mana` | Position, velocity and a simple moving boulder. |
| `thunder_strike.mana` | Invoking Thunder and firing at a target. |
| `ice_barrier.mana` | Invoking Ice and anchoring a shaped object. |
| `life_bloom.mana` | Life invocation and an implemented domain check. |
| `shadow_marker.mana` | Invoking Shadow and assigning a supported shape. |
| `mana_projectile.mana` | A woven projectile making real contact. |
| `precise_beam.mana` | A directed beam with explicit range and width. |
| `multi_target_burst.mana` | One burst affecting several nearby targets. |
| `ignition_reaction.mana` | Handling the runtime's ignition event. |
| `universal_control.mana` | Moving an object with pure-mana control. |
| `collision_bounce.mana` | Two bodies colliding during a small timestep. |
| `basic_calculations.mana` | Helpers, list length and span indexing. |
| `material_states.mana` | Changing a supported material-state label. |
| `ward_then_release.mana` | Previewing a ward before committing it. |
| `reusable_element_spell.mana` | Reusing a spell definition with base elements. |

All listed files are self-contained examples rather than fragments. Read the comments in each program, then change one value and rerun it to see which result changes. The [Building Your First Spells guide](../docs/current/getting_started/BUILDING_FIRST_SPELLS.md) groups these concepts into a learning path.


## Native language syntax

- `native_magic_language.mana` uses the primary `spell` declaration, area-local `weather` statement, natural `conjure` assignment, and `post`/`release` appraisal/commit workflow.


## Additional integration examples

| File | What to look for |
|---|---|
| `preview_commit_boundary.mana` | Counts persistent objects before preview, after preview, and after release to demonstrate transaction boundaries. |
| `plane_path_lifecycle.mana` | Opens a one-way plane path, verifies directionality, closes it, and checks both directions again. |
| `kinetic_thermal_ledger.mana` | Applies mass, heat, velocity, cooling, and direct temperature updates in one energy-accounting sequence. |
| `selective_two_target_cast.mana` | Selects one of two target profiles outside the spell definition and checks that only the selected target is hit. |
| `impact_handler_counter.mana` | Counts an actual runtime impact event and inspects the target after contact. |

These five additions are also covered by deterministic regression tests; they are run by the all-examples smoke test rather than being syntax-only samples.
