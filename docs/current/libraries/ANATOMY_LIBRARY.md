# Anatomy and Comparative Biology Library

**Page kind:** Reference
**Status:** implemented reference catalogue with bounded, mutable per-entity body-state binding. This is a game simulation toolkit, not a clinical or veterinary diagnostic model.

The `anatomy` library answers **what a body is made of**. `physiology` answers **what is happening to that body over time**. Keep those responsibilities separate: an anatomical record can describe a liver, a snake's lung, a bird's air sacs, or an earthworm's cuticle; physiology tracks the selected structures' integrity and uses a deliberately limited subset to influence simulated life state, movement, endurance, and injury.

Load it with:

```mana
load anatomy
load physiology
```

Expected output:

```text
(no output)
```

## 1. What the library models

The catalogue follows the useful anatomical hierarchy:

1. **Organism / species template** — lineage/clade, body plan, support structure, thermoregulation, circulation, respiration, digestion, covering, senses, and editable gameplay trait priors.
2. **System** — a coordinated set of structures and broad functions. This is an organisational model, not a claim that every animal has the same named systems.
3. **Organ or anatomical structure** — a named unit such as a heart, liver, nephridia, air sac, feather, nerve cord, bone, skin layer, gland, tooth, or species-specific structure.
4. **Substructure** — subdivisions or meaningful components, such as the skin's epidermis/dermis, the heart's chambers and valves, or the feather's rachis and barbs.
5. **Tissue** — epithelial, connective, muscle, nervous, blood, cartilage, bone, cuticle, and other lineage-appropriate tissue categories.
6. **Cell reference** — a reusable conceptual record for common cell types. It is not a cell-by-cell organism simulation.
7. **State on a world entity** — integrity, injuries, conditions, blood volume and body traits currently tracked by the runtime.

The expanded shared catalogue contains **991 named organ/structure records**, **23 system categories**, **91 stock organism/body-plan templates**, **14 tissue categories**, and **29 named cell-type references**. The human profile exposes 691 addressable anatomical structures, including 206 individually enumerated typical-adult bone records. Human anatomy detail version 4 adds deeper regional, neural, vascular, cardiac, pulmonary, digestive, renal, endocrine, immune, and joint structures while remaining a reference catalogue rather than a cell-by-cell simulation. Counts describe this library version, not the number of structures every creature possesses; fictional templates are design scaffolds, not biological research claims.

### 1.1 Stock-template coverage

The catalogue includes several dinosaur body plans (Tyrannosaurus, Triceratops, Velociraptor, Stegosaurus, Brachiosaurus, Ankylosaurus, Spinosaurus, Diplodocus, Parasaurolophus and Pachycephalosaurus), plus `pteranodon` (a pterosaur, not a dinosaur) and `mosasaurus` (a marine mosasaur). Fantasy templates include distinct `western_dragon` and `eastern_dragon` body plans, `minotaur`, `hydra`, `phoenix`, `centaur`, `merfolk`, ant castes (`ant_worker`, `ant_soldier`, `ant_queen`) and `slime`. Existing mammal, bird, reptile, amphibian, fish, marine invertebrate, insect and other invertebrate templates remain in the same catalogue. Exact animal traits are still approximate game defaults; fantasy anatomy is author-defined design data.

## 2. API reference

### Discover and inspect reference information

| Expression | Purpose |
|---|---|
| `anatomy.species()` | List stock and runtime-defined species/templates and their classifications. |
| `anatomy.search("wing")` | Search species, special structures, senses, roles and names. |
| `anatomy.profile("human")` | Get a complete species/template record, including clade, systems, anatomy list and simulation assumptions. |
| `anatomy.systems("eagle")` | Get the selected profile's systems and the structures assigned to each. |
| `anatomy.organs("human")` | List the selected body's structures. |
| `anatomy.organs("cow", system="digestive")` | List structures assigned to a particular system. |
| `anatomy.organ("skin", "human")` | Look up one structure's role, substructures, tissues and dependencies. |
| `anatomy.bones("human")` | Get the regional bone summary and count caveats. |
| `anatomy.bone_list("human")` | List the typical adult human bones individually. |
| `anatomy.bone("left_humerus", "human")` | Look up a named bone. |
| `anatomy.tissues("human")` | List tissue families and their common subtypes. |
| `anatomy.cell_types()` | List cell reference entries; use `system="nervous"` to filter. |
| `anatomy.blood("bird")` | Inspect the selected profile's blood/circulation reference. |
| `anatomy.inspect(being)` | Inspect the bound species/template and all structures currently tracked for one world entity. |
| `anatomy.inspect(being, "heart")` | Return the reference record and current state for one selected structure. |
| `anatomy.audit("griffin")` | Check a body template for missing structure references and report composition warnings without forbidding unusual fictional biology. |
| `anatomy.define_system(name, purpose=..., dependencies=..., functions=...)` | Register a custom biological or fictional body system. |
| `anatomy.define_organ(name, system=..., role=..., ...)` | Register a new named structure with substructures, tissue references, dependencies and notes. |
| `anatomy.define_species(name, base=..., components=..., ...)` | Create an extensible species or multi-template chimera. |
| `anatomy.bind(target, species, body_mass_kg=None)` | Apply an anatomical/physical template to a world being. |
| `anatomy.track(target, structure)` | Begin live tracking of an extra structure on one body. |

The reference APIs return copies so a program cannot change stock data by modifying a returned nested record. Use the explicitly mutating operations to define custom records or bind a body.

### Compose a new species from multiple body plans

A custom chimera may take its primary support/body plan from one template and borrow compatible structures, systems, and movement declarations from others. `components` accepts up to 16 donor templates; `trait_merge` chooses `primary`, `max`, or `mean` for inherited trait priors. You may then add your own organs and explicitly choose which movement capabilities to add or remove. Because joining organs does not automatically join their physiology, the profile records unresolved circulation, respiration, and digestion integration for review.

```mana
load anatomy
spell define_chimera():
    anatomy.define_species("Sky Serpent",
        base="griffin",
        components=["eagle", "snake"],
        trait_merge="max",
        movement_mode="flight-capable / slithering",
        movement_capabilities=["fly", "glide", "slither", "climb"],
        append_organs=["venom_gland", "air_sacs"],
        body_mass_kg=210, body_length_m=3.2, body_width_m=1.8, body_height_m=1.5,
        collision_radius_m=0.85,
        notes="Fictional hybrid; verify organ integration before treating as biologically coherent.")
    incant true
cast define_chimera
```

Expected output:

```text
[CAST define_chimera] spell committed
[CAST define_chimera] mana appraisal: 0 mana
```

The resulting record is deliberately editable. It gives the author a starting composite of structures and traits—not a claim that eagle flight anatomy and snake anatomy automatically make a viable organism. Use `anatomy.audit("Sky Serpent")` to review missing references and integration cautions, then explicitly refine its systems and physical assumptions.

### Define custom structures and species

A story may need a dragon's second heart, a mana-sensitive organ, a creature with a venom sac, or a different kind of wing. Define the structure first, then derive a species profile that includes it:

```mana
load anatomy

spell register_aetherborn():
    anatomy.define_organ("lumen gland",
        system="magical_specialisation",
        role="Stores and distributes the creature's fictional aetheric charge.",
        substructures=["inner chamber", "field membrane", "root nerves"],
        tissues=["fictional aether-responsive tissue"],
        dependencies=["nervous", "circulatory"],
        notes="World-specific magical anatomy; not a real biological organ.")

    anatomy.define_species("Aetherborn",
        base="human",
        append_organs=["lumen gland"],
        thermoregulation="endothermic",
        strength=1.2,
        senses=1.4,
        notes="Example user-defined species for this setting.")
    incant true

cast register_aetherborn
```

Expected output:

```text
[CAST register_aetherborn] spell committed
[CAST register_aetherborn] mana appraisal: 0 mana
```


Supported skeleton types are `endoskeleton`, `exoskeleton`, `hydrostatic`, `hybrid`, `none`, and `custom`. Recognised movement categories include terrestrial, flight-capable, swim-capable, slither-capable, amphibious, burrowing, climbing, gliding, cursorial, brachiation, stationary and custom. `movement_mode` also accepts a concise descriptive gait label, so a fantasy body can declare combinations such as `"flying / slithering / climbing"`. These labels and inferred `movement_capabilities` make a template extensible; they are not, by themselves, full gait, flight, climbing, or swimming solvers.

Limits are intentional: at most 512 user-defined anatomy structure definitions, 128 custom anatomy systems, 128 custom species templates per runtime, up to 16 component templates per composite, and 1024 addressable structures per species/body. Each bound entity also caps live tracked structures at 1024. The 512-definition limit applies only to adding new catalogue entries, not to the number of already-known structures a body can use. A custom species inherits a primary body plan, can merge donor species, add/remove structures, choose how traits merge (`primary`, `max`, or `mean`), and explicitly override movement, skeleton, and physical dimensions. Composition is an editable design template; incompatible donor systems are reported rather than silently assumed to function together.

### Bind a being to a body model

Summoning, creature catalogues and entity creation can produce a generic being. Bind that being to a species when the program needs a selected anatomy rather than generic humanoid defaults:

```mana
load planes
load anatomy
load physiology

planes.open_path("Wild Realm", "Mortal Plane")
spell inspect_griffin():
    griffin = summon "Griffin" from "Wild Realm"
    anatomy.bind(griffin, "griffin")
    anatomy.inspect(griffin, "beak")
    physiology.injure(griffin, "left_humerus", 0.1)
    incant griffin

cast inspect_griffin
```

Expected output:

```text
[CAST inspect_griffin] spell committed
[CAST inspect_griffin] mana appraisal: 0 mana
```

`anatomy.bind(target, species, preserve_injuries=true, body_mass_kg=None)` selects the body structures/systems, traits, movement capabilities, and physical envelope. The built-in templates now provide approximate body mass, length, width, height, density, volume, and collision radius. Those game-scale baselines feed the current 2D world physics so that a human, earthworm, eagle, and dragon are not all simulated as the same generic 1 kg body. `body_mass_kg` can override the template mass for an individual. The collider is still a 2D circle proxy—not an articulated skeletal mesh or precise body-shape collision model—and the values are editable gameplay priors, not exact anatomical measurements.

Binding preserves the integrity of overlapping structures and—when changing an already-bound species—preserves the proportion of remaining blood volume. Binding an initially unbound being fills the selected profile's reference blood volume rather than misreading the generic runtime default as prior blood loss.

`anatomy.track(target, structure)` explicitly begins tracking a known structure which was not part of the originally bound model. The API rejects ordinary inanimate items and inactive entities where a body binding is inappropriate.

### Physical body baselines

Every stock body plan now has an approximate physical envelope: `simulation.body_mass_kg`, `body_length_m`, `body_width_m`, `body_height_m`, `body_density_kg_m3`, `body_volume_m3`, and `collision_radius_m`. These values are there so body binding can configure the current world object's physical mass and collider scale; they are deliberately marked as approximate game baselines. They should be customised for unusual variants, juveniles, giant forms, magic-altered bodies, or specific narrative requirements.

`anatomy.define_species` accepts `body_mass_kg`, `body_length_m`, `body_width_m`, `body_height_m`, and `collision_radius_m` as optional positive finite values. For a hybrid, the default mass estimate uses the primary template plus a fraction of each additional donor mass, and dimensions use the largest donor baseline as an initial guess. That is a fallback only: a user-defined chimera should explicitly select its actual intended dimensions.

The runtime remains a 2D world engine. Body dimensions are useful simulation metadata; its default collision collider is still a circle proxy. There is no automatic articulated spine, wing-joint, six-limb coordination, per-segment worm locomotion, or full volume/pressure solver merely because those structures exist in the catalogue. Those require dedicated mechanics and tests.

## 3. Human anatomy reference

The human profile is an extensible reference map, not a claim that all organs, neural pathways, biochemical gradients or tissue mechanics are simulated. It covers these broad systems:

- **Integumentary:** epidermis, dermis, hypodermis/subcutis, skin appendages, follicles and glands, nails/hair and barrier interfaces.
- **Skeletal:** the typical adult 206-bone inventory, named skull/facial bones, auditory ossicles, hyoid, vertebral column, ribs/sternum, girdles, limbs and phalanges, plus cartilage/joints and connective supports.
- **Muscular and locomotor:** skeletal muscle, muscle attachment, tendon/ligament, joint mechanics as reference structures, posture and movement-supporting forms.
- **Nervous:** brain subdivisions, brainstem, cerebellum, spinal cord, peripheral/autonomic nerves and sensory pathways.
- **Sensory:** eyes, ears/inner ear, tongue, tactile receptors, smell-related structures and balance/proprioception as named categories.
- **Circulatory and hematopoietic:** heart, valves, arteries, veins, capillaries, blood/plasma, oxygen carriers, clotting, spleen and marrow/cell-production references.
- **Respiratory:** upper airways, lungs, branching airways and respiratory support structures. The runtime currently uses a compact lung-integrity/oxygen proxy rather than a ventilation/perfusion solver.
- **Digestive:** oral cavity, teeth/tongue/salivary structures, pharynx, oesophagus, stomach, intestines, liver, gallbladder where present and pancreas.
- **Renal/excretory:** kidneys, filtration units as reference structures, ureters, bladder and urethral route.
- **Endocrine and metabolic:** thyroid, adrenal glands, pancreas/islets, liver, metabolic signalling and energy-regulation structures.
- **Immune and lymphatic:** spleen, marrow-associated production, lymph nodes, lymph vessels and tissue immune interfaces.
- **Reproductive:** gonads, ducts and accessory structures as reference records; reproductive cycles and development are not simulated by default.
- **Thermoregulation:** skin, vessels, muscle heat and endocrine/behavioural controls as a functional grouping.

### Typical adult human skeleton

The API exposes **206 individually named reference records**, conventionally grouped into **80 axial** and **126 appendicular bones**. This is the normal teaching count for a typical adult. Age-related fusion, sesamoids, sutural bones and individual anatomical variation mean the inventory is not a universal biological invariant. Each bone record has region/group metadata and is addressable through `anatomy.bone(name, "human")`.

These entries are appropriate for targeting named structures in a spell (for example, the left humerus) or specifying which injury should affect a body trait. They do not model trabecular microarchitecture, osteons, exact fracture surfaces or healing biomechanics unless a game developer builds those subsystems.

## 4. Comparative species templates

The records distinguish **catalogued facts**, **coarse clade summaries**, **unknowns**, and **fictional design decisions**. Gameplay multipliers such as strength/speed/senses are tunable convenience priors, not measured rankings of animals.

### Human

A primate mammal with endoskeleton, four-chambered heart, lungs, mammalian blood-cell traits, endothermic regulation, and the named 206-bone adult reference. Adult blood volume and body temperature in the profile are scenario defaults only. The template can be expanded with reproductive details, specialised immune cell populations, nerve branches, endocrine glands, skin layers or extra skeletal granularity as a world requires.

### Lion and tiger

Both use a felid mammal baseline, with a flexible vertebral column, strong shoulder/forelimb structures, digitigrade hind limbs, tail, jaw and carnassial teeth, vibrissae and retractile/protractile claw apparatus. Their skeleton profiles list skeletal regions and homologous structures but do **not** invent a universal bone count. The mane is recorded as a variable lion feature, not a mandatory structure for every lion.

### Snake

A reptile body plan with an elongated vertebral column and many ribs, specialised jaw articulation, scale covering, vomeronasal/chemical sensing, and species-dependent lung arrangement. The template removes a true diaphragm from its standard respiratory map. Snake species differ in lung morphology and vestigial pelvic structures; the generic “snake” profile cannot stand in for every species. Ectothermy means body temperature depends strongly on environment and behaviour, rather than being clamped to 37 °C.

### Earthworm

A segmented annelid with hydrostatic support—not a bony skeleton—circular and longitudinal body-wall muscles, a moist cuticle/epidermal exchange surface, coelomic compartments, setae in many segments, a ventral nerve cord with anterior cerebral ganglia, nephridia and contractile vascular arches. It does not have a vertebrate-style heart, lungs, kidneys or brain. Consequently its current simulation routes the circulatory proxy through the aortic arches, gas-exchange proxy through the skin/cuticle, neural integrity through the ganglia/nerve cord, and excretory proxy through nephridia. That routing is a gameplay abstraction, not a full annelid physiology simulator.

### Birds: eagle, owl, raven, falcon, parrot and pigeon

Bird templates include beak, wings, flight muscles, a keeled sternum/pectoral attachments as broad anatomical references, and avian respiratory structures. A typical bird has relatively rigid gas-exchanging lungs and compliant air sacs that primarily ventilate those lungs; air sacs should not be described as simple spare lungs. The form list is clade-level and does not claim an exact named-bone inventory or a complete air-sac map for every bird order. Raptors' visual acuity and other sensory differences are descriptive priors, not clinical numeric values.

### Giraffe

A ruminant ungulate template with a long neck, limbs, ossicones, rumen/reticulum/omasum/abomasum, and cardiovascular adaptations relevant to a vertically separated heart and head. Research reviews report high mean arterial pressure in giraffes around 200 mm Hg in studied contexts, associated with cerebral perfusion and specialised vascular/renal adaptations. The library does **not** turn that single reported value into a universal constant; actual physiology varies with measurement and state. This species is ideal for authoring spells that target blood pressure, vessel compliance or posture as separate mechanics later.

### Cow and pig

Cattle are ruminants: rumen, reticulum and omasum act as forestomachs for fermentation and particle processing; the abomasum is the acidic/enzymatic “true stomach.” Microbiome/fermentation and gas release matter to ruminant biology. The catalogue treats the four compartments as distinct structures rather than four identical stomachs. The pig template is monogastric/omnivorous, with a prominent snout/nasal-discus reference, tusks in appropriate sexes/ages/breeds, and behavioural cooling needs; it should not inherit ruminant compartments. A species-specific cattle profile's blood volume and trait values are approximate game defaults rather than veterinary ranges.

### Additional domestic mammals: horse and dog

The horse template uses a monogastric hindgut-fermenting digestive design with large cecum/colon structures, cursorial limbs and hoof/limb-support references. The dog template is broad by design because dog sizes and proportions vary greatly by breed; it uses a canid digitigrade profile, claws/paw pads, strong olfaction and panting-associated cooling, and does not promise breed-specific bone inventories.

### Fictional templates: dragon, griffin, goblin, orc and elf

These profiles are **explicitly fictional, editable proposals**. A dragon's six-limbed flight body, scale armour, tail, optional fire sac and aetheric core are world-design choices; the library does not declare a canonical dragon biology. The griffin is a hybrid sketch with mammalian trunk/hindquarters and avian head/wings; its respiratory, skeletal and blood traits must be authored because real biological hybrids do not determine a coherent design. Goblin, orc and elf start from a humanoid mammal-like scaffold so authors may customise bone proportions, ears, teeth, lifespan, blood chemistry, organs, senses and thermoregulation. Remove the mammal-like defaults if that is not the species the setting needs.

## 5. Tissue and cell references

The tissue API includes broad epithelial types (surface, glandular, transitional and others), connective tissue (loose/dense, adipose, elastic, cartilage, bone, blood), skeletal/cardiac/smooth muscle, nervous tissues, lymphoid, marrow-associated, keratinised structures, cuticle, germinal tissue and fluid compartments. The four familiar teaching-level human tissue classes—epithelial, connective, muscle and nervous—are represented by finer subtypes; the expanded list is designed for cross-clade authoring, so not every subtype occurs in every species.

Cell references include erythrocytes, platelets, thrombocytes, leukocytes, neurons, glial cells, cardiomyocytes, smooth/skeletal muscle cells, osteoblasts/osteocytes/osteoclasts, chondrocytes, keratinocytes, melanocytes, adipocytes, hepatocytes, podocytes, enterocytes, goblet cells, pancreatic beta cells, fibroblasts, endothelial cells, macrophages, mast cells and annelid-focused reference types. These are glossary/reference records; MANA does not simulate every cell's biochemistry or interactions just because an entry exists.

Blood profile metadata records whether a lineage's erythrocytes are nucleated and what clotting-cell model is intended when known. Mammalian mature red cells are normally anucleate, while birds and many reptiles have nucleated erythrocytes. The earthworm profile deliberately avoids forcing a mammalian red-cell model onto an annelid's haemoglobin-bearing circulation. Specific species and taxa can differ; this catalogue is an authoring aid, not a diagnostic atlas.

## 6. Interaction with `physiology`

Use `anatomy` to define, inspect, query and bind anatomical reference data. Use `physiology` for dynamic state mutations:

- `physiology.injure(being, "left_humerus", 0.15)` reduces the named structure's integrity.
- `physiology.heal(being, "left_humerus", 0.1)` restores a bounded amount of integrity.
- `physiology.injure_system(being, "respiratory", 0.2)` can target the selected body system.
- `physiology.manipulate_blood(...)`, `set_bleeding(...)`, `set_temperature(...)`, `kill(...)`, and `revive(...)` operate on the bounded state fields documented in the physiology guide.

After a body is bound, physiology uses the selected species' actual tracked structures for its simplified health hooks. Individual human bone integrity affects aggregate skeletal durability without making one bone act as the entire skeleton. Nonhuman special cases use an appropriate named proxy for the body plan: earthworm cuticle/arches/ganglia/nephridia, avian lungs plus air sacs, and snake lung naming rather than assuming all creatures have identical vertebrate anatomy. Many detailed structures are still reference-only and do not yet have bespoke time-dependent mechanics.

The body model supports up to 1024 addressable structures per species/body, and each bound entity caps live tracked structures at 1024. This is separate from the limit of 512 user-defined structure definitions per runtime. Names, tissue details and cell records may be numerous without generating runtime state for every one; individual dynamic tracking is allocated only when the selected profile is bound or a structure is explicitly tracked.

## 7. Sources and method

The profile text is summarised from educational and peer-reviewed resources, not copied from them. The references below support the broad structures and important clade distinctions; this library is not a substitute for specialist zoological monographs or medical/veterinary guidance.

- [OpenStax, *Anatomy & Physiology 2e*](https://openstax.org/books/anatomy-and-physiology-2e/pages/preface) — introductory human anatomical/physiological structure and system organisation.
- [OpenStax, structural organisation of the human body](https://openstax.org/books/anatomy-and-physiology/pages/1-2-structural-organization-of-the-human-body) — chemical-to-organism structural hierarchy.
- [StatPearls / NCBI Bookshelf, Anatomy, Appendicular Skeleton](https://www.ncbi.nlm.nih.gov/books/NBK537097/) — conventional adult human skeleton division and appendicular structures.
- [Merck Veterinary Manual, *The Digestive System of Beef Cattle*](https://www.merckvetmanual.com/management-and-nutrition/nutrition-beef-cattle/the-digestive-system-of-beef-cattle) — ruminant compartments and their distinct functions.
- [Merck Veterinary Manual, *The Digestive System in Animals*](https://www.merckvetmanual.com/digestive-system/digestive-system-introduction/the-digestive-system-in-animals) — comparative digestive tract structures and physiological functions.
- [Maina & Schachner, avian respiratory-system review, *Philosophical Transactions of the Royal Society B* (2025)](https://pmc.ncbi.nlm.nih.gov/articles/PMC11864829/) — avian lungs, air sacs and lineage-specific respiration.
- [Merck Veterinary Manual, *Overview of Reptiles*](https://www.merckvetmanual.com/exotic-and-laboratory-animals/reptiles/overview-of-reptiles) — reptile physiology, ectothermy and organ-system differences.
- [UF/IFAS, *Earthworm Anatomy*](https://ask.ifas.ufl.edu/publication/in946) — annelid body wall, hydrostatic support and named organ systems.
- [Aalkjær & Wang, *The Remarkable Cardiovascular System of Giraffes*, Annual Review of Physiology (2021)](https://www.annualreviews.org/content/journals/10.1146/annurev-physiol-031620-094629) — giraffe cardiovascular adaptations to height/gravity.

Numeric gameplay priors are not extracted physiological measurements unless the record explicitly says so. Unknown animal bone counts remain unknown. All fictional templates are designer assumptions. Extend the catalogue when the actual use case needs more detail, and write an explicit test for each new dynamic interaction.

## Appendix A — Full catalogue of systems, species, tissues, cells, and structures

This appendix is generated from the exact runtime data shipped with this version. It is the canonical name/reference directory for editors and spell authors. A listed structure is an addressable reference record; it does **not** imply every named part has its own dynamic solver. Runtime-tracked structures are allocated only for the selected body model and explicit additions.

### A1. All system categories

| Key | Display name | Purpose | Dependencies |
|---|---|---|---|
| `integumentary` | Integumentary | Boundary, barrier, sensory interface, temperature exchange, and external identity. | `immune`, `nervous`, `thermoregulation` |
| `skeletal` | Skeletal | Support, protection, force transmission, mineral storage, and (in marrow-bearing vertebrates) blood-cell formation. | `muscular`, `circulatory`, `endocrine` |
| `muscular` | Muscular | Force production, posture, organ movement, heat generation, and locomotion. | `nervous`, `circulatory`, `respiratory`, `skeletal` |
| `nervous` | Nervous | Sensation, integration, memory, coordination, autonomic regulation, and motor commands. | `circulatory`, `respiratory`, `integumentary`, `sensory` |
| `sensory` | Sensory | Detection and interpretation of light, sound, chemicals, pressure, temperature, position, and species-specific cues. | `nervous`, `integumentary` |
| `endocrine` | Endocrine | Slower systemic regulation using hormones and feedback loops. | `nervous`, `circulatory`, `metabolic` |
| `circulatory` | Circulatory | Transport of gases, nutrients, heat, signals, immune cells, and waste. | `heart`, `respiratory`, `digestive`, `renal` |
| `lymphatic` | Lymphatic | Return of interstitial fluid, lipid transport in many vertebrates, and immune-cell traffic. | `circulatory`, `immune`, `digestive` |
| `immune` | Immune | Recognition, containment, and clearance of harmful biological agents and damaged material. | `lymphatic`, `circulatory`, `bone_marrow`, `integumentary` |
| `respiratory` | Respiratory | Gas exchange and (in many species) vocal airflow; design differs radically by clade. | `circulatory`, `muscular`, `nervous` |
| `digestive` | Digestive | Acquisition, mechanical and chemical breakdown, absorption, microbial processing, and waste formation. | `circulatory`, `endocrine`, `nervous`, `microbiome` |
| `metabolic` | Metabolic / hepatic | Nutrient processing, storage, synthesis, detoxification, and homeostatic chemistry. | `digestive`, `circulatory`, `endocrine`, `renal` |
| `renal` | Renal / excretory | Waste removal, water/electrolyte balance, acid-base regulation, and pressure-related signalling. | `circulatory`, `endocrine` |
| `reproductive` | Reproductive | Gamete production, fertilisation, gestation or egg development, and species-specific parental structures. | `endocrine`, `circulatory`, `metabolic` |
| `hematopoietic` | Blood formation | Production, maturation, and turnover of circulating cells or cell analogues. | `skeletal`, `immune`, `endocrine` |
| `thermoregulation` | Thermoregulation | Keeping body temperature within workable bounds through physiology and behaviour. | `integumentary`, `circulatory`, `muscular`, `endocrine` |
| `microbiome` | Resident microbiota | Communities of microorganisms that influence digestion, barrier defence, and local chemistry. | `digestive`, `immune` |
| `locomotor` | Locomotor integration | Coordinated gait, climbing, flight, swimming, burrowing, slithering, or stationary posture. | `skeletal`, `muscular`, `nervous`, `sensory` |
| `developmental` | Development and regeneration | Growth, maturation, regeneration sites and form-specific development. | `endocrine`, `metabolic`, `integumentary` |
| `feeding` | Feeding and prey handling | Capture, grip, cut, crush, filter, chew, swallow or otherwise acquire food. | `muscular`, `sensory`, `digestive` |
| `defence` | Defence and specialised secretions | Claws, venom, ink, stings and other lineage-specific defence structures. | `nervous`, `muscular`, `integumentary` |
| `electroreception` | Electrosensation and electric output | Specialised detection or production of electric fields. | `nervous`, `sensory` |
| `magical_specialisation` | Species-specific / fictional specialisations | Optional structures whose behaviour must be explicitly defined by a species or spell designer. | — |

### A2. Every stock species/template

| Key | Name | Status / clade | Skeleton | Bone count policy | Addressable structures | Distinctive reference details |
|---|---|---|---|---|---:|---|
| `human` | Human | real / mammal / primate | endoskeleton | 206 | 306 | type: closed_double; type: alveolar_lungs; type: monogastric_omnivore; covering: skin, variable hair, nails, sweat and sebaceous glands; mode: placental mammal |
| `lion` | Lion | real / mammal / felid | endoskeleton | Not asserted; use skeletal structures | 137 | type: closed_double; type: alveolar_lungs; type: obligate_carnivore_simple_stomach; covering: fur; scent glands; paw pads; protractile/retractile claw apparatus; special: claws, tail, teeth, vibrissae; Felid-specialised vertebral flexibility and forelimb musculature. |
| `tiger` | Tiger | real / mammal / felid | endoskeleton | Not asserted; use skeletal structures | 137 | type: closed_double; type: alveolar_lungs; type: obligate_carnivore_simple_stomach; covering: striped fur, whiskers, paw pads, claws; special: claws, tail, teeth, vibrissae; Tiger-specific size/marking differences do not imply a different basic organ-system plan from other felids. |
| `snake` | Snake (generalised squamate) | real / reptile / squamate | endoskeleton | Not asserted; use skeletal structures | 109 | type: closed_double; type: elongated_reptilian_lungs; type: carnivorous_elastic_ingestion; covering: keratinised scales; periodic ecdysis; little glandular surface activity; special: serpentine_lung, vomeronasal_organ, fangs, venom_gland, cloaca; Venom apparatus is optional: most snakes are not to be modelled as possessing identical venom delivery systems. |
| `earthworm` | Earthworm (generalised annelid) | real / annelid / invertebrate | hydrostatic | 0 | 32 | type: closed_vessel_system; type: cutaneous_gas_exchange; type: segmented_detritivore_gut; covering: moist cuticle/mucus-coated skin; setae for grip; clitellum in mature individuals of many species; special: hydrostatic_skeleton, earthworm_segment, ventral_nerve_cord, nephridia, aortic_arches, skin_cuticle, clitellum; Hermaphroditic reproductive anatomy is c |
| `eagle` | Eagle | real / bird / raptor | endoskeleton_partly_pneumatic | Not asserted; use skeletal structures | 125 | type: closed_double; type: rigid_lungs_with_air_sacs; type: raptor_avian; covering: contour and flight feathers; keratin beak; scales on feet; special: wings, air_sacs, keel, pneumatic_bones, beak, claws |
| `owl` | Owl | real / bird / raptor | endoskeleton_partly_pneumatic | Not asserted; use skeletal structures | 125 | type: closed_double; type: rigid_lungs_with_air_sacs; type: avian_glandular_stomach_and_gizzard; covering: soft specialised flight feathers, facial disk feathers, feathered legs in many species; special: wings, air_sacs, keel, pneumatic_bones, beak, claws |
| `raven` | Raven | real / bird / corvid | endoskeleton_partly_pneumatic | Not asserted; use skeletal structures | 125 | type: closed_double; type: rigid_lungs_with_air_sacs; type: avian_omnivore; covering: contour feathers and keratin beak; special: wings, air_sacs, keel, pneumatic_bones, beak, claws |
| `falcon` | Falcon | real / bird / raptor | endoskeleton_partly_pneumatic | Not asserted; use skeletal structures | 125 | type: closed_double; type: rigid_lungs_with_air_sacs; type: raptor_avian; covering: flight feathers, contour feathers, scaled feet; special: wings, air_sacs, keel, pneumatic_bones, beak, claws |
| `parrot` | Parrot | real / bird / psittaciform | endoskeleton_partly_pneumatic | Not asserted; use skeletal structures | 125 | type: closed_double; type: rigid_lungs_with_air_sacs; type: avian_herbivore_or_omnivore; covering: contour and flight feathers; powder-down in some taxa; special: wings, air_sacs, keel, beak, claws |
| `pigeon` | Pigeon | real / bird / columbid | endoskeleton_partly_pneumatic | Not asserted; use skeletal structures | 125 | type: closed_double; type: rigid_lungs_with_air_sacs; type: avian_seed_eater; covering: contour feathers and flight feathers; special: wings, air_sacs, keel, pneumatic_bones, beak, claws |
| `giraffe` | Giraffe | real / mammal / ruminant ungulate | endoskeleton | Not asserted; use skeletal structures | 143 | type: closed_double; type: alveolar_lungs; type: ruminant_foregut_fermenter; covering: short patterned coat, skin, tail tuft, ossicone skin/hair; special: abomasum, omasum, ossicones, reticulum, rumen, ruminant_microbiome, tail |
| `cow` | Domestic Cattle | real / mammal / ruminant bovine | endoskeleton | Not asserted; use skeletal structures | 142 | type: closed_double; type: alveolar_lungs; type: ruminant_foregut_fermenter; covering: skin, coat, sweat/sebaceous structures varying with breed, cloven hooves; special: abomasum, omasum, reticulum, rumen, ruminant_microbiome |
| `pig` | Domestic Pig | real / mammal / suid omnivore | endoskeleton | Not asserted; use skeletal structures | 139 | type: closed_double; type: alveolar_lungs; type: monogastric_omnivore; covering: sparse-to-moderate bristles depending on breed, skin, specialised snout disk; cooling relies substantially on behaviour/environment; special: nasal_discus, tusks |
| `horse` | Horse | real / mammal / perissodactyl | endoskeleton | Not asserted; use skeletal structures | 137 | type: closed_double; type: alveolar_lungs; type: hindgut_fermenter_monogastric; covering: hair coat, mane, tail, hoof keratin; special: tail, claws |
| `dog` | Domestic Dog | real / mammal / canid | endoskeleton | Not asserted; use skeletal structures | 137 | type: closed_double; type: alveolar_lungs; type: carnivorous_omnivore_monogastric; covering: coat varies widely; paw pads and claws; special: vibrissae, claws, tail |
| `dragon` | Dragon (fantasy template) | fictional-template / fictional vertebrate-like hexapod | fictional_endoskeleton | Not asserted; use skeletal structures | 143 | type: fictional_closed_double; type: fictional_lungs_plus_optional_aetheric_fire_sac; type: fictional_large_predator; covering: overlapping scale armour, optional osteoderms, under-skin thermal insulation; special: wings, tail, scale_armour, fire_sac, aetheric_core; Every dragon trait is a user-editable fantasy assumption. Size, wing loading, thermal balance |
| `griffin` | Griffin (fantasy template) | fictional-template / fictional mammal-avian hybrid | fictional_hybrid_endoskeleton | Not asserted; use skeletal structures | 142 | type: fictional_closed_double; type: bird-like lungs_with_air_sacs_as_optional_hypothesis; type: carnivorous_hybrid; covering: fur over body, feathers over wings, keratin beak, talons; special: wings, air_sacs, beak, claws, tail; Use as a modular hybrid template, not an assertion that griffins have a coherent canonical anatomy. |
| `goblin` | Goblin (fantasy template) | fictional-template / fictional humanoid | humanoid_endoskeleton | Not asserted; use skeletal structures | 139 | type: four-chambered mammal-like default hypothesis; type: alveolar_mammal-like default hypothesis; type: omnivore_monogastric default hypothesis; covering: user-defined skin, hair and pigmentation; large ears or specialised skin are optional; All features are editable fantasy defaults; there is no scientific goblin anatomy. |
| `orc` | Orc (fantasy template) | fictional-template / fictional robust humanoid | robust_humanoid_endoskeleton | Not asserted; use skeletal structures | 140 | type: four-chambered mammal-like default hypothesis; type: alveolar_mammal-like default hypothesis; type: omnivore_monogastric default hypothesis; covering: thicker dermal layers, scars, hair and pigmentation are configurable; special: tusks; Musculoskeletal robustness and tusks are design options, not a single universal fantasy canon. |
| `elf` | Elf (fantasy template) | fictional-template / fictional gracile humanoid | gracile_humanoid_endoskeleton | Not asserted; use skeletal structures | 139 | type: four-chambered mammal-like default hypothesis; type: alveolar_mammal-like default hypothesis; type: omnivore_monogastric default hypothesis; covering: skin, hair, nails; pointed pinnae optional; Lifespan, senses, bone density and organ differences must be explicitly chosen by the world designer; no universal elf biology exists. |

#### Species-specific modelling rules

- **Human:** typical adult skeleton has 206 individually named reference bones (80 axial; 126 appendicular). It is a conventional reference count, not a universal count for every individual or life stage. <Cite refs={"turn154505search8"} />
- **Other mammals:** named regions and skeletal structures are listed where supported, but exact total bone counts are left unknown in the runtime unless a species-specific count is explicitly curated.
- **Birds:** use feathers, wings, keel/sternum, furcula and species-appropriate skeletal labels. The bird respiratory model separates rigid gas-exchange lungs from ventilatory air sacs; air sacs are not treated as extra gas-exchanging lungs. <Cite refs={"turn852068search5","turn852068search6"} />
- **Cattle and giraffes:** the ruminant digestive profile includes rumen, reticulum, omasum and abomasum rather than a simple monogastric stomach abstraction. Giraffe cardiovascular fields identify height-related circulation as a distinctive comparative note, not a simulated pressure-flow solver. <Cite refs={"turn852068search1","turn852068search3","turn852068search0"} />
- **Snake:** represented as a generalised squamate, not a claim that all snakes share identical lung asymmetry, vestigial limbs or vertebral counts. Those depend on species and lineage.
- **Earthworm:** an annelid with a moist skin/cuticle gas-exchange interface, hydrostatic support, aortic arches, cerebral ganglia and ventral nerve cord, plus nephridia; do not apply vertebrate heart/lung/brain assumptions. <Cite refs={"turn158503search4","turn158503search9"} />
- **Dragon, griffin, goblin, orc and elf:** editable *fictional design templates*. Their organs, blood chemistry, bones and traits are hypotheses supplied for game design; there is no empirically established anatomy to cite.

### A3. Full shared anatomical structure directory

This table documents all **991 shared records** present in `anatomy_data.py`, including the individually addressable human bones and comparative skeleton structures. The API may expose a smaller subset for a given species; call `anatomy.organs(species)` to get that profile’s available list.

| Identifier | System | Record kind | Reference role |
|---|---|---|---|
| `aortic_arches` | `circulatory` | `organ_or_structure` | Contractile arch vessels that help circulate blood in earthworms; commonly called hearts in basic references. |
| `arteries` | `circulatory` | `organ_or_structure` | Carry blood away from the central pump under pressure. |
| `blood` | `circulatory` | `organ_or_structure` | Transport fluid containing liquid phase, gas carriers, immune cells and clotting components. |
| `blood_plasma` | `circulatory` | `organ_or_structure` | Liquid portion transporting proteins, nutrients, dissolved ions, hormones and wastes. |
| `capillaries` | `circulatory` | `organ_or_structure` | Exchange gases, nutrients, fluids, hormones and wastes with tissues. |
| `heart` | `circulatory` | `organ_or_structure` | Pressure-generating pump; chamber count and routing differ by clade. |
| `heart_valves` | `circulatory` | `organ_or_structure` | One-way control of central-pump flow. |
| `veins` | `circulatory` | `organ_or_structure` | Return blood to the central pump; many have valves and act as capacitance vessels. |
| `abomasum` | `digestive` | `organ_or_structure` | Glandular, acid-secreting stomach compartment of ruminants. |
| `cecum` | `digestive` | `organ_or_structure` | Blind-ended fermentation or junctional chamber, varying greatly by species. |
| `cloaca` | `digestive` | `organ_or_structure` | Shared terminal chamber for digestive, urinary and reproductive tracts in birds, reptiles and many other vertebrates. |
| `colon` | `digestive` | `organ_or_structure` | Water/electrolyte recovery and microbial fermentation to species-specific degrees. |
| `crop` | `digestive` | `organ_or_structure` | Expandable foregut pouch used for food storage/softening in many birds and some other animals. |
| `crop_muscle` | `digestive` | `organ_or_structure` | Muscular control around a crop or storage pouch when present. |
| `duodenum` | `digestive` | `organ_or_structure` | Receives stomach contents, bile and pancreatic secretions in mammals. |
| `esophagus` | `digestive` | `organ_or_structure` | Moves swallowed material toward stomach or crop/forestomach using coordinated motility. |
| `gallbladder` | `digestive` | `organ_or_structure` | Stores/concentrates bile in species that possess it. |
| `gizzard` | `digestive` | `organ_or_structure` | Muscular grinding chamber in birds and some other taxa. |
| `ileum` | `digestive` | `organ_or_structure` | Distal small-intestinal segment; includes specialised immune tissue in many mammals. |
| `intestines` | `digestive` | `organ_or_structure` | Small and large bowel regions; inspect species-specific segments for detail. |
| `jejunum` | `digestive` | `organ_or_structure` | Absorptive small-intestinal segment in mammals. |
| `omasum` | `digestive` | `organ_or_structure` | Ruminant compartment with many folds for particle handling and fluid absorption. |
| `oral_cavity` | `digestive` | `organ_or_structure` | Ingestion, food handling, initial processing, and in some species vocal or defensive actions. |
| `pancreas_exocrine` | `digestive` | `organ_or_structure` | Provides digestive enzymes and bicarbonate through ducts in many vertebrates. |
| `proventriculus` | `digestive` | `organ_or_structure` | Glandular first stomach of birds, secreting digestive fluids before muscular grinding. |
| `rectum` | `digestive` | `organ_or_structure` | Stores waste before elimination in many mammals. |
| `reticulum` | `digestive` | `organ_or_structure` | Ruminant forestomach compartment that cooperates with the rumen in mixing and particle handling. |
| `rumen` | `digestive` | `organ_or_structure` | Major microbial fermentation chamber in ruminants. |
| `salivary_glands` | `digestive` | `organ_or_structure` | Lubricate food and provide enzymes or antimicrobial factors where present. |
| `small_intestine` | `digestive` | `organ_or_structure` | Major site of enzymatic digestion and nutrient absorption in mammals and many vertebrates. |
| `stomach` | `digestive` | `organ_or_structure` | Stores and processes ingested material; configuration ranges from simple chamber to specialised multi-compartment foregut. |
| `teeth` | `digestive` | `organ_or_structure` | Mechanical food processing and in some species prey capture or display. |
| `adrenal_glands` | `endocrine` | `organ_or_structure` | Stress, salt balance and metabolic response; arrangement varies across clades. |
| `endocrine_system` | `endocrine` | `organ_or_structure` | Integrated hormone regulation and feedback. |
| `hypothalamus` | `endocrine` | `organ_or_structure` | Links neural state with pituitary and homeostatic control. |
| `parathyroids` | `endocrine` | `organ_or_structure` | Regulate calcium/phosphate signalling in many vertebrates; anatomy varies by clade. |
| `pineal` | `endocrine` | `organ_or_structure` | Light-linked circadian signalling in many vertebrates. |
| `pituitary` | `endocrine` | `organ_or_structure` | Hormone control node under hypothalamic input in many vertebrates. |
| `thymus_endocrine` | `endocrine` | `organ_or_structure` | Immune development and endocrine signalling at a level that varies by species and age. |
| `thyroid` | `endocrine` | `organ_or_structure` | Regulates metabolism and development using thyroid hormones in many vertebrates. |
| `bone_marrow` | `hematopoietic` | `organ_or_structure` | Blood-cell production and marrow immune functions where present. |
| `platelets` | `hematopoietic` | `organ_or_structure` | Primary haemostatic plugs in mammals; other vertebrates generally use nucleated thrombocytes. |
| `red_blood_cells` | `hematopoietic` | `organ_or_structure` | Gas carrier cells in vertebrates; morphology and nucleus status vary by lineage. |
| `stem_cells` | `hematopoietic` | `organ_or_structure` | A broad model label for repair-capable cell populations; potency and tissue access must be defined by spell rules. |
| `cloacal_bursa` | `immune` | `organ_or_structure` | Bursa of Fabricius; avian lymphoid organ important in B-cell development, especially in young birds. |
| `immune_system` | `immune` | `organ_or_structure` | Integrated defensive cells, barriers, tissues, and signalling. |
| `thymus` | `immune` | `organ_or_structure` | T-cell development in many vertebrates, especially prominent in young life stages. |
| `tonsils` | `immune` | `organ_or_structure` | Mucosa-associated immune tissue near the entry to respiratory and digestive tracts in many mammals. |
| `white_blood_cells` | `immune` | `organ_or_structure` | Cellular defence, signalling, and tissue surveillance. |
| `cutaneous_glands` | `integumentary` | `organ_or_structure` | Species-specific secretions for cooling, scent, waterproofing, signalling, or defence. |
| `dermis` | `integumentary` | `organ_or_structure` | Structural and vascular support beneath the epidermal barrier. |
| `epidermis` | `integumentary` | `organ_or_structure` | External epithelial barrier and keratinisation/pigmentation interface. |
| `feather_follicles` | `integumentary` | `organ_or_structure` | Generate and anchor feathers in birds. |
| `feathers` | `integumentary` | `organ_or_structure` | Avian integumentary structures used for insulation, display, waterproofing, and flight control. |
| `hair` | `integumentary` | `organ_or_structure` | Hair coat for insulation, sensation, signalling, and protection in many mammals. |
| `hypodermis` | `integumentary` | `organ_or_structure` | Subcutaneous support, insulation, energy storage, and sliding plane. |
| `scale_armour` | `integumentary` | `organ_or_structure` | Fictional or taxon-specific hard dermal/epidermal defence covering. |
| `scales` | `integumentary` | `organ_or_structure` | Scale covering that protects the body and participates in water balance or locomotion depending on clade. |
| `skin` | `integumentary` | `organ_or_structure` | Protective outer organ; water barrier, sensation, immune interface, and thermoregulation. |
| `skin_cuticle` | `integumentary` | `organ_or_structure` | Moist exchange surface of earthworms, rather than a mammalian skin with hair and sweat glands. |
| `claws` | `locomotor` | `organ_or_structure` | Distal keratin structures for traction, defence, climbing, digging, or prey capture. |
| `earthworm_segment` | `locomotor` | `organ_or_structure` | Repeated body unit with septa, muscles, bristles and local nerve/excretory structures. |
| `fins` | `locomotor` | `organ_or_structure` | Aquatic propulsion/control surfaces in compatible species. |
| `tail` | `locomotor` | `organ_or_structure` | Balance, signalling, steering or locomotion; vertebrae and soft tissue differ by species. |
| `wings` | `locomotor` | `organ_or_structure` | Flight surfaces requiring skeletal support, muscle power, control surfaces and suitable respiratory/metabolic supply. |
| `lymph_nodes` | `lymphatic` | `organ_or_structure` | Filter lymph and provide organised sites for immune activation in many mammals. |
| `lymphatic_system` | `lymphatic` | `organ_or_structure` | Lymph fluid transport and immune-cell traffic. |
| `lymphatic_vessels` | `lymphatic` | `organ_or_structure` | Return interstitial fluid and transport immune cells and, in many vertebrates, absorbed lipids. |
| `spleen` | `lymphatic` | `organ_or_structure` | Filters circulating blood and supports immune and blood-cell functions; size and roles vary by species. |
| `aetheric_core` | `magical_specialisation` | `organ_or_structure` | Fiction-only organ analogue that couples a body to a magical resource or field. |
| `fire_sac` | `magical_specialisation` | `organ_or_structure` | Fiction-only organ concept for a dragon-like species; stores/mediates an explicitly magical breath effect. |
| `venom_gland` | `magical_specialisation` | `organ_or_structure` | Produces or stores venom/toxin in species that actually possess such an apparatus. |
| `liver` | `metabolic` | `organ_or_structure` | Processes nutrients, synthesises proteins, handles many toxins, produces bile in vertebrates. |
| `pancreas` | `metabolic` | `organ_or_structure` | Mixed exocrine digestive enzyme and endocrine hormone organ in many vertebrates. |
| `microbiome` | `microbiome` | `organ_or_structure` | Resident microbes affect fermentation, nutrient availability, barrier function and immune signalling. |
| `ruminant_microbiome` | `microbiome` | `organ_or_structure` | Fermentation microbes in the ruminant forestomach digest otherwise difficult plant material. |
| `fascia` | `muscular` | `organ_or_structure` | Connective-tissue planes that surround, separate, and transmit forces between structures. |
| `muscle_tissue` | `muscular` | `organ_or_structure` | Collective muscle tissue model; separate skeletal, cardiac and smooth variants in detailed profiles. |
| `skeletal_muscles` | `muscular` | `organ_or_structure` | Voluntary/locomotor muscle, with clade-specific fibre and attachment designs. |
| `tendons` | `muscular` | `organ_or_structure` | Transmit muscle force to skeletal or other structures. |
| `autonomic_nerves` | `nervous` | `organ_or_structure` | Automatic regulation of circulation, breathing and digestion. |
| `autonomic_nervous_system` | `nervous` | `organ_or_structure` | Regulates involuntary organ activity, including heart, smooth muscle, and glands. |
| `brain` | `nervous` | `organ_or_structure` | Integrates sensory input, movement, internal regulation, and higher processing. |
| `brainstem` | `nervous` | `organ_or_structure` | Core pathways and autonomic control; major respiratory and cardiovascular centres in mammals. |
| `cerebellum` | `nervous` | `organ_or_structure` | Movement timing, balance, error correction and motor learning. |
| `cerebral_ganglia` | `nervous` | `organ_or_structure` | Paired anterior ganglia coordinating sensory input and local nervous-system activity in the earthworm body plan; not a vertebrate brain. |
| `cerebrum` | `nervous` | `organ_or_structure` | Higher integration, perception, memory and voluntary action in many vertebrates. |
| `enteric_nervous_system` | `nervous` | `organ_or_structure` | Local neural networks coordinating gut motility, secretion and blood flow. |
| `meninges` | `nervous` | `organ_or_structure` | Protective membranes around central nervous structures. |
| `peripheral_nerves` | `nervous` | `organ_or_structure` | Carry sensory and motor signals between the central nervous system and tissues. |
| `spinal_cord` | `nervous` | `organ_or_structure` | Relays signals and coordinates reflexes between central processing and body. |
| `ventral_nerve_cord` | `nervous` | `organ_or_structure` | Segmented longitudinal nerve cord in annelids and many other invertebrates. |
| `bladder` | `renal` | `organ_or_structure` | Urine storage in species that possess a bladder. |
| `kidneys` | `renal` | `organ_or_structure` | Filter body fluid and regulate water, ions, acid/base balance and endocrine signals in vertebrates. |
| `nephridia` | `renal` | `organ_or_structure` | Segmental excretory and osmoregulatory tubules in annelids and some other invertebrates. |
| `nephrons` | `renal` | `organ_or_structure` | Filtering and selective-reabsorption units in vertebrate kidneys that possess nephrons. |
| `ureters` | `renal` | `organ_or_structure` | Transport urine or urine-like fluid from kidneys to storage/outlet structures. |
| `urethra` | `renal` | `organ_or_structure` | Outlet for urine; also part of reproductive pathway in many male mammals. |
| `urinary_bladder` | `renal` | `organ_or_structure` | Stores urine in species that possess a bladder. |
| `clitellum` | `reproductive` | `organ_or_structure` | Glandular band in earthworms and related annelids involved in cocoon production. |
| `cloacal_vent` | `reproductive` | `organ_or_structure` | External shared outlet for excretory and reproductive tracts in birds, reptiles and many other vertebrates. |
| `gonads` | `reproductive` | `organ_or_structure` | Produce gametes and reproductive hormones; paired or unpaired arrangement depends on species. |
| `mammary_glands` | `reproductive` | `organ_or_structure` | Milk production in mammals; development and functional status depend on sex, age and life stage. |
| `ovaries` | `reproductive` | `organ_or_structure` | Produce oocytes and hormones in many female vertebrates. |
| `reproductive_system` | `reproductive` | `organ_or_structure` | Integrated species-specific reproductive structures. |
| `reproductive_tract` | `reproductive` | `organ_or_structure` | Species-specific ducts, accessory glands and external structures for gamete transfer or egg laying. |
| `seminal_vesicles` | `reproductive` | `organ_or_structure` | Species-dependent reproductive accessory structures in some annelids and mammals; the same name does not imply identical anatomy. |
| `testes` | `reproductive` | `organ_or_structure` | Produce sperm and androgens in many male vertebrates. |
| `uterus` | `reproductive` | `organ_or_structure` | Supports embryo/fetal development in many placental mammals; form differs greatly by species. |
| `air_sacs` | `respiratory` | `organ_or_structure` | Thin-walled ventilatory bellows attached to avian lungs; most are not major gas-exchange surfaces. |
| `airway_mucosa` | `respiratory` | `organ_or_structure` | Mucus and cilia / analogous barriers in airway regions where present. |
| `alveoli` | `respiratory` | `organ_or_structure` | Microscopic gas-exchange units in mammalian lungs. |
| `bronchi` | `respiratory` | `organ_or_structure` | Conduct air into branching airway trees in mammalian and many other lungs. |
| `bronchioles` | `respiratory` | `organ_or_structure` | Small conducting airways that regulate airflow in lungs with branching bronchioles. |
| `diaphragm` | `respiratory` | `organ_or_structure` | Major inspiratory muscle in mammals; absent as a true muscular diaphragm in birds and most reptiles. |
| `gills` | `respiratory` | `organ_or_structure` | Water-to-blood gas-exchange structures in fish and some aquatic or larval forms. |
| `larynx` | `respiratory` | `organ_or_structure` | Airway protection and vocal production in many mammals. |
| `lungs` | `respiratory` | `organ_or_structure` | Gas-exchange organs; internal architecture differs across mammals, birds and reptiles. |
| `nasal_cavity` | `respiratory` | `organ_or_structure` | Filters, warms, humidifies and samples inhaled air; may contain specialised scent structures. |
| `pharynx` | `respiratory` | `organ_or_structure` | Shared passage at the crossroads of respiratory and digestive pathways in many vertebrates. |
| `serpentine_lung` | `respiratory` | `organ_or_structure` | Elongated, species-dependent lung arrangement in snakes; often one dominant functional lung. |
| `spiracles` | `respiratory` | `organ_or_structure` | External openings in insect tracheal breathing systems; relevant if custom invertebrates are defined. |
| `trachea` | `respiratory` | `organ_or_structure` | Conducts and conditions air between upper airway and branching lungs where present. |
| `ears` | `sensory` | `organ_or_structure` | Receive sound; in many mammals include external pinna, middle ear, and inner ear. |
| `eyes` | `sensory` | `organ_or_structure` | Capture and process light; arrangement varies by ecological niche. |
| `inner_ear` | `sensory` | `organ_or_structure` | Balance, acceleration sensing, and (in vertebrates) part of hearing. |
| `nasal_discus` | `sensory` | `organ_or_structure` | Specialised tactile/rhinarium structure in pigs and some other mammals for rooting and close contact. |
| `olfactory_bulbs` | `sensory` | `organ_or_structure` | Initial central processing for olfactory signals where present. |
| `olfactory_epithelium` | `sensory` | `organ_or_structure` | Chemical detection for smell; can connect with specialised vomeronasal systems. |
| `tongue` | `sensory` | `organ_or_structure` | Manipulates food and contributes to taste, feeding, grooming, or specialised functions. |
| `vibrissae` | `sensory` | `organ_or_structure` | Specialised tactile hairs that report nearby surfaces and air movement in many mammals. |
| `vomeronasal_organ` | `sensory` | `organ_or_structure` | Accessory chemical-sensing organ in many reptiles and some mammals. |
| `atlas_c1` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the vertebral column region. (region: axial; group: vertebral_column). |
| `axis_c2` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the vertebral column region. (region: axial; group: vertebral_column). |
| `beak` | `skeletal` | `organ_or_structure` | Keratin-covered jaw structures in birds and other beaked animals; shape is diet-specific. |
| `beak_bones` | `skeletal` | `skeletal_structure` | Species-specific or homologous skeletal structure 'beak bones'. |
| `bones` | `skeletal` | `organ_or_structure` | Individual rigid skeletal elements; details are listed by region in anatomy.bones(). |
| `carpal_bones` | `skeletal` | `skeletal_structure` | Species-specific or homologous skeletal structure 'carpal bones'. |
| `carpometacarpus_left` | `skeletal` | `skeletal_structure` | Species-specific or homologous skeletal structure 'carpometacarpus left'. |
| `carpometacarpus_right` | `skeletal` | `skeletal_structure` | Species-specific or homologous skeletal structure 'carpometacarpus right'. |
| `cartilage` | `skeletal` | `organ_or_structure` | Resilient support and low-friction joint surfaces. |
| `caudal_vertebrae` | `skeletal` | `skeletal_structure` | Species-specific or homologous skeletal structure 'caudal vertebrae'. |
| `cervical_c3` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the vertebral column region. (region: axial; group: vertebral_column). |
| `cervical_c4` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the vertebral column region. (region: axial; group: vertebral_column). |
| `cervical_c5` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the vertebral column region. (region: axial; group: vertebral_column). |
| `cervical_c6` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the vertebral column region. (region: axial; group: vertebral_column). |
| `cervical_c7` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the vertebral column region. (region: axial; group: vertebral_column). |
| `cervical_vertebrae` | `skeletal` | `skeletal_structure` | Species-specific or homologous skeletal structure 'cervical vertebrae'. |
| `coccyx` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the vertebral column region. (region: axial; group: vertebral_column). |
| `coelom` | `skeletal` | `organ_or_structure` | Fluid-filled body cavity compartment that supports hydrostatic movement in annelids and other invertebrates. |
| `connective_tissue` | `skeletal` | `organ_or_structure` | Matrix-rich tissue joining, separating, supporting or cushioning structures. |
| `designer_defined_fused_bones` | `skeletal` | `skeletal_structure` | Species-specific or homologous skeletal structure 'designer defined fused bones'. |
| `ethmoid` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the cranial bones region. (region: axial; group: cranial_bones). |
| `fangs` | `skeletal` | `organ_or_structure` | Specialised teeth or tooth analogues used for prey capture, defence or venom delivery. |
| `fantasy_specialised_skeleton` | `skeletal` | `skeletal_structure` | Species-specific or homologous skeletal structure 'fantasy specialised skeleton'. |
| `foot_phalanges` | `skeletal` | `skeletal_structure` | Species-specific or homologous skeletal structure 'foot phalanges'. |
| `forelimb_phalanges` | `skeletal` | `skeletal_structure` | Species-specific or homologous skeletal structure 'forelimb phalanges'. |
| `frontal` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the cranial bones region. (region: axial; group: cranial_bones). |
| `furcula` | `skeletal` | `skeletal_structure` | Species-specific or homologous skeletal structure 'furcula'. |
| `furculum_and_keel_attachments` | `skeletal` | `skeletal_structure` | Species-specific or homologous skeletal structure 'furculum and keel attachments'. |
| `hallux` | `skeletal` | `skeletal_structure` | Species-specific or homologous skeletal structure 'hallux'. |
| `hindlimb_phalanges` | `skeletal` | `skeletal_structure` | Species-specific or homologous skeletal structure 'hindlimb phalanges'. |
| `hydrostatic_skeleton` | `skeletal` | `organ_or_structure` | Support produced by pressurised fluid compartments and body-wall muscles rather than bones. |
| `hyoid` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the hyoid region. (region: axial; group: hyoid). |
| `hyoid_apparatus` | `skeletal` | `skeletal_structure` | Species-specific or homologous skeletal structure 'hyoid apparatus'. |
| `ilium` | `skeletal` | `skeletal_structure` | Species-specific or homologous skeletal structure 'ilium'. |
| `intervertebral_articulations` | `skeletal` | `skeletal_structure` | Species-specific or homologous skeletal structure 'intervertebral articulations'. |
| `ischium` | `skeletal` | `skeletal_structure` | Species-specific or homologous skeletal structure 'ischium'. |
| `jaw_teeth_support` | `skeletal` | `skeletal_structure` | Species-specific or homologous skeletal structure 'jaw teeth support'. |
| `joints` | `skeletal` | `organ_or_structure` | Articulations enabling motion or stable load transfer. |
| `keel` | `skeletal` | `organ_or_structure` | Projecting sternum ridge anchoring major flight muscles in many flying birds. |
| `left_calcaneus` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the lower limbs region. (region: appendicular; group: lower_limbs). |
| `left_capitate` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the upper limbs region. (region: appendicular; group: upper_limbs). |
| `left_clavicle` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the pectoral girdle region. (region: appendicular; group: pectoral_girdle). |
| `left_coracoid` | `skeletal` | `skeletal_structure` | Species-specific or homologous skeletal structure 'left coracoid'. |
| `left_cuboid` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the lower limbs region. (region: appendicular; group: lower_limbs). |
| `left_femur` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the lower limbs region. (region: appendicular; group: lower_limbs). |
| `left_fibula` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the lower limbs region. (region: appendicular; group: lower_limbs). |
| `left_fibula_reduced` | `skeletal` | `skeletal_structure` | Species-specific or homologous skeletal structure 'left fibula reduced'. |
| `left_fourth_toe_distal_phalanx` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the lower limbs region. (region: appendicular; group: lower_limbs). |
| `left_fourth_toe_middle_phalanx` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the lower limbs region. (region: appendicular; group: lower_limbs). |
| `left_fourth_toe_proximal_phalanx` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the lower limbs region. (region: appendicular; group: lower_limbs). |
| `left_great_toe_distal_phalanx` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the lower limbs region. (region: appendicular; group: lower_limbs). |
| `left_great_toe_proximal_phalanx` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the lower limbs region. (region: appendicular; group: lower_limbs). |
| `left_hamate` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the upper limbs region. (region: appendicular; group: upper_limbs). |
| `left_hip_bone` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the pelvic girdle region. (region: appendicular; group: pelvic_girdle). |
| `left_humerus` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the upper limbs region. (region: appendicular; group: upper_limbs). |
| `left_incus` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the auditory ossicles region. (region: axial; group: auditory_ossicles). |
| `left_index_distal_phalanx` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the upper limbs region. (region: appendicular; group: upper_limbs). |
| `left_index_middle_phalanx` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the upper limbs region. (region: appendicular; group: upper_limbs). |
| `left_index_proximal_phalanx` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the upper limbs region. (region: appendicular; group: upper_limbs). |
| `left_inferior_nasal_concha` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the facial bones region. (region: axial; group: facial_bones). |
| `left_intermediate_cuneiform` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the lower limbs region. (region: appendicular; group: lower_limbs). |
| `left_lacrimal` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the facial bones region. (region: axial; group: facial_bones). |
| `left_lateral_cuneiform` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the lower limbs region. (region: appendicular; group: lower_limbs). |
| `left_little_distal_phalanx` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the upper limbs region. (region: appendicular; group: upper_limbs). |
| `left_little_middle_phalanx` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the upper limbs region. (region: appendicular; group: upper_limbs). |
| `left_little_proximal_phalanx` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the upper limbs region. (region: appendicular; group: upper_limbs). |
| `left_little_toe_distal_phalanx` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the lower limbs region. (region: appendicular; group: lower_limbs). |
| `left_little_toe_middle_phalanx` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the lower limbs region. (region: appendicular; group: lower_limbs). |
| `left_little_toe_proximal_phalanx` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the lower limbs region. (region: appendicular; group: lower_limbs). |
| `left_lunate` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the upper limbs region. (region: appendicular; group: upper_limbs). |
| `left_malleus` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the auditory ossicles region. (region: axial; group: auditory_ossicles). |
| `left_maxilla` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the facial bones region. (region: axial; group: facial_bones). |
| `left_medial_cuneiform` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the lower limbs region. (region: appendicular; group: lower_limbs). |
| `left_metacarpal_1` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the upper limbs region. (region: appendicular; group: upper_limbs). |
| `left_metacarpal_2` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the upper limbs region. (region: appendicular; group: upper_limbs). |
| `left_metacarpal_3` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the upper limbs region. (region: appendicular; group: upper_limbs). |
| `left_metacarpal_4` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the upper limbs region. (region: appendicular; group: upper_limbs). |
| `left_metacarpal_5` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the upper limbs region. (region: appendicular; group: upper_limbs). |
| `left_metatarsal_1` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the lower limbs region. (region: appendicular; group: lower_limbs). |
| `left_metatarsal_2` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the lower limbs region. (region: appendicular; group: lower_limbs). |
| `left_metatarsal_3` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the lower limbs region. (region: appendicular; group: lower_limbs). |
| `left_metatarsal_4` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the lower limbs region. (region: appendicular; group: lower_limbs). |
| `left_metatarsal_5` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the lower limbs region. (region: appendicular; group: lower_limbs). |
| `left_middle_distal_phalanx` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the upper limbs region. (region: appendicular; group: upper_limbs). |
| `left_middle_middle_phalanx` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the upper limbs region. (region: appendicular; group: upper_limbs). |
| `left_middle_proximal_phalanx` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the upper limbs region. (region: appendicular; group: upper_limbs). |
| `left_nasal` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the facial bones region. (region: axial; group: facial_bones). |
| `left_navicular` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the lower limbs region. (region: appendicular; group: lower_limbs). |
| `left_palatine` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the facial bones region. (region: axial; group: facial_bones). |
| `left_parietal` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the cranial bones region. (region: axial; group: cranial_bones). |
| `left_patella` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the lower limbs region. (region: appendicular; group: lower_limbs). |
| `left_pisiform` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the upper limbs region. (region: appendicular; group: upper_limbs). |
| `left_radius` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the upper limbs region. (region: appendicular; group: upper_limbs). |
| `left_rib_1` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the thoracic cage region. (region: axial; group: thoracic_cage). |
| `left_rib_10` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the thoracic cage region. (region: axial; group: thoracic_cage). |
| `left_rib_11` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the thoracic cage region. (region: axial; group: thoracic_cage). |
| `left_rib_12` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the thoracic cage region. (region: axial; group: thoracic_cage). |
| `left_rib_2` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the thoracic cage region. (region: axial; group: thoracic_cage). |
| `left_rib_3` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the thoracic cage region. (region: axial; group: thoracic_cage). |
| `left_rib_4` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the thoracic cage region. (region: axial; group: thoracic_cage). |
| `left_rib_5` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the thoracic cage region. (region: axial; group: thoracic_cage). |
| `left_rib_6` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the thoracic cage region. (region: axial; group: thoracic_cage). |
| `left_rib_7` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the thoracic cage region. (region: axial; group: thoracic_cage). |
| `left_rib_8` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the thoracic cage region. (region: axial; group: thoracic_cage). |
| `left_rib_9` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the thoracic cage region. (region: axial; group: thoracic_cage). |
| `left_ring_distal_phalanx` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the upper limbs region. (region: appendicular; group: upper_limbs). |
| `left_ring_middle_phalanx` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the upper limbs region. (region: appendicular; group: upper_limbs). |
| `left_ring_proximal_phalanx` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the upper limbs region. (region: appendicular; group: upper_limbs). |
| `left_scaphoid` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the upper limbs region. (region: appendicular; group: upper_limbs). |
| `left_scapula` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the pectoral girdle region. (region: appendicular; group: pectoral_girdle). |
| `left_second_toe_distal_phalanx` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the lower limbs region. (region: appendicular; group: lower_limbs). |
| `left_second_toe_middle_phalanx` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the lower limbs region. (region: appendicular; group: lower_limbs). |
| `left_second_toe_proximal_phalanx` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the lower limbs region. (region: appendicular; group: lower_limbs). |
| `left_stapes` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the auditory ossicles region. (region: axial; group: auditory_ossicles). |
| `left_talus` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the lower limbs region. (region: appendicular; group: lower_limbs). |
| `left_tarsometatarsus` | `skeletal` | `skeletal_structure` | Species-specific or homologous skeletal structure 'left tarsometatarsus'. |
| `left_temporal` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the cranial bones region. (region: axial; group: cranial_bones). |
| `left_third_toe_distal_phalanx` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the lower limbs region. (region: appendicular; group: lower_limbs). |
| `left_third_toe_middle_phalanx` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the lower limbs region. (region: appendicular; group: lower_limbs). |
| `left_third_toe_proximal_phalanx` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the lower limbs region. (region: appendicular; group: lower_limbs). |
| `left_thumb_distal_phalanx` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the upper limbs region. (region: appendicular; group: upper_limbs). |
| `left_thumb_proximal_phalanx` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the upper limbs region. (region: appendicular; group: upper_limbs). |
| `left_tibia` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the lower limbs region. (region: appendicular; group: lower_limbs). |
| `left_tibiotarsus` | `skeletal` | `skeletal_structure` | Species-specific or homologous skeletal structure 'left tibiotarsus'. |
| `left_trapezium` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the upper limbs region. (region: appendicular; group: upper_limbs). |
| `left_trapezoid` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the upper limbs region. (region: appendicular; group: upper_limbs). |
| `left_triquetrum` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the upper limbs region. (region: appendicular; group: upper_limbs). |
| `left_ulna` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the upper limbs region. (region: appendicular; group: upper_limbs). |
| `left_zygomatic` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the facial bones region. (region: axial; group: facial_bones). |
| `ligaments` | `skeletal` | `organ_or_structure` | Constrain and stabilise movement between skeletal elements. |
| `lumbar_l1` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the vertebral column region. (region: axial; group: vertebral_column). |
| `lumbar_l2` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the vertebral column region. (region: axial; group: vertebral_column). |
| `lumbar_l3` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the vertebral column region. (region: axial; group: vertebral_column). |
| `lumbar_l4` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the vertebral column region. (region: axial; group: vertebral_column). |
| `lumbar_l5` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the vertebral column region. (region: axial; group: vertebral_column). |
| `lumbar_vertebrae` | `skeletal` | `skeletal_structure` | Species-specific or homologous skeletal structure 'lumbar vertebrae'. |
| `mandible` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the facial bones region. (region: axial; group: facial_bones). |
| `maxilla` | `skeletal` | `skeletal_structure` | Species-specific or homologous skeletal structure 'maxilla'. |
| `metacarpal_bones` | `skeletal` | `skeletal_structure` | Species-specific or homologous skeletal structure 'metacarpal bones'. |
| `metatarsal_bones` | `skeletal` | `skeletal_structure` | Species-specific or homologous skeletal structure 'metatarsal bones'. |
| `occipital` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the cranial bones region. (region: axial; group: cranial_bones). |
| `ossicones` | `skeletal` | `organ_or_structure` | Giraffe-specific bony/cartilaginous head projections covered by skin and hair. |
| `pelvic_vestiges_optional` | `skeletal` | `skeletal_structure` | Species-specific or homologous skeletal structure 'pelvic vestiges optional'. |
| `pelvis` | `skeletal` | `skeletal_structure` | Species-specific or homologous skeletal structure 'pelvis'. |
| `pneumatic_bones` | `skeletal` | `organ_or_structure` | Bones invaded by air-sac diverticula in some birds and some other vertebrates, reducing mass or contributing to air spaces. |
| `premaxilla` | `skeletal` | `skeletal_structure` | Species-specific or homologous skeletal structure 'premaxilla'. |
| `pterygoid_bones` | `skeletal` | `skeletal_structure` | Species-specific or homologous skeletal structure 'pterygoid bones'. |
| `pubis` | `skeletal` | `skeletal_structure` | Species-specific or homologous skeletal structure 'pubis'. |
| `pygostyle` | `skeletal` | `skeletal_structure` | Species-specific or homologous skeletal structure 'pygostyle'. |
| `quadrate_bones` | `skeletal` | `skeletal_structure` | Species-specific or homologous skeletal structure 'quadrate bones'. |
| `rib_pairs` | `skeletal` | `skeletal_structure` | Species-specific or homologous skeletal structure 'rib pairs'. |
| `ribs` | `skeletal` | `organ_or_structure` | Protect thoracic organs and, where present, assist breathing mechanics. |
| `right_calcaneus` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the lower limbs region. (region: appendicular; group: lower_limbs). |
| `right_capitate` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the upper limbs region. (region: appendicular; group: upper_limbs). |
| `right_clavicle` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the pectoral girdle region. (region: appendicular; group: pectoral_girdle). |
| `right_coracoid` | `skeletal` | `skeletal_structure` | Species-specific or homologous skeletal structure 'right coracoid'. |
| `right_cuboid` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the lower limbs region. (region: appendicular; group: lower_limbs). |
| `right_femur` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the lower limbs region. (region: appendicular; group: lower_limbs). |
| `right_fibula` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the lower limbs region. (region: appendicular; group: lower_limbs). |
| `right_fibula_reduced` | `skeletal` | `skeletal_structure` | Species-specific or homologous skeletal structure 'right fibula reduced'. |
| `right_fourth_toe_distal_phalanx` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the lower limbs region. (region: appendicular; group: lower_limbs). |
| `right_fourth_toe_middle_phalanx` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the lower limbs region. (region: appendicular; group: lower_limbs). |
| `right_fourth_toe_proximal_phalanx` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the lower limbs region. (region: appendicular; group: lower_limbs). |
| `right_great_toe_distal_phalanx` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the lower limbs region. (region: appendicular; group: lower_limbs). |
| `right_great_toe_proximal_phalanx` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the lower limbs region. (region: appendicular; group: lower_limbs). |
| `right_hamate` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the upper limbs region. (region: appendicular; group: upper_limbs). |
| `right_hip_bone` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the pelvic girdle region. (region: appendicular; group: pelvic_girdle). |
| `right_humerus` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the upper limbs region. (region: appendicular; group: upper_limbs). |
| `right_incus` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the auditory ossicles region. (region: axial; group: auditory_ossicles). |
| `right_index_distal_phalanx` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the upper limbs region. (region: appendicular; group: upper_limbs). |
| `right_index_middle_phalanx` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the upper limbs region. (region: appendicular; group: upper_limbs). |
| `right_index_proximal_phalanx` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the upper limbs region. (region: appendicular; group: upper_limbs). |
| `right_inferior_nasal_concha` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the facial bones region. (region: axial; group: facial_bones). |
| `right_intermediate_cuneiform` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the lower limbs region. (region: appendicular; group: lower_limbs). |
| `right_lacrimal` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the facial bones region. (region: axial; group: facial_bones). |
| `right_lateral_cuneiform` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the lower limbs region. (region: appendicular; group: lower_limbs). |
| `right_little_distal_phalanx` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the upper limbs region. (region: appendicular; group: upper_limbs). |
| `right_little_middle_phalanx` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the upper limbs region. (region: appendicular; group: upper_limbs). |
| `right_little_proximal_phalanx` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the upper limbs region. (region: appendicular; group: upper_limbs). |
| `right_little_toe_distal_phalanx` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the lower limbs region. (region: appendicular; group: lower_limbs). |
| `right_little_toe_middle_phalanx` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the lower limbs region. (region: appendicular; group: lower_limbs). |
| `right_little_toe_proximal_phalanx` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the lower limbs region. (region: appendicular; group: lower_limbs). |
| `right_lunate` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the upper limbs region. (region: appendicular; group: upper_limbs). |
| `right_malleus` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the auditory ossicles region. (region: axial; group: auditory_ossicles). |
| `right_maxilla` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the facial bones region. (region: axial; group: facial_bones). |
| `right_medial_cuneiform` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the lower limbs region. (region: appendicular; group: lower_limbs). |
| `right_metacarpal_1` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the upper limbs region. (region: appendicular; group: upper_limbs). |
| `right_metacarpal_2` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the upper limbs region. (region: appendicular; group: upper_limbs). |
| `right_metacarpal_3` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the upper limbs region. (region: appendicular; group: upper_limbs). |
| `right_metacarpal_4` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the upper limbs region. (region: appendicular; group: upper_limbs). |
| `right_metacarpal_5` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the upper limbs region. (region: appendicular; group: upper_limbs). |
| `right_metatarsal_1` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the lower limbs region. (region: appendicular; group: lower_limbs). |
| `right_metatarsal_2` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the lower limbs region. (region: appendicular; group: lower_limbs). |
| `right_metatarsal_3` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the lower limbs region. (region: appendicular; group: lower_limbs). |
| `right_metatarsal_4` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the lower limbs region. (region: appendicular; group: lower_limbs). |
| `right_metatarsal_5` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the lower limbs region. (region: appendicular; group: lower_limbs). |
| `right_middle_distal_phalanx` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the upper limbs region. (region: appendicular; group: upper_limbs). |
| `right_middle_middle_phalanx` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the upper limbs region. (region: appendicular; group: upper_limbs). |
| `right_middle_proximal_phalanx` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the upper limbs region. (region: appendicular; group: upper_limbs). |
| `right_nasal` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the facial bones region. (region: axial; group: facial_bones). |
| `right_navicular` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the lower limbs region. (region: appendicular; group: lower_limbs). |
| `right_palatine` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the facial bones region. (region: axial; group: facial_bones). |
| `right_parietal` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the cranial bones region. (region: axial; group: cranial_bones). |
| `right_patella` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the lower limbs region. (region: appendicular; group: lower_limbs). |
| `right_pisiform` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the upper limbs region. (region: appendicular; group: upper_limbs). |
| `right_radius` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the upper limbs region. (region: appendicular; group: upper_limbs). |
| `right_rib_1` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the thoracic cage region. (region: axial; group: thoracic_cage). |
| `right_rib_10` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the thoracic cage region. (region: axial; group: thoracic_cage). |
| `right_rib_11` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the thoracic cage region. (region: axial; group: thoracic_cage). |
| `right_rib_12` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the thoracic cage region. (region: axial; group: thoracic_cage). |
| `right_rib_2` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the thoracic cage region. (region: axial; group: thoracic_cage). |
| `right_rib_3` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the thoracic cage region. (region: axial; group: thoracic_cage). |
| `right_rib_4` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the thoracic cage region. (region: axial; group: thoracic_cage). |
| `right_rib_5` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the thoracic cage region. (region: axial; group: thoracic_cage). |
| `right_rib_6` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the thoracic cage region. (region: axial; group: thoracic_cage). |
| `right_rib_7` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the thoracic cage region. (region: axial; group: thoracic_cage). |
| `right_rib_8` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the thoracic cage region. (region: axial; group: thoracic_cage). |
| `right_rib_9` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the thoracic cage region. (region: axial; group: thoracic_cage). |
| `right_ring_distal_phalanx` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the upper limbs region. (region: appendicular; group: upper_limbs). |
| `right_ring_middle_phalanx` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the upper limbs region. (region: appendicular; group: upper_limbs). |
| `right_ring_proximal_phalanx` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the upper limbs region. (region: appendicular; group: upper_limbs). |
| `right_scaphoid` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the upper limbs region. (region: appendicular; group: upper_limbs). |
| `right_scapula` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the pectoral girdle region. (region: appendicular; group: pectoral_girdle). |
| `right_second_toe_distal_phalanx` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the lower limbs region. (region: appendicular; group: lower_limbs). |
| `right_second_toe_middle_phalanx` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the lower limbs region. (region: appendicular; group: lower_limbs). |
| `right_second_toe_proximal_phalanx` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the lower limbs region. (region: appendicular; group: lower_limbs). |
| `right_stapes` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the auditory ossicles region. (region: axial; group: auditory_ossicles). |
| `right_talus` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the lower limbs region. (region: appendicular; group: lower_limbs). |
| `right_tarsometatarsus` | `skeletal` | `skeletal_structure` | Species-specific or homologous skeletal structure 'right tarsometatarsus'. |
| `right_temporal` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the cranial bones region. (region: axial; group: cranial_bones). |
| `right_third_toe_distal_phalanx` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the lower limbs region. (region: appendicular; group: lower_limbs). |
| `right_third_toe_middle_phalanx` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the lower limbs region. (region: appendicular; group: lower_limbs). |
| `right_third_toe_proximal_phalanx` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the lower limbs region. (region: appendicular; group: lower_limbs). |
| `right_thumb_distal_phalanx` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the upper limbs region. (region: appendicular; group: upper_limbs). |
| `right_thumb_proximal_phalanx` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the upper limbs region. (region: appendicular; group: upper_limbs). |
| `right_tibia` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the lower limbs region. (region: appendicular; group: lower_limbs). |
| `right_tibiotarsus` | `skeletal` | `skeletal_structure` | Species-specific or homologous skeletal structure 'right tibiotarsus'. |
| `right_trapezium` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the upper limbs region. (region: appendicular; group: upper_limbs). |
| `right_trapezoid` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the upper limbs region. (region: appendicular; group: upper_limbs). |
| `right_triquetrum` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the upper limbs region. (region: appendicular; group: upper_limbs). |
| `right_ulna` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the upper limbs region. (region: appendicular; group: upper_limbs). |
| `right_zygomatic` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the facial bones region. (region: axial; group: facial_bones). |
| `sacrum` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the vertebral column region. (region: axial; group: vertebral_column). |
| `sesamoid_bones` | `skeletal` | `skeletal_structure` | Species-specific or homologous skeletal structure 'sesamoid bones'. |
| `skeleton` | `skeletal` | `organ_or_structure` | Whole-body framework: bone, cartilage or hydrostatic support depending on species. |
| `skull` | `skeletal` | `organ_or_structure` | Protects the brain and supports sensory and feeding structures. |
| `sphenoid` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the cranial bones region. (region: axial; group: cranial_bones). |
| `sternal_keel` | `skeletal` | `skeletal_structure` | Species-specific or homologous skeletal structure 'sternal keel'. |
| `sternum` | `skeletal` | `organ_or_structure` | Ventral thoracic support and muscle attachment; a pronounced keel anchors flight muscles in many birds. |
| `synsacrum` | `skeletal` | `skeletal_structure` | Species-specific or homologous skeletal structure 'synsacrum'. |
| `tarsal_bones` | `skeletal` | `skeletal_structure` | Species-specific or homologous skeletal structure 'tarsal bones'. |
| `thoracic_t1` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the vertebral column region. (region: axial; group: vertebral_column). |
| `thoracic_t10` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the vertebral column region. (region: axial; group: vertebral_column). |
| `thoracic_t11` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the vertebral column region. (region: axial; group: vertebral_column). |
| `thoracic_t12` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the vertebral column region. (region: axial; group: vertebral_column). |
| `thoracic_t2` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the vertebral column region. (region: axial; group: vertebral_column). |
| `thoracic_t3` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the vertebral column region. (region: axial; group: vertebral_column). |
| `thoracic_t4` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the vertebral column region. (region: axial; group: vertebral_column). |
| `thoracic_t5` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the vertebral column region. (region: axial; group: vertebral_column). |
| `thoracic_t6` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the vertebral column region. (region: axial; group: vertebral_column). |
| `thoracic_t7` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the vertebral column region. (region: axial; group: vertebral_column). |
| `thoracic_t8` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the vertebral column region. (region: axial; group: vertebral_column). |
| `thoracic_t9` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the vertebral column region. (region: axial; group: vertebral_column). |
| `thoracic_vertebrae` | `skeletal` | `skeletal_structure` | Species-specific or homologous skeletal structure 'thoracic vertebrae'. |
| `trunk_vertebrae` | `skeletal` | `skeletal_structure` | Species-specific or homologous skeletal structure 'trunk vertebrae'. |
| `tusks` | `skeletal` | `organ_or_structure` | Enlarged teeth used in defence, digging, display or food acquisition in certain animals. |
| `uncinate_processes` | `skeletal` | `skeletal_structure` | Species-specific or homologous skeletal structure 'uncinate processes'. |
| `vertebral_column` | `skeletal` | `organ_or_structure` | Protects the main nerve cord and anchors ribs and locomotor musculature. |
| `vomer` | `skeletal` | `individual_bone` | Individually addressable human skeletal element in the facial bones region. (region: axial; group: facial_bones). |
| `wing_phalanges` | `skeletal` | `skeletal_structure` | Species-specific or homologous skeletal structure 'wing phalanges'. |
| `zygapophyses` | `skeletal` | `skeletal_structure` | Species-specific or homologous skeletal structure 'zygapophyses'. |

### A4. Tissue reference catalogue

Tissues are reusable descriptive classes. A tissue label can be attached to a custom organ, but the library does not simulate every fibre, extracellular-matrix component, vascular bed or cell division.

| Tissue family | Role | Subtypes represented in the reference |
|---|---|---|
| `epithelial` | covers external and internal surfaces; forms glands and exchange barriers | simple squamous, simple cuboidal, simple columnar, pseudostratified columnar, stratified squamous, transitional, glandular |
| `connective` | supports, connects, separates, stores energy and transmits force | loose connective, dense regular, dense irregular, adipose, reticular, elastic, cartilage, bone, blood |
| `skeletal_muscle` | voluntary force generation and posture in vertebrate skeletal muscles | slow oxidative, fast oxidative-glycolytic, fast glycolytic, tendon junction, motor unit |
| `cardiac_muscle` | rhythmic contraction of a vertebrate heart | cardiomyocytes, intercalated discs, conduction tissue |
| `smooth_muscle` | involuntary contraction in vessels, airway, gut and other hollow structures | visceral, multi-unit, vascular smooth muscle |
| `nervous` | signal generation, transmission and support | neurons, astrocytes, oligodendrocytes or clade analogues, microglia or immune analogues, Schwann cells or peripheral glia |
| `blood` | circulating transport and defence tissue; cellular composition varies by lineage | plasma, erythrocytes or oxygen carriers, leukocytes or immune cells, platelets/thrombocytes or clotting analogues |
| `lymphoid` | immune surveillance, cell maturation and immune-cell traffic | lymphocytes, antigen-presenting cells, stromal cells, lymph |
| `bone_marrow` | blood-cell production and marrow niches in many vertebrates | hematopoietic stem/progenitor cells, myeloid lineages, lymphoid lineages, stromal cells, vascular sinusoids, fatty marrow |
| `cartilage` | resilient flexible support and low-friction bearing surfaces | hyaline, elastic, fibrocartilage |
| `keratinised` | tough external or distal appendage structures | hair, feather, claw/nail, hoof, beak, scale sheath |
| `cuticle` | external non-vertebrate body covering; composition depends on clade | epidermis, secreted surface matrix, sensory openings |
| `germinal` | reproduction and lineage continuity | germ cells, supporting gonadal cells, reproductive ducts or clade-specific equivalents |
| `fluid_compartment` | fluid-filled spaces which support exchange, pressure or hydrostatic mechanics | interstitial fluid, coelomic fluid, lymph, serous fluid, synovial fluid |

### A5. Cell-type reference catalogue

Cell types are abstract reference records. MANA does not allocate one object per cell and does not implement a cellular or molecular simulation by default.

| Cell type | System | Role |
|---|---|---|
| `erythrocyte` | `circulatory` | oxygen and carbon-dioxide transport in many vertebrates; mature mammalian examples are anucleate |
| `leukocyte` | `immune` | umbrella label for immune cells; subdivide into species-appropriate lineages for detailed simulation |
| `thrombocyte` | `circulatory` | nucleated clotting cell in birds, reptiles and many non-mammalian vertebrates |
| `platelet` | `circulatory` | small anucleate clotting fragment in mammals |
| `neuron` | `nervous` | electrical and chemical signalling cell |
| `astrocyte` | `nervous` | central nervous-system support, homeostasis and neurovascular coupling in mammals |
| `oligodendrocyte` | `nervous` | myelination of central nervous-system axons in mammals |
| `schwann_cell` | `nervous` | support and myelination of many peripheral axons in vertebrates |
| `cardiomyocyte` | `circulatory` | contractile heart-muscle cell |
| `smooth_muscle_cell` | `muscular` | involuntary contraction in hollow organs and vessels |
| `skeletal_muscle_fibre` | `muscular` | multinucleate contractile fibre in typical vertebrate skeletal muscle |
| `osteoblast` | `skeletal` | bone-matrix formation |
| `osteocyte` | `skeletal` | mature embedded bone cell involved in maintenance and load sensing |
| `osteoclast` | `skeletal` | bone resorption and remodeling |
| `chondrocyte` | `skeletal` | cartilage matrix maintenance |
| `keratinocyte` | `integumentary` | main epidermal cell; forms barrier keratin in mammals |
| `melanocyte` | `integumentary` | pigment production and transfer in many vertebrates |
| `adipocyte` | `metabolic` | energy storage, insulation and endocrine signalling |
| `hepatocyte` | `metabolic` | major liver cell responsible for many synthetic, metabolic and detoxification tasks |
| `podocyte` | `renal` | specialised filtration-barrier cell in vertebrate kidney glomeruli |
| `enterocyte` | `digestive` | intestinal epithelial absorption cell |
| `goblet_cell` | `digestive` | mucus-secreting epithelial cell at many mucosal surfaces |
| `pancreatic_beta_cell` | `endocrine` | insulin-secreting cell in mammalian pancreatic islets |
| `fibroblast` | `connective` | extracellular matrix production and repair |
| `endothelial_cell` | `circulatory` | lining cell of blood and lymphatic vessels |
| `macrophage` | `immune` | phagocytosis, innate defence and tissue signalling; biology varies by lineage |
| `mast_cell` | `immune` | tissue immune signalling and mediator release in many vertebrates |
| `earthworm_coelomocyte` | `immune` | invertebrate coelomic immune cell analogue; categories vary among annelids |
| `earthworm_epidermal_cell` | `integumentary` | surface cell involved in a moist cuticle interface and gas exchange |

### A6. Blood, fluids, and circulation: what the model means

The reference distinguishes circulating blood, plasma, red-cell/oxygen-carrier records, immune cells, clotting components, lymph and coelomic fluid. Mammalian mature erythrocytes are usually anucleate, while birds and reptiles have nucleated erythrocytes; the catalogue therefore does not force one blood-cell profile onto all lineages. These records are useful for target selection, state variables and spell rules, but do not represent a full fluid-dynamics model.

Available per-profile metadata can include circulation type, pump structure, oxygen-carrier profile, nucleation flag, clotting model, estimated blood-volume fraction and scenario baseline volume. Numerical baselines are game starting conditions, not clinical reference intervals. Species, age, sex, body size, hydration, exertion and health can change the real values.

### A7. How to extend anatomy safely

1. Add an organ/structure record with a system, role, substructures, tissues, dependencies and a note on evidence or fictional status.
2. Add it to a species with `anatomy.define_species(..., append_organs=[...])` or track it on a single entity with `anatomy.track(entity, name)`.
3. Decide if it is descriptive only or dynamic. Dynamic structures need explicit state fields, bounds, interactions, update rules and failure conditions in physiology.
4. Preserve clade differences. Do not use a human heart, lung, brain, blood-cell type, skin gland or bone count as the universal default.
5. Test the healthy state, partial injury, absent structure, critical failure, form-change, and appraisal rollback. Unknown facts should stay unknown.

### A8. Research sources and scope caveat

For the comparative-biology rationale, species differences, model hierarchy, and limits of the built-in physiology, see the standalone [Comparative Anatomy Research and Model Design](COMPARATIVE_ANATOMY_RESEARCH.md). The links below are the primary references used for the concise catalogue in this page. Fictional templates are design hypotheses rather than biological claims.

- [OpenStax Anatomy & Physiology 2e — preface and system organisation](https://openstax.org/books/anatomy-and-physiology-2e/pages/preface).
- [Merck Veterinary Manual — beef cattle digestive system](https://www.merckvetmanual.com/management-and-nutrition/nutrition-beef-cattle/the-digestive-system-of-beef-cattle).
- [Merck Veterinary Manual — ruminant digestive system](https://www.merckvetmanual.com/pharmacology/systemic-pharmacotherapeutics-of-the-digestive-system/the-ruminant-digestive-system).
- [Merck Veterinary Manual — overview of reptiles](https://www.merckvetmanual.com/exotic-and-laboratory-animals/reptiles/overview-of-reptiles).
- [Maina & Schachner — Biology of the avian respiratory system (2025)](https://pmc.ncbi.nlm.nih.gov/articles/PMC11864829/).
- [Aalkjær & Wang — The remarkable cardiovascular system of giraffes (2021)](https://doi.org/10.1146/annurev-physiol-031620-094629).
- [NCBI Bookshelf — Anatomy, Appendicular Skeleton](https://www.ncbi.nlm.nih.gov/books/NBK537097/).
- [UF/IFAS — Earthworm Anatomy](https://ask.ifas.ufl.edu/publication/in946).
