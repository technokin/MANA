# `drafter` Library — MANA v1.0.0

**Page kind:** Reference  

`drafter` creates custom plane definitions. It is a creator, not an editor: a draft may be configured before creation, and `create()` registers it. The library cannot modify a plane after creation. Import `planes` first.

```mana
load planes
load drafter

draft = drafter.begin("Crystal Reach", "ordinary", plane_id="crystal_reach")
drafter.set_value(draft, "gravity_factor", 0.5)
drafter.set_value(draft, "mana_density", 3)
drafter.add_being(draft, "Crystal Drake", "beast", element="Earth", requirements=["crystal heart"])
created_plane = drafter.create(draft)
show planes.identify("Crystal Reach").name
```

Expected output:

```text
Crystal Reach
```

## Creating a plane

### `drafter.begin(name, category="ordinary", plane_id=None)`

Starts a new plane draft. `name` and `category` must be non-empty text. Categories accept a letter-led string containing letters, digits, and spaces; custom category values are supported. If `plane_id` is omitted it is derived from the name. An explicit ID must be lowercase letters/digits/underscores and begin with a letter. The plane is not registered until `drafter.create(draft)` succeeds.

### `drafter.alias(draft, name)`

Adds another name that can identify the new plane. Repeating the same alias on one draft returns `false`. Conflicts with already registered plane or region names are reported at creation and the registration is rolled back.

### `drafter.set_value(draft, key, value)`

Sets a custom value on a plane draft or region draft. The key must be an identifier; metadata keys (`id`, `name`, `category`, `beings`, `regions`, `parent`, and `created`) are reserved. Values may be finite numbers, strings, booleans, null, quantities, vectors, lists, tuples, and text-keyed dictionaries. Executable values, world objects, circular references, and deeply nested values are rejected. Custom values do not change how MANA code or physics behaves.

### `drafter.add_region(draft, name, region_id=None)`

Adds a region to a plane draft. Regions have their own custom values and beings. Nested regions are not supported in this first implementation. The optional ID follows the same ID rules as plane IDs.

### `drafter.add_being(draft_or_region, name, kind="beast", element=None, requirements=None, hp=None, max_hp=None, defence=None, attack=None)`

Adds a being record to the draft or one of its regions. `requirements` is a list of non-empty text values. HP, maximum HP, defence, and attack may be omitted and then remain unset; if supplied they must be finite and non-negative, and HP cannot exceed max HP. Every element resistance defaults to `0` (no protection).

### `drafter.set_being(draft_or_region, being_name, key, value)`

Changes a being's fields while the plane is still a draft. Supported keys: `kind`, `element`, `hp`, `max_hp`, `defence`, `attack`, `summoning_requirements`, and `resistance.<Element>`. Resistance must be a finite value from `0` through `1`. This function cannot edit a plane after creation.

### `drafter.create(draft)`

Registers the plane identity, regions, custom values and beings as one operation. If registration or a `plane_created` event handler fails, registry/data changes are rolled back and the draft remains uncreated. A successful draft becomes immutable through `drafter`.

## Reading registered data

These are read-only helpers; they do not edit an existing plane:

- `drafter.properties_of(plane_or_region)` returns a copy of the custom values.
- `drafter.get_value(plane_or_region, key)` returns one custom value or errors if it does not exist.
- `drafter.beings_of(plane_or_region)` returns being records assigned to the plane/region. A plane's list includes its beings and the beings in its regions; `beings_of(region)` returns that region's own beings.

Beings assigned to a region still use the containing plane as their `home_plane`; regions are not a being's home-plane field. `planes.plane_of(being)` resolves this home plane.

## Terminal workflow and limits

Write the configuration as a `.mana` setup program and run it with the MANA interpreter. The created definition currently lives in that runtime session. Keep the setup program and run it in a new session when the same custom plane is needed again. This version does not generate a persistent plane-data file or a `.manalib` archive automatically. The later IDE can provide a graphical front end to the same creation operations without changing the underlying data model.

`drafter` must be imported after `planes`. Creating planes from inside a `post()` or `release()` spell is rejected because plane definitions are configuration data, not an in-spell world mutation. The library does not implement plane physics, access rules, or entity transfer.

Errors use MANA's standard error classes and receive the calling file and line from the runtime.
