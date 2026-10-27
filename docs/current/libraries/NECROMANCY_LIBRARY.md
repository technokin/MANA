# `necromancy` Library — MANA v2.0.0

**Page kind:** Reference  

`necromancy` provides operations for working with death-related energy and reanimating existing remains. It depends on `planes`, not `summoning`.

## Reanimation

Before reanimation, open a pathway from the Underworld to the Mortal Plane and invoke the **Necro** channel:

```mana
load planes
load necromancy

planes.open_path("Underworld", "Mortal Plane")
planes.invoke("Necro")

bones = tgset:
    material = "Bone"
    state = "solid"
    mass = 2 kg
    volume = 0.002 m3

necromancy.reanimate(bones, "Bone Guard")
show bones.display_name
show necromancy.is_undead(bones)
```

Expected output:

```text
Bone Guard
True
```

The input body must already exist and be declared as bones, skeleton, corpse, dead body, or remains when it is introduced. Creating ordinary Earth and changing its `material` property afterward does not make it an eligible corpse.

### `necromancy.reanimate(corpse, name=None)`

Reanimates one eligible existing body in the Mortal Plane. It does not create the body or bring it from another plane. No joule value is supplied by the spell author. The Underworld transfer is an accounting record, not a finite gameplay fuel pool, and is not added to the body's physical energy.

### `necromancy.reanimate_many(corpses, name=None)`

Reanimates a non-empty list of distinct eligible bodies. If a name is supplied, resulting names are suffixed with `1`, `2`, and so on. Duplicate references are rejected.

### `necromancy.is_undead(thing)`

Returns `true` if the supplied MANA object is marked undead. A non-object input is a type error.

## Summoning an undead is a spell, not a library operation

There is intentionally no `necromancy.summon_skeleton()` or `necromancy.animate_construct()` built-in. A spell such as `summon_skeleton` is written in ordinary MANA and combines the normal object-creation, mana-channel invocation, property, and movement/control operations. It does not require an existing corpse; that is the distinction between summoning/constructing an undead and reanimating remains.

A spell can create an Earth-based body and shape its properties, invoke `Necro`, mark the result as an undead being, then use normal controls such as `velocity()`, `push()`, `pull()`, or `mana.lift()`. It is a regular user-defined spell, not a new built-in operation. See `examples/summon_skeleton_spell.mana`.

## Necro mana bookkeeping

`planes.invoke("Necro")` grants access to the Necro channel; the energy source recorded for reanimation remains the Underworld. Reanimation internally records its usage per body. The record is accounting only: it does not add `bound_energy`, change the body's physical energy, or deplete a finite mana pool. The spell author never supplies an energy amount.

This library does not implement AI or autonomous command-following. Motion and object control use the shared MANA functions, and custom spell behaviour is composed in MANA code. Errors use MANA's standard error system and source locations.
