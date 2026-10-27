"""Reference anatomy and comparative biology data used by MANA's anatomy library.

Real-species records are compact, game-oriented summaries drawn from public
anatomy/physiology references listed in docs/current/libraries/ANATOMY_LIBRARY.md.
Fantasy-species records are explicitly design proposals, not scientific claims.
"""
from __future__ import annotations

import copy
import re

# Records deliberately use plain immutable-ish literals; public calls deep-copy them.
# A body model can address more structures than the custom-definition registry
# permits users to add in one runtime. Keep this cap shared by anatomy and physiology.
MAX_BODY_STRUCTURES = 1024
SYSTEMS: dict[str, dict] = {
    "integumentary": {"label": "Integumentary", "purpose": "Boundary, barrier, sensory interface, temperature exchange, and external identity.", "dependencies": ["immune", "nervous", "thermoregulation"], "functions": ["barrier", "water_balance", "thermal_exchange", "sensation", "pigmentation"]},
    "skeletal": {"label": "Skeletal", "purpose": "Support, protection, force transmission, mineral storage, and (in marrow-bearing vertebrates) blood-cell formation.", "dependencies": ["muscular", "circulatory", "endocrine"], "functions": ["support", "protection", "leverage", "mineral_storage", "hematopoiesis"]},
    "muscular": {"label": "Muscular", "purpose": "Force production, posture, organ movement, heat generation, and locomotion.", "dependencies": ["nervous", "circulatory", "respiratory", "skeletal"], "functions": ["movement", "posture", "peristalsis", "pumping", "thermogenesis"]},
    "nervous": {"label": "Nervous", "purpose": "Sensation, integration, memory, coordination, autonomic regulation, and motor commands.", "dependencies": ["circulatory", "respiratory", "integumentary", "sensory"], "functions": ["signal", "integration", "reflex", "consciousness", "autonomic_control"]},
    "sensory": {"label": "Sensory", "purpose": "Detection and interpretation of light, sound, chemicals, pressure, temperature, position, and species-specific cues.", "dependencies": ["nervous", "integumentary"], "functions": ["vision", "hearing", "smell", "taste", "touch", "balance", "proprioception"]},
    "endocrine": {"label": "Endocrine", "purpose": "Slower systemic regulation using hormones and feedback loops.", "dependencies": ["nervous", "circulatory", "metabolic"], "functions": ["growth", "metabolism", "stress", "reproduction", "fluid_balance"]},
    "circulatory": {"label": "Circulatory", "purpose": "Transport of gases, nutrients, heat, signals, immune cells, and waste.", "dependencies": ["heart", "respiratory", "digestive", "renal"], "functions": ["transport", "pressure", "perfusion", "thermal_distribution", "clotting"]},
    "lymphatic": {"label": "Lymphatic", "purpose": "Return of interstitial fluid, lipid transport in many vertebrates, and immune-cell traffic.", "dependencies": ["circulatory", "immune", "digestive"], "functions": ["fluid_return", "lipid_transport", "immune_traffic"]},
    "immune": {"label": "Immune", "purpose": "Recognition, containment, and clearance of harmful biological agents and damaged material.", "dependencies": ["lymphatic", "circulatory", "bone_marrow", "integumentary"], "functions": ["barrier_defence", "innate_response", "adaptive_response", "repair"]},
    "respiratory": {"label": "Respiratory", "purpose": "Gas exchange and (in many species) vocal airflow; design differs radically by clade.", "dependencies": ["circulatory", "muscular", "nervous"], "functions": ["oxygen_uptake", "carbon_dioxide_removal", "acid_base_support", "vocalisation"]},
    "digestive": {"label": "Digestive", "purpose": "Acquisition, mechanical and chemical breakdown, absorption, microbial processing, and waste formation.", "dependencies": ["circulatory", "endocrine", "nervous", "microbiome"], "functions": ["ingestion", "motility", "digestion", "absorption", "elimination"]},
    "metabolic": {"label": "Metabolic / hepatic", "purpose": "Nutrient processing, storage, synthesis, detoxification, and homeostatic chemistry.", "dependencies": ["digestive", "circulatory", "endocrine", "renal"], "functions": ["fuel_processing", "protein_synthesis", "detoxification", "storage"]},
    "renal": {"label": "Renal / excretory", "purpose": "Waste removal, water/electrolyte balance, acid-base regulation, and pressure-related signalling.", "dependencies": ["circulatory", "endocrine"], "functions": ["filtration", "reabsorption", "secretion", "osmoregulation"]},
    "reproductive": {"label": "Reproductive", "purpose": "Gamete production, fertilisation, gestation or egg development, and species-specific parental structures.", "dependencies": ["endocrine", "circulatory", "metabolic"], "functions": ["gametogenesis", "fertilisation", "development", "lactation_or_provisioning"]},
    "hematopoietic": {"label": "Blood formation", "purpose": "Production, maturation, and turnover of circulating cells or cell analogues.", "dependencies": ["skeletal", "immune", "endocrine"], "functions": ["oxygen_transport", "immune_cells", "hemostasis"]},
    "thermoregulation": {"label": "Thermoregulation", "purpose": "Keeping body temperature within workable bounds through physiology and behaviour.", "dependencies": ["integumentary", "circulatory", "muscular", "endocrine"], "functions": ["heat_generation", "heat_loss", "insulation", "behavioural_control"]},
    "microbiome": {"label": "Resident microbiota", "purpose": "Communities of microorganisms that influence digestion, barrier defence, and local chemistry.", "dependencies": ["digestive", "immune"], "functions": ["fermentation", "metabolite_production", "colonisation_resistance"]},
    "locomotor": {"label": "Locomotor integration", "purpose": "Coordinated gait, climbing, flight, swimming, burrowing, slithering, or stationary posture.", "dependencies": ["skeletal", "muscular", "nervous", "sensory"], "functions": ["gait", "balance", "flight", "swimming", "burrowing"]},
    "developmental": {"label": "Development and regeneration", "purpose": "Growth, life-stage transitions, regeneration sites and form-specific development; each dynamic rule must be explicitly implemented.", "dependencies": ["endocrine", "metabolic", "integumentary"], "functions": ["growth", "maturation", "regrowth", "metamorphosis"]},
    "feeding": {"label": "Feeding and prey handling", "purpose": "Capture, grip, cut, crush, filter, chew, swallow or otherwise acquire food according to the body plan.", "dependencies": ["muscular", "sensory", "digestive"], "functions": ["capture", "biting", "filter_feeding", "grasping", "swallowing"]},
    "defence": {"label": "Defence and specialised secretions", "purpose": "Claws, venom, ink, stings and other lineage-specific defence structures.", "dependencies": ["nervous", "muscular", "integumentary"], "functions": ["deterrence", "venom_delivery", "ink_release", "protective_display"]},
    "electroreception": {"label": "Electrosensation and electric output", "purpose": "Specialised detection or production of electric fields in species that possess the structures.", "dependencies": ["nervous", "sensory"], "functions": ["electric_field_detection", "electric_discharge"]},
    "magical_specialisation": {"label": "Species-specific / fictional specialisations", "purpose": "Optional structures whose behaviour must be explicitly defined by a species or spell designer.", "dependencies": [], "functions": ["custom_capacity"]},
}

# High-level organs and addressable anatomical structures. Entries are reference
# records: the physiology runtime decides which selected structures are tracked.
ORGANS: dict[str, dict] = {}
def _organ(name: str, system: str, role: str, substructures=(), tissues=(), dependencies=(), notes=""):
    ORGANS[name] = {
        "name": name, "system": system, "kind": "organ_or_structure", "role": role,
        "substructures": list(substructures), "tissues": list(tissues),
        "dependencies": list(dependencies), "notes": notes,
    }

# Integument / tissue barriers
_organ("skin", "integumentary", "Protective outer organ; water barrier, sensation, immune interface, and thermoregulation.", ["epidermis", "dermis", "hypodermis/subcutis", "hair follicles or feather follicles", "sweat or specialised skin glands", "sebaceous glands (many mammals)", "cutaneous nerves", "blood vessels", "immune cells"], ["keratinised or specialised epithelium", "connective tissue", "smooth muscle", "sensory nerve endings"], ["immune", "sensory", "thermoregulation"], "Layer composition and appendages vary strongly by clade; do not assume every animal has human-style sweat glands or hair.")
_organ("epidermis", "integumentary", "External epithelial barrier and keratinisation/pigmentation interface.", ["basal layer", "intermediate layers", "surface keratin layer"], ["epithelial cells", "pigment cells", "immune sentinel cells"], ["skin"])
_organ("dermis", "integumentary", "Structural and vascular support beneath the epidermal barrier.", ["collagen matrix", "elastic fibres", "vessels", "nerves", "follicles/glands where present"], ["dense connective tissue", "vascular tissue"], ["skin"])
_organ("hypodermis", "integumentary", "Subcutaneous support, insulation, energy storage, and sliding plane.", ["adipose lobules", "fibrous septa", "larger vessels and nerves"], ["adipose", "loose connective tissue"], ["skin", "metabolic"])
_organ("hair", "integumentary", "Hair coat for insulation, sensation, signalling, and protection in many mammals.", ["shaft", "root", "follicle", "arrector pili muscle", "sebaceous unit"], ["keratinised cells", "epithelium", "smooth muscle"], ["skin"])
_organ("feathers", "integumentary", "Avian integumentary structures used for insulation, display, waterproofing, and flight control.", ["calamus", "rachis", "barbs", "barbules", "contour/down/flight feather classes"], ["keratin"], ["skin", "locomotor"])
_organ("scales", "integumentary", "Scale covering that protects the body and participates in water balance or locomotion depending on clade.", ["epidermal scales", "underlying dermis", "shed outer layer where ecdysis occurs"], ["keratinised epithelium", "connective tissue"], ["skin"], "Snake/reptile scales are not the same tissue or structure as fish scales or pangolin scales.")
_organ("claws", "locomotor", "Distal keratin structures for traction, defence, climbing, digging, or prey capture.", ["distal phalanx", "keratin sheath", "flexor/extensor tendons", "retraction apparatus in some felids"], ["keratin", "bone", "tendon", "ligament"], ["skeletal", "muscular"])
_organ("vibrissae", "sensory", "Specialised tactile hairs that report nearby surfaces and air movement in many mammals.", ["follicle-sinus complex", "sensory innervation"], ["keratin", "connective tissue", "sensory neurons"], ["nervous", "skin"])
_organ("feather_follicles", "integumentary", "Generate and anchor feathers in birds.", ["follicular epithelium", "blood supply during growth", "follicle sheath"], ["epithelium", "connective tissue"], ["feathers"])
_organ("cutaneous_glands", "integumentary", "Species-specific secretions for cooling, scent, waterproofing, signalling, or defence.", ["sweat glands where present", "sebaceous glands where present", "scent glands where present", "uropygial gland in many birds"], ["glandular epithelium"], ["skin", "endocrine"])

# Skeletal and connective structures
_organ("skeleton", "skeletal", "Whole-body framework: bone, cartilage or hydrostatic support depending on species.", ["axial skeleton", "appendicular skeleton where present", "joints", "cartilage", "periosteum", "bone marrow in marrow-bearing vertebrates"], ["compact bone", "spongy bone", "cartilage", "ligament", "marrow"], ["muscular", "hematopoietic"])
_organ("bones", "skeletal", "Individual rigid skeletal elements; details are listed by region in anatomy.bones().", ["cortical/compact layer", "trabecular/spongy layer", "periosteum", "endosteum", "marrow cavity where present", "joint surfaces"], ["bone matrix", "osteoblasts", "osteocytes", "osteoclasts", "marrow"], ["circulatory", "endocrine"])
_organ("joints", "skeletal", "Articulations enabling motion or stable load transfer.", ["articular surfaces", "joint capsule", "synovial membrane/fluid where present", "ligaments", "menisci/discs where present"], ["cartilage", "fibrous connective tissue", "synovial tissue"], ["skeletal", "muscular"])
_organ("cartilage", "skeletal", "Resilient support and low-friction joint surfaces.", ["hyaline", "elastic", "fibrocartilage"], ["chondrocytes", "extracellular matrix"], ["joints"])
_organ("ligaments", "skeletal", "Constrain and stabilise movement between skeletal elements.", ["collagen bundles", "attachments"], ["dense connective tissue"], ["joints", "skeleton"])
_organ("tendons", "muscular", "Transmit muscle force to skeletal or other structures.", ["collagen bundles", "enthesis", "sheath where present"], ["dense regular connective tissue"], ["skeletal_muscles", "skeleton"])
_organ("fascia", "muscular", "Connective-tissue planes that surround, separate, and transmit forces between structures.", ["superficial fascia", "deep fascia", "visceral fascia"], ["connective tissue", "adipose"], ["muscular", "skin"])
_organ("bone_marrow", "hematopoietic", "Blood-cell production and marrow immune functions where present.", ["hematopoietic niches", "stromal support", "vascular sinusoids", "fatty marrow in some bones"], ["hematopoietic cells", "stromal cells", "vascular tissue"], ["skeleton", "circulatory", "immune"])
_organ("vertebral_column", "skeletal", "Protects the main nerve cord and anchors ribs and locomotor musculature.", ["cervical region", "thoracic/trunk region", "lumbar region", "sacrum or fused pelvic region where present", "caudal/tail region", "intervertebral discs where present"], ["bone", "cartilage", "ligaments"], ["spinal_cord", "skeletal_muscles"])
_organ("ribs", "skeletal", "Protect thoracic organs and, where present, assist breathing mechanics.", ["vertebral ends", "shaft", "sternal/cartilaginous connection where present"], ["bone", "cartilage"], ["lungs", "heart", "muscular"])
_organ("sternum", "skeletal", "Ventral thoracic support and muscle attachment; a pronounced keel anchors flight muscles in many birds.", ["manubrium/body/xiphoid in humans", "keel/carina in many flying birds"], ["bone", "cartilage"], ["ribs", "muscular"])
_organ("skull", "skeletal", "Protects the brain and supports sensory and feeding structures.", ["cranial vault", "cranial base", "facial skeleton", "jaw apparatus", "orbits", "sensory capsules"], ["bone", "cartilage", "ligament"], ["brain", "eyes", "oral_cavity"])
_organ("teeth", "digestive", "Mechanical food processing and in some species prey capture or display.", ["enamel", "dentin", "cementum", "pulp", "periodontal ligament", "root and crown"], ["mineralised tissue", "connective tissue", "nerves", "vessels"], ["oral_cavity", "digestive"])
_organ("hydrostatic_skeleton", "skeletal", "Support produced by pressurised fluid compartments and body-wall muscles rather than bones.", ["coelomic compartment", "circular muscles", "longitudinal muscles", "septa", "setae where present"], ["muscle", "epithelium", "coelomic fluid"], ["locomotor"], "Used by earthworms and other invertebrates; not an endoskeleton.")

# Nervous and sensory system
_organ("brain", "nervous", "Integrates sensory input, movement, internal regulation, and higher processing.", ["cerebrum/cerebral hemispheres", "cerebral cortex", "basal nuclei", "thalamus", "hypothalamus", "limbic structures", "brainstem", "cerebellum", "ventricles"], ["neurons", "glia", "blood vessels", "meninges"], ["spinal_cord", "circulatory", "respiratory"])
_organ("cerebrum", "nervous", "Higher integration, perception, memory and voluntary action in many vertebrates.", ["frontal, parietal, temporal, occipital lobes in humans", "cortex", "white matter", "basal nuclei"], ["neurons", "glia"], ["brain"])
_organ("cerebellum", "nervous", "Movement timing, balance, error correction and motor learning.", ["cerebellar cortex", "deep nuclei", "peduncles"], ["neurons", "glia"], ["brain", "inner_ear", "skeletal_muscles"])
_organ("brainstem", "nervous", "Core pathways and autonomic control; major respiratory and cardiovascular centres in mammals.", ["midbrain", "pons", "medulla in mammals", "cranial nerve nuclei"], ["neurons", "glia"], ["brain", "spinal_cord", "heart", "lungs"])
_organ("spinal_cord", "nervous", "Relays signals and coordinates reflexes between central processing and body.", ["grey matter", "white matter", "segmental roots", "meninges/CSF interface"], ["neurons", "glia", "connective tissue"], ["brain", "peripheral_nerves"])
_organ("peripheral_nerves", "nervous", "Carry sensory and motor signals between the central nervous system and tissues.", ["sensory fibres", "motor fibres", "autonomic fibres", "supporting sheaths"], ["neurons", "Schwann cells or clade analogues", "connective tissue"], ["spinal_cord", "brain"])
_organ("autonomic_nervous_system", "nervous", "Regulates involuntary organ activity, including heart, smooth muscle, and glands.", ["sympathetic pathways", "parasympathetic pathways", "ganglia", "visceral afferents"], ["neurons", "glia"], ["heart", "digestive_tract", "endocrine"])
_organ("enteric_nervous_system", "nervous", "Local neural networks coordinating gut motility, secretion and blood flow.", ["myenteric plexus", "submucosal plexus"], ["neurons", "glia"], ["digestive"])
_organ("meninges", "nervous", "Protective membranes around central nervous structures.", ["dura", "arachnoid", "pia in mammals"], ["connective tissue"], ["brain", "spinal_cord"])
_organ("eyes", "sensory", "Capture and process light; arrangement varies by ecological niche.", ["cornea", "lens", "iris", "retina", "optic nerve", "eyelids", "tear structures", "tapetum lucidum in many nocturnal mammals"], ["neural tissue", "epithelium", "transparent connective tissue", "muscle"], ["brain", "nervous"])
_organ("ears", "sensory", "Receive sound; in many mammals include external pinna, middle ear, and inner ear.", ["pinna where present", "ear canal", "tympanum", "malleus/incus/stapes in mammals", "cochlea or clade-specific auditory organ", "vestibular apparatus"], ["epithelium", "bone/cartilage", "hair cells", "neurons"], ["brain", "nervous"])
_organ("inner_ear", "sensory", "Balance, acceleration sensing, and (in vertebrates) part of hearing.", ["semicircular canals", "otolith organs", "cochlear structures in many vertebrates"], ["fluid-filled membranes", "sensory hair cells", "neurons"], ["ears", "nervous"])
_organ("olfactory_epithelium", "sensory", "Chemical detection for smell; can connect with specialised vomeronasal systems.", ["olfactory receptor neurons", "supporting cells", "mucus layer"], ["sensory epithelium"], ["brain"])
_organ("vomeronasal_organ", "sensory", "Accessory chemical-sensing organ in many reptiles and some mammals.", ["paired ducts/chambers where present", "sensory epithelium"], ["sensory epithelium"], ["olfactory_epithelium"], "Presence and function differ across taxa; do not treat as universal.")
_organ("tongue", "sensory", "Manipulates food and contributes to taste, feeding, grooming, or specialised functions.", ["intrinsic/extrinsic muscles in many vertebrates", "papillae", "taste buds where present", "specialised tip or bifurcation in some taxa"], ["skeletal muscle", "epithelium", "sensory nerves"], ["oral_cavity", "sensory"])
_organ("olfactory_bulbs", "sensory", "Initial central processing for olfactory signals where present.", ["glomeruli", "mitral/tufted cells or clade analogues", "interneurons"], ["neurons", "glia"], ["olfactory_epithelium", "brain"])

# Cardiovascular / blood / lymphatic
_organ("heart", "circulatory", "Pressure-generating pump; chamber count and routing differ by clade.", ["atria/auricles", "ventricles", "valves or functional equivalents", "conducting tissue", "coronary vessels", "pericardium"], ["cardiac muscle in vertebrates", "connective tissue", "nerve and conduction cells"], ["blood", "lungs", "nervous"])
_organ("blood", "circulatory", "Transport fluid containing liquid phase, gas carriers, immune cells and clotting components.", ["plasma or equivalent", "oxygen-carriers", "immune cells", "clotting cells/proteins"], ["fluid", "cells"], ["heart", "bone_marrow", "immune"], "Not every animal has red blood cells; many birds/reptiles have nucleated erythrocytes; earthworm haemoglobin is carried differently from mammalian haemoglobin.")
_organ("blood_plasma", "circulatory", "Liquid portion transporting proteins, nutrients, dissolved ions, hormones and wastes.", ["water", "electrolytes", "plasma proteins", "nutrients", "hormones"], ["fluid"], ["liver", "kidneys"])
_organ("red_blood_cells", "hematopoietic", "Gas carrier cells in vertebrates; morphology and nucleus status vary by lineage.", ["haemoglobin-containing erythrocytes in vertebrates", "nucleus retained in birds and reptiles", "mature mammalian erythrocytes typically lack nuclei"], ["cell membrane", "haemoglobin or species-specific carrier"], ["bone_marrow", "respiratory"])
_organ("white_blood_cells", "immune", "Cellular defence, signalling, and tissue surveillance.", ["lymphocytes", "phagocytes", "granulocytes or clade-specific analogues"], ["immune cells"], ["bone_marrow", "lymphatic"])
_organ("platelets", "hematopoietic", "Primary haemostatic plugs in mammals; other vertebrates generally use nucleated thrombocytes.", ["adhesion", "activation", "aggregation"], ["cell fragments in mammals", "thrombocytes in non-mammalian vertebrates"], ["blood", "vessels"])
_organ("arteries", "circulatory", "Carry blood away from the central pump under pressure.", ["elastic arteries", "muscular arteries", "arterioles"], ["endothelium", "smooth muscle", "elastic connective tissue"], ["heart", "capillaries"])
_organ("veins", "circulatory", "Return blood to the central pump; many have valves and act as capacitance vessels.", ["venules", "medium veins", "large veins", "valves where present"], ["endothelium", "smooth muscle", "connective tissue"], ["capillaries", "heart"])
_organ("capillaries", "circulatory", "Exchange gases, nutrients, fluids, hormones and wastes with tissues.", ["endothelial wall", "basement membrane", "pericytes where present"], ["endothelium", "basement membrane"], ["arteries", "veins"])
_organ("lymphatic_vessels", "lymphatic", "Return interstitial fluid and transport immune cells and, in many vertebrates, absorbed lipids.", ["initial lymphatics", "collecting vessels", "valves", "ducts or equivalent return pathways"], ["endothelium", "smooth muscle in larger vessels"], ["circulatory", "immune"])
_organ("lymph_nodes", "lymphatic", "Filter lymph and provide organised sites for immune activation in many mammals.", ["cortex", "medulla", "sinuses", "lymphoid follicles"], ["lymphoid tissue", "stromal cells"], ["lymphatic_vessels", "immune"])
_organ("spleen", "lymphatic", "Filters circulating blood and supports immune and blood-cell functions; size and roles vary by species.", ["red pulp", "white pulp or analogues", "vascular sinuses"], ["lymphoid tissue", "vascular tissue"], ["blood", "immune"])
_organ("thymus", "immune", "T-cell development in many vertebrates, especially prominent in young life stages.", ["cortex", "medulla", "lymphoid epithelial support"], ["epithelial cells", "lymphocytes"], ["immune", "endocrine"])
_organ("tonsils", "immune", "Mucosa-associated immune tissue near the entry to respiratory and digestive tracts in many mammals.", ["lymphoid follicles", "crypts where present", "mucosal epithelium"], ["lymphoid tissue", "epithelium"], ["immune", "integumentary"])

# Respiratory
_organ("nasal_cavity", "respiratory", "Filters, warms, humidifies and samples inhaled air; may contain specialised scent structures.", ["turbinates/conchae", "mucosa", "olfactory region", "sinus openings where present"], ["mucosal epithelium", "vascular tissue", "cartilage/bone"], ["olfactory_epithelium", "lungs"])
_organ("pharynx", "respiratory", "Shared passage at the crossroads of respiratory and digestive pathways in many vertebrates.", ["nasal/oral portions", "muscular walls", "tonsillar tissue where present"], ["skeletal muscle", "mucosa"], ["oral_cavity", "larynx", "esophagus"])
_organ("larynx", "respiratory", "Airway protection and vocal production in many mammals.", ["cartilaginous framework", "vocal folds in many mammals", "intrinsic muscles"], ["cartilage", "muscle", "mucosa"], ["pharynx", "trachea"])
_organ("trachea", "respiratory", "Conducts and conditions air between upper airway and branching lungs where present.", ["cartilaginous rings or supports", "mucociliary lining", "smooth muscle"], ["cartilage", "epithelium", "smooth muscle"], ["larynx", "bronchi"])
_organ("bronchi", "respiratory", "Conduct air into branching airway trees in mammalian and many other lungs.", ["primary/secondary branches", "cartilage where present", "ciliated lining"], ["epithelium", "cartilage", "smooth muscle"], ["trachea", "bronchioles"])
_organ("bronchioles", "respiratory", "Small conducting airways that regulate airflow in lungs with branching bronchioles.", ["smooth muscle", "ciliated/nonciliated epithelium"], ["epithelium", "smooth muscle"], ["bronchi", "alveoli"])
_organ("lungs", "respiratory", "Gas-exchange organs; internal architecture differs across mammals, birds and reptiles.", ["alveoli in mammals", "parabronchi/air capillaries in birds", "faveoli or species-specific chambers in reptiles", "bronchial tree or analogue", "pleural interfaces where present"], ["epithelium", "capillaries", "elastic/connective tissue"], ["heart", "blood", "airway"])
_organ("alveoli", "respiratory", "Microscopic gas-exchange units in mammalian lungs.", ["type I and type II pneumocytes", "surfactant layer", "capillary network"], ["epithelium", "capillary endothelium"], ["lungs", "blood"])
_organ("diaphragm", "respiratory", "Major inspiratory muscle in mammals; absent as a true muscular diaphragm in birds and most reptiles.", ["central tendon", "muscular periphery", "attachments"], ["skeletal muscle", "tendon"], ["lungs", "ribs"])
_organ("air_sacs", "respiratory", "Thin-walled ventilatory bellows attached to avian lungs; most are not major gas-exchange surfaces.", ["cranial and caudal groups", "diverticula in some bones/regions", "airway connections"], ["thin connective membranes", "epithelium"], ["lungs", "sternum", "ribs"], "Avian airflow is not simply a mammalian in-and-out alveolar model; details vary by bird group.")
_organ("gills", "respiratory", "Water-to-blood gas-exchange structures in fish and some aquatic or larval forms.", ["filaments", "lamellae", "supporting arches", "water-flow channels"], ["epithelium", "capillaries", "cartilage/bone depending on taxon"], ["blood", "water_flow"])
_organ("spiracles", "respiratory", "External openings in insect tracheal breathing systems; relevant if custom invertebrates are defined.", ["valves", "tracheae", "tracheoles"], ["epithelium", "cuticle"], ["tracheal_system"])

# Digestive and metabolic
_organ("oral_cavity", "digestive", "Ingestion, food handling, initial processing, and in some species vocal or defensive actions.", ["lips/beak", "jaw", "teeth or grinding plates", "tongue", "palate", "salivary openings"], ["epithelium", "skeletal muscle", "bone/cartilage", "glands"], ["teeth", "tongue", "esophagus"])
_organ("salivary_glands", "digestive", "Lubricate food and provide enzymes or antimicrobial factors where present.", ["parotid/submandibular/sublingual in many mammals", "species-specific glands and ducts"], ["secretory epithelium", "ducts"], ["oral_cavity"])
_organ("esophagus", "digestive", "Moves swallowed material toward stomach or crop/forestomach using coordinated motility.", ["muscular wall", "mucosa", "sphincters where present"], ["epithelium", "smooth/skeletal muscle depending on region", "connective tissue"], ["pharynx", "stomach"])
_organ("stomach", "digestive", "Stores and processes ingested material; configuration ranges from simple chamber to specialised multi-compartment foregut.", ["cardia/fundus/body/antrum in humans", "mucosa and glands", "muscular layers", "species-specific compartments"], ["epithelium", "smooth muscle", "glands", "connective tissue"], ["esophagus", "small_intestine"])
_organ("rumen", "digestive", "Major microbial fermentation chamber in ruminants.", ["papillated mucosa", "fermentation contents", "microbial community", "muscular wall"], ["stratified epithelium", "smooth muscle", "microbiota"], ["reticulum", "microbiome"])
_organ("reticulum", "digestive", "Ruminant forestomach compartment that cooperates with the rumen in mixing and particle handling.", ["honeycomb mucosa", "muscular wall"], ["epithelium", "smooth muscle"], ["rumen"])
_organ("omasum", "digestive", "Ruminant compartment with many folds for particle handling and fluid absorption.", ["laminae/folds", "muscular wall"], ["epithelium", "smooth muscle"], ["reticulum", "abomasum"])
_organ("abomasum", "digestive", "Glandular, acid-secreting stomach compartment of ruminants.", ["glandular mucosa", "muscular wall"], ["epithelium", "glands", "smooth muscle"], ["omasum", "small_intestine"])
_organ("crop", "digestive", "Expandable foregut pouch used for food storage/softening in many birds and some other animals.", ["thin muscular wall", "mucosal lining"], ["epithelium", "smooth muscle"], ["esophagus", "gizzard"])
_organ("proventriculus", "digestive", "Glandular first stomach of birds, secreting digestive fluids before muscular grinding.", ["glandular lining", "muscular wall"], ["glands", "epithelium", "smooth muscle"], ["crop", "gizzard"])
_organ("gizzard", "digestive", "Muscular grinding chamber in birds and some other taxa.", ["thick muscular wall", "protective koilin layer in birds"], ["smooth muscle", "specialised epithelium"], ["proventriculus", "small_intestine"])
_organ("small_intestine", "digestive", "Major site of enzymatic digestion and nutrient absorption in mammals and many vertebrates.", ["duodenum", "jejunum", "ileum", "villi/microvilli in mammals", "species-specific folds"], ["epithelium", "smooth muscle", "vascular and lymphatic tissues"], ["stomach", "liver", "pancreas_exocrine"])
_organ("duodenum", "digestive", "Receives stomach contents, bile and pancreatic secretions in mammals.", ["mucosa", "submucosal glands in some species", "ampullary region where present"], ["epithelium", "smooth muscle", "glands"], ["stomach", "liver", "pancreas_exocrine"])
_organ("jejunum", "digestive", "Absorptive small-intestinal segment in mammals.", ["folds", "villi", "crypts", "lacteals"], ["epithelium", "smooth muscle", "vessels"], ["duodenum", "ileum"])
_organ("ileum", "digestive", "Distal small-intestinal segment; includes specialised immune tissue in many mammals.", ["mucosa", "Peyer patches in many mammals", "terminal junction"], ["epithelium", "lymphoid tissue", "smooth muscle"], ["jejunum", "cecum"])
_organ("cecum", "digestive", "Blind-ended fermentation or junctional chamber, varying greatly by species.", ["mucosa", "microbial habitat", "muscular wall"], ["epithelium", "smooth muscle", "microbiota"], ["ileum", "colon"])
_organ("colon", "digestive", "Water/electrolyte recovery and microbial fermentation to species-specific degrees.", ["ascending/transverse/descending/sigmoid segments in humans", "species-specific spiral or sacculated regions"], ["epithelium", "smooth muscle", "microbiota"], ["cecum", "rectum"])
_organ("rectum", "digestive", "Stores waste before elimination in many mammals.", ["mucosa", "muscular wall", "sphincter complex"], ["epithelium", "smooth muscle", "skeletal muscle at outlet in mammals"], ["colon", "anus"])
_organ("cloaca", "digestive", "Shared terminal chamber for digestive, urinary and reproductive tracts in birds, reptiles and many other vertebrates.", ["coprodeum/urodeum/proctodeum in birds", "species-specific compartments"], ["epithelium", "smooth muscle"], ["digestive", "renal", "reproductive"], "Mammals generally do not have a cloaca; monotremes are an exception.")
_organ("liver", "metabolic", "Processes nutrients, synthesises proteins, handles many toxins, produces bile in vertebrates.", ["lobes", "hepatic lobules or species analogues", "sinusoids", "bile canaliculi/ducts"], ["hepatocytes", "endothelium", "connective tissue"], ["digestive", "circulatory", "renal"])
_organ("gallbladder", "digestive", "Stores/concentrates bile in species that possess it.", ["mucosa", "muscular wall", "ducts"], ["epithelium", "smooth muscle"], ["liver", "small_intestine"], "Absent in some species; not universal.")
_organ("pancreas", "metabolic", "Mixed exocrine digestive enzyme and endocrine hormone organ in many vertebrates.", ["acinar exocrine tissue", "ducts", "islets/endocrine clusters", "species-specific lobulation"], ["glandular epithelium", "endocrine cells"], ["digestive", "endocrine"])
_organ("pancreas_exocrine", "digestive", "Provides digestive enzymes and bicarbonate through ducts in many vertebrates.", ["acini", "duct system"], ["secretory epithelium"], ["duodenum"])
_organ("microbiome", "microbiome", "Resident microbes affect fermentation, nutrient availability, barrier function and immune signalling.", ["gut communities", "skin/oral communities", "species-specific microbial niches"], ["microbial cells", "mucosal habitat"], ["digestive", "immune"])

# Renal, endocrine, reproductive, and tissue-level modules
_organ("kidneys", "renal", "Filter body fluid and regulate water, ions, acid/base balance and endocrine signals in vertebrates.", ["renal cortex/medulla in mammals", "nephrons or nephron-like units", "collecting ducts or clade analogues", "renal vessels"], ["epithelium", "capillaries", "interstitium"], ["blood", "endocrine"])
_organ("nephrons", "renal", "Filtering and selective-reabsorption units in vertebrate kidneys that possess nephrons.", ["glomerulus where present", "renal tubule", "loop segments where present", "collecting interface"], ["epithelium", "capillaries"], ["kidneys"])
_organ("ureters", "renal", "Transport urine or urine-like fluid from kidneys to storage/outlet structures.", ["muscular wall", "peristaltic segments"], ["epithelium", "smooth muscle"], ["kidneys", "urinary_bladder"])
_organ("urinary_bladder", "renal", "Stores urine in species that possess a bladder.", ["stretchable wall", "outlet sphincter or equivalent"], ["epithelium", "smooth muscle"], ["ureters", "urethra"], "Absent in many birds; do not assign the same storage model to all animals.")
_organ("urethra", "renal", "Outlet for urine; also part of reproductive pathway in many male mammals.", ["mucosa", "sphincter structures"], ["epithelium", "smooth/skeletal muscle"], ["urinary_bladder", "reproductive"])
_organ("hypothalamus", "endocrine", "Links neural state with pituitary and homeostatic control.", ["neurosecretory nuclei", "portal signalling in mammals"], ["neurons", "neurosecretory cells"], ["brain", "pituitary"])
_organ("pituitary", "endocrine", "Hormone control node under hypothalamic input in many vertebrates.", ["anterior/posterior regions in mammals", "species-specific divisions"], ["endocrine cells", "neural tissue"], ["hypothalamus", "endocrine"])
_organ("thyroid", "endocrine", "Regulates metabolism and development using thyroid hormones in many vertebrates.", ["follicles or species-specific structure"], ["endocrine epithelium"], ["circulatory", "endocrine"])
_organ("parathyroids", "endocrine", "Regulate calcium/phosphate signalling in many vertebrates; anatomy varies by clade.", ["glandular tissue", "species-specific arrangement"], ["endocrine cells"], ["skeleton", "renal"])
_organ("adrenal_glands", "endocrine", "Stress, salt balance and metabolic response; arrangement varies across clades.", ["cortex/medulla in mammals", "interrenal/chromaffin tissue in other vertebrates"], ["endocrine cells"], ["circulatory", "nervous"])
_organ("pineal", "endocrine", "Light-linked circadian signalling in many vertebrates.", ["pineal tissue or species analogues"], ["neuroendocrine cells"], ["nervous", "thermoregulation"])
_organ("thymus_endocrine", "endocrine", "Immune development and endocrine signalling at a level that varies by species and age.", ["thymic tissue", "age-related involution in many mammals"], ["epithelium", "lymphoid tissue"], ["immune", "endocrine"])
_organ("gonads", "reproductive", "Produce gametes and reproductive hormones; paired or unpaired arrangement depends on species.", ["ovarian tissue or testes", "duct connections", "support cells"], ["germ cells", "endocrine cells", "connective tissue"], ["endocrine", "circulatory"])
_organ("ovaries", "reproductive", "Produce oocytes and hormones in many female vertebrates.", ["follicles", "stroma", "species-specific number/seasonality"], ["germ cells", "endocrine cells", "connective tissue"], ["endocrine", "reproductive"])
_organ("uterus", "reproductive", "Supports embryo/fetal development in many placental mammals; form differs greatly by species.", ["endometrium", "myometrium", "cervix or equivalent"], ["epithelium", "smooth muscle", "connective tissue"], ["ovaries", "circulatory"])
_organ("testes", "reproductive", "Produce sperm and androgens in many male vertebrates.", ["seminiferous tubules", "support cells", "interstitial endocrine tissue"], ["germ cells", "endocrine cells", "connective tissue"], ["endocrine", "reproductive"])
_organ("reproductive_tract", "reproductive", "Species-specific ducts, accessory glands and external structures for gamete transfer or egg laying.", ["ducts", "accessory glands where present", "copulatory structures where present", "oviducts in egg-laying species"], ["epithelium", "smooth muscle", "connective tissue"], ["gonads", "endocrine"])
_organ("mammary_glands", "reproductive", "Milk production in mammals; development and functional status depend on sex, age and life stage.", ["alveoli", "ducts", "lobes", "teat/nipple"], ["secretory epithelium", "smooth muscle", "connective tissue"], ["endocrine", "circulatory"])
_organ("stem_cells", "hematopoietic", "A broad model label for repair-capable cell populations; potency and tissue access must be defined by spell rules.", ["tissue-resident progenitors", "marrow stem/progenitor populations", "specialised lineage populations"], ["progenitor cells"], ["immune", "metabolic"])
_organ("muscle_tissue", "muscular", "Collective muscle tissue model; separate skeletal, cardiac and smooth variants in detailed profiles.", ["skeletal muscle fibres", "cardiac muscle cells", "smooth muscle cells"], ["muscle", "connective tissue", "blood vessels", "nerves"], ["nervous", "circulatory"])
_organ("connective_tissue", "skeletal", "Matrix-rich tissue joining, separating, supporting or cushioning structures.", ["loose connective tissue", "dense connective tissue", "adipose", "fascia", "tendons/ligaments"], ["collagen", "elastin", "ground substance", "resident cells"], ["integumentary", "skeletal"])
_organ("venom_gland", "magical_specialisation", "Produces or stores venom/toxin in species that actually possess such an apparatus.", ["secretory cells", "reservoir", "duct", "fang/groove/canal delivery structure depending on species"], ["glandular epithelium", "muscle", "connective tissue"], ["oral_cavity", "nervous"], "Only venomous species have this system; fictional toxins require explicitly defined properties.")
_organ("fangs", "skeletal", "Specialised teeth or tooth analogues used for prey capture, defence or venom delivery.", ["crown", "root or attachment", "venom groove/canal in some snakes"], ["enamel/dentin or taxon-specific tissue", "periodontal attachment"], ["skull", "venom_gland"])
_organ("wings", "locomotor", "Flight surfaces requiring skeletal support, muscle power, control surfaces and suitable respiratory/metabolic supply.", ["shoulder girdle", "humerus/radius/ulna or wing analogues", "digits/feathers/membrane", "flight muscles"], ["bone", "muscle", "tendon", "feathers or membrane"], ["skeletal", "muscular", "respiratory"])
_organ("tail", "locomotor", "Balance, signalling, steering or locomotion; vertebrae and soft tissue differ by species.", ["caudal vertebrae or body extension", "tail muscles", "skin/feathers/scales"], ["bone/cartilage", "muscle", "connective tissue"], ["skeletal", "muscular"])
_organ("ossicones", "skeletal", "Giraffe-specific bony/cartilaginous head projections covered by skin and hair.", ["ossified core", "skin covering", "vascularised tissue"], ["bone/cartilage", "skin"], ["skull", "integumentary"], "Anatomical details vary by sex and age.")
_organ("crop_muscle", "digestive", "Muscular control around a crop or storage pouch when present.", ["muscular wall", "valve regions"], ["smooth muscle", "epithelium"], ["crop"])
_organ("earthworm_segment", "locomotor", "Repeated body unit with septa, muscles, bristles and local nerve/excretory structures.", ["circular muscle", "longitudinal muscle", "setae", "septum", "segmental ganglion", "nephridia pair in many segments"], ["epithelium", "muscle", "nerve", "coelomic lining"], ["hydrostatic_skeleton", "ventral_nerve_cord"])
_organ("ventral_nerve_cord", "nervous", "Segmented longitudinal nerve cord in annelids and many other invertebrates.", ["cerebral ganglia", "circumpharyngeal connectives", "segmental ganglia"], ["neurons", "glia"], ["earthworm_segment"])
_organ("cerebral_ganglia", "nervous", "Paired anterior ganglia coordinating sensory input and local nervous-system activity in the earthworm body plan; not a vertebrate brain.", ["supra-pharyngeal ganglia", "circumpharyngeal connectives"], ["neurons", "glia"], ["ventral_nerve_cord"])
_organ("nephridia", "renal", "Segmental excretory and osmoregulatory tubules in annelids and some other invertebrates.", ["ciliated funnel where present", "tubule", "external pore"], ["epithelium", "ciliated cells"], ["coelomic fluid", "earthworm_segment"])
_organ("aortic_arches", "circulatory", "Contractile arch vessels that help circulate blood in earthworms; commonly called hearts in basic references.", ["dorsal vessel", "ventral vessel", "lateral connecting vessels", "capillary beds"], ["vessel wall", "muscle", "fluid"], ["blood", "earthworm_segment"])
_organ("coelom", "skeletal", "Fluid-filled body cavity compartment that supports hydrostatic movement in annelids and other invertebrates.", ["coelomic fluid", "septa", "coelomic lining"], ["fluid", "epithelium"], ["hydrostatic_skeleton", "earthworm_segment"])
_organ("fire_sac", "magical_specialisation", "Fiction-only organ concept for a dragon-like species; stores/mediates an explicitly magical breath effect.", ["aether reservoir", "insulated duct", "ignition or release interface", "protective tissue"], ["fictional gland tissue", "insulating tissue"], ["lungs", "nervous"], "Not real anatomy. Use only where a designer wants a magical breath mechanism, and define costs, range, cooldown, heat and failure mode separately.")
_organ("aetheric_core", "magical_specialisation", "Fiction-only organ analogue that couples a body to a magical resource or field.", ["core matrix", "conduits", "stabilising tissue", "release focus"], ["fictional tissue"], ["nervous", "circulatory"], "World-magic design component, not a claim about real biology.")
_organ("scale_armour", "integumentary", "Fictional or taxon-specific hard dermal/epidermal defence covering.", ["scale plates", "attachment layer", "overlap joints", "underlying skin"], ["keratin", "bone/osteoderm where appropriate", "connective tissue"], ["skin", "skeletal"])
_organ("tusks", "skeletal", "Enlarged teeth used in defence, digging, display or food acquisition in certain animals.", ["enamel surface", "dentin core", "pulp", "root/base"], ["mineralised dental tissue", "connective tissue"], ["skull", "teeth"])
_organ("beak", "skeletal", "Keratin-covered jaw structures in birds and other beaked animals; shape is diet-specific.", ["upper/lower rhamphotheca", "supporting jaw bones", "sensory tip in some taxa"], ["keratin", "bone", "connective tissue"], ["skull", "oral_cavity"])
_organ("keel", "skeletal", "Projecting sternum ridge anchoring major flight muscles in many flying birds.", ["sternal ridge", "flight-muscle attachments"], ["bone", "tendon attachment"], ["sternum", "muscular"])
_organ("cloacal_bursa", "immune", "Bursa of Fabricius; avian lymphoid organ important in B-cell development, especially in young birds.", ["lymphoid follicles", "cloacal connection"], ["lymphoid tissue", "epithelium"], ["cloaca", "immune"], "A distinct avian structure; not a generic mammalian organ.")
_organ("airway_mucosa", "respiratory", "Mucus and cilia / analogous barriers in airway regions where present.", ["mucus layer", "ciliated cells in many mammalian airways", "immune cells"], ["epithelium", "mucus", "immune cells"], ["lungs", "immune"])
_organ("skin_cuticle", "integumentary", "Moist exchange surface of earthworms, rather than a mammalian skin with hair and sweat glands.", ["thin cuticle", "epidermis", "mucus film", "capillary bed underneath"], ["epithelium", "mucus", "connective support"], ["circulatory", "thermoregulation"], "Earthworm gas exchange requires a suitably moist surface; this is not a lung or gill.")
_organ("clitellum", "reproductive", "Glandular band in earthworms and related annelids involved in cocoon production.", ["glandular epidermis", "cocoon secretion"], ["glandular epithelium"], ["reproductive", "skin_cuticle"])
_organ("seminal_vesicles", "reproductive", "Species-dependent reproductive accessory structures in some annelids and mammals; the same name does not imply identical anatomy.", ["species-specific storage/secretion structures"], ["glandular or storage tissue"], ["gonads"])
_organ("serpentine_lung", "respiratory", "Elongated, species-dependent lung arrangement in snakes; often one dominant functional lung.", ["anterior vascular exchange region", "posterior air sac region in many snakes", "tracheal connections"], ["respiratory epithelium", "capillaries"], ["heart", "blood"], "Do not hard-code one left/right pattern across all snake species.")
_organ("cloacal_vent", "reproductive", "External shared outlet for excretory and reproductive tracts in birds, reptiles and many other vertebrates.", ["cloacal chamber interface", "species-specific external margins"], ["epithelium", "muscle"], ["cloaca", "renal", "reproductive"])
_organ("pneumatic_bones", "skeletal", "Bones invaded by air-sac diverticula in some birds and some other vertebrates, reducing mass or contributing to air spaces.", ["bone cortex", "air-filled diverticula where present", "marrow or cavity"], ["bone", "air sac lining"], ["air_sacs", "skeleton"], "Pneumaticity varies by species, age, and bone; never assume every bird bone is hollow.")
_organ("ruminant_microbiome", "microbiome", "Fermentation microbes in the ruminant forestomach digest otherwise difficult plant material.", ["bacteria", "archaea", "protozoa", "fungi", "fermentation substrates"], ["microbes", "forestomach mucosa"], ["rumen", "immune"])
_organ("nasal_discus", "sensory", "Specialised tactile/rhinarium structure in pigs and some other mammals for rooting and close contact.", ["dense connective support", "sensory innervation", "skin surface"], ["skin", "connective tissue", "sensory nerves"], ["olfactory_epithelium", "nervous"])

# Some identifiers used by the existing runtime; ensure every tracked physiological
# organ has a catalogue entry so it can be inspected through this library.
for _name, _system, _role in [
    ("autonomic_nerves", "nervous", "Automatic regulation of circulation, breathing and digestion."),
    ("heart_valves", "circulatory", "One-way control of central-pump flow."),
    ("red_blood_cells", "hematopoietic", "Oxygen transport cells, with lineage-specific morphology."),
    ("arteries", "circulatory", "Blood delivery away from the pump."), ("veins", "circulatory", "Blood return pathways."),
    ("capillaries", "circulatory", "Exchange between fluid and tissues."), ("blood_plasma", "circulatory", "Liquid transport phase of blood."),
    ("diaphragm", "respiratory", "Mammalian inspiratory muscle; not a universal vertebrate structure."),
    ("intestines", "digestive", "Small and large bowel regions; inspect species-specific segments for detail."),
    ("bladder", "renal", "Urine storage in species that possess a bladder."),
    ("lymphatic_system", "lymphatic", "Lymph fluid transport and immune-cell traffic."),
    ("immune_system", "immune", "Integrated defensive cells, barriers, tissues, and signalling."),
    ("endocrine_system", "endocrine", "Integrated hormone regulation and feedback."),
    ("skeletal_muscles", "muscular", "Voluntary/locomotor muscle, with clade-specific fibre and attachment designs."),
    ("stem_cells", "hematopoietic", "Abstract repair-capable cell populations; precise potency is tissue-specific."),
    ("skeleton", "skeletal", "Whole-body support structure or hydrostatic equivalent."),
    ("connective_tissue", "skeletal", "Structural matrix connecting and supporting tissues."),
    ("eyes", "sensory", "Vision structures vary by species and ecological niche."),
    ("ears", "sensory", "Auditory and balance-related structures, varying by clade."),
    ("inner_ear", "sensory", "Vestibular and auditory structures where present."),
    ("wings", "locomotor", "Flight or gliding surfaces where the species anatomy supports them."),
    ("tail", "locomotor", "Caudal structure used for balance, steering, signalling or locomotion."),
    ("gills", "respiratory", "Aquatic gas-exchange structures in compatible species."),
    ("fins", "locomotor", "Aquatic propulsion/control surfaces in compatible species."),
    ("reproductive_system", "reproductive", "Integrated species-specific reproductive structures."),
]:
    if _name not in ORGANS:
        _organ(_name, _system, _role)

# Shared high-level organ lists. Species may add/remove or replace specialised organs.
MAMMAL_SYSTEM_ORGANS: dict[str, list[str]] = {
    "integumentary": ["skin", "epidermis", "dermis", "hypodermis", "hair", "cutaneous_glands", "claws", "vibrissae"],
    "skeletal": ["skeleton", "bones", "skull", "vertebral_column", "ribs", "sternum", "joints", "cartilage", "ligaments", "connective_tissue", "bone_marrow"],
    "muscular": ["muscle_tissue", "skeletal_muscles", "tendons", "fascia", "heart"],
    "nervous": ["brain", "cerebrum", "cerebellum", "brainstem", "spinal_cord", "peripheral_nerves", "autonomic_nervous_system", "meninges", "enteric_nervous_system"],
    "sensory": ["eyes", "ears", "inner_ear", "olfactory_epithelium", "olfactory_bulbs", "tongue", "vibrissae"],
    "endocrine": ["hypothalamus", "pituitary", "pineal", "thyroid", "parathyroids", "adrenal_glands", "thymus_endocrine", "pancreas", "gonads"],
    "circulatory": ["heart", "heart_valves", "arteries", "veins", "capillaries", "blood", "blood_plasma", "red_blood_cells", "white_blood_cells", "platelets"],
    "lymphatic": ["lymphatic_vessels", "lymph_nodes", "spleen", "thymus"],
    "immune": ["immune_system", "white_blood_cells", "lymphatic_vessels", "lymph_nodes", "spleen", "thymus", "tonsils", "bone_marrow", "airway_mucosa"],
    "respiratory": ["nasal_cavity", "pharynx", "larynx", "trachea", "bronchi", "bronchioles", "lungs", "alveoli", "diaphragm", "airway_mucosa"],
    "digestive": ["oral_cavity", "teeth", "tongue", "salivary_glands", "esophagus", "stomach", "small_intestine", "duodenum", "jejunum", "ileum", "cecum", "colon", "rectum", "liver", "gallbladder", "pancreas_exocrine", "microbiome"],
    "metabolic": ["liver", "pancreas", "blood_plasma", "adrenal_glands", "thyroid"],
    "renal": ["kidneys", "nephrons", "ureters", "urinary_bladder", "urethra"],
    "reproductive": ["gonads", "ovaries", "uterus", "testes", "reproductive_tract", "mammary_glands"],
    "hematopoietic": ["bone_marrow", "red_blood_cells", "white_blood_cells", "platelets", "stem_cells", "blood"],
    "thermoregulation": ["skin", "cutaneous_glands", "hypodermis", "skeletal_muscles", "blood", "adrenal_glands"],
    "microbiome": ["microbiome"],
    "locomotor": ["skeleton", "bones", "joints", "cartilage", "ligaments", "tendons", "fascia", "skeletal_muscles", "claws", "tail"],
}

BIRD_SYSTEM_ORGANS: dict[str, list[str]] = {
    "integumentary": ["skin", "epidermis", "dermis", "feathers", "feather_follicles", "cutaneous_glands", "beak", "claws"],
    "skeletal": ["skeleton", "bones", "skull", "vertebral_column", "ribs", "sternum", "keel", "pneumatic_bones", "joints", "cartilage", "ligaments", "connective_tissue", "bone_marrow"],
    "muscular": ["muscle_tissue", "skeletal_muscles", "tendons", "fascia", "heart"],
    "nervous": ["brain", "cerebrum", "cerebellum", "brainstem", "spinal_cord", "peripheral_nerves", "autonomic_nervous_system", "meninges"],
    "sensory": ["eyes", "ears", "inner_ear", "olfactory_epithelium", "tongue", "olfactory_bulbs"],
    "endocrine": ["hypothalamus", "pituitary", "pineal", "thyroid", "parathyroids", "adrenal_glands", "pancreas", "gonads"],
    "circulatory": ["heart", "heart_valves", "arteries", "veins", "capillaries", "blood", "blood_plasma", "red_blood_cells", "white_blood_cells", "platelets"],
    "lymphatic": ["lymphatic_vessels", "spleen", "thymus", "cloacal_bursa"],
    "immune": ["immune_system", "white_blood_cells", "lymphatic_vessels", "spleen", "thymus", "cloacal_bursa", "bone_marrow", "airway_mucosa"],
    "respiratory": ["nasal_cavity", "trachea", "lungs", "air_sacs", "airway_mucosa"],
    "digestive": ["beak", "oral_cavity", "tongue", "esophagus", "crop", "proventriculus", "gizzard", "small_intestine", "duodenum", "jejunum", "ileum", "cecum", "colon", "cloaca", "liver", "pancreas_exocrine", "microbiome"],
    "metabolic": ["liver", "pancreas", "blood_plasma", "adrenal_glands", "thyroid"],
    "renal": ["kidneys", "nephrons", "ureters", "cloaca"],
    "reproductive": ["gonads", "ovaries", "testes", "reproductive_tract", "cloaca"],
    "hematopoietic": ["bone_marrow", "red_blood_cells", "white_blood_cells", "platelets", "stem_cells", "blood"],
    "thermoregulation": ["feathers", "skin", "blood", "skeletal_muscles"],
    "microbiome": ["microbiome"],
    "locomotor": ["skeleton", "bones", "joints", "cartilage", "ligaments", "tendons", "skeletal_muscles", "wings", "feathers", "keel", "claws"],
}

REPTILE_SYSTEM_ORGANS: dict[str, list[str]] = {
    **{k: list(v) for k, v in MAMMAL_SYSTEM_ORGANS.items()},
    "integumentary": ["skin", "epidermis", "dermis", "hypodermis", "scales", "cutaneous_glands", "claws"],
    "respiratory": ["nasal_cavity", "pharynx", "trachea", "serpentine_lung", "lungs", "airway_mucosa"],
    "renal": ["kidneys", "nephrons", "ureters", "cloaca"],
    "reproductive": ["gonads", "ovaries", "testes", "reproductive_tract", "cloaca", "cloacal_vent"],
    "thermoregulation": ["skin", "scales", "blood", "skeletal_muscles"],
    "locomotor": ["skeleton", "bones", "skull", "vertebral_column", "ribs", "joints", "cartilage", "ligaments", "tendons", "skeletal_muscles", "tail", "claws"],
}
ANNULID_SYSTEM_ORGANS: dict[str, list[str]] = {
    "integumentary": ["skin_cuticle", "skin", "cutaneous_glands"],
    "skeletal": ["hydrostatic_skeleton", "coelom", "earthworm_segment", "connective_tissue"],
    "muscular": ["muscle_tissue", "skeletal_muscles", "earthworm_segment"],
    "nervous": ["ventral_nerve_cord", "peripheral_nerves", "brain"],
    "sensory": ["skin_cuticle", "olfactory_epithelium", "vibrissae"],
    "circulatory": ["blood", "aortic_arches", "arteries", "veins", "capillaries"],
    "respiratory": ["skin_cuticle"],
    "digestive": ["oral_cavity", "pharynx", "esophagus", "crop", "gizzard", "small_intestine", "intestines", "rectum"],
    "renal": ["nephridia"],
    "reproductive": ["gonads", "reproductive_tract", "clitellum", "seminal_vesicles"],
    "thermoregulation": ["skin_cuticle"],
    "locomotor": ["hydrostatic_skeleton", "earthworm_segment", "skeletal_muscles"],
}

# Canonical human adult skeletal inventory; counts refer to typical adult bones.
# Variable sesamoids, sutural bones and individual anatomy variation can change totals.
HUMAN_BONES = {
    "summary": {"typical_adult_count": 206, "axial_count": 80, "appendicular_count": 126, "caveat": "Typical adult count; age, fusion, sesamoids and individual variation can alter counts."},
    "axial": {
        "cranial_bones": {"count": 8, "items": ["frontal (1)", "parietal (2)", "temporal (2)", "occipital (1)", "sphenoid (1)", "ethmoid (1)"]},
        "facial_bones": {"count": 14, "items": ["mandible (1)", "maxillae (2)", "zygomatic bones (2)", "nasal bones (2)", "lacrimal bones (2)", "palatine bones (2)", "inferior nasal conchae (2)", "vomer (1)"]},
        "auditory_ossicles": {"count": 6, "items": ["malleus right/left (2)", "incus right/left (2)", "stapes right/left (2)"]},
        "hyoid": {"count": 1, "items": ["hyoid bone (1)"]},
        "vertebral_column": {"count": 26, "items": ["atlas C1 (1)", "axis C2 (1)", "cervical vertebrae C3-C7 (5)", "thoracic vertebrae T1-T12 (12)", "lumbar vertebrae L1-L5 (5)", "sacrum (1, fused from usually 5 sacral vertebrae)", "coccyx (1, usually fused from 3-5 coccygeal vertebrae)"]},
        "thoracic_cage": {"count": 25, "items": ["sternum (1)", "true ribs 1-7, right and left (14)", "false ribs 8-10, right and left (6)", "floating ribs 11-12, right and left (4)"]},
    },
    "appendicular": {
        "pectoral_girdle": {"count": 4, "items": ["clavicles right/left (2)", "scapulae right/left (2)"]},
        "upper_limbs": {"count": 60, "items": ["humeri right/left (2)", "radii right/left (2)", "ulnae right/left (2)", "carpals: scaphoid, lunate, triquetrum, pisiform, trapezium, trapezoid, capitate, hamate in each hand (16)", "metacarpals I-V in each hand (10)", "proximal phalanges (10)", "middle phalanges (8; absent in thumbs)", "distal phalanges (10)"]},
        "pelvic_girdle": {"count": 2, "items": ["hip bone right/left (2; each formed from fused ilium, ischium and pubis)"]},
        "lower_limbs": {"count": 60, "items": ["femora right/left (2)", "patellae right/left (2)", "tibiae right/left (2)", "fibulae right/left (2)", "tarsals: talus, calcaneus, navicular, cuboid, medial/intermediate/lateral cuneiform in each foot (14)", "metatarsals I-V in each foot (10)", "proximal phalanges (10)", "middle phalanges (8)", "distal phalanges (10)"]},
    },
}

# Species profiles. Quantitative multipliers are gameplay priors rather than measured
# zoological performance scores. Detailed anatomy notes are species-level summaries.
SPECIES: dict[str, dict] = {
    "human": {"label": "Human", "classification": "real", "clade": "mammal / primate", "base": "mammal", "systems": MAMMAL_SYSTEM_ORGANS,
        "skeleton": {"type": "endoskeleton", "count": 206, "inventory": "human_adult", "regions": ["axial skeleton", "pectoral girdle", "upper limbs", "pelvic girdle", "lower limbs", "joints", "cartilage", "ligaments", "tendons"]},
        "circulation": {"type": "closed_double", "pump": "four_chambered_heart", "oxygen_carrier": "haemoglobin in mature anucleate erythrocytes", "notes": "Systemic and pulmonary circuits; individual values depend on age, size, activity and condition."},
        "respiration": {"type": "alveolar_lungs", "structures": ["nasal cavity", "pharynx", "larynx", "trachea", "bronchi", "bronchioles", "alveoli", "diaphragm", "intercostal muscles"], "notes": "Mammalian tidal ventilation."},
        "digestion": {"type": "monogastric_omnivore", "structures": ["oral cavity", "teeth", "salivary glands", "esophagus", "stomach", "duodenum", "jejunum", "ileum", "cecum", "colon", "rectum", "liver", "gallbladder", "pancreas"], "notes": "Microbiota and liver/pancreatic secretions interact with nutrient uptake."},
        "integument": {"covering": "skin, variable hair, nails, sweat and sebaceous glands", "layers": ["epidermis", "dermis", "hypodermis"], "notes": "Sweating and skin blood-flow are important for heat loss."},
        "blood": {"cell_profile": "mammalian", "erythrocytes_nucleated": False, "haemoglobin": True, "platelet_model": "platelets", "volume_fraction_estimate": [0.06, 0.08]},
        "thermoregulation": "endothermic; physiological and behavioural regulation", "movement_mode": "terrestrial / bipedal", "senses": ["binocular vision", "hearing", "olfaction", "taste", "touch", "proprioception", "vestibular sense"],
        "reproduction": {"mode": "placental mammal", "female_structures": ["ovaries", "oviducts", "uterus", "cervix", "vagina", "mammary glands"], "male_structures": ["testes", "epididymides", "ductus deferentes", "accessory glands", "penis"], "note": "An individual does not necessarily possess every sex-specific structure; model configuration may omit or alter these."},
        "traits": {"strength": 1.0, "speed": 1.0, "endurance": 1.0, "durability": 1.0, "senses": 1.0, "reflexes": 1.0, "regeneration": 1.0, "recovery": 1.0}, "simulation": {"blood_volume_l": 5.0, "body_temperature_c": 37.0, "note": "Reference baseline only; not a clinical normal range or diagnostic system."},
        "evidence": "real-species-summary"},
    "lion": {"label": "Lion", "classification": "real", "clade": "mammal / felid", "base": "mammal", "systems": MAMMAL_SYSTEM_ORGANS,
        "skeleton": {"type": "endoskeleton", "count": None, "inventory": "felid", "regions": ["axial skeleton", "flexible vertebral column", "scapula/forelimb", "digitigrade hindlimb", "tail", "retractile claw apparatus", "jaw and carnassial teeth"]},
        "circulation": {"type": "closed_double", "pump": "four_chambered_heart", "oxygen_carrier": "mammalian erythrocytes", "notes": "Detailed parameters depend on age, mass, exercise, captivity and health."},
        "respiration": {"type": "alveolar_lungs", "notes": "Powerful mammalian ventilatory and exertion systems."}, "digestion": {"type": "obligate_carnivore_simple_stomach", "structures": ["canines", "carnassial teeth", "shorter carnivore-adapted gut", "stomach", "small intestine", "liver", "pancreas"]},
        "integument": {"covering": "fur; scent glands; paw pads; protractile/retractile claw apparatus", "special": ["mane in adult males of many populations; not a universal body trait"]},
        "blood": {"cell_profile": "mammalian", "erythrocytes_nucleated": False, "platelet_model": "platelets", "volume_fraction_estimate": [0.06, 0.08]}, "thermoregulation": "endothermic", "movement_mode": "digitigrade quadruped", "senses": ["binocular forward vision", "dim-light vision supported by tapetum lucidum", "hearing", "olfaction", "vibrissal touch"],
        "special_organs": ["vibrissae", "claws", "tusks"], "traits": {"strength": 1.8, "speed": 1.3, "endurance": 1.0, "durability": 1.2, "senses": 1.5, "reflexes": 1.4, "regeneration": 1.0, "recovery": 1.0}, "simulation": {"blood_volume_l": 7.0}, "notes": ["Felid-specialised vertebral flexibility and forelimb musculature.", "Claws are anatomically specialised; retraction mechanics are not merely a status effect."], "evidence": "real-species-summary"},
    "tiger": {"label": "Tiger", "classification": "real", "clade": "mammal / felid", "base": "mammal", "systems": MAMMAL_SYSTEM_ORGANS,
        "skeleton": {"type": "endoskeleton", "count": None, "inventory": "felid", "regions": ["axial skeleton", "flexible vertebral column", "powerful shoulder/forelimb", "digitigrade hindlimb", "tail", "claw apparatus", "jaw and carnassial teeth"]},
        "circulation": {"type": "closed_double", "pump": "four_chambered_heart", "oxygen_carrier": "mammalian erythrocytes"}, "respiration": {"type": "alveolar_lungs"},
        "digestion": {"type": "obligate_carnivore_simple_stomach", "structures": ["canines", "carnassial teeth", "stomach", "small intestine", "liver", "pancreas"]},
        "integument": {"covering": "striped fur, whiskers, paw pads, claws"}, "blood": {"cell_profile": "mammalian", "erythrocytes_nucleated": False, "platelet_model": "platelets", "volume_fraction_estimate": [0.06, 0.08]},
        "thermoregulation": "endothermic", "movement_mode": "digitigrade quadruped", "senses": ["binocular vision", "dim-light vision", "hearing", "olfaction", "vibrissal touch"],
        "special_organs": ["vibrissae", "claws", "tusks"], "traits": {"strength": 1.9, "speed": 1.25, "endurance": 1.0, "durability": 1.25, "senses": 1.45, "reflexes": 1.35, "regeneration": 1.0, "recovery": 1.0}, "simulation": {"blood_volume_l": 10.0},
        "notes": ["Tiger-specific size/marking differences do not imply a different basic organ-system plan from other felids."], "evidence": "real-species-summary"},
    "snake": {"label": "Snake (generalised squamate)" , "classification": "real", "clade": "reptile / squamate", "base": "reptile", "systems": REPTILE_SYSTEM_ORGANS,
        "skeleton": {"type": "endoskeleton", "count": None, "inventory": "snake", "regions": ["many trunk vertebrae and ribs", "elongated skull and mobile jaw joints", "no limbs in most snakes", "tail vertebrae", "pelvic vestiges in some lineages"]},
        "circulation": {"type": "closed_double", "pump": "generally_three_chambered_reptile_heart", "oxygen_carrier": "nucleated erythrocytes", "notes": "Intracardiac shunting and circulation patterns vary by species and state."},
        "respiration": {"type": "elongated_reptilian_lungs", "structures": ["trachea", "elongated lung; frequently one dominant right lung", "posterior saccular region in many species"], "notes": "Left/right lung development varies across snake lineages; do not assume one exact layout."},
        "digestion": {"type": "carnivorous_elastic_ingestion", "structures": ["kinetic skull/jaw", "esophagus", "stretchable stomach", "elongated intestine", "liver", "cloaca"]},
        "integument": {"covering": "keratinised scales; periodic ecdysis; little glandular surface activity", "special": ["ventral scutes", "scale sensory interface"]}, "blood": {"cell_profile": "reptilian", "erythrocytes_nucleated": True, "platelet_model": "thrombocytes", "volume_fraction_estimate": [0.05, 0.08]},
        "thermoregulation": "ectothermic; behaviour and external heat strongly affect body temperature", "movement_mode": "limbless undulation", "senses": ["chemical sensing via tongue and vomeronasal pathway in many snakes", "vision varying by species", "ground vibration and touch", "infrared pit organs in certain lineages only"],
        "special_organs": ["serpentine_lung", "vomeronasal_organ", "fangs", "venom_gland", "cloaca"], "traits": {"strength": 1.0, "speed": 1.05, "endurance": 0.8, "durability": 0.9, "senses": 1.35, "reflexes": 1.2, "regeneration": 1.0, "recovery": 0.8}, "simulation": {"blood_volume_l": 0.25, "body_temperature_c": 25.0},
        "notes": ["Venom apparatus is optional: most snakes are not to be modelled as possessing identical venom delivery systems.", "No true muscular diaphragm; ventilation mechanics differ from mammals."], "evidence": "real-species-summary"},
    "earthworm": {"label": "Earthworm (generalised annelid)", "classification": "real", "clade": "annelid / invertebrate", "base": "annelid", "systems": ANNULID_SYSTEM_ORGANS,
        "skeleton": {"type": "hydrostatic", "count": 0, "inventory": "segmented_hydrostatic", "regions": ["segmented body", "coelom and septa", "circular and longitudinal muscles", "setae/bristles", "no bones or vertebral column"]},
        "circulation": {"type": "closed_vessel_system", "pump": "contractile aortic arches / pseudohearts depending on description and species", "oxygen_carrier": "haemoglobin may be dissolved in circulating fluid; not mammalian red cells", "notes": "Vessel arrangement and arch number vary across annelid taxa."},
        "respiration": {"type": "cutaneous_gas_exchange", "structures": ["moist cuticle/epidermis", "subsurface capillaries"], "notes": "Drying can critically impair gas exchange."},
        "digestion": {"type": "segmented_detritivore_gut", "structures": ["mouth/prostomium", "pharynx", "esophagus", "crop", "gizzard", "intestine", "anus"]},
        "integument": {"covering": "moist cuticle/mucus-coated skin; setae for grip; clitellum in mature individuals of many species"},
        "blood": {"cell_profile": "annelid", "erythrocytes_nucleated": None, "platelet_model": "species-specific cells/clotting", "volume_fraction_estimate": None, "notes": "Do not use mammalian litre or erythrocyte assumptions."},
        "thermoregulation": "ectothermic", "movement_mode": "peristaltic burrowing", "senses": ["touch", "light response", "chemical sensing", "vibration response"], "special_organs": ["hydrostatic_skeleton", "earthworm_segment", "ventral_nerve_cord", "nephridia", "aortic_arches", "skin_cuticle", "clitellum"],
        "traits": {"strength": 0.15, "speed": 0.2, "endurance": 0.8, "durability": 0.25, "senses": 0.55, "reflexes": 0.45, "regeneration": 1.15, "recovery": 0.9}, "simulation": {"blood_volume_l": 0.01, "body_temperature_c": 18.0},
        "notes": ["Hermaphroditic reproductive anatomy is common in earthworms, but reproductive modes differ across annelids.", "The catalogue is a reference to a typical earthworm, not every worm: roundworms, flatworms and marine annelids differ greatly."], "evidence": "real-species-summary"},
    "eagle": {"label": "Eagle", "classification": "real", "clade": "bird / raptor", "base": "bird", "systems": BIRD_SYSTEM_ORGANS,
        "skeleton": {"type": "endoskeleton_partly_pneumatic", "count": None, "inventory": "avian_raptor", "regions": ["skull/beak", "cervical series", "furcula", "coracoid and scapula", "keel-bearing sternum", "wing bones", "synsacrum", "tibiotarsus", "tarsometatarsus", "digits/talons"]},
        "circulation": {"type": "closed_double", "pump": "four_chambered_heart", "oxygen_carrier": "nucleated erythrocytes"},
        "respiration": {"type": "rigid_lungs_with_air_sacs", "structures": ["rigid lungs", "parabronchi/air capillaries", "cranial and caudal air sacs", "airway pathways"], "notes": "Air sacs act mainly as ventilatory bellows; they are not simply mammalian alveoli."},
        "digestion": {"type": "raptor_avian", "structures": ["hooked beak", "esophagus", "crop may be present", "proventriculus", "gizzard", "intestine", "cloaca"]}, "integument": {"covering": "contour and flight feathers; keratin beak; scales on feet"},
        "blood": {"cell_profile": "avian", "erythrocytes_nucleated": True, "platelet_model": "thrombocytes", "volume_fraction_estimate": [0.07, 0.12]}, "thermoregulation": "endothermic", "movement_mode": "powered flight / perching", "senses": ["high acuity vision", "raptorial depth judgement", "hearing", "balance", "species-specific olfaction"],
        "special_organs": ["wings", "air_sacs", "keel", "pneumatic_bones", "beak", "claws"], "traits": {"strength": 0.6, "speed": 1.7, "endurance": 1.2, "durability": 0.8, "senses": 1.9, "reflexes": 1.7, "regeneration": 1.0, "recovery": 1.0}, "simulation": {"blood_volume_l": 0.35}, "evidence": "real-species-summary"},
    "owl": {"label": "Owl", "classification": "real", "clade": "bird / raptor", "base": "bird", "systems": BIRD_SYSTEM_ORGANS,
        "skeleton": {"type": "endoskeleton_partly_pneumatic", "count": None, "inventory": "avian_raptor", "regions": ["avian axial skeleton", "keel/sternum", "wing bones", "specialised neck vertebrae", "talons"]},
        "circulation": {"type": "closed_double", "pump": "four_chambered_heart", "oxygen_carrier": "nucleated erythrocytes"}, "respiration": {"type": "rigid_lungs_with_air_sacs"},
        "digestion": {"type": "avian_glandular_stomach_and_gizzard", "structures": ["beak", "esophagus", "proventriculus", "gizzard", "intestine", "cloaca"]},
        "integument": {"covering": "soft specialised flight feathers, facial disk feathers, feathered legs in many species"}, "blood": {"cell_profile": "avian", "erythrocytes_nucleated": True, "platelet_model": "thrombocytes", "volume_fraction_estimate": [0.07, 0.12]},
        "thermoregulation": "endothermic", "movement_mode": "powered flight / perch", "senses": ["large light-sensitive eyes in many species", "facial-disk sound collection", "strong directional hearing in many species", "silent-flight feather specialisation"],
        "special_organs": ["wings", "air_sacs", "keel", "pneumatic_bones", "beak", "claws"], "traits": {"strength": 0.55, "speed": 1.35, "endurance": 1.05, "durability": 0.75, "senses": 1.9, "reflexes": 1.65, "regeneration": 1.0, "recovery": 1.0}, "simulation": {"blood_volume_l": 0.18}, "evidence": "real-species-summary"},
    "raven": {"label": "Raven", "classification": "real", "clade": "bird / corvid", "base": "bird", "systems": BIRD_SYSTEM_ORGANS,
        "skeleton": {"type": "endoskeleton_partly_pneumatic", "count": None, "inventory": "avian_corvid", "regions": ["skull/beak", "cervical series", "furcula", "keel", "wing bones", "synsacrum", "legs and grasping feet"]},
        "circulation": {"type": "closed_double", "pump": "four_chambered_heart", "oxygen_carrier": "nucleated erythrocytes"}, "respiration": {"type": "rigid_lungs_with_air_sacs"},
        "digestion": {"type": "avian_omnivore", "structures": ["beak", "esophagus", "crop often present or variable", "proventriculus", "gizzard", "intestine", "cloaca"]},
        "integument": {"covering": "contour feathers and keratin beak"}, "blood": {"cell_profile": "avian", "erythrocytes_nucleated": True, "platelet_model": "thrombocytes", "volume_fraction_estimate": [0.07, 0.12]},
        "thermoregulation": "endothermic", "movement_mode": "flight / walking / perching", "senses": ["vision", "hearing", "touch", "smell varying by species"], "special_organs": ["wings", "air_sacs", "keel", "pneumatic_bones", "beak", "claws"],
        "traits": {"strength": 0.4, "speed": 1.2, "endurance": 1.45, "durability": 0.75, "senses": 1.25, "reflexes": 1.25, "regeneration": 1.0, "recovery": 1.0}, "simulation": {"blood_volume_l": 0.25}, "evidence": "real-species-summary"},
    "falcon": {"label": "Falcon", "classification": "real", "clade": "bird / raptor", "base": "bird", "systems": BIRD_SYSTEM_ORGANS,
        "skeleton": {"type": "endoskeleton_partly_pneumatic", "count": None, "inventory": "avian_raptor", "regions": ["avian skeleton", "high-speed flight wing frame", "keel", "tail control feathers", "talons"]}, "circulation": {"type": "closed_double", "pump": "four_chambered_heart", "oxygen_carrier": "nucleated erythrocytes"}, "respiration": {"type": "rigid_lungs_with_air_sacs"},
        "digestion": {"type": "raptor_avian", "structures": ["hooked beak", "proventriculus", "gizzard", "intestine", "cloaca"]}, "integument": {"covering": "flight feathers, contour feathers, scaled feet"}, "blood": {"cell_profile": "avian", "erythrocytes_nucleated": True, "platelet_model": "thrombocytes", "volume_fraction_estimate": [0.07, 0.12]},
        "thermoregulation": "endothermic", "movement_mode": "powered flight / high-speed stoop in some falcons", "senses": ["acute vision", "flight visual tracking", "hearing"], "special_organs": ["wings", "air_sacs", "keel", "pneumatic_bones", "beak", "claws"],
        "traits": {"strength": 0.45, "speed": 1.9, "endurance": 1.1, "durability": 0.75, "senses": 1.85, "reflexes": 1.8, "regeneration": 1.0, "recovery": 1.0}, "simulation": {"blood_volume_l": 0.12}, "evidence": "real-species-summary"},
    "parrot": {"label": "Parrot", "classification": "real", "clade": "bird / psittaciform", "base": "bird", "systems": BIRD_SYSTEM_ORGANS,
        "skeleton": {"type": "endoskeleton_partly_pneumatic", "count": None, "inventory": "avian_perching", "regions": ["curved beak support", "furcula and keel", "wing bones", "zygodactyl feet with opposed toe pairs"]}, "circulation": {"type": "closed_double", "pump": "four_chambered_heart", "oxygen_carrier": "nucleated erythrocytes"}, "respiration": {"type": "rigid_lungs_with_air_sacs"},
        "digestion": {"type": "avian_herbivore_or_omnivore", "structures": ["strong curved beak", "crop", "proventriculus", "gizzard", "intestine", "cloaca"]}, "integument": {"covering": "contour and flight feathers; powder-down in some taxa"},
        "blood": {"cell_profile": "avian", "erythrocytes_nucleated": True, "platelet_model": "thrombocytes", "volume_fraction_estimate": [0.07, 0.12]}, "thermoregulation": "endothermic", "movement_mode": "flight / climbing / grasping", "senses": ["vision", "hearing", "beak/tongue mechanosensation", "balance"],
        "special_organs": ["wings", "air_sacs", "keel", "beak", "claws"], "traits": {"strength": 0.45, "speed": 1.1, "endurance": 1.1, "durability": 0.8, "senses": 1.2, "reflexes": 1.25, "regeneration": 1.0, "recovery": 1.0}, "simulation": {"blood_volume_l": 0.12}, "evidence": "real-species-summary"},
    "pigeon": {"label": "Pigeon", "classification": "real", "clade": "bird / columbid", "base": "bird", "systems": BIRD_SYSTEM_ORGANS,
        "skeleton": {"type": "endoskeleton_partly_pneumatic", "count": None, "inventory": "avian_flight", "regions": ["keel", "furcula", "wing frame", "synsacrum", "tail fan"]}, "circulation": {"type": "closed_double", "pump": "four_chambered_heart", "oxygen_carrier": "nucleated erythrocytes"}, "respiration": {"type": "rigid_lungs_with_air_sacs"},
        "digestion": {"type": "avian_seed_eater", "structures": ["beak", "crop", "proventriculus", "gizzard", "intestine", "cloaca"]}, "integument": {"covering": "contour feathers and flight feathers"}, "blood": {"cell_profile": "avian", "erythrocytes_nucleated": True, "platelet_model": "thrombocytes", "volume_fraction_estimate": [0.07, 0.12]},
        "thermoregulation": "endothermic", "movement_mode": "powered flight / walking", "senses": ["vision", "navigation-related sensory systems", "hearing"], "special_organs": ["wings", "air_sacs", "keel", "pneumatic_bones", "beak", "claws"],
        "traits": {"strength": 0.35, "speed": 1.3, "endurance": 1.4, "durability": 0.7, "senses": 1.2, "reflexes": 1.35, "regeneration": 1.0, "recovery": 1.0}, "simulation": {"blood_volume_l": 0.04}, "evidence": "real-species-summary"},
    "giraffe": {"label": "Giraffe", "classification": "real", "clade": "mammal / ruminant ungulate", "base": "mammal", "systems": MAMMAL_SYSTEM_ORGANS,
        "skeleton": {"type": "endoskeleton", "count": None, "inventory": "large_ruminant", "regions": ["seven elongated cervical vertebrae", "long limb bones", "fused distal metapodials", "cloven hooves", "ossicones", "tail" ]},
        "circulation": {"type": "closed_double", "pump": "four_chambered_heart_with_high_pressure_adaptations", "oxygen_carrier": "mammalian erythrocytes", "notes": "Long-neck cerebral perfusion depends on specialised cardiovascular adaptations; do not assign human pressures."},
        "respiration": {"type": "alveolar_lungs", "notes": "Large mammalian lungs; respiratory mechanics scale with body size."},
        "digestion": {"type": "ruminant_foregut_fermenter", "structures": ["rumen", "reticulum", "omasum", "abomasum", "small intestine", "large intestine", "liver", "pancreas"]},
        "integument": {"covering": "short patterned coat, skin, tail tuft, ossicone skin/hair"}, "blood": {"cell_profile": "mammalian", "erythrocytes_nucleated": False, "platelet_model": "platelets", "volume_fraction_estimate": [0.06, 0.08]},
        "thermoregulation": "endothermic", "movement_mode": "large ungulate quadruped", "senses": ["vision", "hearing", "olfaction", "long-range environmental monitoring"], "special_organs": ["rumen", "reticulum", "omasum", "abomasum", "ossicones", "tail"],
        "traits": {"strength": 2.0, "speed": 1.25, "endurance": 1.35, "durability": 1.4, "senses": 1.05, "reflexes": 0.9, "regeneration": 1.0, "recovery": 1.0}, "simulation": {"blood_volume_l": 35.0}, "evidence": "real-species-summary"},
    "cow": {"label": "Domestic Cattle", "classification": "real", "clade": "mammal / ruminant bovine", "base": "mammal", "systems": MAMMAL_SYSTEM_ORGANS,
        "skeleton": {"type": "endoskeleton", "count": None, "inventory": "large_ruminant", "regions": ["axial skeleton", "cloven hooves", "fused metapodials", "horn cores in horned breeds", "tail"]}, "circulation": {"type": "closed_double", "pump": "four_chambered_heart", "oxygen_carrier": "mammalian erythrocytes"}, "respiration": {"type": "alveolar_lungs"},
        "digestion": {"type": "ruminant_foregut_fermenter", "structures": ["rumen", "reticulum", "omasum", "abomasum", "small intestine", "large intestine", "liver", "pancreas", "ruminant_microbiome"]},
        "integument": {"covering": "skin, coat, sweat/sebaceous structures varying with breed, cloven hooves"}, "blood": {"cell_profile": "mammalian", "erythrocytes_nucleated": False, "platelet_model": "platelets", "volume_fraction_estimate": [0.06, 0.08]},
        "thermoregulation": "endothermic; rumen fermentation contributes heat", "movement_mode": "ungulate quadruped", "senses": ["wide field vision", "hearing", "olfaction", "taste"], "special_organs": ["rumen", "reticulum", "omasum", "abomasum", "ruminant_microbiome", "tusks"],
        "traits": {"strength": 1.7, "speed": 0.85, "endurance": 1.25, "durability": 1.35, "senses": 1.0, "reflexes": 0.8, "regeneration": 1.0, "recovery": 1.0}, "simulation": {"blood_volume_l": 25.0}, "evidence": "real-species-summary"},
    "pig": {"label": "Domestic Pig", "classification": "real", "clade": "mammal / suid omnivore", "base": "mammal", "systems": MAMMAL_SYSTEM_ORGANS,
        "skeleton": {"type": "endoskeleton", "count": None, "inventory": "suid", "regions": ["axial skeleton", "cloven hoof with accessory digits", "strong snout/nasal support", "canine tusks in some sexes/lines"]}, "circulation": {"type": "closed_double", "pump": "four_chambered_heart", "oxygen_carrier": "mammalian erythrocytes"}, "respiration": {"type": "alveolar_lungs"},
        "digestion": {"type": "monogastric_omnivore", "structures": ["snout/mouth", "stomach", "small intestine", "cecum", "colon", "liver", "pancreas", "microbiome"]},
        "integument": {"covering": "sparse-to-moderate bristles depending on breed, skin, specialised snout disk; cooling relies substantially on behaviour/environment"}, "blood": {"cell_profile": "mammalian", "erythrocytes_nucleated": False, "platelet_model": "platelets", "volume_fraction_estimate": [0.06, 0.08]},
        "thermoregulation": "endothermic; behavioural cooling is important", "movement_mode": "ungulate quadruped", "senses": ["strong olfaction", "hearing", "vision", "snout touch"], "special_organs": ["nasal_discus", "tusks"],
        "traits": {"strength": 1.1, "speed": 0.95, "endurance": 1.0, "durability": 1.1, "senses": 1.25, "reflexes": 0.9, "regeneration": 1.0, "recovery": 1.0}, "simulation": {"blood_volume_l": 6.0}, "evidence": "real-species-summary"},
    "horse": {"label": "Horse", "classification": "real", "clade": "mammal / perissodactyl", "base": "mammal", "systems": MAMMAL_SYSTEM_ORGANS,
        "skeleton": {"type": "endoskeleton", "count": None, "inventory": "equid", "regions": ["single weight-bearing hoof per limb", "elongated metapodials", "long limbs", "mobile cervical and thoracolumbar regions"]}, "circulation": {"type": "closed_double", "pump": "four_chambered_heart", "oxygen_carrier": "mammalian erythrocytes", "notes": "Exercise physiology and spleen-mediated red-cell mobilisation are notable in horses."}, "respiration": {"type": "alveolar_lungs", "notes": "High ventilatory demand during galloping; no true gallbladder in horses."},
        "digestion": {"type": "hindgut_fermenter_monogastric", "structures": ["stomach", "small intestine", "large cecum", "large colon", "small colon", "liver", "pancreas"]}, "integument": {"covering": "hair coat, mane, tail, hoof keratin"}, "blood": {"cell_profile": "mammalian", "erythrocytes_nucleated": False, "platelet_model": "platelets", "volume_fraction_estimate": [0.06, 0.08]}, "thermoregulation": "endothermic", "movement_mode": "cursorial quadruped", "senses": ["wide lateral vision", "hearing", "olfaction", "touch"], "special_organs": ["tail", "claws"], "traits": {"strength": 1.5, "speed": 1.6, "endurance": 1.7, "durability": 1.0, "senses": 1.1, "reflexes": 1.2, "regeneration": 1.0, "recovery": 1.0}, "simulation": {"blood_volume_l": 35.0}, "evidence": "real-species-summary"},
    "dog": {"label": "Domestic Dog", "classification": "real", "clade": "mammal / canid", "base": "mammal", "systems": MAMMAL_SYSTEM_ORGANS,
        "skeleton": {"type": "endoskeleton", "count": None, "inventory": "canid", "regions": ["axial skeleton", "quadruped limb bones", "long muzzle/jaw varies by breed", "tail varies by breed"]}, "circulation": {"type": "closed_double", "pump": "four_chambered_heart", "oxygen_carrier": "mammalian erythrocytes"}, "respiration": {"type": "alveolar_lungs"}, "digestion": {"type": "carnivorous_omnivore_monogastric", "structures": ["stomach", "small intestine", "colon", "liver", "pancreas"]}, "integument": {"covering": "coat varies widely; paw pads and claws"}, "blood": {"cell_profile": "mammalian", "erythrocytes_nucleated": False, "platelet_model": "platelets", "volume_fraction_estimate": [0.06, 0.08]}, "thermoregulation": "endothermic; panting supports heat loss", "movement_mode": "digitigrade quadruped", "senses": ["olfaction", "hearing", "vision", "touch"], "special_organs": ["vibrissae", "claws", "tail"], "traits": {"strength": 1.0, "speed": 1.35, "endurance": 1.2, "durability": 0.9, "senses": 1.6, "reflexes": 1.3, "regeneration": 1.0, "recovery": 1.0}, "simulation": {"blood_volume_l": 1.2}, "evidence": "real-species-summary"},
    # Fantasy profiles are explicitly provisional, editable synthesis patterns.
    "dragon": {"label": "Dragon (fantasy template)", "classification": "fictional-template", "clade": "fictional vertebrate-like hexapod", "base": "mammal", "systems": MAMMAL_SYSTEM_ORGANS,
        "skeleton": {"type": "fictional_endoskeleton", "count": None, "inventory": "dragon_hexapod", "regions": ["axial trunk and neck", "four load-bearing limbs", "two wing limbs", "reinforced sternum/shoulders", "tail", "horns/crest attachment", "dense skull and jaw"]}, "circulation": {"type": "fictional_closed_double", "pump": "four-chambered default hypothesis", "oxygen_carrier": "designer-defined", "notes": "This is a design hypothesis, not established biology."},
        "respiration": {"type": "fictional_lungs_plus_optional_aetheric_fire_sac", "structures": ["lungs", "airways", "optional fire_sac", "optional aetheric_core"], "notes": "Breath weapon is an optional magical subsystem. Define fuel/energy, heat dissipation, cooldown and failure modes."},
        "digestion": {"type": "fictional_large_predator", "structures": ["jaw/teeth", "esophagus", "stomach", "intestines", "liver", "pancreas"]}, "integument": {"covering": "overlapping scale armour, optional osteoderms, under-skin thermal insulation"},
        "blood": {"cell_profile": "designer-defined vertebrate analogue", "erythrocytes_nucleated": "designer-defined", "platelet_model": "designer-defined", "volume_fraction_estimate": None}, "thermoregulation": "designer-defined endotherm or ectotherm; default to active thermal exchange", "movement_mode": "quadrupedal plus powered flight if mass/wing physics permit", "senses": ["forward vision", "olfaction", "hearing", "vibration sensing optional"],
        "special_organs": ["wings", "tail", "scale_armour", "fire_sac", "aetheric_core"], "traits": {"strength": 3.0, "speed": 1.3, "endurance": 1.4, "durability": 2.5, "senses": 1.5, "reflexes": 1.1, "regeneration": 1.1, "recovery": 1.1}, "simulation": {"blood_volume_l": 60.0}, "notes": ["Every dragon trait is a user-editable fantasy assumption. Size, wing loading, thermal balance, and breath mechanics need explicit world rules."], "evidence": "fictional-design-proposal"},
    "griffin": {"label": "Griffin (fantasy template)", "classification": "fictional-template", "clade": "fictional mammal-avian hybrid", "base": "mammal", "systems": MAMMAL_SYSTEM_ORGANS,
        "skeleton": {"type": "fictional_hybrid_endoskeleton", "count": None, "inventory": "griffin_hybrid", "regions": ["feline-like trunk/pelvis/hind limbs", "avian skull and beak", "paired wings and reinforced pectoral girdle", "tail", "talons"]}, "circulation": {"type": "fictional_closed_double", "pump": "four-chambered design assumption", "oxygen_carrier": "designer-defined"}, "respiration": {"type": "bird-like lungs_with_air_sacs_as_optional_hypothesis", "structures": ["lungs", "optional air_sacs", "airway"], "notes": "Hybrid lung/air-sac anatomy is a fantasy design decision."},
        "digestion": {"type": "carnivorous_hybrid", "structures": ["beak/jaw", "teeth where retained", "esophagus", "stomach", "intestines", "liver", "pancreas"]}, "integument": {"covering": "fur over body, feathers over wings, keratin beak, talons"}, "blood": {"cell_profile": "designer-defined", "erythrocytes_nucleated": "designer-defined", "platelet_model": "designer-defined"}, "thermoregulation": "fictional endotherm default", "movement_mode": "quadrupedal plus powered flight if wings and mass permit", "senses": ["predatory vision", "hearing", "olfaction", "vibrissal/mechanical touch optional"], "special_organs": ["wings", "air_sacs", "beak", "claws", "tail"],
        "traits": {"strength": 2.0, "speed": 1.5, "endurance": 1.2, "durability": 1.2, "senses": 1.65, "reflexes": 1.45, "regeneration": 1.0, "recovery": 1.0}, "simulation": {"blood_volume_l": 8.0}, "notes": ["Use as a modular hybrid template, not an assertion that griffins have a coherent canonical anatomy."], "evidence": "fictional-design-proposal"},
    "goblin": {"label": "Goblin (fantasy template)", "classification": "fictional-template", "clade": "fictional humanoid", "base": "mammal", "systems": MAMMAL_SYSTEM_ORGANS,
        "skeleton": {"type": "humanoid_endoskeleton", "count": None, "inventory": "goblin_humanoid", "regions": ["humanoid skull", "vertebral column", "narrow shoulder girdle", "hands/feet", "jaw/teeth variation"]}, "circulation": {"type": "four-chambered mammal-like default hypothesis"}, "respiration": {"type": "alveolar_mammal-like default hypothesis"}, "digestion": {"type": "omnivore_monogastric default hypothesis"}, "integument": {"covering": "user-defined skin, hair and pigmentation; large ears or specialised skin are optional"}, "blood": {"cell_profile": "fictional mammal-like by default"}, "thermoregulation": "fictional endotherm default", "movement_mode": "bipedal / climbing", "senses": ["hearing emphasis optional", "low-light vision optional", "smell"], "special_organs": [], "traits": {"strength": 0.8, "speed": 1.1, "endurance": 0.9, "durability": 0.75, "senses": 1.3, "reflexes": 1.2, "regeneration": 1.0, "recovery": 1.0}, "simulation": {"blood_volume_l": 2.0}, "notes": ["All features are editable fantasy defaults; there is no scientific goblin anatomy."], "evidence": "fictional-design-proposal"},
    "orc": {"label": "Orc (fantasy template)", "classification": "fictional-template", "clade": "fictional robust humanoid", "base": "mammal", "systems": MAMMAL_SYSTEM_ORGANS,
        "skeleton": {"type": "robust_humanoid_endoskeleton", "count": None, "inventory": "orc_humanoid", "regions": ["robust axial skeleton", "thick limb bones", "large joint surfaces", "jaw/tusk attachment" ]}, "circulation": {"type": "four-chambered mammal-like default hypothesis"}, "respiration": {"type": "alveolar_mammal-like default hypothesis"}, "digestion": {"type": "omnivore_monogastric default hypothesis"}, "integument": {"covering": "thicker dermal layers, scars, hair and pigmentation are configurable"}, "blood": {"cell_profile": "fictional mammal-like by default"}, "thermoregulation": "fictional endotherm default", "movement_mode": "bipedal", "senses": ["vision", "hearing", "olfaction"], "special_organs": ["tusks"], "traits": {"strength": 1.6, "speed": 0.95, "endurance": 1.3, "durability": 1.3, "senses": 1.0, "reflexes": 0.95, "regeneration": 1.0, "recovery": 1.2}, "simulation": {"blood_volume_l": 6.0}, "notes": ["Musculoskeletal robustness and tusks are design options, not a single universal fantasy canon."], "evidence": "fictional-design-proposal"},
    "elf": {"label": "Elf (fantasy template)", "classification": "fictional-template", "clade": "fictional gracile humanoid", "base": "mammal", "systems": MAMMAL_SYSTEM_ORGANS,
        "skeleton": {"type": "gracile_humanoid_endoskeleton", "count": None, "inventory": "elf_humanoid", "regions": ["humanoid axial skeleton", "long-limbed appendicular skeleton", "ear cartilage variation" ]}, "circulation": {"type": "four-chambered mammal-like default hypothesis"}, "respiration": {"type": "alveolar_mammal-like default hypothesis"}, "digestion": {"type": "omnivore_monogastric default hypothesis"}, "integument": {"covering": "skin, hair, nails; pointed pinnae optional"}, "blood": {"cell_profile": "fictional mammal-like by default"}, "thermoregulation": "fictional endotherm default", "movement_mode": "bipedal", "senses": ["hearing acuity optional", "low-light vision optional", "balance"], "special_organs": [], "traits": {"strength": 0.9, "speed": 1.2, "endurance": 1.25, "durability": 0.9, "senses": 1.45, "reflexes": 1.3, "regeneration": 1.0, "recovery": 1.2}, "simulation": {"blood_volume_l": 4.0}, "notes": ["Lifespan, senses, bone density and organ differences must be explicitly chosen by the world designer; no universal elf biology exists."], "evidence": "fictional-design-proposal"},
}

# Additional cross-clade structures. These are reusable anatomy records, not
# separate spell implementations. Some are lineage-specific; fictional anatomy
# remains explicitly designer-defined.
_EXTRA_STRUCTURES = [
    ("trunk", "locomotor", "Highly mobile muscular proboscis used for grasping, sensing and manipulation."),
    ("tusk", "skeletal", "Elongated tooth used for defence, display or environmental manipulation."),
    ("large_pinnae", "sensory", "Large external ears involved in sound collection and heat exchange in some mammals."),
    ("foot_cushion", "locomotor", "Load-distributing soft-tissue structure beneath the foot."),
    ("wing_membrane", "locomotor", "Membranous flight surface supported by elongated digits in bats."),
    ("elongated_wing_digits", "skeletal", "Elongated hand/finger bones that support a bat wing membrane."),
    ("echolocation_organs", "sensory", "Structures supporting biological sound emission and echo reception in species that use echolocation."),
    ("webbed_feet", "locomotor", "Digit webbing that increases surface area for swimming."),
    ("osteoderms", "integumentary", "Bony deposits within the skin that provide armour in some reptiles."),
    ("secondary_palate", "digestive", "Structure separating oral and nasal passages in crocodilians and some other animals."),
    ("conical_teeth", "digestive", "Conical teeth adapted for gripping prey rather than complex chewing."),
    ("crocodilian_heart", "circulatory", "Four-chambered crocodilian heart with specialised circulation pathways."),
    ("salt_glands", "renal", "Specialised glands for salt handling in selected animals."),
    ("permeable_skin", "integumentary", "Skin participating in water balance and, in many amphibians, gas exchange."),
    ("buccal_cavity", "respiratory", "Mouth-cavity structures that can contribute to ventilatory mechanics in some amphibians."),
    ("tympanum", "sensory", "External or surface-associated sound-transmitting membrane in many amphibians."),
    ("metamorphic_gills", "respiratory", "Life-stage-dependent aquatic gas-exchange structures in amphibian larvae."),
    ("cartilaginous_skeleton", "skeletal", "Skeleton built primarily from cartilage rather than mineralised bone."),
    ("gill_slits", "respiratory", "Openings associated with aquatic gill ventilation."),
    ("pectoral_fins", "locomotor", "Paired fins used for steering, lift or manoeuvring in aquatic animals."),
    ("dorsal_fins", "locomotor", "Median fins contributing to stability and directional control in aquatic animals."),
    ("caudal_fin", "locomotor", "Tail fin used for thrust and directional control in aquatic animals."),
    ("dermal_denticles", "integumentary", "Tooth-like dermal scales that influence protection and water flow in cartilaginous fish."),
    ("lateral_line", "sensory", "Mechanosensory system detecting local water movement and pressure gradients in many fish."),
    ("ampullae_of_lorenzini", "sensory", "Electroreceptive structures found in sharks and related cartilaginous fish."),
    ("spiral_valve", "digestive", "Spiral intestinal structure that increases effective absorptive path length in many sharks."),
    ("oil_rich_liver", "metabolic", "Large lipid-rich liver that contributes to energy storage and buoyancy in many sharks."),
    ("blowhole", "respiratory", "External breathing opening in cetaceans; it connects to lungs, not gills."),
    ("melon", "sensory", "Specialised forehead tissue involved in sound focusing in toothed whales."),
    ("flippers", "locomotor", "Modified forelimbs used for steering and stability in aquatic mammals."),
    ("tail_flukes", "locomotor", "Horizontal tail flukes providing propulsion in cetaceans."),
    ("blubber", "integumentary", "Subcutaneous fat layer supporting insulation and energy storage in many marine mammals."),
    ("mantle", "locomotor", "Muscular body wall involved in ventilation and jet propulsion in cephalopods."),
    ("arms", "locomotor", "Flexible appendages with distributed control and grasping capability in cephalopods."),
    ("suckers", "locomotor", "Adhesive/grasping structures on cephalopod arms."),
    ("siphon", "locomotor", "Muscular funnel directing water for propulsion and waste movement in cephalopods."),
    ("systemic_heart", "circulatory", "Main pump delivering circulating fluid to the body in organisms with specialised multi-pump circulation."),
    ("branchial_hearts", "circulatory", "Auxiliary pumps that move blood toward the gills in cephalopods."),
    ("chromatophores", "integumentary", "Pigment-control structures supporting colour change and signalling in many cephalopods."),
    ("distributed_ganglia", "nervous", "Regional nerve centres coordinating local movement and sensation."),
    ("ink_sac", "defence", "Ink-producing defensive organ in many cephalopods."),
    ("statocysts", "sensory", "Balance and orientation organs in many invertebrates."),
    ("cephalopod_hemocyanin", "circulatory", "Copper-containing oxygen carrier in many cephalopod circulatory systems."),
    ("exoskeleton", "integumentary", "External supportive cuticle, with composition and moult patterns varying by arthropod."),
    ("chelicerae", "feeding", "Paired anterior appendages in chelicerates; may support feeding or venom delivery."),
    ("pedipalps", "sensory", "Paired appendages involved in sensing, handling prey or reproduction in arachnids."),
    ("spinnerets", "locomotor", "Appendages that extrude and direct silk from silk-producing glands."),
    ("book_lungs", "respiratory", "Layered respiratory structures found in some arachnids."),
    ("tracheae", "respiratory", "Branched air-conducting tubes in some arthropods and other invertebrates."),
    ("venom_glands", "defence", "Secretory structures that produce venom in species and individuals that possess them."),
    ("silk_glands", "integumentary", "Secretory structures producing silk proteins in spiders and selected other arthropods."),
    ("simple_eyes", "sensory", "Simple visual organs with taxon-specific acuity and arrangement."),
    ("hemolymph", "circulatory", "Circulating fluid in animals with an open circulatory system."),
    ("malpighian_tubules", "renal", "Excretory and osmoregulatory structures in many arthropods."),
    ("carapace", "skeletal", "Dorsal shell structure in turtles and some other animals."),
    ("plastron", "skeletal", "Ventral shell structure in turtles."),
    ("keratin_beak", "feeding", "Keratinous beak used for feeding in turtles and some other animals."),
    ("olfactory_turbinates", "sensory", "Nasal structures that increase olfactory surface area in many mammals."),
    ("whisker_follicles", "sensory", "Follicle structures supporting tactile whisker sensation."),
    ("fat_reserves", "metabolic", "Adipose reserves available for insulation and energy storage."),
    ("plantigrade_paws", "locomotor", "Foot structures that contact the ground across much of the sole."),
    ("large_claws", "locomotor", "Large keratin claws used in digging, climbing, gripping or defence."),
    # Expanded human/vertebrate detail for spells that need an addressable target.
    ("cerebral_cortex", "nervous", "Major cerebral processing tissue; detailed regional function is not continuously simulated."),
    ("hippocampus", "nervous", "Memory formation and spatial-navigation structure in many vertebrates."),
    ("amygdala", "nervous", "Threat, salience and affect-related processing structure in many vertebrates."),
    ("hypothalamus", "endocrine", "Coordinates selected autonomic, hormonal, thermal and homeostatic responses."),
    ("pituitary_gland", "endocrine", "Hormone-releasing gland with multiple regulatory axes."),
    ("pineal_gland", "endocrine", "Melatonin and daily timing-related endocrine structure in many vertebrates."),
    ("thalamus", "nervous", "Major relay and processing structure for many sensory and motor signals."),
    ("basal_ganglia", "nervous", "Movement selection and action-learning circuitry in vertebrates."),
    ("corpus_callosum", "nervous", "Interhemispheric axon tract prominent in placental mammals."),
    ("meninges", "nervous", "Protective connective-tissue coverings surrounding brain and spinal cord in vertebrates."),
    ("cerebrospinal_fluid", "nervous", "Fluid surrounding and supporting central nervous-system structures."),
    ("cranial_nerves", "nervous", "Nerve pathways linking head structures to the central nervous system."),
    ("vagus_nerve", "nervous", "Major parasympathetic and visceral sensory/motor pathway in many vertebrates."),
    ("sympathetic_chain", "nervous", "Autonomic nerve chain involved in rapid systemic responses in many vertebrates."),
    ("retina", "sensory", "Light-sensitive neural tissue in camera-type eyes."),
    ("cornea", "sensory", "Transparent anterior surface contributing to eye protection and optical power."),
    ("lens", "sensory", "Optical structure focusing light onto a retinal surface."),
    ("optic_nerve", "sensory", "Nerve pathway transmitting visual signals from the retina."),
    ("cochlea", "sensory", "Inner-ear structure supporting frequency-coded hearing in many vertebrates."),
    ("semicircular_canals", "sensory", "Vestibular structures sensing angular acceleration in many vertebrates."),
    ("vestibular_nerve", "sensory", "Nerve pathway carrying balance/orientation information."),
    ("taste_buds", "sensory", "Chemical-sensory structures for taste; layout differs by lineage."),
    ("olfactory_epithelium", "sensory", "Chemical-sensory surface supporting olfaction in many animals."),
    ("salivary_glands", "digestive", "Secretory glands that lubricate food and begin some digestive processes."),
    ("tonsils", "immune", "Mucosal lymphoid tissues at selected entryways in some vertebrates."),
    ("thymus", "immune", "T-cell maturation organ in many vertebrates."),
    ("lymphatic_vessels", "lymphatic", "Vessels returning tissue fluid and transporting immune cells in many vertebrates."),
    ("lymphocytes", "immune", "Adaptive and innate-like immune cell families; exact types vary by lineage."),
    ("sinoatrial_node", "circulatory", "Primary pacemaker structure in many vertebrate hearts."),
    ("atrioventricular_node", "circulatory", "Electrical conduction relay between atria and ventricles in many vertebrate hearts."),
    ("cardiac_conduction_system", "circulatory", "Specialised tissue coordinating heart contraction timing."),
    ("aorta", "circulatory", "Major systemic artery in many vertebrates."),
    ("vena_cava", "circulatory", "Major venous return route in many vertebrates."),
    ("coronary_arteries", "circulatory", "Vessels supplying cardiac tissue in many vertebrates."),
    ("pulmonary_arteries", "circulatory", "Vessels carrying blood toward respiratory gas-exchange surfaces in lung-bearing vertebrates."),
    ("pulmonary_veins", "circulatory", "Vessels returning oxygenated blood from lungs in many vertebrates."),
    ("arterioles", "circulatory", "Small arteries that help regulate local vascular resistance."),
    ("venules", "circulatory", "Small veins receiving blood from capillary beds."),
    ("alveoli", "respiratory", "Microscopic gas-exchange sacs in mammalian lungs; not universal across lung-bearing clades."),
    ("pleura", "respiratory", "Membranous surfaces around mammalian lungs that aid low-friction movement."),
    ("bronchi", "respiratory", "Major branches of the airway tree in many lung-breathing vertebrates."),
    ("bronchioles", "respiratory", "Smaller airway branches distributing gas within lung tissue."),
    ("larynx", "respiratory", "Airway and sound-production structure in many tetrapods."),
    ("duodenum", "digestive", "First small-intestinal segment receiving stomach contents and digestive secretions in many vertebrates."),
    ("jejunum", "digestive", "Small-intestinal region important in nutrient absorption in many mammals."),
    ("ileum", "digestive", "Distal small-intestinal region with lineage-specific absorptive and immune roles."),
    ("appendix", "digestive", "Cecal-associated structure present in some mammals; size and role vary widely."),
    ("colon", "digestive", "Large-intestinal segment involved in water and electrolyte processing in many vertebrates."),
    ("rectum", "digestive", "Distal digestive tract for temporary waste storage before elimination in many animals."),
    ("gallbladder", "digestive", "Stores and concentrates bile in species that possess one."),
    ("bile_ducts", "digestive", "Channels moving bile from liver/gallbladder to the intestine where present."),
    ("pancreatic_islets", "endocrine", "Endocrine pancreatic cell clusters regulating aspects of blood nutrient balance in many vertebrates."),
    ("glomeruli", "renal", "Filtration structures within kidneys of many vertebrates."),
    ("nephrons", "renal", "Functional filtration and processing units in vertebrate kidneys."),
    ("ureters", "renal", "Channels transporting urine from kidneys to storage or elimination structures."),
    ("urethra", "renal", "Outlet channel for urine in many vertebrates; anatomy varies by sex and species."),
    ("synovial_membrane", "skeletal", "Joint-lining tissue contributing synovial fluid in synovial joints."),
    ("bursae", "skeletal", "Fluid-filled low-friction sacs around selected tendons and joints."),
    ("rotator_cuff", "muscular", "Shoulder muscle-tendon group stabilising the shoulder in humans and related anatomy."),
    ("forelimb_muscle_groups", "muscular", "Grouped forelimb force-producing structures for species-specific locomotion."),
    ("hindlimb_muscle_groups", "muscular", "Grouped hindlimb force-producing structures for species-specific locomotion."),
    ("jaw_muscles", "muscular", "Muscles generating bite and feeding forces."),
    ("intercostal_muscles", "respiratory", "Body-wall muscles contributing respiration in many vertebrates."),
    ("tail_muscles", "locomotor", "Muscle groups controlling tail motion, steering, balance or propulsion."),
    ("longitudinal_muscles", "muscular", "Lengthwise muscles used in body bending or peristaltic locomotion, including annelids."),
    ("circular_muscles", "muscular", "Circumferential muscles used in body-wall shaping and peristaltic locomotion."),
    ("body_wall_muscles", "muscular", "Muscular body wall supporting movement in forms without limb-based locomotion."),
    ("clitellum", "reproductive", "Thickened annelid body region involved in cocoon formation in mature earthworms and relatives."),
    ("seminal_vesicles", "reproductive", "Reproductive structures with lineage-specific roles in gamete maturation or storage."),
    ("crop", "digestive", "Expandable storage region in the digestive tract of many birds and some invertebrates."),
    ("gizzard", "digestive", "Muscular grinding region in birds and some invertebrates."),
    ("cecum", "digestive", "Blind-ended gut pouch important in fermentation or digestion in some lineages."),
    ("rumen", "digestive", "Fermentation chamber in ruminant mammals."),
    ("reticulum", "digestive", "Ruminant stomach compartment involved in sorting and fermentation."),
    ("omasum", "digestive", "Ruminant stomach compartment involved in particle processing and fluid absorption."),
    ("abomasum", "digestive", "Acid-secreting true stomach compartment in ruminants."),
    ("ruminant_microbiome", "microbiome", "Microbial community supporting fermentation in ruminants."),
    ("antlers", "skeletal", "Seasonally grown bony head appendages in cervids; not the same structure as permanent horns."),
    ("horn_core", "skeletal", "Bony core supporting a keratin-covered horn in many bovids."),
    ("pouch", "reproductive", "Marsupial pouch and associated skin/mammary structures in species that possess one."),
    ("kangaroo_hindlimbs", "locomotor", "Elongated hindlimbs specialised for hopping in macropods."),
    ("bird_keel", "skeletal", "Sternal keel providing attachment area for major flight muscles in many flying birds."),
    ("feather_follicles", "integumentary", "Follicles producing feathers in birds."),
    ("comb", "integumentary", "Fleshy head appendage in some birds with display and thermoregulatory roles."),
    ("wattle", "integumentary", "Fleshy appendage in some birds, often involved in display and heat exchange."),
    ("egg_shell_gland", "reproductive", "Oviduct region depositing shell material in egg-laying species where present."),
    ("antennae", "sensory", "Paired sensory appendages in insects and many crustaceans."),
    ("compound_eyes", "sensory", "Multi-faceted eyes common in insects and many crustaceans."),
    ("mandibles", "feeding", "Paired jaws used for cutting, crushing or carrying food in arthropods and other groups."),
    ("six_legs", "locomotor", "Three pairs of walking legs in insects."),
    ("spiracles", "respiratory", "External openings connecting to tracheal respiration in many arthropods."),
    ("sting", "defence", "Modified ovipositor or related apparatus used for defence in some insects."),
    ("pollen_baskets", "locomotor", "Hind-leg or body structures carrying pollen in some bees."),
    ("wing_bars", "locomotor", "Articulated wing structural elements in flying insects."),
    ("silk_spinning_structures", "integumentary", "Silk-producing structures in non-spider invertebrates or fictional silk users."),
    ("multiple_necks", "locomotor", "Fictional repeated neck support and control structures for multi-headed creatures."),
    ("regenerative_buds", "developmental", "Fictional or species-specific regenerative growth sites; behaviour must be explicitly defined."),
    ("fire_resistant_mucosa", "integumentary", "Fictional heat-resistant protective lining for creatures with magical fire emission."),
    ("aetheric_core", "magical_specialisation", "User-defined fictional structure for a magical organism; no biological reality is implied."),
    ("aetheric_nerves", "magical_specialisation", "Fictional signal pathways for user-defined magical physiology."),
    ("mana_sensing_pits", "sensory", "Fictional sensory structures responsive to an explicitly defined magical field."),
    ("gill_rakers", "feeding", "Structures filtering or sorting particles and prey around fish gill arches in many species."),
    ("swim_bladder", "respiratory", "Gas-filled organ aiding buoyancy in many bony fish; absent in many lineages."),
    ("spiracles_of_shark", "respiratory", "Additional water-entry openings near the head in many sharks and rays."),
    ("electric_organs", "specialised", "Specialised tissues producing electrical discharges in selected fish."),
    ("electric_receptors", "sensory", "Receptors detecting electrical fields in selected aquatic animals."),
    ("feathered_scales", "integumentary", "Overlapping feather/scale interface in birds and designer hybrid forms."),
    ("egg_sac", "reproductive", "Protective egg-carrying structure in selected invertebrates and fictional creatures."),
    ("spermatheca", "reproductive", "Structure storing sperm in many invertebrates and some other animals."),
    ("book_gills", "respiratory", "Layered gill structures in selected aquatic arthropods."),
    ("walking_legs", "locomotor", "General multi-jointed limb group used by arthropods and other invertebrates."),
    ("crushing_claw", "feeding", "Specialised claw used to crush hard prey or materials."),
    ("regenerative_limb_bud", "developmental", "Regrowth zone used by selected animals or fictional species after limb loss."),
    ("photophores", "integumentary", "Light-producing organs in selected marine organisms."),
    ("lateral_olfactory_sac", "sensory", "Species-specific olfactory chamber or sensory sac in a custom body plan."),
    ("dorsal_vessel", "circulatory", "Dorsal contractile vessel in selected invertebrate circulation systems."),
    ("nerve_net", "nervous", "Diffuse neural network rather than a centralised vertebrate brain/spinal-cord plan."),
    ("tentacles", "locomotor", "Flexible appendages used for capture, feeding, locomotion or sensation."),
    ("nematocysts", "defence", "Cnidarian stinging organelles; species behaviour is reference-only unless implemented."),
    ("gastrovascular_cavity", "digestive", "Combined digestive and distribution cavity in some simple-bodied animals."),
    ("basal_disc", "locomotor", "Adhesive or anchoring body surface in sessile or slow-moving simple animals."),
    ("baleen", "feeding", "Keratinous filter-feeding plates in baleen whales."),
    ("rostrum", "feeding", "Projecting head/jaw structure; shape and function vary widely by species."),
    ("pyrogenic_sac", "magical_specialisation", "Fictional organ template for a user-defined fire-emission mechanism."),
    ("ash_reconstitution_core", "magical_specialisation", "Fictional structural record for a phoenix-like regeneration concept; not a real organ."),
    ("glandular_venom_reservoir", "defence", "Reservoir for specialised venom secretion in species or fictional designs that define one."),
    ("mantle_pen", "skeletal", "Internal flexible support structure in squid and some cephalopods."),
    ("crab_gills", "respiratory", "Gills housed within a crustacean branchial chamber."),
    ("walking_legs", "locomotor", "General multi-jointed limb group used by arthropods and other invertebrates."),
]
# Expanded body-plan details used by additional stock species and freely composed
# user-created species. These are anatomical reference entries; presence alone does
# not imply that each structure has a bespoke dynamic solver.
_EXTRA_STRUCTURES.extend([
    ("opposable_thumb", "locomotor", "Grasping digit with a range of opposition and precision-grip capabilities."),
    ("brachiation_shoulders", "skeletal", "Shoulder and forelimb support pattern associated with suspensory locomotion."),
    ("knuckle_walking_metacarpals", "skeletal", "Load-bearing hand/forelimb structures in knuckle-walking body plans."),
    ("prehensile_tail", "locomotor", "Tail with grasping or stabilising function when the selected species supports it."),
    ("goat_horns", "integumentary", "Bony horn cores covered by keratin in goats and related ungulates; sex and breed vary."),
    ("sheep_wool_follicles", "integumentary", "Dense wool-producing follicles in wool-bearing sheep breeds."),
    ("rumen_papillae", "digestive", "Rumen surface structures that contribute to volatile-fatty-acid absorption."),
    ("rhino_horn", "integumentary", "Keratin-rich horn structure; it is not a conventional bony horn core."),
    ("thick_dermis", "integumentary", "Thickened dermal layer described for selected large mammals and fictional armour-like skins."),
    ("hippo_canine_tusks", "feeding", "Enlarged canine teeth used in display and defence in hippopotamuses."),
    ("aquatic_ear_valves", "sensory", "Structures/behaviours that limit water entry into the external ear canal."),
    ("ostrich_kicking_legs", "locomotor", "Powerful cursorial hindlimbs adapted for running and kicking."),
    ("reduced_wings", "locomotor", "Avian wings with roles in display, balance or manoeuvring rather than powered flight."),
    ("hummingbird_hover_muscles", "muscular", "Flight-muscle specialisation for sustained hovering; reference-only in this model."),
    ("elongated_bill", "feeding", "Long slender bill used for nectar access or specialised feeding in selected birds."),
    ("projectile_tongue", "feeding", "Rapidly extendable tongue apparatus in selected lizards; exact biomechanics are species-specific."),
    ("independently_moving_eyes", "sensory", "Eye-motion capability associated with broad-field visual sampling in chameleons."),
    ("zygodactyl_feet", "locomotor", "Two-forward/two-backward toe arrangement in selected climbing or grasping birds."),
    ("dewlap", "integumentary", "Expandable throat skin used for display or thermoregulation in selected reptiles."),
    ("salt_gland", "excretory", "Specialised salt excretion structure in selected marine reptiles and seabirds."),
    ("turtle_flippers", "locomotor", "Modified limbs used for aquatic propulsion in marine turtles."),
    ("echolocation_melon", "sensory", "Forehead acoustic-fat structure that helps shape echolocation clicks in toothed cetaceans."),
    ("dorsal_fin", "locomotor", "Dorsal fin that contributes to stability in selected aquatic animals."),
    ("tail_flukes", "locomotor", "Horizontal tail flukes that generate propulsion in cetaceans."),
    ("paddle_tail", "locomotor", "Broad flattened tail used for swimming in manatees and other aquatic animals."),
    ("bristles", "sensory", "Tactile bristles used to detect local contact or water movement in selected mammals."),
    ("radula", "feeding", "Toothed ribbon used by most molluscs to scrape or process food; absent in some lineages."),
    ("muscular_foot", "locomotor", "Molluscan muscular foot used for crawling, anchoring or other movement."),
    ("pneumostome", "respiratory", "External opening for a lung-like mantle cavity in pulmonate gastropods."),
    ("pectines", "sensory", "Comb-like sensory organs found on the underside of scorpions."),
    ("venom_telson", "defence", "Terminal sting apparatus associated with the scorpion telson."),
    ("wingscales", "integumentary", "Tiny scales covering butterfly and moth wings."),
    ("proboscis", "feeding", "Extendable feeding tube in butterflies, moths and other animals with a proboscis."),
    ("anterior_sucker", "locomotor", "Anterior attachment structure in leeches and other sucker-bearing annelids."),
    ("posterior_sucker", "locomotor", "Posterior attachment structure used for anchoring and looping locomotion in leeches."),
    ("hirudin_glands", "defence", "Fiction-neutral catalogue label for leech salivary structures; specific secretions differ by species."),
    ("jellyfish_bell", "locomotor", "Contractile bell used for propulsion in many medusae."),
    ("rhopalia", "sensory", "Sensory structures that may contain balance and light-detection organs in medusae."),
    ("tube_feet", "locomotor", "Hydraulic appendages used for movement, attachment and handling by echinoderms."),
    ("water_vascular_system", "circulatory", "Hydraulic canal system used by echinoderms to operate tube feet and related structures."),
    ("madreporite", "circulatory", "Porous plate involved in water-vessel exchange in many sea stars."),
    ("radial_nerve", "nervous", "Radial nerve cord pattern in echinoderms; not a vertebrate central nervous system."),
    ("pyloric_caeca", "digestive", "Digestive gland structures extending into sea-star arms."),
    ("pedicellariae", "defence", "Small pincer-like structures on some echinoderms, varying by species."),
    ("diplosomites", "skeletal", "Body rings formed from fused segments in many millipedes."),
    ("defensive_glands", "defence", "Species-specific glands that release deterrent secretions in some arthropods."),
    ("elytra", "integumentary", "Hardened forewings forming protective covers over beetle hindwings."),
    ("tarsi", "locomotor", "Distal segmented parts of arthropod legs used in contact and locomotion."),
    ("web_claws", "locomotor", "Claws and terminal structures used to grip surfaces or manipulate silk; species-specific."),
    ("crocodilian_heart", "circulatory", "Crocodilian heart with specialised cardiac anatomy; functional shunting is not fully simulated."),
    ("conical_teeth", "feeding", "Conical teeth used by many toothed predators and piscivores."),
    ("mantle", "integumentary", "Molluscan tissue surrounding the visceral mass and often forming shell material."),
    ("shell", "integumentary", "External shell or shell-derived support structure where present."),
    ("bell_margin_sensors", "sensory", "Sensory structures located around the margin of selected medusae."),
])

# Prehistoric and fantasy anatomy records shared by their body-plan templates.
PREHISTORIC_STRUCTURE_DETAILS = [
    ("spinosaur_sail", "integumentary", "Tall dorsal sail or sail-like neural-spine profile; exact soft-tissue outline is uncertain."),
    ("elongated_crocodilian_snout", "feeding", "Long narrow snout suited to a fish-catching feeding model."),
    ("conical_fish_gripping_teeth", "feeding", "Conical teeth associated with grasping slippery prey."),
    ("diplodocid_whiplash_tail", "locomotor", "Very long tail used for balance and movement; exact dynamic performance is not assumed."),
    ("diplodocid_neck_support", "skeletal", "Long-neck support structures for a sauropod body plan."),
    ("parasaurolophus_cranial_crest", "sensory", "Elongated cranial crest; possible acoustic functions remain uncertain and are not presumed by the simulator."),
    ("pachycephalosaur_dome", "skeletal", "Thickened cranial dome represented as a distinct structure; impact behaviour is not auto-enabled."),
    ("pachycephalosaur_reinforced_skull", "skeletal", "Reinforced skull structure associated with the dome-headed body-plan template."),
    ("pterosaur_wing_finger", "skeletal", "Elongated fourth manual digit supporting a pterosaur wing membrane."),
    ("pterosaur_wing_membrane", "locomotor", "Wing membrane supported by an elongated finger and limb elements."),
    ("pterosaur_pneumatic_bones", "skeletal", "Air-space-associated skeletal structure in the pterosaur template; model is approximate."),
    ("mosasaur_flippers", "locomotor", "Modified limbs used for aquatic manoeuvring."),
    ("mosasaur_paddle_tail", "locomotor", "Tail profile contributing to swimming propulsion."),
    ("mosasaur_conical_teeth", "feeding", "Conical teeth used for grasping aquatic prey."),
    ("dragon_fire_resistant_mucosa", "integumentary", "Fictional protected lining for a dragon's configured heat-emission pathway."),
    ("dragon_pyrogenic_sac", "magical_specialisation", "Optional fictional organ for a user-defined magical heat or flame mechanism."),
    ("dragon_scale_bed", "integumentary", "Dermal support region for overlapping fantasy scales."),
    ("dragon_aetheric_core", "magical_specialisation", "Fictional structure for a setting-defined internal magical function; not a mana reservoir by default."),
]
_EXTRA_STRUCTURES.extend(PREHISTORIC_STRUCTURE_DETAILS)

for _name, _system, _role in _EXTRA_STRUCTURES:
    if _name not in ORGANS:
        _organ(_name, _system, _role)

# Additional human anatomy references. These are addressable structures rather
# than a cell-by-cell simulation; only state hooks documented by physiology.py
# are dynamically simulated. Keeping these records separate from the shared
# mammal map avoids making human-only structures appear in every mammal.
_HUMAN_DETAIL_STRUCTURES = [
    # Brain subdivisions and central integration
    ("frontal_lobe", "nervous", "Executive planning, voluntary motor planning, speech-related and behavioural functions."),
    ("parietal_lobe", "nervous", "Somatosensory integration and spatial attention."),
    ("temporal_lobe", "nervous", "Auditory processing and memory-related functions."),
    ("occipital_lobe", "nervous", "Visual processing regions."),
    ("insula", "nervous", "Interoceptive, autonomic and multisensory integration region."),
    ("corpus_callosum", "nervous", "Major interhemispheric fibre tract."),
    ("basal_ganglia", "nervous", "Movement selection, habit and action gating circuits."),
    ("hippocampus", "nervous", "Memory formation and spatial-context processing structure."),
    ("amygdala", "nervous", "Salience, threat-learning and emotional processing structure."),
    ("thalamus", "nervous", "Major relay and state-regulation structure."),
    ("midbrain", "nervous", "Brainstem region involved in motor, visual and auditory pathways."),
    ("pons", "nervous", "Brainstem relay and respiratory/sleep-related functions."),
    ("medulla_oblongata", "nervous", "Brainstem autonomic and vital-reflex region."),
    ("cerebellar_vermis", "nervous", "Midline cerebellar region involved in coordination and posture."),
    ("dura_mater", "nervous", "Outer meningeal covering around the brain and spinal cord."),
    ("arachnoid_mater", "nervous", "Middle meningeal layer surrounding cerebrospinal fluid spaces."),
    ("pia_mater", "nervous", "Inner meningeal layer closely following the central nervous system."),
    ("cerebrospinal_fluid", "nervous", "Fluid compartment providing buoyancy, chemical stability and cushioning."),
    ("choroid_plexus", "nervous", "Structure producing most cerebrospinal fluid."),
    ("cranial_nerves", "nervous", "Named cranial nerve pathways connecting brain with head, neck and viscera."),
    ("optic_nerve", "sensory", "Visual information pathway from retina to brain."),
    ("optic_chiasm", "sensory", "Partial crossing of optic nerve fibres."),
    ("vagus_nerve", "nervous", "Major parasympathetic and visceral sensory/motor pathway."),
    ("brachial_plexus", "nervous", "Nerve network supplying much of the upper limbs."),
    ("lumbar_plexus", "nervous", "Nerve network supplying abdominal wall and parts of the lower limbs."),
    ("sacral_plexus", "nervous", "Nerve network supplying pelvis and much of the lower limbs."),
    ("sciatic_nerve", "nervous", "Large nerve pathway supplying posterior thigh and distal lower limb branches."),
    ("femoral_nerve", "nervous", "Major motor and sensory pathway of the anterior thigh."),
    ("median_nerve", "nervous", "Upper-limb nerve serving selected forearm/hand muscles and sensation."),
    ("ulnar_nerve", "nervous", "Upper-limb nerve serving selected intrinsic hand muscles and sensation."),
    ("radial_nerve", "nervous", "Upper-limb nerve serving extensor compartments and sensation."),
    ("phrenic_nerve", "nervous", "Motor supply to the diaphragm and associated sensory pathways."),
    ("enteric_plexus", "nervous", "Intrinsic neural networks coordinating gut motility and secretion."),
    # Human special senses and oral structures
    ("cornea", "sensory", "Transparent anterior eye surface and major refractive interface."),
    ("lens", "sensory", "Adjustable optical element that focuses light on the retina."),
    ("retina", "sensory", "Light-sensitive neural tissue converting photons to neural signals."),
    ("optic_disc", "sensory", "Retinal exit region for optic nerve fibres; physiologically blind spot."),
    ("cochlea", "sensory", "Inner-ear organ for auditory frequency analysis."),
    ("semicircular_canals", "sensory", "Inner-ear angular-acceleration sensing structures."),
    ("tympanic_membrane", "sensory", "Eardrum transmitting sound pressure to the middle ear."),
    ("incus", "sensory", "Middle-ear ossicle transmitting vibration between malleus and stapes."),
    ("malleus", "sensory", "Middle-ear ossicle mechanically coupled to the tympanic membrane."),
    ("stapes", "sensory", "Middle-ear ossicle transmitting vibration to the oval window."),
    ("incisors", "feeding", "Front teeth specialised for cutting and biting."),
    ("canines", "feeding", "Teeth contributing to tearing and food handling."),
    ("premolars", "feeding", "Teeth contributing to crushing and grinding."),
    ("molars", "feeding", "Posterior teeth specialised for grinding."),
    ("periodontal_ligament", "feeding", "Connective attachment suspending each tooth in its socket."),
    ("dental_pulp", "feeding", "Vascular and neural soft tissue inside a tooth."),
    ("parotid_gland", "digestive", "Major salivary gland near the ear."),
    ("submandibular_gland", "digestive", "Major salivary gland beneath the mandible."),
    ("sublingual_gland", "digestive", "Major salivary gland in the floor of the mouth."),
    # Cardiovascular subdivisions
    ("aorta", "circulatory", "Main systemic artery distributing blood from the left ventricle."),
    ("superior_vena_cava", "circulatory", "Large vein returning blood from the upper body."),
    ("inferior_vena_cava", "circulatory", "Large vein returning blood from the lower body."),
    ("pulmonary_arteries", "circulatory", "Arteries carrying blood from the right ventricle to the lungs."),
    ("pulmonary_veins", "circulatory", "Veins returning oxygenated blood from the lungs."),
    ("coronary_arteries", "circulatory", "Arteries supplying the heart muscle."),
    ("coronary_veins", "circulatory", "Venous drainage pathways from the heart muscle."),
    ("carotid_arteries", "circulatory", "Major arterial supply pathways for head and brain."),
    ("jugular_veins", "circulatory", "Major venous drainage pathways for head and neck."),
    ("hepatic_portal_vein", "circulatory", "Carries nutrient-rich blood from digestive organs to the liver."),
    ("hepatic_veins", "circulatory", "Drain blood from the liver toward the inferior vena cava."),
    ("arterioles", "circulatory", "Small arteries regulating resistance and local tissue perfusion."),
    ("venules", "circulatory", "Small veins collecting blood from capillary beds."),
    ("capillary_beds", "circulatory", "Exchange networks for gases, nutrients, fluids and metabolites."),
    ("thoracic_duct", "lymphatic", "Major lymphatic vessel returning lymph to venous circulation."),
    ("cervical_lymph_nodes", "immune", "Regional lymph nodes in the neck."),
    ("axillary_lymph_nodes", "immune", "Regional lymph nodes in the axilla."),
    ("inguinal_lymph_nodes", "immune", "Regional lymph nodes in the groin."),
    # Muscle groups and force transmission
    ("deltoid", "muscular", "Shoulder muscle group producing and controlling arm elevation."),
    ("pectoralis_major", "muscular", "Large anterior chest muscle contributing to shoulder movement."),
    ("latissimus_dorsi", "muscular", "Broad back muscle contributing to shoulder extension and adduction."),
    ("trapezius", "muscular", "Upper-back muscle group controlling scapular and neck movement."),
    ("rotator_cuff", "muscular", "Shoulder muscle-tendon group stabilising and rotating the humeral head."),
    ("biceps_brachii", "muscular", "Upper-arm muscle contributing to elbow flexion and forearm supination."),
    ("triceps_brachii", "muscular", "Upper-arm muscle group extending the elbow."),
    ("forearm_flexors", "muscular", "Forearm muscle group flexing wrist and digits."),
    ("forearm_extensors", "muscular", "Forearm muscle group extending wrist and digits."),
    ("rectus_abdominis", "muscular", "Abdominal wall muscle contributing to trunk flexion and bracing."),
    ("external_obliques", "muscular", "Abdominal wall muscles contributing to rotation and side-bending."),
    ("erector_spinae", "muscular", "Paraspinal muscle group supporting spinal extension and posture."),
    ("gluteus_maximus", "muscular", "Major hip extensor and force-transfer muscle."),
    ("gluteus_medius", "muscular", "Hip abductor and pelvic stabiliser during gait."),
    ("iliopsoas", "muscular", "Hip flexor muscle group important in leg advancement."),
    ("quadriceps_femoris", "muscular", "Anterior thigh muscle group extending the knee."),
    ("hamstrings", "muscular", "Posterior thigh muscle group acting on hip and knee."),
    ("gastrocnemius", "muscular", "Calf muscle contributing to plantar flexion and propulsion."),
    ("soleus", "muscular", "Deep calf muscle supporting posture and ankle propulsion."),
    ("tibialis_anterior", "muscular", "Muscle lifting the forefoot during swing phase."),
    ("pelvic_floor_muscles", "muscular", "Muscle layers supporting pelvic organs and continence."),
    ("deep_neck_flexors", "muscular", "Deep cervical muscle group supporting head/neck control."),
    # Skeletal and connective interfaces
    ("intervertebral_discs", "skeletal", "Fibrocartilaginous discs distributing spinal loads and permitting motion."),
    ("menisci", "skeletal", "Knee fibrocartilage improving load distribution and joint congruence."),
    ("anterior_cruciate_ligament", "skeletal", "Knee ligament limiting selected anterior translation and rotation."),
    ("posterior_cruciate_ligament", "skeletal", "Knee ligament limiting selected posterior translation."),
    ("achilles_tendon", "skeletal", "Tendon transmitting calf-muscle force to the calcaneus."),
    ("patellar_tendon", "skeletal", "Patellar tendon/ligament transmitting quadriceps force to the tibia."),
    ("rotator_cuff_tendons", "skeletal", "Tendons anchoring cuff muscles around the shoulder joint."),
    ("temporomandibular_joint", "skeletal", "Paired jaw joints enabling controlled mandibular motion."),
    ("atlantoaxial_joint", "skeletal", "Upper cervical pivot joint permitting substantial head rotation."),
    ("sacroiliac_joints", "skeletal", "Joints transmitting loads between spine and pelvic girdle."),
    ("costal_cartilages", "skeletal", "Cartilage connecting ribs to the sternum or adjacent costal cartilages."),
    ("synovial_membrane", "skeletal", "Tissue lining many synovial joint capsules and producing synovial fluid."),
    ("joint_capsules", "skeletal", "Fibrous capsules enclosing synovial joints."),
    # Respiratory and digestive subdivisions
    ("epiglottis", "respiratory", "Laryngeal-associated structure helping protect the airway during swallowing."),
    ("vocal_folds", "respiratory", "Laryngeal tissues producing voiced sound through controlled airflow."),
    ("pleura", "respiratory", "Serous membranes surrounding lungs and lining the thoracic cavity."),
    ("right_lung", "respiratory", "Right lung reference unit; detailed lobar behaviour is not independently simulated."),
    ("left_lung", "respiratory", "Left lung reference unit; detailed lobar behaviour is not independently simulated."),
    ("respiratory_bronchioles", "respiratory", "Small conducting/exchange airways distal to terminal bronchioles."),
    ("lower_esophageal_sphincter", "digestive", "Functional high-pressure region helping limit reflux into the oesophagus."),
    ("pyloric_sphincter", "digestive", "Muscular outlet regulating passage from stomach to duodenum."),
    ("ileocecal_valve", "digestive", "Junctional structure between ileum and caecum."),
    ("vermiform_appendix", "digestive", "Small lymphoid-rich appendage of the human caecum."),
    ("rectal_ampulla", "digestive", "Distal rectal storage region before defecation."),
    ("internal_anal_sphincter", "digestive", "Involuntary smooth-muscle component of the anal continence mechanism."),
    ("external_anal_sphincter", "digestive", "Voluntary skeletal-muscle component of the anal continence mechanism."),
    ("mesentery", "digestive", "Peritoneal fold supporting vessels, lymphatics and nerves to bowel."),
    ("peritoneum", "digestive", "Serous membrane lining the abdominal cavity and covering many viscera."),
    # Renal microanatomy / endocrine / immune
    ("renal_cortex", "renal", "Outer kidney region containing renal corpuscles and convoluted tubules."),
    ("renal_medulla", "renal", "Inner kidney region containing loops and collecting ducts."),
    ("glomeruli", "renal", "Capillary tufts forming the initial blood-filtration component of nephrons."),
    ("renal_tubules", "renal", "Tubular nephron components for reabsorption and secretion."),
    ("collecting_ducts", "renal", "Ducts regulating final urine concentration and delivery."),
    ("renal_pelvis", "renal", "Collecting funnel directing urine into each ureter."),
    ("bladder_trigone", "renal", "Triangular region at the bladder base around ureteric and urethral openings."),
    ("adrenal_cortex", "endocrine", "Outer adrenal region producing steroid hormone classes."),
    ("adrenal_medulla", "endocrine", "Inner adrenal region secreting catecholamines during sympathetic activation."),
    ("islets_of_langerhans", "endocrine", "Pancreatic endocrine cell clusters regulating glucose and other functions."),
    ("hypophyseal_stalk", "endocrine", "Connection between hypothalamus and pituitary gland."),
    ("tonsillar_crypts", "immune", "Invaginations increasing mucosal immune sampling area in palatine tonsils."),
    ("mucosal_immune_tissue", "immune", "Distributed immune structures at mucosal barriers."),
    ("erythrocytes", "hematopoietic", "Mature red blood cells in typical human circulation; dynamic count not cell-by-cell simulated."),
    ("neutrophils", "immune", "Innate immune granulocytes involved in rapid inflammatory responses."),
    ("lymphocytes", "immune", "Adaptive and innate lymphoid cell family; subtype mix is context dependent."),
    ("monocytes", "immune", "Circulating immune cells able to differentiate into tissue phagocyte lineages."),
    ("eosinophils", "immune", "Granulocytes involved in parasite-associated and allergic responses."),
    ("basophils", "immune", "Rare circulating granulocytes involved in selected inflammatory responses."),
    # Skin, hair, reproductive and life-stage reference structures
    ("nails", "integumentary", "Keratinised distal digits providing protection and counterpressure for manipulation."),
    ("eccrine_sweat_glands", "thermoregulation", "Watery sweat glands important in human evaporative cooling."),
    ("apocrine_sweat_glands", "integumentary", "Specialised sweat glands concentrated in selected body regions."),
    ("sebaceous_units", "integumentary", "Sebaceous glands and associated follicles contributing lipid-rich surface secretion."),
    ("arrector_pili", "integumentary", "Small smooth muscles associated with hair follicles."),
    ("vas_deferens", "reproductive", "Duct transporting sperm from epididymis toward the ejaculatory tract."),
    ("seminal_vesicles", "reproductive", "Accessory glands contributing seminal fluid."),
    ("prostate", "reproductive", "Accessory gland contributing secretions to semen."),
    ("right_ovary", "reproductive", "Right gonadal structure in an individual possessing typical paired ovaries."),
    ("left_ovary", "reproductive", "Left gonadal structure in an individual possessing typical paired ovaries."),
    ("right_testis", "reproductive", "Right gonadal structure in an individual possessing typical paired testes."),
    ("left_testis", "reproductive", "Left gonadal structure in an individual possessing typical paired testes."),
]

# Human detail catalogue v3: high-value regional anatomy and microstructure.
HUMAN_DETAIL_STRUCTURES_V3 = [('prefrontal_cortex', 'nervous', 'Prefrontal cortical regions supporting planning, inhibition and context-sensitive action selection.'), ('primary_motor_cortex', 'nervous', 'Cortical region contributing to voluntary movement commands.'), ('primary_somatosensory_cortex', 'nervous', 'Cortical region representing touch, position and selected bodily sensations.'), ('auditory_cortex', 'nervous', 'Cortical regions participating in sound processing.'), ('corticospinal_tract', 'nervous', 'Descending pathway contributing to skilled voluntary movement.'), ('spinothalamic_tract', 'nervous', 'Ascending pathway carrying selected pain, temperature and crude-touch information.'), ('dorsal_column_pathway', 'nervous', 'Ascending pathway carrying discriminative touch, vibration and position-related information.'), ('vestibular_nuclei', 'nervous', 'Brainstem processing centres integrating balance and head-motion signals.'), ('reticular_formation', 'nervous', 'Distributed brainstem network contributing to arousal and state regulation.'), ('olfactory_bulb', 'sensory', 'Neural structure processing olfactory input before distributed cortical processing.'), ('brachiocephalic_trunk', 'circulatory', 'Major arterial branch supplying the right head/neck and right upper limb through downstream vessels.'), ('subclavian_arteries', 'circulatory', 'Paired arterial routes supplying upper-limb and selected thoracic structures.'), ('axillary_arteries', 'circulatory', 'Arterial routes through the axilla supplying the upper limb.'), ('brachial_arteries', 'circulatory', 'Major upper-arm arterial routes.'), ('radial_arteries', 'circulatory', 'Forearm arterial routes on the radial side.'), ('ulnar_arteries', 'circulatory', 'Forearm arterial routes on the ulnar side.'), ('femoral_arteries', 'circulatory', 'Major arterial routes supplying lower limbs.'), ('popliteal_arteries', 'circulatory', 'Arterial routes around the posterior knee region.'), ('dorsalis_pedis_arteries', 'circulatory', 'Arterial supply along the dorsum of the foot.'), ('dural_venous_sinuses', 'circulatory', 'Venous channels within dura that drain blood from the cranial cavity.'), ('coronary_sinus', 'circulatory', 'Major venous channel draining much of the myocardium into the right atrium.'), ('pulmonary_capillary_network', 'respiratory', 'Capillary network surrounding alveoli for gas exchange; not a separate blood-volume simulation.'), ('alveolar_type_i_cells', 'respiratory', 'Thin alveolar epithelial cells forming much of the gas-exchange surface.'), ('alveolar_type_ii_cells', 'respiratory', 'Alveolar cells producing surfactant and participating in epithelial maintenance.'), ('pulmonary_surfactant_layer', 'respiratory', 'Surface-active film that reduces alveolar surface tension.'), ('hepatic_lobules', 'digestive', 'Repeating liver tissue organisation around vascular and biliary routes.'), ('bile_canaliculi', 'digestive', 'Microscopic channels collecting bile from hepatocytes.'), ('pancreatic_duct', 'digestive', 'Duct system delivering exocrine pancreatic secretions to the small intestine.'), ('gastric_mucosa', 'digestive', 'Stomach lining containing mucus-producing, acid-secreting and enzyme-related cell populations.'), ('small_intestinal_villi', 'digestive', 'Mucosal projections increasing absorptive surface area.'), ('intestinal_crypts', 'digestive', 'Intestinal gland structures containing epithelial renewal and specialised secretory cells.'), ('proximal_convoluted_tubules', 'renal', 'Nephron segments responsible for substantial reabsorption of water and solutes.'), ('loop_of_henle', 'renal', 'Nephron loop contributing to medullary concentration gradients.'), ('distal_convoluted_tubules', 'renal', 'Nephron segments involved in regulated electrolyte handling.'), ('peritubular_capillaries', 'renal', 'Capillary network associated with renal tubular exchange.'), ('vasa_recta', 'renal', 'Specialised medullary vessels supporting exchange around long nephron loops.'), ('masseter', 'muscular', 'Major jaw-closing muscle contributing to bite force.'), ('orbicularis_oculi', 'muscular', 'Muscle group closing the eyelids and supporting blink function.'), ('orbicularis_oris', 'muscular', 'Muscle complex controlling lip closure and shaping.'), ('sternocleidomastoid', 'muscular', 'Neck muscle contributing to head rotation and flexion.'), ('serratus_anterior', 'muscular', 'Muscle stabilising and rotating the scapula during arm movement.'), ('external_intercostals', 'muscular', 'Thoracic-wall muscles participating in respiratory mechanics.'), ('internal_intercostals', 'muscular', 'Thoracic-wall muscles contributing to selected respiratory movements.'), ('thenar_muscles', 'muscular', 'Thumb-side intrinsic hand muscles supporting opposition and precision grip.'), ('hypothenar_muscles', 'muscular', 'Little-finger-side intrinsic hand muscles supporting fine hand movement.'), ('plantar_fascia', 'locomotor', 'Fibrous sheet supporting the foot arch and transmitting load during gait.'), ('ankle_stabilising_complex', 'locomotor', 'Ligament and tendon groups contributing to ankle stability; not a single anatomical organ.'), ('thoracic_duct_valves', 'lymphatic', 'Valves maintaining directional lymph movement through the thoracic duct system.'), ('right_lymphatic_duct', 'lymphatic', 'Terminal lymphatic channel draining selected right upper-body regions.'), ('spleen_white_pulp', 'immune', 'Lymphoid spleen compartment involved in immune surveillance.'), ('spleen_red_pulp', 'hematopoietic', 'Spleen compartment involved in filtering blood and handling aged blood cells.'), ('thyroid_follicles', 'endocrine', 'Follicular units producing and storing thyroid hormone precursors.'), ('parathyroid_cells', 'endocrine', 'Parathyroid cell populations regulating calcium-related physiology.')]
_HUMAN_DETAIL_STRUCTURES.extend(HUMAN_DETAIL_STRUCTURES_V3)
# Human detail catalogue v4: organ subregions, neurovascular routes, and
# locomotor / visceral interfaces. These remain addressable references rather
# than promises of cell-level or continuous organ simulation.
HUMAN_DETAIL_STRUCTURES_V4 = [
    # Central nervous system and signal integration
    ("corpus_callosum", "nervous", "Major interhemispheric fibre tract linking cortical regions."),
    ("cingulate_cortex", "nervous", "Medial cortical regions involved in attention, motivation and response monitoring."),
    ("insula", "nervous", "Cortical region integrating selected visceral, sensory and salience information."),
    ("hippocampal_formation", "nervous", "Medial temporal structures important to formation and retrieval of episodic memories."),
    ("amygdaloid_complex", "nervous", "Deep temporal nuclei involved in emotional learning and threat relevance."),
    ("thalamic_nuclei", "nervous", "Relay and integration nuclei for many sensory and motor loops."),
    ("hypothalamic_nuclei", "nervous", "Neural nuclei coordinating endocrine, autonomic, temperature and fluid-balance functions."),
    ("basal_ganglia", "nervous", "Subcortical circuits contributing to action selection and movement control."),
    ("caudate_nucleus", "nervous", "Basal-ganglia structure participating in action selection and learning circuits."),
    ("putamen", "nervous", "Basal-ganglia structure participating in movement-related loops."),
    ("globus_pallidus", "nervous", "Basal-ganglia output and relay structure within movement-control circuits."),
    ("subthalamic_nucleus", "nervous", "Basal-ganglia node influencing movement suppression and selection."),
    ("substantia_nigra", "nervous", "Midbrain nuclei contributing to dopamine signalling and movement-related circuits."),
    ("locus_coeruleus", "nervous", "Brainstem nucleus contributing noradrenergic signals to arousal and attention."),
    ("nucleus_tractus_solitarius", "nervous", "Brainstem nucleus receiving selected visceral and taste-related sensory signals."),
    ("nucleus_ambiguus", "nervous", "Medullary motor nucleus contributing to swallowing, phonation and selected autonomic functions."),
    ("dorsal_root_ganglia", "nervous", "Sensory neuron cell bodies associated with spinal nerves."),
    ("ventral_spinal_roots", "nervous", "Motor axon routes leaving spinal cord segments."),
    ("dorsal_spinal_roots", "nervous", "Sensory axon routes entering spinal cord segments."),
    ("brachial_plexus", "nervous", "Nerve network distributing motor and sensory signals to much of the upper limb."),
    ("lumbar_plexus", "nervous", "Nerve network supplying parts of the abdominal wall and anterior/medial lower limb."),
    ("sacral_plexus", "nervous", "Nerve network supplying posterior lower-limb and pelvic regions."),
    ("phrenic_nerves", "nervous", "Motor and sensory nerves supplying the diaphragm and nearby structures."),
    ("vagus_nerve", "nervous", "Cranial nerve with broad visceral parasympathetic and sensory functions."),
    ("sympathetic_trunks", "nervous", "Paired sympathetic chain pathways coordinating selected autonomic responses."),
    ("parasympathetic_ganglia", "nervous", "Peripheral autonomic ganglia serving selected visceral targets."),
    ("neuromuscular_junctions", "nervous", "Motor-neuron synapses that transmit commands to skeletal muscle fibres."),
    ("muscle_spindles", "sensory", "Proprioceptive receptors sensing muscle length and changes in stretch."),
    ("golgi_tendon_organs", "sensory", "Proprioceptive receptors responding to tension transmitted through tendons."),
    ("cutaneous_nociceptors", "sensory", "Free nerve endings responsive to potentially damaging stimuli."),
    ("cutaneous_mechanoreceptors", "sensory", "Receptors responding to pressure, skin deformation and vibration."),
    ("cutaneous_thermoreceptors", "sensory", "Receptors contributing to detection of skin temperature changes."),
    ("retinal_ganglion_cells", "sensory", "Retinal output neurons carrying visual signals toward the brain."),
    ("retinal_photoreceptors", "sensory", "Rods and cones transducing light into neural signals."),
    ("optic_chiasm", "sensory", "Partial crossing point for optic nerve fibres."),
    ("optic_radiations", "sensory", "Pathways carrying visual information from thalamic relay nuclei to cortex."),
    ("cochlear_hair_cells", "sensory", "Inner-ear sensory cells transducing sound-related motion."),
    ("vestibular_hair_cells", "sensory", "Inner-ear sensory cells transducing head-motion and orientation cues."),
    ("organ_of_corti", "sensory", "Cochlear sensory epithelium supporting auditory transduction."),
    ("utricle_and_saccule", "sensory", "Vestibular organs sensing linear acceleration and head tilt."),
    ("eustachian_tubes", "respiratory", "Channels connecting middle-ear spaces with the nasopharynx for pressure equalisation."),
    ("lacrimal_gland", "integumentary", "Tear-producing gland supporting ocular surface lubrication and defence."),
    ("meibomian_glands", "integumentary", "Eyelid glands contributing lipid to the tear film."),
    # Cerebral and spinal coverings / fluid spaces
    ("dura_mater", "nervous", "Tough outer meningeal covering around brain and spinal cord."),
    ("arachnoid_mater", "nervous", "Meningeal layer associated with cerebrospinal-fluid spaces."),
    ("pia_mater", "nervous", "Delicate inner meningeal layer closely following central nervous-system surfaces."),
    ("cerebrospinal_fluid_spaces", "nervous", "Ventricular and subarachnoid fluid spaces cushioning and supporting the central nervous system."),
    ("lateral_ventricles", "nervous", "Paired cerebral ventricles containing cerebrospinal fluid."),
    ("third_ventricle", "nervous", "Midline diencephalic cerebrospinal-fluid cavity."),
    ("fourth_ventricle", "nervous", "Hindbrain cerebrospinal-fluid cavity connected to central and subarachnoid spaces."),
    ("choroid_plexus", "nervous", "Specialised tissue producing much of the cerebrospinal fluid."),
    # Cardiovascular regional anatomy and microcirculation
    ("left_atrium", "circulatory", "Heart chamber receiving oxygenated pulmonary venous return."),
    ("right_atrium", "circulatory", "Heart chamber receiving systemic venous return."),
    ("left_ventricle", "circulatory", "Heart chamber driving systemic arterial circulation."),
    ("right_ventricle", "circulatory", "Heart chamber driving pulmonary circulation."),
    ("sinoatrial_node", "circulatory", "Primary pacemaker region for typical human cardiac rhythm."),
    ("atrioventricular_node", "circulatory", "Conduction node that delays and relays atrial activation."),
    ("his_bundle", "circulatory", "Cardiac conduction tract carrying signals from AV node toward ventricles."),
    ("purkinje_fibres", "circulatory", "Specialised conducting fibres distributing ventricular activation."),
    ("ascending_aorta", "circulatory", "Aortic segment emerging from the left ventricle."),
    ("aortic_arch", "circulatory", "Curved aortic segment giving rise to major head and upper-limb arteries."),
    ("descending_thoracic_aorta", "circulatory", "Thoracic aortic segment supplying chest-wall and thoracic branches."),
    ("abdominal_aorta", "circulatory", "Aortic segment giving rise to major abdominal and lower-body arteries."),
    ("renal_arteries", "circulatory", "Arterial routes supplying the kidneys."),
    ("mesenteric_arteries", "circulatory", "Arterial routes supplying substantial portions of the intestine."),
    ("splenic_artery", "circulatory", "Arterial supply to spleen and selected neighbouring structures."),
    ("hepatic_artery", "circulatory", "Arterial supply to liver tissue."),
    ("iliac_arteries", "circulatory", "Major pelvic arterial routes supplying pelvic organs and lower limbs."),
    ("brachiocephalic_veins", "circulatory", "Large venous routes joining upper-body return into the superior vena cava."),
    ("azygos_vein", "circulatory", "Thoracic venous route providing collateral drainage."),
    ("portal_venous_sinusoids", "circulatory", "Low-pressure vascular channels within liver tissue receiving portal and arterial blood."),
    ("glomerular_capillaries", "renal", "Capillary tufts filtering blood into nephron filtration spaces."),
    ("systemic_endothelium", "circulatory", "Vascular lining controlling exchange, barrier properties and selected signalling."),
    ("vascular_smooth_muscle", "circulatory", "Contractile cells in vessel walls regulating diameter and resistance."),
    ("pericytes", "circulatory", "Perivascular support cells associated with microvessel stability and regulation."),
    ("lymphatic_capillaries", "lymphatic", "Initial lymph vessels collecting interstitial fluid and selected macromolecules."),
    ("cisterna_chyli", "lymphatic", "Variable lymphatic reservoir receiving lower-body lymph before the thoracic duct."),
    # Respiratory tree and thoracic mechanics
    ("nasal_conchae", "respiratory", "Curved nasal structures increasing air-contact surface and conditioning inhaled air."),
    ("nasal_sinuses", "respiratory", "Air spaces in skull bones connected to the nasal cavity."),
    ("nasopharynx", "respiratory", "Upper pharyngeal region carrying air behind the nasal cavity."),
    ("oropharynx", "respiratory", "Pharyngeal region shared by respiratory and digestive passageways."),
    ("laryngopharynx", "respiratory", "Lower pharyngeal region routing air toward larynx and food toward oesophagus."),
    ("laryngeal_cartilages", "respiratory", "Cartilaginous framework maintaining airway shape and voice structures."),
    ("tracheal_rings", "respiratory", "Incomplete cartilaginous rings supporting tracheal patency."),
    ("mainstem_bronchi", "respiratory", "Right and left primary airways branching from the trachea."),
    ("lobar_bronchi", "respiratory", "Airway branches supplying major lung lobes."),
    ("segmental_bronchi", "respiratory", "Airways supplying bronchopulmonary segments."),
    ("terminal_bronchioles", "respiratory", "Small conducting airways preceding respiratory bronchioles."),
    ("alveolar_ducts", "respiratory", "Distal passages leading into clusters of alveoli."),
    ("alveolar_sacs", "respiratory", "Clusters of alveoli forming distal gas-exchange regions."),
    ("intercostal_neurovascular_bundles", "respiratory", "Nerve and vessel routes running along intercostal spaces."),
    ("diaphragmatic_tendon", "muscular", "Central tendon receiving fibres of the respiratory diaphragm."),
    ("costodiaphragmatic_recesses", "respiratory", "Pleural recesses accommodating lung expansion during deep inspiration."),
    # Digestive tract, mesenteries, accessory organs
    ("hard_palate", "feeding", "Bony and mucosal roof of the oral cavity separating it from the nasal cavity."),
    ("soft_palate", "feeding", "Mobile posterior palate contributing to swallowing and speech."),
    ("lingual_papillae", "feeding", "Surface structures on the tongue with mechanical and taste-related roles."),
    ("taste_buds", "sensory", "Sensory epithelial structures supporting taste detection."),
    ("pharyngeal_constrictors", "muscular", "Muscle groups propelling swallowed material through the pharynx."),
    ("oesophageal_mucosa", "digestive", "Protective lining of the oesophagus."),
    ("oesophageal_muscularis", "digestive", "Layered muscle wall driving food transport by coordinated contraction."),
    ("stomach_fundus", "digestive", "Proximal stomach region that accommodates swallowed material and gas."),
    ("stomach_body", "digestive", "Major central stomach region involved in mixing and secretion."),
    ("stomach_antrum", "digestive", "Distal stomach region involved in mixing and controlled gastric emptying."),
    ("duodenum", "digestive", "First small-intestinal segment receiving gastric contents, bile and pancreatic secretions."),
    ("jejunum", "digestive", "Small-intestinal region with substantial nutrient absorption."),
    ("ileum", "digestive", "Distal small-intestinal region involved in nutrient and bile-salt recovery."),
    ("cecum", "digestive", "Blind pouch at the junction of small and large intestine."),
    ("ascending_colon", "digestive", "Right-sided colon segment involved in water and electrolyte handling."),
    ("transverse_colon", "digestive", "Cross-abdominal colon segment carrying intestinal contents."),
    ("descending_colon", "digestive", "Left-sided colon segment carrying contents toward the sigmoid colon."),
    ("sigmoid_colon", "digestive", "Curved distal colon segment before the rectum."),
    ("pancreatic_acini", "digestive", "Exocrine pancreatic units producing digestive enzyme-rich secretions."),
    ("pancreatic_islets", "endocrine", "Endocrine pancreatic clusters regulating glucose and other metabolic states."),
    ("gallbladder_fundus", "digestive", "Fundal region of the gallbladder reservoir."),
    ("extrahepatic_bile_ducts", "digestive", "Bile drainage routes outside liver tissue."),
    ("hepatic_bile_ductules", "digestive", "Small ducts collecting bile from the liver's canalicular network."),
    ("enteric_nerve_plexuses", "nervous", "Myenteric and submucosal neural networks coordinating gut movement and secretion."),
    ("intestinal_lacteals", "lymphatic", "Lymphatic capillaries within intestinal villi participating in lipid transport."),
    # Renal / urinary microanatomy
    ("renal_corpuscles", "renal", "Nephron filtration units comprising glomerular capillaries and associated capsule."),
    ("bowmans_capsule", "renal", "Capsular structure surrounding the glomerular filtration space."),
    ("podocyte_foot_processes", "renal", "Specialised epithelial processes forming part of the glomerular filtration barrier."),
    ("juxtaglomerular_apparatus", "renal", "Nephron-vessel interface contributing to renal pressure and filtration regulation."),
    ("macula_densa", "renal", "Distal-nephron sensory epithelial region monitoring tubular fluid composition."),
    ("renal_collecting_ducts", "renal", "Collecting ducts regulating final urine concentration under hormonal control."),
    ("minor_renal_calyces", "renal", "Small collecting spaces receiving urine from renal papillae."),
    ("major_renal_calyces", "renal", "Larger renal collecting spaces that drain toward the renal pelvis."),
    ("ureteropelvic_junctions", "renal", "Transitions between renal pelvis and ureter where flow coordination can matter."),
    ("ureteric_smooth_muscle", "renal", "Muscular wall generating peristaltic urine transport through ureters."),
    ("urethral_sphincter_complex", "renal", "Smooth and skeletal muscle components contributing to urinary continence."),
    ("urinary_bladder_detrusor", "renal", "Smooth muscle wall of the urinary bladder."),
    # Musculoskeletal force-chain detail for movement spells
    ("cervical_fascia", "locomotor", "Connective-tissue planes organising neck structures and transmitting selected forces."),
    ("thoracolumbar_fascia", "locomotor", "Fascial complex participating in trunk load transfer and muscular attachment."),
    ("abdominal_aponeuroses", "muscular", "Broad connective expansions of abdominal wall muscles."),
    ("linea_alba", "locomotor", "Midline fibrous seam transmitting loads between abdominal wall sides."),
    ("rotator_cuff_muscle_bellies", "muscular", "Muscle portions of the supraspinatus, infraspinatus, teres minor and subscapularis group."),
    ("elbow_capsule", "skeletal", "Fibrous capsule supporting the elbow joint and its congruent articulation."),
    ("wrist_ligament_complex", "skeletal", "Ligament groups stabilising carpal articulations."),
    ("finger_flexor_tendons", "skeletal", "Tendons transmitting forearm muscle force to finger flexion."),
    ("finger_extensor_tendons", "skeletal", "Tendons transmitting extensor force across the hand and digits."),
    ("thumb_opposition_unit", "locomotor", "Muscle, tendon and joint group enabling thumb opposition and precision grip."),
    ("hip_joint_capsule", "skeletal", "Capsular support around the hip joint."),
    ("acetabular_labrum", "skeletal", "Fibrocartilaginous rim deepening the hip socket."),
    ("hip_abductor_group", "muscular", "Muscles stabilising the pelvis during single-leg support and gait."),
    ("adductor_muscle_group", "muscular", "Medial thigh muscles contributing to hip adduction and stability."),
    ("knee_extensor_mechanism", "locomotor", "Quadriceps, patella and tendon structures transmitting force to knee extension."),
    ("knee_collateral_ligaments", "skeletal", "Medial and lateral ligaments stabilising the knee against selected side loads."),
    ("ankle_lateral_ligaments", "skeletal", "Ligaments resisting excessive inversion and related ankle movement."),
    ("plantar_intrinsic_muscles", "muscular", "Intrinsic foot muscles contributing to toe control and arch stability."),
    ("foot_arch_ligaments", "skeletal", "Ligaments contributing to the longitudinal and transverse foot arches."),
    ("intervertebral_facet_joints", "skeletal", "Paired spinal joints guiding and limiting regional vertebral motion."),
    ("cervical_intervertebral_discs", "skeletal", "Cervical disc structures distributing loads and allowing neck movement."),
    ("lumbar_intervertebral_discs", "skeletal", "Lumbar disc structures distributing trunk loads and allowing spinal movement."),
    ("sacrospinous_ligament", "skeletal", "Pelvic ligament supporting sacral-pelvic stability."),
    ("sacrotuberous_ligament", "skeletal", "Pelvic ligament helping limit sacral movement under load."),
    ("pelvic_symphysis", "skeletal", "Fibrocartilaginous joint joining the pubic bones anteriorly."),
    # Endocrine, immune, integumentary, reproductive and blood support
    ("hypothalamic_pituitary_portal_vessels", "endocrine", "Specialised vascular route carrying hypothalamic releasing signals to the anterior pituitary."),
    ("anterior_pituitary_cell_groups", "endocrine", "Pituitary endocrine cell populations producing multiple regulatory hormones."),
    ("posterior_pituitary_terminals", "endocrine", "Neural terminals releasing hypothalamically produced hormones into circulation."),
    ("pancreatic_alpha_cells", "endocrine", "Pancreatic endocrine cells contributing glucagon signalling."),
    ("pancreatic_beta_cells", "endocrine", "Pancreatic endocrine cells contributing insulin signalling."),
    ("zona_glomerulosa", "endocrine", "Outer adrenal cortical zone producing mineralocorticoid hormones."),
    ("zona_fasciculata", "endocrine", "Adrenal cortical zone producing glucocorticoid hormones."),
    ("zona_reticularis", "endocrine", "Inner adrenal cortical zone producing selected androgen precursors."),
    ("thymic_cortex", "immune", "Thymic region where developing T cells undergo early selection processes."),
    ("thymic_medulla", "immune", "Thymic region involved in later T-cell selection and tolerance mechanisms."),
    ("bone_marrow_stromal_niche", "hematopoietic", "Supportive marrow microenvironment regulating blood-cell progenitors."),
    ("lymph_node_cortex", "immune", "Lymph-node region containing follicles and B-cell-rich areas."),
    ("lymph_node_paracortex", "immune", "Lymph-node region enriched for T cells and specialised antigen-presenting interactions."),
    ("lymph_node_medulla", "immune", "Lymph-node drainage and immune-cell region near efferent lymphatic outflow."),
    ("cutaneous_barrier_lipids", "integumentary", "Intercellular lipid components supporting the epidermal water barrier."),
    ("hair_follicle_bulge", "integumentary", "Follicular stem-cell niche involved in hair-cycle regeneration."),
    ("nail_matrix", "integumentary", "Growth region producing the nail plate."),
    ("dermal_papillae", "integumentary", "Dermal projections supporting exchange and mechanical coupling with overlying epidermis."),
    ("cutaneous_arteriovenous_shunts", "thermoregulation", "Specialised vascular routes regulating heat exchange in selected skin regions."),
    ("mammary_alveoli", "reproductive", "Secretory units of the mammary gland during lactation."),
    ("lactiferous_ducts", "reproductive", "Ducts transporting mammary secretions toward the nipple."),
    ("uterine_endometrium", "reproductive", "Inner uterine lining whose state changes with reproductive physiology."),
    ("uterine_myometrium", "reproductive", "Smooth muscle layer of the uterus."),
    ("fallopian_tube_fimbriae", "reproductive", "Finger-like tubal structures near the ovary that help capture the ovulated oocyte."),
    ("epididymal_duct", "reproductive", "Highly coiled duct where sperm mature and are stored."),
    ("seminiferous_tubules", "reproductive", "Testicular tubules where sperm production occurs."),
    ("blood_brain_barrier_endothelium", "nervous", "Specialised vascular barrier regulating transfer between blood and central nervous-system tissue."),
    ("microglia", "immune", "Resident immune surveillance cells within central nervous-system tissue."),
    ("oligodendrocyte_myelin", "nervous", "Myelin insulation around many central nervous-system axons."),
    ("peripheral_myelin", "nervous", "Myelin around many peripheral nerve fibres, produced by Schwann cells."),
    ("tendon_entheses", "skeletal", "Attachment interfaces transferring force from tendon into bone or periosteal structures."),
    ("muscle_fascicles", "muscular", "Bundles of skeletal muscle fibres organised within connective-tissue sheaths."),
    ("motor_units", "muscular", "Motor neurons and their recruited muscle fibres forming functional force-control units."),
    ("capillary_basement_membrane", "circulatory", "Extracellular matrix layer contributing to microvascular filtration and support."),
    ("lymphatic_valves", "lymphatic", "Valves that support one-way movement of lymph through collecting vessels."),
    ("peritoneal_ligaments", "digestive", "Peritoneal folds supporting selected abdominal viscera and carrying vessels."),
    ("greater_omentum", "digestive", "Peritoneal fold associated with fat storage, immune activity and containment of abdominal inflammation."),
    ("lesser_omentum", "digestive", "Peritoneal fold connecting liver with stomach and proximal duodenum."),
    ("mesocolon", "digestive", "Peritoneal attachment supporting segments of colon and associated neurovascular routes."),
    ("anal_columns", "digestive", "Mucosal folds in the anal canal associated with vascular and glandular structures."),
    ("salivary_ducts", "digestive", "Duct network conducting saliva from major salivary glands to the oral cavity."),
    ("lacrimal_drainage_pathway", "integumentary", "Tear drainage route through canaliculi and the nasolacrimal system."),
]
_HUMAN_DETAIL_STRUCTURES.extend(HUMAN_DETAIL_STRUCTURES_V4)

for _name, _system, _role in _HUMAN_DETAIL_STRUCTURES:
    if _name not in ORGANS:
        _organ(_name, _system, _role, dependencies=[_system])
    ORGANS[_name].setdefault("body_region", "human-specific or human-detailed")
    ORGANS[_name].setdefault("simulation_level", "reference_with_selected_state_hooks")
    ORGANS[_name].setdefault("tags", [_system, "human-detail"] )


def _stock_variant(key, label, base, *, clade, skeleton, movement_mode, special_organs,
                   traits, simulation, system_additions=None, system_removals=None,
                   systems_override=None, inherit_special_organs=True,
                   thermoregulation=None, circulation=None, respiration=None,
                   digestion=None, integument=None, blood=None, senses=None, notes=None,
                   classification="real"):
    """Build an editable stock reference by extending a related body plan."""
    parent = SPECIES[base]
    profile = copy.deepcopy(parent)
    systems_map = ({name: list(items) for name, items in systems_override.items()}
                   if systems_override is not None
                   else {name: list(items) for name, items in parent.get("systems", {}).items()})
    for system_name, names in (system_removals or {}).items():
        systems_map[system_name] = [name for name in systems_map.get(system_name, []) if name not in set(names)]
    for system_name, names in (system_additions or {}).items():
        bucket = systems_map.setdefault(system_name, [])
        for name in names:
            if name not in bucket:
                bucket.append(name)
    profile.update({
        "label": label, "classification": classification, "clade": clade,
        "base": base, "systems": systems_map, "skeleton": copy.deepcopy(skeleton),
        "movement_mode": movement_mode,
        "special_organs": list(dict.fromkeys((list(parent.get("special_organs", [])) if inherit_special_organs else []) + list(special_organs))),
        "traits": {**copy.deepcopy(parent.get("traits", {})), **traits},
        "simulation": copy.deepcopy(simulation),
        "thermoregulation": thermoregulation if thermoregulation is not None else parent.get("thermoregulation"),
        "evidence": "real-species-summary; game trait values are illustrative priors",
        "notes": list(parent.get("notes", [])) + list(notes or []),
    })
    if circulation is not None: profile["circulation"] = copy.deepcopy(circulation)
    if respiration is not None: profile["respiration"] = copy.deepcopy(respiration)
    if digestion is not None: profile["digestion"] = copy.deepcopy(digestion)
    if integument is not None: profile["integument"] = copy.deepcopy(integument)
    if blood is not None: profile["blood"] = copy.deepcopy(blood)
    if senses is not None: profile["senses"] = list(senses)
    SPECIES[key] = profile


# Clade-specific system maps prevent a composite template from inheriting a
# misleading mammalian or annelid default merely because its data was seeded from
# a related profile. They remain high-level reference maps, not full solvers.
_CROCODILIAN_SYSTEMS = {k: list(v) for k, v in REPTILE_SYSTEM_ORGANS.items()}
_CROCODILIAN_SYSTEMS["respiratory"] = ["nasal_cavity", "pharynx", "trachea", "lungs", "airway_mucosa"]
_CROCODILIAN_SYSTEMS["digestive"] = ["oral_cavity", "teeth", "secondary_palate", "conical_teeth", "esophagus", "stomach", "small_intestine", "colon", "liver", "pancreas"]
_CROCODILIAN_SYSTEMS["circulatory"] = ["crocodilian_heart", "heart_valves", "arteries", "veins", "capillaries", "blood", "blood_plasma", "red_blood_cells", "white_blood_cells", "platelets"]
_CROCODILIAN_SYSTEMS["integumentary"] = ["skin", "epidermis", "dermis", "scales", "osteoderms", "cutaneous_glands"]
_CROCODILIAN_SYSTEMS["locomotor"] = ["skeleton", "joints", "cartilage", "ligaments", "tendons", "skeletal_muscles", "webbed_feet", "tail", "claws"]
_CROCODILIAN_SYSTEMS["renal"] = ["kidneys", "nephrons", "ureters", "cloaca"]
_CROCODILIAN_SYSTEMS["reproductive"] = ["gonads", "ovaries", "testes", "reproductive_tract", "cloaca"]
_TORTOISE_SYSTEMS = {k: list(v) for k, v in REPTILE_SYSTEM_ORGANS.items()}
_TORTOISE_SYSTEMS["respiratory"] = ["nasal_cavity", "pharynx", "trachea", "lungs", "airway_mucosa"]
_TORTOISE_SYSTEMS["integumentary"] = ["skin", "epidermis", "dermis", "scales", "carapace", "plastron", "cutaneous_glands"]
_TORTOISE_SYSTEMS["skeletal"] = ["skeleton", "skull", "vertebral_column", "ribs", "carapace", "plastron", "limb_girdles", "forelimb_bones", "hindlimb_bones", "joints", "cartilage", "ligaments", "connective_tissue"]
_TORTOISE_SYSTEMS["digestive"] = ["keratin_beak", "oral_cavity", "esophagus", "stomach", "small_intestine", "colon", "liver", "pancreas"]
_TORTOISE_SYSTEMS["locomotor"] = ["skeleton", "joints", "cartilage", "ligaments", "tendons", "skeletal_muscles", "claws", "forelimb_bones", "hindlimb_bones"]
_FROG_SYSTEMS = {k: list(v) for k, v in REPTILE_SYSTEM_ORGANS.items()}
_FROG_SYSTEMS["respiratory"] = ["lungs", "buccal_cavity", "permeable_skin", "metamorphic_gills"]
_FROG_SYSTEMS["integumentary"] = ["skin", "epidermis", "dermis", "permeable_skin", "cutaneous_glands"]
_FROG_SYSTEMS["skeletal"] = ["skeleton", "skull", "vertebral_column", "ribs", "limb_girdles", "forelimb_bones", "hindlimb_bones", "elongated_hindlimbs", "urostyle", "joints", "cartilage", "connective_tissue"]
_FROG_SYSTEMS["locomotor"] = ["skeleton", "joints", "skeletal_muscles", "tendons", "webbed_feet", "elongated_hindlimbs"]
_SHARK_SYSTEMS = {
    "integumentary": ["skin", "dermis", "dermal_denticles"],
    "skeletal": ["cartilaginous_skeleton", "skull", "vertebral_column", "jaw_cartilages", "connective_tissue"],
    "muscular": ["muscle_tissue", "skeletal_muscles", "tail"],
    "nervous": ["brain", "brainstem", "spinal_cord", "peripheral_nerves", "autonomic_nervous_system"],
    "sensory": ["eyes", "inner_ear", "olfactory_epithelium", "lateral_line", "ampullae_of_lorenzini"],
    "endocrine": ["hypothalamus", "pituitary", "thyroid", "gonads"],
    "circulatory": ["heart", "arteries", "veins", "capillaries", "blood", "blood_plasma", "red_blood_cells"],
    "respiratory": ["gills", "gill_slits"],
    "digestive": ["oral_cavity", "teeth", "esophagus", "stomach", "spiral_valve", "intestines", "oil_rich_liver"],
    "renal": ["kidneys", "cloaca"], "reproductive": ["gonads", "reproductive_tract", "cloaca"],
    "hematopoietic": ["blood", "red_blood_cells"], "locomotor": ["cartilaginous_skeleton", "pectoral_fins", "dorsal_fins", "caudal_fin", "skeletal_muscles"],
}
_OCTOPUS_SYSTEMS = {
    "integumentary": ["skin", "chromatophores"],
    "skeletal": ["mantle", "connective_tissue"],
    "muscular": ["muscle_tissue", "mantle", "arms"],
    "nervous": ["distributed_ganglia", "brain", "peripheral_nerves"],
    "sensory": ["eyes", "statocysts", "suckers", "distributed_ganglia"],
    "circulatory": ["systemic_heart", "branchial_hearts", "hemolymph", "cephalopod_hemocyanin"],
    "respiratory": ["gills", "mantle"],
    "digestive": ["beak", "oral_cavity", "esophagus", "stomach", "intestines"],
    "renal": ["nephridia"], "locomotor": ["mantle", "arms", "suckers", "siphon"],
    "magical_specialisation": ["ink_sac"],
}
_SPIDER_SYSTEMS = {
    "integumentary": ["exoskeleton", "skin"],
    "skeletal": ["exoskeleton", "connective_tissue"],
    "muscular": ["muscle_tissue", "skeletal_muscles"],
    "nervous": ["brain", "distributed_ganglia", "peripheral_nerves"],
    "sensory": ["simple_eyes", "pedipalps", "distributed_ganglia"],
    "circulatory": ["hemolymph"], "respiratory": ["book_lungs", "tracheae"],
    "digestive": ["chelicerae", "oral_cavity", "stomach", "intestines"],
    "renal": ["malpighian_tubules"], "locomotor": ["exoskeleton", "pedipalps", "spinnerets", "chelicerae", "skeletal_muscles"],
    "magical_specialisation": ["venom_glands", "silk_glands"],
}
_DOLPHIN_SYSTEMS = {k: list(v) for k, v in MAMMAL_SYSTEM_ORGANS.items()}
for _sys in list(_DOLPHIN_SYSTEMS):
    _DOLPHIN_SYSTEMS[_sys] = [n for n in _DOLPHIN_SYSTEMS[_sys] if n not in {"hair", "vibrissae", "claws", "diaphragm", "gallbladder", "urinary_bladder", "urethra"}]
_DOLPHIN_SYSTEMS["respiratory"] = ["blowhole", "trachea", "bronchi", "lungs", "alveoli"]
_DOLPHIN_SYSTEMS["locomotor"] = ["skeleton", "vertebral_column", "skeletal_muscles", "flippers", "tail_flukes"]
_DOLPHIN_SYSTEMS["integumentary"] = ["skin", "epidermis", "dermis", "blubber"]
_DOLPHIN_SYSTEMS["sensory"] = ["eyes", "inner_ear", "olfactory_epithelium", "melon", "echolocation_organs"]

# Additional stock templates deliberately span mammals, reptiles, amphibians,
# fish and invertebrates. These are reference/game templates, not an assertion that
# every species within a group shares the same detailed anatomy.
_stock_variant("wolf", "Wolf", "dog", clade="mammal / canid", movement_mode="digitigrade cursorial quadruped",
    skeleton={"type":"endoskeleton","count":None,"inventory":"canid","regions":["axial skeleton","long muzzle","digitigrade limbs","flexible vertebral column","tail"]},
    special_organs=["olfactory_turbinates","whisker_follicles","large_claws"],
    traits={"strength":1.25,"speed":1.55,"endurance":1.55,"senses":1.8,"reflexes":1.4}, simulation={"blood_volume_l":4.0},
    senses=["long-range olfaction","hearing","vision","pack/social signalling","proprioception"],
    notes=["Wolf body traits vary by species, age and condition; values are illustrative game priors."])
_stock_variant("bear", "Bear (generalised template)", "dog", clade="mammal / ursid", movement_mode="plantigrade quadruped with climbing capability",
    skeleton={"type":"endoskeleton","count":None,"inventory":"ursid","regions":["robust axial skeleton","powerful forelimbs","plantigrade feet","broad skull and jaw","tail"]},
    special_organs=["plantigrade_paws","large_claws","fat_reserves","olfactory_turbinates"],
    traits={"strength":2.0,"speed":1.25,"endurance":1.2,"durability":1.4,"senses":1.7,"reflexes":1.0}, simulation={"blood_volume_l":18.0},
    senses=["strong olfaction","hearing","vision","touch","balance"],
    integument={"covering":"fur, thick subcutaneous fat and large claws; species-specific variation"},
    notes=["Generalised bear template; bear species differ greatly in size, diet and ecology."])
_stock_variant("elephant", "Elephant (generalised template)", "human", clade="mammal / proboscidean", movement_mode="large quadruped",
    skeleton={"type":"endoskeleton","count":None,"inventory":"proboscidean","regions":["mass-bearing limbs","columnar limb bones","large skull","trunk support","ribs","pelvis"]},
    special_organs=["trunk","tusk","large_pinnae","foot_cushion","fat_reserves"],
    traits={"strength":3.0,"speed":0.8,"endurance":1.3,"durability":2.0,"senses":1.4,"reflexes":0.7}, simulation={"blood_volume_l":200.0},
    senses=["olfaction","hearing","low-frequency vibration sensitivity","trunk touch","vision"],
    integument={"covering":"thick skin with sparse hair; large ears contribute to heat exchange"},
    notes=["Illustrative large-elephant game baseline; the template does not model all load and heat constraints."])
_stock_variant("bat", "Bat (generalised template)", "dog", clade="mammal / chiropteran", movement_mode="powered flight / hanging / crawling",
    skeleton={"type":"endoskeleton","count":None,"inventory":"chiropteran","regions":["elongated finger bones","wing membrane attachment","shoulder girdle","keel or specialised sternum varies by species","hindlimbs and claws"]},
    special_organs=["wing_membrane","elongated_wing_digits","echolocation_organs","large_claws"],
    traits={"strength":0.65,"speed":1.5,"endurance":1.1,"durability":0.7,"senses":1.8,"reflexes":1.6}, simulation={"blood_volume_l":0.04},
    system_additions={"locomotor":["wings","wing_membrane","elongated_wing_digits"],"sensory":["echolocation_organs"]},
    senses=["echolocation in many species","hearing","vision","olfaction","wing proprioception"],
    notes=["Bat flight is supported by a membrane over elongated digits; not a bird-style feathered wing."])
_stock_variant("crocodile", "Crocodile (generalised crocodilian)", "snake", clade="reptile / crocodilian", movement_mode="quadrupedal / swimming / ambush locomotion", systems_override=_CROCODILIAN_SYSTEMS, inherit_special_organs=False,
    skeleton={"type":"endoskeleton","count":None,"inventory":"crocodilian","regions":["robust skull","vertebral column","ribs","four limbs","osteoderms","powerful tail"]},
    special_organs=["osteoderms","secondary_palate","conical_teeth","crocodilian_heart","webbed_feet","tail","cloaca"],
    traits={"strength":2.2,"speed":1.0,"endurance":1.2,"durability":1.7,"senses":1.35,"reflexes":1.0}, simulation={"blood_volume_l":20.0},
    system_additions={"skeletal":["osteoderms"],"circulatory":["crocodilian_heart"],"locomotor":["webbed_feet","tail"],"digestive":["secondary_palate","conical_teeth"],"renal":["cloaca"]},
    system_removals={"respiratory":["diaphragm"],"integumentary":["hair","vibrissae"],"reproductive":["mammary_glands"]},
    circulation={"type":"closed_double","pump":"four-chambered crocodilian heart","oxygen_carrier":"nucleated erythrocytes","notes":"Shunting behaviour is species- and state-dependent."},
    respiration={"type":"reptilian_lungs","notes":"Breathing mechanics and underwater breath-holding are not fully simulated."},
    thermoregulation="ectothermic; environmental heat and behaviour are important",
    senses=["vision","hearing","pressure/vibration cues","olfaction"],
    notes=["Crocodilian traits vary by species; this profile is not a complete species-specific veterinary model."])
_stock_variant("tortoise", "Tortoise (generalised testudine)", "snake", clade="reptile / testudine", movement_mode="terrestrial quadruped", systems_override=_TORTOISE_SYSTEMS, inherit_special_organs=False,
    skeleton={"type":"endoskeleton","count":None,"inventory":"testudine_shell","regions":["carapace integrated with ribs/vertebrae","plastron","limb girdles","limb bones","skull"]},
    special_organs=["carapace","plastron","keratin_beak","cloaca"],
    traits={"strength":0.8,"speed":0.35,"endurance":1.2,"durability":2.1,"senses":0.9,"reflexes":0.55}, simulation={"blood_volume_l":0.8},
    system_additions={"skeletal":["carapace","plastron"],"digestive":["keratin_beak"],"renal":["cloaca"]},
    system_removals={"respiratory":["diaphragm"],"integumentary":["hair","vibrissae"]},
    senses=["vision","olfaction","touch","vibration"],
    notes=["Tortoise shell is integrated with the skeleton; it is not an external removable box in the biological template."])
_stock_variant("frog", "Frog (generalised amphibian)", "snake", clade="amphibian / anuran", movement_mode="jumping / swimming / terrestrial locomotion", systems_override=_FROG_SYSTEMS, inherit_special_organs=False,
    skeleton={"type":"endoskeleton","count":None,"inventory":"anuran","regions":["short vertebral column","elongated hindlimbs","pelvic girdle","urostyle","forelimb landing support"]},
    special_organs=["permeable_skin","buccal_cavity","webbed_feet","tympanum","metamorphic_gills","cloaca"],
    traits={"strength":0.8,"speed":1.1,"endurance":0.65,"durability":0.65,"senses":1.0,"reflexes":1.5}, simulation={"blood_volume_l":0.02},
    system_additions={"integumentary":["permeable_skin"],"respiratory":["buccal_cavity","metamorphic_gills"],"sensory":["tympanum"],"locomotor":["webbed_feet"]},
    system_removals={"respiratory":["diaphragm"],"integumentary":["hair","vibrissae"],"digestive":["gallbladder"]},
    respiration={"type":"adult lungs plus cutaneous exchange; larval gills vary by life stage"},
    thermoregulation="ectothermic; skin moisture can be important",
    senses=["vision","hearing","vibration","chemical sensing","skin pressure cues"],
    notes=["Frog life stages differ; the larval gill structures are marked as stage-dependent reference features."])
_stock_variant("shark", "Shark (generalised cartilaginous fish)", "snake", clade="cartilaginous fish / elasmobranch", movement_mode="aquatic swimming", systems_override=_SHARK_SYSTEMS, inherit_special_organs=False,
    skeleton={"type":"cartilaginous","count":None,"inventory":"elasmobranch","regions":["cartilaginous cranium","vertebral column","jaw cartilages","pectoral girdle/fins","pelvic fins","caudal fin"]},
    special_organs=["cartilaginous_skeleton","gills","gill_slits","pectoral_fins","dorsal_fins","caudal_fin","dermal_denticles","lateral_line","ampullae_of_lorenzini","spiral_valve","oil_rich_liver","cloaca"],
    traits={"strength":1.3,"speed":1.4,"endurance":1.5,"durability":1.0,"senses":1.8,"reflexes":1.35}, simulation={"blood_volume_l":25.0},
    system_additions={"skeletal":["cartilaginous_skeleton"],"respiratory":["gills","gill_slits"],"locomotor":["pectoral_fins","dorsal_fins","caudal_fin"],"integumentary":["dermal_denticles"],"sensory":["lateral_line","ampullae_of_lorenzini"],"digestive":["spiral_valve","oil_rich_liver"],"renal":["cloaca"]},
    system_removals={"respiratory":["lungs","diaphragm","alveoli","bronchi","bronchioles"],"integumentary":["hair","vibrissae","cutaneous_glands"],"reproductive":["mammary_glands","uterus","mammary_glands"]},
    circulation={"type":"closed circulation","pump":"two-chambered heart","oxygen_carrier":"fish erythrocytes; species-specific blood chemistry"},
    respiration={"type":"gills","notes":"Water must pass over functioning gills for ordinary aquatic respiration in this model."},
    digestion={"type":"predatory fish digestion","structures":["mouth","teeth","esophagus","stomach","spiral_valve","intestines","oil_rich_liver"]},
    thermoregulation="ectothermic; some shark lineages have regional endothermy",
    senses=["electroreception","lateral-line mechanosensation","olfaction","vision","hearing/vibration"],
    notes=["Generalised shark template; gill count, buoyancy strategy and reproduction vary among shark taxa."])
_stock_variant("dolphin", "Dolphin (generalised toothed cetacean)", "dog", clade="mammal / cetacean", movement_mode="aquatic swimming / diving", systems_override=_DOLPHIN_SYSTEMS, inherit_special_organs=False,
    skeleton={"type":"endoskeleton","count":None,"inventory":"cetacean","regions":["streamlined axial skeleton","reduced pelvic vestiges","flipper bones","tail flukes","neck vertebrae with restricted motion"]},
    special_organs=["blowhole","melon","flippers","tail_flukes","blubber","echolocation_organs"],
    traits={"strength":1.8,"speed":1.8,"endurance":1.5,"durability":1.1,"senses":1.8,"reflexes":1.5}, simulation={"blood_volume_l":35.0},
    system_additions={"respiratory":["blowhole"],"locomotor":["flippers","tail_flukes"],"integumentary":["blubber"],"sensory":["melon","echolocation_organs"]},
    circulation={"type":"closed double mammalian circulation","pump":"four-chambered heart"},
    respiration={"type":"lungs via blowhole","notes":"Dolphins are mammals and must surface to breathe; they do not have gills."},
    integument={"covering":"streamlined skin over subcutaneous blubber; external hair is reduced"},
    senses=["biosonar/echolocation","hearing","vision","touch","social acoustic communication"],
    notes=["Aquatic traits do not imply underwater breathing; breath-hold and diving responses are approximations."])
_stock_variant("octopus", "Octopus (generalised cephalopod)", "earthworm", clade="mollusc / cephalopod", movement_mode="aquatic crawling / jet propulsion / grasping", systems_override=_OCTOPUS_SYSTEMS, inherit_special_organs=False,
    skeleton={"type":"none","count":None,"inventory":"cephalopod","regions":["soft mantle","head and beak","eight arms","siphon","internal support structures vary by species"]},
    special_organs=["mantle","arms","suckers","beak","siphon","gills","systemic_heart","branchial_hearts","chromatophores","distributed_ganglia","ink_sac","statocysts","cephalopod_hemocyanin"],
    traits={"strength":0.8,"speed":1.1,"endurance":0.8,"durability":0.55,"senses":1.4,"reflexes":1.25,"regeneration":1.15}, simulation={"blood_volume_l":0.3},
    system_additions={"skeletal":["mantle"],"locomotor":["arms","suckers","siphon"],"circulatory":["systemic_heart","branchial_hearts","cephalopod_hemocyanin"],"respiratory":["gills"],"sensory":["statocysts"],"integumentary":["chromatophores"],"nervous":["distributed_ganglia"],"magical_specialisation":["ink_sac"]},
    system_removals={"skeletal":["bones","skull","vertebral_column","sternum","ribs"],"respiratory":["lungs","diaphragm","alveoli"],"integumentary":["hair","feathers","vibrissae"],"locomotor":["legs","wings"]},
    circulation={"type":"closed circulation","pump":"three hearts (one systemic and two branchial)","oxygen_carrier":"hemocyanin-rich blood in many cephalopods"},
    respiration={"type":"gills","notes":"Aquatic gill ventilation and mantle movement are not a full fluid simulation."},
    digestion={"type":"predatory cephalopod","structures":["beak","radula where present","esophagus","stomach","digestive gland","intestine"]},
    thermoregulation="ectothermic marine invertebrate",
    senses=["camera-type eyes","chemosensation","touch/sucker sensation","balance/statocysts","distributed arm sensing"],
    notes=["Octopus limbs show substantial local neural control; this template is not a full nervous-system simulation."])
_stock_variant("spider", "Spider (generalised arachnid)", "earthworm", clade="arthropod / arachnid", movement_mode="terrestrial crawling / climbing / silk production", systems_override=_SPIDER_SYSTEMS, inherit_special_organs=False,
    skeleton={"type":"exoskeleton","count":None,"inventory":"arachnid","regions":["prosoma exoskeleton","opisthosoma","eight walking legs","chelicerae","pedipalps","spinnerets"]},
    special_organs=["exoskeleton","chelicerae","pedipalps","spinnerets","book_lungs","tracheae","venom_glands","silk_glands","simple_eyes","hemolymph","malpighian_tubules"],
    traits={"strength":0.55,"speed":1.0,"endurance":0.7,"durability":0.65,"senses":1.25,"reflexes":1.45}, simulation={"blood_volume_l":0.0005},
    system_additions={"integumentary":["exoskeleton"],"locomotor":["pedipalps","spinnerets"],"respiratory":["book_lungs","tracheae"],"circulatory":["hemolymph"],"renal":["malpighian_tubules"],"sensory":["simple_eyes"],"magical_specialisation":["venom_glands","silk_glands"]},
    system_removals={"skeletal":["bones","skull","vertebral_column","sternum","ribs"],"respiratory":["lungs","diaphragm","alveoli"],"integumentary":["hair","feathers","vibrissae"],"circulatory":["heart","red_blood_cells","platelets"]},
    circulation={"type":"open circulatory system","pump":"dorsal vessel/heart-like pump","oxygen_carrier":"hemolymph; details vary by lineage"},
    respiration={"type":"book lungs and/or tracheae; species-dependent"},
    thermoregulation="ectothermic arthropod",
    senses=["vibration sensing","simple eyes","chemical sensing","airflow/touch through sensory hairs"],
    notes=["Venom and silk systems vary among spider species; the template does not make them universal in all arachnids."])

# Additional clade maps and stock profiles. These extend the catalogue from a
# handful of broad vertebrates to distinct mammal, bird, amphibian, insect,
# crustacean, mollusc and fictional composite body plans.
_INSECT_SYSTEMS = {
    "integumentary": ["exoskeleton", "skin", "cuticle"],
    "skeletal": ["exoskeleton", "walking_legs", "wing_bars"],
    "muscular": ["muscle_tissue", "body_wall_muscles", "walking_legs"],
    "nervous": ["brain", "distributed_ganglia", "ventral_nerve_cord"],
    "sensory": ["compound_eyes", "antennae", "simple_eyes"],
    "circulatory": ["hemolymph", "dorsal_vessel"],
    "respiratory": ["spiracles", "tracheae"],
    "digestive": ["mandibles", "crop", "gizzard", "intestines"],
    "renal": ["malpighian_tubules"],
    "reproductive": ["gonads", "spermatheca", "egg_sac"],
    "locomotor": ["walking_legs", "six_legs", "wing_bars"],
    "defence": ["sting", "glandular_venom_reservoir"],
}
_CRAB_SYSTEMS = {
    "integumentary": ["exoskeleton", "carapace", "cuticle"],
    "skeletal": ["exoskeleton", "carapace", "walking_legs", "crushing_claw"],
    "muscular": ["muscle_tissue", "walking_legs", "crushing_claw"],
    "nervous": ["brain", "distributed_ganglia", "ventral_nerve_cord"],
    "sensory": ["compound_eyes", "antennae", "statocysts"],
    "circulatory": ["hemolymph", "dorsal_vessel"],
    "respiratory": ["crab_gills", "gills"],
    "digestive": ["mandibles", "stomach", "intestines"],
    "renal": ["nephridia"],
    "reproductive": ["gonads", "egg_sac"],
    "locomotor": ["walking_legs", "crushing_claw"],
}
_HYDRA_SYSTEMS = {
    "integumentary": ["skin", "body_wall_muscles"],
    "nervous": ["nerve_net", "tentacles"],
    "sensory": ["tentacles", "nerve_net"],
    "digestive": ["gastrovascular_cavity", "tentacles"],
    "locomotor": ["basal_disc", "tentacles", "body_wall_muscles"],
    "developmental": ["regenerative_buds"],
    "defence": ["nematocysts"],
}
_FISH_SYSTEMS = {
    "integumentary": ["skin", "scales", "mucus_glands"],
    "skeletal": ["skeleton", "skull", "vertebral_column", "ribs", "fin_rays", "jaws"],
    "muscular": ["muscle_tissue", "body_wall_muscles"],
    "nervous": ["brain", "brainstem", "spinal_cord", "peripheral_nerves"],
    "sensory": ["eyes", "olfactory_epithelium", "lateral_line", "inner_ear"],
    "circulatory": ["fish_heart", "blood", "arteries", "veins", "capillaries"],
    "respiratory": ["gills", "gill_arches", "gill_filaments", "operculum"],
    "digestive": ["mouth", "jaws", "teeth", "esophagus", "stomach", "pyloric_caeca", "intestines", "liver"],
    "renal": ["kidneys", "nephrons"],
    "reproductive": ["gonads", "reproductive_tract"],
    "locomotor": ["fins", "fin_rays", "tail"],
}
_GASTROPOD_SYSTEMS = {
    "integumentary": ["skin", "mantle", "shell"],
    "skeletal": ["shell", "muscular_foot"],
    "muscular": ["body_wall_muscles", "muscular_foot"],
    "nervous": ["cerebral_ganglia", "ganglia", "nerve_cord"],
    "sensory": ["tentacles", "statocysts", "olfactory_epithelium"],
    "circulatory": ["heart", "hemolymph", "circulatory_vessels"],
    "respiratory": ["gills", "pneumostome", "mantle"],
    "digestive": ["mouth", "radula", "crop", "stomach", "hepatopancreas", "intestines"],
    "renal": ["nephridia"],
    "reproductive": ["gonads", "reproductive_tract", "spermatheca"],
    "locomotor": ["muscular_foot", "tentacles", "mantle"],
}
_SCORPION_SYSTEMS = {key: list(value) for key, value in _SPIDER_SYSTEMS.items()}
_SCORPION_SYSTEMS["respiratory"] = ["book_lungs", "tracheae"]
_SCORPION_SYSTEMS["defence"] = ["venom_telson", "venom_glands", "defensive_glands"]
_SCORPION_SYSTEMS["sensory"] = ["simple_eyes", "pectines", "sensory_hairs"]
_LIZARD_SYSTEMS = {key: list(value) for key, value in REPTILE_SYSTEM_ORGANS.items()}
_LIZARD_SYSTEMS["respiratory"] = ["nasal_cavity", "pharynx", "trachea", "lungs", "airway_mucosa"]
_LIZARD_SYSTEMS["locomotor"] = ["skeleton", "joints", "skeletal_muscles", "forelimb_bones", "hindlimb_bones", "claws", "tail"]
_LIZARD_SYSTEMS["sensory"] = ["eyes", "independently_moving_eyes", "olfactory_epithelium", "vomeronasal_organ", "inner_ear"]
_JELLYFISH_SYSTEMS = {key: list(value) for key, value in _HYDRA_SYSTEMS.items()}
_JELLYFISH_SYSTEMS["locomotor"] = ["jellyfish_bell", "bell_margin_sensors", "tentacles", "body_wall_muscles"]
_JELLYFISH_SYSTEMS["sensory"] = ["rhopalia", "statocysts", "bell_margin_sensors", "nerve_net"]
_JELLYFISH_SYSTEMS["defence"] = ["nematocysts"]
_SEA_STAR_SYSTEMS = {
    "integumentary": ["skin", "pedicellariae"],
    "skeletal": ["ossicles", "radial_ossicles", "spines", "pedicellariae"],
    "muscular": ["body_wall_muscles", "tube_feet"],
    "nervous": ["radial_nerve", "nerve_ring", "sensory_epithelium"],
    "sensory": ["sensory_epithelium", "statocysts"],
    "circulatory": ["water_vascular_system", "madreporite", "haemal_channels"],
    "digestive": ["mouth", "stomach", "pyloric_caeca", "intestines"],
    "locomotor": ["tube_feet", "radial_ossicles", "spines"],
    "developmental": ["regenerative_buds"],
    "defence": ["pedicellariae", "spines"],
}
_MYRIAPOD_SYSTEMS = {key: list(value) for key, value in _INSECT_SYSTEMS.items()}
_MYRIAPOD_SYSTEMS["locomotor"] = ["walking_legs", "diplosomites", "body_wall_muscles"]
_MYRIAPOD_SYSTEMS["defence"] = ["defensive_glands", "cuticle"]

_stock_variant("deer", "Deer (generalised cervid)", "cow", clade="mammal / cervid", movement_mode="cursorial quadruped / jumping",
    skeleton={"type":"endoskeleton","count":None,"inventory":"cervid","regions":["slender axial skeleton","long limb bones","cloven hooves","cervical spine","antler attachment where present"]},
    special_organs=["antlers","large_pinnae","olfactory_turbinates","hooves"],
    traits={"strength":1.1,"speed":1.65,"endurance":1.35,"durability":0.9,"senses":1.5,"reflexes":1.5}, simulation={"blood_volume_l":6.0},
    notes=["Cervid antlers are seasonal bony structures in many species; antler presence and branching vary by sex, species and life stage."])
_stock_variant("rabbit", "Rabbit (generalised lagomorph)", "dog", clade="mammal / lagomorph", movement_mode="terrestrial hopping / digging",
    skeleton={"type":"endoskeleton","count":None,"inventory":"lagomorph","regions":["light axial skeleton","elongated hindlimbs","pelvic girdle","incisor apparatus"]},
    special_organs=["large_pinnae","cecum","whisker_follicles","large_claws","fat_reserves"],
    traits={"strength":0.45,"speed":1.45,"endurance":0.8,"durability":0.55,"senses":1.4,"reflexes":1.7}, simulation={"blood_volume_l":0.18},
    system_additions={"digestive":["cecum"],"locomotor":["large_claws"]},
    notes=["Rabbit profiles should represent powerful hindlimb propulsion and hindgut fermentation rather than a generic small dog."])
_stock_variant("camel", "Camel (generalised camelid)", "horse", clade="mammal / camelid", movement_mode="cursorial quadruped / desert endurance",
    skeleton={"type":"endoskeleton","count":None,"inventory":"camelid","regions":["long limbs","padded feet","long neck","specialised axial load support"]},
    special_organs=["fat_reserves","foot_cushion","large_pinnae","ruminant_microbiome"],
    traits={"strength":1.6,"speed":1.0,"endurance":2.0,"durability":1.25,"senses":1.0,"reflexes":0.9}, simulation={"blood_volume_l":45.0},
    thermoregulation="endothermic with strong water-conservation and variable-temperature adaptations",
    notes=["Camel digestive anatomy differs from true ruminants; this profile is a camelid game template and should not be interpreted as a cattle stomach model."])
_stock_variant("kangaroo", "Kangaroo (generalised macropod)", "dog", clade="mammal / marsupial / macropod", movement_mode="bipedal hopping / tail-supported posture",
    skeleton={"type":"endoskeleton","count":None,"inventory":"macropod","regions":["elongated hindlimbs","specialised ankle/foot","reduced forelimbs","large balancing tail"]},
    special_organs=["pouch","kangaroo_hindlimbs","tail","fat_reserves"],
    traits={"strength":1.1,"speed":1.6,"endurance":1.35,"durability":1.0,"senses":1.0,"reflexes":1.4}, simulation={"blood_volume_l":9.0},
    notes=["A macropod's hopping gait is not equivalent to a bipedal human gait; specialised hindlimb and tail mechanics need a locomotion solver for detailed movement."])
_stock_variant("chicken", "Chicken (generalised galliform bird)", "eagle", clade="bird / galliform", movement_mode="terrestrial walking / short-burst flight",
    skeleton={"type":"endoskeleton","count":None,"inventory":"galliform","regions":["keeled sternum","wing bones","hindlimbs","beak","tail vertebrae"]},
    special_organs=["bird_keel","feather_follicles","crop","gizzard","cloaca","comb","wattle","air_sacs","keratin_beak"],
    traits={"strength":0.45,"speed":0.75,"endurance":0.8,"durability":0.65,"senses":1.0,"reflexes":1.0}, simulation={"blood_volume_l":0.18},
    system_additions={"digestive":["crop","gizzard","cloaca"],"locomotor":["bird_keel","feather_follicles"]},
    notes=["Flight ability, body size and egg-laying traits vary substantially across domestic breeds; values are illustrative game priors."])
_stock_variant("penguin", "Penguin (generalised diving bird)", "eagle", clade="bird / sphenisciform", movement_mode="aquatic swimming / diving; terrestrial waddling", inherit_special_organs=False,
    skeleton={"type":"endoskeleton","count":None,"inventory":"penguin","regions":["dense flightless-bird skeleton","wing bones modified as flippers","webbed feet","keel","tail"]},
    special_organs=["bird_keel","feather_follicles","flippers","webbed_feet","air_sacs","blubber"],
    traits={"strength":0.9,"speed":1.35,"endurance":1.6,"durability":1.0,"senses":1.0,"reflexes":1.1}, simulation={"blood_volume_l":1.0},
    system_additions={"locomotor":["flippers","webbed_feet"],"integumentary":["blubber"]},
    system_removals={"locomotor":["wings"]},
    thermoregulation="endothermic; dense feathering and fat insulation support cold-water life",
    notes=["Penguin wings are flippers for underwater propulsion; this profile does not confer powered aerial flight."])
_stock_variant("seal", "Seal (generalised pinniped)", "dog", clade="mammal / pinniped", movement_mode="aquatic swimming / diving; terrestrial haul-out",
    skeleton={"type":"endoskeleton","count":None,"inventory":"pinniped","regions":["axial skeleton","foreflippers","hindflippers","spinal flexibility","tail region"]},
    special_organs=["flippers","blubber","whisker_follicles","large_pinnae"],
    traits={"strength":1.15,"speed":1.35,"endurance":1.5,"durability":1.15,"senses":1.3,"reflexes":1.15}, simulation={"blood_volume_l":18.0},
    system_additions={"locomotor":["flippers"],"integumentary":["blubber"]},
    thermoregulation="endothermic marine mammal; insulation and dive responses are simplified",
    notes=["Pinniped propulsion differs across true seals, sea lions and walruses; this is a general template."])
_stock_variant("whale", "Whale (generalised cetacean)", "dolphin", clade="mammal / cetacean", movement_mode="aquatic swimming / deep diving",
    skeleton={"type":"endoskeleton","count":None,"inventory":"cetacean","regions":["large axial skeleton","reduced pelvic vestiges","flippers","tail flukes","rib cage"]},
    special_organs=["blowhole","flippers","tail_flukes","blubber","baleen","rostrum"],
    traits={"strength":3.0,"speed":1.3,"endurance":2.0,"durability":2.0,"senses":1.4,"reflexes":0.9}, simulation={"blood_volume_l":2500.0},
    notes=["Baleen and toothed whales differ substantially; treat feeding structures and dive physiology as template choices, not a universal whale design."])
_stock_variant("squid", "Squid (generalised cephalopod)", "octopus", clade="mollusc / cephalopod / squid", movement_mode="aquatic jet propulsion / fin swimming",
    skeleton={"type":"none","count":None,"inventory":"cephalopod","regions":["mantle","internal pen","head","fins","eight arms and two tentacles","siphon"]},
    special_organs=["mantle","mantle_pen","arms","tentacles","suckers","siphon","gills","systemic_heart","branchial_hearts","chromatophores","distributed_ganglia","ink_sac","statocysts","cephalopod_hemocyanin"],
    traits={"strength":1.0,"speed":1.5,"endurance":1.0,"durability":0.55,"senses":1.4,"reflexes":1.4,"regeneration":1.0}, simulation={"blood_volume_l":0.5},
    system_additions={"skeletal":["mantle_pen"],"locomotor":["tentacles","siphon"],"magical_specialisation":["ink_sac"]},
    notes=["The internal pen is a flexible support rather than a vertebrate skeleton; squid propulsion uses mantle and siphon mechanics not fully simulated here."])
_stock_variant("crab", "Crab (generalised decapod crustacean)", "spider", clade="arthropod / crustacean / decapod", movement_mode="terrestrial or aquatic walking / sideways locomotion",
    systems_override=_CRAB_SYSTEMS, inherit_special_organs=False,
    skeleton={"type":"exoskeleton","count":None,"inventory":"decapod","regions":["cephalothorax carapace","abdomen","five pairs of thoracic appendages","claws"]},
    special_organs=["exoskeleton","carapace","antennae","compound_eyes","walking_legs","crushing_claw","crab_gills","hemolymph","mandibles"],
    traits={"strength":0.85,"speed":0.75,"endurance":0.9,"durability":1.5,"senses":1.0,"reflexes":1.0}, simulation={"blood_volume_l":0.04},
    notes=["Crabs use a calcified external skeleton and open circulation; gill requirements depend on species and habitat."])
_stock_variant("bee", "Bee (generalised insect)", "spider", clade="arthropod / insect / hymenopteran", movement_mode="flight / walking / nectar gathering",
    systems_override=_INSECT_SYSTEMS, inherit_special_organs=False,
    skeleton={"type":"exoskeleton","count":None,"inventory":"insect","regions":["head","thorax","abdomen","six legs","two pairs of wings where present"]},
    special_organs=["exoskeleton","compound_eyes","antennae","mandibles","six_legs","spiracles","tracheae","wing_bars","crop","sting","pollen_baskets","hemolymph"],
    traits={"strength":0.05,"speed":1.4,"endurance":1.2,"durability":0.25,"senses":1.5,"reflexes":1.6}, simulation={"blood_volume_l":0.00002},
    system_additions={"locomotor":["wing_bars","pollen_baskets"],"feeding":["mandibles"],"defence":["sting"]},
    thermoregulation="small ectothermic insect with social thermoregulation possible in some species",
    notes=["A bee's colony behaviour, caste, reproductive status and sting presence vary; the model is an individual body template, not a colony simulation."])
_stock_variant("ant", "Ant (generalised insect)", "spider", clade="arthropod / insect / formicid", movement_mode="terrestrial walking / climbing / carrying loads",
    systems_override=_INSECT_SYSTEMS, inherit_special_organs=False,
    skeleton={"type":"exoskeleton","count":None,"inventory":"insect","regions":["head","thorax/alitrunk","petiole","abdomen","six legs","antennae"]},
    special_organs=["exoskeleton","compound_eyes","antennae","mandibles","six_legs","spiracles","tracheae","hemolymph","glandular_venom_reservoir"],
    traits={"strength":0.03,"speed":0.65,"endurance":1.3,"durability":0.25,"senses":1.5,"reflexes":1.35}, simulation={"blood_volume_l":0.00001},
    notes=["Ants vary by caste and species; individual anatomy is modelled separately from colony organisation or pheromone communication networks."])
_stock_variant("salamander", "Salamander (generalised amphibian)", "frog", clade="amphibian / urodela", movement_mode="terrestrial crawling / swimming / tail propulsion",
    skeleton={"type":"endoskeleton","count":None,"inventory":"urodele","regions":["elongated trunk","tail vertebrae","four limbs in typical forms","shoulder and pelvic girdles"]},
    special_organs=["permeable_skin","lungs","tail","metamorphic_gills","regenerative_limb_bud"],
    traits={"strength":0.65,"speed":0.7,"endurance":0.8,"durability":0.65,"senses":0.9,"reflexes":0.8,"regeneration":1.4}, simulation={"blood_volume_l":0.03},
    notes=["Regenerative ability varies widely among salamander species and tissues; this profile only provides a starting point for explicitly defined regeneration rules."])
_stock_variant("freshwater_hydra", "Freshwater Hydra (simple cnidarian)", "earthworm", clade="cnidarian / hydrozoan", movement_mode="anchored / gliding / somersaulting in some species", systems_override=_HYDRA_SYSTEMS, inherit_special_organs=False,
    skeleton={"type":"hydrostatic","count":None,"inventory":"cnidarian","regions":["body column","tentacles","basal disc","gastrovascular cavity"]},
    special_organs=["nerve_net","tentacles","nematocysts","gastrovascular_cavity","basal_disc","regenerative_buds"],
    traits={"strength":0.05,"speed":0.1,"endurance":0.8,"durability":0.3,"senses":0.4,"reflexes":0.4,"regeneration":2.5}, simulation={"blood_volume_l":0.00001},
    classification="real", thermoregulation="ectothermic aquatic invertebrate",
    notes=["Hydra lacks vertebrate-style brain, heart, blood, lungs and skeleton; this profile uses a nerve-net and gastrovascular body plan. Regeneration values are a game abstraction."])


def _stock_composite(key, label, component_keys, *, primary, movement_mode, movement_capabilities,
                     skeleton_type="hybrid", remove_organs=None, traits=None, notes=None):
    """Static editable fantasy hybrid assembled from multiple catalogue profiles."""
    sources = [(name, SPECIES[name]) for name in component_keys]
    base = SPECIES[primary]
    profile = copy.deepcopy(base)
    removed = set(remove_organs or [])
    merged_systems = {}
    merged_special = []
    component_types = []
    regions = []
    organ_sources = {}
    for source_name, source in sources:
        component_types.append(source.get("skeleton", {}).get("type", "unknown"))
        regions.extend(source.get("skeleton", {}).get("regions", []))
        for sys_name, organs in source.get("systems", {}).items():
            bucket = merged_systems.setdefault(sys_name, [])
            for organ in organs:
                if organ not in removed and organ not in bucket:
                    bucket.append(organ)
                if organ not in removed:
                    organ_sources.setdefault(organ, [])
                    if source_name not in organ_sources[organ]:
                        organ_sources[organ].append(source_name)
        for organ in source.get("special_organs", []):
            if organ not in removed and organ not in merged_special:
                merged_special.append(organ)
            if organ not in removed:
                organ_sources.setdefault(organ, [])
                if source_name not in organ_sources[organ]:
                    organ_sources[organ].append(source_name)
    merged_systems = {name: [organ for organ in organs if organ not in removed]
                      for name, organs in merged_systems.items() if any(organ not in removed for organ in organs)}
    base_traits = copy.deepcopy(base.get("traits", {}))
    all_trait_names = set().union(*(source.get("traits", {}).keys() for _, source in sources))
    for trait in all_trait_names:
        base_traits[trait] = max(float(source.get("traits", {}).get(trait, 1.0)) for _, source in sources)
    base_traits.update(traits or {})
    profile.update({
        "label": label, "classification": "fictional-design-proposal", "clade": "fictional composite",
        "base": primary, "components": list(component_keys), "component_sources": organ_sources,
        "systems": merged_systems, "special_organs": merged_special,
        "skeleton": {"type": skeleton_type, "count": None, "inventory": "composite_or_species_specific", "regions": list(dict.fromkeys(regions)), "component_types": list(dict.fromkeys(component_types))},
        "movement_mode": movement_mode, "movement_capabilities": list(movement_capabilities),
        "traits": base_traits,
        "circulation": {"type": "composite design assumption", "components": [source.get("circulation", {}) for _, source in sources], "notes": "Choose how donor circulation systems integrate; merged records do not mean automatic physiological compatibility."},
        "respiration": {"type": "composite design assumption", "components": [source.get("respiration", {}) for _, source in sources], "notes": "Choose a coherent respiratory plan or explicitly define magical support."},
        "digestion": {"type": "composite design assumption", "components": [source.get("digestion", {}) for _, source in sources], "notes": "Donor digestive anatomies are not automatically compatible."},
        "evidence": "fictional multi-template design proposal",
        "notes": list(notes or []) + ["This composite is an editable starting point. Validate organ connections, body plan, movement, respiration and circulation before treating it as functionally viable."],
    })
    SPECIES[key] = profile

# More species templates across mammals, birds, reptiles, fish, molluscs,
# arthropods and cnidarians. These are deliberately editable reference bodies;
# shared data describes homologous structures, not identical behaviour.
_stock_variant("chimpanzee", "Chimpanzee (generalised ape)", "human", clade="mammal / primate / ape", movement_mode="knuckle-walking / climbing / brachiation-capable",
    skeleton={"type":"endoskeleton","count":None,"inventory":"great_ape","regions":["robust shoulder girdle","long arms","grasping hands","knuckle-walking forelimb structures","shorter lower limbs relative to arms"]},
    special_organs=["opposable_thumb","brachiation_shoulders","knuckle_walking_metacarpals","canine_teeth","large_jaw_muscles"],
    traits={"strength":1.5,"speed":1.2,"endurance":1.15,"durability":1.25,"senses":1.1,"reflexes":1.2}, simulation={"blood_volume_l":4.0},
    notes=["Great-ape locomotion is not a human gait with altered strength; climbing and knuckle-walking need movement rules."])
_stock_variant("gorilla", "Gorilla (generalised ape)", "chimpanzee", clade="mammal / primate / ape", movement_mode="knuckle-walking / climbing",
    skeleton={"type":"endoskeleton","count":None,"inventory":"gorilla","regions":["large robust body frame","broad thorax","long forelimbs","knuckle-walking forelimbs","large jaw and skull"]},
    special_organs=["opposable_thumb","knuckle_walking_metacarpals","large_jaw_muscles","canine_teeth"],
    traits={"strength":2.1,"speed":0.95,"endurance":1.25,"durability":1.6,"senses":1.0,"reflexes":0.9}, simulation={"blood_volume_l":10.0})
_stock_variant("goat", "Goat (generalised caprine ruminant)", "cow", clade="mammal / caprine ruminant", movement_mode="quadrupedal / climbing / jumping",
    inherit_special_organs=False, skeleton={"type":"endoskeleton","count":None,"inventory":"caprine","regions":["cloven hooves","horn attachment where present","flexible spine","quadruped limb bones"]},
    special_organs=["rumen","reticulum","omasum","abomasum","ruminant_microbiome","goat_horns","hooves","rumen_papillae","beard"],
    traits={"strength":1.0,"speed":1.2,"endurance":1.3,"durability":1.0,"senses":1.1,"reflexes":1.25}, simulation={"blood_volume_l":4.0},
    thermoregulation="endothermic ruminant; coat and heat tolerance vary by breed",
    notes=["Horn presence, beard and coat vary by sex and breed; the template is not a universal goat individual."])
_stock_variant("sheep", "Sheep (generalised ovine ruminant)", "goat", clade="mammal / ovine ruminant", movement_mode="quadrupedal / grazing / flock movement",
    inherit_special_organs=False, skeleton={"type":"endoskeleton","count":None,"inventory":"ovine","regions":["cloven hooves","horn attachment where present","quadruped limb bones"]},
    special_organs=["rumen","reticulum","omasum","abomasum","ruminant_microbiome","sheep_wool_follicles","hooves","rumen_papillae"],
    traits={"strength":0.9,"speed":0.95,"endurance":1.25,"durability":0.95,"senses":1.0,"reflexes":1.0}, simulation={"blood_volume_l":4.0})
_stock_variant("rhinoceros", "Rhinoceros (generalised rhino)", "elephant", clade="mammal / perissodactyl", movement_mode="large quadruped / charge",
    inherit_special_organs=False, skeleton={"type":"endoskeleton","count":None,"inventory":"rhinoceros","regions":["massive axial frame","thick limb bones","large shoulder/hip attachments","horn-supporting skull"]},
    special_organs=["rhino_horn","thick_dermis","large_nares","thick_skin","keratinised_footpads"],
    traits={"strength":2.2,"speed":1.15,"endurance":1.1,"durability":2.0,"senses":0.9,"reflexes":0.8}, simulation={"blood_volume_l":180.0})
_stock_variant("hippopotamus", "Hippopotamus (generalised hippo)", "dolphin", clade="mammal / artiodactyl / semi-aquatic", movement_mode="quadrupedal / wading / swimming",
    inherit_special_organs=False, skeleton={"type":"endoskeleton","count":None,"inventory":"hippopotamus","regions":["barrel-shaped axial frame","short strong limbs","large skull","webbed feet"]},
    special_organs=["hippo_canine_tusks","aquatic_ear_valves","thick_dermis","cutaneous_glands","webbed_feet"],
    traits={"strength":2.4,"speed":0.9,"endurance":1.2,"durability":1.8,"senses":1.0,"reflexes":0.75}, simulation={"blood_volume_l":250.0},
    thermoregulation="endothermic semi-aquatic mammal; skin and water exposure affect heat exchange",
    digestion={"type":"hindgut_fermenter_herbivore","structures":["oral_cavity","large_incisisors","hippo_canine_tusks","stomach","intestines","liver","pancreas"]})
_stock_variant("ostrich", "Ostrich (generalised flightless bird)", "eagle", clade="bird / ratite", movement_mode="terrestrial high-speed running / kicking",
    inherit_special_organs=False, skeleton={"type":"endoskeleton","count":None,"inventory":"ratite","regions":["long powerful hindlimbs","large keeled/modified sternum by species","reduced wings","long neck"]},
    special_organs=["reduced_wings","ostrich_kicking_legs","feathers","air_sacs","avian_lungs","beak","claws"],
    traits={"strength":1.2,"speed":1.8,"endurance":1.5,"durability":1.1,"senses":1.05,"reflexes":1.15}, simulation={"blood_volume_l":6.0},
    thermoregulation="endothermic bird with avian respiratory system",
    system_additions={"locomotor":["ostrich_kicking_legs","reduced_wings"],"integumentary":["feathers"]},
    notes=["Ostriches do not fly; their wings are retained structures with roles in display and balance."])
_stock_variant("hummingbird", "Hummingbird (generalised nectar-feeding bird)", "eagle", clade="bird / apodiform", movement_mode="powered flight / hovering / rapid manoeuvring",
    inherit_special_organs=False, skeleton={"type":"endoskeleton","count":None,"inventory":"hummingbird","regions":["lightened skeleton","specialised shoulder/wing joints","compact hindlimbs","long slender bill"]},
    special_organs=["hummingbird_hover_muscles","elongated_bill","feathers","air_sacs","avian_lungs","long_tongue"],
    traits={"strength":0.12,"speed":1.8,"endurance":1.1,"durability":0.25,"senses":1.2,"reflexes":1.8}, simulation={"blood_volume_l":0.001},
    system_additions={"locomotor":["hummingbird_hover_muscles"],"feeding":["elongated_bill","long_tongue"]},
    notes=["Hovering is declared as a capability; full wingbeat/aerodynamic simulation is not provided by this profile."])
_stock_variant("chameleon", "Chameleon (generalised lizard)", "snake", clade="reptile / squamate / chameleon", movement_mode="arboreal climbing / slow walking / projectile tongue feeding",
    systems_override=_LIZARD_SYSTEMS, inherit_special_organs=False,
    skeleton={"type":"endoskeleton","count":None,"inventory":"chameleon","regions":["grasping feet","curved claws","prehensile tail","mobile skull","limb girdles"]},
    special_organs=["independently_moving_eyes","projectile_tongue","prehensile_tail","zygodactyl_feet","chromatophores","claws","lungs","vomeronasal_organ"],
    traits={"strength":0.45,"speed":0.55,"endurance":0.75,"durability":0.65,"senses":1.5,"reflexes":1.25}, simulation={"blood_volume_l":0.04},
    system_additions={"locomotor":["prehensile_tail","zygodactyl_feet"],"sensory":["independently_moving_eyes"],"feeding":["projectile_tongue"]},
    notes=["Colour change is represented as a specialisation; it is not a universal instantaneous camouflage effect in every species."])
_stock_variant("iguana", "Iguana (generalised lizard)", "chameleon", clade="reptile / squamate / iguanian", movement_mode="terrestrial / climbing / swimming in selected species",
    inherit_special_organs=False, skeleton={"type":"endoskeleton","count":None,"inventory":"iguana","regions":["quadruped limb bones","long tail","dorsal spine structures","robust jaw"]},
    special_organs=["dewlap","iguana_dorsal_spines","salt_gland","claws","tail","lungs","scales"],
    traits={"strength":0.8,"speed":0.95,"endurance":0.9,"durability":0.95,"senses":1.1,"reflexes":1.05}, simulation={"blood_volume_l":0.2})
_stock_variant("sea_turtle", "Sea turtle (generalised marine turtle)", "tortoise", clade="reptile / chelonian / marine", movement_mode="aquatic swimming / diving / nesting on land",
    systems_override={**_TORTOISE_SYSTEMS,"locomotor":["skeleton","joints","skeletal_muscles","turtle_flippers","tail"],"respiratory":["nasal_cavity","pharynx","trachea","lungs"],"integumentary":["skin","scales","carapace","plastron"]}, inherit_special_organs=False,
    skeleton={"type":"endoskeleton","count":None,"inventory":"marine_turtle","regions":["carapace and plastron integrated with axial skeleton","forelimbs modified as flippers","reduced hindlimb mobility for terrestrial movement"]},
    special_organs=["carapace","plastron","turtle_flippers","salt_gland","lungs","cloaca"],
    traits={"strength":1.0,"speed":1.2,"endurance":1.5,"durability":1.5,"senses":1.0,"reflexes":0.8}, simulation={"blood_volume_l":2.0},
    thermoregulation="ectothermic marine reptile; nesting and diving constraints are species-dependent")
_stock_variant("eel", "Eel (generalised bony fish)", "shark", clade="bony fish / anguilliform", movement_mode="aquatic undulation / crevice navigation",
    systems_override=_FISH_SYSTEMS, inherit_special_organs=False,
    skeleton={"type":"endoskeleton","count":None,"inventory":"anguilliform","regions":["elongated vertebral column","continuous dorsal/anal fin margins in many species","reduced pelvic fins or absent fins by lineage"]},
    special_organs=["gills","gill_arches","lateral_line","fins","elongated_body_muscles","mucus_glands"],
    traits={"strength":0.7,"speed":1.2,"endurance":1.1,"durability":0.75,"senses":1.1,"reflexes":1.1}, simulation={"blood_volume_l":0.4},
    respiration={"type":"gill respiration","notes":"Eel breathing varies among species; body skin may contribute but does not replace the gills universally."})
_stock_variant("orca", "Orca (killer whale; toothed cetacean)", "dolphin", clade="mammal / cetacean / odontocete", movement_mode="aquatic swimming / cooperative pursuit / deep diving",
    inherit_special_organs=False, skeleton={"type":"endoskeleton","count":None,"inventory":"odontocete","regions":["large axial skeleton","flippers","tail flukes","large skull and jaw"]},
    special_organs=["echolocation_melon","conical_teeth","dorsal_fin","tail_flukes","blowhole","flippers","blubber"],
    traits={"strength":3.2,"speed":1.6,"endurance":2.0,"durability":2.1,"senses":1.6,"reflexes":1.1}, simulation={"blood_volume_l":500.0},
    system_additions={"sensory":["echolocation_melon"],"locomotor":["dorsal_fin","tail_flukes"],"feeding":["conical_teeth"]},
    notes=["Orcas are toothed whales, not baleen filter feeders; social hunting and acoustic communication are behaviour models, not anatomy alone."])
_stock_variant("manatee", "Manatee (generalised sirenian)", "dolphin", clade="mammal / sirenian / aquatic herbivore", movement_mode="aquatic swimming / slow grazing / surface breathing",
    inherit_special_organs=False, skeleton={"type":"endoskeleton","count":None,"inventory":"sirenian","regions":["dense axial skeleton","forelimb flippers","paddle-shaped tail","specialised ribs"]},
    special_organs=["paddle_tail","bristles","flippers","molars","blowhole_like_nares"],
    traits={"strength":1.3,"speed":0.75,"endurance":1.3,"durability":1.2,"senses":0.9,"reflexes":0.65}, simulation={"blood_volume_l":70.0},
    digestion={"type":"aquatic herbivore","structures":["oral_cavity","molars","esophagus","stomach","intestines","cecum","liver","pancreas"]},
    notes=["Manatee teeth are replaced through a tooth-replacement conveyor; the mechanism is represented as reference-only."])
_stock_variant("snail", "Snail (generalised gastropod mollusc)", "octopus", clade="mollusc / gastropod", movement_mode="crawling / adhesion / shell withdrawal",
    systems_override=_GASTROPOD_SYSTEMS, inherit_special_organs=False,
    skeleton={"type":"custom","count":None,"inventory":"gastropod","regions":["muscular foot","visceral mass","mantle and shell where present","head and tentacles"]},
    special_organs=["radula","muscular_foot","mantle","shell","pneumostome","tentacles","statocysts","mucus_glands"],
    traits={"strength":0.08,"speed":0.08,"endurance":0.7,"durability":0.8,"senses":0.8,"reflexes":0.5,"regeneration":1.0}, simulation={"blood_volume_l":0.005},
    circulation={"type":"open circulation","oxygen_carrier":"hemolymph; details vary across gastropods"},
    respiration={"type":"gills in many aquatic forms; lung-like mantle cavity in pulmonate land snails"},
    notes=["The word snail covers diverse gastropods; shell, gill/lung and reproductive traits require species-specific editing."])
_stock_variant("scorpion", "Scorpion (generalised arachnid)", "spider", clade="arthropod / arachnid / scorpion", movement_mode="terrestrial crawling / burrowing / pincer grasping",
    systems_override=_SCORPION_SYSTEMS, inherit_special_organs=False,
    skeleton={"type":"exoskeleton","count":None,"inventory":"scorpion","regions":["prosoma","segmented mesosoma","metasoma/tail","pedipalps","eight walking legs"]},
    special_organs=["exoskeleton","pedipalps","pectines","venom_telson","book_lungs","hemolymph","simple_eyes","malpighian_tubules"],
    traits={"strength":0.5,"speed":0.65,"endurance":0.9,"durability":0.8,"senses":1.4,"reflexes":1.2}, simulation={"blood_volume_l":0.0004},
    notes=["Venom potency and sting mechanics are species-specific. The template does not make an abstract venom label an automatic damage engine."])
_stock_variant("butterfly", "Butterfly (generalised lepidopteran insect)", "bee", clade="arthropod / insect / lepidopteran", movement_mode="powered flight / perching / nectar feeding",
    systems_override=_INSECT_SYSTEMS, inherit_special_organs=False,
    skeleton={"type":"exoskeleton","count":None,"inventory":"lepidopteran","regions":["head","thorax","abdomen","two pairs of scaled wings","six legs"]},
    special_organs=["exoskeleton","compound_eyes","antennae","proboscis","wingscales","six_legs","spiracles","tracheae"],
    traits={"strength":0.02,"speed":0.8,"endurance":0.7,"durability":0.12,"senses":1.2,"reflexes":1.3}, simulation={"blood_volume_l":0.000005},
    system_additions={"locomotor":["six_legs"],"feeding":["proboscis"],"integumentary":["wingscales"]},
    system_removals={"defence":["sting","glandular_venom_reservoir"]},
    notes=["Metamorphosis requires separate life-stage profiles; this adult body template does not simulate the caterpillar/pupa transition."])
_stock_variant("leech", "Leech (generalised annelid)", "earthworm", clade="annelid / hirudinean", movement_mode="looping / crawling / aquatic swimming in selected species",
    inherit_special_organs=False, skeleton={"type":"hydrostatic","count":0,"inventory":"hirudinean","regions":["segmented hydrostatic body","anterior sucker","posterior sucker","coelom modified by lineage"]},
    special_organs=["hydrostatic_skeleton","skin_cuticle","cerebral_ganglia","ventral_nerve_cord","nephridia","anterior_sucker","posterior_sucker","hirudin_glands"],
    traits={"strength":0.2,"speed":0.2,"endurance":0.8,"durability":0.25,"senses":0.8,"reflexes":0.8,"regeneration":1.2}, simulation={"blood_volume_l":0.001},
    notes=["Some leeches feed on blood and others do not; feeding type and secretions should be explicit species settings."])
_stock_variant("jellyfish", "Jellyfish (generalised medusa)", "freshwater_hydra", clade="cnidarian / medusozoan", movement_mode="pulsed swimming / drifting",
    systems_override=_JELLYFISH_SYSTEMS, inherit_special_organs=False,
    skeleton={"type":"hydrostatic","count":0,"inventory":"medusa","regions":["contractile bell","radial symmetry","tentacles","gastrovascular cavity"]},
    special_organs=["jellyfish_bell","rhopalia","bell_margin_sensors","tentacles","nerve_net","nematocysts","gastrovascular_cavity"],
    traits={"strength":0.05,"speed":0.35,"endurance":0.5,"durability":0.1,"senses":0.5,"reflexes":0.4,"regeneration":1.3}, simulation={"blood_volume_l":0.0},
    notes=["Cnidarians have a nerve net and lack a vertebrate brain or heart. Some jellyfish are tiny and some are large; values are illustrative only."])
_stock_variant("sea_star", "Sea star (starfish; generalised echinoderm)", "earthworm", clade="echinoderm / asteroid", movement_mode="slow crawling / adhesion / arm regeneration",
    systems_override=_SEA_STAR_SYSTEMS, inherit_special_organs=False,
    skeleton={"type":"custom","count":None,"inventory":"asteroid","regions":["radial ossicles","arms","tube feet","water vascular system","madreporite"]},
    special_organs=["ossicles","radial_ossicles","tube_feet","water_vascular_system","madreporite","radial_nerve","pyloric_caeca","pedicellariae","regenerative_limb_bud"],
    traits={"strength":0.15,"speed":0.05,"endurance":0.8,"durability":0.7,"senses":0.4,"reflexes":0.2,"regeneration":1.7}, simulation={"blood_volume_l":0.0},
    notes=["Echinoderm water-vascular mechanics and regeneration are reference capabilities rather than full hydraulic solvers."])
_stock_variant("millipede", "Millipede (generalised myriapod)", "ant", clade="arthropod / myriapod / diplopod", movement_mode="many-legged crawling / burrowing",
    systems_override=_MYRIAPOD_SYSTEMS, inherit_special_organs=False,
    skeleton={"type":"exoskeleton","count":None,"inventory":"diplopod","regions":["head","many trunk rings","paired legs on most diplosegments","body wall and defensive glands"]},
    special_organs=["exoskeleton","diplosomites","walking_legs","spiracles","tracheae","defensive_glands","mandibles","hemolymph"],
    traits={"strength":0.08,"speed":0.3,"endurance":0.8,"durability":0.35,"senses":0.7,"reflexes":0.5}, simulation={"blood_volume_l":0.0001},
    notes=["Segment and leg counts vary widely across millipedes; this template deliberately does not hard-code a universal count."])
_stock_variant("beetle", "Beetle (generalised coleopteran insect)", "bee", clade="arthropod / insect / coleopteran", movement_mode="walking / burrowing / flight where capable",
    systems_override=_INSECT_SYSTEMS, inherit_special_organs=False,
    skeleton={"type":"exoskeleton","count":None,"inventory":"coleopteran","regions":["head","thorax","abdomen","six legs","hardened elytra covering hindwings where present"]},
    special_organs=["exoskeleton","elytra","compound_eyes","antennae","mandibles","tarsi","six_legs","spiracles","tracheae","hemolymph"],
    traits={"strength":0.08,"speed":0.7,"endurance":0.85,"durability":0.45,"senses":0.9,"reflexes":0.9}, simulation={"blood_volume_l":0.00001},
    system_additions={"integumentary":["elytra"],"locomotor":["tarsi","six_legs"]},
    notes=["Flight, horn-like structures and digging adaptations differ across beetle groups; use a custom derivative for a specific family."])

# Composite reference templates are conveniences, not closed chimera recipes. The
# same composition capability is available to users through anatomy.define_species().
_stock_composite("centaur", "Centaur (editable human-equine hybrid)", ["horse", "human"], primary="horse",
    movement_mode="equine lower body with humanoid torso", movement_capabilities=["walk", "run", "jump", "gallop", "carry"])
_stock_composite("merfolk", "Merfolk (editable aquatic humanoid hybrid)", ["human", "dolphin"], primary="human",
    movement_mode="aquatic humanoid / swimming", movement_capabilities=["swim", "dive", "surface_breathe", "use_arms"],
    remove_organs=["femur", "tibia", "fibula", "patella", "tarsals", "metatarsals", "ankle_bones", "foot_bones", "lower_limb_bones"])
_stock_composite("minotaur", "Minotaur (editable bull-humanoid hybrid)", ["cow", "human"], primary="human",
    movement_mode="powerful bipedal / quadrupedal capable humanoid", movement_capabilities=["walk", "run", "jump", "charge", "carry"],
    traits={"strength": 2.2, "durability": 1.5}, notes=["The designer must choose whether ruminant digestive structures remain present in this humanoid hybrid."])
_stock_composite("hydra", "Hydra (multi-headed regenerative dragon-like template)", ["dragon", "crocodile"], primary="dragon",
    movement_mode="heavy quadrupedal / aquatic-capable", movement_capabilities=["walk", "run", "swim", "bite_multiple_targets"],
    traits={"strength": 3.2, "durability": 2.8, "regeneration": 2.5}, notes=["Multiple heads and regrowth structures are fictional traits; neck coordination and regenerative rules must be implemented explicitly."])
_stock_composite("phoenix", "Phoenix (fictional regenerative firebird)", ["eagle"], primary="eagle",
    movement_mode="powered flight / magical reconstitution", movement_capabilities=["fly", "glide", "dive", "reconstitute_from_ash"], skeleton_type="custom",
    traits={"speed": 1.8, "regeneration": 3.0, "recovery": 2.5, "durability": 1.5}, notes=["Pyrogenic and ash-reconstitution structures are fictional, and their behaviour must be defined as explicit mechanisms rather than assumed from the template."])

# Dinosaur body plans use clade-specific structural references and explicitly
# approximate gameplay priors. These profiles are not claims of complete fossil
# reconstruction or full locomotion simulation.
_DINOSAUR_SYSTEMS = {k: list(v) for k, v in REPTILE_SYSTEM_ORGANS.items()}
_DINOSAUR_SYSTEMS["integumentary"] = ["skin", "epidermis", "dermis", "scales", "feathers", "cutaneous_glands"]
_DINOSAUR_SYSTEMS["skeletal"] = ["skeleton", "skull", "vertebral_column", "ribs", "sternum", "pelvic_girdle", "forelimb_bones", "hindlimb_bones", "tail", "joints", "cartilage", "ligaments", "tendons", "bone_marrow"]
_DINOSAUR_SYSTEMS["muscular"] = ["muscle_tissue", "skeletal_muscles", "jaw_muscles", "neck_muscles", "tail_muscles", "hindlimb_muscles", "heart"]
_DINOSAUR_SYSTEMS["respiratory"] = ["nasal_cavity", "pharynx", "trachea", "lungs", "air_sacs", "airway_mucosa"]
_DINOSAUR_SYSTEMS["digestive"] = ["oral_cavity", "teeth", "beak", "esophagus", "stomach", "small_intestine", "colon", "liver", "pancreas", "microbiome"]
_DINOSAUR_SYSTEMS["locomotor"] = ["skeleton", "joints", "cartilage", "ligaments", "tendons", "skeletal_muscles", "forelimb_bones", "hindlimb_bones", "tail", "feet", "claws"]

_stock_variant("tyrannosaurus", "Tyrannosaurus rex (dinosaur reference template)", "crocodile",
    clade="dinosaur / theropod / tyrannosaurid", systems_override=_DINOSAUR_SYSTEMS, inherit_special_organs=False,
    skeleton={"type":"endoskeleton", "count":None, "inventory":"large_theropod", "regions":["large skull", "short forelimbs", "powerful hindlimbs", "long balancing tail", "pneumatic vertebrae (model assumption)"]},
    movement_mode="large bipedal terrestrial predator",
    special_organs=["large_predatory_teeth", "deep_skull", "jaw_muscles", "two_digit_forelimbs", "tail_muscles", "large_theropod_pelvis", "pneumatic_bones"],
    traits={"strength":3.4,"speed":1.1,"endurance":1.0,"durability":2.5,"senses":1.4,"reflexes":1.1},
    simulation={"blood_volume_l":250.0}, classification="real-species-template",
    notes=["Body mass, soft tissue and movement numbers are game estimates; detailed gait and predator behaviour are not fully simulated."])
_stock_variant("triceratops", "Triceratops (ceratopsian dinosaur template)", "rhinoceros",
    clade="dinosaur / ornithischian / ceratopsian", systems_override=_DINOSAUR_SYSTEMS, inherit_special_organs=False,
    skeleton={"type":"endoskeleton", "count":None, "inventory":"ceratopsian", "regions":["quadrupedal limbs", "large frill", "three facial horns", "beaked skull", "short tail"]},
    movement_mode="heavy quadrupedal terrestrial herbivore",
    special_organs=["bony_frill", "nasal_horn", "brow_horns", "keratin_beak", "herbivore_teeth", "columnar_limbs"],
    traits={"strength":2.7,"speed":0.9,"endurance":1.2,"durability":2.8,"senses":1.0,"reflexes":0.9},
    simulation={"blood_volume_l":300.0}, classification="real-species-template",
    notes=["Frill and horn coverings include soft-tissue/keratin assumptions; numerical traits are gameplay priors."])
_stock_variant("velociraptor", "Velociraptor (small feathered dromaeosaur template)", "ostrich",
    clade="dinosaur / theropod / dromaeosaurid", systems_override=_DINOSAUR_SYSTEMS, inherit_special_organs=False,
    skeleton={"type":"endoskeleton", "count":None, "inventory":"small_theropod", "regions":["light bipedal skeleton", "long balancing tail", "grasping forelimbs", "enlarged second-toe claw"]},
    movement_mode="small feathered bipedal cursorial hunter",
    special_organs=["feathers", "flight_feathers", "sickle_claw", "grasping_forelimbs", "tail_stiffening_tendons", "hunting_teeth"],
    traits={"strength":0.75,"speed":1.45,"endurance":1.25,"durability":0.75,"senses":1.35,"reflexes":1.5},
    simulation={"blood_volume_l":0.5}, classification="real-species-template",
    notes=["This profile represents a dromaeosaur with plumage; popular movie-scale proportions are not treated as fossil evidence."])
_stock_variant("stegosaurus", "Stegosaurus (armoured herbivore dinosaur template)", "tortoise",
    clade="dinosaur / ornithischian / stegosaurian", systems_override=_DINOSAUR_SYSTEMS, inherit_special_organs=False,
    skeleton={"type":"endoskeleton", "count":None, "inventory":"stegosaurian", "regions":["quadrupedal limbs", "dorsal plates", "tail spikes", "small skull", "heavy trunk"]},
    movement_mode="slow heavy quadrupedal terrestrial herbivore",
    special_organs=["dorsal_plates", "tail_spikes", "small_herbivore_skull", "columnar_limbs", "herbivore_teeth"],
    traits={"strength":2.0,"speed":0.75,"endurance":1.0,"durability":2.4,"senses":0.9,"reflexes":0.75},
    simulation={"blood_volume_l":120.0}, classification="real-species-template",
    notes=["Dorsal plates and tail spikes are structural references; thermoregulatory or defensive functions are not assumed by the model."])
_stock_variant("brachiosaurus", "Brachiosaurus (sauropod dinosaur template)", "giraffe",
    clade="dinosaur / sauropod / brachiosaurid", systems_override=_DINOSAUR_SYSTEMS, inherit_special_organs=False,
    skeleton={"type":"endoskeleton", "count":None, "inventory":"sauropod", "regions":["very long neck", "large trunk", "columnar limbs", "long balancing tail", "pneumatic vertebrae (model assumption)"]},
    movement_mode="very large slow quadrupedal terrestrial herbivore",
    special_organs=["elongated_neck", "cervical_vertebrae", "columnar_limbs", "long_tail", "pneumatic_bones", "air_sacs", "herbivore_teeth"],
    traits={"strength":4.0,"speed":0.55,"endurance":1.0,"durability":3.5,"senses":0.9,"reflexes":0.5},
    simulation={"blood_volume_l":9000.0}, classification="real-species-template",
    notes=["Scale, mass, neck posture and soft tissues are approximate game choices, not a validated biomechanical reconstruction."])
_stock_variant("ankylosaurus", "Ankylosaurus (armoured dinosaur template)", "tortoise",
    clade="dinosaur / ankylosaurian / ankylosaurid", systems_override=_DINOSAUR_SYSTEMS, inherit_special_organs=False,
    skeleton={"type":"endoskeleton", "count":None, "inventory":"ankylosaur", "regions":["low quadrupedal body", "dermal armour", "reinforced skull", "tail club", "short robust limbs"]},
    movement_mode="low heavy quadrupedal terrestrial herbivore",
    special_organs=["osteoderms", "tail_club", "reinforced_skull", "columnar_limbs", "herbivore_teeth"],
    traits={"strength":2.3,"speed":0.7,"endurance":1.1,"durability":3.2,"senses":0.9,"reflexes":0.7},
    simulation={"blood_volume_l":500.0}, classification="real-species-template",
    notes=["Osteoderm arrangement and the tail club are represented as structures; damage geometry is not individually simulated."])

# Additional prehistoric templates. These are reference body plans with bounded
# trait priors, not claims of complete paleobiomechanical simulation.
_stock_variant("spinosaurus", "Spinosaurus (semi-aquatic theropod template)", "crocodile",
    clade="dinosaur / theropod / spinosaurid", systems_override=_DINOSAUR_SYSTEMS, inherit_special_organs=False,
    skeleton={"type":"endoskeleton", "count":None, "inventory":"spinosaurid", "regions":["elongated skull", "long trunk", "dorsal neural spines", "robust hindlimbs", "long tail"]},
    movement_mode="large terrestrial / semi-aquatic wading and swimming",
    special_organs=["spinosaur_sail", "elongated_crocodilian_snout", "conical_fish_gripping_teeth", "long_tail", "hindlimb_muscles", "air_sacs"],
    traits={"strength":3.5,"speed":0.75,"endurance":1.0,"durability":2.5,"senses":1.2,"reflexes":0.7},
    simulation={"blood_volume_l":850.0}, classification="real-species-template",
    notes=["Body proportions and aquatic ecology remain debated; this is a configurable game template, not a definitive reconstruction."])
_stock_variant("diplodocus", "Diplodocus (long-tailed sauropod template)", "brachiosaurus",
    clade="dinosaur / sauropod / diplodocid", systems_override=_DINOSAUR_SYSTEMS, inherit_special_organs=False,
    skeleton={"type":"endoskeleton", "count":None, "inventory":"diplodocid", "regions":["elongated neck", "long trunk", "very long whip-like tail", "columnar limbs", "pneumatic vertebral regions"]},
    movement_mode="very large slow quadrupedal terrestrial herbivore",
    special_organs=["diplodocid_whiplash_tail", "diplodocid_neck_support", "pneumatic_bones", "air_sacs", "herbivore_teeth"],
    traits={"strength":3.8,"speed":0.45,"endurance":1.0,"durability":3.0,"senses":0.9,"reflexes":0.45},
    simulation={"blood_volume_l":6500.0}, classification="real-species-template",
    notes=["Scale values are conservative game estimates; tail and neck motion are not articulated simulations."])
_stock_variant("parasaurolophus", "Parasaurolophus (crested herbivorous dinosaur template)", "ostrich",
    clade="dinosaur / ornithischian / hadrosaurid", systems_override=_DINOSAUR_SYSTEMS, inherit_special_organs=False,
    skeleton={"type":"endoskeleton", "count":None, "inventory":"hadrosaurid", "regions":["duck-billed skull", "cranial crest", "broad trunk", "hindlimbs", "forelimbs", "tail"]},
    movement_mode="bipedal or quadrupedal terrestrial running",
    special_organs=["parasaurolophus_cranial_crest", "beak", "herbivore_teeth", "tail", "air_sacs"],
    traits={"strength":1.8,"speed":1.4,"endurance":1.2,"durability":1.6,"senses":1.0,"reflexes":1.1},
    simulation={"blood_volume_l":500.0}, classification="real-species-template",
    notes=["Crest acoustics are uncertain; this template makes no automatic sound-generation claim."])
_stock_variant("pachycephalosaurus", "Pachycephalosaurus (dome-headed dinosaur template)", "ostrich",
    clade="dinosaur / ornithischian / pachycephalosaurid", systems_override=_DINOSAUR_SYSTEMS, inherit_special_organs=False,
    skeleton={"type":"endoskeleton", "count":None, "inventory":"pachycephalosaurid", "regions":["domed skull roof", "bipedal hindlimbs", "small forelimbs", "balancing tail"]},
    movement_mode="bipedal terrestrial running",
    special_organs=["pachycephalosaur_dome", "pachycephalosaur_reinforced_skull", "tail", "hindlimb_muscles", "herbivore_teeth"],
    traits={"strength":1.5,"speed":1.35,"endurance":1.1,"durability":1.5,"senses":0.95,"reflexes":1.0},
    simulation={"blood_volume_l":80.0}, classification="real-species-template",
    notes=["The role of head-to-head impact is uncertain; a reinforced dome does not automatically imply safe ramming mechanics."])
_PTEROSAUR_SYSTEMS = {k: list(v) for k, v in _DINOSAUR_SYSTEMS.items()}
_PTEROSAUR_SYSTEMS["locomotor"] = ["skeleton", "joints", "cartilage", "ligaments", "tendons", "skeletal_muscles", "pterosaur_wing_membrane", "pterosaur_wing_finger", "wings", "feet", "claws"]
_PTEROSAUR_SYSTEMS["skeletal"] = list(dict.fromkeys(_PTEROSAUR_SYSTEMS.get("skeletal", []) + ["pterosaur_wing_finger", "pterosaur_pneumatic_bones"]))
_stock_variant("pteranodon", "Pteranodon (pterosaur flight template; not a dinosaur)", "eagle",
    clade="archosaur / pterosaur / pterodactyloid", systems_override=_PTEROSAUR_SYSTEMS, inherit_special_organs=False,
    skeleton={"type":"endoskeleton", "count":None, "inventory":"pterosaur", "regions":["elongated fourth wing finger", "wing membrane", "lightweight trunk", "elongated skull crest", "hindlimbs"]},
    movement_mode="powered flight / soaring / terrestrial quadrupedal launch (modelled abstractly)",
    special_organs=["pterosaur_wing_finger", "pterosaur_wing_membrane", "pterosaur_pneumatic_bones", "flight_muscles", "wings", "crest"],
    traits={"strength":1.7,"speed":1.7,"endurance":1.3,"durability":1.0,"senses":1.0,"reflexes":1.3},
    simulation={"blood_volume_l":22.0}, classification="real-species-template",
    notes=["Pterosaurs are flying reptiles, not dinosaurs. Launch biomechanics and the flight model are simplified."])
_MARINE_REPTILE_SYSTEMS = {k: list(v) for k, v in _CROCODILIAN_SYSTEMS.items()}
_MARINE_REPTILE_SYSTEMS["locomotor"] = ["skeleton", "joints", "cartilage", "ligaments", "tendons", "skeletal_muscles", "mosasaur_flippers", "mosasaur_paddle_tail", "tail"]
_stock_variant("mosasaurus", "Mosasaurus (marine mosasaur template)", "crocodile",
    clade="reptile / squamate / mosasaur", systems_override=_MARINE_REPTILE_SYSTEMS, inherit_special_organs=False,
    skeleton={"type":"endoskeleton", "count":None, "inventory":"mosasaur", "regions":["elongated aquatic trunk", "paddle-like limbs", "powerful tail", "long skull", "rib cage"]},
    movement_mode="large aquatic swimming / tail propulsion",
    special_organs=["mosasaur_flippers", "mosasaur_paddle_tail", "mosasaur_conical_teeth", "salt_glands", "conical_teeth"],
    traits={"strength":3.0,"speed":1.4,"endurance":1.0,"durability":2.0,"senses":1.15,"reflexes":1.0},
    simulation={"blood_volume_l":900.0}, classification="real-species-template",
    notes=["Marine reptile; aquatic propulsion is approximated and not a fluid-dynamics simulation."])

# Distinct dragon body plans: western quadruped-with-wings vs eastern serpentine
# dragon with optional magical flight. The generic `dragon` remains compatible.
_stock_variant("western_dragon", "Western Dragon (four-legged, winged fantasy template)", "dragon",
    clade="fictional dragon / western hexapod", inherit_special_organs=False,
    skeleton={"type":"hybrid", "count":None, "inventory":"western_dragon", "regions":["four weight-bearing limbs", "paired wings", "long tail", "large skull", "rib cage", "reinforced shoulder girdle"]},
    movement_mode="heavy quadrupedal / wing-powered flight",
    special_organs=["wings", "wing_membrane", "flight_muscles", "bird_keel", "air_sacs", "fire_resistant_mucosa", "pyrogenic_sac", "horns", "claws", "tail", "dragon_scales"],
    traits={"strength":3.4,"speed":1.3,"endurance":1.4,"durability":2.8,"senses":1.4,"reflexes":1.2,"regeneration":1.2},
    simulation={"blood_volume_l":250.0}, classification="fictional-design-proposal",
    notes=["Six-limbed vertebrate-like anatomy is deliberately fictional; choose wing attachment, respiratory integration and flight physics explicitly."])
_stock_variant("eastern_dragon", "Eastern Dragon / Long (serpentine fantasy template)", "snake",
    clade="fictional dragon / serpentine long", inherit_special_organs=False,
    skeleton={"type":"hybrid", "count":None, "inventory":"eastern_dragon", "regions":["elongated flexible trunk", "many vertebrae", "four short limbs where selected", "long tail", "antler-like horns", "whiskers"]},
    movement_mode="serpentine swimming / coiling / magical flight",
    special_organs=["serpentine_body", "elongated_vertebral_column", "four_short_limbs", "antler_horns", "dragon_whiskers", "mane", "cloud_sail", "aetheric_core", "water_sensing_barbels", "dragon_scales"],
    traits={"strength":2.8,"speed":1.5,"endurance":1.8,"durability":2.2,"senses":1.8,"reflexes":1.5,"regeneration":1.1},
    simulation={"blood_volume_l":120.0}, classification="fictional-design-proposal",
    notes=["Flight is a fictional capability and does not imply anatomical wings; use a magical propulsion rule or remove flight from a custom derivative.", "Horn, whisker, mane and limb arrangement vary across East Asian dragon traditions; this is an editable archetype, not a universal depiction."])

# Ant caste profiles remain individual arthropod bodies; social organisation and
# pheromone networks are a separate colony-level model, not silently simulated.
_stock_variant("ant_worker", "Worker Ant (caste template)", "ant", clade="arthropod / insect / ant / worker caste",
    skeleton={"type":"exoskeleton", "count":None, "inventory":"worker_ant", "regions":["head", "thorax", "petiole", "abdomen", "six legs", "antennae"]},
    movement_mode="walking / climbing / carrying", special_organs=["mandibles", "antennae", "chemical_sensilla", "crop_social_stomach", "worker_foregut"],
    traits={"strength":0.035,"speed":0.7,"endurance":1.5,"durability":0.28,"senses":1.6,"reflexes":1.4}, simulation={"blood_volume_l":0.00001},
    classification="role-variant-template", notes=["Worker caste phenotype varies by species; this is not an individual ant species diagnosis."])
_stock_variant("ant_soldier", "Soldier Ant (caste template)", "ant", clade="arthropod / insect / ant / soldier caste",
    skeleton={"type":"exoskeleton", "count":None, "inventory":"soldier_ant", "regions":["reinforced head", "thorax", "petiole", "abdomen", "six legs", "antennae"]},
    movement_mode="terrestrial walking / defensive guarding", special_organs=["enlarged_mandibles", "reinforced_head_capsule", "chemical_sensilla", "defensive_glands", "six_legs"],
    traits={"strength":0.055,"speed":0.55,"endurance":1.15,"durability":0.4,"senses":1.4,"reflexes":1.1}, simulation={"blood_volume_l":0.00002},
    classification="role-variant-template", notes=["Large-headed and soldier forms occur in selected ant lineages; not every colony has a distinct soldier caste."])
_stock_variant("ant_queen", "Queen Ant (reproductive caste template)", "ant", clade="arthropod / insect / ant / queen caste",
    skeleton={"type":"exoskeleton", "count":None, "inventory":"queen_ant", "regions":["head", "thorax with flight-muscle history in winged queens", "enlarged abdomen", "petiole", "six legs", "antennae"]},
    movement_mode="walking / digging / winged dispersal in reproductive phase", special_organs=["developed_ovaries", "spermatheca", "enlarged_gaster", "flight_muscles_optional", "wing_scar_optional"],
    traits={"strength":0.045,"speed":0.35,"endurance":1.0,"durability":0.35,"senses":1.3,"reflexes":0.8}, simulation={"blood_volume_l":0.00004},
    classification="role-variant-template", notes=["Queen size, wing status, colony founding and reproductive strategy depend on species and life stage."])

_SLIME_SYSTEMS = {
    "integumentary": ["gel_membrane", "surface_mucus", "selective_gel_barrier"],
    "skeletal": ["gel_matrix", "hydrostatic_support", "shape_memory_matrix"],
    "muscular": ["contractile_gel_fibres", "cytoskeletal_network"],
    "nervous": ["distributed_sensory_network", "signal_conduction_filaments"],
    "sensory": ["sensory_pits", "chemoreceptors", "pressure_sensors", "light_sensitive_cells"],
    "digestive": ["nutrient_absorption_surface", "digestive_vacuoles", "gastrogel_cavity", "extracellular_enzyme_glands"],
    "metabolic": ["nutrient_reservoir", "enzyme_network", "cellular_energy_matrix"],
    "renal": ["contractile_vacuoles", "osmotic_membrane"],
    "locomotor": ["pseudopods", "gel_propulsion_bands", "adhesive_foot"],
    "developmental": ["regenerative_core", "fission_buds", "fragment_repair_nodes"],
    "defence": ["acid_secretion_glands", "toxin_secretion_sacs", "irritant_surface_mucus"],
    "magical_specialisation": ["aetheric_core", "shape_memory_matrix", "elemental_adaptation_nodule"],
}
_stock_variant("slime", "Slime (fictional amorphous organism template)", "freshwater_hydra",
    clade="fictional organism / amorphous gel-bodied", systems_override=_SLIME_SYSTEMS, inherit_special_organs=False,
    skeleton={"type":"hydrostatic", "count":None, "inventory":"amorphous_gel", "regions":["gel membrane", "distributed internal matrix", "contractile regions", "pseudopods", "optional central core"]},
    movement_mode="amoeboid crawling / flowing / squeezing through gaps",
    special_organs=["gel_membrane", "surface_mucus", "gel_matrix", "hydrostatic_support", "shape_memory_matrix", "contractile_gel_fibres", "cytoskeletal_network", "distributed_sensory_network", "signal_conduction_filaments", "sensory_pits", "chemoreceptors", "pressure_sensors", "light_sensitive_cells", "nutrient_absorption_surface", "digestive_vacuoles", "gastrogel_cavity", "extracellular_enzyme_glands", "nutrient_reservoir", "enzyme_network", "cellular_energy_matrix", "contractile_vacuoles", "osmotic_membrane", "pseudopods", "gel_propulsion_bands", "adhesive_foot", "regenerative_core", "fission_buds", "fragment_repair_nodes", "acid_secretion_glands", "toxin_secretion_sacs", "irritant_surface_mucus", "aetheric_core"],
    traits={"strength":0.4,"speed":0.45,"endurance":1.4,"durability":0.65,"senses":0.7,"reflexes":0.35,"regeneration":1.8,"recovery":1.5},
    simulation={"blood_volume_l":0.0}, circulation={"type":"distributed diffusion / internal fluid movement", "notes":"No vertebrate heart or blood is assumed; transport rules are a fictional simplified body-plan choice."},
    respiration={"type":"surface diffusion / magical exchange where configured", "notes":"No lungs are assumed. Gas exchange is a design-level approximation."},
    digestion={"type":"external digestion and absorptive gel", "notes":"Nutrient processing is fictional and not a biochemical solver."},
    classification="fictional-design-proposal",
    notes=["No brain, heart, bones or mammalian organs are required by this template. Its behaviour is amorphous and distributed; individual gel rheology and fission dynamics need explicit mechanics."])

# Refine the existing minotaur rather than introducing a duplicate entry.
SPECIES["minotaur"]["label"] = "Minotaur (bull-humanoid chimera template)"
SPECIES["minotaur"]["special_organs"] = list(dict.fromkeys(SPECIES["minotaur"].get("special_organs", []) + ["horns", "bovine_muzzle", "cloven_hooves", "reinforced_cervical_muscles", "humanoid_hands", "bovine_tail"]))
SPECIES["minotaur"]["notes"] = list(SPECIES["minotaur"].get("notes", [])) + ["Select one integrated locomotor plan and explicitly decide whether ruminant digestive compartments remain or are replaced by a humanoid-compatible tract."]
SPECIES["ant"]["notes"] = list(SPECIES["ant"].get("notes", [])) + ["Ant caste and colony metadata are separate from the individual ant body template."]

for _dino_key, _caps in {
    "tyrannosaurus": ["walk", "run", "bite", "balance_tail"],
    "triceratops": ["walk", "run", "charge", "brace"],
    "velociraptor": ["walk", "run", "jump", "climb", "grasp"],
    "stegosaurus": ["walk", "brace", "tail_strike"],
    "brachiosaurus": ["walk", "reach_high", "brace"],
    "ankylosaurus": ["walk", "brace", "tail_strike"],
}.items():
    SPECIES[_dino_key]["movement_capabilities"] = _caps

SPECIES["phoenix"]["special_organs"] = list(dict.fromkeys(SPECIES["phoenix"].get("special_organs", []) + ["pyrogenic_sac", "ash_reconstitution_core", "fire_resistant_mucosa", "aetheric_core"]))
SPECIES["hydra"]["special_organs"] = list(dict.fromkeys(SPECIES["hydra"].get("special_organs", []) + ["multiple_necks", "regenerative_buds", "glandular_venom_reservoir"]))
SPECIES["dragon"]["special_organs"] = list(dict.fromkeys(SPECIES["dragon"].get("special_organs", []) + ["fire_resistant_mucosa", "pyrogenic_sac"]))
SPECIES["griffin"]["special_organs"] = list(dict.fromkeys(SPECIES["griffin"].get("special_organs", []) + ["wing_membrane", "bird_keel", "air_sacs"]))

# Add species-specific organs that are not in the shared clade list.
SPECIES["lion"]["special_organs"] = sorted((set(SPECIES["lion"].get("special_organs", [])) - {"tusks"}) | {"vibrissae", "claws", "tail", "teeth"})
SPECIES["tiger"]["special_organs"] = sorted((set(SPECIES["tiger"].get("special_organs", [])) - {"tusks"}) | {"vibrissae", "claws", "tail", "teeth"})
SPECIES["cow"]["special_organs"] = sorted((set(SPECIES["cow"].get("special_organs", [])) - {"tusks"}) | {"rumen", "reticulum", "omasum", "abomasum", "ruminant_microbiome"})
SPECIES["giraffe"]["special_organs"] = sorted(set(SPECIES["giraffe"].get("special_organs", [])) | {"rumen", "reticulum", "omasum", "abomasum", "ruminant_microbiome", "ossicones"})

# Select organ sets for every profile and merge only the proper clade-specific parts.
for _key, _profile in SPECIES.items():
    systems_map = _profile["systems"]
    if _key == "snake":
        systems_map = dict(systems_map)
        # Snakes lack a true diaphragm; the broad reptile map shares mammal organs as an index.
        systems_map["respiratory"] = [x for x in systems_map["respiratory"] if x != "diaphragm"]
        systems_map["digestive"] = [x for x in systems_map["digestive"] if x not in {"gallbladder"}] + ["cloaca", "serpentine_lung", "vomeronasal_organ"]
    if _key == "earthworm":
        systems_map = dict(systems_map)
        # Ensure there are no mammalian-only structures in the worm's active record.
        systems_map["skeletal"] = ["hydrostatic_skeleton", "coelom", "earthworm_segment", "connective_tissue"]
        systems_map["circulatory"] = ["blood", "aortic_arches", "arteries", "veins", "capillaries"]
        systems_map["respiratory"] = ["skin_cuticle"]
        systems_map["digestive"] = ["oral_cavity", "pharynx", "esophagus", "crop", "gizzard", "small_intestine", "intestines", "rectum"]
        systems_map["renal"] = ["nephridia"]
        systems_map["nervous"] = ["cerebral_ganglia", "ventral_nerve_cord", "peripheral_nerves"]
        systems_map["reproductive"] = ["gonads", "reproductive_tract", "clitellum", "seminal_vesicles"]
    organs = []
    for names in systems_map.values():
        for name in names:
            if name not in organs:
                organs.append(name)
    for name in _profile.get("special_organs", []):
        if name not in organs:
            organs.append(name)
    _profile["organ_names"] = organs
    _profile["systems"] = {sys: [name for name in names if name in organs] for sys, names in systems_map.items() if any(name in organs for name in names)}
    _profile.setdefault("bones", {"type": _profile.get("skeleton", {}).get("type", "unknown"), "inventory": _profile.get("skeleton", {}).get("inventory", "species_specific"), "regions": list(_profile.get("skeleton", {}).get("regions", [])), "count": _profile.get("skeleton", {}).get("count")})
    _profile.setdefault("special_organs", [])
    _profile.setdefault("notes", [])

# Add human-only reference structures after each profile's shared/clade organ map
# has been consolidated. Human has deeper addressability without leaking those
# structures into other mammals. The shared 1024 per-entity structure cap remains.
_human_systems = SPECIES["human"]["systems"]
for _name, _system, _role in _HUMAN_DETAIL_STRUCTURES:
    if _name not in SPECIES["human"]["organ_names"]:
        SPECIES["human"]["organ_names"].append(_name)
    _members = _human_systems.setdefault(_system, [])
    if _name not in _members:
        _members.append(_name)
SPECIES["human"]["systems"] = {k: list(dict.fromkeys(v)) for k, v in _human_systems.items()}
SPECIES["human"]["human_detail_version"] = 4
SPECIES["human"]["notes"] = list(SPECIES["human"].get("notes", [])) + [
    "Expanded human profile includes regional organ systems, brain subdivisions, neurovascular pathways, joint and tendon interfaces, renal/pulmonary/digestive microanatomy, endocrine regions, immune compartments and reproductive structures.",
    "Anatomy detail version 4 provides an expanded addressable reference map; structure inclusion does not imply continuous simulation for every entry.",
    "Catalogue presence is not proof of a dedicated dynamic solver for every structure; physiology only updates structures covered by implemented state hooks."]

SPECIES["western_dragon"]["special_organs"] = list(dict.fromkeys(SPECIES["western_dragon"].get("special_organs", []) + ["fire_resistant_mucosa", "pyrogenic_sac", "wing_membrane", "flight_muscles", "dragon_scales"]))
SPECIES["eastern_dragon"]["special_organs"] = list(dict.fromkeys(SPECIES["eastern_dragon"].get("special_organs", []) + ["antler_horns", "dragon_whiskers", "cloud_sail", "aetheric_core", "dragon_scales"]))

# Consolidate late-added dragon structures into the addressable body/system maps.
# This fixes earlier catalogue ordering where a special-organ addition could be
# inspectable by name but absent from organ_names and therefore absent from audits.
DRAGON_PROFILE_CONSOLIDATION = {
    "western_dragon": {
        "integumentary": ["dragon_scales", "dragon_scale_bed"],
        "locomotor": ["wing_membrane", "wings"],
        "muscular": ["flight_muscles"],
        "magical_specialisation": ["fire_resistant_mucosa", "pyrogenic_sac"],
    },
    "eastern_dragon": {
        "integumentary": ["dragon_scales", "dragon_scale_bed"],
        "sensory": ["dragon_whiskers", "water_sensing_barbels"],
        "magical_specialisation": ["antler_horns", "cloud_sail", "aetheric_core"],
    },
}
for _species_name, _systems_to_add in DRAGON_PROFILE_CONSOLIDATION.items():
    _dragon = SPECIES[_species_name]
    _dragon_systems = _dragon.setdefault("systems", {})
    _dragon_names = _dragon.setdefault("organ_names", [])
    for _system_name, _structure_names in _systems_to_add.items():
        _bucket = _dragon_systems.setdefault(_system_name, [])
        for _structure_name in _structure_names:
            if _structure_name not in _dragon_names:
                _dragon_names.append(_structure_name)
            if _structure_name not in _bucket:
                _bucket.append(_structure_name)
    _dragon["organ_names"] = list(dict.fromkeys(_dragon_names))
    _dragon["systems"] = {k: list(dict.fromkeys(v)) for k, v in _dragon_systems.items()}


SPECIES_ALIASES = {
    "person": "human", "humanoid": "human", "human being": "human", "man": "human", "woman": "human",
    "lioness": "lion", "tiger": "tiger", "serpent": "snake", "python": "snake", "viper": "snake", "cobra": "snake",
    "worm": "earthworm", "nightcrawler": "earthworm", "eagle": "eagle", "bald eagle": "eagle", "owl": "owl",
    "raven": "raven", "crow": "raven", "falcon": "falcon", "hawk": "falcon", "parrot": "parrot", "pigeon": "pigeon", "dove": "pigeon",
    "cattle": "cow", "bovine": "cow", "pig": "pig", "boar": "pig", "horse": "horse", "dog": "dog",
    "griffon": "griffin", "goblin": "goblin", "orc": "orc", "elf": "elf",
    "gray wolf": "wolf", "grey wolf": "wolf", "brown bear": "bear", "grizzly": "bear",
    "african elephant": "elephant", "bat": "bat", "croc": "crocodile", "alligator": "crocodile",
    "turtle": "tortoise", "frog": "frog", "amphibian": "frog", "shark": "shark", "dolphin": "dolphin",
    "orca": "dolphin", "killer whale": "dolphin", "octopus": "octopus", "spider": "spider", "arachnid": "spider",
    "cervid": "deer", "lagomorph": "rabbit", "camelid": "camel", "wallaroo": "kangaroo",
    "domestic chicken": "chicken", "penguin": "penguin", "seal": "seal", "whale": "whale",
    "squid": "squid", "crustacean": "crab", "bee": "bee", "ant": "ant", "salamander": "salamander",
    "hydra polyp": "freshwater_hydra", "centaur": "centaur", "mermaid": "merfolk", "merman": "merfolk",
    "minotaur": "minotaur", "phoenix": "phoenix", "hydra": "hydra",
    "tyrannosaurus rex": "tyrannosaurus", "t rex": "tyrannosaurus", "trex": "tyrannosaurus",
    "velociraptor": "velociraptor", "stegosaurus": "stegosaurus", "brachiosaurus": "brachiosaurus",
    "ankylosaur": "ankylosaurus", "spinosaur": "spinosaurus", "diplodocus": "diplodocus",
    "parasaur": "parasaurolophus", "pachycephalosaur": "pachycephalosaurus",
    "pterodactyl": "pteranodon", "pterosaur": "pteranodon", "mosasaur": "mosasaurus",
    "western dragon": "western_dragon", "wyvern": "western_dragon",
    "eastern dragon": "eastern_dragon", "long": "eastern_dragon", "lung dragon": "eastern_dragon",
    "worker ant": "ant_worker", "soldier ant": "ant_soldier", "queen ant": "ant_queen",
    "slime creature": "slime", "gelatinous slime": "slime",
    "chimp": "chimpanzee", "great ape": "chimpanzee",
    "gorilla": "gorilla", "goat": "goat", "sheep": "sheep", "rhino": "rhinoceros",
    "hippo": "hippopotamus", "ostrich": "ostrich", "hummingbird": "hummingbird",
    "chameleon": "chameleon", "iguana": "iguana", "sea turtle": "sea_turtle",
    "eel": "eel", "orca": "orca", "killer whale": "orca", "manatee": "manatee",
    "snail": "snail", "scorpion": "scorpion", "butterfly": "butterfly", "leech": "leech",
    "jellyfish": "jellyfish", "sea star": "sea_star", "starfish": "sea_star",
    "millipede": "millipede", "beetle": "beetle",
}

# Individually addressable typical adult human bone inventory. This is deliberately
# expanded from the regional inventory above; animal profiles do not inherit these
# human-specific counts or phalangeal assumptions.
def _make_human_bone_records():
    records = []
    def add(name, region, group):
        records.append({"name": name, "region": region, "group": group,
                        "classification": "human", "counting_note": "Typical adult inventory; anatomical variation exists."})
    for name in ["frontal", "left_parietal", "right_parietal", "left_temporal", "right_temporal", "occipital", "sphenoid", "ethmoid"]:
        add(name, "axial", "cranial_bones")
    for name in ["mandible", "left_maxilla", "right_maxilla", "left_zygomatic", "right_zygomatic", "left_nasal", "right_nasal", "left_lacrimal", "right_lacrimal", "left_palatine", "right_palatine", "left_inferior_nasal_concha", "right_inferior_nasal_concha", "vomer"]:
        add(name, "axial", "facial_bones")
    for side in ("left", "right"):
        for name in ("malleus", "incus", "stapes"):
            add(f"{side}_{name}", "axial", "auditory_ossicles")
    add("hyoid", "axial", "hyoid")
    add("atlas_c1", "axial", "vertebral_column")
    add("axis_c2", "axial", "vertebral_column")
    for n in range(3, 8): add(f"cervical_c{n}", "axial", "vertebral_column")
    for n in range(1, 13): add(f"thoracic_t{n}", "axial", "vertebral_column")
    for n in range(1, 6): add(f"lumbar_l{n}", "axial", "vertebral_column")
    add("sacrum", "axial", "vertebral_column")
    add("coccyx", "axial", "vertebral_column")
    add("sternum", "axial", "thoracic_cage")
    for side in ("left", "right"):
        for n in range(1, 13): add(f"{side}_rib_{n}", "axial", "thoracic_cage")
    for name in ("left_clavicle", "right_clavicle", "left_scapula", "right_scapula"):
        add(name, "appendicular", "pectoral_girdle")
    for side in ("left", "right"):
        for name in ("humerus", "radius", "ulna"):
            add(f"{side}_{name}", "appendicular", "upper_limbs")
        for name in ("scaphoid", "lunate", "triquetrum", "pisiform", "trapezium", "trapezoid", "capitate", "hamate"):
            add(f"{side}_{name}", "appendicular", "upper_limbs")
        for n in range(1, 6): add(f"{side}_metacarpal_{n}", "appendicular", "upper_limbs")
        for level, digits in (("proximal", ["thumb", "index", "middle", "ring", "little"]),
                              ("middle", ["index", "middle", "ring", "little"]),
                              ("distal", ["thumb", "index", "middle", "ring", "little"])):
            for digit in digits: add(f"{side}_{digit}_{level}_phalanx", "appendicular", "upper_limbs")
    add("left_hip_bone", "appendicular", "pelvic_girdle")
    add("right_hip_bone", "appendicular", "pelvic_girdle")
    for side in ("left", "right"):
        for name in ("femur", "patella", "tibia", "fibula"):
            add(f"{side}_{name}", "appendicular", "lower_limbs")
        for name in ("talus", "calcaneus", "navicular", "cuboid", "medial_cuneiform", "intermediate_cuneiform", "lateral_cuneiform"):
            add(f"{side}_{name}", "appendicular", "lower_limbs")
        for n in range(1, 6): add(f"{side}_metatarsal_{n}", "appendicular", "lower_limbs")
        for level, digits in (("proximal", ["great_toe", "second_toe", "third_toe", "fourth_toe", "little_toe"]),
                              ("middle", ["second_toe", "third_toe", "fourth_toe", "little_toe"]),
                              ("distal", ["great_toe", "second_toe", "third_toe", "fourth_toe", "little_toe"])):
            for digit in digits: add(f"{side}_{digit}_{level}_phalanx", "appendicular", "lower_limbs")
    return records


HUMAN_BONE_RECORDS = _make_human_bone_records()

# Comparative skeletal *structures* for species where an exact full named-bone
# inventory is not asserted in this compact catalogue. Fused elements, digits and
# counts vary by species, breed, age and pathology; the API keeps count=None.
_MAMMAL_SKELETAL_STRUCTURES = [
    "skull", "mandible", "maxilla", "cervical_vertebrae", "thoracic_vertebrae", "lumbar_vertebrae",
    "sacrum", "caudal_vertebrae", "ribs", "sternum", "left_scapula", "right_scapula",
    "left_humerus", "right_humerus", "left_radius", "right_radius", "left_ulna", "right_ulna",
    "carpal_bones", "metacarpal_bones", "forelimb_phalanges", "pelvis", "ilium", "ischium", "pubis",
    "left_femur", "right_femur", "left_patella", "right_patella", "left_tibia", "right_tibia",
    "left_fibula", "right_fibula", "tarsal_bones", "metatarsal_bones", "hindlimb_phalanges",
    "sesamoid_bones", "jaw_teeth_support", "hyoid_apparatus",
]
_BIRD_SKELETAL_STRUCTURES = [
    "skull", "beak_bones", "mandible", "cervical_vertebrae", "thoracic_vertebrae", "synsacrum",
    "caudal_vertebrae", "pygostyle", "ribs", "uncinate_processes", "sternum", "sternal_keel",
    "furcula", "left_coracoid", "right_coracoid", "left_scapula", "right_scapula",
    "left_humerus", "right_humerus", "left_radius", "right_radius", "left_ulna", "right_ulna",
    "carpometacarpus_left", "carpometacarpus_right", "wing_phalanges", "pelvis", "left_femur", "right_femur",
    "left_tibiotarsus", "right_tibiotarsus", "left_fibula_reduced", "right_fibula_reduced",
    "left_tarsometatarsus", "right_tarsometatarsus", "foot_phalanges", "hallux", "furculum_and_keel_attachments",
]
_SNAKE_SKELETAL_STRUCTURES = [
    "skull", "premaxilla", "maxilla", "mandible", "quadrate_bones", "pterygoid_bones",
    "vertebral_column", "cervical_vertebrae", "trunk_vertebrae", "caudal_vertebrae", "rib_pairs",
    "zygapophyses", "intervertebral_articulations", "pelvic_vestiges_optional",
]

_MAMMALS = {"lion", "tiger", "giraffe", "cow", "pig", "horse", "dog", "wolf", "bear", "elephant", "bat", "dolphin", "deer", "rabbit", "camel", "kangaroo", "seal", "whale"}
_BIRDS = {"eagle", "owl", "raven", "falcon", "parrot", "pigeon", "chicken", "penguin", "phoenix"}
for _species_name, _profile in SPECIES.items():
    if _species_name == "human":
        _structures = [record["name"] for record in HUMAN_BONE_RECORDS]
        _profile["skeletal_structures"] = _structures
        for _record in HUMAN_BONE_RECORDS:
            _bone_name = _record["name"]
            ORGANS.setdefault(_bone_name, {
                "name": _bone_name, "system": "skeletal", "kind": "individual_bone",
                "role": f"Individually addressable human skeletal element in the {_record['group'].replace('_', ' ')} region.",
                "substructures": [], "tissues": ["bone", "marrow where present", "periosteum"],
                "dependencies": ["muscular", "circulatory"], "notes": _record["counting_note"],
                "bone_region": _record["region"], "bone_group": _record["group"],
            })
        for _bone_name in _structures:
            if _bone_name not in _profile["organ_names"]:
                _profile["organ_names"].append(_bone_name)
        _profile["systems"].setdefault("skeletal", [])
        _profile["systems"]["skeletal"] = list(dict.fromkeys(_profile["systems"]["skeletal"] + _structures))
    elif _species_name in _MAMMALS:
        _structures = _MAMMAL_SKELETAL_STRUCTURES
    elif _species_name in _BIRDS:
        _structures = _BIRD_SKELETAL_STRUCTURES
    elif _species_name == "snake":
        _structures = _SNAKE_SKELETAL_STRUCTURES
    elif _species_name in {"crocodile", "tortoise", "frog"}:
        _structures = ["skull", "vertebral_column", "ribs", "limb_girdles", "forelimb_bones", "hindlimb_bones", "phalanges"]
        if _species_name == "tortoise": _structures += ["carapace", "plastron"]
        if _species_name == "frog": _structures += ["elongated_hindlimbs", "urostyle"]
    elif _species_name == "shark":
        _structures = ["cartilaginous_skeleton", "cartilaginous_cranium", "vertebral_column", "jaw_cartilages", "pectoral_fins", "pelvic_fins", "caudal_fin"]
    elif _species_name in {"octopus", "spider", "bee", "ant", "freshwater_hydra"}:
        # No conventional itemised vertebrate bones. Preserve the profile's own
        # exoskeletal, hydrostatic or soft-body regions for inspection instead.
        _structures = list(_profile.get("skeleton", {}).get("regions", []))
    elif _species_name in {"crab"}:
        _structures = list(_profile.get("skeleton", {}).get("regions", []))
    elif _species_name in {"dragon", "griffin", "goblin", "orc", "elf", "centaur", "merfolk", "minotaur", "hydra"}:
        # Editable fantasy scaffolds; static inventory is intentionally unspecified.
        _structures = list(_profile.get("skeleton", {}).get("regions", [])) + ["fantasy_specialised_skeleton", "designer_defined_fused_bones"]
    elif _species_name == "salamander":
        _structures = ["skull", "vertebral_column", "ribs", "limb_girdles", "forelimb_bones", "hindlimb_bones", "tail_vertebrae"]
    else:
        _structures = list(_profile.get("skeleton", {}).get("regions", []))
    if _species_name != "human":
        # `skeleton.regions` is descriptive prose (e.g. "paired wings and reinforced
        # pectoral girdle"), not a list of addressable organs. Only add canonical
        # identifiers to `skeletal_structures`; retain every descriptive region in
        # the original skeleton record so users can still inspect the body plan.
        _addressable = []
        for _candidate in _structures:
            if not isinstance(_candidate, str):
                continue
            _candidate = _candidate.strip().casefold()
            if not re.fullmatch(r"[a-z][a-z0-9_]{0,63}", _candidate):
                continue
            if any(_part in {"where", "when", "present", "optional", "varies", "or", "and", "by"}
                   for _part in _candidate.split("_")):
                continue
            if _candidate not in _addressable:
                _addressable.append(_candidate)
        _profile["skeletal_structures"] = _addressable
        _system_names = _profile["systems"].setdefault("skeletal", [])
        # Only conventional endoskeletal/composite skeletal structures are inserted
        # into active organ tracking. Soft-bodied and exoskeletal taxa keep their
        # body regions in the profile, but these are not fictitious bones or organs.
        _skel_type = str(_profile.get("skeleton", {}).get("type", "")).casefold()
        _track_as_skeletal_organs = "endoskeleton" in _skel_type or _skel_type == "hybrid"
        if _track_as_skeletal_organs:
            for _name in _profile["skeletal_structures"]:
                if _name not in ORGANS:
                    ORGANS[_name] = {"name": _name, "system": "skeletal", "kind": "skeletal_structure",
                                     "role": f"Species-specific or homologous skeletal structure '{_name.replace('_', ' ')}'.",
                                     "substructures": [], "tissues": ["bone or cartilage depending on species"],
                                     "dependencies": ["muscular", "locomotor"],
                                     "notes": "Structural label, not a claim of one universal bone count; consult species-specific osteology."}
                if _name not in _profile["organ_names"]:
                    _profile["organ_names"].append(_name)
                if _name not in _system_names:
                    _system_names.append(_name)

# Dimensioned physical priors make anatomy-bound beings participate in movement
# with plausible game-scale mass and collision proxies instead of the generic
# 1 kg / 1 m^3 object defaults. These are deliberately explicit design baselines:
# they are not zoological measurements and can be overridden on custom species.
# Values: mass kg, body length m, body width m, body height m, collision radius m,
# apparent bulk density kg/m^3. The physics engine is still a 2D point/circle
# approximation; articulated anatomy is metadata plus selected state hooks.
_BODY_PHYSICAL_BASELINES = {
    "human": (70.0, 0.45, 0.55, 1.75, 0.36, 985.0),
    "lion": (190.0, 1.90, 0.75, 1.10, 0.62, 990.0),
    "tiger": (220.0, 2.20, 0.78, 1.05, 0.66, 990.0),
    "snake": (8.0, 2.50, 0.18, 0.18, 0.14, 1020.0),
    "earthworm": (0.005, 0.12, 0.006, 0.006, 0.004, 1020.0),
    "eagle": (5.0, 0.90, 1.80, 0.50, 0.30, 900.0),
    "owl": (2.5, 0.45, 0.90, 0.40, 0.22, 900.0),
    "raven": (1.2, 0.35, 0.75, 0.30, 0.17, 900.0),
    "falcon": (1.1, 0.40, 0.80, 0.30, 0.17, 900.0),
    "parrot": (0.6, 0.25, 0.35, 0.25, 0.12, 900.0),
    "pigeon": (0.35, 0.30, 0.65, 0.20, 0.11, 900.0),
    "giraffe": (900.0, 4.50, 1.50, 5.20, 1.05, 990.0),
    "cow": (650.0, 2.50, 1.00, 1.55, 0.82, 990.0),
    "pig": (120.0, 1.50, 0.65, 1.00, 0.47, 990.0),
    "horse": (500.0, 2.40, 0.80, 1.70, 0.68, 990.0),
    "dog": (25.0, 0.90, 0.40, 0.65, 0.30, 990.0),
    "dragon": (800.0, 4.00, 2.50, 2.40, 1.35, 900.0),
    "griffin": (180.0, 2.00, 1.80, 1.40, 0.80, 940.0),
    "goblin": (35.0, 0.60, 0.35, 1.10, 0.28, 980.0),
    "orc": (120.0, 1.20, 0.65, 2.00, 0.50, 990.0),
    "elf": (65.0, 0.45, 0.50, 1.80, 0.35, 985.0),
    "wolf": (45.0, 1.30, 0.50, 0.80, 0.34, 990.0),
    "bear": (250.0, 1.80, 1.00, 1.50, 0.70, 990.0),
    "elephant": (5000.0, 5.00, 2.00, 3.20, 1.55, 990.0),
    "bat": (0.04, 0.07, 0.30, 0.05, 0.035, 900.0),
    "crocodile": (250.0, 3.00, 0.80, 0.70, 0.55, 1010.0),
    "tortoise": (8.0, 0.50, 0.30, 0.25, 0.22, 1000.0),
    "frog": (0.10, 0.10, 0.08, 0.06, 0.04, 1020.0),
    "shark": (300.0, 2.20, 0.70, 0.70, 0.52, 1030.0),
    "dolphin": (250.0, 2.20, 0.80, 1.00, 0.55, 1025.0),
    "octopus": (5.0, 0.65, 0.50, 0.35, 0.25, 1025.0),
    "spider": (0.005, 0.03, 0.05, 0.02, 0.025, 1050.0),
    "deer": (70.0, 1.50, 0.50, 1.20, 0.40, 990.0),
    "rabbit": (2.0, 0.40, 0.20, 0.25, 0.14, 990.0),
    "camel": (550.0, 2.30, 0.80, 1.90, 0.68, 990.0),
    "kangaroo": (75.0, 1.20, 0.55, 1.70, 0.43, 990.0),
    "chicken": (2.5, 0.40, 0.40, 0.35, 0.18, 900.0),
    "penguin": (25.0, 0.60, 0.35, 0.80, 0.25, 950.0),
    "seal": (120.0, 1.50, 0.65, 0.80, 0.45, 1025.0),
    "whale": (2500.0, 7.00, 1.80, 2.00, 1.45, 1025.0),
    "squid": (1.0, 0.40, 0.20, 0.20, 0.13, 1025.0),
    "crab": (0.04, 0.10, 0.10, 0.05, 0.05, 1050.0),
    "bee": (0.00002, 0.012, 0.025, 0.007, 0.006, 1050.0),
    "ant": (0.00001, 0.006, 0.003, 0.002, 0.0015, 1050.0),
    "salamander": (0.03, 0.20, 0.04, 0.04, 0.03, 1020.0),
    "freshwater_hydra": (0.00001, 0.015, 0.003, 0.003, 0.002, 1000.0),
    "chimpanzee": (50.0, 0.80, 0.50, 1.30, 0.40, 990.0),
    "gorilla": (160.0, 1.20, 0.70, 1.70, 0.58, 990.0),
    "goat": (60.0, 0.90, 0.40, 0.90, 0.34, 990.0),
    "sheep": (70.0, 0.90, 0.50, 0.80, 0.35, 990.0),
    "rhinoceros": (2000.0, 3.50, 1.70, 1.80, 1.15, 990.0),
    "hippopotamus": (1500.0, 3.00, 1.50, 1.50, 1.00, 1010.0),
    "ostrich": (100.0, 2.00, 0.60, 2.50, 0.48, 900.0),
    "hummingbird": (0.004, 0.06, 0.10, 0.05, 0.025, 900.0),
    "chameleon": (0.15, 0.20, 0.07, 0.12, 0.05, 1020.0),
    "iguana": (4.0, 0.80, 0.20, 0.40, 0.18, 1020.0),
    "sea_turtle": (80.0, 1.00, 0.80, 0.40, 0.40, 1025.0),
    "eel": (2.0, 0.80, 0.08, 0.08, 0.08, 1025.0),
    "orca": (4000.0, 5.50, 2.00, 2.00, 1.45, 1025.0),
    "manatee": (500.0, 3.00, 1.20, 1.20, 0.90, 1025.0),
    "snail": (0.02, 0.04, 0.025, 0.03, 0.02, 1050.0),
    "scorpion": (0.01, 0.08, 0.06, 0.04, 0.03, 1050.0),
    "butterfly": (0.001, 0.06, 0.09, 0.02, 0.02, 950.0),
    "leech": (0.005, 0.10, 0.01, 0.01, 0.008, 1020.0),
    "jellyfish": (0.5, 0.30, 0.30, 0.25, 0.18, 1025.0),
    "sea_star": (0.3, 0.25, 0.25, 0.06, 0.15, 1025.0),
    "millipede": (0.02, 0.15, 0.02, 0.02, 0.01, 1050.0),
    "beetle": (0.01, 0.03, 0.03, 0.02, 0.012, 1050.0),
    "centaur": (600.0, 2.20, 1.00, 2.00, 0.95, 990.0),
    "merfolk": (100.0, 1.60, 0.60, 1.70, 0.48, 1000.0),
    "minotaur": (450.0, 1.80, 0.80, 2.10, 0.80, 990.0),
    "hydra": (1300.0, 5.00, 2.00, 2.50, 1.50, 930.0),
    "phoenix": (8.0, 0.90, 1.80, 0.70, 0.35, 900.0),
    "tyrannosaurus": (8000.0, 12.0, 3.5, 4.0, 2.2, 1000.0),
    "triceratops": (7000.0, 8.0, 3.0, 3.0, 2.0, 1000.0),
    "velociraptor": (18.0, 2.0, 0.55, 1.0, 0.45, 950.0),
    "stegosaurus": (5000.0, 7.0, 2.6, 3.0, 1.8, 1000.0),
    "brachiosaurus": (28000.0, 18.0, 5.0, 12.0, 4.8, 990.0),
    "ankylosaurus": (6000.0, 7.0, 2.5, 2.0, 1.8, 1000.0),
    "spinosaurus": (7500.0, 14.0, 4.5, 4.2, 2.2, 1000.0),
    "diplodocus": (12000.0, 24.0, 3.8, 5.0, 2.5, 990.0),
    "parasaurolophus": (2500.0, 9.0, 2.3, 2.8, 1.3, 1000.0),
    "pachycephalosaurus": (450.0, 4.5, 1.1, 1.8, 0.7, 990.0),
    "pteranodon": (25.0, 5.5, 6.0, 1.8, 0.8, 900.0),
    "mosasaurus": (9000.0, 13.0, 3.0, 3.0, 2.0, 1025.0),
    "western_dragon": (950.0, 5.5, 3.8, 3.0, 1.7, 920.0),
    "eastern_dragon": (420.0, 9.0, 1.4, 1.8, 0.9, 920.0),
    "ant_worker": (0.000012, 0.006, 0.003, 0.002, 0.0015, 1050.0),
    "ant_soldier": (0.000025, 0.008, 0.004, 0.003, 0.002, 1050.0),
    "ant_queen": (0.00008, 0.015, 0.007, 0.004, 0.003, 1050.0),
    "slime": (1.5, 0.45, 0.35, 0.35, 0.24, 1030.0),
}

for _species_key, _profile in SPECIES.items():
    _baseline = _BODY_PHYSICAL_BASELINES.get(_species_key)
    if _baseline is None:
        # A defensive fallback for future templates: use the nearest declared
        # body profile's mass when possible, then a conservative 70 kg baseline.
        _base_key = str(_profile.get("base", "human")).casefold().replace(" ", "_")
        _parent = SPECIES.get(_base_key, SPECIES.get("human", {}))
        _parent_sim = _parent.get("simulation", {}) if isinstance(_parent, dict) else {}
        _parent_mass = _parent_sim.get("body_mass_kg", 70.0) if isinstance(_parent_sim, dict) else 70.0
        _baseline = (float(_parent_mass), 0.6, 0.3, 1.0, 0.3, 990.0)
    _mass, _length, _width, _height, _radius, _density = _baseline
    _simulation = _profile.setdefault("simulation", {})
    _simulation.update({
        "body_mass_kg": _mass,
        "body_length_m": _length,
        "body_width_m": _width,
        "body_height_m": _height,
        "collision_radius_m": _radius,
        "body_density_kg_m3": _density,
        "body_volume_m3": _mass / _density,
        "physical_model_note": "Approximate game-scale baseline; the 2D collider is a circle proxy, not an articulated body or exact species measurement.",
    })

_BODY_BASELINE_KEYS = set(_BODY_PHYSICAL_BASELINES)

# Normalised schema used by inspection, tooling and future physiology modules.
# `simulation_level` is explicit so catalogue-only structures are never mistaken
# for full organ solvers.
for _organ_key, _organ_meta in ORGANS.items():
    _organ_meta.setdefault("id", _organ_key)
    _organ_meta.setdefault("tags", list(dict.fromkeys([_organ_meta.get("system", "custom"), _organ_meta.get("kind", "organ_or_structure")])))
    _organ_meta.setdefault("body_region", "species-dependent")
    _organ_meta.setdefault("laterality", "species-dependent")
    _organ_meta.setdefault("parent", None)
    _organ_meta.setdefault("simulation_level", "reference_with_selected_state_hooks")
    _organ_meta.setdefault("state_fields", ["integrity"] if _organ_meta.get("kind") == "organ_or_structure" else [])

# Build constant stock search text once. The runtime can combine this with small
# per-runtime custom registries instead of repeatedly traversing all anatomy.
SPECIES_SEARCH_TEXT = {
    _key: " ".join([_key, str(_profile.get("label", "")), str(_profile.get("clade", "")),
                    " ".join(_profile.get("senses", [])), " ".join(_profile.get("special_organs", [])),
                    " ".join(_profile.get("organ_names", [])), " ".join(_profile.get("components", []))]).casefold()
    for _key, _profile in SPECIES.items()
}
ORGAN_SEARCH_TEXT = {
    _key: " ".join([_key, str(_profile.get("name", "")), str(_profile.get("role", "")),
                    str(_profile.get("system", "")), " ".join(_profile.get("tags", []))]).casefold()
    for _key, _profile in ORGANS.items()
}
