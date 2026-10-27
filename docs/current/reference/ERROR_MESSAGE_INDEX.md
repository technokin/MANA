# Generated MANA Error Message Index

**Page kind:** Reference

Generated from direct error-constructor calls in `magiclang/`. Run `python tools/generate_error_catalogue.py` after changing error messages. Dynamic templates show expressions in braces. Errors raised indirectly through a variable are listed as expression-supplied messages where statically visible; runtime-composed details depend on the values involved.

**Indexed call sites:** 1020

| Error class | Source | Line | Message template |
|---|---|---:|---|
| `MagicErrorML` | [`magiclang/libraries/anatomy.py`](../../../magiclang/libraries/anatomy.py) | 89 | `f"unknown anatomy species '{species}'; use anatomy.species() or anatomy.search() ({available})"` |
| `MagicErrorML` | [`magiclang/libraries/anatomy.py`](../../../magiclang/libraries/anatomy.py) | 111 | `f"unknown anatomical structure '{name}'; use anatomy.organs(species) or anatomy.define_organ()"` |
| `MagicErrorML` | [`magiclang/libraries/anatomy.py`](../../../magiclang/libraries/anatomy.py) | 298 | `'unknown human bone region; use axial, appendicular, cranial_bones, facial_bones, vertebral_column, thoracic_cage, upper_limbs, lower_limbs, or a named girdle'` |
| `MagicErrorML` | [`magiclang/libraries/anatomy.py`](../../../magiclang/libraries/anatomy.py) | 314 | `f"'{region}' is not a known region in the {selected.get('label', species)} skeletal inventory"` |
| `MagicErrorML` | [`magiclang/libraries/anatomy.py`](../../../magiclang/libraries/anatomy.py) | 326 | `'unknown human bone region; use axial, appendicular, or a named bone group'` |
| `MagicErrorML` | [`magiclang/libraries/anatomy.py`](../../../magiclang/libraries/anatomy.py) | 345 | `f"unknown bone region for {selected.get('label', species)}"` |
| `MagicErrorML` | [`magiclang/libraries/anatomy.py`](../../../magiclang/libraries/anatomy.py) | 358 | `f"unknown individually catalogued bone '{name}' for {species}; use anatomy.bone_list(species)"` |
| `MagicErrorML` | [`magiclang/libraries/anatomy.py`](../../../magiclang/libraries/anatomy.py) | 380 | `'anatomy.define_organ() changes the anatomy catalogue; use it in a committed spell'` |
| `MagicErrorML` | [`magiclang/libraries/anatomy.py`](../../../magiclang/libraries/anatomy.py) | 385 | `f"anatomical structure '{key}' already exists"` |
| `MagicErrorML` | [`magiclang/libraries/anatomy.py`](../../../magiclang/libraries/anatomy.py) | 419 | `'anatomy.define_system() changes the anatomy catalogue; use it in a committed spell'` |
| `MagicErrorML` | [`magiclang/libraries/anatomy.py`](../../../magiclang/libraries/anatomy.py) | 425 | `f"anatomy system '{key}' already exists"` |
| `MagicErrorML` | [`magiclang/libraries/anatomy.py`](../../../magiclang/libraries/anatomy.py) | 466 | `'anatomy.define_species() changes the species catalogue; use it in a committed spell'` |
| `MagicErrorML` | [`magiclang/libraries/anatomy.py`](../../../magiclang/libraries/anatomy.py) | 471 | `f"species '{key}' already exists or is a reserved alias"` |
| `MagicErrorML` | [`magiclang/libraries/anatomy.py`](../../../magiclang/libraries/anatomy.py) | 488 | `'anatomy.define_species() trait_merge must be primary, max, or mean'` |
| `MagicErrorML` | [`magiclang/libraries/anatomy.py`](../../../magiclang/libraries/anatomy.py) | 518 | `f"unknown organ '{value}'; define it with anatomy.define_organ() first"` |
| `MagicErrorML` | [`magiclang/libraries/anatomy.py`](../../../magiclang/libraries/anatomy.py) | 533 | `'a custom species must retain at least one anatomical structure'` |
| `MagicErrorML` | [`magiclang/libraries/anatomy.py`](../../../magiclang/libraries/anatomy.py) | 551 | `'skeleton_type must be endoskeleton, exoskeleton, hydrostatic, hybrid, none, or custom'` |
| `MagicErrorML` | [`magiclang/libraries/anatomy.py`](../../../magiclang/libraries/anatomy.py) | 731 | `'anatomy.bind() requires a living being or target profile, not an ordinary physical object'` |
| `MagicErrorML` | [`magiclang/libraries/anatomy.py`](../../../magiclang/libraries/anatomy.py) | 733 | `'anatomy.bind() cannot change an inactive entity'` |
| `MagicErrorML` | [`magiclang/libraries/anatomy.py`](../../../magiclang/libraries/anatomy.py) | 735 | `'anatomy.bind() changes an entity body model; use it in a committed spell'` |
| `MagicErrorML` | [`magiclang/libraries/anatomy.py`](../../../magiclang/libraries/anatomy.py) | 829 | `'anatomy.track() requires a living being or target profile, not an ordinary physical object'` |
| `MagicErrorML` | [`magiclang/libraries/anatomy.py`](../../../magiclang/libraries/anatomy.py) | 831 | `'anatomy.track() cannot change an inactive entity'` |
| `MagicErrorML` | [`magiclang/libraries/anatomy.py`](../../../magiclang/libraries/anatomy.py) | 833 | `'anatomy.track() changes the entity body model; use it in a committed spell'` |
| `MagicErrorML` | [`magiclang/libraries/arcana.py`](../../../magiclang/libraries/arcana.py) | 69 | `f"unknown magical discipline '{name}'; use arcana.schools() or arcana.search()"` |
| `MagicErrorML` | [`magiclang/libraries/arcana.py`](../../../magiclang/libraries/arcana.py) | 90 | `'arcana.define() changes the catalogue; use a committed spell'` |
| `MagicErrorML` | [`magiclang/libraries/arcana.py`](../../../magiclang/libraries/arcana.py) | 96 | `f"magical discipline '{key}' already exists or is reserved by an alias"` |
| `MagicErrorML` | [`magiclang/libraries/armory.py`](../../../magiclang/libraries/armory.py) | 31 | `f"armory.{label}() expects a living being or target profile"` |
| `MagicErrorML` | [`magiclang/libraries/armory.py`](../../../magiclang/libraries/armory.py) | 33 | `f"armory.{label}() cannot use an inactive target"` |
| `MagicErrorML` | [`magiclang/libraries/armory.py`](../../../magiclang/libraries/armory.py) | 50 | `f"unknown item blueprint '{item}'; use armory.blueprints()"` |
| `MagicErrorML` | [`magiclang/libraries/armory.py`](../../../magiclang/libraries/armory.py) | 82 | `'armory.define() changes the world catalogue; call it in an executable spell'` |
| `MagicErrorML` | [`magiclang/libraries/armory.py`](../../../magiclang/libraries/armory.py) | 88 | `'armory.define() name must be 1–64 letters, digits, spaces, or hyphens and start with a letter'` |
| `MagicErrorML` | [`magiclang/libraries/armory.py`](../../../magiclang/libraries/armory.py) | 90 | `f"item blueprint '{display}' is already registered"` |
| `MagicErrorML` | [`magiclang/libraries/armory.py`](../../../magiclang/libraries/armory.py) | 92 | `'armory.define() slot must be weapon, shield, body_armour, head, hands, legs, projectile, tool, or resource'` |
| `MagicErrorML` | [`magiclang/libraries/armory.py`](../../../magiclang/libraries/armory.py) | 98 | `f"unknown material '{material}'; inspect materials.all() or define it with materials.define() first"` |
| `MagicErrorML` | [`magiclang/libraries/armory.py`](../../../magiclang/libraries/armory.py) | 108 | `'armory.define() shape must be a supported MANA shape'` |
| `MagicErrorML` | [`magiclang/libraries/armory.py`](../../../magiclang/libraries/armory.py) | 135 | `'armory.define() payload is unsupported'` |
| `MagicErrorML` | [`magiclang/libraries/armory.py`](../../../magiclang/libraries/armory.py) | 138 | `'only projectile blueprints may have a payload'` |
| `MagicErrorML` | [`magiclang/libraries/armory.py`](../../../magiclang/libraries/armory.py) | 154 | `'launch_speed is only supported by equipment with attack_style="ranged"'` |
| `MagicErrorML` | [`magiclang/libraries/armory.py`](../../../magiclang/libraries/armory.py) | 170 | `'armory.equip() requires an item made from a conjure equipment blueprint'` |
| `MagicErrorML` | [`magiclang/libraries/armory.py`](../../../magiclang/libraries/armory.py) | 172 | `'projectiles are ammunition; launch them instead of equipping them as worn gear'` |
| `MagicErrorML` | [`magiclang/libraries/armory.py`](../../../magiclang/libraries/armory.py) | 174 | `'armory.equip() cannot equip an inactive item'` |
| `MagicErrorML` | [`magiclang/libraries/armory.py`](../../../magiclang/libraries/armory.py) | 177 | `'this item is already equipped by another entity; unequip it first'` |
| `MagicErrorML` | [`magiclang/libraries/armory.py`](../../../magiclang/libraries/armory.py) | 184 | `f"{slot} slot is already occupied; unequip its current item first"` |
| `MagicErrorML` | [`magiclang/libraries/armory.py`](../../../magiclang/libraries/armory.py) | 202 | `'this item is not equipped by that wearer'` |
| `MagicErrorML` | [`magiclang/libraries/armory.py`](../../../magiclang/libraries/armory.py) | 217 | `'armory.imbue() currently supports conjured projectile blueprints only'` |
| `MagicErrorML` | [`magiclang/libraries/armory.py`](../../../magiclang/libraries/armory.py) | 223 | `'unsupported projectile payload; choose none, binding, net, shock, smoke, flare, anchor, burst, or acid'` |
| `MagicErrorML` | [`magiclang/libraries/armory.py`](../../../magiclang/libraries/armory.py) | 245 | `'armory.launch() requires a projectile created from a conjure blueprint'` |
| `MagicErrorML` | [`magiclang/libraries/armory.py`](../../../magiclang/libraries/armory.py) | 247 | `'armory.launch() requires unused, unequipped ammunition'` |
| `MagicErrorML` | [`magiclang/libraries/armory.py`](../../../magiclang/libraries/armory.py) | 254 | `'armory.launch() requires a ranged launcher equipped by the wielder'` |
| `MagicErrorML` | [`magiclang/libraries/armory.py`](../../../magiclang/libraries/armory.py) | 257 | `'armory.launch() requires positioned wielder and target'` |
| `MagicErrorML` | [`magiclang/libraries/armory.py`](../../../magiclang/libraries/armory.py) | 305 | `'armory.strike() requires a conjured melee weapon blueprint'` |
| `MagicErrorML` | [`magiclang/libraries/armory.py`](../../../magiclang/libraries/armory.py) | 307 | `'armory.strike() requires the weapon to be equipped by the wielder'` |
| `MagicErrorML` | [`magiclang/libraries/armory.py`](../../../magiclang/libraries/armory.py) | 321 | `'armory.strike() requires positioned entities'` |
| `MagicErrorML` | [`magiclang/libraries/armory.py`](../../../magiclang/libraries/armory.py) | 325 | `f"target is out of weapon reach ({distance} m > {reach} m)"` |
| `MagicErrorML` | [`magiclang/libraries/armory.py`](../../../magiclang/libraries/armory.py) | 328 | `'armory.strike() target needs an active hit-point profile'` |
| `MagicErrorML` | [`magiclang/libraries/drafter.py`](../../../magiclang/libraries/drafter.py) | 86 | `f"drafter.{operation}() defines plane data and cannot run inside post()/release()"` |
| `MagicErrorML` | [`magiclang/libraries/drafter.py`](../../../magiclang/libraries/drafter.py) | 88 | `f"drafter.{operation}() cannot mutate a draft from a directly called helper"` |
| `MagicErrorML` | [`magiclang/libraries/mana.py`](../../../magiclang/libraries/mana.py) | 223 | `f"{operation}() changes the world and cannot run inside a directly called helper; execute the containing spell with post() or release()"` |
| `MagicErrorML` | [`magiclang/libraries/mana.py`](../../../magiclang/libraries/mana.py) | 295 | `f"unsupported mana construct shape '{shape}'; choose a shape from the MANA shape catalogue"` |
| `MagicErrorML` | [`magiclang/libraries/mana.py`](../../../magiclang/libraries/mana.py) | 458 | `'mana.control() action must be toward, away, lift, hold, stop, or release'` |
| `MagicErrorML` | [`magiclang/libraries/materials.py`](../../../magiclang/libraries/materials.py) | 70 | `f"unknown physical material '{value}'; check materials.search() or periodic.lookup()"` |
| `MagicErrorML` | [`magiclang/libraries/materials.py`](../../../magiclang/libraries/materials.py) | 137 | `'materials.by_state() state must be solid, liquid, gas, plasma, or powder'` |
| `MagicErrorML` | [`magiclang/libraries/materials.py`](../../../magiclang/libraries/materials.py) | 228 | `'materials.define() changes the world catalogue; call it inside an executable spell'` |
| `MagicErrorML` | [`magiclang/libraries/materials.py`](../../../magiclang/libraries/materials.py) | 232 | `'materials.define() name must be 1–64 letters, digits, spaces, or hyphens and start with a letter'` |
| `MagicErrorML` | [`magiclang/libraries/materials.py`](../../../magiclang/libraries/materials.py) | 234 | `f"'{display_name}' is already registered; custom materials cannot shadow catalogue entries"` |
| `MagicErrorML` | [`magiclang/libraries/materials.py`](../../../magiclang/libraries/materials.py) | 236 | `f"custom material '{display_name}' is already defined in this world"` |
| `MagicErrorML` | [`magiclang/libraries/materials.py`](../../../magiclang/libraries/materials.py) | 243 | `'materials.define() state must be solid, liquid, gas, plasma, or powder'` |
| `MagicErrorML` | [`magiclang/libraries/materials.py`](../../../magiclang/libraries/materials.py) | 317 | `'composition entries must use Symbol:mass_fraction, separated by commas'` |
| `MagicErrorML` | [`magiclang/libraries/materials.py`](../../../magiclang/libraries/materials.py) | 320 | `f"unknown element symbol/name in custom composition: '{bits[0].strip()}'"` |
| `MagicErrorML` | [`magiclang/libraries/materials.py`](../../../magiclang/libraries/materials.py) | 322 | `f"element {element.symbol} appears more than once in custom composition"` |
| `MagicErrorML` | [`magiclang/libraries/materials.py`](../../../magiclang/libraries/materials.py) | 332 | `f"periodic data for {element.symbol} has no usable atomic mass"` |
| `MagicErrorML` | [`magiclang/libraries/metals.py`](../../../magiclang/libraries/metals.py) | 47 | `'metals.control() changes the world; use it inside a spell'` |
| `MagicErrorML` | [`magiclang/libraries/metals.py`](../../../magiclang/libraries/metals.py) | 52 | `'metals.control() cannot control an inactive object'` |
| `MagicErrorML` | [`magiclang/libraries/metals.py`](../../../magiclang/libraries/metals.py) | 54 | `'metals.control() requires an object made from a registered metal or alloy'` |
| `MagicErrorML` | [`magiclang/libraries/metals.py`](../../../magiclang/libraries/metals.py) | 70 | `'metals.field() changes world state; use it inside a spell'` |
| `MagicErrorML` | [`magiclang/libraries/necromancy.py`](../../../magiclang/libraries/necromancy.py) | 34 | `f"necromancy.{operation}() changes the world; execute it within post()/release()"` |
| `MagicErrorML` | [`magiclang/libraries/necromancy.py`](../../../magiclang/libraries/necromancy.py) | 41 | `f"necromancy.{operation}() cannot affect an inactive object"` |
| `MagicErrorML` | [`magiclang/libraries/necromancy.py`](../../../magiclang/libraries/necromancy.py) | 43 | `f"{runtime._object_label(value)} is already animated"` |
| `MagicErrorML` | [`magiclang/libraries/necromancy.py`](../../../magiclang/libraries/necromancy.py) | 68 | `f"necromancy.{operation}() requires an existing object identified as a corpse, bones, skeleton, or remains"` |
| `MagicErrorML` | [`magiclang/libraries/necromancy.py`](../../../magiclang/libraries/necromancy.py) | 135 | `'reanimate_many() cannot contain the same body more than once'` |
| `MagicErrorML` | [`magiclang/libraries/necromancy.py`](../../../magiclang/libraries/necromancy.py) | 171 | `'necromancy.lichify() target and phylactery must be different objects'` |
| `MagicErrorML` | [`magiclang/libraries/necromancy.py`](../../../magiclang/libraries/necromancy.py) | 174 | `'this entity is already bound to a lich phylactery'` |
| `MagicErrorML` | [`magiclang/libraries/necromancy.py`](../../../magiclang/libraries/necromancy.py) | 178 | `'necromancy.lichify() requires a living being or an existing body/remains'` |
| `MagicErrorML` | [`magiclang/libraries/necromancy.py`](../../../magiclang/libraries/necromancy.py) | 183 | `'necromancy.lichify() requires a physical object created by conjure() as the phylactery'` |
| `MagicErrorML` | [`magiclang/libraries/necromancy.py`](../../../magiclang/libraries/necromancy.py) | 189 | `'necromancy.lichify() phylactery cannot be equipped; unequip it first'` |
| `MagicErrorML` | [`magiclang/libraries/necromancy.py`](../../../magiclang/libraries/necromancy.py) | 191 | `'this phylactery is already bound to another entity'` |
| `MagicErrorML` | [`magiclang/libraries/necromancy.py`](../../../magiclang/libraries/necromancy.py) | 247 | `'necromancy.reconstitute() requires a lich bound to a phylactery'` |
| `MagicErrorML` | [`magiclang/libraries/necromancy.py`](../../../magiclang/libraries/necromancy.py) | 254 | `"the lich's phylactery is missing or inactive; reconstitution is impossible"` |
| `MagicErrorML` | [`magiclang/libraries/necromancy.py`](../../../magiclang/libraries/necromancy.py) | 257 | `"the phylactery's soul binding is broken or belongs to another lich"` |
| `MagicErrorML` | [`magiclang/libraries/periodic.py`](../../../magiclang/libraries/periodic.py) | 16 | `f"unknown chemical element '{value}'"` |
| `MagicErrorML` | [`magiclang/libraries/periodic.py`](../../../magiclang/libraries/periodic.py) | 46 | `f"density for {entry.name} is not registered; provide density=... explicitly"` |
| `MagicErrorML` | [`magiclang/libraries/physiology.py`](../../../magiclang/libraries/physiology.py) | 114 | `f"physiology.{operation}() requires a living being or target profile"` |
| `MagicErrorML` | [`magiclang/libraries/physiology.py`](../../../magiclang/libraries/physiology.py) | 116 | `f"physiology.{operation}() cannot affect an inactive being"` |
| `MagicErrorML` | [`magiclang/libraries/physiology.py`](../../../magiclang/libraries/physiology.py) | 122 | `f"physiology.{operation}() changes body state; call it inside an executable spell"` |
| `MagicErrorML` | [`magiclang/libraries/physiology.py`](../../../magiclang/libraries/physiology.py) | 128 | `f"physiology.{operation}() requires a living, conscious-capable body; current state is {state}"` |
| `MagicErrorML` | [`magiclang/libraries/physiology.py`](../../../magiclang/libraries/physiology.py) | 631 | `'physiology.define_form() name must be 1–48 letters, digits, or spaces and start with a letter'` |
| `MagicErrorML` | [`magiclang/libraries/physiology.py`](../../../magiclang/libraries/physiology.py) | 633 | `f"body form '{key}' is already registered"` |
| `MagicErrorML` | [`magiclang/libraries/physiology.py`](../../../magiclang/libraries/physiology.py) | 642 | `f"physiology.define_form() organ '{organ}' is duplicated"` |
| `MagicErrorML` | [`magiclang/libraries/physiology.py`](../../../magiclang/libraries/physiology.py) | 651 | `'physiology.define_form() vital_structures must be included in organs'` |
| `MagicErrorML` | [`magiclang/libraries/physiology.py`](../../../magiclang/libraries/physiology.py) | 658 | `'a living body form must include brain and heart or appropriate clade-specific equivalents (such as ganglia and aortic arches/hemolymph); set vital_structures explicitly for a deliberately different fictional life-support model, or use a purpose-built construct for nonliving forms'` |
| `MagicErrorML` | [`magiclang/libraries/physiology.py`](../../../magiclang/libraries/physiology.py) | 661 | `'physiology.define_form() movement_mode must be terrestrial, flight-capable, swim-capable, slither-capable, amphibious, stationary, burrowing, climbing, gliding, or custom'` |
| `MagicErrorML` | [`magiclang/libraries/physiology.py`](../../../magiclang/libraries/physiology.py) | 676 | `f"unknown body trait '{trait}' in physiology.define_form()"` |
| `MagicErrorML` | [`magiclang/libraries/physiology.py`](../../../magiclang/libraries/physiology.py) | 685 | `f"body trait '{trait}' was specified more than once"` |
| `MagicErrorML` | [`magiclang/libraries/physiology.py`](../../../magiclang/libraries/physiology.py) | 773 | `'physiology.enhance() trait must be strength, speed, endurance, durability, senses, reflexes, regeneration, or recovery'` |
| `MagicErrorML` | [`magiclang/libraries/physiology.py`](../../../magiclang/libraries/physiology.py) | 826 | `"physiology.propel() mode must be 'physical' or 'arcane'"` |
| `MagicErrorML` | [`magiclang/libraries/physiology.py`](../../../magiclang/libraries/physiology.py) | 828 | `'physiology.propel() cannot propel an anchored being; call unanchor() first'` |
| `MagicErrorML` | [`magiclang/libraries/physiology.py`](../../../magiclang/libraries/physiology.py) | 902 | `'physiology.heal() cannot restore a dead being; use physiology.revive() or necromancy'` |
| `MagicErrorML` | [`magiclang/libraries/physiology.py`](../../../magiclang/libraries/physiology.py) | 929 | `'physiology.manipulate_blood() mode must be bind, draw, clot, restore, or purge'` |
| `MagicErrorML` | [`magiclang/libraries/physiology.py`](../../../magiclang/libraries/physiology.py) | 994 | `'unknown body system; use physiology.systems() or anatomy.systems(species) to inspect the catalogue'` |
| `MagicErrorML` | [`magiclang/libraries/physiology.py`](../../../magiclang/libraries/physiology.py) | 1014 | `'physiology.heal_system() cannot restore a dead being; use physiology.revive() or necromancy'` |
| `MagicErrorML` | [`magiclang/libraries/physiology.py`](../../../magiclang/libraries/physiology.py) | 1020 | `'unknown body system; use physiology.systems() or anatomy.systems(species) to inspect the catalogue'` |
| `MagicErrorML` | [`magiclang/libraries/physiology.py`](../../../magiclang/libraries/physiology.py) | 1065 | `'physiology.kill() requires a living target; this target is already dead or undead'` |
| `MagicErrorML` | [`magiclang/libraries/physiology.py`](../../../magiclang/libraries/physiology.py) | 1075 | `'physiology.revive() requires a dead body that still exists'` |
| `MagicErrorML` | [`magiclang/libraries/physiology.py`](../../../magiclang/libraries/physiology.py) | 1077 | `'physiology.revive() cannot reach this soul; resolve its soul binding first'` |
| `MagicErrorML` | [`magiclang/libraries/physiology.py`](../../../magiclang/libraries/physiology.py) | 1080 | `'physiology.revive() body has reached the three-revival stability limit'` |
| `MagicErrorML` | [`magiclang/libraries/physiology.py`](../../../magiclang/libraries/physiology.py) | 1157 | `f"physiology.{operation}() requires a known organ/structure; use anatomy.organs(species) or anatomy.define_organ() to inspect or define the catalogue"` |
| `MagicErrorML` | [`magiclang/libraries/planes.py`](../../../magiclang/libraries/planes.py) | 58 | `f"the {channel_name} mana channel must be invoked before its energy can be recorded; use planes.invoke(\"{channel_name}\") first"` |
| `MagicErrorML` | [`magiclang/libraries/summoning.py`](../../../magiclang/libraries/summoning.py) | 181 | `f"summoning '{record.name}' is missing required conditions: {', '.join(missing)}"` |
| `MagicErrorML` | [`magiclang/libraries/summoning.py`](../../../magiclang/libraries/summoning.py) | 223 | `'summoning.bring() changes the world; call it from a spell using post()/release()'` |
| `MagicErrorML` | [`magiclang/libraries/summoning.py`](../../../magiclang/libraries/summoning.py) | 300 | `'this being has already been sent back'` |
| `MagicErrorML` | [`magiclang/libraries/summoning.py`](../../../magiclang/libraries/summoning.py) | 324 | `'only a named/tamed summoned being can be recalled'` |
| `MagicErrorML` | [`magiclang/libraries/summoning.py`](../../../magiclang/libraries/summoning.py) | 326 | `'this being must be sent back before it can be recalled'` |
| `MagicErrorML` | [`magiclang/libraries/weather.py`](../../../magiclang/libraries/weather.py) | 72 | `'wind_direction must be east, west, north, south, northeast, northwest, southeast, or southwest'` |
| `MagicErrorML` | [`magiclang/libraries/weather.py`](../../../magiclang/libraries/weather.py) | 136 | `'weather.configure() changes world state; call it from a spell with post() or release()'` |
| `MagicErrorML` | [`magiclang/libraries/weather.py`](../../../magiclang/libraries/weather.py) | 138 | `<message supplied by expression: 'weather kind must be one of: ' + ', '.join(_PRESETS)>` |
| `MagicErrorML` | [`magiclang/libraries/weather.py`](../../../magiclang/libraries/weather.py) | 167 | `'precipitation must be none, rain, snow, dust, ash, or hail'` |
| `MagicErrorML` | [`magiclang/libraries/weather.py`](../../../magiclang/libraries/weather.py) | 226 | `'active local weather-zone limit (256) reached; wait for a zone to expire or clear an area'` |
| `MagicErrorML` | [`magiclang/libraries/weather.py`](../../../magiclang/libraries/weather.py) | 295 | `'precipitation kind must be rain, snow, dust, ash, hail, or none'` |
| `MagicErrorML` | [`magiclang/libraries/world.py`](../../../magiclang/libraries/world.py) | 89 | `'world.configure() changes world laws; call it from a spell with post() or release()'` |
| `MagicErrorML` | [`magiclang/libraries/world.py`](../../../magiclang/libraries/world.py) | 135 | `'world.reset() changes world laws; call it from a spell with post() or release()'` |
| `MagicErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 361 | `'mana cannot be stored on a magical object'` |
| `MagicErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 363 | `f"{name} is a runtime-managed property and cannot be assigned directly"` |
| `MagicErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1386 | `'a directly called definition must be pure; move world-changing or scheduling statements into a spell and execute it with post() or release()'` |
| `MagicErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1397 | `'a directly called definition must be pure; use post() or release() to execute a spell'` |
| `MagicErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1432 | `'weather changes world state; place the statement inside a spell and use post() or release()'` |
| `MagicErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1466 | `'a directly called definition cannot weave mana; use post() or release()'` |
| `MagicErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1499 | `'a directly called definition must be pure; use show from a spell or top-level code'` |
| `MagicErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1515 | `f"target '{self._object_label(selected)}' is not targetable"` |
| `MagicErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1718 | `'a directly called definition cannot assign object properties; use post() or release()'` |
| `MagicErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1724 | `'a directly called definition cannot mutate a list; use post() or release()'` |
| `MagicErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1742 | `f"'{element_name}' is not a directly available elemental plane type; combine fundamental elements or use a registered elemental plane"` |
| `MagicErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1749 | `f"creating {element_name} requires 'load planes' and 'planes.invoke(\"{element_name}\")' first"` |
| `MagicErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1755 | `f"creating {element_name} requires 'planes.invoke(\"{element_name}\")' first"` |
| `MagicErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1812 | `'a directly called definition cannot create objects; use post() or release()'` |
| `MagicErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1818 | `f"unknown built-in element or element variable '{element_name}'"` |
| `MagicErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1822 | `f"create expects a registered element type; '{element_name}' is not an element selector"` |
| `MagicErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1826 | `'mana is woven, not created; use `construct = weave mana` and add settings beneath `weave mana:` if needed'` |
| `MagicErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1905 | `f"'{callee.name}' expects one of the four base element types: Fire, Water, Earth, or Air"` |
| `MagicErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1981 | `'a directly called definition must be pure; move world-changing operations into a spell and execute it with post() or release()'` |
| `MagicErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 2187 | `'mana is not stored on objects'` |
| `MagicErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 2190 | `'acceleration_persistent is an internal physics flag; use accelerate() or assign .acc'` |
| `MagicErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 2192 | `'bound_energy is managed by planar energy transfers and cannot be assigned directly'` |
| `MagicErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 2194 | `f"{name} is a runtime-managed cost readout and cannot be assigned directly"` |
| `MagicErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 2199 | `f"{name} is managed by the energy-release ledger and cannot be assigned directly"` |
| `MagicErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 2203 | `f"{name} is managed by runtime object lifecycle operations"` |
| `MagicErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 2205 | `f"{name} is calculated by the integrity system and cannot be assigned directly"` |
| `MagicErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 2206 | `f"{name} is derived from mass, temp, and velocity; change those inputs instead"` |
| `MagicErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 2236 | `f"cannot change {name} on an inactive object; separate or reactivate it first"` |
| `MagicErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 2271 | `'mass cannot be reduced by direct assignment; use a matter-removal operation or Null'` |
| `MagicErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 2312 | `'targets cannot store mana; spell mana is reported as a calculated cost'` |
| `MagicErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 2358 | `'target state must be solid, liquid, gas, plasma, powder, or burning'` |
| `MagicErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 2374 | `'target density is derived from mass and volume; set mass and volume instead'` |
| `MagicErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 2418 | `f"unsupported shape '{geometry}'; choose a shape from the MANA shape catalogue"` |
| `MagicErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 2429 | `'cannot move an anchored object; call unanchor() first'` |
| `MagicErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 2548 | `'cannot apply an impulse to an anchored object; call unanchor() first'` |
| `MagicErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 3216 | `'combine() requires two distinct objects; an object cannot be combined with itself'` |
| `MagicErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 3420 | `'a directly called definition cannot summon a being; put the operation in a spell and use appraise or cast'` |
| `MagicErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 3446 | `'a directly called definition cannot conjure matter; use post() or release()'` |
| `MagicErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 3452 | `'conjure() creates physical matter; use create for elemental manifestations and summoning for beings'` |
| `MagicErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 3476 | `f"unknown equipment blueprint '{item}'; inspect armory.blueprints() for supported forms"` |
| `MagicErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 3478 | `'conjure() cannot specify an item blueprint both as its first word and item=...'` |
| `MagicErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 3487 | `"material=... is only valid when conjuring an equipment blueprint; write 'conjure sword, material=steel'"` |
| `MagicErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 3503 | `'conjure() creates ordinary matter, not pure mana or released-energy carriers; use weave mana for mana constructs'` |
| `MagicErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 3506 | `'conjure() creates physical matter; use create for elemental manifestations and summoning for beings'` |
| `MagicErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 3509 | `f"density for {element_record.name} is not registered; provide density=... explicitly"` |
| `MagicErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 3512 | `f"conjure() has no density for '{material_name}'; provide density=... or use a registered material such as {choices}"` |
| `MagicErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 3536 | `'conjure() shape must be a supported MANA shape'` |
| `MagicErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 3565 | `'conjure() state must be solid, liquid, gas, plasma, or powder'` |
| `MagicErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 3599 | `'conjure() payload must be none, binding, shock, smoke, flare, anchor, burst, or acid'` |
| `MagicErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 3601 | `'payload=... is supported only for projectile blueprints such as arrow, shock arrow, or smoke arrow'` |
| `MagicErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 3683 | `'transmute() requires matter; woven mana and released-energy carriers are not materials'` |
| `MagicErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 3689 | `'transmute() state must be solid, liquid, gas, plasma, or powder'` |
| `MagicErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 3713 | `f"transmute() has no registered density for '{material_name}'; provide density=... or use a registered material/periodic-table element"` |
| `MagicErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 3813 | `'transfigure() works on living beings or matter made by conjure(); use shape() to change ordinary object geometry'` |
| `MagicErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 3892 | `<message supplied by expression: 'unsupported transfiguration form; choose humanoid, wizard, knight, bird, serpent, beast, or golem. Use physiology.define_form() or anatomy.define_species() to register a body form, or shape() for geometric forms.' + suffix>` |
| `MagicErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 3931 | `f"unsupported matter state '{state}'"` |
| `MagicErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 3933 | `f"{self._object_label(target)} is not defined as powderable"` |
| `MagicErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 4148 | `'cannot aim an anchored object; call unanchor() first'` |
| `MagicErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 4165 | `f"cannot {operation} an anchored object; call unanchor() first"` |
| `MagicErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 4473 | `'mana appraisal is calculated internally; do not pass mana= to an operation'` |
| `MagicErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 4490 | `'mana appraisal readout must be a finite non-negative number'` |
| `MagicErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 4494 | `'mana appraisal readout is outside the supported numeric range'` |
| `MagicErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 4496 | `'mana appraisal readout must be a finite non-negative number'` |
| `MagicErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 4623 | `f"{label} must be a non-negative mana amount"` |
| `MagicErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 4627 | `f"{label} is outside the supported numeric range"` |
| `MagicErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 4629 | `f"{label} must be finite"` |
| `MagicErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 4867 | `f"{operation}() cannot modify an inactive object"` |
| `MagicErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 4873 | `f"{operation}() is forbidden for this target"` |
| `MagicErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 4960 | `'simul blocks currently require direct operation calls; nested control flow is ambiguous'` |
| `MagicErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 4965 | `f"simul cannot verify write conflicts for '{op_name}'"` |
| `MagicErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 4967 | `f"{op_name}() needs a target inside simul"` |
| `MagicErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 4973 | `f"simul conflict: {writes[key]} and {op_name}() both write the same {prop} property"` |
| `PhysicsErrorML` | [`magiclang/libraries/anatomy.py`](../../../magiclang/libraries/anatomy.py) | 387 | `'a runtime can define at most 512 custom anatomical structures'` |
| `PhysicsErrorML` | [`magiclang/libraries/anatomy.py`](../../../magiclang/libraries/anatomy.py) | 427 | `'a runtime can define at most 128 custom anatomy systems'` |
| `PhysicsErrorML` | [`magiclang/libraries/anatomy.py`](../../../magiclang/libraries/anatomy.py) | 473 | `'a runtime can define at most 128 custom species profiles'` |
| `PhysicsErrorML` | [`magiclang/libraries/anatomy.py`](../../../magiclang/libraries/anatomy.py) | 531 | `'a species profile can include at most 1024 addressable anatomical structures'` |
| `PhysicsErrorML` | [`magiclang/libraries/anatomy.py`](../../../magiclang/libraries/anatomy.py) | 615 | `f"anatomy.define_species() {trait} must be between 0.05 and 10"` |
| `PhysicsErrorML` | [`magiclang/libraries/anatomy.py`](../../../magiclang/libraries/anatomy.py) | 670 | `f"anatomy.define_species() {field_name} must be a positive finite number"` |
| `PhysicsErrorML` | [`magiclang/libraries/anatomy.py`](../../../magiclang/libraries/anatomy.py) | 673 | `f"anatomy.define_species() {field_name} must not exceed {upper}"` |
| `PhysicsErrorML` | [`magiclang/libraries/anatomy.py`](../../../magiclang/libraries/anatomy.py) | 739 | `'anatomy.bind() body_mass_kg must be positive, finite, and no greater than 1e12'` |
| `PhysicsErrorML` | [`magiclang/libraries/anatomy.py`](../../../magiclang/libraries/anatomy.py) | 841 | `'an entity can track at most 1024 individual anatomical structures'` |
| `PhysicsErrorML` | [`magiclang/libraries/anatomy.py`](../../../magiclang/libraries/anatomy.py) | 846 | `'an entity can track at most 1024 individual anatomical structures'` |
| `PhysicsErrorML` | [`magiclang/libraries/anatomy.py`](../../../magiclang/libraries/anatomy.py) | 855 | `'a body system can track at most 1024 anatomical structures'` |
| `PhysicsErrorML` | [`magiclang/libraries/arcana.py`](../../../magiclang/libraries/arcana.py) | 98 | `'a runtime can define at most 64 custom magical disciplines'` |
| `PhysicsErrorML` | [`magiclang/libraries/armory.py`](../../../magiclang/libraries/armory.py) | 102 | `'armory.define() mass must be between 0.001 and 100000 kg'` |
| `PhysicsErrorML` | [`magiclang/libraries/armory.py`](../../../magiclang/libraries/armory.py) | 116 | `f"armory.define() {label} must be between 0.001 and 1000 metres"` |
| `PhysicsErrorML` | [`magiclang/libraries/armory.py`](../../../magiclang/libraries/armory.py) | 126 | `f"armory.define() {label} must be between {lower} and {upper}"` |
| `PhysicsErrorML` | [`magiclang/libraries/armory.py`](../../../magiclang/libraries/armory.py) | 150 | `'armory.define() launch_speed must be greater than 0 and no more than 2000 m/s'` |
| `PhysicsErrorML` | [`magiclang/libraries/armory.py`](../../../magiclang/libraries/armory.py) | 261 | `'armory.launch() needs a positive target separation greater than 0.1 m'` |
| `PhysicsErrorML` | [`magiclang/libraries/armory.py`](../../../magiclang/libraries/armory.py) | 269 | `'armory.launch() speed must be greater than 0 and no more than 2000 m/s'` |
| `PhysicsErrorML` | [`magiclang/libraries/armory.py`](../../../magiclang/libraries/armory.py) | 273 | `'armory.launch() projectile collision radius is invalid'` |
| `PhysicsErrorML` | [`magiclang/libraries/armory.py`](../../../magiclang/libraries/armory.py) | 318 | `'armory.strike() force must be greater than 0 and no more than 100000 N'` |
| `PhysicsErrorML` | [`magiclang/libraries/geometry2d.py`](../../../magiclang/libraries/geometry2d.py) | 28 | `f"{label} is outside the supported numeric range"` |
| `PhysicsErrorML` | [`magiclang/libraries/geometry2d.py`](../../../magiclang/libraries/geometry2d.py) | 44 | `f"{label} is outside the supported numeric range"` |
| `PhysicsErrorML` | [`magiclang/libraries/geometry2d.py`](../../../magiclang/libraries/geometry2d.py) | 59 | `f"{label} must lie in the 2D x-y plane (z must be 0)"` |
| `PhysicsErrorML` | [`magiclang/libraries/geometry2d.py`](../../../magiclang/libraries/geometry2d.py) | 67 | `f"{label} must lie in the 2D x-y plane (z must be 0)"` |
| `PhysicsErrorML` | [`magiclang/libraries/geometry2d.py`](../../../magiclang/libraries/geometry2d.py) | 74 | `f"{label} cannot be negative"` |
| `PhysicsErrorML` | [`magiclang/libraries/geometry2d.py`](../../../magiclang/libraries/geometry2d.py) | 82 | `f"{label} is undefined for the zero vector"` |
| `PhysicsErrorML` | [`magiclang/libraries/geometry2d.py`](../../../magiclang/libraries/geometry2d.py) | 92 | `'geometry2d.direction() requires z = 0; import vector3d for 3D vectors'` |
| `PhysicsErrorML` | [`magiclang/libraries/geometry2d.py`](../../../magiclang/libraries/geometry2d.py) | 112 | `'angle() is undefined for the zero vector'` |
| `PhysicsErrorML` | [`magiclang/libraries/mana.py`](../../../magiclang/libraries/mana.py) | 39 | `f"{label} must be finite and {requirement}"` |
| `PhysicsErrorML` | [`magiclang/libraries/mana.py`](../../../magiclang/libraries/mana.py) | 66 | `f"{label} cannot be the zero vector"` |
| `PhysicsErrorML` | [`magiclang/libraries/mana.py`](../../../magiclang/libraries/mana.py) | 257 | `'mana.stop() needs an object with positive mass'` |
| `PhysicsErrorML` | [`magiclang/libraries/mana.py`](../../../magiclang/libraries/mana.py) | 403 | `'mana.emit() energy (power × duration) must be finite'` |
| `PhysicsErrorML` | [`magiclang/libraries/materials.py`](../../../magiclang/libraries/materials.py) | 187 | `'materials.recommend() limit must be an integer from 1 to 50'` |
| `PhysicsErrorML` | [`magiclang/libraries/materials.py`](../../../magiclang/libraries/materials.py) | 241 | `'materials.define() density must be between 0.01 and 100000 kg/m^3'` |
| `PhysicsErrorML` | [`magiclang/libraries/materials.py`](../../../magiclang/libraries/materials.py) | 262 | `f"materials.define() {field_name} must be between {lower} and {upper}"` |
| `PhysicsErrorML` | [`magiclang/libraries/materials.py`](../../../magiclang/libraries/materials.py) | 278 | `f"materials.define() {field_name} must be between {lower} and {upper}"` |
| `PhysicsErrorML` | [`magiclang/libraries/materials.py`](../../../magiclang/libraries/materials.py) | 286 | `f"materials.define() {field_name} must be null or a finite Kelvin value from 0 to 1000000"` |
| `PhysicsErrorML` | [`magiclang/libraries/materials.py`](../../../magiclang/libraries/materials.py) | 289 | `'materials.define() boiling_point_k cannot be lower than melting_point_k'` |
| `PhysicsErrorML` | [`magiclang/libraries/materials.py`](../../../magiclang/libraries/materials.py) | 328 | `'composition mass fractions must be greater than 0 and at most 1'` |
| `PhysicsErrorML` | [`magiclang/libraries/materials.py`](../../../magiclang/libraries/materials.py) | 338 | `'custom compositions may contain at most 20 elements'` |
| `PhysicsErrorML` | [`magiclang/libraries/materials.py`](../../../magiclang/libraries/materials.py) | 341 | `'custom composition mass fractions must sum to 1.0 (within 0.02)'` |
| `PhysicsErrorML` | [`magiclang/libraries/metals.py`](../../../magiclang/libraries/metals.py) | 31 | `f"metals.{label}() value must be {'greater than 0' if positive else 'non-negative'}{bound}"` |
| `PhysicsErrorML` | [`magiclang/libraries/metals.py`](../../../magiclang/libraries/metals.py) | 78 | `'the world can contain at most 64 active magnetic fields; wait for one to expire'` |
| `PhysicsErrorML` | [`magiclang/libraries/necromancy.py`](../../../magiclang/libraries/necromancy.py) | 141 | `'necromantic accounting total must be finite'` |
| `PhysicsErrorML` | [`magiclang/libraries/necromancy.py`](../../../magiclang/libraries/necromancy.py) | 187 | `'necromancy.lichify() phylactery must have positive finite mass'` |
| `PhysicsErrorML` | [`magiclang/libraries/periodic.py`](../../../magiclang/libraries/periodic.py) | 29 | `f"atomic number must be between 1 and {len(ELEMENTS)}"` |
| `PhysicsErrorML` | [`magiclang/libraries/physiology.py`](../../../magiclang/libraries/physiology.py) | 136 | `f"physiology.{label} must be between {low} and {high}"` |
| `PhysicsErrorML` | [`magiclang/libraries/physiology.py`](../../../magiclang/libraries/physiology.py) | 274 | `'an entity can track at most 1024 anatomical structures'` |
| `PhysicsErrorML` | [`magiclang/libraries/physiology.py`](../../../magiclang/libraries/physiology.py) | 635 | `'a runtime can register at most 128 custom body forms'` |
| `PhysicsErrorML` | [`magiclang/libraries/physiology.py`](../../../magiclang/libraries/physiology.py) | 780 | `'physiology.enhance() duration must be greater than 0 and at most 60 seconds'` |
| `PhysicsErrorML` | [`magiclang/libraries/physiology.py`](../../../magiclang/libraries/physiology.py) | 786 | `f"a being can have at most {_MAX_ENHANCEMENTS} concurrent body enhancements"` |
| `PhysicsErrorML` | [`magiclang/libraries/physiology.py`](../../../magiclang/libraries/physiology.py) | 824 | `'physiology.propel() speed must be greater than 0 and no greater than the speed of light'` |
| `PhysicsErrorML` | [`magiclang/libraries/physiology.py`](../../../magiclang/libraries/physiology.py) | 833 | `'physiology.propel() requires a being with positive mass'` |
| `PhysicsErrorML` | [`magiclang/libraries/physiology.py`](../../../magiclang/libraries/physiology.py) | 861 | `"requested physical movement exceeds this body's current integrity-energy threshold; enhance/reinforce the body or use physiology.propel(..., mode='arcane') for explicitly magical high-speed movement"` |
| `PhysicsErrorML` | [`magiclang/libraries/physiology.py`](../../../magiclang/libraries/physiology.py) | 936 | `'physiology.manipulate_blood() duration must be greater than 0 and no more than 60 seconds'` |
| `PhysicsErrorML` | [`magiclang/libraries/physiology.py`](../../../magiclang/libraries/physiology.py) | 1041 | `'physiology.set_temperature() must be between 250 K and 400 K'` |
| `PhysicsErrorML` | [`magiclang/libraries/planes.py`](../../../magiclang/libraries/planes.py) | 226 | `'a pathway cannot connect a plane or region to itself'` |
| `PhysicsErrorML` | [`magiclang/libraries/planes.py`](../../../magiclang/libraries/planes.py) | 327 | `'send_energy() requires different source and destination planes or regions'` |
| `PhysicsErrorML` | [`magiclang/libraries/planes.py`](../../../magiclang/libraries/planes.py) | 333 | `'planes.send_energy() amount must be finite and non-negative'` |
| `PhysicsErrorML` | [`magiclang/libraries/planes.py`](../../../magiclang/libraries/planes.py) | 382 | `'open_channel() requires different source and destination planes'` |
| `PhysicsErrorML` | [`magiclang/libraries/planes.py`](../../../magiclang/libraries/planes.py) | 387 | `'planes.open_channel() rate must be finite and positive'` |
| `PhysicsErrorML` | [`magiclang/libraries/three_d.py`](../../../magiclang/libraries/three_d.py) | 30 | `f"{label} is outside the supported numeric range"` |
| `PhysicsErrorML` | [`magiclang/libraries/three_d.py`](../../../magiclang/libraries/three_d.py) | 77 | `'cannot normalize a zero vector'` |
| `PhysicsErrorML` | [`magiclang/libraries/three_d.py`](../../../magiclang/libraries/three_d.py) | 153 | `'angle_between() is undefined for a zero vector'` |
| `PhysicsErrorML` | [`magiclang/libraries/three_d.py`](../../../magiclang/libraries/three_d.py) | 169 | `'cannot project onto a zero vector'` |
| `PhysicsErrorML` | [`magiclang/libraries/three_d.py`](../../../magiclang/libraries/three_d.py) | 215 | `'vector3d.is_zero() tolerance cannot be negative'` |
| `PhysicsErrorML` | [`magiclang/libraries/three_d.py`](../../../magiclang/libraries/three_d.py) | 237 | `'vector3d.is_planar() tolerance cannot be negative'` |
| `PhysicsErrorML` | [`magiclang/libraries/three_d.py`](../../../magiclang/libraries/three_d.py) | 279 | `'vector3d.pressure() area must be greater than zero'` |
| `PhysicsErrorML` | [`magiclang/libraries/weather.py`](../../../magiclang/libraries/weather.py) | 50 | `f"{label} must be finite"` |
| `PhysicsErrorML` | [`magiclang/libraries/weather.py`](../../../magiclang/libraries/weather.py) | 64 | `f"{label} must be finite"` |
| `PhysicsErrorML` | [`magiclang/libraries/weather.py`](../../../magiclang/libraries/weather.py) | 80 | `'wind_direction cannot be the zero vector'` |
| `PhysicsErrorML` | [`magiclang/libraries/weather.py`](../../../magiclang/libraries/weather.py) | 164 | `'weather intensity must be between 0 and 1'` |
| `PhysicsErrorML` | [`magiclang/libraries/weather.py`](../../../magiclang/libraries/weather.py) | 171 | `'wind_speed must be between 0 and 250 m/s'` |
| `PhysicsErrorML` | [`magiclang/libraries/weather.py`](../../../magiclang/libraries/weather.py) | 174 | `'weather temperature must be between 0 K and 10000 K'` |
| `PhysicsErrorML` | [`magiclang/libraries/weather.py`](../../../magiclang/libraries/weather.py) | 181 | `'humidity, clouds, fog, and lightning must be between 0 and 1'` |
| `PhysicsErrorML` | [`magiclang/libraries/weather.py`](../../../magiclang/libraries/weather.py) | 183 | `'heat must be between -1 and 1'` |
| `PhysicsErrorML` | [`magiclang/libraries/weather.py`](../../../magiclang/libraries/weather.py) | 197 | `'weather duration must be greater than 0 and at most 86400 seconds'` |
| `PhysicsErrorML` | [`magiclang/libraries/weather.py`](../../../magiclang/libraries/weather.py) | 214 | `'weather area radius must be greater than 0 and at most 1000000 m'` |
| `PhysicsErrorML` | [`magiclang/libraries/weather.py`](../../../magiclang/libraries/weather.py) | 309 | `'weather temperature must be between 0 K and 10000 K'` |
| `PhysicsErrorML` | [`magiclang/libraries/weather.py`](../../../magiclang/libraries/weather.py) | 329 | `'heat must be between -1 and 1'` |
| `PhysicsErrorML` | [`magiclang/libraries/world.py`](../../../magiclang/libraries/world.py) | 37 | `f"{label} must be finite"` |
| `PhysicsErrorML` | [`magiclang/libraries/world.py`](../../../magiclang/libraries/world.py) | 107 | `'world.configure() air_density must be between 0 and 100 kg/m³'` |
| `PhysicsErrorML` | [`magiclang/libraries/world.py`](../../../magiclang/libraries/world.py) | 112 | `'world.configure() restitution must be between 0 and 1'` |
| `PhysicsErrorML` | [`magiclang/libraries/world.py`](../../../magiclang/libraries/world.py) | 117 | `'world.configure() friction must be between 0 and 2'` |
| `PhysicsErrorML` | [`magiclang/physics.py`](../../../magiclang/physics.py) | 32 | `'vector component is outside the supported numeric range'` |
| `PhysicsErrorML` | [`magiclang/physics.py`](../../../magiclang/physics.py) | 48 | `'vector magnitude exceeds the supported numeric range'` |
| `PhysicsErrorML` | [`magiclang/physics.py`](../../../magiclang/physics.py) | 75 | `'vector scale is outside the supported numeric range'` |
| `PhysicsErrorML` | [`magiclang/physics.py`](../../../magiclang/physics.py) | 77 | `'vector scale must be finite'` |
| `PhysicsErrorML` | [`magiclang/physics.py`](../../../magiclang/physics.py) | 89 | `'division by zero'` |
| `PhysicsErrorML` | [`magiclang/physics.py`](../../../magiclang/physics.py) | 96 | `'vector divisor is outside the supported numeric range'` |
| `PhysicsErrorML` | [`magiclang/physics.py`](../../../magiclang/physics.py) | 98 | `'vector divisor must be finite'` |
| `PhysicsErrorML` | [`magiclang/physics.py`](../../../magiclang/physics.py) | 100 | `'division by zero'` |
| `PhysicsErrorML` | [`magiclang/physics.py`](../../../magiclang/physics.py) | 118 | `'cannot normalize a zero-length vector'` |
| `PhysicsErrorML` | [`magiclang/physics.py`](../../../magiclang/physics.py) | 141 | `f"{label} must lie in the 2D x-y world plane (z must be 0); 3D vector calculations remain available outside world simulation"` |
| `PhysicsErrorML` | [`magiclang/physics.py`](../../../magiclang/physics.py) | 164 | `'numeric physical quantity is outside the supported range'` |
| `PhysicsErrorML` | [`magiclang/physics.py`](../../../magiclang/physics.py) | 166 | `'numeric physical quantity must be finite'` |
| `PhysicsErrorML` | [`magiclang/physics.py`](../../../magiclang/physics.py) | 183 | `'speed cannot exceed c'` |
| `PhysicsErrorML` | [`magiclang/physics.py`](../../../magiclang/physics.py) | 187 | `'a massive object cannot reach c; relativistic energy diverges'` |
| `PhysicsErrorML` | [`magiclang/physics.py`](../../../magiclang/physics.py) | 203 | `'speed cannot exceed c'` |
| `PhysicsErrorML` | [`magiclang/physics.py`](../../../magiclang/physics.py) | 205 | `'a massive object cannot reach c'` |
| `PhysicsErrorML` | [`magiclang/physics.py`](../../../magiclang/physics.py) | 221 | `'area must be greater than zero'` |
| `PhysicsErrorML` | [`magiclang/physics.py`](../../../magiclang/physics.py) | 231 | `'cannot move in a zero-length direction'` |
| `PhysicsErrorML` | [`magiclang/physics.py`](../../../magiclang/physics.py) | 244 | `f"speed {speed} m/s exceeds c ({C} m/s)"` |
| `PhysicsErrorML` | [`magiclang/physics.py`](../../../magiclang/physics.py) | 249 | `'a massive object cannot reach c'` |
| `PhysicsErrorML` | [`magiclang/physics.py`](../../../magiclang/physics.py) | 259 | `f"speed {speed} m/s exceeds c ({C} m/s)"` |
| `PhysicsErrorML` | [`magiclang/physics_engine.py`](../../../magiclang/physics_engine.py) | 76 | `'mass cannot be negative'` |
| `PhysicsErrorML` | [`magiclang/physics_engine.py`](../../../magiclang/physics_engine.py) | 86 | `'collision_radius cannot be negative'` |
| `PhysicsErrorML` | [`magiclang/physics_engine.py`](../../../magiclang/physics_engine.py) | 93 | `'area cannot be negative'` |
| `PhysicsErrorML` | [`magiclang/physics_engine.py`](../../../magiclang/physics_engine.py) | 111 | `'restitution is outside the supported numeric range'` |
| `PhysicsErrorML` | [`magiclang/physics_engine.py`](../../../magiclang/physics_engine.py) | 115 | `'restitution must be between 0 (no bounce) and 1 (elastic bounce)'` |
| `PhysicsErrorML` | [`magiclang/physics_engine.py`](../../../magiclang/physics_engine.py) | 130 | `'friction must be between 0 and 2'` |
| `PhysicsErrorML` | [`magiclang/physics_engine.py`](../../../magiclang/physics_engine.py) | 142 | `'collision radius must be finite and non-negative'` |
| `PhysicsErrorML` | [`magiclang/physics_engine.py`](../../../magiclang/physics_engine.py) | 145 | `'collision radius must be finite and non-negative'` |
| `PhysicsErrorML` | [`magiclang/physics_engine.py`](../../../magiclang/physics_engine.py) | 596 | `'world collider swept bounds exceed the supported numeric range'` |
| `PhysicsErrorML` | [`magiclang/physics_engine.py`](../../../magiclang/physics_engine.py) | 708 | `'physics timestep must be a finite positive duration'` |
| `PhysicsErrorML` | [`magiclang/physics_engine.py`](../../../magiclang/physics_engine.py) | 712 | `'physics timestep is outside the supported numeric range'` |
| `PhysicsErrorML` | [`magiclang/physics_engine.py`](../../../magiclang/physics_engine.py) | 714 | `'physics timestep must be a finite positive duration'` |
| `PhysicsErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1649 | `'wait duration cannot be negative'` |
| `PhysicsErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1658 | `'after delay cannot be negative'` |
| `PhysicsErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1667 | `'every interval must be greater than zero'` |
| `PhysicsErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1858 | `'unary arithmetic result is outside the supported numeric range'` |
| `PhysicsErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1860 | `f"invalid unary arithmetic operation: {exc}"` |
| `PhysicsErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1991 | `'division by zero'` |
| `PhysicsErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1993 | `'operation exceeded the supported numeric range'` |
| `PhysicsErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1995 | `f"operation rejected the supplied numeric value: {exc}"` |
| `PhysicsErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 2086 | `'division by zero'` |
| `PhysicsErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 2090 | `f"exponent exceeds the MANA safety limit ({MAX_POWER_EXPONENT}); value is outside the supported numeric range"` |
| `PhysicsErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 2094 | `f"exponent exceeds the MANA safety limit ({MAX_POWER_EXPONENT}); value is outside the supported numeric range"` |
| `PhysicsErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 2107 | `f"integer power result exceeds the MANA size limit ({MAX_INTEGER_RESULT_BITS} bits)"` |
| `PhysicsErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 2116 | `'division by zero'` |
| `PhysicsErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 2118 | `'arithmetic result is outside the supported numeric range'` |
| `PhysicsErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 2120 | `f"invalid arithmetic operation: {exc}"` |
| `PhysicsErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 2124 | `'arithmetic result is complex; MANA supports real-valued numbers only'` |
| `PhysicsErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 2126 | `'arithmetic result must be finite; operation produced infinity or NaN'` |
| `PhysicsErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 2243 | `'restitution is outside the supported numeric range'` |
| `PhysicsErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 2247 | `'restitution must be between 0 and 1'` |
| `PhysicsErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 2323 | `f"target field '{name}' is outside the supported numeric range"` |
| `PhysicsErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 2325 | `f"target field '{name}' must be finite"` |
| `PhysicsErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 2339 | `f"target {name} must be {rule}"` |
| `PhysicsErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 2343 | `'target temperature cannot be below 0 K'` |
| `PhysicsErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 2372 | `'ignition temperature cannot be below 0 K'` |
| `PhysicsErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 2382 | `'area cannot be negative'` |
| `PhysicsErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 2386 | `'target collision_radius cannot be negative'` |
| `PhysicsErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 2437 | `'move() cannot use a zero direction'` |
| `PhysicsErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 2456 | `'heat() amount cannot be negative; use cool() to decrease temperature'` |
| `PhysicsErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 2484 | `'cool() amount cannot be negative'` |
| `PhysicsErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 2489 | `'cooling cannot reduce temperature below 0 K'` |
| `PhysicsErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 2556 | `'impulse() vector must be non-zero'` |
| `PhysicsErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 2560 | `'impulse() requires a target with positive finite mass'` |
| `PhysicsErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 2608 | `'velocity() speed cannot be negative'` |
| `PhysicsErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 2618 | `f"cannot aim '{self._object_label(target)}' at '{self._object_label(selected)}': they occupy the same position; give the target a distance or position"` |
| `PhysicsErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 2865 | `'automatic target flight exceeds 60 s; use a closer target or configure motion explicitly'` |
| `PhysicsErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 3341 | `'not enough thermal energy is available to form Ice'` |
| `PhysicsErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 3518 | `'conjure() density must be finite and greater than zero'` |
| `PhysicsErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 3523 | `'conjure() mass must be greater than 0 and no more than 1e12 kg'` |
| `PhysicsErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 3527 | `'conjure() dimensions are outside the supported range'` |
| `PhysicsErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 3553 | `f"conjure() {label} must be between 0 and {maximum}"` |
| `PhysicsErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 3561 | `'conjure() temperature must be between 0 K and 10000000 K'` |
| `PhysicsErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 3580 | `f"conjure() {field_name} must be between 0.0001 and 1000 metres"` |
| `PhysicsErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 3590 | `'conjure() durability must be greater than 0 and at most 1e9'` |
| `PhysicsErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 3715 | `'transmute() density must be finite and greater than zero'` |
| `PhysicsErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 3739 | `'transmute() requires positive mass, volume, and area'` |
| `PhysicsErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 3747 | `'transmute() result is outside the supported physical range'` |
| `PhysicsErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 3900 | `'transfigure() scale must be between 0.05 and 20'` |
| `PhysicsErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 3945 | `'absolute pressure cannot be negative'` |
| `PhysicsErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 3955 | `'volume cannot be negative'` |
| `PhysicsErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 4134 | `'direction() component is outside the supported numeric range'` |
| `PhysicsErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 4136 | `'direction() components must be finite'` |
| `PhysicsErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 4140 | `'direction() cannot be the zero vector'` |
| `PhysicsErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 4153 | `'aim() direction cannot be zero'` |
| `PhysicsErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 4168 | `f"{operation}() duration must be between 0 and {MAX_PERSISTENCE_SECONDS} seconds"` |
| `PhysicsErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 4172 | `f"{operation}() duration is outside the supported numeric range"` |
| `PhysicsErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 4174 | `f"{operation}() duration must be between 0 and {MAX_PERSISTENCE_SECONDS} seconds"` |
| `PhysicsErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 4176 | `f"{operation}() force magnitude cannot be negative"` |
| `PhysicsErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 4181 | `f"{operation}() direction cannot be zero"` |
| `PhysicsErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 4187 | `f"{operation}() target must have positive mass"` |
| `PhysicsErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 4238 | `'rotate() angle is outside the supported numeric range'` |
| `PhysicsErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 4254 | `'scale() factor must be finite and greater than zero'` |
| `PhysicsErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 4258 | `'scale() factor is outside the supported numeric range'` |
| `PhysicsErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 4260 | `'scale() factor must be finite and greater than zero'` |
| `PhysicsErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 4267 | `'scale() result is outside the supported numeric range'` |
| `PhysicsErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 4269 | `'scale() would reduce volume to zero; choose a larger factor'` |
| `PhysicsErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 4278 | `'scale() result is outside the supported numeric range'` |
| `PhysicsErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 4439 | `'sqrt() cannot calculate the real square root of a negative value'` |
| `PhysicsErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 4512 | `'planar energy transfer must be finite and non-negative'` |
| `PhysicsErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 4544 | `'energy transfer must be a finite number'` |
| `PhysicsErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 4546 | `'energy transfer must be a finite number'` |
| `PhysicsErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 4658 | `'body mass must be a positive finite number of kilograms'` |
| `PhysicsErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 4660 | `'body mass must be greater than 0 and no greater than 1e12 kg'` |
| `PhysicsErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 4671 | `'current body scale is outside the supported physical-profile range'` |
| `PhysicsErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 4679 | `'body physical dimensions exceed the supported numeric range'` |
| `PhysicsErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 4683 | `'body collision radius must be positive and finite'` |
| `PhysicsErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 4896 | `f"{label} is outside the supported numeric range"` |
| `PhysicsErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 4898 | `f"{label} must be finite"` |
| `PhysicsErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 4923 | `'mass cannot be negative'` |
| `PhysicsErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 4925 | `'volume cannot be negative'` |
| `PhysicsErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 4927 | `'area cannot be negative'` |
| `PhysicsErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 4929 | `'collision_radius cannot be negative; use 0 m for area-derived 2D bounds'` |
| `PhysicsErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 4932 | `'temperature cannot be below 0 K'` |
| `PhysicsErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 4934 | `'temperature exceeds the Planck temperature; this requires the causality library'` |
| `PhysicsErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 4938 | `'absolute pressure cannot be negative'` |
| `PhysicsErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 5074 | `'time advancement requires a finite non-negative duration'` |
| `PhysicsErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 5079 | `'physics timestep must be a finite positive duration'` |
| `PhysicsErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 5081 | `f"physics timestep cannot exceed {MAX_TIMESTEP_SECONDS} s; smaller steps reduce missed collisions"` |
| `PhysicsErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 5492 | `'planar channel produced an invalid energy amount'` |
| `PhysicsErrorML` | [`magiclang/units.py`](../../../magiclang/units.py) | 165 | `'quantity is outside the supported numeric range'` |
| `PhysicsErrorML` | [`magiclang/units.py`](../../../magiclang/units.py) | 167 | `'quantity must be finite'` |
| `PhysicsErrorML` | [`magiclang/units.py`](../../../magiclang/units.py) | 170 | `'mass cannot be negative'` |
| `PhysicsErrorML` | [`magiclang/units.py`](../../../magiclang/units.py) | 172 | `'volume cannot be negative'` |
| `PhysicsErrorML` | [`magiclang/units.py`](../../../magiclang/units.py) | 174 | `'absolute temperature cannot be below 0 K'` |
| `PhysicsErrorML` | [`magiclang/units.py`](../../../magiclang/units.py) | 232 | `'division by zero'` |
| `PhysicsErrorML` | [`magiclang/units.py`](../../../magiclang/units.py) | 236 | `'division by zero'` |
| `PhysicsErrorML` | [`magiclang/units.py`](../../../magiclang/units.py) | 247 | `'division by zero'` |
| `RuntimeErrorML` | [`magiclang/libraries/drafter.py`](../../../magiclang/libraries/drafter.py) | 75 | `'this draft has already been created; registered plane data is immutable through drafter'` |
| `RuntimeErrorML` | [`magiclang/libraries/drafter.py`](../../../magiclang/libraries/drafter.py) | 204 | `f"'{key}' is reserved for plane-definition metadata"` |
| `RuntimeErrorML` | [`magiclang/libraries/drafter.py`](../../../magiclang/libraries/drafter.py) | 207 | `'a plane draft may define at most 256 custom properties'` |
| `RuntimeErrorML` | [`magiclang/libraries/drafter.py`](../../../magiclang/libraries/drafter.py) | 219 | `'a plane draft may define at most 100 regions'` |
| `RuntimeErrorML` | [`magiclang/libraries/drafter.py`](../../../magiclang/libraries/drafter.py) | 221 | `f"region '{name}' is already present in this draft"` |
| `RuntimeErrorML` | [`magiclang/libraries/drafter.py`](../../../magiclang/libraries/drafter.py) | 246 | `'a plane draft may define at most 1000 beings'` |
| `RuntimeErrorML` | [`magiclang/libraries/drafter.py`](../../../magiclang/libraries/drafter.py) | 276 | `'being hp cannot exceed max_hp'` |
| `RuntimeErrorML` | [`magiclang/libraries/drafter.py`](../../../magiclang/libraries/drafter.py) | 278 | `'being hp cannot exceed max_hp'` |
| `RuntimeErrorML` | [`magiclang/libraries/drafter.py`](../../../magiclang/libraries/drafter.py) | 299 | `f"unknown resistance element '{element_name}'"` |
| `RuntimeErrorML` | [`magiclang/libraries/drafter.py`](../../../magiclang/libraries/drafter.py) | 310 | `'being field must be kind, element, hp, max_hp, defence, attack, summoning_requirements, or resistance.<Element>'` |
| `RuntimeErrorML` | [`magiclang/libraries/drafter.py`](../../../magiclang/libraries/drafter.py) | 319 | `f"being '{being_name}' must identify exactly one being in this draft or region"` |
| `RuntimeErrorML` | [`magiclang/libraries/drafter.py`](../../../magiclang/libraries/drafter.py) | 387 | `f"plane or region '{reference.qualified_name}' has no custom property '{key}'"` |
| `RuntimeErrorML` | [`magiclang/libraries/necromancy.py`](../../../magiclang/libraries/necromancy.py) | 126 | `f"necromancy.reanimate_many() is limited to {MAX_REANIMATION_BATCH} bodies per call"` |
| `RuntimeErrorML` | [`magiclang/libraries/planar_registry.py`](../../../magiclang/libraries/planar_registry.py) | 142 | `f"plane or region reference '{value.qualified_name}' is not registered in this MANA runtime"` |
| `RuntimeErrorML` | [`magiclang/libraries/planar_registry.py`](../../../magiclang/libraries/planar_registry.py) | 149 | `f"unknown plane or region '{value}'"` |
| `RuntimeErrorML` | [`magiclang/libraries/planar_registry.py`](../../../magiclang/libraries/planar_registry.py) | 152 | `f"plane or region '{value}' is not currently loaded"` |
| `RuntimeErrorML` | [`magiclang/libraries/planar_registry.py`](../../../magiclang/libraries/planar_registry.py) | 164 | `"a region's parent must be a plane"` |
| `RuntimeErrorML` | [`magiclang/libraries/planar_registry.py`](../../../magiclang/libraries/planar_registry.py) | 172 | `f"region alias '{alias}' conflicts with an existing plane or region"` |
| `RuntimeErrorML` | [`magiclang/libraries/planar_registry.py`](../../../magiclang/libraries/planar_registry.py) | 197 | `"a region's parent must be a top-level plane"` |
| `RuntimeErrorML` | [`magiclang/libraries/planar_registry.py`](../../../magiclang/libraries/planar_registry.py) | 203 | `f"region ID '{region_id}' is already registered"` |
| `RuntimeErrorML` | [`magiclang/libraries/planar_registry.py`](../../../magiclang/libraries/planar_registry.py) | 209 | `f"region alias '{alias}' conflicts with an existing plane or region"` |
| `RuntimeErrorML` | [`magiclang/libraries/planar_registry.py`](../../../magiclang/libraries/planar_registry.py) | 253 | `f"plane ID '{plane_id}' is already registered"` |
| `RuntimeErrorML` | [`magiclang/libraries/planar_registry.py`](../../../magiclang/libraries/planar_registry.py) | 265 | `f"plane alias '{alias}' is already registered"` |
| `RuntimeErrorML` | [`magiclang/libraries/plane_data/elemental_planes.py`](../../../magiclang/libraries/plane_data/elemental_planes.py) | 163 | `f"unknown elemental being '{name}'"` |
| `RuntimeErrorML` | [`magiclang/libraries/planes.py`](../../../magiclang/libraries/planes.py) | 38 | `f"'{_label(reference)}' is not an elemental plane"` |
| `RuntimeErrorML` | [`magiclang/libraries/planes.py`](../../../magiclang/libraries/planes.py) | 40 | `f"elemental plane '{reference.name}' has no data library assigned"` |
| `RuntimeErrorML` | [`magiclang/libraries/planes.py`](../../../magiclang/libraries/planes.py) | 45 | `f"no elemental data record is registered for '{reference.name}'"` |
| `RuntimeErrorML` | [`magiclang/libraries/planes.py`](../../../magiclang/libraries/planes.py) | 184 | `f"regions_of() expects a plane, not region '{_label(reference)}'"` |
| `RuntimeErrorML` | [`magiclang/libraries/planes.py`](../../../magiclang/libraries/planes.py) | 194 | `f"parent_of() expects a region, not plane '{reference.name}'"` |
| `RuntimeErrorML` | [`magiclang/libraries/planes.py`](../../../magiclang/libraries/planes.py) | 303 | `f"no open route connects {_label(start)} to {_label(end)}"` |
| `RuntimeErrorML` | [`magiclang/libraries/planes.py`](../../../magiclang/libraries/planes.py) | 355 | `f"no open route connects {_label(start)} to {_label(end)}"` |
| `RuntimeErrorML` | [`magiclang/libraries/planes.py`](../../../magiclang/libraries/planes.py) | 390 | `f"no open route connects {_label(start)} to {_label(end)}"` |
| `RuntimeErrorML` | [`magiclang/libraries/planes.py`](../../../magiclang/libraries/planes.py) | 455 | `f"no elemental spirit record is defined for '{reference.name}'"` |
| `RuntimeErrorML` | [`magiclang/libraries/summoning.py`](../../../magiclang/libraries/summoning.py) | 101 | `"a being's home plane must be a top-level plane, not a region"` |
| `RuntimeErrorML` | [`magiclang/libraries/summoning.py`](../../../magiclang/libraries/summoning.py) | 103 | `f"being '{record.name}' belongs to '{record.home_plane}', not '{source_ref.name}'"` |
| `RuntimeErrorML` | [`magiclang/libraries/summoning.py`](../../../magiclang/libraries/summoning.py) | 115 | `"a being's home plane must be a top-level plane, not a region"` |
| `RuntimeErrorML` | [`magiclang/libraries/summoning.py`](../../../magiclang/libraries/summoning.py) | 125 | `f"being '{being}' is not defined in plane '{source_ref.name}'"` |
| `RuntimeErrorML` | [`magiclang/libraries/summoning.py`](../../../magiclang/libraries/summoning.py) | 127 | `f"being name '{being}' is duplicated in plane '{source_ref.name}'"` |
| `RuntimeErrorML` | [`magiclang/libraries/summoning.py`](../../../magiclang/libraries/summoning.py) | 156 | `f"unknown being '{being}'; for a custom being, provide its home plane, e.g. summoning.bring(\"Crystal Drake\", \"Crystal Reach\")"` |
| `RuntimeErrorML` | [`magiclang/libraries/summoning.py`](../../../magiclang/libraries/summoning.py) | 161 | `f"being name '{being}' is ambiguous; supply its home plane ({homes})"` |
| `RuntimeErrorML` | [`magiclang/libraries/summoning.py`](../../../magiclang/libraries/summoning.py) | 165 | `"a being's home plane must be a top-level plane, not a region"` |
| `RuntimeErrorML` | [`magiclang/libraries/summoning.py`](../../../magiclang/libraries/summoning.py) | 228 | `'summoning source and destination must be different planes'` |
| `RuntimeErrorML` | [`magiclang/libraries/summoning.py`](../../../magiclang/libraries/summoning.py) | 230 | `f"active summoned-being limit ({MAX_ACTIVE_SUMMONED_BEINGS}) reached; send a being back or return one before summoning another"` |
| `RuntimeErrorML` | [`magiclang/libraries/summoning.py`](../../../magiclang/libraries/summoning.py) | 303 | `'this being has no distinct home plane to return to'` |
| `RuntimeErrorML` | [`magiclang/physics_engine.py`](../../../magiclang/physics_engine.py) | 634 | `'physics broad-phase index exceeded its cell-membership safety limit; reduce the number of very large or fast-moving colliders'` |
| `RuntimeErrorML` | [`magiclang/physics_engine.py`](../../../magiclang/physics_engine.py) | 659 | `'physics broad-phase exceeded its candidate-work safety limit; reduce the number of densely packed colliders'` |
| `RuntimeErrorML` | [`magiclang/physics_engine.py`](../../../magiclang/physics_engine.py) | 666 | `f"physics would check more than {max_pair_checks} collision pairs in one substep; the current budget is exhausted. Reduce colliders or split the scene."` |
| `RuntimeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 133 | `f"cannot safely open library '{name}': {exc.strerror or exc.__class__.__name__}"` |
| `RuntimeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 140 | `f"library '{name}' must be a regular .manalib file"` |
| `RuntimeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 142 | `f"library '{name}' exceeds the {MAX_LIBRARY_ARCHIVE_BYTES}-byte compressed archive limit"` |
| `RuntimeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 147 | `f"library '{name}' exceeds the {MAX_LIBRARY_ARCHIVE_BYTES}-byte compressed archive limit"` |
| `RuntimeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 151 | `f"cannot safely read library '{name}': {exc.strerror or exc.__class__.__name__}"` |
| `RuntimeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 158 | `f"library '{name}' is not a valid .manalib archive"` |
| `RuntimeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 354 | `"mana is not stored on objects; inspect the spell's mana appraisal readout"` |
| `RuntimeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 476 | `f"'{name}' is not identified"` |
| `RuntimeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 738 | `'internal Visualiser observation buffer order is invalid'` |
| `RuntimeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1009 | `<message supplied by expression: 'library load cycle detected: ' + ' -> '.join(cycle)>` |
| `RuntimeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1011 | `f"invalid library name '{name}'"` |
| `RuntimeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1031 | `f"library {name} needs {dependency} loaded first"` |
| `RuntimeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1104 | `f"library name '{name}' is reserved by the MANA language or built-in API"` |
| `RuntimeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1107 | `f"library '{name}' is not available; built-in libraries are geometry2d, vector3d, planes, elemental_planes, hell, heaven, atlantis, fae_paradise, lineage_halls, and wild_realm. User libraries must be packaged as libraries/{name}.manalib"` |
| `RuntimeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1116 | `f"cannot inspect library package '{name}': {exc.strerror or exc.__class__.__name__}"` |
| `RuntimeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1118 | `f"library '{name}' must be a regular .manalib file inside the project libraries directory"` |
| `RuntimeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1127 | `f"library '{name}' exceeds the {MAX_LIBRARY_ARCHIVE_MEMBERS}-member archive limit"` |
| `RuntimeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1132 | `f"library '{name}' contains duplicate archive member names"` |
| `RuntimeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1135 | `f"library '{name}' exceeds the {MAX_LIBRARY_UNCOMPRESSED_BYTES}-byte uncompressed size limit"` |
| `RuntimeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1140 | `f"library package '{name}' is corrupt at {bad_member}"` |
| `RuntimeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1144 | `f"library '{name}' manifest exceeds the {MAX_LIBRARY_MANIFEST_BYTES}-byte safety limit"` |
| `RuntimeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1152 | `f"library '{name}' has no valid or safely nested mana-library.json manifest"` |
| `RuntimeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1154 | `f"library '{name}' manifest must be a JSON object"` |
| `RuntimeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1156 | `f"library '{name}' has an unsupported package format"` |
| `RuntimeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1158 | `f"library manifest name does not match loaded name '{name}'"` |
| `RuntimeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1164 | `f"library '{name}' manifest dependencies must be a unique list of library names"` |
| `RuntimeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1168 | `f"library '{name}' manifest entry must be a relative path string"` |
| `RuntimeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1173 | `f"library '{name}' has an unsafe entry path"` |
| `RuntimeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1177 | `f"library '{name}' is missing its UTF-8 MANA entry file '{entry}'"` |
| `RuntimeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1183 | `f"runtime reached the source-location safety limit ({MAX_SOURCE_LOCATION_ENTRIES} entries)"` |
| `RuntimeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1193 | `f"library '{name}' entry files may contain only ordinary def functions, load statements, and skip at top level"` |
| `RuntimeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1201 | `f"library '{name}' manifest must list one or more valid exported names"` |
| `RuntimeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1208 | `f"library '{name}' exports undefined names: {', '.join(missing_exports)}"` |
| `RuntimeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1216 | `f"library '{name}' is not a valid .manalib archive"` |
| `RuntimeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1234 | `'execution stopped by user'` |
| `RuntimeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1253 | `f"runtime reached the source-location safety limit ({MAX_SOURCE_LOCATION_ENTRIES} entries)"` |
| `RuntimeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1336 | `f"program exceeded the cumulative allocation safety limit ({MAX_CUMULATIVE_ALLOCATION_UNITS} {kind} units)"` |
| `RuntimeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1341 | `f"runtime exceeded its cumulative allocation safety limit ({MAX_RUNTIME_CUMULATIVE_ALLOCATION_UNITS} {kind} units)"` |
| `RuntimeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1354 | `f"program exceeded the execution statement budget ({MAX_EXECUTION_STATEMENTS})"` |
| `RuntimeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1435 | `'the built-in weather rules are unavailable'` |
| `RuntimeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1438 | `'the built-in weather.configure operation is unavailable'` |
| `RuntimeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1448 | `f"invalid library function name '{stmt.name}'"` |
| `RuntimeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1481 | `'the built-in mana construct helper is unavailable'` |
| `RuntimeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1508 | `'incant can only be used inside a def'` |
| `RuntimeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1613 | `'while loop exceeded the safety iteration limit'` |
| `RuntimeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1629 | `'for loop exceeded the safety iteration limit'` |
| `RuntimeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1651 | `f"wait duration exceeds the {MAX_PERSISTENCE_SECONDS}s safety cap"` |
| `RuntimeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1660 | `f"after delay exceeds the {MAX_PERSISTENCE_SECONDS}s safety cap"` |
| `RuntimeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1669 | `'every interval exceeds the persistent-spell safety cap'` |
| `RuntimeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1682 | `f"unsupported statement {type(stmt).__name__}"` |
| `RuntimeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1732 | `f"list index {index} is out of range for a list of length {len(container)}"` |
| `RuntimeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1762 | `f"expression evaluation exceeds the safety limit ({MAX_EXPRESSION_DEPTH} nested operations)"` |
| `RuntimeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1808 | `f"index {index} is out of range for a value of length {len(container)}"` |
| `RuntimeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1863 | `f"unknown unary operator {expr.op}"` |
| `RuntimeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1876 | `f"{name} is a MANA command/special form, not a value-producing function; write it using its documented standalone syntax"` |
| `RuntimeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1896 | `f"unsupported expression {type(expr).__name__}"` |
| `RuntimeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1935 | `f"MANA definition call depth exceeded the safety limit ({MAX_FUNCTION_DEPTH})"` |
| `RuntimeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 2053 | `f"string result exceeds the MANA size limit ({MAX_COLLECTION_SIZE} characters)"` |
| `RuntimeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 2060 | `f"list result exceeds the MANA size limit ({MAX_COLLECTION_SIZE} items)"` |
| `RuntimeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 2077 | `f"repeated {kind} exceed the MANA size limit ({MAX_COLLECTION_SIZE})"` |
| `RuntimeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 2112 | `f"unknown binary operator {op}"` |
| `RuntimeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 2902 | `f"runtime exceeded the world-object safety limit ({MAX_WORLD_OBJECTS_PER_RUNTIME})"` |
| `RuntimeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 2908 | `f"program exceeded the world-object safety limit ({MAX_WORLD_OBJECTS_PER_EXECUTION})"` |
| `RuntimeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 2948 | `'integer is too large to display; reduce its size before using show()'` |
| `RuntimeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 3429 | `'the built-in summoning rules are unavailable'` |
| `RuntimeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 3432 | `'the built-in summoning operation is unavailable'` |
| `RuntimeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 3586 | `'equipment blueprint is missing a physical dimension'` |
| `RuntimeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 3988 | `f"program exceeded the cumulative output safety limit ({MAX_CUMULATIVE_OUTPUT_CHARS} characters)"` |
| `RuntimeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 3993 | `f"runtime exceeded its cumulative output safety limit ({MAX_RUNTIME_CUMULATIVE_OUTPUT_CHARS} characters)"` |
| `RuntimeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 4097 | `'integer is too large to display; reduce its size before using show()'` |
| `RuntimeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 4916 | `'timing value is outside the supported numeric range'` |
| `RuntimeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 4918 | `'timing value must be finite'` |
| `RuntimeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 5041 | `'timer execution exceeded the per-advance safety limit'` |
| `RuntimeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 5045 | `'incant cannot escape from a persistent timer'` |
| `RuntimeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 5092 | `f"advance_time() requires {step_count} physics steps; the safety cap is {MAX_PHYSICS_STEPS_PER_ADVANCE}"` |
| `RuntimeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 5538 | `'span() step cannot be zero'` |
| `RuntimeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 5551 | `'span() exceeds the safety iteration limit'` |
| `RuntimeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 5565 | `f"'{name}' is reserved and cannot be used as an identifier"` |
| `SyntaxErrorML` | [`magiclang/lexer.py`](../../../magiclang/lexer.py) | 24 | `f"source exceeds the {MAX_SOURCE_BYTES}-character safety limit"` |
| `SyntaxErrorML` | [`magiclang/lexer.py`](../../../magiclang/lexer.py) | 31 | `'source contains invalid Unicode surrogate characters'` |
| `SyntaxErrorML` | [`magiclang/lexer.py`](../../../magiclang/lexer.py) | 33 | `f"source exceeds the {MAX_SOURCE_BYTES}-byte safety limit"` |
| `SyntaxErrorML` | [`magiclang/lexer.py`](../../../magiclang/lexer.py) | 42 | `f"source exceeds the {MAX_SOURCE_LINES}-line safety limit"` |
| `SyntaxErrorML` | [`magiclang/lexer.py`](../../../magiclang/lexer.py) | 51 | `f"source exceeds the {MAX_TOKEN_COUNT}-token safety limit"` |
| `SyntaxErrorML` | [`magiclang/lexer.py`](../../../magiclang/lexer.py) | 78 | `'mixed tabs and spaces in indentation'` |
| `SyntaxErrorML` | [`magiclang/lexer.py`](../../../magiclang/lexer.py) | 83 | `'mixed tabs and spaces in indentation; use one style consistently'` |
| `SyntaxErrorML` | [`magiclang/lexer.py`](../../../magiclang/lexer.py) | 97 | `'inconsistent indentation'` |
| `SyntaxErrorML` | [`magiclang/lexer.py`](../../../magiclang/lexer.py) | 135 | `'unterminated string'` |
| `SyntaxErrorML` | [`magiclang/lexer.py`](../../../magiclang/lexer.py) | 139 | `f"string literal exceeds the {MAX_STRING_LITERAL_CHARS}-character safety limit"` |
| `SyntaxErrorML` | [`magiclang/lexer.py`](../../../magiclang/lexer.py) | 152 | `'numeric literal exceeds the supported input range'` |
| `SyntaxErrorML` | [`magiclang/lexer.py`](../../../magiclang/lexer.py) | 157 | `'numeric literal is outside the supported finite range'` |
| `SyntaxErrorML` | [`magiclang/lexer.py`](../../../magiclang/lexer.py) | 212 | `f"unexpected character {ch}"` |
| `SyntaxErrorML` | [`magiclang/parser.py`](../../../magiclang/parser.py) | 65 | `<message supplied by expression: message or self._unexpected_token_message(token_type)>` |
| `SyntaxErrorML` | [`magiclang/parser.py`](../../../magiclang/parser.py) | 125 | `"expression or block nesting exceeds MANA's parser safety limit"` |
| `SyntaxErrorML` | [`magiclang/parser.py`](../../../magiclang/parser.py) | 149 | `f"'{self.current.value}' is reserved and cannot be used as an identifier"` |
| `SyntaxErrorML` | [`magiclang/parser.py`](../../../magiclang/parser.py) | 237 | `"show needs a value, for example 'show stone.temp'"` |
| `SyntaxErrorML` | [`magiclang/parser.py`](../../../magiclang/parser.py) | 243 | `'show/post/release/tune cannot be nested inside another expression'` |
| `SyntaxErrorML` | [`magiclang/parser.py`](../../../magiclang/parser.py) | 245 | `"create must be assigned to a name first, for example 'fire = create Fire'"` |
| `SyntaxErrorML` | [`magiclang/parser.py`](../../../magiclang/parser.py) | 251 | `f"'{expr.name}' is not identified"` |
| `SyntaxErrorML` | [`magiclang/parser.py`](../../../magiclang/parser.py) | 261 | `"write tuning as 'tune(spell.operation) = target, value'"` |
| `SyntaxErrorML` | [`magiclang/parser.py`](../../../magiclang/parser.py) | 267 | `'tune must identify a named spell instance'` |
| `SyntaxErrorML` | [`magiclang/parser.py`](../../../magiclang/parser.py) | 278 | `"the old '.tune' syntax is removed; use 'tune(spell.operation) = target, value'"` |
| `SyntaxErrorML` | [`magiclang/parser.py`](../../../magiclang/parser.py) | 294 | `'show/post/release cannot be assigned to variables; tune is only valid as a special assignment form'` |
| `SyntaxErrorML` | [`magiclang/parser.py`](../../../magiclang/parser.py) | 299 | `"create results must be assigned directly to a variable name, for example 'fire = create Fire'"` |
| `SyntaxErrorML` | [`magiclang/parser.py`](../../../magiclang/parser.py) | 301 | `"create results must be assigned directly, for example 'fire = create Fire'"` |
| `SyntaxErrorML` | [`magiclang/parser.py`](../../../magiclang/parser.py) | 307 | `"create results must be assigned directly, for example 'fire = create Fire'"` |
| `SyntaxErrorML` | [`magiclang/parser.py`](../../../magiclang/parser.py) | 310 | `'show/post/release must be standalone commands; tune must be used as an assignment'` |
| `SyntaxErrorML` | [`magiclang/parser.py`](../../../magiclang/parser.py) | 312 | `'show/post/release/tune cannot be nested inside another command'` |
| `SyntaxErrorML` | [`magiclang/parser.py`](../../../magiclang/parser.py) | 320 | `f"{mode} expects a named spell, for example '{mode}(fireball)'"` |
| `SyntaxErrorML` | [`magiclang/parser.py`](../../../magiclang/parser.py) | 326 | `'release accepts only the spell name; visual presentation is available with post(spell, visual)'` |
| `SyntaxErrorML` | [`magiclang/parser.py`](../../../magiclang/parser.py) | 329 | `"post's second argument must be 'text' or 'visual'"` |
| `SyntaxErrorML` | [`magiclang/parser.py`](../../../magiclang/parser.py) | 333 | `"post accepts at most two arguments: the spell name and optional 'text' or 'visual'"` |
| `SyntaxErrorML` | [`magiclang/parser.py`](../../../magiclang/parser.py) | 341 | `f"{context} cannot contain show/post/release; these are standalone commands"` |
| `SyntaxErrorML` | [`magiclang/parser.py`](../../../magiclang/parser.py) | 346 | `f"{context} cannot contain an unassigned create; use 'name = create Element'"` |
| `SyntaxErrorML` | [`magiclang/parser.py`](../../../magiclang/parser.py) | 405 | `f"expected 'into' in {operation} statement"` |
| `SyntaxErrorML` | [`magiclang/parser.py`](../../../magiclang/parser.py) | 417 | `f"{operation} needs a destination after 'into'; use a name or a parenthesised expression"` |
| `SyntaxErrorML` | [`magiclang/parser.py`](../../../magiclang/parser.py) | 470 | `f"summon option '{key.value}' is specified more than once"` |
| `SyntaxErrorML` | [`magiclang/parser.py`](../../../magiclang/parser.py) | 478 | `'summon options cannot end with a comma'` |
| `SyntaxErrorML` | [`magiclang/parser.py`](../../../magiclang/parser.py) | 480 | `'separate summon options with commas'` |
| `SyntaxErrorML` | [`magiclang/parser.py`](../../../magiclang/parser.py) | 483 | `<message supplied by expression: 'unknown summon option(s): ' + ', '.join(unknown)>` |
| `SyntaxErrorML` | [`magiclang/parser.py`](../../../magiclang/parser.py) | 499 | `f"summon needs a {label}; use a name or a parenthesised expression"` |
| `SyntaxErrorML` | [`magiclang/parser.py`](../../../magiclang/parser.py) | 515 | `'weather needs a named climate preset'` |
| `SyntaxErrorML` | [`magiclang/parser.py`](../../../magiclang/parser.py) | 523 | `f"weather option '{key.value}' is specified more than once"` |
| `SyntaxErrorML` | [`magiclang/parser.py`](../../../magiclang/parser.py) | 536 | `'weather options cannot end with a comma'` |
| `SyntaxErrorML` | [`magiclang/parser.py`](../../../magiclang/parser.py) | 538 | `'separate weather options with commas'` |
| `SyntaxErrorML` | [`magiclang/parser.py`](../../../magiclang/parser.py) | 544 | `<message supplied by expression: 'unknown weather option(s): ' + ', '.join(unknown)>` |
| `SyntaxErrorML` | [`magiclang/parser.py`](../../../magiclang/parser.py) | 552 | `"conjure needs a material name, e.g. 'iron = conjure steel, mass=5 kg'"` |
| `SyntaxErrorML` | [`magiclang/parser.py`](../../../magiclang/parser.py) | 564 | `f"conjure option '{key.value}' is specified more than once"` |
| `SyntaxErrorML` | [`magiclang/parser.py`](../../../magiclang/parser.py) | 575 | `'conjure options cannot end with a comma'` |
| `SyntaxErrorML` | [`magiclang/parser.py`](../../../magiclang/parser.py) | 577 | `'separate conjure options with commas'` |
| `SyntaxErrorML` | [`magiclang/parser.py`](../../../magiclang/parser.py) | 580 | `<message supplied by expression: 'unknown conjure option(s): ' + ', '.join(unknown)>` |
| `SyntaxErrorML` | [`magiclang/parser.py`](../../../magiclang/parser.py) | 600 | `f"parameter '{param}' is defined more than once"` |
| `SyntaxErrorML` | [`magiclang/parser.py`](../../../magiclang/parser.py) | 608 | `'required parameters must come before parameters with defaults'` |
| `SyntaxErrorML` | [`magiclang/parser.py`](../../../magiclang/parser.py) | 616 | `'spell definitions accept no parameters or one element selector: use spell name(element):'` |
| `SyntaxErrorML` | [`magiclang/parser.py`](../../../magiclang/parser.py) | 621 | `'the spell element selector cannot have a default value'` |
| `SyntaxErrorML` | [`magiclang/parser.py`](../../../magiclang/parser.py) | 623 | `'library modules may export ordinary def functions, not spell definitions'` |
| `SyntaxErrorML` | [`magiclang/parser.py`](../../../magiclang/parser.py) | 627 | `'target selection belongs outside a spell; use `tgset(target): release(spell)` around the cast'` |
| `SyntaxErrorML` | [`magiclang/parser.py`](../../../magiclang/parser.py) | 661 | `'incant accepts one value expression; function-call syntax is not supported'` |
| `SyntaxErrorML` | [`magiclang/parser.py`](../../../magiclang/parser.py) | 672 | `'incant accepts one value expression; function-call syntax is not supported'` |
| `SyntaxErrorML` | [`magiclang/parser.py`](../../../magiclang/parser.py) | 677 | `'create results must be assigned directly before use with incant'` |
| `SyntaxErrorML` | [`magiclang/parser.py`](../../../magiclang/parser.py) | 679 | `'show/post/release are commands and tune is not an incant value'` |
| `SyntaxErrorML` | [`magiclang/parser.py`](../../../magiclang/parser.py) | 707 | `f"target field '{field_name}' is defined more than once"` |
| `SyntaxErrorML` | [`magiclang/parser.py`](../../../magiclang/parser.py) | 725 | `'weave currently accepts only `mana`'` |
| `SyntaxErrorML` | [`magiclang/parser.py`](../../../magiclang/parser.py) | 740 | `f"construct setting '{field_name}' is defined more than once"` |
| `SyntaxErrorML` | [`magiclang/parser.py`](../../../magiclang/parser.py) | 927 | `'property name must be an identifier'` |
| `SyntaxErrorML` | [`magiclang/parser.py`](../../../magiclang/parser.py) | 1063 | `<message supplied by expression: message>` |
| `SyntaxErrorML` | [`magiclang/runner.py`](../../../magiclang/runner.py) | 21 | `'MANA source must be a regular file'` |
| `SyntaxErrorML` | [`magiclang/runner.py`](../../../magiclang/runner.py) | 23 | `f"source exceeds the {MAX_SOURCE_FILE_BYTES}-byte safety limit"` |
| `SyntaxErrorML` | [`magiclang/runner.py`](../../../magiclang/runner.py) | 30 | `f"cannot read source file: {exc.strerror or exc.__class__.__name__}"` |
| `SyntaxErrorML` | [`magiclang/runner.py`](../../../magiclang/runner.py) | 32 | `f"source exceeds the {MAX_SOURCE_FILE_BYTES}-byte safety limit"` |
| `SyntaxErrorML` | [`magiclang/runner.py`](../../../magiclang/runner.py) | 39 | `'source file is not valid UTF-8'` |
| `TypeErrorML` | [`magiclang/libraries/anatomy.py`](../../../magiclang/libraries/anatomy.py) | 77 | `f"anatomy.{what} expects non-empty text"` |
| `TypeErrorML` | [`magiclang/libraries/anatomy.py`](../../../magiclang/libraries/anatomy.py) | 211 | `'anatomy.search() expects non-empty search text'` |
| `TypeErrorML` | [`magiclang/libraries/anatomy.py`](../../../magiclang/libraries/anatomy.py) | 352 | `'anatomy.bone() expects a bone name'` |
| `TypeErrorML` | [`magiclang/libraries/anatomy.py`](../../../magiclang/libraries/anatomy.py) | 382 | `'anatomy.define_organ() name must be 1–64 letters, digits, spaces, underscores or hyphens, starting with a letter'` |
| `TypeErrorML` | [`magiclang/libraries/anatomy.py`](../../../magiclang/libraries/anatomy.py) | 389 | `'anatomy.define_organ() system must be a named system'` |
| `TypeErrorML` | [`magiclang/libraries/anatomy.py`](../../../magiclang/libraries/anatomy.py) | 392 | `'anatomy.define_organ() role must be 1–500 characters'` |
| `TypeErrorML` | [`magiclang/libraries/anatomy.py`](../../../magiclang/libraries/anatomy.py) | 397 | `f"anatomy.define_organ() {label} must be a list of up to {max_items} non-empty strings of at most 160 characters"` |
| `TypeErrorML` | [`magiclang/libraries/anatomy.py`](../../../magiclang/libraries/anatomy.py) | 400 | `'anatomy.define_organ() notes must be text no longer than 1000 characters'` |
| `TypeErrorML` | [`magiclang/libraries/anatomy.py`](../../../magiclang/libraries/anatomy.py) | 421 | `'anatomy.define_system() name must be 1–64 valid characters'` |
| `TypeErrorML` | [`magiclang/libraries/anatomy.py`](../../../magiclang/libraries/anatomy.py) | 429 | `'anatomy.define_system() purpose must be 1–1000 characters'` |
| `TypeErrorML` | [`magiclang/libraries/anatomy.py`](../../../magiclang/libraries/anatomy.py) | 431 | `'anatomy.define_system() notes must be text up to 2000 characters'` |
| `TypeErrorML` | [`magiclang/libraries/anatomy.py`](../../../magiclang/libraries/anatomy.py) | 436 | `f"anatomy.define_system() {label} must be a list of up to 64 non-empty strings of at most 160 characters"` |
| `TypeErrorML` | [`magiclang/libraries/anatomy.py`](../../../magiclang/libraries/anatomy.py) | 468 | `'anatomy.define_species() name must be valid non-empty text'` |
| `TypeErrorML` | [`magiclang/libraries/anatomy.py`](../../../magiclang/libraries/anatomy.py) | 479 | `'anatomy.define_species() components must be a list of up to 16 donor species'` |
| `TypeErrorML` | [`magiclang/libraries/anatomy.py`](../../../magiclang/libraries/anatomy.py) | 511 | `f"anatomy.define_species() {label} must be a list of up to 1024 organ names"` |
| `TypeErrorML` | [`magiclang/libraries/anatomy.py`](../../../magiclang/libraries/anatomy.py) | 515 | `f"anatomy.define_species() {label} entries must be text"` |
| `TypeErrorML` | [`magiclang/libraries/anatomy.py`](../../../magiclang/libraries/anatomy.py) | 566 | `'movement_mode must be a supported category or a descriptive gait label up to 120 characters'` |
| `TypeErrorML` | [`magiclang/libraries/anatomy.py`](../../../magiclang/libraries/anatomy.py) | 583 | `f"anatomy.define_species() {label} must be a list of up to 64 capability names"` |
| `TypeErrorML` | [`magiclang/libraries/anatomy.py`](../../../magiclang/libraries/anatomy.py) | 587 | `f"anatomy.define_species() {label} entries must be non-empty text up to 64 characters"` |
| `TypeErrorML` | [`magiclang/libraries/anatomy.py`](../../../magiclang/libraries/anatomy.py) | 599 | `'thermoregulation must be non-empty text up to 240 characters'` |
| `TypeErrorML` | [`magiclang/libraries/anatomy.py`](../../../magiclang/libraries/anatomy.py) | 601 | `'notes must be text up to 2000 characters'` |
| `TypeErrorML` | [`magiclang/libraries/anatomy.py`](../../../magiclang/libraries/anatomy.py) | 729 | `'anatomy.bind() expects a MANA world object'` |
| `TypeErrorML` | [`magiclang/libraries/anatomy.py`](../../../magiclang/libraries/anatomy.py) | 737 | `'anatomy.bind() preserve_injuries must be true or false'` |
| `TypeErrorML` | [`magiclang/libraries/anatomy.py`](../../../magiclang/libraries/anatomy.py) | 826 | `'anatomy.track() expects a MANA world object'` |
| `TypeErrorML` | [`magiclang/libraries/anatomy.py`](../../../magiclang/libraries/anatomy.py) | 936 | `'anatomy.inspect() expects a MANA world object'` |
| `TypeErrorML` | [`magiclang/libraries/arcana.py`](../../../magiclang/libraries/arcana.py) | 56 | `'arcana lookup expects non-empty text'` |
| `TypeErrorML` | [`magiclang/libraries/arcana.py`](../../../magiclang/libraries/arcana.py) | 77 | `'arcana.search() expects non-empty text'` |
| `TypeErrorML` | [`magiclang/libraries/arcana.py`](../../../magiclang/libraries/arcana.py) | 92 | `'arcana.define() name must begin with a letter and contain at most 64 letters, digits, spaces, underscores or hyphens'` |
| `TypeErrorML` | [`magiclang/libraries/arcana.py`](../../../magiclang/libraries/arcana.py) | 101 | `f"arcana.define() {label_name} must be non-empty text up to {max_len} characters"` |
| `TypeErrorML` | [`magiclang/libraries/arcana.py`](../../../magiclang/libraries/arcana.py) | 105 | `f"arcana.define() {label_name} must be a non-empty list of up to {max_count} short text entries"` |
| `TypeErrorML` | [`magiclang/libraries/armory.py`](../../../magiclang/libraries/armory.py) | 23 | `f"armory.{label}() expects a MANA world object"` |
| `TypeErrorML` | [`magiclang/libraries/armory.py`](../../../magiclang/libraries/armory.py) | 84 | `'armory.define() name must be non-empty text'` |
| `TypeErrorML` | [`magiclang/libraries/armory.py`](../../../magiclang/libraries/armory.py) | 94 | `'armory.define() material must be non-empty text'` |
| `TypeErrorML` | [`magiclang/libraries/armory.py`](../../../magiclang/libraries/armory.py) | 104 | `'armory.define() shape must be text'` |
| `TypeErrorML` | [`magiclang/libraries/armory.py`](../../../magiclang/libraries/armory.py) | 123 | `f"armory.define() {label} must be a number"` |
| `TypeErrorML` | [`magiclang/libraries/armory.py`](../../../magiclang/libraries/armory.py) | 132 | `'armory.define() payload must be text'` |
| `TypeErrorML` | [`magiclang/libraries/armory.py`](../../../magiclang/libraries/armory.py) | 140 | `'armory.define() attack_style must be non-empty text no longer than 40 characters'` |
| `TypeErrorML` | [`magiclang/libraries/armory.py`](../../../magiclang/libraries/armory.py) | 142 | `'armory.define() description must be text no longer than 280 characters'` |
| `TypeErrorML` | [`magiclang/libraries/armory.py`](../../../magiclang/libraries/armory.py) | 219 | `'armory.imbue() payload must be text'` |
| `TypeErrorML` | [`magiclang/libraries/armory.py`](../../../magiclang/libraries/armory.py) | 231 | `'armory.has_slot() slot must be text'` |
| `TypeErrorML` | [`magiclang/libraries/armory.py`](../../../magiclang/libraries/armory.py) | 316 | `'armory.strike() force must be a force in newtons (e.g. force=900 N)'` |
| `TypeErrorML` | [`magiclang/libraries/drafter.py`](../../../magiclang/libraries/drafter.py) | 77 | `'expected a draft returned by drafter.begin() or drafter.add_region()'` |
| `TypeErrorML` | [`magiclang/libraries/drafter.py`](../../../magiclang/libraries/drafter.py) | 94 | `'custom plane data nesting exceeds 16 levels'` |
| `TypeErrorML` | [`magiclang/libraries/drafter.py`](../../../magiclang/libraries/drafter.py) | 99 | `'custom plane numeric values must be finite'` |
| `TypeErrorML` | [`magiclang/libraries/drafter.py`](../../../magiclang/libraries/drafter.py) | 107 | `'custom plane data can contain values, not executable functions or world objects'` |
| `TypeErrorML` | [`magiclang/libraries/drafter.py`](../../../magiclang/libraries/drafter.py) | 110 | `'custom plane data cannot contain circular references'` |
| `TypeErrorML` | [`magiclang/libraries/drafter.py`](../../../magiclang/libraries/drafter.py) | 129 | `'custom plane data object keys must be non-empty text'` |
| `TypeErrorML` | [`magiclang/libraries/drafter.py`](../../../magiclang/libraries/drafter.py) | 134 | `f"unsupported custom plane data value: {type(value).__name__}"` |
| `TypeErrorML` | [`magiclang/libraries/drafter.py`](../../../magiclang/libraries/drafter.py) | 165 | `f"invalid being definition '{being.name}': {exc}"` |
| `TypeErrorML` | [`magiclang/libraries/drafter.py`](../../../magiclang/libraries/drafter.py) | 175 | `'drafter.begin() name must be non-empty text'` |
| `TypeErrorML` | [`magiclang/libraries/drafter.py`](../../../magiclang/libraries/drafter.py) | 177 | `'drafter.begin() category must be non-empty text'` |
| `TypeErrorML` | [`magiclang/libraries/drafter.py`](../../../magiclang/libraries/drafter.py) | 180 | `'plane category must start with a letter and contain only letters, digits, or spaces'` |
| `TypeErrorML` | [`magiclang/libraries/drafter.py`](../../../magiclang/libraries/drafter.py) | 184 | `'plane_id must start with a lowercase letter and contain lowercase letters, digits, or underscores'` |
| `TypeErrorML` | [`magiclang/libraries/drafter.py`](../../../magiclang/libraries/drafter.py) | 191 | `'drafter.alias() expects non-empty alias text'` |
| `TypeErrorML` | [`magiclang/libraries/drafter.py`](../../../magiclang/libraries/drafter.py) | 202 | `'custom property name must be a valid identifier'` |
| `TypeErrorML` | [`magiclang/libraries/drafter.py`](../../../magiclang/libraries/drafter.py) | 215 | `'drafter.add_region() expects a plane draft'` |
| `TypeErrorML` | [`magiclang/libraries/drafter.py`](../../../magiclang/libraries/drafter.py) | 217 | `'region name must be non-empty text'` |
| `TypeErrorML` | [`magiclang/libraries/drafter.py`](../../../magiclang/libraries/drafter.py) | 223 | `'region_id must start with a lowercase letter and contain lowercase letters, digits, or underscores'` |
| `TypeErrorML` | [`magiclang/libraries/drafter.py`](../../../magiclang/libraries/drafter.py) | 234 | `'being name must be non-empty text'` |
| `TypeErrorML` | [`magiclang/libraries/drafter.py`](../../../magiclang/libraries/drafter.py) | 236 | `'being kind must be non-empty text'` |
| `TypeErrorML` | [`magiclang/libraries/drafter.py`](../../../magiclang/libraries/drafter.py) | 238 | `'being element must be non-empty text or null'` |
| `TypeErrorML` | [`magiclang/libraries/drafter.py`](../../../magiclang/libraries/drafter.py) | 242 | `'being requirements must be a list of text values'` |
| `TypeErrorML` | [`magiclang/libraries/drafter.py`](../../../magiclang/libraries/drafter.py) | 244 | `'being requirements must contain non-empty text values'` |
| `TypeErrorML` | [`magiclang/libraries/drafter.py`](../../../magiclang/libraries/drafter.py) | 268 | `f"being {key} must be a finite non-negative number or null"` |
| `TypeErrorML` | [`magiclang/libraries/drafter.py`](../../../magiclang/libraries/drafter.py) | 272 | `f"being {key} is outside the supported numeric range"` |
| `TypeErrorML` | [`magiclang/libraries/drafter.py`](../../../magiclang/libraries/drafter.py) | 274 | `f"being {key} must be a finite non-negative number or null"` |
| `TypeErrorML` | [`magiclang/libraries/drafter.py`](../../../magiclang/libraries/drafter.py) | 283 | `'being kind must be non-empty text'` |
| `TypeErrorML` | [`magiclang/libraries/drafter.py`](../../../magiclang/libraries/drafter.py) | 288 | `'being element must be non-empty text or null'` |
| `TypeErrorML` | [`magiclang/libraries/drafter.py`](../../../magiclang/libraries/drafter.py) | 293 | `'summoning_requirements must be a list of non-empty strings'` |
| `TypeErrorML` | [`magiclang/libraries/drafter.py`](../../../magiclang/libraries/drafter.py) | 301 | `'element resistance must be a finite number from 0 to 1'` |
| `TypeErrorML` | [`magiclang/libraries/drafter.py`](../../../magiclang/libraries/drafter.py) | 305 | `'element resistance is outside the supported numeric range'` |
| `TypeErrorML` | [`magiclang/libraries/drafter.py`](../../../magiclang/libraries/drafter.py) | 307 | `'element resistance must be a finite number from 0 to 1'` |
| `TypeErrorML` | [`magiclang/libraries/drafter.py`](../../../magiclang/libraries/drafter.py) | 316 | `'drafter.set_being() expects a being name and field name'` |
| `TypeErrorML` | [`magiclang/libraries/drafter.py`](../../../magiclang/libraries/drafter.py) | 326 | `'drafter.create() expects a plane draft'` |
| `TypeErrorML` | [`magiclang/libraries/drafter.py`](../../../magiclang/libraries/drafter.py) | 328 | `'plane name must be non-empty text'` |
| `TypeErrorML` | [`magiclang/libraries/drafter.py`](../../../magiclang/libraries/drafter.py) | 383 | `'drafter.get_value() key must be non-empty text'` |
| `TypeErrorML` | [`magiclang/libraries/geometry2d.py`](../../../magiclang/libraries/geometry2d.py) | 24 | `f"{label} must be a finite number"` |
| `TypeErrorML` | [`magiclang/libraries/geometry2d.py`](../../../magiclang/libraries/geometry2d.py) | 30 | `f"{label} must be a finite number"` |
| `TypeErrorML` | [`magiclang/libraries/geometry2d.py`](../../../magiclang/libraries/geometry2d.py) | 40 | `f"{label} must be a finite distance in metres"` |
| `TypeErrorML` | [`magiclang/libraries/geometry2d.py`](../../../magiclang/libraries/geometry2d.py) | 46 | `f"{label} must be a finite distance in metres"` |
| `TypeErrorML` | [`magiclang/libraries/geometry2d.py`](../../../magiclang/libraries/geometry2d.py) | 55 | `f"{label} must be a 2D point or an object with a position"` |
| `TypeErrorML` | [`magiclang/libraries/geometry2d.py`](../../../magiclang/libraries/geometry2d.py) | 65 | `f"{label} must be a vector"` |
| `TypeErrorML` | [`magiclang/libraries/geometry2d.py`](../../../magiclang/libraries/geometry2d.py) | 259 | `'polygon_area() expects a list of at least three 2D points'` |
| `TypeErrorML` | [`magiclang/libraries/geometry2d.py`](../../../magiclang/libraries/geometry2d.py) | 396 | `'point_in_polygon() expects a list of at least three points'` |
| `TypeErrorML` | [`magiclang/libraries/mana.py`](../../../magiclang/libraries/mana.py) | 60 | `f"{label} must be a direction vector"` |
| `TypeErrorML` | [`magiclang/libraries/mana.py`](../../../magiclang/libraries/mana.py) | 246 | `'destination is required outside tgset(target):'` |
| `TypeErrorML` | [`magiclang/libraries/mana.py`](../../../magiclang/libraries/mana.py) | 292 | `'mana.form() shape must be non-empty text'` |
| `TypeErrorML` | [`magiclang/libraries/mana.py`](../../../magiclang/libraries/mana.py) | 301 | `'mana.form() collidable must be true or false'` |
| `TypeErrorML` | [`magiclang/libraries/mana.py`](../../../magiclang/libraries/mana.py) | 303 | `'mana.form() anchored must be true or false'` |
| `TypeErrorML` | [`magiclang/libraries/mana.py`](../../../magiclang/libraries/mana.py) | 455 | `'mana.control() action must be text'` |
| `TypeErrorML` | [`magiclang/libraries/materials.py`](../../../magiclang/libraries/materials.py) | 64 | `'materials.profile() expects a non-empty material name or element symbol'` |
| `TypeErrorML` | [`magiclang/libraries/materials.py`](../../../magiclang/libraries/materials.py) | 79 | `'materials.search() expects a non-empty text query'` |
| `TypeErrorML` | [`magiclang/libraries/materials.py`](../../../magiclang/libraries/materials.py) | 107 | `'materials.by_category() expects a non-empty category'` |
| `TypeErrorML` | [`magiclang/libraries/materials.py`](../../../magiclang/libraries/materials.py) | 185 | `'materials.recommend() expects a non-empty purpose'` |
| `TypeErrorML` | [`magiclang/libraries/materials.py`](../../../magiclang/libraries/materials.py) | 190 | `'materials.recommend() purpose must contain searchable words'` |
| `TypeErrorML` | [`magiclang/libraries/materials.py`](../../../magiclang/libraries/materials.py) | 226 | `'materials.define() name must be non-empty text'` |
| `TypeErrorML` | [`magiclang/libraries/materials.py`](../../../magiclang/libraries/materials.py) | 245 | `'materials.define() category must be non-empty text no longer than 80 characters'` |
| `TypeErrorML` | [`magiclang/libraries/materials.py`](../../../magiclang/libraries/materials.py) | 259 | `f"materials.define() {field_name} must be a number"` |
| `TypeErrorML` | [`magiclang/libraries/materials.py`](../../../magiclang/libraries/materials.py) | 275 | `f"materials.define() {field_name} must be a number"` |
| `TypeErrorML` | [`magiclang/libraries/materials.py`](../../../magiclang/libraries/materials.py) | 294 | `f"materials.define() {label} must be a list of up to 32 text labels"` |
| `TypeErrorML` | [`magiclang/libraries/materials.py`](../../../magiclang/libraries/materials.py) | 298 | `f"materials.define() {label} entries must be non-empty text up to 80 characters"` |
| `TypeErrorML` | [`magiclang/libraries/materials.py`](../../../magiclang/libraries/materials.py) | 306 | `'materials.define() combustible and brittle must be true or false'` |
| `TypeErrorML` | [`magiclang/libraries/materials.py`](../../../magiclang/libraries/materials.py) | 311 | `"materials.define() composition must be text such as 'Fe:0.96,C:0.04'"` |
| `TypeErrorML` | [`magiclang/libraries/materials.py`](../../../magiclang/libraries/materials.py) | 326 | `'composition mass fractions must be numeric'` |
| `TypeErrorML` | [`magiclang/libraries/metals.py`](../../../magiclang/libraries/metals.py) | 50 | `'metals.control() target must be a MANA world object'` |
| `TypeErrorML` | [`magiclang/libraries/metals.py`](../../../magiclang/libraries/metals.py) | 56 | `'metals.control() direction must be a planar direction vector'` |
| `TypeErrorML` | [`magiclang/libraries/metals.py`](../../../magiclang/libraries/metals.py) | 76 | `"metals.field() polarity must be 'attract' or 'repel'"` |
| `TypeErrorML` | [`magiclang/libraries/necromancy.py`](../../../magiclang/libraries/necromancy.py) | 39 | `f"necromancy.{operation}() expects an existing MANA object"` |
| `TypeErrorML` | [`magiclang/libraries/necromancy.py`](../../../magiclang/libraries/necromancy.py) | 105 | `'necromancy.reanimate() name must be non-empty text when supplied'` |
| `TypeErrorML` | [`magiclang/libraries/necromancy.py`](../../../magiclang/libraries/necromancy.py) | 124 | `'necromancy.reanimate_many() expects a non-empty list of corpse objects'` |
| `TypeErrorML` | [`magiclang/libraries/necromancy.py`](../../../magiclang/libraries/necromancy.py) | 133 | `'reanimate_many() list entries must be MANA objects'` |
| `TypeErrorML` | [`magiclang/libraries/necromancy.py`](../../../magiclang/libraries/necromancy.py) | 138 | `'necromancy.reanimate_many() name must be non-empty text when supplied'` |
| `TypeErrorML` | [`magiclang/libraries/necromancy.py`](../../../magiclang/libraries/necromancy.py) | 169 | `'necromancy.lichify() target must be an active MANA entity'` |
| `TypeErrorML` | [`magiclang/libraries/necromancy.py`](../../../magiclang/libraries/necromancy.py) | 180 | `'necromancy.lichify() phylactery must be an active MANA object'` |
| `TypeErrorML` | [`magiclang/libraries/necromancy.py`](../../../magiclang/libraries/necromancy.py) | 193 | `'necromancy.lichify() name must be non-empty text no longer than 80 characters'` |
| `TypeErrorML` | [`magiclang/libraries/necromancy.py`](../../../magiclang/libraries/necromancy.py) | 236 | `'necromancy.is_lich() expects a MANA object'` |
| `TypeErrorML` | [`magiclang/libraries/necromancy.py`](../../../magiclang/libraries/necromancy.py) | 244 | `'necromancy.reconstitute() expects a MANA lich object'` |
| `TypeErrorML` | [`magiclang/libraries/necromancy.py`](../../../magiclang/libraries/necromancy.py) | 291 | `'necromancy.is_undead() expects a MANA object'` |
| `TypeErrorML` | [`magiclang/libraries/periodic.py`](../../../magiclang/libraries/periodic.py) | 13 | `'periodic lookup expects an element name or symbol as text'` |
| `TypeErrorML` | [`magiclang/libraries/periodic.py`](../../../magiclang/libraries/periodic.py) | 27 | `'periodic.by_number() expects an integer atomic number'` |
| `TypeErrorML` | [`magiclang/libraries/periodic.py`](../../../magiclang/libraries/periodic.py) | 37 | `'periodic.search() expects text'` |
| `TypeErrorML` | [`magiclang/libraries/periodic.py`](../../../magiclang/libraries/periodic.py) | 40 | `'periodic.search() requires a non-empty query'` |
| `TypeErrorML` | [`magiclang/libraries/physiology.py`](../../../magiclang/libraries/physiology.py) | 111 | `f"physiology.{operation}() expects a MANA world object"` |
| `TypeErrorML` | [`magiclang/libraries/physiology.py`](../../../magiclang/libraries/physiology.py) | 133 | `f"physiology.{label} must be a finite number"` |
| `TypeErrorML` | [`magiclang/libraries/physiology.py`](../../../magiclang/libraries/physiology.py) | 628 | `'physiology.define_form() name must be non-empty text'` |
| `TypeErrorML` | [`magiclang/libraries/physiology.py`](../../../magiclang/libraries/physiology.py) | 637 | `'physiology.define_form() organs must be a list of 3–1024 known organ names'` |
| `TypeErrorML` | [`magiclang/libraries/physiology.py`](../../../magiclang/libraries/physiology.py) | 647 | `'physiology.define_form() vital_structures must be a list of 1–16 structure names'` |
| `TypeErrorML` | [`magiclang/libraries/physiology.py`](../../../magiclang/libraries/physiology.py) | 667 | `'physiology.define_form() label must be non-empty text up to 64 characters'` |
| `TypeErrorML` | [`magiclang/libraries/physiology.py`](../../../magiclang/libraries/physiology.py) | 673 | `'physiology.define_form() trait_factors must be a dictionary when called from Python'` |
| `TypeErrorML` | [`magiclang/libraries/physiology.py`](../../../magiclang/libraries/physiology.py) | 777 | `'physiology.enhance() duration must use seconds'` |
| `TypeErrorML` | [`magiclang/libraries/physiology.py`](../../../magiclang/libraries/physiology.py) | 817 | `'physiology.propel() direction must be a dimensionless vector, e.g. vector3d.direction(0, 1, 0)'` |
| `TypeErrorML` | [`magiclang/libraries/physiology.py`](../../../magiclang/libraries/physiology.py) | 821 | `'physiology.propel() speed must use velocity units such as 15 m/s'` |
| `TypeErrorML` | [`magiclang/libraries/physiology.py`](../../../magiclang/libraries/physiology.py) | 933 | `'physiology.manipulate_blood() duration must use seconds'` |
| `TypeErrorML` | [`magiclang/libraries/physiology.py`](../../../magiclang/libraries/physiology.py) | 990 | `'physiology.injure_system() system must be text'` |
| `TypeErrorML` | [`magiclang/libraries/physiology.py`](../../../magiclang/libraries/physiology.py) | 1016 | `'physiology.heal_system() system must be text'` |
| `TypeErrorML` | [`magiclang/libraries/physiology.py`](../../../magiclang/libraries/physiology.py) | 1038 | `'physiology.set_temperature() temperature must use kelvin (K)'` |
| `TypeErrorML` | [`magiclang/libraries/physiology.py`](../../../magiclang/libraries/physiology.py) | 1063 | `'physiology.kill() cause must be non-empty text no longer than 80 characters'` |
| `TypeErrorML` | [`magiclang/libraries/physiology.py`](../../../magiclang/libraries/physiology.py) | 1146 | `f"physiology.{operation}() organ must be text"` |
| `TypeErrorML` | [`magiclang/libraries/planar_registry.py`](../../../magiclang/libraries/planar_registry.py) | 146 | `'plane identifier must be a name, ID, or plane/region reference'` |
| `TypeErrorML` | [`magiclang/libraries/planar_registry.py`](../../../magiclang/libraries/planar_registry.py) | 166 | `'region name must be non-empty text'` |
| `TypeErrorML` | [`magiclang/libraries/planar_registry.py`](../../../magiclang/libraries/planar_registry.py) | 195 | `'region parent must be a registered plane'` |
| `TypeErrorML` | [`magiclang/libraries/planar_registry.py`](../../../magiclang/libraries/planar_registry.py) | 199 | `'region ID must start with a lowercase letter and contain lowercase letters, digits, or underscores'` |
| `TypeErrorML` | [`magiclang/libraries/planar_registry.py`](../../../magiclang/libraries/planar_registry.py) | 201 | `'region name must be non-empty text'` |
| `TypeErrorML` | [`magiclang/libraries/planar_registry.py`](../../../magiclang/libraries/planar_registry.py) | 240 | `'plane ID must start with a lowercase letter and contain lowercase letters, digits, or underscores'` |
| `TypeErrorML` | [`magiclang/libraries/planar_registry.py`](../../../magiclang/libraries/planar_registry.py) | 242 | `'plane name must be non-empty text'` |
| `TypeErrorML` | [`magiclang/libraries/planar_registry.py`](../../../magiclang/libraries/planar_registry.py) | 244 | `'plane category must be non-empty text'` |
| `TypeErrorML` | [`magiclang/libraries/planar_registry.py`](../../../magiclang/libraries/planar_registry.py) | 247 | `'plane category must start with a letter and contain only letters, digits, or spaces'` |
| `TypeErrorML` | [`magiclang/libraries/planar_registry.py`](../../../magiclang/libraries/planar_registry.py) | 251 | `'plane data_library must be a library name or null'` |
| `TypeErrorML` | [`magiclang/libraries/planar_registry.py`](../../../magiclang/libraries/planar_registry.py) | 255 | `'plane aliases must be a list of names'` |
| `TypeErrorML` | [`magiclang/libraries/planar_registry.py`](../../../magiclang/libraries/planar_registry.py) | 260 | `'plane aliases must be non-empty text'` |
| `TypeErrorML` | [`magiclang/libraries/plane_data/elemental_planes.py`](../../../magiclang/libraries/plane_data/elemental_planes.py) | 158 | `'elemental_planes.find_being() expects a name'` |
| `TypeErrorML` | [`magiclang/libraries/planes.py`](../../../magiclang/libraries/planes.py) | 148 | `'planes.exists() expects a plane or region name'` |
| `TypeErrorML` | [`magiclang/libraries/planes.py`](../../../magiclang/libraries/planes.py) | 167 | `'planes.plane_of() expects a being record or world object, not a plane name or plane reference'` |
| `TypeErrorML` | [`magiclang/libraries/planes.py`](../../../magiclang/libraries/planes.py) | 202 | `'planes.planes_in() category must be non-empty text'` |
| `TypeErrorML` | [`magiclang/libraries/planes.py`](../../../magiclang/libraries/planes.py) | 211 | `'planes.open_path() one_way must be true or false'` |
| `TypeErrorML` | [`magiclang/libraries/planes.py`](../../../magiclang/libraries/planes.py) | 336 | `'planes.send_energy() kind must be non-empty text when supplied'` |
| `TypeErrorML` | [`magiclang/libraries/planes.py`](../../../magiclang/libraries/planes.py) | 348 | `f"planes.send_energy() kind must be a known elemental energy label ({allowed}) or a registered internal transfer label"` |
| `TypeErrorML` | [`magiclang/libraries/summoning.py`](../../../magiclang/libraries/summoning.py) | 109 | `'summoning.bring() expects a being name or a BeingRecord'` |
| `TypeErrorML` | [`magiclang/libraries/summoning.py`](../../../magiclang/libraries/summoning.py) | 178 | `'summoning requirements must be a list of non-empty text values'` |
| `TypeErrorML` | [`magiclang/libraries/summoning.py`](../../../magiclang/libraries/summoning.py) | 202 | `f"summoning.{operation}() expects a being created by summoning.bring()"` |
| `TypeErrorML` | [`magiclang/libraries/summoning.py`](../../../magiclang/libraries/summoning.py) | 284 | `'summoning.tame() name must be non-empty text when supplied'` |
| `TypeErrorML` | [`magiclang/libraries/three_d.py`](../../../magiclang/libraries/three_d.py) | 26 | `f"{label} must be a finite number or a {dimension} quantity"` |
| `TypeErrorML` | [`magiclang/libraries/three_d.py`](../../../magiclang/libraries/three_d.py) | 32 | `f"{label} must be a finite number or a {dimension} quantity"` |
| `TypeErrorML` | [`magiclang/libraries/three_d.py`](../../../magiclang/libraries/three_d.py) | 62 | `'vector3d.magnitude() expects a vector'` |
| `TypeErrorML` | [`magiclang/libraries/three_d.py`](../../../magiclang/libraries/three_d.py) | 74 | `'vector3d.normalize() expects a vector'` |
| `TypeErrorML` | [`magiclang/libraries/three_d.py`](../../../magiclang/libraries/three_d.py) | 90 | `'vector3d.rotate() expects a vector'` |
| `TypeErrorML` | [`magiclang/libraries/three_d.py`](../../../magiclang/libraries/three_d.py) | 106 | `'vector3d.lerp() expects two vectors'` |
| `TypeErrorML` | [`magiclang/libraries/three_d.py`](../../../magiclang/libraries/three_d.py) | 122 | `'vector3d.dot() expects two vectors'` |
| `TypeErrorML` | [`magiclang/libraries/three_d.py`](../../../magiclang/libraries/three_d.py) | 130 | `'vector3d.cross() expects two vectors'` |
| `TypeErrorML` | [`magiclang/libraries/three_d.py`](../../../magiclang/libraries/three_d.py) | 139 | `'vector3d.distance() expects two vectors'` |
| `TypeErrorML` | [`magiclang/libraries/three_d.py`](../../../magiclang/libraries/three_d.py) | 147 | `'vector3d.angle_between() expects two vectors'` |
| `TypeErrorML` | [`magiclang/libraries/three_d.py`](../../../magiclang/libraries/three_d.py) | 166 | `'vector3d.project() expects two vectors'` |
| `TypeErrorML` | [`magiclang/libraries/three_d.py`](../../../magiclang/libraries/three_d.py) | 185 | `'vector3d.reflect() expects vectors'` |
| `TypeErrorML` | [`magiclang/libraries/three_d.py`](../../../magiclang/libraries/three_d.py) | 199 | `'vector3d.scale() expects a vector'` |
| `TypeErrorML` | [`magiclang/libraries/three_d.py`](../../../magiclang/libraries/three_d.py) | 206 | `'vector3d.components() expects a vector'` |
| `TypeErrorML` | [`magiclang/libraries/three_d.py`](../../../magiclang/libraries/three_d.py) | 212 | `'vector3d.is_zero() expects a vector'` |
| `TypeErrorML` | [`magiclang/libraries/three_d.py`](../../../magiclang/libraries/three_d.py) | 227 | `'vector3d.planar() expects a vector'` |
| `TypeErrorML` | [`magiclang/libraries/three_d.py`](../../../magiclang/libraries/three_d.py) | 234 | `'vector3d.is_planar() expects a vector'` |
| `TypeErrorML` | [`magiclang/libraries/three_d.py`](../../../magiclang/libraries/three_d.py) | 251 | `'vector3d.object_vector() expects a vector or MANA object'` |
| `TypeErrorML` | [`magiclang/libraries/three_d.py`](../../../magiclang/libraries/three_d.py) | 254 | `'vector3d.object_vector() field must be pos, vel, acc, force, momentum, direction, or anchor_pos'` |
| `TypeErrorML` | [`magiclang/libraries/three_d.py`](../../../magiclang/libraries/three_d.py) | 272 | `'vector3d.pressure() force must be a force quantity or force vector'` |
| `TypeErrorML` | [`magiclang/libraries/weather.py`](../../../magiclang/libraries/weather.py) | 47 | `f"{label} must be a finite number"` |
| `TypeErrorML` | [`magiclang/libraries/weather.py`](../../../magiclang/libraries/weather.py) | 62 | `f"{label} must be a number with compatible units"` |
| `TypeErrorML` | [`magiclang/libraries/weather.py`](../../../magiclang/libraries/weather.py) | 82 | `'wind_direction must be a compass direction or planar direction vector'` |
| `TypeErrorML` | [`magiclang/libraries/world.py`](../../../magiclang/libraries/world.py) | 34 | `f"{label} must be a finite number"` |
| `TypeErrorML` | [`magiclang/libraries/world.py`](../../../magiclang/libraries/world.py) | 123 | `f"world.configure() {key} must be true or false"` |
| `TypeErrorML` | [`magiclang/physics.py`](../../../magiclang/physics.py) | 28 | `'vector components must be finite numeric values'` |
| `TypeErrorML` | [`magiclang/physics.py`](../../../magiclang/physics.py) | 34 | `'vector components must be finite numeric values'` |
| `TypeErrorML` | [`magiclang/physics.py`](../../../magiclang/physics.py) | 53 | `'vector operation requires another vector'` |
| `TypeErrorML` | [`magiclang/physics.py`](../../../magiclang/physics.py) | 67 | `'boolean values cannot scale a vector'` |
| `TypeErrorML` | [`magiclang/physics.py`](../../../magiclang/physics.py) | 86 | `'boolean values cannot scale a vector'` |
| `TypeErrorML` | [`magiclang/physics.py`](../../../magiclang/physics.py) | 106 | `'vector dot product requires another vector'` |
| `TypeErrorML` | [`magiclang/physics.py`](../../../magiclang/physics.py) | 139 | `f"{label} requires a vector"` |
| `TypeErrorML` | [`magiclang/physics.py`](../../../magiclang/physics.py) | 152 | `'boolean values are not numeric physical quantities'` |
| `TypeErrorML` | [`magiclang/physics.py`](../../../magiclang/physics.py) | 168 | `f"expected numeric value, got {type(value).__name__}"` |
| `TypeErrorML` | [`magiclang/physics.py`](../../../magiclang/physics.py) | 173 | `f"{label} requires a vector"` |
| `TypeErrorML` | [`magiclang/physics.py`](../../../magiclang/physics.py) | 229 | `'displacement direction must be a vector'` |
| `TypeErrorML` | [`magiclang/physics_engine.py`](../../../magiclang/physics_engine.py) | 107 | `'restitution must be a finite number between 0 and 1'` |
| `TypeErrorML` | [`magiclang/physics_engine.py`](../../../magiclang/physics_engine.py) | 113 | `'restitution must be a finite number between 0 and 1'` |
| `TypeErrorML` | [`magiclang/physics_engine.py`](../../../magiclang/physics_engine.py) | 127 | `'friction must be a finite number between 0 and 2'` |
| `TypeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 356 | `f"{self.element} object has no property '{name}'"` |
| `TypeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 365 | `f"{self.element} object has no property '{name}'"` |
| `TypeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1400 | `f"{stmt.mode}({stmt.spell.name}) expects a named spell or configured spell instance, not {type(spell).__name__}"` |
| `TypeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1411 | `"tune requires a configured spell instance; create one first, for example 'fire_ball = e_ball(Fire)'"` |
| `TypeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1417 | `f"cannot tune '{spell.name}.{stmt.operation}' for '{stmt.target_name}': that operation and target do not exist in the spell"` |
| `TypeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1422 | `f"cannot tune '{spell.name}.{stmt.operation}' for '{stmt.target_name}': multiple matching operations exist; make the target/operation unambiguous"` |
| `TypeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1454 | `"spell definitions accept no parameters or one base-element selector: use 'spell name(element):'"` |
| `TypeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1470 | `<message supplied by expression: 'unknown weave setting(s): ' + ', '.join(unknown) + '; supported settings are ' + ', '.join(sorted(allowed))>` |
| `TypeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1620 | `'for loop expects a list or span'` |
| `TypeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1728 | `'indexed assignment requires a list; only list items are assignable'` |
| `TypeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1730 | `'list index must be an integer'` |
| `TypeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1735 | `'assignment target must be a variable or object property'` |
| `TypeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1804 | `'indexing is supported for lists, strings, and spans'` |
| `TypeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1806 | `'index must be an integer'` |
| `TypeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1862 | `f"unary '{expr.op}' is not supported for {type(value).__name__}"` |
| `TypeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1902 | `f"spell template '{callee.name}' expects exactly one element: {callee.name}(Fire)"` |
| `TypeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1910 | `f"spell '{callee.name}' takes no arguments"` |
| `TypeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1914 | `f"function '{callee.name}' takes at most {len(callee.params)} arguments"` |
| `TypeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1920 | `f"function '{callee.name}' has no parameter '{name}'"` |
| `TypeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1922 | `f"function '{callee.name}' got multiple values for '{name}'"` |
| `TypeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1930 | `f"function '{callee.name}' is missing required argument '{name}'"` |
| `TypeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1956 | `f"spell '{callee.name}' cannot be called as a value; use post({callee.name}) or release({callee.name})"` |
| `TypeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1969 | `f"configured spell '{callee.name}' is not called directly; use post({callee.name}) or release({callee.name})"` |
| `TypeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1997 | `<message supplied by expression: str(exc)>` |
| `TypeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1998 | `f"value {callee} is not callable"` |
| `TypeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 2122 | `<message supplied by expression: str(exc)>` |
| `TypeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 2132 | `f"library '{obj.name}' does not export '{name}'"` |
| `TypeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 2159 | `f"object has no MANA property '{name}'"` |
| `TypeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 2164 | `'properties can only be assigned on magical objects'` |
| `TypeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 2185 | `'properties can only be assigned on magical objects'` |
| `TypeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 2210 | `'display_name must be non-empty text'` |
| `TypeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 2212 | `'object_kind must be non-empty text'` |
| `TypeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 2214 | `'material must be non-empty text'` |
| `TypeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 2217 | `'stabilizers must be a list of registered element names'` |
| `TypeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 2224 | `'stabilizers may contain only Earth, Water, Air, Order, Light, Space, Time, Entropy, or Death'` |
| `TypeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 2231 | `f"{obj.element} object has no property '{name}'"` |
| `TypeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 2239 | `'restitution must be a finite number between 0 and 1'` |
| `TypeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 2245 | `'restitution must be a finite number between 0 and 1'` |
| `TypeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 2254 | `'friction must be between 0 and 2'` |
| `TypeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 2257 | `'collidable must be true or false'` |
| `TypeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 2319 | `f"target field '{name}' must be a non-negative number"` |
| `TypeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 2332 | `f"{name} must be between 0 and 1 (0 = none, 1 = full resistance)"` |
| `TypeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 2346 | `'target material must be non-empty text'` |
| `TypeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 2350 | `'target kind must be non-empty text'` |
| `TypeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 2354 | `'target shape must be non-empty text'` |
| `TypeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 2362 | `'target combustible must be true or false'` |
| `TypeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 2365 | `'target anchored must be true or false'` |
| `TypeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 2368 | `'target powderable must be true or false'` |
| `TypeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 2393 | `'target restitution must be between 0 and 1'` |
| `TypeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 2401 | `'target friction must be between 0 and 2'` |
| `TypeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 2405 | `'target collidable must be true or false'` |
| `TypeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 2414 | `'shape() expects a built-in geometry name'` |
| `TypeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 2434 | `'move() direction must be a vector'` |
| `TypeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 2550 | `'impulse() expects a momentum vector, for example vector3d.direction(1, 0, 0) * (10 kg*m/s)'` |
| `TypeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 2646 | `'detect() currently expects a magical object'` |
| `TypeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 2649 | `'detect() property name must be text'` |
| `TypeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 2651 | `f"detect() target has no property '{property_name}'"` |
| `TypeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 2670 | `"appraise presentation must be 'text' or 'visual'"` |
| `TypeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 2682 | `"post presentation must be 'text' or 'visual'"` |
| `TypeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 2691 | `f"'{candidate.name}' is an ordinary function, not a spell; call it normally to calculate a value"` |
| `TypeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 2693 | `f"'{candidate.name}' is a spell template; configure it first, e.g. '{candidate.name}(Fire)'"` |
| `TypeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 2704 | `f"'{candidate}' is an ordinary function, not a spell; call it normally to calculate a value"` |
| `TypeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 2706 | `f"'{candidate}' is a spell template; configure it first, e.g. '{candidate}(Fire)'"` |
| `TypeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 2708 | `f"{mode}() expected a named spell or configured spell instance, got {candidate}"` |
| `TypeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 2710 | `f"{mode}() accepts a spell name only, not a magical object; use object operations for objects"` |
| `TypeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 2711 | `f"{mode}() expects one spell name"` |
| `TypeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 3449 | `f"conjure() got unsupported option(s): {unknown}"` |
| `TypeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 3454 | `'conjure() source must be a material name or equipment blueprint'` |
| `TypeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 3468 | `'conjure() material must be non-empty text'` |
| `TypeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 3470 | `'conjure() item must be non-empty text'` |
| `TypeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 3539 | `'conjure() anchored and collidable options must be true or false'` |
| `TypeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 3550 | `f"conjure() {label} must be a finite number"` |
| `TypeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 3596 | `'conjure() payload must be text'` |
| `TypeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 3685 | `'transmute() material must be a non-empty text name'` |
| `TypeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 3687 | `'transmute() preserve_mass must be true or false'` |
| `TypeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 3815 | `'transfigure() form must be non-empty text'` |
| `TypeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 3898 | `'transfigure() scale must be a finite dimensionless number'` |
| `TypeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 3927 | `'transform() state must be text'` |
| `TypeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 3963 | `'show() separator must be text'` |
| `TypeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 4129 | `'direction() components must be numbers'` |
| `TypeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 4150 | `'aim() direction must be a vector created by direction()'` |
| `TypeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 4178 | `f"{operation}() direction must be a vector"` |
| `TypeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 4222 | `'pull() needs position vectors on both objects'` |
| `TypeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 4234 | `'rotate() angle must be a finite number of radians'` |
| `TypeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 4240 | `'rotate() angle must be a finite number of radians'` |
| `TypeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 4293 | `'reflect() needs a non-zero direction vector as surface normal'` |
| `TypeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 4315 | `'split() parts must be an integer between 2 and 10000'` |
| `TypeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 4431 | `'sqrt() expects a non-negative number'` |
| `TypeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 4437 | `'sqrt() expects a non-negative number'` |
| `TypeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 4448 | `'magnitude() expects a vector or numeric quantity'` |
| `TypeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 4454 | `'has_domain() domain must be text'` |
| `TypeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 4861 | `f"{operation}() expects a magical object"` |
| `TypeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 4878 | `f"{operation}() requires target property '{prop}'"` |
| `TypeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 4889 | `f"{label} requires a numeric value"` |
| `TypeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 4912 | `'timing requires a numeric duration'` |
| `TypeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 5512 | `'emit() event name must be text'` |
| `TypeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 5534 | `'span() expects 1 to 3 integer arguments'` |
| `TypeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 5536 | `'span() arguments must be integers'` |
| `TypeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 5558 | `'length() expects a list, string, or span'` |
| `TypeErrorML` | [`magiclang/units.py`](../../../magiclang/units.py) | 161 | `'quantity value must be numeric, not boolean or text'` |
| `TypeErrorML` | [`magiclang/units.py`](../../../magiclang/units.py) | 181 | `f"cannot combine a quantity in {self.dimension} with {other_kind}; expected another quantity in {self.dimension}"` |
| `TypeErrorML` | [`magiclang/units.py`](../../../magiclang/units.py) | 213 | `'boolean values cannot be used as quantities'` |
| `TypeErrorML` | [`magiclang/units.py`](../../../magiclang/units.py) | 227 | `'boolean values cannot be used as quantities'` |
| `TypeErrorML` | [`magiclang/units.py`](../../../magiclang/units.py) | 242 | `'boolean values cannot be used as quantities'` |
| `TypeErrorML` | [`magiclang/units.py`](../../../magiclang/units.py) | 255 | `'quantity exponent must be an integer'` |
| `UnitErrorML` | [`magiclang/libraries/armory.py`](../../../magiclang/libraries/armory.py) | 113 | `f"armory.define() {label} must use metres"` |
| `UnitErrorML` | [`magiclang/libraries/armory.py`](../../../magiclang/libraries/armory.py) | 147 | `'armory.define() launch_speed must use m/s'` |
| `UnitErrorML` | [`magiclang/libraries/armory.py`](../../../magiclang/libraries/armory.py) | 267 | `'armory.launch() speed must use m/s'` |
| `UnitErrorML` | [`magiclang/libraries/geometry2d.py`](../../../magiclang/libraries/geometry2d.py) | 21 | `f"{label} must be a plain number, not {value.dimension}"` |
| `UnitErrorML` | [`magiclang/libraries/geometry2d.py`](../../../magiclang/libraries/geometry2d.py) | 37 | `f"{label} must be measured in metres"` |
| `UnitErrorML` | [`magiclang/libraries/geometry2d.py`](../../../magiclang/libraries/geometry2d.py) | 57 | `f"{label} must use metre coordinates"` |
| `UnitErrorML` | [`magiclang/libraries/geometry2d.py`](../../../magiclang/libraries/geometry2d.py) | 120 | `'angle_between() requires vectors with matching dimensions'` |
| `UnitErrorML` | [`magiclang/libraries/geometry2d.py`](../../../magiclang/libraries/geometry2d.py) | 192 | `'lerp() requires vectors with matching dimensions'` |
| `UnitErrorML` | [`magiclang/libraries/mana.py`](../../../magiclang/libraries/mana.py) | 54 | `'mana effect position must be a position vector in metres or a positioned object'` |
| `UnitErrorML` | [`magiclang/libraries/mana.py`](../../../magiclang/libraries/mana.py) | 62 | `f"{label} must be dimensionless or a displacement vector"` |
| `UnitErrorML` | [`magiclang/libraries/mana.py`](../../../magiclang/libraries/mana.py) | 143 | `'mana energy transfer needs a target temperature in K'` |
| `UnitErrorML` | [`magiclang/libraries/mana.py`](../../../magiclang/libraries/mana.py) | 165 | `'mana burst recipients need position and velocity vectors'` |
| `UnitErrorML` | [`magiclang/libraries/mana.py`](../../../magiclang/libraries/mana.py) | 242 | `'the selected tgset target needs a position for automatic control'` |
| `UnitErrorML` | [`magiclang/libraries/mana.py`](../../../magiclang/libraries/mana.py) | 259 | `'mana.stop() needs a valid velocity vector'` |
| `UnitErrorML` | [`magiclang/libraries/mana.py`](../../../magiclang/libraries/mana.py) | 261 | `'mana.stop() needs an object temperature in K'` |
| `UnitErrorML` | [`magiclang/libraries/mana.py`](../../../magiclang/libraries/mana.py) | 474 | `'mana.control() target needs a position in metres'` |
| `UnitErrorML` | [`magiclang/libraries/mana.py`](../../../magiclang/libraries/mana.py) | 535 | `'mana.collect() items need positions in metres'` |
| `UnitErrorML` | [`magiclang/libraries/mana.py`](../../../magiclang/libraries/mana.py) | 564 | `f"{label} must be a position vector in metres or a positioned object"` |
| `UnitErrorML` | [`magiclang/libraries/materials.py`](../../../magiclang/libraries/materials.py) | 238 | `'materials.define() density must use density units, e.g. 7800 kg/m^3'` |
| `UnitErrorML` | [`magiclang/libraries/metals.py`](../../../magiclang/libraries/metals.py) | 22 | `f"metals.{label}() center must be a positioned object or Vector3 in metres"` |
| `UnitErrorML` | [`magiclang/libraries/metals.py`](../../../magiclang/libraries/metals.py) | 27 | `f"metals.{label}() requires a quantity in {dimension}"` |
| `UnitErrorML` | [`magiclang/libraries/planes.py`](../../../magiclang/libraries/planes.py) | 329 | `'planes.send_energy() amount must be an energy quantity in joules'` |
| `UnitErrorML` | [`magiclang/libraries/planes.py`](../../../magiclang/libraries/planes.py) | 331 | `f"planes.send_energy() requires joules, not {amount.dimension}"` |
| `UnitErrorML` | [`magiclang/libraries/planes.py`](../../../magiclang/libraries/planes.py) | 385 | `f"planes.open_channel() rate must be measured in watts, not {actual}"` |
| `UnitErrorML` | [`magiclang/libraries/summoning.py`](../../../magiclang/libraries/summoning.py) | 196 | `'summoning position must be a position vector measured in metres or a positioned object'` |
| `UnitErrorML` | [`magiclang/libraries/three_d.py`](../../../magiclang/libraries/three_d.py) | 23 | `f"{label} must use {dimension}, not {value.dimension}"` |
| `UnitErrorML` | [`magiclang/libraries/three_d.py`](../../../magiclang/libraries/three_d.py) | 108 | `'vector3d.lerp() requires matching vector dimensions'` |
| `UnitErrorML` | [`magiclang/libraries/three_d.py`](../../../magiclang/libraries/three_d.py) | 141 | `'vector3d.distance() requires matching coordinate units'` |
| `UnitErrorML` | [`magiclang/libraries/three_d.py`](../../../magiclang/libraries/three_d.py) | 149 | `'angle_between() requires matching vector dimensions'` |
| `UnitErrorML` | [`magiclang/libraries/three_d.py`](../../../magiclang/libraries/three_d.py) | 257 | `f"object has no vector-valued '{field}' property"` |
| `UnitErrorML` | [`magiclang/libraries/three_d.py`](../../../magiclang/libraries/three_d.py) | 265 | `f"vector3d.pressure() force vector must use N, not {force_value.dimension}"` |
| `UnitErrorML` | [`magiclang/libraries/three_d.py`](../../../magiclang/libraries/three_d.py) | 269 | `f"vector3d.pressure() force must use N, not {force_value.dimension}"` |
| `UnitErrorML` | [`magiclang/libraries/three_d.py`](../../../magiclang/libraries/three_d.py) | 274 | `'vector3d.pressure() force must include N units'` |
| `UnitErrorML` | [`magiclang/libraries/three_d.py`](../../../magiclang/libraries/three_d.py) | 277 | `f"vector3d.pressure() area must use m2, not {actual}"` |
| `UnitErrorML` | [`magiclang/libraries/weather.py`](../../../magiclang/libraries/weather.py) | 44 | `f"{label} must be dimensionless"` |
| `UnitErrorML` | [`magiclang/libraries/weather.py`](../../../magiclang/libraries/weather.py) | 57 | `f"{label} must use {dimension}, not {value.dimension}"` |
| `UnitErrorML` | [`magiclang/libraries/weather.py`](../../../magiclang/libraries/weather.py) | 77 | `'wind_direction vector must be a planar, dimensionless direction'` |
| `UnitErrorML` | [`magiclang/libraries/weather.py`](../../../magiclang/libraries/weather.py) | 111 | `'weather area center must be a 2D position in metres or a positioned object'` |
| `UnitErrorML` | [`magiclang/libraries/weather.py`](../../../magiclang/libraries/weather.py) | 219 | `'weather area center must be a 2D position in metres or a positioned object'` |
| `UnitErrorML` | [`magiclang/libraries/world.py`](../../../magiclang/libraries/world.py) | 31 | `f"{label} must be dimensionless"` |
| `UnitErrorML` | [`magiclang/libraries/world.py`](../../../magiclang/libraries/world.py) | 96 | `'world.configure() gravity must be an acceleration vector in m/s²'` |
| `UnitErrorML` | [`magiclang/libraries/world.py`](../../../magiclang/libraries/world.py) | 102 | `'world.configure() air_density must use kg/m³'` |
| `UnitErrorML` | [`magiclang/parser.py`](../../../magiclang/parser.py) | 986 | `f"unknown unit '{candidate}'"` |
| `UnitErrorML` | [`magiclang/parser.py`](../../../magiclang/parser.py) | 999 | `'numeric literal is outside the supported range for unit conversion'` |
| `UnitErrorML` | [`magiclang/parser.py`](../../../magiclang/parser.py) | 1004 | `'numeric literal is outside the supported finite range for unit conversion'` |
| `UnitErrorML` | [`magiclang/physics.py`](../../../magiclang/physics.py) | 55 | `f"vector dimensions differ: {self.dimension} and {other.dimension}"` |
| `UnitErrorML` | [`magiclang/physics.py`](../../../magiclang/physics.py) | 158 | `f"expected {expected}, got {value.dimension}"` |
| `UnitErrorML` | [`magiclang/physics.py`](../../../magiclang/physics.py) | 175 | `f"{label} expects {dimension}, got {value.dimension}"` |
| `UnitErrorML` | [`magiclang/physics.py`](../../../magiclang/physics.py) | 256 | `'clamp_speed() expects a velocity vector'` |
| `UnitErrorML` | [`magiclang/physics_engine.py`](../../../magiclang/physics_engine.py) | 48 | `'2D world physics requires every active object to have a position vector in metres'` |
| `UnitErrorML` | [`magiclang/physics_engine.py`](../../../magiclang/physics_engine.py) | 55 | `'2D world physics requires every active object to have a velocity vector in m/s'` |
| `UnitErrorML` | [`magiclang/physics_engine.py`](../../../magiclang/physics_engine.py) | 62 | `'2D world physics requires every active object to have an acceleration vector in m/s2'` |
| `UnitErrorML` | [`magiclang/physics_engine.py`](../../../magiclang/physics_engine.py) | 74 | `'physics simulation requires mass measured in kg'` |
| `UnitErrorML` | [`magiclang/physics_engine.py`](../../../magiclang/physics_engine.py) | 84 | `'collision_radius must be measured in metres'` |
| `UnitErrorML` | [`magiclang/physics_engine.py`](../../../magiclang/physics_engine.py) | 91 | `'2D collision bounds require area measured in m2'` |
| `UnitErrorML` | [`magiclang/physics_engine.py`](../../../magiclang/physics_engine.py) | 400 | `'mana projectile impact target needs a temperature in K'` |
| `UnitErrorML` | [`magiclang/physics_engine.py`](../../../magiclang/physics_engine.py) | 716 | `'2D world gravity must be an acceleration vector in m/s2'` |
| `UnitErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 2047 | `f"cannot compare these values: {exc}"` |
| `UnitErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 2251 | `'friction must be dimensionless'` |
| `UnitErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 2266 | `f"{obj.element}.{name} requires a vector in {old.dimension}"` |
| `UnitErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 2316 | `f"target field '{name}' must be a plain number"` |
| `UnitErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 2329 | `f"target field '{name}' must be dimensionless"` |
| `UnitErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 2377 | `'target pos must be a position vector'` |
| `UnitErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 2390 | `'target restitution must be dimensionless'` |
| `UnitErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 2398 | `'target friction must be dimensionless'` |
| `UnitErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 2453 | `'heat() expects a temperature change in K, not an absolute Celsius temperature'` |
| `UnitErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 2481 | `'cool() expects a temperature change in K, not an absolute Celsius temperature'` |
| `UnitErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 2505 | `'accelerate() vector must be in m/s2'` |
| `UnitErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 2523 | `'decelerate() vector must be in m/s2'` |
| `UnitErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 2552 | `f"impulse() vector must use {MOMENTUM}"` |
| `UnitErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 2566 | `'impulse() target velocity must be a velocity vector'` |
| `UnitErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 2602 | `'velocity() vector must be in m/s'` |
| `UnitErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 2614 | `'targeted velocity requires source and target positions in metres'` |
| `UnitErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 2841 | `'selected target needs a world position in metres'` |
| `UnitErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 3531 | `'conjure() position must be a 2D position measured in metres'` |
| `UnitErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 3543 | `'conjure() velocity must be a velocity vector, e.g. velocity=direction(1, 0) * (5 m/s)'` |
| `UnitErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 3577 | `f"conjure() {field_name} must be a distance, e.g. {field_name}=0.8 m"` |
| `UnitErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 3894 | `'transfigure() scale must be dimensionless'` |
| `UnitErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 4126 | `'direction() components must be dimensionless'` |
| `UnitErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 4231 | `'rotate() angle is dimensionless and interpreted in radians'` |
| `UnitErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 4251 | `'scale() factor must be dimensionless'` |
| `UnitErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 4361 | `'anchor() position must be a position vector in metres'` |
| `UnitErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 4434 | `'sqrt() currently accepts only dimensionless quantities'` |
| `UnitErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 4620 | `f"{label} must be measured in mana"` |
| `UnitErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 4886 | `f"{label} requires {expected}, got {value.dimension}"` |
| `UnitErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 4909 | `f"timing requires seconds, got {value.dimension}"` |
| `UnitErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 5089 | `'advance_time() gravity must be an acceleration vector in m/s2'` |
| `UnitErrorML` | [`magiclang/units.py`](../../../magiclang/units.py) | 89 | `f"unknown or unsupported dimension/unit '{value}'"` |
| `UnitErrorML` | [`magiclang/units.py`](../../../magiclang/units.py) | 121 | `f"unknown unit '{text}'"` |
| `UnitErrorML` | [`magiclang/units.py`](../../../magiclang/units.py) | 138 | `f"C is only supported as a standalone absolute-temperature literal, not '{text}'"` |
| `UnitErrorML` | [`magiclang/units.py`](../../../magiclang/units.py) | 147 | `f"unknown unit '{text}'"` |
| `UnitErrorML` | [`magiclang/units.py`](../../../magiclang/units.py) | 186 | `f"incompatible dimensions: {self.dimension} and {other.dimension}"` |
| `UnitErrorML` | [`magiclang/units.py`](../../../magiclang/units.py) | 192 | `'two absolute temperatures cannot be added'` |
| `UnitErrorML` | [`magiclang/units.py`](../../../magiclang/units.py) | 202 | `'an absolute temperature cannot be subtracted from a temperature change'` |
| `UnitErrorML` | [`magiclang/units.py`](../../../magiclang/units.py) | 215 | `'absolute temperatures cannot be multiplied; use a temperature difference in K'` |
| `UnitErrorML` | [`magiclang/units.py`](../../../magiclang/units.py) | 229 | `'absolute temperatures cannot be divided; use a temperature difference in K'` |
| `UnitErrorML` | [`magiclang/units.py`](../../../magiclang/units.py) | 244 | `'absolute temperatures cannot be divided; use a temperature difference in K'` |
| `UnitErrorML` | [`magiclang/units.py`](../../../magiclang/units.py) | 253 | `'absolute temperatures cannot be exponentiated; use a temperature difference in K'` |
| `UnitErrorML` | [`magiclang/units.py`](../../../magiclang/units.py) | 261 | `'an absolute temperature cannot be negated; use a signed Celsius literal such as -10 C'` |
| `UnitErrorML` | [`magiclang/units.py`](../../../magiclang/units.py) | 296 | `'matter_to_mana() expects mass in kg'` |
| `UnitErrorML` | [`magiclang/units.py`](../../../magiclang/units.py) | 302 | `'mana_to_matter() expects a mana quantity'` |
| `UnitErrorML` | [`magiclang/units.py`](../../../magiclang/units.py) | 308 | `'mana_to_energy() expects a mana quantity'` |
| `UnitErrorML` | [`magiclang/units.py`](../../../magiclang/units.py) | 314 | `'energy_to_mana() expects energy in joules'` |
