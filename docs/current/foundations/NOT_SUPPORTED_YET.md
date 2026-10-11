# MANA: Not Supported Yet

**Page kind:** Explanation

This page collects current limitations in one place. A listed limitation is not necessarily a bug: it means the capability is not part of the implemented runtime yet. The [Implementation Status](IMPLEMENTATION_STATUS.md) page records the wider status of each subsystem.

| Limitation | Current behaviour | Related documentation |
|---|---|---|
| No 3D world simulation | The world solver advances objects and resolves collisions in 2D. `vector3d` provides calculations only. | [World Engine: 2D and 3D](WORLD_ENGINE_2D_3D.md), [3D Vector Calculations](../libraries/VECTOR3D_LIBRARY.md) |
| Beings do not autonomously fight | Being records and combat-like statistics exist, but there is no complete combat AI or tactical behaviour system. | [Beings and Summoning](BEINGS_AND_SUMMONING.md), [Creature Catalogue](CREATURE_CATALOGUE.md) |
| Plane interiors are not fully simulated | Plane metadata, regions, pathways, and energy-transfer functions exist; every plane is not an independently simulated world. | [Planes and Pathways](PLANES_AND_PATHWAYS.md), [Plane Catalogue](PLANE_CATALOGUE.md) |
| Arbitrary interplane travel is limited | Current being transfer follows implemented routes and destinations; it is not unrestricted movement to any imaginable plane. | [Summoning Library](../libraries/SUMMONING_LIBRARY.md) |
| Naraka sub-regions remain future expansion | Current region entries and names are catalogue data, not a complete simulation of every sub-region. | [Plane Catalogue](PLANE_CATALOGUE.md) |
| Necromancy is a subset | Reanimation operates on existing remains; it does not provide a complete lifecycle, autonomous undead AI, or every custom-spell accounting rule. | [Necromancy and Undead](NECROMANCY_AND_UNDEAD.md), [Necromancy Library](../libraries/NECROMANCY_LIBRARY.md) |
| Static checking is not full execution verification | `--check` catches lexical and syntax errors, not every runtime or physical failure. | [Language Specification](../language/LANGUAGE_SPEC.md), [Error Catalogue](../reference/ERROR_CATALOGUE.md) |

Planned features must not be described as implemented until the runtime, documentation, and tests agree.
