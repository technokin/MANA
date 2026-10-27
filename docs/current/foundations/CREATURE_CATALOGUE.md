# Built-in Being and Creature Catalogue

**Page kind:** Explanation  

**Version:** 2.0.0
**Scope:** current built-in records, home planes, prototype stats, and what the runtime can do with them.

## 1. What a being record is

A being record is species/entity data, not a complete autonomous creature simulation. The record may include `name`, `kind`, `home_plane`, optional `element`, `summoning_requirements`, `hp`, `max_hp`, `defence`, `attack`, and `resistance`. Resistances are fractions from `0` (no protection assigned) to `1` (full protection under the current convention). These stats are prototype data; they do not imply finished combat AI, creature pathfinding, decision-making, or balanced encounters.

A being's home plane is a top-level plane. A creature listed in a Hell region still has `home_plane = "Hell"`, not `"Hell.Naraka"`. The `planes` library looks up the home plane; `summoning` moves a defined being through a pathway. Once present in the Mortal Plane, the resulting entity is a world object and uses the existing 2D runtime.

## 2. Elemental and special-plane spirits

All thirteen records are stored in the shared `elemental_planes` data library while remaining separate plane identities.

| Name | Plane/channel | HP | Defence | Attack |
|---|---|---:|---:|---:|
| Fire Spirit | Fire | 180 | 12 | 20 |
| Water Spirit | Water | 180 | 14 | 18 |
| Earth Spirit | Earth | 240 | 22 | 19 |
| Air Spirit | Air | 160 | 10 | 20 |
| Ice Spirit | Ice | 190 | 16 | 20 |
| Metal Spirit | Metal | 260 | 24 | 22 |
| Thunder Spirit | Thunder | 175 | 11 | 27 |
| Life Spirit | Life | 220 | 16 | 18 |
| Death Spirit | Death | 220 | 17 | 24 |
| Underworld Spirit | Underworld | 260 | 20 | 25 |
| Holy Spirit | Holy | 220 | 18 | 24 |
| Shadow Spirit | Shadow | 200 | 15 | 24 |
| Void Spirit | Void | 280 | 20 | 30 |

For these records, the initial `max_hp` equals the listed HP. Resistance maps are populated for recognised labels and default to zero unless a record overrides them. The table describes current data defaults only.

## 3. Other built-in beings

| Name | Home plane | Kind | HP | Defence | Attack |
|---|---|---|---:|---:|---:|
| Mermaid | Atlantis | `being` | 90 | 5 | 8 |
| Elf | Fae Paradise | `fairy` | 80 | 5 | 11 |
| Griffin | Wild Realm | `beast` | 180 | 14 | 22 |
| Werewolf | Wild Realm | `being` | 150 | 11 | 18 |
| Vampire | Wild Realm | `being` | 140 | 10 | 17 |
| Chimera | Wild Realm | `beast` | 220 | 13 | 24 |
| Giant | Wild Realm | `being` | 300 | 20 | 28 |
| Orc | Wild Realm | `being` | 110 | 8 | 14 |

The current data modules for Heaven, Lineage Halls, and Hell do not list additional built-in beings. A plane can exist without an assigned species catalogue.

## 4. Bringing, naming, taming, returning, recalling

The cross-plane library operation is `summoning.bring(...)`. It finds the being record, checks the source route, and manifests an instance in the Mortal Plane. Destination is implicit in the current implementation. This is not the same as a user-authored spell named `summon_griffin` or `summon_skeleton`.

A program can assign the returned instance to a variable if it needs to refer to that exact being later. Taming associates a stable name/identity with the instance, so it can be sent back and recalled. The current system is a data/route/instance mechanism, not a general creature companion AI.

```mana
load planes
load summoning

planes.open_path("Wild Realm", "Mortal Plane")
griffin = summoning.bring("Griffin")
summoning.tame(griffin, "Scout")
summoning.send_back(griffin)
summoning.call(griffin)
```

Expected output:

```text
(no output)
```

Check the current [Summoning Library](../libraries/SUMMONING_LIBRARY.md) for exact signatures and route rules before relying on optional forms.

## 5. Necromancy is separate

A skeleton assembled from available materials or summoned by a spell is not automatically a reanimated corpse. `necromancy.reanimate(...)` requires an existing object marked as bones, corpse, or remains. A spell that creates and controls an undead construct is ordinary MANA code combining Necro access and universal control; it must not call a hidden built-in `summon_skeleton` function.

See [Necromancy and Undead](NECROMANCY_AND_UNDEAD.md) for the distinction and current limitations.

## 6. What is not implemented by the catalogue

Being data does not currently provide a full system for:

- autonomous navigation and path planning;
- decision-making, loyalty, fear, tactics, or general AI;
- a complete attack/damage/resistance combat loop for every interaction;
- species-specific animation or a graphical creature viewer;
- permanent persistence of custom creature records between sessions;
- arbitrary transfer between every possible pair of planes.

Those features can be added later, but they require explicit runtime work and tests. Do not infer them from the presence of a stat field.

## 7. Related references

- [Beings and Summoning](BEINGS_AND_SUMMONING.md)
- [Necromancy and Undead](NECROMANCY_AND_UNDEAD.md)
- [Planes and Pathways](PLANES_AND_PATHWAYS.md)
- [Summoning Library](../libraries/SUMMONING_LIBRARY.md)
- [Implementation Status](IMPLEMENTATION_STATUS.md)
