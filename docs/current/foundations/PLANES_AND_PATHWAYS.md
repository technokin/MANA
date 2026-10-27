# Planes, Pathways, and the Planar Catalogue

**Page kind:** Explanation  

**Current source version:** v2.0.0

Planes are locations in the cosmology. For MANA's program, their relevant properties are identity, category, parent relationship for a region, and the data library that describes the plane's inhabitants or region entries. Plane contents must not act as hidden language laws: changing a plane record cannot change how unrelated arithmetic, physics operations, or definitions execute.

## 1. Responsibility boundaries

- `planes` identifies plane/region records, categorises them, opens and closes pathways, finds routes, records cross-plane energy transfers, and manages invocation permission for registered plane channels.
- `drafter` creates custom plane definitions and adds the initial data attached to them. It is a creator, not a general editor for changing a completed plane.
- Plane-data libraries hold the heavier data for individual planes or logical groups, such as their beings and regions. They load when needed instead of bloating the identity registry.
- `summoning` uses plane references and open pathways to bring a defined being into the Mortal Plane. `planes` alone moves no beings.

There is no separate portal library. A pathway is a record connecting two endpoints, with a direction rule and an open/closed state.

## 2. Built-in top-level planes

The runtime ships with twenty top-level plane references:

| Plane | Category | Data behaviour |
|---|---|---|
| Fire | elemental | Elemental-plane data library |
| Water | elemental | Elemental-plane data library |
| Earth | elemental | Elemental-plane data library |
| Air | elemental | Elemental-plane data library |
| Ice | elemental | Elemental-plane data library |
| Metal | elemental | Elemental-plane data library |
| Thunder | elemental | Elemental-plane data library |
| Life | elemental | Elemental-plane data library |
| Death | elemental | Elemental-plane data library |
| Underworld | elemental | Elemental-plane data library |
| Holy | elemental | Elemental-plane data library |
| Shadow | elemental | Elemental-plane data library |
| Void | elemental | Elemental-plane data library |
| Mortal Plane | mortal | Baseline simulated world; no separate being-data module |
| Hell | afterlife | Data module registers Hell's regions |
| Heaven | afterlife | Its own lazy data module |
| Atlantis | living realm | Its own lazy data module, including Mermaid |
| Fae Paradise | living realm | Its own lazy data module, including Elf |
| Lineage Halls | afterlife | Its own lazy data module |
| Wild Realm | living realm | Its own lazy data module, including six listed species |

Names and aliases are case/punctuation normalised by the registry, so identifiers such as `Mortal`, `Mortal World`, `World`, and `Our World` resolve to the Mortal Plane. The aliases are convenience lookup forms, not extra planes.

The earlier candidate catalogue names Dreaming, Primordial Expanse, and Outer Expanse are not in this current built-in registry. They should not be documented as available built-ins until registered by a future implementation or created through `drafter`.

## 3. The thirteen elemental/special plane entries

The elemental data library stores the following as thirteen separate plane records: Fire, Water, Earth, Air, Ice, Metal, Thunder, Life, Death, Underworld, Holy, Shadow, and Void. Each has a separate elemental/spirit record. This grouping is a storage decision; it does not merge the thirteen identities into a single plane and does not change the four-element fundamental rule.

The built-in identity registry stores the name, ID, category, parent relationship, and data-library name. Element affinity and spirit details live in the elemental data module. This avoids copying the same heavyweight data into the always-loaded registry.

## 4. Hell and regions

Hell is one top-level plane. Its current data module registers three regions:

- `Hell.Naraka`
- `Hell.The Ten Courts`
- `Hell.Yomi Hollows`

A region has a parent plane and receives the category of that parent. Region references are addressable through qualified names. The plan reserves sixteen Naraka subregions (eight hot and eight cold) for later, but those sixteen are not currently registered. The data module currently has no Hell-specific beings.

## 5. Pathways and routes

A direct pathway can be one-way or two-way. Two-way is the default. Each pathway has source and destination endpoints, a directionality flag, and an open/closed state. Closing a pathway can invalidate routes and causes continuous channels with no remaining route to be pruned.

The implementation provides these functions:

- `identify(name)` / `exists(name)` resolve or test known plane/region identities.
- `all_planes()` lists top-level planes; `regions_of(plane)` and `parent_of(region)` work with regions.
- `category_of(plane)`, `planes_in(category)`, and `same_category(a,b)` inspect the category catalogue.
- `open_path(a,b,one_way=false)`, `close_path(a,b)`, and `is_open(a,b)` manage direct pathways.
- `paths_of(plane)` returns open direct pathway records; `neighbors(plane)` returns destinations reachable in one step.
- `find_route(a,b)` returns a deterministic shortest route through the currently open directional network or a clear error if no route exists.
- `reachable(a)` returns every plane/region reachable through open pathways.

Pathways start empty in each new runtime. Knowing a plane exists does not mean any path is open.

## 6. Energy transport

`send_energy(amount, source, destination, kind=None)` moves a finite non-negative energy quantity in joules along an open route and adds a transfer entry to the runtime ledger. The source plane needs the relevant invocation permission when its channel is non-base. The route and energy transfer are validated before a receipt is returned.

`open_channel(a,b,rate)` creates a continuous directional energy flow with a rate in watts, provided a route exists and source permission is present. `close_channel(a,b)` closes it. Channels are runtime state; they are not saved permanent cosmological connections. `energy_sent(a,b)` totals recorded direct ledger transfers for the specified source/destination pair.

This is energy bookkeeping, not a limited mana reservoir. The transferred quantity allows the ledger to track where recorded energy comes from and where it goes. MANA energy readouts and a planar transfer entry do not create a user-supplied spell budget.

## 7. Invocation and special channels

`invoke(plane_or_mana)` records permission for the corresponding non-base plane channel. `revoke(...)` removes that permission and stops continuous channels sourced from that plane; `has_permission(...)` checks it. The four fundamental base elements are always permitted. `element_of(plane)` reads the stored element label; `spirit_of(plane)` reads the data library's elemental spirit record.

The string `Necro` is a special channel alias for the Underworld permission. It is not a plane with its own identity. Necromancy's transfer record can therefore use the Necro label while the source remains Underworld.

## 8. Plane creator and data libraries

`drafter` creates plane identity/data records, including custom variables, regions, and beings. The `planes` registry is what makes the identity available for pathway operations. A creator may define custom properties, but those values have no side effect on unrelated language or physics execution unless a program/library explicitly reads them.

Built-in plane content data loads by namespace—for example, `load elemental_planes`, `load wild_realm`, or `load atlantis` after `load planes`. Lazy loading is intentional: loading one plane's beings must not automatically load all other planes' data.

## 9. Non-goals and current limits

The `planes` library does not define how planes were created, simulate a plane's internal physical laws, simulate geographical exploration, or move creatures. It does not open paths based on lore descriptions. It uses explicit pathway records only. Being travel is handled by `summoning`; necromancy is separate and uses local remains plus a recorded Underworld/Necro transfer.

See [Planes Library](../libraries/PLANES_LIBRARY.md), [Plane Creator](../libraries/DRAFTER_LIBRARY.md), and [Beings and Cross-Plane Summoning](BEINGS_AND_SUMMONING.md).
