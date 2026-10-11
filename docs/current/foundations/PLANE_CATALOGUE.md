# MANA Plane Catalogue

**Page kind:** Explanation  

**Version:** 1.0.0
**Purpose:** list the currently defined plane identities, their category, associated records, and implementation boundaries. This is a technical catalogue, not an account of internal plane laws.

## 1. Plane identity and library boundaries

The `planes` library identifies planes and regions, categorises them, opens/closes explicit pathways, finds routes, and records energy transfer. It does not define how a plane was formed, simulate its internal laws, explore its geography, or move beings. `drafter` creates custom plane records. Plane-data libraries hold additional data. `summoning` handles being transfer.

A plane is not automatically a runtime world. A registered plane can have a name and a pathway graph even if its data library has no beings or region records. A region is addressed under its parent plane, for example `Hell.Naraka`; a being's `home_plane` remains the top-level plane, not the region.

## 2. Foundational elemental/special planes

The current registry/data model has thirteen distinct records grouped in `elemental_planes`:

| Plane / channel | Associated label | Current role |
|---|---|---|
| Fire | Fire | Base elemental plane and Fire Spirit record. |
| Water | Water | Base elemental plane and Water Spirit record. |
| Earth | Earth | Base elemental plane and Earth Spirit record. |
| Air | Air | Base elemental plane and Air Spirit record. |
| Ice | Ice | Specialised plane and Ice Spirit record. |
| Metal | Metal | Specialised plane and Metal Spirit record. |
| Thunder | Thunder | Specialised plane and Thunder Spirit record. |
| Life | Life | Conceptual/special plane and Life Spirit record. |
| Death | Death | Conceptual/special plane and Death Spirit record. |
| Underworld | Underworld / Necro channel | Source for recorded necromantic energy access and Underworld Spirit record. |
| Holy | Holy | Specialised plane and Holy Spirit record. |
| Shadow | Shadow | Specialised plane and Shadow Spirit record. |
| Void | Void | Specialised plane and Void Spirit record. |

The four base elements are available without invocation. The other channels require invocation permission before their plane energy can be drawn through `planes`. The existence of an Ice Plane does not mean Ice must always be invoked: a supported Water + Air interaction can produce Ice as a result. `Void` is not the same as the design concept `Null`.

## 3. Other top-level planes

| Plane | Category/use | Current registered content and limits |
|---|---|---|
| Mortal Plane | Baseline physical world | The default destination for cross-plane beings and the current 2D world simulation. |
| Hell | Afterlife/underworld grouping | One plane with named regions; not three separate top-level planes. |
| Heaven | Afterlife/divine grouping | Registered plane/data module; no built-in beings currently listed. |
| Atlantis | Living realm | Contains the built-in Mermaid record. |
| Fae Paradise | Living realm | Contains the built-in Elf record. |
| Lineage Halls | Ancestral realm | Registered plane/data module; no built-in beings currently listed. |
| Wild Realm | Living/beast realm | Contains Griffin, Werewolf, Vampire, Chimera, Giant, and Orc records. |

The following ideas were deliberately kept out of the current catalogue: The Dreaming, Primordial Expanse, and Outer Expanse. They must not be treated as implemented planes merely because earlier notes discussed them.

## 4. Hell and regions

Hell is one top-level plane. The current built-in region names are:

- `Hell.Naraka`
- `Hell.Ten Courts`
- `Hell.Yomi Hollows`

The eight-hot/eight-cold Naraka subregions were an idea for a future expansion and are not represented as sixteen fully implemented region records unless the current source explicitly adds them. Region identity and pathways are data; they do not impose different MANA language semantics or change the physics solver.

## 5. Elemental spirits and plane data

The elemental/special plane data library includes the following spirit records: Fire Spirit, Water Spirit, Earth Spirit, Air Spirit, Ice Spirit, Metal Spirit, Thunder Spirit, Life Spirit, Death Spirit, Underworld Spirit, Holy Spirit, Shadow Spirit, and Void Spirit. `planes.spirit_of(...)` returns the data record. Looking up a record is not the same as contacting, summoning, or controlling the spirit.

The documented prototype stats are data defaults, not final combat balance. See [Beings and Summoning](BEINGS_AND_SUMMONING.md) for the current stat table and caveats.

## 6. Pathways

Pathways are explicit graph edges between two planes or supported region identifiers. They have direction and open/closed state. Route-finding only uses currently open, directionally valid edges. No route is inferred from names, category similarity, or a description. A closed path is not traversable; a route can contain several edges.

`planes.open_path(a, b)` creates or opens a direct connection; `planes.close_path(a, b)` closes it. Route helpers include `is_open`, `paths_of`, `neighbors`, `find_route`, and `reachable`. The precise function contracts and errors are in the [Planes Library Reference](../libraries/PLANES_LIBRARY.md).

## 7. Energy transfer

With `planes` alone, energy can cross an open route; beings cannot. `planes.send_energy(...)` records an energy transfer in the shared ledger. It does not create a finite plane-energy reservoir or deduct a caster's mana pool. Continuous channels are modelled in virtual time and recorded in the ledger. Necro is a channel label tied to Underworld access; it is not a separate finite necro-energy battery.

## 8. Plane creation and custom records

`drafter` lets a program create custom plane records, add properties, regions, and being records, then register them for use by the runtime. This is a runtime/data operation; it is not a full graphical plane editor, and custom records do not automatically persist across sessions. The separate Library Builder packages reusable libraries; it is not the same as plane creation.

## 9. Related references

- [Planes and Pathways](PLANES_AND_PATHWAYS.md)
- [Planes Library](../libraries/PLANES_LIBRARY.md)
- [Plane Creator (`drafter`)](../libraries/DRAFTER_LIBRARY.md)
- [Cross-Plane Summoning](../libraries/SUMMONING_LIBRARY.md)
- [Beings and Summoning](BEINGS_AND_SUMMONING.md)
- [Implementation Status](IMPLEMENTATION_STATUS.md)
