"""Original magical-discipline catalogue, inspired by broad genre themes.

This library describes schools, their research questions, constraints and counters.
It is metadata rather than a promise that every school has a dedicated simulator.
"""
from __future__ import annotations

import copy
import re
from typing import Any

from ..errors import MagicErrorML, PhysicsErrorML, TypeErrorML

_SCHOOLS: dict[str, dict[str, Any]] = {
    "mystic_magic": {"label": "Mystic Magic", "domain": "structured spellcraft", "description": "Uses diagrams, words, gestures, prepared anchors and trained control to shape effects through explicit magical rules.", "patterns": ["spell construction", "wards", "sigils", "portal geometry", "binding circles", "counterspells"], "cost_axes": ["precision", "preparation", "range", "complexity", "stability"], "limits": ["complex workings need a complete specification", "broken anchors can destabilise sustained effects", "prepared geometry does not grant unlimited energy"], "counters": ["disrupt the anchor", "break line of effect", "counter the declared operation", "outwait finite duration"], "status": "foundational-practice"},
    "chaos_magic": {"label": "Chaos Magic", "domain": "probability and unstable rule alteration", "description": "Alters possible outcomes, local constraints or the weighting of uncertain events. It must define an outcome space and a bounded scope rather than acting as an unrestricted wish.", "patterns": ["probability shift", "conditional alteration", "local law distortion", "wild surge", "causal debt"], "cost_axes": ["uncertainty", "scope", "duration", "precision", "backlash risk"], "limits": ["cannot guarantee a logically impossible outcome", "wide outcome spaces increase instability", "lasting law changes require explicit persistence"], "counters": ["stabilisation wards", "reduce the outcome space", "anchor a known invariant", "interrupt concentration"], "status": "design-catalogue"},
    "dimensional_magic": {"label": "Dimensional Magic", "domain": "planes, boundaries and topology", "description": "Finds, measures, opens, seals and traverses pathways between distinct planes or folded regions.", "patterns": ["plane appraisal", "pathway opening", "portal", "spatial fold", "boundary seal", "coordinate anchor"], "cost_axes": ["distance", "boundary resistance", "mass transported", "stability", "destination knowledge"], "limits": ["a destination must be identified", "a pathway must obey its transition rules", "unstable links can collapse or misroute travel"], "counters": ["seal the boundary", "move or disrupt the anchor", "conceal destination signatures", "block the route"], "status": "partial-foundation"},
    "astral_magic": {"label": "Astral Magic", "domain": "consciousness projection and non-corporeal presence", "description": "Separates a projection or point of awareness from the body's ordinary sensory location. A complete model must state what the projection can perceive, touch, carry and return to.", "patterns": ["astral projection", "remote perception", "dream entry", "spirit rendezvous", "return tether"], "cost_axes": ["distance", "duration", "sensory resolution", "tether strength", "resistance"], "limits": ["projection is not automatically a physical duplicate", "corporeal damage and projected harm are distinct", "return and body protection must be explicit"], "counters": ["tether ward", "concealment", "anti-projection boundary", "break sensory link"], "status": "design-catalogue"},
    "telepathy": {"label": "Telepathy", "domain": "mental information exchange", "description": "Sends, receives or interprets thoughts and intentions with consent, resistance, range and privacy represented as explicit rules.", "patterns": ["thought message", "surface-thought reading", "shared perception", "mental barrier", "memory imprint"], "cost_axes": ["range", "number of minds", "depth", "duration", "resistance"], "limits": ["thoughts are not a perfect factual transcript", "language, attention and mental state affect interpretation", "deep access should face stronger resistance"], "counters": ["mental ward", "noise or decoy thoughts", "distance", "consent boundary", "counter-intrusion"], "status": "design-catalogue"},
    "telekinesis": {"label": "Telekinesis", "domain": "remote mechanical force", "description": "Applies forces to selected objects without direct contact. The world engine should resolve mass, torque, collisions, anchoring and momentum instead of teleporting objects to the desired position.", "patterns": ["lift", "push", "pull", "hold", "rotate", "multi-object manipulation"], "cost_axes": ["total mass", "acceleration", "range", "precision", "number of targets"], "limits": ["force and momentum are finite", "objects still collide and can break", "holding multiple targets divides attention or control"], "counters": ["anchor the target", "increase mass or friction", "break line of effect", "overload precision"], "status": "supported-principle"},
    "energy_magic": {"label": "Energy Magic", "domain": "energy transfer and field shaping", "description": "Creates, channels, redirects or dissipates named forms of energy with accounting, coupling efficiency and heat/force consequences.", "patterns": ["energy bolt", "beam", "barrier", "absorption", "redirection", "pulse"], "cost_axes": ["energy quantity", "transfer rate", "coupling", "range", "heat dissipation"], "limits": ["transfers must be accounted for", "absorbing energy needs capacity and a destination", "high power can produce collateral heat or impulse"], "counters": ["reflective or absorptive boundary", "decoupling barrier", "heat sink", "interrupt the channel"], "status": "partial-foundation"},
    "elemental_magic": {"label": "Elemental Magic", "domain": "Fire, Water, Earth and Air", "description": "Works with the four foundational elements as magical domains. It does not make arbitrary conversion between elements legal unless a separate rule explicitly permits it.", "patterns": ["elemental projection", "element shaping", "elemental resistance", "elemental sensing", "elemental pressure"], "cost_axes": ["mass affected", "range", "state change", "control precision", "environmental availability"], "limits": ["four elements are foundational categories, not a replacement for chemical composition", "material properties still matter", "visual effects do not create matter by themselves"], "counters": ["environmental mismatch", "counter-elemental ward", "break the channel", "use material-specific resistance"], "status": "supported-domain"},
    "weather_magic": {"label": "Weather Magic", "domain": "local and regional atmospheric state", "description": "Changes wind, precipitation, temperature, humidity, cloud cover, fog and lightning through composable environmental parameters.", "patterns": ["summon rain", "wind shear", "fog bank", "hail or snow", "lightning conditions", "heat wave"], "cost_axes": ["area", "intensity", "duration", "humidity/heat gradient", "storm organisation"], "limits": ["large zones require more time and environmental exchange", "extreme states create hazards for everyone in the area", "wind and rain must affect world objects through physics"], "counters": ["leave the region", "barrier or shelter", "disrupt moisture/thermal source", "counter-climate field"], "status": "supported-principle"},
    "conjuration": {"label": "Conjuration", "domain": "bringing physical matter into existence", "description": "Creates a new physical object with a defined material, mass, geometry, position and world interaction. It is distinct from summoning an existing being.", "patterns": ["raw material", "weapon blueprint", "armour piece", "arrow", "temporary construct", "material reserve"], "cost_axes": ["mass", "complexity", "precision", "persistence", "material scarcity or rule"], "limits": ["mass and composition must be explicit", "conjured objects need valid physics properties", "equipment quality follows materials and geometry"], "counters": ["dispel only if bound by a dispellable effect", "damage the object", "deny access to the required pattern"], "status": "supported-principle"},
    "transmutation": {"label": "Transmutation", "domain": "material composition", "description": "Changes an object's composition while following configured conservation, mass, energy and material-property rules.", "patterns": ["alloy conversion", "purification", "material substitution", "corrosion reversal", "state conversion"], "cost_axes": ["mass changed", "atomic composition distance", "purity", "thermal/pressure state", "precision"], "limits": ["geometry belongs to shaping", "composition must be represented", "conservation policy must be explicit"], "counters": ["material lock", "composition ward", "interrupted work", "protected structure"], "status": "supported-principle"},
    "transfiguration": {"label": "Transfiguration", "domain": "form and organisation", "description": "Changes the form of eligible living entities or conjured matter while respecting the selected body or material model. Shape alone changes geometry, not life or identity.", "patterns": ["body form", "species template", "material form", "temporary alteration", "restoration"], "cost_axes": ["structural difference", "living complexity", "duration", "identity preservation", "reversibility"], "limits": ["life-support systems must remain valid", "a new shape is not automatically a living organism", "species designs need stated assumptions"], "counters": ["form anchor", "reversion pattern", "resistive anatomy", "interrupt before completion"], "status": "partial-foundation"},
    "blood_magic": {"label": "Blood Magic", "domain": "circulation, blood and blood-borne signatures", "description": "Interacts with circulating fluid, clotting, flow, blood-bound marks and permitted biological signals. Detailed targets require a physiology model; volume and injury limits still apply.", "patterns": ["stop bleeding", "clotting", "blood tracking", "flow redirection", "blood ward", "blood oath"], "cost_axes": ["volume", "flow rate", "target resistance", "range", "precision"], "limits": ["blood is not a universal substitute for life", "blood loss affects body state", "a blood signature is not proof of all memories or identity"], "counters": ["clotting ward", "blood-sealing", "distance", "body protection", "decoy signature"], "status": "supported-principle"},
    "vitality_magic": {"label": "Vitality Magic", "domain": "healing, growth, body regulation and life-support", "description": "Supports repair and homeostasis through an explicit anatomy model. It must distinguish wound closure, tissue regeneration, organ repair and resurrection.", "patterns": ["wound closure", "tissue repair", "toxin clearance", "stamina restoration", "organ restoration", "controlled adaptation"], "cost_axes": ["damage severity", "tissue complexity", "time", "available matter/energy", "immune compatibility"], "limits": ["healing does not imply instant regrowth", "severe organ damage needs a corresponding anatomy model", "resurrection must address death and identity separately"], "counters": ["anti-healing ward", "ongoing injury", "toxin or infection", "incompatible tissue"], "status": "partial-foundation"},
    "necromancy": {"label": "Necromancy", "domain": "death, remains, undeath and soul-state", "description": "Works with corpses, remains, skeletal constructs, undeath and defined soul/identity transitions. Reanimating remains differs from summoning a new being.", "patterns": ["corpse animation", "skeletal servant", "lich transformation", "death-sense", "soul tether", "post-mortem memory echo"], "cost_axes": ["body condition", "control complexity", "duration", "identity retention", "soul resistance"], "limits": ["a corpse is not living tissue", "memory or personality restoration is a separate rule", "lich states require explicit anchors and failure conditions"], "counters": ["banishment", "soul ward", "destroy the control anchor", "sanctify or release remains"], "status": "partial-foundation"},
    "illusion": {"label": "Illusion Magic", "domain": "perception and sensory interpretation", "description": "Changes what a perceiver senses or how signals are interpreted without necessarily creating corresponding physical matter.", "patterns": ["visual image", "soundscape", "false scent", "decoy signature", "group illusion", "invisibility-like concealment"], "cost_axes": ["number of senses", "viewers", "resolution", "area", "duration"], "limits": ["illusions do not automatically block physical objects", "sensors may detect inconsistencies", "each sensory channel must be declared"], "counters": ["alternate sensory channel", "disbelief or probing", "environmental measurement", "illusion detection"], "status": "design-catalogue"},
    "wards_and_seals": {"label": "Wards and Seals", "domain": "protection, permission and boundary conditions", "description": "Defines what may pass, affect, sense or change across a region, object or entity boundary.", "patterns": ["barrier", "permission seal", "anti-summoning boundary", "containment", "alarm ward", "spell reflection"], "cost_axes": ["boundary area", "excluded operations", "number of permissions", "duration", "attack pressure"], "limits": ["a ward needs explicit coverage and categories", "no finite barrier blocks every possible effect by default", "reflected effects need a valid destination"], "counters": ["find a coverage gap", "deplete finite barrier strength", "authenticate permission", "counter the ward's declared rule"], "status": "supported-principle"},
    "rune_magic": {"label": "Rune Magic", "domain": "stored instructions and conditional triggers", "description": "Encodes a bounded effect into a mark, object or location which runs when declared conditions are met.", "patterns": ["trigger glyph", "storage sigil", "alarm rune", "delayed cast", "keyed ward", "linked runes"], "cost_axes": ["instruction complexity", "storage duration", "trigger sensitivity", "payload size", "number of linked runes"], "limits": ["stored effects require a defined trigger and expiration", "linked runes need cycle and amplification limits", "payloads inherit normal world safety rules"], "counters": ["erase or cover the rune", "spoof/disable the trigger", "break the link", "wait for expiry"], "status": "design-catalogue"},
    "cosmic_magic": {"label": "Cosmic Magic", "domain": "large-scale celestial and fundamental phenomena", "description": "Models magic drawing on star-like sources, celestial cycles or very large-scale field alignment without assuming unlimited power.", "patterns": ["star alignment", "celestial mark", "cosmic beam", "gravity well", "stellar ward", "astral navigation"], "cost_axes": ["source distance", "source strength", "alignment", "scale", "stability"], "limits": ["source availability and propagation must be defined", "large scale does not mean infinite control", "cosmic effects need measurable boundaries"], "counters": ["break alignment", "block source coupling", "move out of field", "disrupt anchor"], "status": "design-catalogue"},
    "shadow_magic": {"label": "Shadow Magic", "domain": "light exclusion, concealment and dark-associated pathways", "description": "Uses occlusion, perception gaps and bounded shadow-space constructs. Darkness itself is not a universal substance unless the world defines it as one.", "patterns": ["shadow veil", "concealment", "shadow tether", "darkness field", "shadow-step", "shade construct"], "cost_axes": ["light contrast", "area", "distance", "anchor continuity", "duration"], "limits": ["a shadow depends on light and geometry unless given magical existence", "darkness does not erase physical collisions", "travel needs valid endpoints"], "counters": ["distributed light", "anchor exposure", "boundary ward", "reveal signature"], "status": "design-catalogue"},
    "light_magic": {"label": "Light Magic", "domain": "illumination, radiance and optical interaction", "description": "Produces light, guides it, focuses it or alters reflection and visibility; thermal and energy consequences depend on intensity.", "patterns": ["illumination", "flash", "beam", "light bridge", "refraction veil", "radiant ward"], "cost_axes": ["radiant output", "focus", "area", "duration", "heat"], "limits": ["visibility and damage are distinct", "intense radiant output requires energy accounting", "line of sight still matters unless redirected"], "counters": ["occlusion", "diffusion", "reflective boundary", "light absorption"], "status": "supported-principle"},
    "sound_magic": {"label": "Sound Magic", "domain": "vibration and acoustic interaction", "description": "Creates, filters or directs mechanical waves in a medium, including silence, resonance and disruptive pulses.", "patterns": ["sound burst", "silence zone", "resonance", "directional shout", "echo mapping", "vibration sensing"], "cost_axes": ["amplitude", "frequency", "area", "medium", "precision"], "limits": ["sound needs a medium", "resonance depends on object properties", "hearing damage and structural breakage require distinct thresholds"], "counters": ["isolation", "damping material", "phase cancellation", "leave the medium/zone"], "status": "design-catalogue"},
    "alchemy": {"label": "Alchemy", "domain": "material recipes and controlled reactions", "description": "Combines materials, reagents, temperature, pressure and magical catalysts into explicitly described processes.", "patterns": ["elixir", "catalyst", "purification", "alloying", "volatile reaction", "material analysis"], "cost_axes": ["ingredient mass", "purity", "reaction energy", "time", "yield"], "limits": ["reactions require recipes and compatible conditions", "yield and by-products must be specified", "alchemical labels do not replace material data"], "counters": ["remove a reagent", "quench the reaction", "contaminate catalyst", "interrupt the process"], "status": "supported-principle"},
    "dream_magic": {"label": "Dream Magic", "domain": "sleep states, dream environments and symbolic communication", "description": "Creates or enters a bounded dream-state representation while keeping physical and dream-world effects separate.", "patterns": ["lucid entry", "dream message", "nightmare veil", "dream sanctuary", "memory symbol"], "cost_axes": ["participants", "stability", "duration", "consent/resistance", "memory fidelity"], "limits": ["dream consequences do not automatically alter physical matter", "memory can be symbolic or distorted", "awakening and safe return must be defined"], "counters": ["wake signal", "mind ward", "dream anchor", "withdraw consent"], "status": "design-catalogue"},
}

_ALIASES = {
    "mysticism": "mystic_magic", "sorcery": "mystic_magic", "sorcerer magic": "mystic_magic",
    "chaos": "chaos_magic", "probability magic": "chaos_magic", "reality warping": "chaos_magic",
    "portal magic": "dimensional_magic", "space magic": "dimensional_magic", "astral projection": "astral_magic",
    "mind magic": "telepathy", "psychic": "telepathy", "telekinesis magic": "telekinesis",
    "element magic": "elemental_magic", "weather": "weather_magic", "conjuring": "conjuration",
    "transmutation magic": "transmutation", "shapeshifting": "transfiguration", "healing magic": "vitality_magic",
    "death magic": "necromancy", "protective magic": "wards_and_seals", "enchantment": "rune_magic",
    "shadow": "shadow_magic", "solar magic": "light_magic", "acoustics": "sound_magic",
}
_NAME = re.compile(r"[A-Za-z][A-Za-z0-9_ -]{0,63}\Z")


def _key(value: Any) -> str:
    if not isinstance(value, str) or not value.strip():
        raise TypeErrorML("arcana lookup expects non-empty text")
    return "_".join(value.strip().casefold().replace("-", " ").split())


def build_library(runtime: Any) -> dict[str, Any]:
    def records() -> dict[str, dict[str, Any]]:
        return {**copy.deepcopy(_SCHOOLS), **copy.deepcopy(getattr(runtime, "custom_arcana_schools", {}))}

    def school(name: Any) -> dict[str, Any]:
        key = _key(name)
        key = _ALIASES.get(key.replace("_", " "), key)
        known = records()
        if key not in known:
            raise MagicErrorML(f"unknown magical discipline '{name}'; use arcana.schools() or arcana.search()")
        return copy.deepcopy({"name": key, **known[key]})

    def schools() -> list[dict[str, Any]]:
        return [{"name": name, **copy.deepcopy(value)} for name, value in sorted(records().items())]

    def search(query: Any) -> list[dict[str, Any]]:
        if not isinstance(query, str) or not query.strip():
            raise TypeErrorML("arcana.search() expects non-empty text")
        key = query.strip().casefold()
        result = []
        for name, value in records().items():
            aliases = [alias for alias, canonical in _ALIASES.items() if canonical == name]
            haystack = " ".join([name, name.replace("_", " "), value.get("label", ""), value.get("domain", ""), value.get("description", ""), *aliases, *value.get("patterns", []), *value.get("limits", []), *value.get("counters", [])]).casefold()
            if key in haystack:
                result.append({"name": name, "label": value.get("label"), "domain": value.get("domain"), "status": value.get("status")})
        return result[:200]

    def define(name: Any, *, label: Any, domain: Any, description: Any,
               patterns: Any, limits: Any, counters: Any, status: Any = "user-defined") -> dict[str, Any]:
        if getattr(runtime, "_pure_call_depth", 0):
            raise MagicErrorML("arcana.define() changes the catalogue; use a committed spell")
        if not isinstance(name, str) or not _NAME.fullmatch(name.strip()):
            raise TypeErrorML("arcana.define() name must begin with a letter and contain at most 64 letters, digits, spaces, underscores or hyphens")
        key = _key(name)
        known = records()
        if key in known or key.replace("_", " ") in _ALIASES:
            raise MagicErrorML(f"magical discipline '{key}' already exists or is reserved by an alias")
        if len(getattr(runtime, "custom_arcana_schools", {})) >= 64:
            raise PhysicsErrorML("a runtime can define at most 64 custom magical disciplines")
        def text(label_name: str, value: Any, max_len: int) -> str:
            if not isinstance(value, str) or not value.strip() or len(value) > max_len:
                raise TypeErrorML(f"arcana.define() {label_name} must be non-empty text up to {max_len} characters")
            return value.strip()
        def words(label_name: str, value: Any, max_count: int) -> list[str]:
            if not isinstance(value, list) or not value or len(value) > max_count or any(not isinstance(v, str) or not v.strip() or len(v) > 180 for v in value):
                raise TypeErrorML(f"arcana.define() {label_name} must be a non-empty list of up to {max_count} short text entries")
            return list(dict.fromkeys(v.strip() for v in value))
        record = {"label": text("label", label, 80), "domain": text("domain", domain, 120),
                  "description": text("description", description, 1000), "patterns": words("patterns", patterns, 64),
                  "limits": words("limits", limits, 32), "counters": words("counters", counters, 32),
                  "cost_axes": [], "status": text("status", status, 40)}
        runtime.custom_arcana_schools[key] = copy.deepcopy(record)
        runtime._observe("world.changed", operation="arcana_school_defined", school=key)
        return {"name": key, **copy.deepcopy(record)}

    define.__mana_runtime_operation__ = True

    def count() -> int:
        return len(_SCHOOLS) + len(getattr(runtime, "custom_arcana_schools", {}))

    return {"school": school, "schools": schools, "search": search, "define": define, "count": count}
