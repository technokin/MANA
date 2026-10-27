# Necromancy, Reanimation, and Undead Control

**Page kind:** Explanation  

**Current source version:** v2.0.0

MANA separates reanimating an existing body from writing a spell that constructs or summons an undead being. They can both involve Necro mana and ordinary object manipulation, but they are not the same operation.

## 1. Reanimation requires remains

**Established design:** reanimation requires an existing corpse, skeleton, bones, or remains. Necromancy does not create a body from nothing and then claim it has been reanimated. A normal rock cannot become a valid corpse simply because the spell assigns a label after the fact.

The current implementation records a `body_present` marker when a supported `tgset` material/state is introduced. A valid reanimation request must still have recognised corpse/bone/skeleton/remains markers. It must be an active world object and must not already be undead.

`necromancy.reanimate(corpse[, name])` animates one qualifying object. `necromancy.reanimate_many(corpses[, name])` supports a non-empty list of distinct qualifying objects. `necromancy.is_undead(thing)` checks whether the object currently has the undead flag.

The current function applies the reanimated-being properties to the existing object rather than inventing a separate body's mass. It marks it as a being/undead, sets the home plane to Mortal Plane, keeps the same physical object reference, and raises the `being_reanimated` event. Movement remains handled by general MANA control and physics.

## 2. Necro channel and bookkeeping

`planes.invoke("Necro")` invokes the Necro channel, which maps to Underworld permission in the plane registry. The physical plane used as the source is Underworld; `Necro` is a channel label, not an extra top-level plane.

The current implementation records an internal marker of `100 J` for one reanimation and `100 J` per body in a batch. This is ledger bookkeeping. The user does not pass that number into `reanimate`, it is not a spell budget, it is not subtracted from a mana pool, and it is not added to the object's physical energy. The prototype number may be changed independently from the ability to reanimate.

The pathway must be open for the required Underworld-to-Mortal-Plane transfer record. The relevant permission must be active. A missing route or missing permission raises a MANA error and the operation rolls back its partial state.

## 3. A summon-skeleton spell is ordinary MANA code

There is no built-in `necromancy.summon_skeleton()` operation and no general `summoning.summon()` operation. A user defines a spell that creates/assembles the intended construct using normal object creation, the `Mana` type where appropriate, `mana` constructs/controls, and the required channel/accounting steps.

For example, the following is a structural sketch to explain responsibility. It is not claimed to be a complete skeleton model or combat-ready spell:

```mana
load planes
load necromancy

spell summon_skeleton():
    planes.invoke("Necro")
    frame = create Earth
    frame = transform(frame, "solid")
    # Additional bone-like structure, identity, and control rules are required.
    incant frame

post(summon_skeleton)
```

Expected output:

```text
[POST summon_skeleton] inputs: no parameters
[POST summon_skeleton] energy input: 293150 J (create Earth; matter creation (initial state))
[POST summon_skeleton] created Earth (Earth, 1 kg; create Earth)
[POST summon_skeleton] executed transform(frame, 'solid')
[POST summon_skeleton] spell completed
[POST summon_skeleton] mana appraisal: 0.1 mana
[POST summon_skeleton] created: frame (Earth, 1 kg)
```

A real spell must obey the actual signatures and effect restrictions of the shipped version. The sketch above does not turn Earth into biological remains and should not be confused with `necromancy.reanimate()`. A fully general automatic ledger hook for any user-written spell that invokes Necro is still a broader language/runtime design issue; the current library's reanimation bookkeeping should not be interpreted as a general automatic accounting implementation for all custom spells.

## 4. Constructed undead versus reanimated remains

A constructed skeleton-like entity is assembled/manifested through a spell. A reanimated skeleton already existed as physical bones. This distinction matters for mass, provenance, material, physical energy and the validity of the operation. A construct's energy/matter input follows the core creation model; a reanimated body's existing physical energy/provenance is not replaced by a fabricated fresh body.

Necromantic operations may use:

- **Necro channel permission** to authorise the Underworld-linked energy/accounting operation;
- **ordinary MANA material and geometry operations** to create or form parts;
- **pure mana** to form energy-based constructs or apply universal control;
- **physics and motion** to move or halt the resulting world object;
- **loops/list structures** to operate on multiple entities.

These capabilities should compose. Do not create a unique movement primitive just for a skeleton archer, a skeleton horse, bone armour, bone spear, or an army. Specialist necromancy functions are for death-related concepts (such as reanimation), while general motion/control remains general.

## 5. Cross-plane summoning is different

The `summoning` library is for already-defined beings from other planes. It looks up a `BeingRecord`, verifies an open route to the Mortal Plane, applies the declared summoning requirements, and creates a world object associated with the source being. A built-in Griffin has a Wild Realm home plane; it can be brought from there. A custom summon-skeleton spell need not pretend that a skeleton is a predefined Wild Realm creature or cross a pathway if it creates the body locally.

A local corpse can be reanimated without `summoning`. A spirit or creature that actually must cross from the Underworld or another plane would require the relevant cross-plane system, separate from reanimating a local body.

## 6. Control after reanimation

The reanimation function marks the entity as undead and a being. It does not provide full decision-making AI. To have a skeleton walk to a position, follow a target, stop, attack, or carry something, the program must use available movement/force/control operations or a future behaviour system. `tgset` is for target profile/context; target selection remains outside the spell body.

## 7. Failure conditions and rollback

The current reanimation operation rejects:

- a non-object argument;
- inactive objects;
- objects not originally marked as a corpse/bone/skeleton/remains;
- objects already marked undead;
- a missing Necro/Underworld invocation permission or closed route;
- duplicate body references in a batch;
- invalid optional names.

Library calls that change the world must be executed under `post` or `release`, not inside a directly called pure `def`. A failed reanimation must not leave partial body changes or fake ledger entries behind.
