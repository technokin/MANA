# MANA Magic Inspiration Catalogue

**Purpose:** a separate design catalogue for future MANA magic. This document is intentionally separate from `CHANGELOG.md`: it is a pool of magical disciplines, spell concepts, rules, and counters—not a record of code changes.

**Status legend**

- **Available primitive:** the current runtime has a relevant primitive that can be composed into an early spell. This does not mean the complete named concept exists as a finished spell.
- **Partial foundation:** some required world/body/material/plane state exists, but important rules, persistence, targeting, or counters are missing.
- **Design target:** a proposed capability that needs implementation and tests before it can be called supported.

MANA treats mana as an omnipresent magical medium and uses appraisal/recording to examine a spell's likely or actual effects. It is not designed around a personal mana battery. Magical limitations should instead emerge from target validity, distance, time, material properties, resistance, world laws, routes, anchors, consequences, and explicit spell rules.

The concepts below take high-level inspiration from broad superhero and comic-book magic themes—mystic arts, artifacts, portals, protective constructs, runic sorcery, emotional/psychic phenomena and occult transformations. They are reinterpreted as original MANA disciplines, not reproductions of specific character powers, dialogue, named spells, costumes, plots, or proprietary rule systems.

## A. Materialcraft and transmutation

### 1. Argent Recasting — **Available primitive**
Change the composition of an existing object to a different registered material while preserving identity and, by default, mass. Destination density changes the volume and collision scale. Counterplay: a ward may prohibit composition changes, and an object's heat or phase can make a requested result unstable. Foundation: `transmute`, `materials.profile`, `periodic.lookup`.

### 2. Alloy Invocation — **Available primitive / partial foundation**
Define a world-local alloy with composition fractions, density, hardness, toughness, conductivity, magnetic response and corrosion resistance, then conjure equipment from it. Its statistics must be measured as game parameters, not claimed to be real metallurgical data. Counterplay: a competing transmuter, corrosive environment, high heat, brittleness, or a material profile with weak toughness.

### 3. Iron Current — **Available primitive**
Apply a directional magical field to magnetically responsive objects. Metal does not obey the caster just because it contains a metal name; the object's magnetic-response profile, mass, distance, anchoring and collision state affect the result. Counterplay: nonresponsive alloys, anchors, counter-force, distance limits and structural failure. Foundation: `metals.control`, `metals.field`.

### 4. Forge Without Flame — **Available primitive**
Conjure a physical blank, then shape it into a blade, shield, spearhead, chain, tool or projectile. The item inherits the material's mechanics. Counterplay is not a dispel animation: the item can still be dropped, blocked, broken, constrained by mass, or made unusable by changing its geometry/material. Foundation: `conjure`, `shape`, `armory` blueprints.

### 5. Returning Filings — **Design target**
Command a cloud of small metallic pieces to assemble into a chosen object. Requires a particle/aggregate model, distance and mass checks, obstruction handling and a clear rule for whether the particles remain separate physical objects or are merged into one. Counterplay: nonmetal fragments, binding wards, magnetic interference or dispersion.

### 6. Living Alloy — **Partial foundation**
A conjured construct changes shape in response to commands while retaining a persistent core identity. It needs a construct state machine, structural integrity, joints/segments and bounded shape changes. It should not be implemented as unconstrained teleporting geometry. Counterplay: severed connections, conflicting commands, anchor loss or structural damage.

### 7. Tempering Word — **Partial foundation**
Temporarily improve toughness or hardness without changing the object's composition. The model should state which coefficient changes and whether the effect expires. It should not grant infinite durability. Counterplay: stronger impacts, duration expiry, conflicting transmutation, or a curse that lowers cohesion.

### 8. Sunder Sigil — **Design target**
Introduce controlled stress into an object at a chosen seam, reducing structural integrity rather than deleting the object. Needs crack propagation and stress-concentration rules. Counterplay: reinforcement, flexible materials, repair, or interrupting the sigil before it completes.

### 9. Weight Reins — **Design target**
Change apparent gravitational loading or local inertia for a target object, while keeping inertial mass and gravitational response carefully defined as separate properties. Requires a dedicated world law to avoid accidental perpetual motion. Counterplay: anchoring, range limits, competing fields and instability under rapid changes.

### 10. Artificer's Imprint — **Partial foundation**
Store a bounded magical instruction on a conjured item: trigger, condition, effect, duration, owner and use count. This should be an event-driven enchantment record, not arbitrary executable Python hidden in object metadata. Counterplay: break the focus rune, use the item incorrectly, dispel it, or exhaust its permitted triggers.

## B. Weaponcraft, armour, arrows and constructs

### 11. Patterned Armament — **Available primitive**
Choose a reusable equipment blueprint—sword, axe, spear, hammer, dagger, shield, bow, crossbow or tool—and create a physical item with actual mass, material, geometry, durability and slot metadata. Users can define their own designs. Counterplay: slot constraints, load, damage, disarming, range and material limits. Foundation: `armory.define`, `armory.inspect`, `conjure`.

### 12. Spell-Headed Arrow — **Available primitive / partial foundation**
Create a normal physical arrow and attach a supported payload such as binding, net, shock, smoke, flare, anchor or burst. Launch speed and collision decide whether it hits. The payload resolves through a bounded effect handler. Counterplay: dodge, shields, cover, armour, payload resistance or removing the arrow before impact.

### 13. Splitflight Quiver — **Design target**
A launched arrow branches into a small fan of sub-projectiles. Requires a child-projectile budget, inherited velocity, collision handling and a rule for total mass/energy bookkeeping. Counterplay: area barriers, cover, interception, or restricting the number of branches.

### 14. Aegis Geometry — **Partial foundation**
Shape a physical shield or conjured energy construct that blocks defined collision paths. Define coverage, integrity, angle, force capacity and what happens when overloaded. Counterplay: flanking, bypassing the protected region, repeated impacts, armour penetration or striking the anchor.

### 15. Folded Armour — **Design target**
A wearable object unfolds from a compact conjured case. The transformation must change physical geometry over a timed animation while keeping mass, collision and equipment slots consistent. Counterplay: jam a joint, damage the case, or interrupt assembly.

### 16. Guardian Effigy — **Partial foundation**
Turn conjured material into a persistent construct whose movement and choices are driven by a simple command policy. It is distinct from summoning an existing being. It needs ownership, an instruction list, movement limits, collision avoidance and a shutdown state. Counterplay: damage its core, invalidate its orders or sever its control link.

### 17. Retort Chain — **Design target**
A conjured chain wraps, anchors or restrains a target. Each segment or the aggregate chain must have length, tensile limit, attachment state and collision. Counterplay: cut it, loosen the anchor, exceed tensile strength, or use form changes that fit through its loops.

### 18. Siege Mark — **Partial foundation**
An enchantment makes a physical projectile transfer more impact energy or mark a target for follow-up effects. It must alter launch parameters or a supported contact handler, not simply report exaggerated damage. Counterplay: remove the mark, break line of sight, absorb the hit or use a ward against repeat impacts.

## C. Weather, elemental magic and terrain

### 19. Circle of Rain — **Available primitive / partial foundation**
Create a local weather zone that applies precipitation, wind, humidity, temperature and duration within a radius. This is a spell changing the weather of an area—not a separate `rain_spell()` function baked into the engine. Counterplay: leave the area, wait for expiry, overwrite the zone, or shelter behind a world-appropriate barrier. Foundation: native `weather` statement and environment solver.

### 20. Windwrit — **Available primitive**
Set a wind vector and let the world engine apply drag to exposed objects. It should affect arrows, smoke and loose materials differently according to mass, area and drag coefficient. Counterplay: heavy/anchored objects, sheltered positions, counter-wind and drag-resistant shapes.

### 21. Thunderhead Covenant — **Partial foundation**
A weather zone builds storm intensity and lightning chance over time. It requires charge accumulation, strike selection, conductive paths and safe rate limits. Counterplay: ground the zone, disperse clouds, leave the radius or interrupt the caster's anchor.

### 22. Frost Bloom — **Partial foundation**
Draw heat from nearby materials and deposit frost, making selected surfaces slippery or causing phase changes. Requires energy accounting, thermal exchange and clear material thresholds. Counterplay: fire/heat, insulation, dry surfaces and materials whose phase rules resist the effect.

### 23. Emberwake — **Partial foundation**
A controlled trail of heat follows a moving object or spell. Burning must depend on material combustibility, ignition threshold and available fuel; the visual trail must not itself cause damage unless recorded as a world effect. Counterplay: water, lack of fuel, heat-resistant materials or extinguishing wards.

### 24. Stone Choir — **Partial foundation**
Move or reshape nearby earth-like matter into a wall, bridge or stepping stones. Needs material availability, mass conservation, load limits, anchoring and collision updates. Counterplay: lack of material, unstable ground, cracking, erosion or interrupting the control.

### 25. Pressure Mantle — **Design target**
Create a local high/low-pressure volume that can push, slow or buffet objects. Requires a pressure field separate from an ordinary velocity impulse. Counterplay: sealed barriers, equalising pressure, field disruption or hiding in a stable shelter.

### 26. Veil of Mist — **Partial foundation**
Change area fog and visibility records; creature perception must consume those records for concealment to work. Counterplay: wind dispersal, heat, magical sensing or moving outside the zone. A fog overlay that only draws grey pixels is not a complete stealth mechanic.

### 27. Ashfall Mantle — **Partial foundation**
A local falling particle/material effect coats objects and degrades visibility. The coating must have bounded mass, duration and clean-up. Counterplay: wash it away, move with the wind, use sealed equipment or dispel the source zone.

### 28. Elemental Refraction — **Design target**
Convert one elemental interaction into another under declared rules—for example, incoming flame is dispersed into heat and light rather than reflected unchanged. Needs a reaction table, energy ledger entry and clear resistance semantics. Counterplay: overwhelm the conversion limit, attack through another channel or disrupt the focus.

## D. Portals, planes and boundary magic

### 29. Threshold Door — **Partial foundation**
Open a named route between two known planes or regions. A route is a world relationship, not a visual ring. It needs endpoint identity, permission, width, duration, transport capacity and rules for blocked or unavailable endpoints. Counterplay: close the path, guard the threshold, sever the anchor or deny the route.

### 30. Anchor of Return — **Partial foundation**
Record a safe return point for a being or object. Teleport/return should move a world entity with its identity and inventory, and fail clearly if the anchor is destroyed or its route is closed. Counterplay: corrupt the anchor, bind the target, or isolate it from a valid route.

### 31. Wayfold — **Design target**
Compress the route between two points without making the world distance itself negative. It needs a transit phase, line-of-sight or destination selection rules, collision-at-arrival handling and an anti-loop limit. Counterplay: lock destinations, anchor space or place a ward around the exit.

### 32. Boundary Ward — **Partial foundation**
Refuse specified entity classes, hostile effects or plane crossings at a boundary. State exactly what the ward observes and which events it can cancel. Counterplay: find an allowed route, satisfy a condition, overload a finite strength or attack the ward's anchor.

### 33. Pocket Sanctum — **Design target**
Create a bounded mini-region with local gravity, climate and access rules. This is a major world-engine feature: requires scoped world state, entity ownership, separate local simulation context and safe entry/exit. Counterplay: lose the focus, exhaust duration or discover the only exit.

### 34. Echo Gate — **Design target**
Create a temporary portal that replays a recorded movement path or sends an object to a known nearby exit. Must define whether it moves the same object or creates a copy; copies require explicit mass/identity rules. Counterplay: interrupt recording, block the exit or reject duplicate identities.

### 35. Planar Beacon — **Partial foundation**
Reveal the presence and direction of a known route or anchor. A beacon reports recorded planar relationships, not omnisciently all beings in all planes. Counterplay: mask the signature, close the path or use a false decoy.

## E. Illusion, perception, mind and information

### 36. Glass Double — **Design target**
Create an illusion that resembles a selected object or being but carries a distinct `illusion` identity and no ordinary mass by default. If it can exert force, that needs a separately declared construct rule. Counterplay: touch tests, magical appraisal, contradictory light/sound or revealing wards.

### 37. Borrowed Sight — **Design target**
Read through another consenting/controlled viewpoint for a limited duration. Requires a perception stream and authority rules; it should not reveal private object properties or source code accidentally. Counterplay: break link, block sensory channels, use a ward or send deceptive stimuli.

### 38. Memory Seal — **Design target**
Hide or lock a fictional memory record inside a being's state. This requires an explicit memory model and identity ownership; it should not rewrite arbitrary interpreter variables. Counterplay: consent key, counterspell, trusted witness or breaking the seal's focus.

### 39. Thought Lantern — **Design target**
Render a being's declared intention or emotional state as a perceptible aura. It is not mind-reading unless that capability is explicitly granted by the spell and model. Counterplay: mental wards, noisy states, deliberate masking or distance.

### 40. Veil of Unnotice — **Design target**
Reduce how strongly observers attend to a target rather than making it invisible. Needs perception checks, observer traits and a scope. Counterplay: direct scrutiny, area search, mechanical sensors or a target drawing attention through sound and impact.

### 41. False Horizon — **Design target**
Alter perceived distance/direction inside an area while leaving physical coordinates unchanged. Pathfinding, aiming and user controls must know whether they operate in true world coordinates or perceived coordinates. Counterplay: anchor lines, outside observer, touch/echo cues or a dispelling pulse.

### 42. Omen Reading — **Partial foundation**
Use appraisal records and known state to predict possible outcomes with uncertainty. A reliable divination result must describe its evidence and limitations, not read future events from nothing. Counterplay: uncertain branches, concealed state, active intervention or probability shifts.

## F. Time, causality and fate

### 43. Moment's Hush — **Design target**
Slow selected entities relative to the world clock. Needs per-entity time scale or local substep policy; animation speed alone is not enough. Counterplay: break the area boundary, dispel the time anchor, or exploit its limited duration.

### 44. Afterimage Step — **Design target**
Leave a decoy at the previous position while the actual entity moves along a legal path. The decoy's mass, collision and duration must be explicit. Counterplay: area detection, collision testing or forcing multiple rapid steps until the effect ends.

### 45. Reprise Mark — **Partial foundation / design target**
Record a limited snapshot of a target and restore only whitelisted properties later. Restoring a full world snapshot can duplicate objects or reverse unrelated interactions, so the spell needs an explicit property list and causal limits. Counterplay: destroy the mark, invalidate dependencies or exceed the saved time window.

### 46. Debt of Seconds — **Design target**
Borrow future recovery time to gain a temporary burst of speed or reflexes. The current body enhancement primitives can model the boost; the consequence requires an explicit delayed fatigue/debuff state. Counterplay: wait out the burst or interrupt before the debt is applied.

### 47. Forked Outcome — **Design target**
Appraise a small number of possible choices without committing any result. This expands the current trial/appraisal idea into bounded branching. Branch count must be capped to prevent exponential simulation. Counterplay is not applicable as combat magic; constraints are computational limits and uncertainty in the model.

### 48. Causal Tether — **Design target**
Bind two world events so that a defined event to one changes a property of the other. Needs cycle detection, recursion limits, distance/scope and ownership rules. Counterplay: break the tether, block the triggering event or counter the linked effect.

## G. Bodycraft, blood, healing and enhancement

### 49. Iron-Bone Mantle — **Partial foundation**
Enhance body durability and change a bounded set of material-like body traits, but don't literally replace all tissue with metal unless the body model supports each organ's material and function. Counterplay: duration, flexibility penalties, magnetic control, heat or a ward against bodily change.

### 50. Colossus Pulse — **Available primitive / partial foundation**
Temporarily increase strength, endurance and damage resistance through `physiology.enhance`. Actual force output changes only where the world engine consumes those traits. Counterplay: exhaustion/duration, immobilisation, leverage, or structural limits in the environment.

### 51. Far-Eye Rite — **Partial foundation**
Enhance sensory traits and add a bounded long-range observation stream. The current sense multiplier is a foundation; actual ray-cast visibility, occlusion and target information filtering require further implementation. Counterplay: darkness, cover, illusion, sensory overload and anti-scrying wards.

### 52. Blood Compass — **Partial foundation**
Sense a known blood signature in a permitted radius, but only where a target has a body-state record and the caster has the required relation/key. Requires signature ownership and privacy rules. Counterplay: masking, decoy signatures, purging or breaking the link.

### 53. Crimson Command — **Available primitive / partial foundation**
Temporarily bind, draw, clot, restore or purge a modelled blood state using the supported physiology primitives. Damage, volume and death consequences follow body rules. Counterplay: warded circulation, range restriction, concentration interruption, clotted state or a counterspell. This is game-world fiction and must not be represented as real medical procedure.

### 54. Graft of Beasts — **Partial foundation**
Register a custom body form with an explicitly chosen organ set, movement mode and trait factors, then transfigure an eligible target. The organ list must support the form's stated functions; flight or underwater breathing cannot be assumed just because the visual has wings or gills. Counterplay: form incompatibility, time limit, lost focus or returning to the original form.

### 55. Second Heart — **Design target**
Conjure/manifest a temporary auxiliary organ or magical organ-anchor that contributes a clearly named resilience effect. Needs organ-instance identity, removal consequences and limits against stacking dozens of hearts. Counterplay: disrupt the anchor, target the original system or wait for expiry.

### 56. Thread of Mending — **Available primitive / partial foundation**
Restore organ integrity and selected body state with `physiology.heal`/`heal_system`, with costs and limits declared in a spell. Severe injury, death, destroyed soul and missing body are distinct outcomes; healing must not silently revive the dead. Counterplay: curse, continued damage, obstruction or a condition that blocks healing.

### 57. Unbroken Pulse — **Partial foundation**
Temporary automatic stabilization when a body's HP or blood state crosses a threshold. Requires an explicit event/timer registration and a one-use flag. Counterplay: drain the protection, prevent the trigger, or target the binding mark.

### 58. Mirror-Skin — **Design target**
A body enchantment returns a fraction of a defined effect (impact, heat or curse) to its source. It must record damage conversion and avoid reflection loops. Counterplay: indirect effects, overload, dispel or an effect that is not in the mirror's declared set.

### 59. Many-Limbed Form — **Partial foundation**
Define a form with additional limbs/sensory parts and a specified movement model. The current anatomy form registry can catalogue organs, but combat reach, grasping slots and independent limbs need implementation. Counterplay: limited coordination, organ damage or form duration expiry.

### 60. Breath Beyond Breath — **Design target**
Temporarily substitute gills, air sacs or an enchanted oxygen store to survive in a declared environment. Must interact with oxygen debt and body form, not simply set a “can breathe” flag forever. Counterplay: storage depletion, pressure/temperature limits or damage to the substitute organ.

## H. Death, undeath and soul anchors

### 61. Severance Word — **Available primitive / partial foundation**
Commit a lethal state transition through an explicit spell rule. The result must emit `being_died`, preserve the body record and state the cause; it cannot merely set a green hit effect. Counterplay depends on declared requirements: resistance, line of sight, valid target, a protective ward, or a failed appraisal condition.

### 62. Bonewake — **Available primitive**
Animate eligible existing remains with the necromancy library. This is not resurrection: the being is undead/animated, not biologically alive, and the original soul state is not assumed to return. Counterplay: dismantle the body, sever control or interrupt the planar source.

### 63. Phylactery Covenant — **Available primitive / partial foundation**
Bind a lich-like being's continuing identity to a registered anchor so it can attempt reconstitution after bodily destruction. The anchor must exist and meet the library's checks. Counterplay: locate and secure the anchor, sever the planar route or resolve the soul binding. The model does not claim a full philosophy of consciousness; it maintains explicit state and events.

### 64. Grave Reconstitution — **Available primitive / partial foundation**
Rebuild a supported lich body from its persistent anchor. This is a special identity/body transition, not ordinary `physiology.revive()`. Counterplay: destroy or ward the anchor, prevent the route, or impose a declared reconstitution delay.

### 65. Soul Ledger — **Design target**
Track a being's soul state, bindings, claims, names and destination as typed records. A soul record must have identity and authority rules to avoid duplicate souls or arbitrary resurrection. Counterplay: lawful release, counter-binding, true-name protection or destroying the relevant anchor.

### 66. Revenant Oath — **Design target**
A dead being returns only when a stated oath/condition is satisfied. Requires an event-driven pact with explicit trigger count, timer, target identity and failure conditions. Counterplay: fulfil or revoke the oath, prevent its trigger or anchor the body/soul away from the return path.

### 67. Lich's Vessel — **Partial foundation**
Use a conjured object as a focus for a soul anchor. A vessel should have mass, material, durability and a unique binding record; destroying its graphic should not count unless the world engine registers actual object damage/destruction. Counterplay: physical destruction, binding severance or route denial.

### 68. Grave Silence — **Design target**
Prevent a limited set of resurrection/reanimation events in an area. Needs a ward rule that intercepts `being_revived`, `being_reanimated` or `being_reconstituted` with clear priority. Counterplay: leave the area, break the sigil or use a different declared life/death channel.

## I. Wards, curses and anti-magic

### 69. Rule Ward — **Partial foundation**
A ward states which operation classes it blocks, reflects, reduces or allows. It should be data-driven and event-based, not a bespoke conditional hidden inside each spell. Counterplay: exceed its strength, exploit an excluded category, change the route or break the ward anchor.

### 70. Spell Sieve — **Design target**
Inspect an incoming magical operation and filter selected components (for example, heat passes but force is damped). Needs a standard effect payload/typing system so spells can be composed and intercepted. Counterplay: polymorphic/unknown effects, overload, or bypassing the defended channel.

### 71. Silence of Runes — **Partial foundation**
Suppress a declared group of spell starts for a limited time or zone. A complete implementation must prevent the runtime effect, not just remove the UI gesture or incantation. Counterplay: leave zone, disrupt the suppressor or use an allowed nonverbal/physical effect only if rules explicitly permit it.

### 72. Burden Curse — **Partial foundation**
Apply a persistent negative condition to a body or object: weakened trait, increased drag, poor recovery, rust vulnerability or noisy planar signature. Each curse needs owner, duration, stack limit, dispel path and exact affected properties. Counterplay: cleanse, resist, remove the anchor or wait for expiration.

### 73. Oath-Bound Seal — **Design target**
Store a condition and its consequence in a typed contract. The engine must distinguish a real event condition from arbitrary source-code execution. Counterplay: satisfy/release the oath, invalidate its witness or break the seal under stated conditions.

### 74. Reflecting Sigil — **Partial foundation**
Return one selected incoming effect if capacity remains. Reflection must preserve target and projectile identities correctly, avoid infinite loops by marking reflected effects and account for barriers and impact ordering. Counterplay: exhaust capacity, use another effect type or attack the focus.

## J. Artifacts, enchantment, appraisal and spell design

### 75. Named Focus — **Partial foundation**
A wand, staff, ring or blade serves as a focus that modifies a spell's reach, precision, stability or allowed effect set. It must be a real equipment object with properties and durability, not an invisible global boost. Counterplay: disarm, damage, steal, jam or ward the focus.

### 76. Spell Imprint — **Design target**
Record one named spell pattern on an eligible object. Casting it should run a validated spell instance with a bounded number of charges or trigger count and clear ownership rules. Counterplay: remove the imprint, use it incorrectly, exhaust it or disrupt its target condition.

### 77. Appraisal Sight — **Available primitive / partial foundation**
Inspect the recorded changes from an `appraise` trial before committing a spell. Expand it to show certainty, estimated inputs, collateral effects, unsupported rules and rollback scope. Counterplay: hidden information, unknown materials, branching outcomes and false premises—not an arbitrary “anti-appraisal spell.”

### 78. Mana Trace — **Partial foundation**
Read recent magical events and energy/route records to follow a spell's path. This is only as complete as the event recording; missing historical data should be clearly reported. Counterplay: expired logs, decoys, wards that mask signatures and route changes.

### 79. Ley Confluence — **Design target**
Let several compatible anchors cooperate to support a large ward or spell, with explicit range, participant count, stability and failure cascade rules. Counterplay: disrupt one critical anchor, isolate participants or make their declared intent incompatible.

### 80. Grand Working — **Design target**
A multi-stage spell whose phases each have conditions and checkpoints. A failed phase should leave a defined partial state or roll back according to the spell's declaration. This is a stronger language feature than a long linear function because the stage boundaries, state and failure paths become inspectable.

## K. Rules for converting inspiration into MANA

Every concept should be designed in this order:

1. Define the **world-state change**. Which object, body, climate, plane route, property or record changes?
2. Define **preconditions**. What target class, range, material, route, body state or anchor must exist?
3. Define **resolution**. Is it instantaneous, continuous, collision-triggered, timed, or event-driven?
4. Define **limits**. Duration, strength, mass, target count, range, concurrency and recursion must be bounded.
5. Define **counterplay**. What can resist, block, break, dispel, evade or expire the effect?
6. Define **recording**. Which event tells the Visualiser and spell appraisal what actually happened?
7. Define **tests**. Include success, invalid target, out-of-range, collision, expiry, interrupted cast, partial failure and repeated-use cases.
8. Only then give the syntax a name. Avoid adding a new function if a general existing operation can express the same semantic action.

A named concept is **not implemented** until its underlying conditions, world effects, counterplay, documentation and tests exist. Prefer shared primitives—material profiles, body-state transitions, event reactions, fields, wards and typed effects—over fifty unrelated special-case functions.

## Sources for broad thematic inspiration

These are official character/theme pages used only as broad inspiration anchors. MANA's spell concepts above are original interpretations and do not reproduce specific named powers or story content.

- [Marvel — Doctor Strange](https://www.marvel.com/characters/doctor-strange-stephen-strange/on-screen): mystic arts, portals, wards, and artifact-oriented sorcery themes.
- [Marvel — Loki](https://www.marvel.com/characters/loki/on-screen): illusion, deception, and transformation themes.
- [Marvel — Marvel Mystics](https://www.marvel.com/comics/discover/606/marvel-mystics): mystical disciplines and occult artifacts across Marvel stories.
- [DC — Doctor Fate](https://www.dc.com/characters/doctor-fate): protective magic, fate, mystical knowledge, and artifact-bound power themes.
- [DC — Zatanna](https://www.dc.com/characters/zatanna): verbal/structured spellcasting as a thematic prompt for language-based incantation.
- [DC — Raven](https://www.dc.com/characters/raven): shadow, emotion, soul and boundary themes.
- [DC — Green Lantern](https://www.dc.com/characters/green-lantern): construct creation and focus-dependent manifestations, reinterpreted here as bounded magical constructs rather than copied ring mechanics.
