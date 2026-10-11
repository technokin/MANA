# MANA Libraries Folder

Place compiled MANA library packages (`.manalib`) in this folder. Import them from a `.mana` program by library name:

```mana
load my_library
show my_library.identity(42)
```

Create and build a library with the tooling in `tools/library_builder.py`. Read `docs/current/libraries/LIBRARY_BUILDER.md` before publishing a library. Built-in libraries `geometry2d`, `vector3d`, `planes`, `mana`, `drafter`, `summoning`, and `necromancy` do not need to be installed here. `drafter` creates plane definitions, `summoning` transfers defined beings into the simulated Mortal Plane through open pathways, and `necromancy` reanimates bodies already present in the Mortal Plane using Underworld energy. Plane data libraries (`elemental_planes`, `hell`, `heaven`, `atlantis`, `fae_paradise`, `lineage_halls`, and `wild_realm`) are also built in. The lowercase `mana` namespace is installed automatically; importing it is optional.
