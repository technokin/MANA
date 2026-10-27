# Arcana: Magical Disciplines Library

**Page kind:** Reference
**Status:** implemented, extensible classification catalogue. A listed discipline is not automatically a fully implemented simulator.

`arcana` organises magical practice by its subject, methods, costs, constraints and counters. It is the right place for broad schools such as **Mystic Magic** (structured diagrams, wards and portal geometry) or **Chaos Magic** (bounded probability and rule distortion). It is not a hard-coded set of copyrighted characters or a list of special abilities attached to them.

```mana
load arcana

spell inspect_mystic_practice():
    arcana.school("Mystic Magic")
    arcana.school("Chaos Magic")
    incant arcana.search("portal")

cast inspect_mystic_practice
```

Expected output:

```text
[CAST inspect_mystic_practice] spell committed
[CAST inspect_mystic_practice] mana appraisal: 0 mana
```

## API

- `arcana.schools()` — all built-in and custom entries.
- `arcana.school(name)` — one named discipline, including alias lookup.
- `arcana.search(query)` — search descriptions, domains, practices, constraints and counters.
- `arcana.count()` — number of registered disciplines in this runtime.
- `arcana.define(name, label=..., domain=..., description=..., patterns=..., limits=..., counters=..., status=...)` — add a world-local discipline entry.

Each entry has `label`, `domain`, `description`, `patterns`, `cost_axes`, `limits`, `counters` and `status`. Custom entries are runtime-local and transactional: an appraisal that is rolled back must not leave a permanent definition. Use plain MANA lists and named arguments; dictionary literal syntax is not required.

## Current disciplines

| Discipline | Core magical domain | Typical patterns | Status boundary |
|---|---|---|---|
| Mystic Magic | Structured spellcraft | circles, sigils, wards, counterspells, portal geometry | Foundational practice; individual spells still need implementation. |
| Chaos Magic | Probability and local rule alteration | bounded outcome bias, unstable conditions, causal debt | Design catalogue; never an unrestricted wish. |
| Dimensional Magic | Planes, boundaries and topology | appraisal, portals, folds, seals, anchors | Partial foundation connected to `planes`. |
| Astral Magic | Non-corporeal projection and remote awareness | projection, dream entry, return tether | Design catalogue. |
| Telepathy | Mental information exchange | messages, surface thoughts, shared perception, mind wards | Design catalogue with consent/resistance requirements. |
| Telekinesis | Remote mechanical force | lift, push, pull, hold, rotate | Supported principle; world physics should resolve momentum and collisions. |
| Energy Magic | Transfer and shaping of energy | beam, pulse, barrier, absorption, redirection | Partial foundation; transfers need accounting. |
| Elemental Magic | Fire, Water, Earth and Air | projection, shaping, sensing, resistance | Supported domain; does not replace chemistry. |
| Weather Magic | Area and regional atmosphere | rain, wind, fog, snow, temperature gradients, storm setup | Supported principle through weather parameters. |
| Conjuration | Bringing physical matter into existence | materials, blueprints, armour, arrows, constructs | Supported principle; object validity and material properties matter. |
| Transmutation | Composition | alloys, purification, material substitution, corrosion reversal | Supported principle; shape and mass conservation are separate concerns. |
| Transfiguration | Form/organisation | body forms, eligible conjured matter, reversal | Partial foundation; shape is not equivalent to life. |
| Blood Magic | Blood and circulation | flow, binding, clotting, tracking, wards | Supported through bounded physiology fields; not a full circulatory-fluid solver. |
| Vitality Magic | Repair and body function | healing, stamina recovery, tissue repair, temporary enhancement | Partial foundation; organ viability and death states constrain effects. |
| Necromancy | Death-state, remains and undead animation | reanimation, binding, decay control, revenant conditions | Implemented bounded death/undead mechanics; not universal resurrection. |
| Illusion | Perceptual input and interpretation | concealment, decoy, false sound/image, misdirection | Design catalogue. |
| Wards and Seals | Defensive constraints and boundaries | alarms, barriers, keyed access, containment | Partial foundation; ward scope and duration must be explicit. |
| Rune Magic | Persistent symbolic instructions | triggers, delayed casting, storage marks, anchors | Design catalogue. |
| Cosmic Magic | Celestial sources and large-scale fields | alignments, stellar source, gravity wells | Design catalogue. |
| Shadow Magic | Occlusion, concealment and shadow constructs | veil, tether, step, concealment field | Design catalogue; shadows are not automatically physical matter. |
| Light Magic | Illumination and optical interaction | flash, beam, refraction, light bridge | Supported principle. |
| Sound Magic | Acoustic vibration | silence, resonance, directed sound, echo mapping | Design catalogue. |
| Alchemy | Material recipes/reactions | elixir, catalyst, alloying, purification | Supported principle; recipes need yields and by-products. |
| Dream Magic | Dream-state experiences | entry, message, sanctuary, nightmare | Design catalogue; dream effects do not automatically affect physical matter. |

`arcana` currently contains 24 discipline entries. The catalogue is intended to grow, but a new school should only be marked implemented once its mechanics exist in the runtime and have tests.

## Adding a discipline

```mana
load arcana

spell register_echo_craft():
    arcana.define("echo_craft",
        label="Echo Craft",
        domain="sound-memory impressions",
        description="Stores and replays a bounded acoustic pattern in a prepared anchor.",
        patterns=["record sound", "replay sound", "directional echo"],
        limits=["requires an acoustic sample", "anchor storage is finite", "replayed sound does not recreate the original physical event"],
        counters=["break anchor", "mask the sample", "wait for expiry"],
        status="user-defined")
    incant true

cast register_echo_craft
```

Expected output:

```text
[CAST register_echo_craft] spell committed
[CAST register_echo_craft] mana appraisal: 0 mana
```

This registers metadata only. To make the discipline work in the world, add or compose relevant built-in operations, define conservation and world-state effects, make errors deterministic, expose it to the visualiser if useful, and add positive/negative tests. The `status` field should say what is actually implemented, not what is hoped for.

## Inspirations and naming policy

Broad genre ideas can inspire original mechanics: learned mystic spellcraft, chaos/reality distortion, dimensional travel, astral projection, vitality restoration, blood manipulation or necromancy. Avoid coding one film/comic character as the definition of an entire school. The school should describe reusable mechanics, while a named spell is one authored use of those mechanics.

See the separate [MANA Magic Inspiration Catalogue](../../../MANA_MAGIC_INSPIRATION_CATALOGUE.md) for the expanded cross-media idea list. That list is a design catalogue; it is not the same thing as runtime feature status.
