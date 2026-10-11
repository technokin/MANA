# MANA v0.10.6 — Necromancy and summoned-entity audit

## Changes

- `planes.invoke("Necro")` is an alias for invoking the Underworld energy channel. The plane registry remains the source identity used by energy-pathway accounting.
- `necromancy.reanimate(corpse, name=None)` and `reanimate_many(corpses, name=None)` do not accept energy amounts. They record ledger-only Necro usage internally, without changing physical object energy or adding `bound_energy`.
- `tgset` marks an object as a body only when its initial declaration identifies bone/corpse/remains material or kind. Relabelling an ordinary Earth object later does not qualify it for reanimation.
- `necromancy.animate_construct(construct, name=None)` animates an existing solid Earth/stone/rock/clay construct without requiring a corpse.
- `summoning.summon(being, source_plane=None, position=None, requirements=None)` uses the Mortal Plane implicitly, infers home planes for indexed built-in beings, and defaults to a position 10 m ahead along +X.
- Assignment of a summoned instance to a variable marks that exact instance as tamed under the variable name. `summoning.tame`, `send_back`, and `call` support explicit naming, return through a reverse route, and recall of the same instance.
- Added the `being_tamed`, `being_returned`, and `being_animated` events.
- Added a canonical location note for the owner-supplied logo SVG at `assets/branding/mana-logo.svg`.

## Verification

- The complete pytest suite passes: **257 tests**.
- All public `.mana` examples run successfully through the smoke test.
- The current VSIX is built from the same `0.10.6` version source and is validated by the packaging tests.
- Local Markdown links were checked after the documentation update.

## Limits

- The world simulation remains 2D; the 3D vector library calculates vectors and bridges planar values only.
- The default Necro ledger amounts (100 J per reanimated body and 250 J per animated construct) are bookkeeping markers, not physical object energy or a finite cost.
- `summoning` can manifest entities only in the Mortal Plane. `send_back` requires a route in the reverse direction.
- Creature AI and independent combat behaviour are not implemented; behaviours are composed from the existing MANA runtime operations.
