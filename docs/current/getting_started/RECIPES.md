# MANA Recipes

**Page kind:** How-to

Each recipe is a starting point using currently implemented APIs. Run the examples with `python mana.py file.mana`. Examples that affect world state use `release`; replace it with `post` to inspect a trial and roll back its changes.

## Projectile spell

```mana
spldef earth_bolt():
    bolt = create Earth
    shape(bolt, circle)
    velocity(bolt, 25 m/s)
    incant bolt

release(earth_bolt)
show("Earth bolt released")
```

Expected output:

```text
Earth bolt released
```

The projectile's physical state depends on the runtime's physics step.

## Summon a being

```mana
load planes
load summoning
planes.open_path("Wild Realm", "Mortal Plane")
summoning.bring("Griffin")
show("Griffin summoned")
```

Expected output:

```text
Griffin summoned
```

Summoning obeys the registered being data and route requirements; it is not an unconditional spawn operation.

## Reanimate remains

```mana
load planes
load necromancy
planes.open_path("Underworld", "Mortal Plane")
planes.invoke("Necro")
bones = tgset:
    material = "Bone"
    state = "solid"
undead = necromancy.reanimate(bones, "Bone Guard")
show("Bone Guard reanimated")
```

Expected output:

```text
Bone Guard reanimated
```

This is a minimal API illustration; consult the [Necromancy Library](../libraries/NECROMANCY_LIBRARY.md) for required corpse/remains fields and current constraints before using it in a larger spell.

## Related references

- [Summoning Library](../libraries/SUMMONING_LIBRARY.md)
- [Necromancy Library](../libraries/NECROMANCY_LIBRARY.md)
- [Planes Library](../libraries/PLANES_LIBRARY.md)
