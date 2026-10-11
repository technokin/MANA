# `summoning` Library — MANA v1.0.0

**Page kind:** Reference  

`summoning` brings a defined being through a pathway opened by `planes`. It depends on `planes`. A user-defined spell such as `summon_skeleton` is not a built-in `summoning` function; this library is only for bringing an already-defined being across planes. The destination is implicit: beings manifest in the Mortal Plane, which is the only currently simulated world space.

## `summoning.bring(being, source_plane=None, position=None, requirements=None)`

Resolves and manifests a being. For built-in beings, MANA can infer the home plane, so the normal call is:

```mana
load planes
load summoning

planes.open_path("Wild Realm", "Mortal Plane")
summoning.bring("Griffin")
```

Assigning the result to a name keeps a handle to that particular summoned instance and automatically tames it:

```mana
load planes
load summoning

planes.open_path("Wild Realm", "Mortal Plane")
planes.open_path("Mortal Plane", "Wild Realm")
griffin = summoning.bring("Griffin")
show griffin.tame_name
summoning.send_back(griffin)
summoning.call(griffin)
```

- `being`: a known being name or a `BeingRecord`.
- `source_plane`: optional for built-in beings and already registered custom beings; specify it for ambiguous/unindexed custom records.
- `position`: optional position vector in metres or an existing positioned object. If omitted, the default is 10 m along +X from the runtime caster position.
- `requirements`: optional list of condition strings. Every condition declared on the being must be present; requirements are not automatically searched for or consumed.

An open route from the being's home plane to the Mortal Plane is required. Summoning records the transfer in the internal energy ledger; it does not ask the caller to enter an energy amount. The summoned entity is a normal MANA world object and can use existing movement, physics, `tgset`, and universal mana controls. No generic `plane` property is added.

## Taming and returning a being

### `summoning.tame(being, name=None)`

Marks a summoned instance as tamed. A supplied name is stored as its stable personal name. Assigning the result of `bring()` to a variable automatically tames that instance using the variable name, so an explicit call is optional.

### `summoning.send_back(being)`

Returns an active summoned being to its home plane and marks that instance inactive in the Mortal Plane. A reverse route from the Mortal Plane to its home plane must be open.

### `summoning.call(being)`

Recalls the same tamed instance after `send_back()`. It requires a pathway from the home plane to the Mortal Plane. It does not create a duplicate.

### `summoning.find_being(being, source_plane=None)`

Returns a `BeingRecord`. The source can be omitted for a built-in being that has an entry in the lightweight lookup index. This helper does not copy the being record into a global variable.

## Scope and limits

The current engine can manifest beings only in the Mortal Plane. Other planes have no simulated world space yet. Summoning does not implement AI or combat decisions, and it does not automatically tame an unassigned result. The transfer is represented in MANA's internal ledger; it does not consume a finite mana pool. Errors use MANA's standard error system and receive the source file and line from the runtime.
