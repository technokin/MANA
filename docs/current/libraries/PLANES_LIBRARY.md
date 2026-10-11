# `planes` Library — MANA v1.0.0

**Page kind:** Reference  

The built-in `planes` library identifies planes, classifies them, manages open/closed pathways, and accounts for energy moving through those pathways. Importing it does not create planes or automatically connect them.

```mana
load planes

fire = planes.identify("Fire")
show fire.name
show planes.category_of(fire)
```

Expected output:

```text
Fire
elemental
```

Plane references are read-only records. A region is addressed by a qualified name such as `Hell.Naraka`.

## Catalogue

The compact registry keeps plane identities loaded. Its initial catalogue contains the following 20 planes:

- **Elemental:** `Fire`, `Water`, `Earth`, `Air`, `Ice`, `Metal`, `Thunder`, `Life`, `Death`, `Underworld`, `Holy`, `Shadow`, `Void`.
- **Mortal:** `Mortal Plane`.
- **Afterlife:** `Hell`, `Heaven`, `Lineage Halls`.
- **Living realm:** `Atlantis`, `Fae Paradise`, `Wild Realm`.

`Hell` currently has three regions, loaded from the `hell` data library when needed: `Hell.Naraka`, `Hell.The Ten Courts`, and `Hell.Yomi Hollows`. Naraka's sixteen proposed subregions are not in the initial data set.

## Plane identification and categories

### `planes.identify(name)`

Returns a read-only plane or region reference. It accepts a plane name, supported alias, ID, or qualified region name. Unknown names raise `RuntimeErrorML` with the source location.

```mana
load planes
fire = planes.identify("Fire Plane")
naraka = planes.identify("Hell.Naraka")
show fire.name
show naraka.parent_plane
```

Expected output:

```text
Fire
Hell
```

### `planes.exists(name)`

Returns `true` if the supplied plane or region name, alias, or ID identifies a registered entry; otherwise returns `false`. Known regions are loaded from their assigned data library when checked. A non-name input raises `TypeErrorML`.

```mana
load planes
show planes.exists("Fire")
show planes.exists("Hell.Naraka")
show planes.exists("Unknown")
```

Expected output:

```text
True
True
False
```

### `planes.plane_of(thing)`

Returns the registered home plane for a being record or summoned/reanimated world object. Other ordinary values and normal MANA objects map to `Mortal Plane`. A string plane name or a `PlaneReference` raises `TypeErrorML`: a location identifier is not itself a being or world object. MANA objects do not receive a `plane` property.

### `planes.all_planes()`

Returns the names of the 20 top-level planes. Regions are returned by `regions_of`, not included in this list.

### `planes.regions_of(plane)` and `planes.parent_of(region)`

`regions_of` loads only that plane's data library and returns qualified region names. It raises an error if given a region. `parent_of` returns the parent plane reference and raises an error if given a top-level plane.

### `planes.category_of(plane)`

Returns one of `elemental`, `mortal`, `afterlife`, or `living realm`. A region inherits the category of its parent plane.

### `planes.planes_in(category)`

Returns top-level plane names matching a category. Category input is case-insensitive; spaces, hyphens, and underscores are normalized.

### `planes.same_category(a, b)`

Returns `true` when both references have the same category, including when one reference is a region.

## Pathways

Pathways start closed. Plane existence alone does not create a connection. Both planes and regions can be endpoints. A one-way pathway permits transit from its source to its destination only.

### `planes.open_path(a, b, one_way=false)`

Opens a direct pathway. The default is bidirectional; use `one_way=true` for a single directed pathway. Returns `true` if at least one direction changed to open, otherwise `false`.

```mana
load planes
planes.open_path("Mortal Plane", "Fire")
planes.open_path("Underworld", "Mortal Plane", one_way=true)
```

Expected output:

```text
(no output)
```

### `planes.close_path(a, b)`

Closes the pathway record between the two endpoints, regardless of which direction was used when it opened. The closed record is retained and can be reopened with `open_path`. Returns `true` when an open pathway was closed and `false` when no open pathway existed.

### `planes.is_open(a, b)`

Returns whether the direct directed pathway from `a` to `b` is open.

### `planes.paths_of(plane)`

Returns the currently open outgoing pathways as records containing `source`, `destination`, `state`, and `one_way`.

### `planes.neighbors(plane)`

Returns the names of destinations reachable in one open step.

### `planes.find_route(a, b)`

Returns a shortest route through open directed pathways, including the starting point and destination. If no open route exists, it raises `RuntimeErrorML`.

### `planes.reachable(a)`

Returns all other planes or regions reachable from `a`, in deterministic breadth-first order. The starting point is excluded.

## Energy transfer

With `planes` alone, **only energy crosses pathways**. Being transfer is not implemented by this library. Energy has no plane-specific object property or separate local reservoir; transfers are recorded through MANA's existing energy ledger.

### `planes.send_energy(amount, source, destination, kind=None)`

Moves an energy `Quantity` measured in joules from `source` to `destination` along an open route. `kind` is optional. When supplied, it must be a registered elemental/plane-energy name (case-insensitive), such as `"Death"`, or a library-defined internal transfer label. Unknown labels such as `"deth"` raise `TypeErrorML`.

- The source and destination must differ.
- An open route must exist.
- The amount must be finite, non-negative energy measured in joules.
- Taking energy from a non-base elemental plane requires prior invocation of that plane.
- The ledger entry records the amount, source-side delta `-amount`, destination-side delta `+amount`, zero net delta, route, and optional kind label.
- The function emits `energy_arrived` after the transfer.

```mana
load planes
planes.open_path("Underworld", "Mortal Plane")
planes.invoke("Underworld")
receipt = planes.send_energy(500 J, "Underworld", "Mortal Plane", "Death")
total = planes.energy_sent("Underworld", "Mortal Plane")
show receipt.amount_j
show total
```

Expected output:

```text
500.0
500 J
```

The four base elements (`Fire`, `Water`, `Earth`, `Air`) never require invocation. The other nine elemental planes must be invoked before their energy can be taken. Invocation grants permission and does not spend or store mana.

Directly creating a non-base element type, such as `Life`, likewise requires `load planes` and prior `planes.invoke("Life")`. A type such as `Ice` can instead be produced by a valid combination of base elements (Water and Air under the defined interaction rules) without invoking the Ice Plane. These are the two supported routes; a non-base type cannot be created freely as though it were one of the four base elements.

### `planes.open_channel(a, b, rate)`

Opens a continuous, one-direction energy flow from `a` to `b`. `rate` must be a positive power quantity in watts. An open route and any required source invocation must exist. Energy is transferred as virtual time advances through `advance_time`; each transfer is recorded in the ledger. If the route closes or source permission is revoked, the channel closes.

### `planes.close_channel(a, b)`

Closes the channel flowing from `a` to `b`. Returns `true` if a channel existed.

### `planes.energy_sent(a, b)`

Returns a joule quantity with the total recorded planar energy sent from `a` to `b` in the current runtime. It is calculated from ledger entries, not a separate energy store.

## Elemental planes

### `planes.invoke(plane_or_mana)`

Grants permission to take energy from a non-base elemental plane. The argument is normally the plane name. `planes.invoke("Necro")` is a special mana-channel name that grants the same Underworld permission used for ledger-recorded necromantic energy; the physical source remains the Underworld. `planes.invoke("Underworld")` remains accepted as the plane-name form. The four base elements never require invocation. Returns `true` when permission is newly granted (or when no permission is needed) and `false` if the permission was already present.

### `planes.revoke(plane)` and `planes.has_permission(plane)`

`revoke` removes non-base permission and closes continuous channels originating there. It returns `false` for base elements, whose availability cannot be revoked. `has_permission` returns `true` for base elements and otherwise reports whether the plane was invoked.

### `planes.element_of(plane)`

Returns the element held by an elemental plane. It errors for other planes and regions.

### `planes.spirit_of(plane)`

Returns the elemental spirit's data record. It loads `elemental_planes` on demand. This is data lookup only; transferring a being belongs to `summoning`.

## Plane data libraries

The plane data libraries keep records separate from the compact plane registry and are loaded independently:

| Library | Contents |
|---|---|
| `elemental_planes` | The 13 elemental plane records and their elemental spirits |
| `hell` | Hell's current regions and any beings assigned to Hell |
| `heaven` | Beings assigned to Heaven |
| `atlantis` | Mermaid record |
| `fae_paradise` | Elf record |
| `lineage_halls` | Beings assigned to Lineage Halls |
| `wild_realm` | Griffin, werewolf, vampire, chimera, giant, and orc records |

Import `planes` before explicitly importing a plane data library. For example:

```mana
load planes
load wild_realm

creatures = wild_realm.beings
griffin = creatures[0]
home = planes.plane_of(griffin)
show home.name
```

Expected output:

```text
Wild Realm
```

Being records include `name`, `kind`, `home_plane`, `element`, `summoning_requirements`, `hp`, `max_hp`, `defence`, `attack`, and a `resistance` map with values from `0` to `1` for every supported element. Resistance defaults to zero. Every built-in being has initial HP, max HP, defence and attack values; these are editable prototype balance baselines, not canonical statistics from an external source. Custom beings may omit those statistics until their creator chooses values. These fields are data only; the current library does not simulate being behaviour.

## Events

These event names can be used with MANA's `when` statement:

- `path_opened` — a pathway direction changes from closed to open.
- `path_closed` — an open pathway direction changes to closed.
- `energy_arrived` — energy reaches its destination through `send_energy` or an active channel.

The handler's `event_args` list contains the event arguments in order. For example:

```mana
load planes

when path_opened:
    show event_args
```

Expected output:

```text
(no output)
```

## Errors and boundaries

The library raises MANA language errors for unknown planes/regions, invalid categories or argument types, attempts to use region-only functions on top-level planes (or vice versa), missing routes, closed pathways, invalid energy units, uninvoked non-base elemental sources, and operations on non-elemental planes where an elemental plane is required. Runtime errors are attached to the source file and line by the interpreter.

This library does not create planes, store arbitrary plane configuration values, give MANA objects a generic `plane` property, or transfer beings. `drafter` creates plane definitions, `summoning` manifests beings through pathways, and `necromancy` records `Necro` mana usage with the Underworld as its accounting source for local bodies or solid constructs. Plane values are data and do not modify general MANA execution or physics.


## Integration boundaries

`planes` does not create plane definitions or transfer beings. `drafter` registers new plane identities; `summoning` resolves being records and requires an open route to manifest a being in the Mortal Plane; `necromancy` uses `planes` to record the use of the Necro mana channel for an existing local body or a solid construct; it does not depend on `summoning`. Import `planes` before any of those libraries.

## Built-in being statistics

Every built-in being record has an initial `hp`, `max_hp`, `defence`, and `attack` value, plus a resistance value for every supported element. Resistances default to `0` (no protection) and use the range `0` to `1`. The listed combat values are **editable prototype balance baselines**, chosen to provide usable relative durability and attack strength; they are not canonical statistics from a particular mythology or external fictional franchise. Custom plane data can define its own values.
