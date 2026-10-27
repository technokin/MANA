# Comparative Anatomy Research and Model Design

**Page kind:** Research-backed design reference  
**Status:** Current design reference for the built-in `anatomy` and `physiology` libraries  
**Scope:** Human, comparative vertebrates, insects and other invertebrates, extinct animals, and editable fictional body plans

This page explains what the anatomy catalogue represents, how its species differ, how much biological detail is recorded, and how to extend it without flattening every organism into a human-shaped creature. It is a game-engine reference, not a clinical, veterinary, evolutionary, or forensic authority.

## 1. Model philosophy: data depth without pretending to simulate every cell

MANA needs detailed anatomy because spells may inspect, injure, protect, change, repair, control, kill, revive, or re-form a creature. A catalogue entry must therefore be useful to code: it needs a stable identifier, system membership, anatomical role, substructure references where known, material/tissue hints, dependencies, and an evidence/scope note.

It is not useful to create one world object for every red blood cell, neuron, collagen fibre, bacterium, or water molecule by default. A typical creature should instead have a compact body model with nested anatomical records and a smaller set of changing physiological state variables. A spell can address a whole system, organ, tissue, blood compartment, named bone, body region, or custom substructure. Projects that need cellular detail can add a finer subsystem without forcing every ordinary scene to pay that cost.

The data hierarchy is:

1. **Organism / body plan** — species template, body size and shape, clade, skeleton/support type, movement modes, broad baseline traits, and species-specific exceptions.
2. **Body system** — functional grouping. One organ may participate in several systems; the assignment is a useful model index, not a claim that biology has rigid non-overlapping categories.
3. **Organ or named structure** — stable name, role, substructures, associated tissues, dependencies and presence/absence rules.
4. **Tissue** — broad material and structural category such as epithelium, connective tissue, muscle, nervous tissue, blood, cartilage, bone, feather, scale/cuticle or fluid compartment.
5. **Cell type** — reference record describing a cell's typical role. Cell entries are metadata unless a project implements cell-scale dynamics.
6. **Dynamic state** — condition that can change during simulation: integrity, injury, inflammation, oxygenation, blood volume, clotting, temperature, toxin burden, consciousness, life state, regeneration, or a custom variable.
7. **Spell and world interaction** — rules that change state, check prerequisites, cause secondary effects and resolve failure.

OpenStax uses the chemical, cellular, tissue, organ and organ-system levels to teach human structure, while emphasizing homeostasis and disruption. MANA follows that broad hierarchy but adapts it to multiple clades and fictional species. See [OpenStax Anatomy & Physiology 2e](https://openstax.org/books/anatomy-and-physiology-2e/pages/preface).

## 2. Coverage currently supplied by MANA

The expanded catalogue contains **23 broad system records, 991 named organ/structure records, 29 named cell-type records, 14 tissue categories, 91 species/body-plan templates, and 206 individually named records in the typical adult human bone inventory**. The human template has 691 addressable structures in this catalogue revision. Stock additions include more dinosaur/pterosaur/marine-reptile templates, distinct western/eastern dragons, minotaur, ant castes, and a slime body plan. This is a wide reference foundation, not a claim that every entry has a bespoke simulation solver or that one inventory can enumerate every part of every species.

### 2.1 Physical envelope and composable body plans

Stock templates now carry explicit approximate mass, body dimensions, density, volume, and collider-radius baselines. These connect comparative anatomy to MANA's physical world state rather than letting a tiny insect, earthworm, eagle, human, and dragon inherit one generic mass. Values are approximate game-scale priors and should be overridden for particular individual bodies or fantasy designs. The runtime still uses a 2D circular collider rather than a fully articulated body.

Custom profiles can combine a primary body plan with multiple donor templates, add/remove named structures, override traits, and declare movement capabilities. This supports author-defined chimeras and entirely fictional anatomy without making the built-in species list a closed whitelist. It is a composition framework, not automatic biological compatibility: circulation, respiration, digestion, skeleton interfaces, thermoregulation, and movement still need coherent integration rules. `anatomy.audit(species)` reports structural errors and non-blocking design warnings.

### 2.2 System catalogue

| System | Main model responsibilities | Example structures / states |
|---|---|---|
| `integumentary` | Outer barrier, contact, water loss, appearance, surface protection | skin, epidermis, dermis, hair, fur, feathers, scales, claws, hooves, cuticle, glands |
| `skeletal` | Support, leverage, protection, named bone damage, mineralised structures | skull, vertebral column, ribs, limbs, joints, cartilage, bone marrow, exoskeleton or hydrostatic support where appropriate |
| `muscular` | Force, posture, organ movement and locomotion | skeletal muscle, smooth muscle, cardiac muscle, tendons, fascia, sphincters |
| `nervous` | Signal transmission, reflexes, coordination and consciousness proxies | brain or ganglia, spinal/ventral nerve cord, peripheral nerves, autonomic and enteric networks |
| `sensory` | Input channels used by perception- and targeting-oriented spells | eyes, ears, inner ear, olfactory epithelium, tongue, tactile and balance receptors; specialised senses are clade-specific |
| `endocrine` | Slower systemic regulation and internal feedback | pituitary/hypothalamic axis where present, thyroid, adrenal, pancreas, gonads and other glands |
| `circulatory` | Fluid transport and pump state | heart or circulatory pump, vessels, blood, aortic arches in annelid models, haemolymph where appropriate |
| `lymphatic` | Fluid return and transport | lymph vessels, lymph nodes, lymphatic organs; absence or different layout must be represented for non-mammal profiles |
| `immune` | Defence, inflammatory response, recognition and clearance | marrow/lymphoid tissues, leukocytes or clade-appropriate immune cells, barriers and immune state |
| `respiratory` | Oxygen/carbon dioxide exchange and ventilation | mammalian airways/alveoli, avian lungs/air sacs, reptile lungs, skin-mediated exchange in the earthworm model |
| `digestive` | Intake, processing, absorption and elimination | mouth, pharynx, oesophagus, gut regions, liver/pancreas where present, cloaca or anus as appropriate, crop/gizzard in birds, ruminant stomach compartments |
| `metabolic` | Energy stores, chemical processing and internal balance | liver, adipose, cellular energy reserves, glycogen/fat stores, detoxification and metabolic status proxies |
| `renal` | Waste handling, water and electrolyte balance | kidneys and urinary pathways in many vertebrates; nephridia in earthworm; reptile/bird excretion differs from mammalian defaults |
| `reproductive` | Reproductive structures and life-stage-specific features | gonads, ducts, uterus or egg-related structures, reproductive organs that differ by clade; optional for non-reproductive or abstract beings |
| `hematopoietic` | Production/replenishment of blood components | bone marrow in many mammals; other blood-cell production sites and mechanisms vary by lineage |
| `thermoregulation` | Heat generation, loss, insulation and behaviour | fur/feathers, skin blood flow, panting, behavioural cooling, ectothermic or endothermic strategies |
| `microbiome` | Symbiotic organisms and fermentation | rumen microbial community, gut flora, other named microbial niches; separate state from the host's own organs |
| `locomotor` | Integrated movement mechanics | gait, limbs/wings/fins, slithering, burrowing, trunk movement, joints and force chains |
| `developmental` | Growth, maturation, regeneration, and life-stage transition reference | growth zones, regenerative structures, metamorphic stages |
| `feeding` | Prey handling and food acquisition | beak, jaw, tentacles, filter-feeding structures, grasping parts |
| `defence` | Specialised defensive structures and secretions | venom apparatus, stingers, ink glands, defensive displays |
| `electroreception` | Electrical-field detection and discharge reference | electroreceptors, electric organs, field-sensing structures |
| `magical_specialisation` | Explicitly fictional/setting-defined structures | dragon flame organ, griffin hybrid compatibility, aetheric organ or other user-created magical anatomy |

These are MANA's modelling categories. They intentionally include cross-cutting concepts such as `locomotor`, `thermoregulation`, and `microbiome` rather than exactly copying a textbook's count of human organ systems.

### 2.2 What a named entry does and does not mean

A named organ entry can currently be queried, inspected, tracked on a body model, associated with a system, used as the target of supported injury/healing operations, and linked to other structures through metadata. That does **not** mean every entry has a dedicated mechanical solver. For example, listing a pancreas does not by itself implement glucose homeostasis; listing a liver does not implement every biochemical pathway; listing an eye does not simulate optics or a retina neuron-by-neuron.

A simulation rule becomes dynamic only when MANA has explicitly modelled state and an update/interaction rule for it. The library should be honest about this distinction. Descriptive depth provides vocabulary and structure; physiology supplies selected mechanisms.

## 3. Human body profile

The human profile is the most detailed built-in template. Its named structure set spans the MANA system catalogue, and its typical adult skeletal reference lists 206 individually addressable bones: 80 axial and 126 appendicular records. Bone counts vary across life stages and among people; newborn skeletons contain more separate elements that later fuse, so 206 is a conventional adult reference rather than a universal invariant. The inventory is a practical coding reference, not a substitute for individual anatomy.

### 3.1 Skin and surface system

Human skin is not simply an outer shell. The model distinguishes epidermis, dermis and the underlying hypodermal/subcutaneous interface where useful, and includes accessory structures such as follicles, hair, nails, sweat/sebaceous glands, sensory endings, small vessels and immune-active cells. The skin is a barrier against water loss and external insults, participates in sensation and immune defence, and supports heat exchange. A skin spell should therefore be able to select appearance, barrier integrity, sensation, hydration, pigmentation, thermal loss and wound state independently where the implementation exposes those properties.

OpenStax describes skin and accessory structures as a dynamic protective organ system, not merely an appearance layer: [Integumentary system](https://openstax.org/books/anatomy-and-physiology-2e/pages/5-introduction). For MANA, layer names are structural references; the full keratin, melanocyte, immune and microvascular biology is not solved cell-by-cell.

### 3.2 Skeleton, joints and force transmission

The human bone inventory includes the skull and face, auditory ossicles, hyoid, vertebral regions, ribs, sternum, shoulder girdle, upper limbs, pelvis, lower limbs and sesamoid structures where represented. Each record can be addressed by a stable name such as `left_humerus` rather than only damaging a generic “skeleton” stat. Joints, cartilage, ligaments, tendons and fascia are separate structures because they fail differently: a bone fracture, ligament tear, joint displacement and tendon rupture are not equivalent.

Bones contribute to support, protection, leverage, mineral storage and marrow functions. The model can record individual-bone integrity and aggregate it into broader skeletal condition, but it does not currently calculate every fracture line, growth plate, microtrabecular stress or bone-remodelling cycle. For general human skeletal functions, see [NCBI Bookshelf: Anatomy, Appendicular Skeleton](https://www.ncbi.nlm.nih.gov/books/NBK537097/) and [OpenStax Bone and Skeletal Tissue](https://openstax.org/books/anatomy-and-physiology-2e/pages/6-introduction).

### 3.3 Muscle, fascia and movement

A body needs a force chain: neural command or reflex → muscle activation → tendon/fascia force transmission → joint or body-wall movement → contact with the world. Smooth and cardiac muscle are not ordinary voluntary skeletal muscle; a language-level spell that strengthens voluntary movement should not automatically increase heart contraction or gut peristalsis. Muscular records include major skeletal muscles and groups, smooth muscle, cardiac muscle, tendons, fascia, diaphragm and clade-specific body-wall muscles. The current simulator uses aggregate multipliers/state values for several physiological effects; it does not run a full musculoskeletal inverse-dynamics solver.

### 3.4 Nervous system and senses

The profile contains central processing, brain regions, spinal cord, peripheral/autonomic pathways and special-sense structures. For magic, this supports explicit effects such as impaired movement command, loss or gain of sensation, altered reflexes, confusion, sleep, paralysis or enhanced perception. These effects should have different targets and counters: an eye injury differs from optic-nerve disruption, which differs from a visual-processing effect. In the model, however, the hierarchy of `eye → optic nerve → neural processing` is descriptive/dependency metadata unless a specific spell or physiology rule implements the signal chain.

### 3.5 Blood, heart, vessels and lymph

Blood is both a transport medium and a state-bearing compartment. Relevant properties include current/max blood volume, composition/capacity approximations, oxygenation, flow/pressure proxies, clotting, loss, contamination and healing. The heart, conducting tissue, vessels, marrow and lymphatic structures are separate targets. A blood-manipulation effect should specify which operation it performs: move fluid, alter pressure, restrict a vessel, affect clotting, sense a trace, change a property, or create a magical link. A blanket “control blood” operation is too vague to be a robust world rule.

A common adult-human blood-volume estimate is roughly five litres, but actual volume depends strongly on body size and physiological state; the game's defaults are scale references only, not safe clinical values. See [NCBI Bookshelf: Blood Volume](https://www.ncbi.nlm.nih.gov/books/?term=Blood+Volume+StatPearls).

### 3.6 Breathing, digestion, renal and metabolic balance

The respiratory profile differentiates upper/lower airways, lungs, gas-exchange surfaces, respiratory muscles and relevant blood transport. The digestive profile separates ingestion, mechanical processing, chemical digestion, intestinal absorption, liver/pancreatic roles, microbiome links and elimination. Renal and metabolic records represent waste/water balance, energy storage and chemical processing, but these are not a comprehensive biochemical model. Spells that manipulate air, poison, water or metabolism should consult the relevant structures and the implemented rules rather than silently assuming one numeric “health” value explains every failure.

### 3.7 Endocrine, immune, reproductive and life-stage states

The reference names glands, immune structures, reproductive organs and their clade-appropriate variants. These are extension points for hormonal feedback, infection, immune resistance, fertility, pregnancy/egg development, maturation and ageing mechanics. Their presence in the catalogue does not mean MANA currently models all hormone concentrations, immune memory, gametogenesis, embryology or developmental timing.

## 4. Mammal comparisons

Mammal templates share a broad endoskeletal, lung-breathing, hair/fur and mammalian circulation plan, but ecological specialisations alter the details. The following comparisons guide spell targeting and custom extension; they are not veterinary diagnosis templates.

### 4.1 Lion and tiger

Lion and tiger bodies have many shared big-cat structures: powerful forequarters, flexible spine, large jaw muscles, carnassial teeth, claws, paw pads, vibrissae, tail and highly developed sensory/motor systems. Their musculoskeletal model needs to represent both force and joint range; simply setting `strength=2` is not enough to make a physically coherent pounce. A tiger profile is not a lion profile with different stripes, and neither should use human hands/feet as the locomotor default.

For game simulation, useful separable state includes bite force proxy, forelimb force, paw/claw integrity, stride acceleration, balance, hearing/smell/low-light perception and recovery. These values are gameplay tuning, not published performance measurements. The source-level reference confirms close anatomical similarity between the two species, which is why a shared feline structure catalogue with species-specific deltas is more maintainable than two unrelated lists: [Smithsonian National Zoo — Lion](https://nationalzoo.si.edu/animals/lion) and [Smithsonian National Zoo — Tiger](https://nationalzoo.si.edu/animals/tiger).

### 4.2 Giraffe and cow: ruminant digestive model

Both giraffe and cattle are ruminants in the catalogue. Their digestive model needs four stomach compartments—rumen, reticulum, omasum and abomasum—plus fermentation by a microbial community, regurgitation/rumination, absorption and intestinal processing. Those compartments are not four interchangeable names for one stomach. A food or poison spell should be able to target the fermentation compartment, the true stomach, intestine, liver/metabolic handling or circulation depending on its intended mechanism.

Cattle have a dental pad rather than upper incisors and have ruminant feeding mechanics. The giraffe adds a long neck, ossicones, specialised circulation and postural pressure-management concerns. The giraffe's high arterial pressure and vascular/renal adaptations are documented in a 2021 review; MANA should use those facts qualitatively unless a setting explicitly opts into validated numerical baselines. Sources: [Merck Veterinary Manual — Beef Cattle Digestive System](https://www.merckvetmanual.com/management-and-nutrition/nutrition-beef-cattle/the-digestive-system-of-beef-cattle), [Merck Veterinary Manual — Ruminant Digestive System](https://www.merckvetmanual.com/pharmacology/systemic-pharmacotherapeutics-of-the-digestive-system/the-ruminant-digestive-system), and [Aalkjær & Wang, The Remarkable Cardiovascular System of Giraffes (2021)](https://doi.org/10.1146/annurev-physiol-031620-094629).

### 4.3 Pig, horse and dog

The pig profile is a monogastric mammal and must not inherit the cow's four-compartment fermenting stomach. Its nose/snout, skin, limbs, dentition and digestive profile differ from ruminants. The horse profile requires an equid limb/hoof and hindgut-fermentation emphasis rather than a ruminant fore-stomach. The dog profile is a generalised canid with a muzzle, dentition, scent-oriented sensory profile and digitigrade limb mechanics, but it should not pretend all breeds have the same proportions or performance.

The catalogue has shared mammalian components to avoid unnecessary duplication; it then adds or removes features through explicit species records. Shared data should only be inherited when the corresponding anatomy is actually shared. If an organ is absent, mark it absent/remove it from the species-specific inventory; do not merely set it to zero damage.

## 5. Snake: elongated reptilian body plan

A snake needs a fundamentally different model from a legged mammal. Key features include a long vertebral column with numerous ribs, flexible jaw apparatus, elongate body muscles, scale-covered skin, a cloacal outlet, species-specific venom apparatus when applicable, and a long sequence of organs arranged along the trunk. Most snakes lack a developed diaphragm; ventilation depends on rib/body-wall mechanics and clade-specific lung architecture. Many species have a dominant elongated right lung and a reduced or absent left lung, but boas and pythons can retain both lungs, so the catalogue must not treat “one lung only” as universal.

The current profile deliberately excludes a diaphragm and marks venom as species/individual capability rather than a universal snake property. Important effect targets include scale integrity, ribs/vertebrae, jaw ligaments, lung/airway, venom gland/duct/fang when present, sensory tongue/vomeronasal route, circulatory system and cloaca. Flexible-body movement must be controlled by body segments and lateral curvature, not a four-limb gait. Sources: [Merck Veterinary Manual — Overview of Reptiles](https://www.merckvetmanual.com/exotic-and-laboratory-animals/reptiles/overview-of-reptiles) and [NCBI/PubMed — Gravity and the Evolution of Cardiopulmonary Morphology in Snakes](https://pubmed.ncbi.nlm.nih.gov/?term=Gravity+and+the+Evolution+of+Cardiopulmonary+Morphology+in+Snakes).

## 6. Birds: eagle, falcon, owl, raven, parrot and pigeon

The built-in bird templates share avian body-plan components but have different ecological specialisations. An eagle and falcon emphasise powerful flight and visual tracking; owls add a nocturnal auditory/visual profile and specialised feather structure; ravens are generalist corvids with manipulative beaks and cognition-oriented gameplay hooks; parrots have a strong curved beak and zygodactyl feet in many species; pigeons are a compact generalist flight profile. These are setting/model distinctions, not absolute statements about every species or individual.

Bird respiration is a major cross-clade distinction. Bird lungs are comparatively rigid, and air sacs drive one-way airflow through the gas-exchange region; air sacs are ventilatory bellows, not simply extra mammalian lungs. Avian skeletons may be partly pneumatic, but pneumaticity varies by taxon and bone, so “all bird bones are hollow” is an incorrect implementation rule. Birds do not cool by sweating as humans do; panting, gular movements, posture and air flow can matter. The profile uses nucleated avian red blood cells rather than copying mammalian erythrocytes.

Spell interactions can target feather condition, wing joints, keel/flight muscles, air sac ventilation, gas-exchange lung, beak, talons, visual system, inner-ear/balance system and thermal regulation separately. A wing injury can reduce flight control without instantly stopping circulation or consciousness; respiratory damage and feather damage should not be treated as equivalent. Sources: [Merck Veterinary Manual — Introduction to Birds](https://www.merckvetmanual.com/bird-owners/introduction-to-birds/introduction-to-birds), [Maina & Schachner — Biology of the Avian Respiratory System (2025)](https://pmc.ncbi.nlm.nih.gov/articles/PMC11864829/), and [Schachner & Moore — What It Takes to Make a Bird Lung (2025)](https://pmc.ncbi.nlm.nih.gov/articles/PMC11864838/).

## 7. Earthworm: annelid body plan, not a tiny vertebrate

The earthworm template uses a hydrostatic skeleton and segmented body wall rather than bones. Circular and longitudinal muscles work against fluid pressure in a coelomic compartment; setae anchor segments during locomotion. The digestive tube includes mouth, pharynx, oesophagus, crop, gizzard and intestine. The closed circulatory model includes dorsal/ventral vessels and aortic arches rather than a vertebrate four-chambered heart. Neural references include cerebral ganglia and a ventral nerve cord rather than a mammalian brain/spinal-cord layout. Excretion uses segmental nephridia. Gas exchange is modelled through the moist body surface/cuticle, not lungs. The clitellum is associated with reproduction in mature individuals and should be life-stage-aware.

A spell which “strikes the heart” must not automatically kill an earthworm simply because the word `heart` is part of the spell. It needs to target a structure actually present in the selected body model or use a general physiological effect such as severe circulation failure. Similarly, a mammal-style bone fracture is invalid for the earthworm profile, though body-wall damage, segment injury, coelomic pressure loss or nerve-cord damage can be meaningful extensions.

Source: [University of Florida/IFAS — Earthworm Anatomy](https://ask.ifas.ufl.edu/publication/in946) and [William Paterson University — Introduction to Organismal Systems](https://www.wpunj.edu/cos/biology/faculty-staff/droberts/AnimalPhysiologyLabManual.html) (teaching reference; anatomy differs across annelid species).

## 8. Fictional body plans: dragons, griffins, goblins, orcs and elves

These are editable **fictional templates**, not research claims. A fictional profile must clearly separate its borrowed biological analogue from its invented anatomy. Shared humanoid templates can provide baseline skin, skeleton, muscle, nerve, circulation, respiration, digestion and reproduction concepts, but each fantasy species should specify how it differs.

### 8.1 Dragon

A dragon may be quadrupedal with wings (a six-limbed vertebrate-like body plan), but real vertebrate tetrapods do not ordinarily have six limbs. The template must therefore state that the design is speculative. A flight-capable dragon needs a credible mass-to-wing-area ratio, skeletal bracing, shoulder/wing articulation, flight muscle, circulation and respiration model; “has wings” alone is not sufficient. Fire breathing can be represented as a separate magical specialisation (for example, a heat-resistant conduit or spell-mediated emission), not as an assumed biological organ unless the world designer defines one. Heat-resistant mouth/throat tissue, ignition chemistry and fuel storage are user-designed fictional rules.

### 8.2 Griffin

A griffin hybrid profile has a mammalian-like body plus an avian head/wings or another explicitly chosen arrangement. It needs custom joints, compatible muscle attachment, separate lung/air-sac assumptions if bird-like respiration is selected, and clear rules for feather/fur/skin boundaries. A template cannot biologically inherit all eagle and lion systems without conflict. The designer must pick a hybrid model and define which components are integrated, duplicated, or magical.

### 8.3 Goblin, orc and elf

These are humanoid fictional templates. At present, their physiology mostly uses a mammal-like baseline with editable skeletal, muscle, sensory, circulation and magical-specialisation traits. This is a design starting point, not established lore. An elf can have acute sensory range or long lifespan only if the project's rule set defines the mechanism; an orc's strength does not imply invulnerability; a goblin's size does not determine intelligence. Add organs such as an aetheric node, extended sensory structure, redundant organ, or regenerative tissue only with explicit roles, dependencies, costs, failure states and counters.

## 9. Blood, oxygen, injury and death: choosing a level of simulation

The physiology library tracks selected high-value body state—such as injury, health, blood volume/loss, oxygenation, temperature, toxic burden, consciousness and life state. These variables are deliberately lower-dimensional than real physiology. Real blood is a combination of plasma and cellular components; oxygen transport depends on ventilation, gas exchange, circulation, oxygen carrier concentration and affinity, and tissue demand. The state model therefore needs species-specific parameters or explicit custom profiles, not a universal human number.

Injury should be local first, then propagated only by declared rules. Damage to a named bone changes that bone's integrity and can contribute to aggregate skeletal impairment. Damage to a gas-exchange structure can affect oxygenation; blood loss can affect circulating volume; failure of a critical organ may change life state, but there should be explicit thresholds and dependencies. Do not infer total-organism death from a single missing descriptive entry, and do not infer that “revive” repairs every underlying injury. Revival may restore life state while leaving the original injury, toxicity or missing structure for subsequent healing/resolution.

For magical body manipulation, define operation, target, duration, reversibility, cost, prerequisites, side effects, resistance and failure behaviour. “Control blood” can mean telekinetic displacement, altered pressure, coagulation, sensing, poisoning, or changing blood composition; these are separate rules. Self-transfiguration should have checks for body-plan compatibility, breathing/circulation viability, volume/mass assumptions, sensory continuity, and whether the new anatomy has required organs. Incompatible forms should fail safely or yield an explicitly unstable transformation instead of silently leaving a mammalian body with a snake's organs.

## 10. User-defined anatomy and freedom

Built-in profiles are not a closed list. Use the documented custom-species and custom-organ operations to add species-specific structures. The intended workflow is:

1. Start from the closest body plan or create a new one.
2. Declare skeleton/support type, movement mode, circulation and respiratory strategy, and which systems are present.
3. Add structures with stable names, role, substructures, tissue types, dependencies, and a `status`/evidence note such as `reference`, `approximate`, `user-defined`, or `fictional-template`.
4. Declare what happens when a structure is injured, absent, transformed, poisoned, healed, or restored from death.
5. Keep profile size within the library's limits: up to 1024 addressable/tracked structures per body, separately from the 512 user-defined structure-definition limit per runtime. Use substructure lists for descriptive detail instead of creating hundreds of world objects.
6. Test valid state, absent structure, partial damage, critical damage, healing, transformation, revival, and appraisal rollback.

Example MANA-style usage (check the function reference for exact signatures):

```mana
load planes
load anatomy
load physiology
planes.open_path("Wild Realm", "Mortal Plane")

spell examine_griffin():
    griffin = summon "Griffin" from "Wild Realm"
    anatomy.bind(griffin, "griffin")
    anatomy.inspect(griffin, "wings")
    physiology.profile(griffin)
    incant griffin

cast examine_griffin
```

Expected output:

```text
[CAST examine_griffin] spell committed
[CAST examine_griffin] mana appraisal: 0 mana
```

The reference profile provides names and selected default values. It is not a guarantee that every organ receives continuous simulation. New dynamic behaviour requires runtime implementation and tests, not just adding a row to a data file.

## 11. Reference sources and what they support

- [OpenStax — Anatomy & Physiology 2e](https://openstax.org/books/anatomy-and-physiology-2e/pages/preface): hierarchy of chemical, cellular, tissue, organ and system levels; homeostasis; human integumentary and skeletal concepts.
- [OpenStax — Integumentary System](https://openstax.org/books/anatomy-and-physiology-2e/pages/5-introduction): skin/accessory structures as a protective and dynamic organ system.
- [NCBI Bookshelf — Anatomy, Appendicular Skeleton](https://www.ncbi.nlm.nih.gov/books/NBK537097/): human skeletal regions and structures.
- [NCBI Bookshelf search — Blood Volume / StatPearls](https://www.ncbi.nlm.nih.gov/books/?term=Blood+Volume+StatPearls): adult blood volume as a variable clinical estimate, not a fixed universal quantity.
- [Merck Veterinary Manual — Respiratory System in Animals](https://www.merckvetmanual.com/respiratory-system/respiratory-system-introduction/the-respiratory-system-in-animals): interspecies differences in mammalian airway/lung structure and function.
- [Merck Veterinary Manual — Introduction to Birds](https://www.merckvetmanual.com/bird-owners/introduction-to-birds/introduction-to-birds): rigid bird lungs, air-sac ventilation, thermal biology and bird-specific traits.
- [Maina & Schachner — Biology of the Avian Respiratory System (2025)](https://pmc.ncbi.nlm.nih.gov/articles/PMC11864829/): contemporary review of the bird respiratory system.
- [Schachner & Moore — What It Takes to Make a Bird Lung (2025)](https://pmc.ncbi.nlm.nih.gov/articles/PMC11864838/): avian lung structure and evolution.
- [Merck Veterinary Manual — Overview of Reptiles](https://www.merckvetmanual.com/exotic-and-laboratory-animals/reptiles/overview-of-reptiles): cloaca, variable lung complexity, lack of a true diaphragm in reptiles, and long-axis arrangement of snake organs.
- [PubMed search — Gravity and Evolution of Cardiopulmonary Morphology in Snakes](https://pubmed.ncbi.nlm.nih.gov/?term=Gravity+and+the+Evolution+of+Cardiopulmonary+Morphology+in+Snakes): comparative background for elongate snake lungs and variability across groups.
- [University of Florida/IFAS — Earthworm Anatomy](https://ask.ifas.ufl.edu/publication/in946): earthworm body plan and named internal structures.
- [William Paterson University — Animal Physiology Lab Manual](https://www.wpunj.edu/cos/biology/faculty-staff/droberts/AnimalPhysiologyLabManual.html): educational dissection/anatomy context including organismal systems; treat as a teaching source.
- [Merck Veterinary Manual — Digestive System of Beef Cattle](https://www.merckvetmanual.com/management-and-nutrition/nutrition-beef-cattle/the-digestive-system-of-beef-cattle): ruminant stomach compartments and cattle-specific digestive anatomy.
- [Merck Veterinary Manual — Ruminant Digestive System](https://www.merckvetmanual.com/pharmacology/systemic-pharmacotherapeutics-of-the-digestive-system/the-ruminant-digestive-system): rumen/reticulum/omasum/abomasum and microbial fermentation.
- [Aalkjær & Wang — The Remarkable Cardiovascular System of Giraffes (Annual Review of Physiology, 2021)](https://doi.org/10.1146/annurev-physiol-031620-094629): giraffe heart, blood vessels, kidney and cranial perfusion adaptations.
- [Smithsonian National Zoo — Lion](https://nationalzoo.si.edu/animals/lion) and [Tiger](https://nationalzoo.si.edu/animals/tiger): accessible species background for felid form and ecology.

### Evidence and versioning policy

Species facts can change with new research or taxonomic scope. A source supports the facts it discusses, not every field in MANA's tables. Where a profile is generalised (for example, “snake”, “earthworm”, or “eagle”), exact structure and counts can differ among species. Numerical defaults used by the game are not automatically research measurements. All fantasy templates are fictional hypotheses and should be reviewed as design documents, not biology.
