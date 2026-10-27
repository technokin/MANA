# Beings, Creature Data, and Cross-Plane Summoning

**Page kind:** Explanation  

**Current source version:** v2.0.0

A being is data describing an entity and the place it belongs to. A being record is not itself an active, moving world object. `summoning` uses a record to instantiate an entity in the Mortal Plane. After it exists as a world object, ordinary MANA movement, physical operations, and universal mana controls operate on it.

## 1. Being record fields

Current built-in/custom being records support these fields:

| Field | Meaning |
|---|---|
| `name` | Display/species name used to look up the being. |
| `kind` | Broad category such as `beast`, `being`, `fairy`, or `elemental`. |
| `home_plane` | Top-level home plane name. Being homes cannot be regions. |
| `element` | Optional element association. It does not automatically add abilities or immunity. |
| `summoning_requirements` | List of text conditions that have to be supplied when summoning. Empty means no extra conditions have been declared. |
| `hp`, `max_hp` | Current and maximum hit points, when assigned. |
| `defence` | Defence value, when assigned. |
| `attack` | Attack value, when assigned. |
| `resistance` | Map from a registered element/channel label to a fraction from `0` to `1`; default is `0`. |

A resistance of `0` means no protection assigned in the record; `1` means full protection according to the resistance convention. The current engine does not yet contain a complete combat AI or final damage/balance system for every possible being, so these values should not be presented as a completed role-playing game combat model.

The built-in data values below are prototype calibration values. They are present in source and should be adjusted deliberately when corresponding combat rules/tests change. They are not real-world measurements.

## 2. Current built-in beings and stats

### Elemental/special-plane spirits

The `elemental_planes` data library groups all thirteen plane/elemental spirit records into one module; each still belongs to a distinct plane.

| Spirit | Plane/channel | HP = max HP | Defence | Attack |
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

The resistance dictionary exists for all recognised resistance labels, initially set to zero unless overridden. These spirit entries are data records; `planes.spirit_of(...)` retrieves a record, while contacting or bringing the spirit into the Mortal Plane is a separate operation.

### Other built-in species

| Being | Home plane | Kind | HP = max HP | Defence | Attack |
|---|---|---|---:|---:|---:|
| Mermaid | Atlantis | `being` | 90 | 5 | 8 |
| Elf | Fae Paradise | `fairy` | 80 | 5 | 11 |
| Griffin | Wild Realm | `beast` | 180 | 14 | 22 |
| Werewolf | Wild Realm | `being` | 150 | 11 | 18 |
| Vampire | Wild Realm | `being` | 140 | 10 | 17 |
| Chimera | Wild Realm | `beast` | 220 | 13 | 24 |
| Giant | Wild Realm | `being` | 300 | 20 | 28 |
| Orc | Wild Realm | `being` | 110 | 8 | 14 |

Heaven, Lineage Halls, and Hell currently have their data modules/regions but no built-in beings listed. No extra species should be implied by a plane's existence.

## 3. Finding a being

`load planes` is required before `load summoning` because summoning uses the plane registry and routes. `summoning.find_being(name[, source_plane])` returns a being record without manifesting it. Built-in beings may be inferred from the loaded or indexed built-in data modules. A custom/ambiguous name should provide a source plane, for example:

```mana
load planes
load drafter
load summoning

draft = drafter.begin("Crystal Reach", "living realm")
drafter.add_being(draft, "Crystal Drake", kind="beast")
crystal_reach = drafter.create(draft)
record = summoning.find_being("Crystal Drake", "Crystal Reach")
show record.name
```

This is an illustration of the namespace relationship. The exact arguments and accepted optional fields are specified in [Plane Creator](../libraries/DRAFTER_LIBRARY.md); all operations should be checked against the guide shipped with the version being used.

## 4. Bringing a being through a pathway

The implemented cross-plane operation is `summoning.bring(...)`, deliberately not a universal `summon()` function. A user-written spell named `summon_skeleton`, `summon_griffin`, or `summon_army` is ordinary MANA code; the specialist library function `bring` is for bringing a defined existing being from its recorded home plane.

```mana
load planes
load summoning

planes.open_path("Wild Realm", "Mortal Plane")
griffin = summoning.bring("Griffin")
show griffin.species
```

Expected output:

```text
Griffin
```

The variable is optional; it names that specific summoned instance so a program can tame, return, and recall it later. A built-in being's source plane can be inferred. The destination is implicit because the active world is the Mortal Plane. A route must already be open and directionality must permit travel. Cross-plane energy/being ledger records are produced; this accounting is not a finite mana-cost pool.

A brought entity is marked as a being, retains its species/home-plane data, and enters the 2D world. A nonzero z position is rejected because the world engine is not 3D.

## 5. Taming, sending back, and recalling

- `summoning.tame(being[, name])` marks a brought entity as tamed and gives it a stable recall name. Taming operates on that individual instance, not every member of its species.
- `summoning.send_back(being)` returns a brought entity to its home plane and requires an open route in the reverse direction. The entity's identity remains in its retained object/record state as returned.
- `summoning.call(being)` recalls that returned tamed instance through the route to the Mortal Plane. It is not a way to create an arbitrary new creature from nothing.

A named/tamed instance is useful when a program needs to send a being away and later bring back that same instance. It is not required merely to summon a new ordinary built-in species. The library does not implement a complete relationship, obedience, feeding, or creature AI system; `tame` is currently an instance-management flag and name mechanism.

## 6. Groups and armies

Groups and armies should be composable program behaviour. A user can loop over records or create several constructed/reanimated entities, then apply ordinary controls or release multiple spells. This does not require a separate language keyword or a hardcoded function for every formation. Large groups are subject to runtime loop/object-count/performance constraints.

A cross-plane army of defined beings is different from a necromantic skeleton-summoning spell. `summoning.bring` instantiates beings defined in a home-plane data source. A spell that creates a skeleton-like construct from Necro energy and ordinary mana constructs is not required to have a pre-existing creature record or pass through `summoning`; it is written as a `spell` using available general primitives.

## 7. Where being records live

Built-in plane data modules are loaded independently. The current modules are `elemental_planes`, `atlantis`, `fae_paradise`, `hell`, `heaven`, `lineage_halls`, and `wild_realm`. Custom beings are stored in data registered by `drafter` for the active runtime. The plane identity catalogue remains compact; loading Atlantis must not force all Wild Realm beings into memory.

A being's `home_plane` is a top-level plane, not a region. A being from Naraka, for example, is still defined as coming from Hell when the home-plane rule says Hell. Region-specific membership is not currently an independent being-travel model.

## 8. Limits

- The world is 2D and cross-plane destination is the Mortal Plane.
- A direct open route is required for travel; `summoning` does not create a pathway automatically.
- Being stats are data; complete AI, battle logic, and species-specific action systems are not complete.
- The engine does not automatically generate a full creature design or balancing model from a name.
- Summoning and reanimation have separate meanings; they must not be merged into one operation.
