from __future__ import annotations

import copy
import difflib
import io
import json
import math
import os
import re
import stat
import sys
import threading
import traceback
import zipfile
from contextlib import contextmanager
from pathlib import Path
from itertools import count
from dataclasses import dataclass, field, fields, is_dataclass
from typing import Any

from .ast_nodes import (
    Program, Block, LoadLibrary, Literal, Name, ListLiteral, Attribute, Subscript, Unary,
    Binary, Call, Create, Assignment, ExpressionStatement, FunctionDef, Incant,
    TargetSet, TargetContext, If, While, For, Simul, Wait, After, Event, Every,
    SpellModeStatement, TuneAssignment, SkipStatement, WeaveMana, WeatherStatement,
)
from .elements import (
    ELEMENTS, FUNDAMENTAL_ELEMENTS, interaction, can_influence,
)
from .materials import (
    composition_for_material, phase_for_temperature, resolve_element, resolve_material, physical_material_profile,
    MATERIAL_DENSITIES_KG_M3, MATERIAL_DEFAULT_STATES,
)
from .errors import MagicLangError, MagicErrorML, PhysicsErrorML, RuntimeErrorML, TypeErrorML, UnitErrorML
from .physics import (
    C, PLANCK_TEMPERATURE_K, Vector3, enforce_speed, require_2d_world_vector, force as physics_force, kinetic_energy,
    momentum, pressure as physics_pressure,
)
from .physics_engine import (
    DEFAULT_TIMESTEP_SECONDS, MAX_COLLISION_PAIR_CHECKS_PER_ADVANCE,
    MAX_PHYSICS_STEPS_PER_ADVANCE, MAX_TIMESTEP_SECONDS, step_world,
)
from .units import (
    ACCELERATION, DENSITY, DIMENSIONLESS, ENERGY, FORCE, JOULES_PER_MANA, K,
    KG, M, M2, M3, MANA, MOMENTUM, PRESSURE, S, VELOCITY, Quantity,
    energy_to_mana, mana_to_energy, mana_to_matter, matter_to_mana,
)

MAX_LOOP_ITERATIONS = 1_000_000
MAX_EXECUTION_STATEMENTS = 250_000
MAX_CUMULATIVE_ALLOCATION_UNITS = 500_000
MAX_RUNTIME_CUMULATIVE_ALLOCATION_UNITS = 5_000_000
MAX_RUNTIME_CUMULATIVE_OUTPUT_CHARS = 20_000_000
MAX_SOURCE_LOCATION_ENTRIES = 300_000
MAX_WORLD_OBJECTS_PER_EXECUTION = 10_000
MAX_WORLD_OBJECTS_PER_RUNTIME = 20_000
MAX_DISPLAY_CHARS = 100_000
MAX_DISPLAY_ITEMS = 10_000
MAX_DISPLAY_DEPTH = 32
MAX_CUMULATIVE_OUTPUT_CHARS = 2_000_000
MAX_FUNCTION_DEPTH = 25
MAX_EXPRESSION_DEPTH = 256
MAX_POWER_EXPONENT = 100_000
MAX_INTEGER_RESULT_BITS = 1_000_000
MAX_COLLECTION_SIZE = 1_000_000
MAX_OBSERVER_BUFFER_RECORDS = 50_000
MAX_OBSERVER_SNAPSHOTS_PER_ADVANCE = 200
MAX_OBSERVER_ENTITIES = 300
MAX_LIBRARY_ARCHIVE_BYTES = 2_000_000
MAX_LIBRARY_ARCHIVE_MEMBERS = 128
MAX_LIBRARY_UNCOMPRESSED_BYTES = 2_000_000
MAX_LIBRARY_MANIFEST_BYTES = 64_000
MANA_EVENT_NAMES = {"impact", "collision", "damaged", "path_opened", "path_closed", "energy_arrived", "plane_created", "being_summoned", "being_returned", "being_tamed", "being_reanimated", "being_animated", "being_died", "being_revived", "being_lichified", "being_reconstituted", "blood_changed", "mana_formed", "mana_burst", "mana_emitted", "object_ignited"}
MAX_TIMER_FIRES_PER_ADVANCE = 100_000
MAX_PERSISTENCE_SECONDS = 60.0
# The four fundamental elements are created directly. Other direct elemental
# forms must match one of the registered elemental planes and be invoked first.
PLANAR_ELEMENT_NAMES = frozenset({
    "Fire", "Water", "Earth", "Air", "Ice", "Metal", "Thunder", "Life",
    "Death", "Underworld", "Holy", "Shadow", "Void",
})
NON_BASE_PLANAR_ELEMENTS = PLANAR_ELEMENT_NAMES - FUNDAMENTAL_ELEMENTS
DEFAULT_SPECIFIC_HEAT_J_PER_KG_K = 1000.0
# Editable starting-state defaults for the four fundamental elements.
ELEMENT_START_TEMPERATURE_K = {
    "Fire": 1000.0,
    "Water": 273.15,
    "Earth": 293.15,
    "Air": 288.15,
}
# Initial material failure thresholds. Values are joules per kilogram. These
# are calibration constants, not universal material measurements. Their scale
# is intentionally high enough that default object temperatures retain high
# integrity while extreme energy loads can still cause collapse.
INTEGRITY_BREAK_ENERGY_J_PER_KG = {
    "Fire": 2.0e12, "Water": 2.5e12, "Earth": 3.0e12, "Air": 1.5e12,
    "Light": 2.0e12, "Darkness": 1.5e12, "Life": 2.0e12, "Death": 1.0e12,
    "Order": 3.0e12, "Entropy": 5.0e11, "Spirit": 1.2e12, "Soul": 1.2e12,
    "Space": 1.5e12, "Time": 1.5e12, "Void": 5.0e11, "Lightning": 8.0e11,
    "Sound": 8.0e11, "Metal": 3.0e12, "Nature": 2.0e12, "Ice": 2.5e12,
    "Mud": 1.5e12, "Wood": 2.0e12, "Compound": 1.5e12, "ThermalRelease": 0.0,
}
DEFAULT_INTEGRITY_BREAK_ENERGY_J_PER_KG = 1.5e12
INTEGRITY_THRESHOLD_BONUS = {"Earth": 0.50, "Order": 0.75, "Time": 0.25}
INTEGRITY_THERMAL_FACTORS = {"Water": 0.70, "Air": 0.80, "Light": 0.85}
INTEGRITY_COLLAPSE_STABILIZERS = {"Entropy": 0.75, "Death": 0.80}
INTEGRITY_MAX_THRESHOLD_MULTIPLIER = 2.5
ENERGY_DERIVED_PROPERTIES = {
    "energy", "thermal_energy", "kinetic_energy", "momentum", "mana_energy", "bound_energy", "integrity",
    "integrity_break_energy", "integrity_energy", "integrity_last_score_j",
    "integrity_effective_energy_j", "integrity_collapsed", "collapsed_into",
    "released_energy", "released_mana", "energy_origin", "energy_sources",
    "local_released_energy", "local_released_mana", "local_energy_origin", "local_energy_sources",
}
RUNTIME_MANAGED_PROPERTIES = ENERGY_DERIVED_PROPERTIES | {
    "active", "released", "mana_used", "mana_cost", "creation_mana_cost", "acceleration_persistent",
}


@contextmanager
def _open_bounded_library_archive(path: Path, name: str):
    """Read a size-bounded archive from a single regular-file descriptor.

    The no-follow flag, where supported, prevents a symlink swap between the
    path check and open. Passing an immutable bounded byte snapshot to zipfile
    also prevents a concurrent writer from changing the archive mid-parse.
    """
    flags = os.O_RDONLY | getattr(os, "O_BINARY", 0) | getattr(os, "O_NOFOLLOW", 0)
    try:
        fd = os.open(path, flags)
    except OSError as exc:
        raise RuntimeErrorML(
            f"cannot safely open library '{name}': {exc.strerror or exc.__class__.__name__}"
        ) from exc
    try:
        with os.fdopen(fd, "rb") as handle:
            info = os.fstat(handle.fileno())
            if not stat.S_ISREG(info.st_mode):
                raise RuntimeErrorML(f"library '{name}' must be a regular .manalib file")
            if info.st_size > MAX_LIBRARY_ARCHIVE_BYTES:
                raise RuntimeErrorML(
                    f"library '{name}' exceeds the {MAX_LIBRARY_ARCHIVE_BYTES:,}-byte compressed archive limit"
                )
            data = handle.read(MAX_LIBRARY_ARCHIVE_BYTES + 1)
            if len(data) > MAX_LIBRARY_ARCHIVE_BYTES:
                raise RuntimeErrorML(
                    f"library '{name}' exceeds the {MAX_LIBRARY_ARCHIVE_BYTES:,}-byte compressed archive limit"
                )
    except OSError as exc:
        raise RuntimeErrorML(
            f"cannot safely read library '{name}': {exc.strerror or exc.__class__.__name__}"
        ) from exc
    try:
        with zipfile.ZipFile(io.BytesIO(data), "r") as archive:
            yield archive
    except zipfile.BadZipFile as exc:
        raise RuntimeErrorML(f"library '{name}' is not a valid .manalib archive") from exc


_OBJECT_IDS = count(1)
# Most world objects start from the same immutable defaults for their element.
# Reuse those templates after the first construction, copying mutable containers
# per object so lists/sets never leak state between entities.
_OBJECT_DEFAULTS_CACHE: dict[str, dict[str, Any]] = {}
_MUTABLE_DEFAULT_KEYS = ("stabilizers", "energy_sources", "local_energy_sources", "forbidden_ops")
# ``create Element`` currently creates the default 1 kg material object. Cache
# its conversion readout so mass creation does not allocate a new Quantity for
# each iteration of a large spell. If default mass ever becomes configurable,
# route that path back through matter_to_mana(obj.properties["mass"]).
_DEFAULT_CREATION_MANA_COST = matter_to_mana(Quantity(1, KG)).value
# Physical material values are centralised in magiclang.materials so conjuration,
# transmutation, the periodic table, and equipment share one catalogue.


def _clone_default_properties(properties: dict[str, Any]) -> dict[str, Any]:
    """Copy a cached default map while isolating its mutable collection values.

    The cached defaults are built only by ``MagicObject.__post_init__`` and
    always contain these keys with their documented container types. Copying
    them directly avoids repeated type-dispatch in the hot object-creation path.
    """
    clone = properties.copy()
    for key in _MUTABLE_DEFAULT_KEYS:
        clone[key] = properties[key].copy()
    return clone


@dataclass(slots=True)
class MagicObject:
    element: str
    properties: dict[str, Any] = field(default_factory=dict)
    object_id: int = field(default_factory=lambda: next(_OBJECT_IDS), init=False)

    def __post_init__(self):
        was_empty = not self.properties
        if was_empty:
            cached_defaults = _OBJECT_DEFAULTS_CACHE.get(self.element)
            if cached_defaults is not None:
                self.properties = _clone_default_properties(cached_defaults)
                return

        is_element = self.element in ELEMENTS or self.element in PLANAR_ELEMENT_NAMES
        kind = (
            "mana_construct" if self.element == "Mana"
            else "target" if self.element == "Target"
            else "element" if is_element
            else "material"
        )
        pos = Vector3(0, 0, 0, M)
        vel = Vector3(0, 0, 0, VELOCITY)
        acc = Vector3(0, 0, 0, ACCELERATION)
        direction = Vector3(1, 0, 0, DIMENSIONLESS)
        start_temp = 0.0 if self.element == "Mana" else ELEMENT_START_TEMPERATURE_K.get(self.element, 293.15)
        start_mass = Quantity(0, KG) if self.element == "Mana" else Quantity(1, KG)
        start_volume = Quantity(0, M3) if self.element == "Mana" else Quantity(1, M3)
        start_area = Quantity(0, M2) if self.element == "Mana" else Quantity(1, M2)
        start_density = Quantity(0, DENSITY) if self.element == "Mana" else Quantity(1, DENSITY)
        start_thermal_energy = start_mass.value * DEFAULT_SPECIFIC_HEAT_J_PER_KG_K * start_temp
        defaults = {
            "object_kind": kind,
            "mass": start_mass,
            "volume": start_volume,
            # The 2D world collider uses projected area; volume remains a
            # material/energy property and is available to physics libraries.
            "area": start_area,
            "density": start_density,
            "pos": pos,
            "vel": vel,
            "acc": acc,
            "force": Vector3(0, 0, 0, FORCE),
            "momentum": Vector3(0, 0, 0, MOMENTUM),
            "energy": Quantity(start_thermal_energy, ENERGY),
            "thermal_energy": Quantity(start_thermal_energy, ENERGY),
            "kinetic_energy": Quantity(0, ENERGY),
            "temp": Quantity(start_temp, K),
            "pressure": Quantity(101325, PRESSURE),
            "state": "solid",
            "material": "PureMana" if self.element == "Mana" else self.element,
            "kind": kind,
            "shape": "point",
            "combustible": False,
            "powderable": self.element not in {"Fire", "Water", "Air", "Mana", "ThermalRelease"},
            "ignition_temp": Quantity(573.15, K),
            "mana_energy": Quantity(0, ENERGY),
            # Energy transferred from a plane and bound to sustain an active
            # effect (for example, necromantic animation). This is energy, not
            # a stored mana pool or a current-plane property.
            "bound_energy": Quantity(0, ENERGY),
            "direction": direction,
            "rot": 0.0,
            "scale": 1.0,
            # 0 m means derive the collision proxy from volume. A positive value
            # explicitly overrides it. Shape labels are not exact collider geometry.
            "collision_radius": Quantity(0, M),
            "restitution": None,
            "friction": None,
            "collidable": True,
            "acceleration_persistent": True,
            "anchored": False,
            "anchor_pos": pos,
            "active": True,
            "released": False,
            "bound": False,
            "mana_used": 0.0,  # legacy field name; this is a cost readout, not a mana pool
            "mana_cost": 0.0,
            "creation_mana_cost": 0.0,
            "mana_intensity": 1.0,
            "released_energy": Quantity(0, ENERGY),
            "integrity": 1.0,
            "integrity_break_energy": Quantity(
                INTEGRITY_BREAK_ENERGY_J_PER_KG.get(self.element, DEFAULT_INTEGRITY_BREAK_ENERGY_J_PER_KG), ENERGY
            ),
            "integrity_energy": Quantity(start_thermal_energy, ENERGY),
            "integrity_last_score_j": None,
            "integrity_effective_energy_j": None,
            "integrity_collapsed": False,
            "stabilizers": [],
            "collapsed_into": None,
            "energy_origin": None,
            "energy_sources": [],
            # This object's own release is separate from energy inherited from components.
            "local_released_energy": Quantity(0, ENERGY),
            "local_released_mana": 0.0,
            "local_energy_origin": None,
            "local_energy_sources": [],
            "forbidden_ops": set(),
            "components": (),
            "hp": 100.0 if self.element == "Target" else None,
            "max_hp": 100.0 if self.element == "Target" else None,
            "defence": 0.0 if self.element == "Target" else None,
            "resist_fire": 0.0 if self.element == "Target" else None,
            "resist_water": 0.0 if self.element == "Target" else None,
            "resist_earth": 0.0 if self.element == "Target" else None,
            "resist_air": 0.0 if self.element == "Target" else None,
            "distance": Quantity(0, M) if self.element == "Target" else None,
            "targetable": True if self.element == "Target" else None,
        }
        for key, value in defaults.items():
            # Runtime-owned nullable properties must exist even before a value
            # is assigned (for example, collapsed_into is None until collapse).
            if value is not None or key in {"collapsed_into", "restitution", "friction"}:
                self.properties.setdefault(key, value)
        # Target profiles may add fields such as resist_light or range, but normal
        # elemental objects expose only defined properties. Mana is never stored.
        self.properties.pop("mana", None)
        # Objects created without an explicitly supplied state start with a coherent
        # energy ledger. Supplied composite/split states are preserved for the caller
        # to finish configuring.
        if not self.properties.get("energy_state_initialized", False):
            mass = self.properties.get("mass", Quantity(1, KG))
            temp = self.properties.get("temp", Quantity(start_temp, K))
            thermal = mass.value * DEFAULT_SPECIFIC_HEAT_J_PER_KG_K * temp.value
            vel_value = self.properties.get("vel", vel)
            kinetic = kinetic_energy(mass, vel_value) if isinstance(vel_value, Vector3) else Quantity(0, ENERGY)
            self.properties["thermal_energy"] = Quantity(max(0.0, thermal), ENERGY)
            self.properties["kinetic_energy"] = kinetic
            self.properties["momentum"] = momentum(mass, vel_value) if isinstance(vel_value, Vector3) else Vector3(0,0,0,MOMENTUM)
            released = self.properties.get("released_energy", Quantity(0, ENERGY))
            mana_energy = self.properties.get("mana_energy", Quantity(0, ENERGY))
            bound_energy = self.properties.get("bound_energy", Quantity(0, ENERGY))
            self.properties["energy"] = self.properties["thermal_energy"] + kinetic + released + mana_energy + bound_energy
            self.properties["energy_state_initialized"] = True
        # Set an initial integrity baseline for direct engine-side construction too.
        # The runtime recalculates this after configured properties/stabilizers change.
        if self.element not in {"ThermalRelease", "Mana"} and not self.properties.get("integrity_collapsed", False):
            mass = self.properties.get("mass", Quantity(1, KG))
            material = self.properties.get("material", self.element)
            mass_kg = max(0.0, mass.value) if isinstance(mass, Quantity) else 1.0
            break_per_kg = INTEGRITY_BREAK_ENERGY_J_PER_KG.get(
                material, INTEGRITY_BREAK_ENERGY_J_PER_KG.get(self.element, DEFAULT_INTEGRITY_BREAK_ENERGY_J_PER_KG)
            )
            break_energy = max(0.0, mass_kg * break_per_kg)
            energy = self.properties.get("energy", Quantity(0, ENERGY))
            energy_j = max(0.0, energy.value) if isinstance(energy, Quantity) else 0.0
            self.properties["integrity_break_energy"] = Quantity(break_energy, ENERGY)
            self.properties["integrity_energy"] = Quantity(energy_j, ENERGY)
            self.properties["integrity_last_score_j"] = energy_j
            self.properties["integrity_effective_energy_j"] = energy_j
            if break_energy <= 0:
                self.properties["integrity"] = 1.0 if energy_j <= 0 else 0.0
            elif energy_j <= 0:
                self.properties["integrity"] = 1.0
            else:
                self.properties["integrity"] = max(0.0, min(1.0, 1.0 - (energy_j / break_energy) ** (1.0 / 3.0)))

        # Cache only objects created with no caller-supplied properties. Never
        # cache custom target profiles, composites, split objects, or summon data.
        if was_empty:
            _OBJECT_DEFAULTS_CACHE[self.element] = _clone_default_properties(self.properties)

    def get(self, name: str):
        if name == "mana":
            raise RuntimeErrorML("mana is not stored on objects; inspect the spell's mana appraisal readout")
        if name not in self.properties:
            raise TypeErrorML(f"{self.element} object has no property '{name}'")
        return self.properties[name]

    def set(self, name: str, value: Any):
        if name == "mana":
            raise MagicErrorML("mana cannot be stored on a magical object")
        if name in RUNTIME_MANAGED_PROPERTIES:
            raise MagicErrorML(f"{name} is a runtime-managed property and cannot be assigned directly")
        if name not in self.properties and self.properties.get("object_kind") != "target":
            raise TypeErrorML(f"{self.element} object has no property '{name}'")
        self.properties[name] = value

    def __repr__(self):
        kind = self.properties.get("object_kind", "object")
        display_name = self.properties.get("display_name", self.element)
        return f"<{kind}:{display_name}#{self.object_id}>"


@dataclass(frozen=True, slots=True)
class ElementTypeValue:
    """A reference to an engine-registered element type, not a created object."""
    name: str

    def __repr__(self):
        return self.name


@dataclass
class FunctionValue:
    params: list[str]
    body: Block
    closure: "Environment"
    name: str = "<anonymous>"
    defaults: dict[str, Any] = field(default_factory=dict)
    library_function: bool = False
    is_spell: bool = False
    tuned_values: dict[str, Any] = field(default_factory=dict)  # legacy host field; no longer used by MANA syntax

    def __repr__(self):
        if not self.is_spell:
            return f"<function:{self.name}>"
        kind = "element-spell-template" if self.params == ["element"] else "spell"
        return f"<{kind}:{self.name}>"


@dataclass
class SpellInstance:
    """A configured instance of a reusable element-parameterized spell definition."""
    definition: FunctionValue
    element: ElementTypeValue
    name: str = "<unassigned spell instance>"
    tuned_operations: dict[tuple[str, str], Any] = field(default_factory=dict)

    def __repr__(self):
        return f"<spell-instance:{self.name} ({self.element.name})>"


@dataclass(slots=True)
class SpellChange:
    target: str
    property: str
    before: str
    after: str
    operation: str

    def __repr__(self):
        return f"{self.target}.{self.property}: {self.before} -> {self.after} ({self.operation})"


@dataclass(slots=True)
class SpellResult:
    """Execution record produced by release() or post()."""
    mode: str
    spell: str
    presentation: str = "text"
    ok: bool = True
    committed: bool = False
    incant_value: Any = None
    created: list[Any] = field(default_factory=list)
    affected: list[Any] = field(default_factory=list)
    changes: list[SpellChange] = field(default_factory=list)
    hits: list[Any] = field(default_factory=list)
    mana_used: Any = None  # retained field name; represents a calculated appraisal readout
    energy_transfers: list[dict[str, Any]] = field(default_factory=list)
    rules_fired: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    trace: list[str] = field(default_factory=list)
    report_label: str | None = None
    _created_ids: set[int] = field(default_factory=set, repr=False)

    def __repr__(self):
        status = "ok" if self.ok else "failed"
        return (f"<SpellResult {self.spell!r} mode={self.mode} {status}, "
                f"created={len(self.created)}, affected={len(self.affected)}, changes={len(self.changes)}, "
                f"hits={len(self.hits)}, mana_appraisal={self.mana_used}>")


@dataclass(slots=True)
class LibraryNamespace:
    """Read-only namespace exposing the public values of one MANA library."""
    name: str
    values: dict[str, Any]
    origin: str = "built-in"
    dependencies: tuple[str, ...] = ()

    def __repr__(self):
        return f"<MANA library {self.name} ({self.origin})>"


@dataclass
class Environment:
    values: dict[str, Any] = field(default_factory=dict)
    parent: "Environment | None" = None
    scope_boundary: bool = False

    def get(self, name: str):
        if name in self.values:
            return self.values[name]
        if self.parent is not None:
            return self.parent.get(name)
        raise RuntimeErrorML(f"'{name}' is not identified")

    def contains(self, name: str) -> bool:
        return name in self.values or (self.parent is not None and self.parent.contains(name))

    def assign(self, name: str, value: Any):
        # Control-flow blocks share the enclosing definition/module scope.
        # Assigning a new name inside `if`/`for`/`while` therefore keeps it
        # available afterwards. Assignments do not implicitly rebind outer
        # function or module names.
        target = self
        while target.parent is not None and not target.scope_boundary:
            target = target.parent
        target.values[name] = value

    def set_local(self, name: str, value: Any):
        self.values[name] = value


@dataclass(slots=True)
class IncantSignal(Exception):
    value: Any


@dataclass(slots=True)
class TimerRegistration:
    interval: float
    statement: Every
    env: Environment
    elapsed: float = 0.0
    until_next: float = 0.0
    active: bool = True


@dataclass(slots=True)
class EventRegistration:
    name: str
    statement: Event
    env: Environment
    elapsed: float = 0.0
    active: bool = True


class Runtime:
    LANGUAGE_KEYWORDS = {
        "def", "spldef", "load", "incant", "tgset", "weave", "if", "elif", "else", "while", "for", "in",
        "and", "or", "not", "true", "false", "create", "simul",
        "wait", "after", "every", "when", "skip", "tune",
    }
    RESERVED_PROPERTIES = {
        "mass", "volume", "area", "density", "pos", "vel", "acc", "force",
        "energy", "temp", "pressure", "state", "material", "mana",
        "integrity", "integrity_break_energy", "integrity_energy", "stabilizers", "bound_energy",
        "rot", "scale", "anchored", "anchor_pos", "direction", "active", "released", "bound",
        "collision_radius", "restitution", "friction", "collidable", "acceleration_persistent", "combustible",
        "powderable", "ignition_temp", "kind", "hp", "max_hp", "defence",
    }
    BUILTIN_NAMES = {
        "shape", "move", "heat", "cool", "accelerate", "decelerate", "velocity", "impulse",
        "detect", "release", "bind", "combine", "separate", "transform", "compress", "summon",
        "expand", "momentum", "kinetic_energy", "force", "pressure",
        "has_domain", "matter_to_mana", "mana_to_matter", "mana_to_energy",
        "energy_to_mana", "show", "post", "active_objects", "sqrt", "span", "length", "advance_time", "emit",
        "rotate", "scale", "push", "pull", "reflect", "split",
        "anchor", "unanchor", "dispel", "last_collisions", "conjure", "transmute", "transfigure",
        "weather", "periodic", "world", "materials", "armory", "metals", "physiology", "anatomy", "arcana",
        "point", "line", "ray", "segment", "circle", "round", "arc", "ellipse",
        "ring", "polygon", "beam", "wave", "disc", "spiral", "fan", "wall", "field",
        "dome", "cage", "chain", "tendril", "cone", "corridor", "c",
        "pi", "geometry2d", "vector3d", "planes", "elemental_planes", "hell",
        "heaven", "atlantis", "fae_paradise", "lineage_halls", "wild_realm",
        "summoning", "drafter", "necromancy", "mana", "Mana",
    }
    # check_name() is called for every assignment and function parameter. Build
    # this immutable lookup once instead of allocating and unioning several sets
    # inside every loop iteration.
    RESERVED_IDENTIFIERS = frozenset(
        LANGUAGE_KEYWORDS | RESERVED_PROPERTIES | BUILTIN_NAMES | set(ELEMENTS)
        | set(PLANAR_ELEMENT_NAMES) | {"Mana", "distance", "magnitude", "aim"}
    )

    def __init__(self, project_root: str | Path | None = None, *, observe_file: str | Path | None = None):
        self.global_env = Environment(scope_boundary=True)
        self.project_root = Path(project_root).resolve() if project_root is not None else Path.cwd().resolve()
        self.library_root = self.project_root / "libraries"
        self._library_namespaces: dict[str, LibraryNamespace] = {}
        self._libraries_loading: set[str] = set()
        self._library_load_stack: list[str] = []
        self.event_handlers: list[EventRegistration] = []
        self.timers: list[TimerRegistration] = []
        self._mana_lock = threading.RLock()
        self.total_mana_used = 0.0  # calculated readout; never a spendable pool
        self.energy_ledger: list[dict[str, Any]] = []
        # Continuous simulation exchanges are accumulated per advance_time call
        # instead of storing one Python dict per object per 60 Hz substep.
        self._continuous_energy_batch: dict[str, dict[str, dict[str, Any]]] | None = None
        self._planar_channels: dict[tuple[str, str], dict[str, Any]] = {}
        self.energy_input_j = 0.0
        self.energy_output_j = 0.0
        self.elapsed_virtual_time = 0.0
        self.last_collisions: list[dict[str, Any]] = []
        # Environment is world state, not spell state. Weather controls update
        # these parameters; advance_time applies them to physics and materials.
        self.environment_state: dict[str, Any] = {
            "kind": "clear", "intensity": 0.0, "precipitation": "none",
            "wind_speed_mps": 0.0, "wind_x_mps": 0.0, "wind_y_mps": 0.0,
            "wind_direction_name": "east", "wind": 0.0, "wind_direction": 1.0,
            "temperature_k": 293.15, "humidity": 0.45, "clouds": 0.0, "fog": 0.0,
            "heat": 0.0, "lightning": 0.0, "started_at": 0.0, "until": None,
            "duration": None, "indefinite": True,
        }
        # Local climate zones overlay the global climate only inside their radius.
        # Newest matching zones take precedence; expired zones are pruned during
        # world stepping and state snapshots so preview/release remain transactional.
        self.weather_regions: list[dict[str, Any]] = []
        self._next_weather_region_id = 1
        # Magnetism is a bounded world field, distinct from a one-shot push/pull.
        self.magnetic_fields: list[dict[str, Any]] = []
        self._next_magnetic_field_id = 1
        # User-defined alloys and item forms belong to one world/runtime, never
        # to process-global registries that could leak between projects.
        self.custom_material_profiles: dict[str, dict[str, Any]] = {}
        self.custom_item_blueprints: dict[str, dict[str, Any]] = {}
        self.custom_body_forms: dict[str, dict[str, Any]] = {}
        # Anatomy catalogues and user-defined species/structures are scoped to one Runtime.
        self.custom_anatomy_species: dict[str, dict[str, Any]] = {}
        self.custom_anatomy_organs: dict[str, dict[str, Any]] = {}
        self.custom_anatomy_systems: dict[str, dict[str, Any]] = {}
        self.custom_arcana_schools: dict[str, dict[str, Any]] = {}
        # The global world-law settings are independent of individual spells.
        # A zero-gravity default preserves MANA's established 2D world unless a
        # project explicitly enables gravity through world.configure().
        self.world_settings = {
            "gravity": Vector3(0, 0, 0, ACCELERATION), "air_density_kg_m3": 1.225,
            "default_restitution": 0.2, "friction_coefficient": 0.35, "drag_enabled": True,
            "thermal_exchange_enabled": True, "phase_changes_enabled": True,
            "wetting_enabled": True,
        }
        self._spell_run_stack: list[SpellResult] = []
        self._spell_instance_stack: list[SpellInstance | None] = []
        self._target_context_stack: list[MagicObject] = []
        self._function_depth = 0
        self._pure_call_depth = 0
        self._stop_requested = threading.Event()
        self._source_locations: dict[int, tuple[str, int, int]] = {}
        # Keep only the last few parsed programs for repeated embedded runs and
        # diagnostics. Their source maps stay usable without retaining every
        # historical editor buffer forever.
        self._recent_programs: list[Program] = []
        # Host applications may reuse a Runtime for many editor runs. These
        # lifetime quotas stop repeated individually-small runs growing retained
        # allocations/output indefinitely.
        self._runtime_allocation_units = 0
        self._runtime_output_chars = 0
        self._diagnostic_context = threading.local()
        self._evaluation_context = threading.local()
        # Shared across nested functions, spells and loops for one top-level run.
        # This prevents individually-small allocations or loops from multiplying
        # into an unbounded process allocation. Runtime instances also have a
        # lifetime world-object cap for repeated embedded executions.
        self._budget_context = threading.local()
        self._world_object_ids_seen: set[int] = set()
        self.trace_detail = os.environ.get("MANA_TRACE_DETAIL", "full").strip().lower()
        if self.trace_detail not in {"summary", "full"}:
            self.trace_detail = "summary"
        # Objects committed by release() live here even with no graphical world engine.
        self.active_objects: list[MagicObject] = []
        self._install_builtins()
        # Pure-mana tools are part of the core language experience. The namespace
        # is available without an explicit load; `load mana` is also accepted.
        from .libraries.mana import build_library as build_mana_library
        mana_namespace = LibraryNamespace("mana", build_mana_library(self), "built-in", ())
        self.global_env.set_local("mana", mana_namespace)
        from .libraries.weather import build_library as build_weather_library
        weather_namespace = LibraryNamespace("weather", build_weather_library(self), "built-in", ())
        self.global_env.set_local("weather", weather_namespace)
        from .libraries.periodic import build_library as build_periodic_library
        periodic_namespace = LibraryNamespace("periodic", build_periodic_library(), "built-in", ())
        self.global_env.set_local("periodic", periodic_namespace)
        from .libraries.world import build_library as build_world_library
        world_namespace = LibraryNamespace("world", build_world_library(self), "built-in", ())
        self.global_env.set_local("world", world_namespace)
        self.caster_position = Vector3(0, 0, 0, M)
        self.observer = None
        self._observer_buffers: list[list[tuple[str, float, dict[str, Any]]]] = []
        self._observer_buffer_drops: list[int] = []
        if observe_file is not None:
            from .observe import ObservationRecorder
            self.observer = ObservationRecorder(Path(observe_file))
            self._observe("session.started", source_version=(self.project_root / "VERSION").read_text(encoding="utf-8").strip() if (self.project_root / "VERSION").is_file() else "unknown")

    def close_observer(self) -> None:
        """Close an optional recording. No observer is created for normal runs."""
        observer, self.observer = self.observer, None
        if observer is not None:
            observer.close()

    def _observe(self, event_type: str, **payload) -> None:
        """Queue or write a best-effort observation without changing world state."""
        if self.observer is None:
            return
        if self._spell_run_stack:
            current_result = self._spell_run_stack[-1]
            payload.setdefault("mode", current_result.mode)
            payload.setdefault("spell", current_result.spell)
            if current_result.mode == "post":
                payload.setdefault("presentation", current_result.presentation)
        record = (event_type, self.elapsed_virtual_time, payload)
        if self._observer_buffers:
            buffer = self._observer_buffers[-1]
            if len(buffer) >= MAX_OBSERVER_BUFFER_RECORDS:
                self._observer_buffer_drops[-1] += 1
                return
            buffer.append(record)
        else:
            self.observer.write(*record)

    def _finish_observer_buffer(
        self,
        records: list[tuple[str, float, dict[str, Any]]],
        *,
        commit: bool,
        dropped: int = 0,
    ) -> None:
        """Commit bounded telemetry only when the surrounding simulation commits."""
        if not commit or self.observer is None:
            return
        if self._observer_buffers:
            parent = self._observer_buffers[-1]
            available = max(0, MAX_OBSERVER_BUFFER_RECORDS - len(parent))
            parent.extend(records[:available])
            overflow = max(0, len(records) - available) + dropped
            self._observer_buffer_drops[-1] += overflow
            return
        for record in records:
            self.observer.write(*record)
        if dropped:
            self.observer.write(
                "recording.notice",
                self.elapsed_virtual_time,
                {"message": "Some observation events were omitted to keep memory bounded.", "dropped_events": dropped},
            )

    def _begin_observer_buffer(self) -> list[tuple[str, float, dict[str, Any]]] | None:
        """Start a nested telemetry transaction when recording is enabled."""
        if self.observer is None:
            return None
        records: list[tuple[str, float, dict[str, Any]]] = []
        self._observer_buffers.append(records)
        self._observer_buffer_drops.append(0)
        return records

    def _end_observer_buffer(
        self,
        records: list[tuple[str, float, dict[str, Any]]] | None,
        *,
        keep_world_events: bool,
    ) -> None:
        """Finish a telemetry transaction, hiding changes from failed releases."""
        if records is None or self.observer is None:
            return
        if not self._observer_buffers or self._observer_buffers[-1] is not records:
            raise RuntimeErrorML("internal Visualiser observation buffer order is invalid")
        self._observer_buffers.pop()
        dropped = self._observer_buffer_drops.pop()
        if not keep_world_events:
            # Preserve the attempt and result for debugging, plus only the final
            # snapshot after the runtime has restored the pre-cast world. Earlier
            # contacts/effects from a failed release were never committed.
            tail_snapshot = next(
                (record for record in reversed(records)
                 if record[0] == "scene.snapshot" and record[2].get("reason", "").startswith("after_")),
                None,
            )
            records = [
                record for record in records
                if record[0] in {"spell.started", "spell.result", "spell.crashed", "preview.output"}
                or record is tail_snapshot
            ]
        self._finish_observer_buffer(records, commit=True, dropped=dropped)

    def _visual_entity(self, obj: MagicObject) -> dict[str, Any]:
        props = obj.properties
        position = props.get("pos")
        pos = [float(position.x), float(position.y)] if isinstance(position, Vector3) else None
        radius = props.get("collision_radius")
        if isinstance(radius, Quantity) and radius.dimension == M:
            radius_m = radius.value
        else:
            area = props.get("area")
            radius_m = math.sqrt(max(0.0, area.value) / math.pi) if isinstance(area, Quantity) and area.dimension == M2 else 0.22
        threshold = props.get("integrity_break_energy")
        threshold_j = threshold.value if isinstance(threshold, Quantity) and threshold.value > 0 else 1.0e8
        kinetic = props.get("kinetic_energy")
        thermal = props.get("thermal_energy")
        temp = props.get("temp")
        released = props.get("released_energy")
        bound = props.get("bound_energy")
        woven = props.get("mana_energy")
        # A visual-only intensity derived from the engine's calculated energy. For
        # matter, ignore its ordinary starting heat so a cold stone does not glow
        # just because it exists; velocity, extra heat, released energy and bound
        # energy all contribute. Woven constructs use their own effect energy.
        # The logarithmic curve is deliberately cosmetic and never affects physics.
        energy_for_glow = 0.0
        if obj.element == "Mana":
            energy_for_glow = woven.value if isinstance(woven, Quantity) else 0.0
        else:
            if isinstance(kinetic, Quantity):
                energy_for_glow += max(0.0, kinetic.value)
            if isinstance(thermal, Quantity):
                mass = props.get("mass")
                mass_kg = mass.value if isinstance(mass, Quantity) and mass.dimension == KG else 0.0
                baseline_temp = ELEMENT_START_TEMPERATURE_K.get(obj.element, 293.15)
                baseline_heat = max(0.0, mass_kg * DEFAULT_SPECIFIC_HEAT_J_PER_KG_K * baseline_temp)
                energy_for_glow += max(0.0, thermal.value - baseline_heat)
            if isinstance(released, Quantity):
                energy_for_glow += max(0.0, released.value)
            if isinstance(bound, Quantity):
                energy_for_glow += max(0.0, bound.value)
        glow_denominator = math.log1p(max(1.0, threshold_j))
        energy_glow = max(0.0, min(1.0, math.log1p(max(0.0, energy_for_glow)) / glow_denominator))
        return {
            "id": obj.object_id,
            "name": str(props.get("display_name") or obj.element),
            "element": obj.element,
            "kind": str(props.get("object_kind", "material")),
            "shape": str(props.get("shape", "circle")),
            "visual_form": str(props.get("visual_form", "")),
            "state": str(props.get("state", "solid")),
            "material": str(props.get("material", obj.element)),
            "position": pos,
            "radius_m": float(radius_m),
            "active": bool(props.get("active", True)),
            "collidable": bool(props.get("collidable", True)),
            "anchored": bool(props.get("anchored", False)),
            "hp": props.get("hp"),
            "max_hp": props.get("max_hp"),
            "integrity": props.get("integrity"),
            "energy_glow": energy_glow,
            "temperature_k": temp.value if isinstance(temp, Quantity) and math.isfinite(temp.value) else None,
            "mass_kg": props.get("mass").value if isinstance(props.get("mass"), Quantity) and props["mass"].dimension == KG else None,
            "volume_m3": props.get("volume").value if isinstance(props.get("volume"), Quantity) and props["volume"].dimension == M3 else None,
            "density_kg_m3": props.get("density").value if isinstance(props.get("density"), Quantity) and props["density"].dimension == DENSITY else None,
            "wetness": float(props.get("wetness", 0.0)),
            "dust_coating": float(props.get("dust_coating", 0.0)),
            "kinetic_energy_j": kinetic.value if isinstance(kinetic, Quantity) and math.isfinite(kinetic.value) else None,
            "thermal_energy_j": thermal.value if isinstance(thermal, Quantity) and math.isfinite(thermal.value) else None,
            "tamed": bool(props.get("is_tamed", False)),
            "summoned": bool(props.get("is_summoned", False)),
            "undead": bool(props.get("is_undead", False)),
            "living": bool(props.get("living", props.get("object_kind") == "being")),
            "created_by_conjure": bool(props.get("created_by_conjure", False)),
            "composition": props.get("composition"),
            "atomic_number": props.get("atomic_number"),
            "element_symbol": props.get("element_symbol"),
            "melting_point_k": props.get("melting_point_k"),
            "boiling_point_k": props.get("boiling_point_k"),
            "estimated_material_data": bool(props.get("estimated_material_data", False)),
            "visual_scale": float(props.get("visual_scale", 1.0)),
            # Lightweight species metadata lets the optional visualiser choose
            # a suitable generic silhouette without loading anatomy into the renderer.
            "species": str(props.get("species", ""))[:120],
            "anatomy_species_id": str(props.get("anatomy_species_id", ""))[:120],
            "body_form": str(props.get("body_form", ""))[:120],
            "skeleton_type": str(props.get("skeleton_type", ""))[:80],
        }

    def _observed_objects(self, limit: int | None = None) -> list[MagicObject]:
        """Collect objects for a snapshot, optionally stopping at a safe upper bound."""
        found: dict[int, MagicObject] = {}
        seen: set[int] = set()

        def has_room() -> bool:
            return limit is None or len(found) < limit

        def walk(value):
            if not has_room() or value is None:
                return
            marker = id(value)
            if marker in seen:
                return
            if isinstance(value, MagicObject):
                found[value.object_id] = value
                seen.add(marker)
                return
            if isinstance(value, dict):
                seen.add(marker)
                for item in value.values():
                    if not has_room():
                        break
                    walk(item)
            elif isinstance(value, (list, tuple, set)):
                seen.add(marker)
                for item in value:
                    if not has_room():
                        break
                    walk(item)
            elif isinstance(value, Environment):
                seen.add(marker)
                for item in value.values.values():
                    if not has_room():
                        break
                    walk(item)
            elif isinstance(value, FunctionValue):
                seen.add(marker)
                walk(value.closure)
            elif isinstance(value, SpellInstance):
                seen.add(marker)
                walk(value.definition)
                walk(value.element)
                for item in value.tuned_operations.values():
                    if not has_room():
                        break
                    walk(item)

        # Prefer the objects already materialised in the world. With huge user
        # scopes this avoids walking every historical variable just to draw a
        # bounded snapshot.
        walk(self.active_objects)
        if len(found) < (limit if limit is not None else float("inf")):
            walk(self.global_env)
        return sorted(found.values(), key=lambda item: item.object_id)
    def _observer_value(self, value):
        if isinstance(value, MagicObject):
            return {"entity_id": value.object_id, "name": self._object_label(value), "element": value.element}
        if isinstance(value, Quantity):
            return {"value": value.value, "unit": str(value.dimension)}
        if isinstance(value, Vector3):
            return {"vector": [value.x, value.y, value.z], "unit": str(value.dimension)}
        if isinstance(value, (str, int, float, bool)) or value is None:
            return value
        if isinstance(value, (list, tuple)):
            return [self._observer_value(item) for item in value[:100]]
        if isinstance(value, dict):
            return {str(key): self._observer_value(item) for key, item in list(value.items())[:100]}
        return str(value)[:300]

    def _observe_scene(self, reason: str, *, mode: str | None = None, presentation: str | None = None) -> None:
        if self.observer is None:
            return
        max_entities = MAX_OBSERVER_ENTITIES
        # Collect one extra item to detect truncation without scanning a million
        # objects on every snapshot. The displayed count is explicitly a lower
        # bound when the collection stops early.
        objects = self._observed_objects(limit=max_entities + 1)
        truncated = len(objects) > max_entities
        entities = [self._visual_entity(obj) for obj in objects[:max_entities]]
        payload = {
            "reason": reason,
            "entities": entities,
            "entity_count": len(objects),
            "entity_count_exact": not truncated,
            "truncated": truncated,
            "environment": dict(self.environment_state),
        }
        # _run_spell_mode emits its final snapshot after restoring the world and
        # popping the spell stack. Pass the presentation explicitly so playback
        # can distinguish the real restored world from a visual-only preview.
        if mode is not None:
            payload["mode"] = mode
        if presentation is not None:
            payload["presentation"] = presentation
        self._observe("scene.snapshot", **payload)

    def _install_builtins(self):
        builtins = {
            "shape": self.op_shape,
            "move": self.op_move,
            "heat": self.op_heat,
            "cool": self.op_cool,
            "accelerate": self.op_accelerate,
            "decelerate": self.op_decelerate,
            "velocity": self.op_velocity,
            "impulse": self.op_impulse,
            "detect": self.op_detect,
            "bind": self.op_bind,
            "combine": self.op_combine,
            "separate": self.op_separate,
            "transform": self.op_transform,
            "compress": self.op_compress,
            "expand": self.op_expand,
            "momentum": self.op_momentum,
            "kinetic_energy": self.op_kinetic_energy,
            "force": self.op_force,
            "pressure": self.op_pressure,
            "has_domain": self.op_has_domain,
            "matter_to_mana": self.op_matter_to_mana,
            "mana_to_matter": self.op_mana_to_matter,
            "mana_to_energy": self.op_mana_to_energy,
            "energy_to_mana": self.op_energy_to_mana,
            "advance_time": self.advance_time,
            "emit": self.emit_event,
            "show": self.op_show,
            "active_objects": self.op_active_objects,
            "rotate": self.op_rotate,
            "scale": self.op_scale,
            "push": self.op_push,
            "pull": self.op_pull,
            "reflect": self.op_reflect,
            "split": self.op_split,
            "anchor": self.op_anchor,
            "unanchor": self.op_unanchor,
            "dispel": self.op_dispel,
            "last_collisions": self.op_last_collisions,
            "conjure": self.op_conjure,
            "summon": self.op_summon,
            "transmute": self.op_transmute,
            "transfigure": self.op_transfigure,
            "sqrt": self.op_sqrt,
            "span": self.safe_span,
            "length": self.safe_length,
        }
        for name, fn in builtins.items():
            self.global_env.set_local(name, fn)
        self.global_env.set_local("c", Quantity(C, VELOCITY))
        self.global_env.set_local("pi", math.pi)
        for name in (
            # No dedicated 3D-shape catalogue. These are useful 2D/functional forms.
            "point", "line", "ray", "segment", "circle", "round", "arc", "ellipse",
            "ring", "polygon", "beam", "wave", "disc", "spiral", "fan", "wall",
            "field", "dome", "cage", "chain", "tendril", "cone", "corridor",
            "sphere", "ball", "projectile", "barrier", "shield",
        ):
            self.global_env.set_local(name, name)

    def _load_library(self, name: str, importing_env: Environment | None = None) -> LibraryNamespace:
        if name in self._libraries_loading:
            try:
                start = self._library_load_stack.index(name)
                cycle = self._library_load_stack[start:] + [name]
            except ValueError:
                cycle = self._library_load_stack + [name]
            raise RuntimeErrorML("library load cycle detected: " + " -> ".join(cycle))
        if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", name):
            raise RuntimeErrorML(f"invalid library name '{name}'")

        builtin_dependencies = {
            "elemental_planes": ("planes",),
            "hell": ("planes",),
            "heaven": ("planes",),
            "atlantis": ("planes",),
            "fae_paradise": ("planes",),
            "lineage_halls": ("planes",),
            "wild_realm": ("planes",),
            "drafter": ("planes",),
            "summoning": ("planes",),
            "necromancy": ("planes",),
        }

        def ensure_dependencies(dependencies: tuple[str, ...] | list[str]) -> None:
            if importing_env is None:
                return  # internal lazy loads from a library already loaded
            for dependency in dependencies:
                if not importing_env.contains(dependency):
                    raise RuntimeErrorML(f"library {name} needs {dependency} loaded first")

        if name in self._library_namespaces:
            namespace = self._library_namespaces[name]
            ensure_dependencies(namespace.dependencies or builtin_dependencies.get(name, ()))
            return namespace

        if name in {"geometry2d", "vector3d", "planes", "mana", "weather", "periodic", "materials", "armory", "metals", "physiology", "anatomy", "arcana", "drafter", "summoning", "necromancy"} or name in builtin_dependencies:
            dependencies = builtin_dependencies.get(name, ())
            ensure_dependencies(dependencies)
            if name == "geometry2d":
                from .libraries.geometry2d import build_library
                namespace = LibraryNamespace(name, build_library(self), "built-in", tuple(dependencies))
            elif name == "vector3d":
                from .libraries.three_d import build_library
                namespace = LibraryNamespace(name, build_library(), "built-in", tuple(dependencies))
            elif name == "planes":
                from .libraries.planes import build_library
                namespace = LibraryNamespace(name, build_library(self), "built-in", tuple(dependencies))
            elif name == "mana":
                from .libraries.mana import build_library
                namespace = LibraryNamespace(name, build_library(self), "built-in", tuple(dependencies))
            elif name == "weather":
                from .libraries.weather import build_library
                namespace = LibraryNamespace(name, build_library(self), "built-in", tuple(dependencies))
            elif name == "periodic":
                from .libraries.periodic import build_library
                namespace = LibraryNamespace(name, build_library(), "built-in", tuple(dependencies))
            elif name == "materials":
                from .libraries.materials import build_library
                namespace = LibraryNamespace(name, build_library(self), "built-in", tuple(dependencies))
            elif name == "armory":
                from .libraries.armory import build_library
                namespace = LibraryNamespace(name, build_library(self), "built-in", tuple(dependencies))
            elif name == "metals":
                from .libraries.metals import build_library
                namespace = LibraryNamespace(name, build_library(self), "built-in", tuple(dependencies))
            elif name == "physiology":
                from .libraries.physiology import build_library
                namespace = LibraryNamespace(name, build_library(self), "built-in", tuple(dependencies))
            elif name == "anatomy":
                from .libraries.anatomy import build_library
                namespace = LibraryNamespace(name, build_library(self), "built-in", tuple(dependencies))
            elif name == "arcana":
                from .libraries.arcana import build_library
                namespace = LibraryNamespace(name, build_library(self), "built-in", tuple(dependencies))
            elif name == "world":
                from .libraries.world import build_library
                namespace = LibraryNamespace(name, build_library(self), "built-in", tuple(dependencies))
            elif name == "drafter":
                from .libraries.drafter import build_library
                namespace = LibraryNamespace(name, build_library(self), "built-in", tuple(dependencies))
            elif name == "summoning":
                from .libraries.summoning import build_library
                namespace = LibraryNamespace(name, build_library(self), "built-in", tuple(dependencies))
            elif name == "necromancy":
                from .libraries.necromancy import build_library
                namespace = LibraryNamespace(name, build_library(self), "built-in", tuple(dependencies))
            else:
                # Import just the requested data module. In particular, asking for
                # Atlantis must not import the Wild Realm or every other plane's
                # potentially large being catalogue as a side effect.
                from importlib import import_module
                data_module = import_module(f".libraries.plane_data.{name}", package=__package__)
                namespace = LibraryNamespace(name, data_module.build_library(self), "built-in plane data", tuple(dependencies))
            self._library_namespaces[name] = namespace
            return namespace

        reserved_names = (
            self.LANGUAGE_KEYWORDS | self.BUILTIN_NAMES | self.RESERVED_PROPERTIES
            | set(ELEMENTS) | {"system", "python", "os", "sys", "subprocess", "c", "pi"}
        )
        if name in reserved_names or name in {"distance", "magnitude", "aim"}:
            raise RuntimeErrorML(f"library name '{name}' is reserved by the MANA language or built-in API")
        package_path = self.library_root / f"{name}.manalib"
        if not package_path.is_file():
            raise RuntimeErrorML(
                f"library '{name}' is not available; built-in libraries are geometry2d, vector3d, planes, "
                "elemental_planes, hell, heaven, atlantis, fae_paradise, lineage_halls, and wild_realm. "
                f"User libraries must be packaged as libraries/{name}.manalib"
            )
        try:
            resolved_library_root = self.library_root.resolve()
            resolved_package = package_path.resolve(strict=True)
        except OSError as exc:
            raise RuntimeErrorML(f"cannot inspect library package '{name}': {exc.strerror or exc.__class__.__name__}") from exc
        if resolved_package.parent != resolved_library_root:
            raise RuntimeErrorML(f"library '{name}' must be a regular .manalib file inside the project libraries directory")
        package_path = resolved_package

        self._libraries_loading.add(name)
        self._library_load_stack.append(name)
        try:
            with _open_bounded_library_archive(package_path, name) as archive:
                infos = archive.infolist()
                if len(infos) > MAX_LIBRARY_ARCHIVE_MEMBERS:
                    raise RuntimeErrorML(
                        f"library '{name}' exceeds the {MAX_LIBRARY_ARCHIVE_MEMBERS}-member archive limit"
                    )
                member_names = [info.filename for info in infos]
                if len(member_names) != len(set(member_names)):
                    raise RuntimeErrorML(f"library '{name}' contains duplicate archive member names")
                total_uncompressed = sum(info.file_size for info in infos)
                if total_uncompressed > MAX_LIBRARY_UNCOMPRESSED_BYTES:
                    raise RuntimeErrorML(
                        f"library '{name}' exceeds the {MAX_LIBRARY_UNCOMPRESSED_BYTES}-byte uncompressed size limit"
                    )
                bad_member = archive.testzip()
                if bad_member is not None:
                    raise RuntimeErrorML(f"library package '{name}' is corrupt at {bad_member}")
                try:
                    manifest_info = archive.getinfo("mana-library.json")
                    if manifest_info.file_size > MAX_LIBRARY_MANIFEST_BYTES:
                        raise RuntimeErrorML(
                            f"library '{name}' manifest exceeds the {MAX_LIBRARY_MANIFEST_BYTES:,}-byte safety limit"
                        )
                    manifest_bytes = archive.read("mana-library.json")
                    manifest = json.loads(manifest_bytes.decode("utf-8-sig"))
                except RuntimeErrorML:
                    raise
                except (KeyError, UnicodeDecodeError, json.JSONDecodeError, RecursionError) as exc:
                    raise RuntimeErrorML(f"library '{name}' has no valid or safely nested mana-library.json manifest") from exc
                if not isinstance(manifest, dict):
                    raise RuntimeErrorML(f"library '{name}' manifest must be a JSON object")
                if manifest.get("format") != "manalib" or manifest.get("format_version") != 1:
                    raise RuntimeErrorML(f"library '{name}' has an unsupported package format")
                if manifest.get("name") != name:
                    raise RuntimeErrorML(f"library manifest name does not match loaded name '{name}'")
                dependencies = manifest.get("dependencies", [])
                if not isinstance(dependencies, list) or any(
                    not isinstance(item, str) or not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", item)
                    for item in dependencies
                ) or len(dependencies) != len(set(dependencies)):
                    raise RuntimeErrorML(f"library '{name}' manifest dependencies must be a unique list of library names")
                ensure_dependencies(tuple(dependencies))
                entry = manifest.get("entry", "main.mana")
                if not isinstance(entry, str):
                    raise RuntimeErrorML(f"library '{name}' manifest entry must be a relative path string")
                entry_parts = entry.replace("\\", "/").split("/")
                if (not isinstance(entry, str) or Path(entry).is_absolute()
                        or entry.startswith(("/", "\\")) or re.match(r"^[A-Za-z]:", entry)
                        or ".." in entry_parts):
                    raise RuntimeErrorML(f"library '{name}' has an unsafe entry path")
                try:
                    source = archive.read(entry).decode("utf-8-sig")
                except (KeyError, UnicodeDecodeError) as exc:
                    raise RuntimeErrorML(f"library '{name}' is missing its UTF-8 MANA entry file '{entry}'") from exc
                from .lexer import Lexer
                from .parser import Parser
                program = Parser(Lexer(source, f"{package_path}!/{entry}").tokenize(),
                                 f"{package_path}!/{entry}", allow_library_parameters=True).parse()
                if len(self._source_locations) + len(program.locations) > MAX_SOURCE_LOCATION_ENTRIES:
                    raise RuntimeErrorML(
                        f"runtime reached the source-location safety limit ({MAX_SOURCE_LOCATION_ENTRIES:,} entries)"
                    )
                self._source_locations.update(program.locations)
                allowed = (FunctionDef, LoadLibrary, SkipStatement)
                if any(
                    not isinstance(statement, allowed)
                    or (isinstance(statement, FunctionDef) and statement.is_spell)
                    for statement in program.statements
                ):
                    raise RuntimeErrorML(
                        f"library '{name}' entry files may contain only ordinary def functions, load statements, and skip at top level"
                    )
                export_names = manifest.get("exports")
                if not isinstance(export_names, list) or not export_names or any(
                    not isinstance(item, str) or not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", item)
                    for item in export_names
                ):
                    raise RuntimeErrorML(f"library '{name}' manifest must list one or more valid exported names")
                defined_names = {
                    statement.name for statement in program.statements
                    if isinstance(statement, FunctionDef) and not statement.is_spell
                }
                missing_exports = sorted(set(export_names) - defined_names)
                if missing_exports:
                    raise RuntimeErrorML(f"library '{name}' exports undefined names: {', '.join(missing_exports)}")
                module_env = Environment(parent=self.global_env, scope_boundary=True)
                self.exec_block(Block(program.statements), module_env)
                values = {export: module_env.get(export) for export in export_names}
                namespace = LibraryNamespace(name, values, str(package_path), tuple(dependencies))
                self._library_namespaces[name] = namespace
                return namespace
        except zipfile.BadZipFile as exc:
            raise RuntimeErrorML(f"library '{name}' is not a valid .manalib archive") from exc
        finally:
            self._libraries_loading.discard(name)
            if self._library_load_stack and self._library_load_stack[-1] == name:
                self._library_load_stack.pop()
            elif name in self._library_load_stack:
                self._library_load_stack.remove(name)

    def request_stop(self) -> None:
        """Request cooperative cancellation at the next MANA statement boundary."""
        self._stop_requested.set()

    @property
    def stop_requested(self) -> bool:
        return self._stop_requested.is_set()

    def _check_stop_requested(self) -> None:
        if self._stop_requested.is_set():
            raise RuntimeErrorML("execution stopped by user")

    def execute(self, program: Program) -> Any:
        owns_budget = getattr(self._budget_context, "state", None) is None
        if owns_budget:
            self._budget_context.state = {
                "statements": 0,
                "allocations": 0,
                "world_objects": 0,
                "world_ids": set(),
                "output_chars": 0,
            }
            self._recent_programs.append(program)
            del self._recent_programs[:-4]
            self._prune_source_locations()
        try:
            if len(self._source_locations) + len(program.locations) > MAX_SOURCE_LOCATION_ENTRIES:
                self._prune_source_locations()
                if len(self._source_locations) + len(program.locations) > MAX_SOURCE_LOCATION_ENTRIES:
                    raise RuntimeErrorML(
                        f"runtime reached the source-location safety limit ({MAX_SOURCE_LOCATION_ENTRIES:,} entries)"
                    )
            self._source_locations.update(program.locations)
            if self.observer is not None:
                self._observe("program.started", filename=program.filename)
            result = self.exec_block(Block(program.statements), self.global_env)
            if self.observer is not None:
                self._observe_scene("program.completed")
                self._observe("program.completed", filename=program.filename)
            return result
        finally:
            if owns_budget:
                self._budget_context.state = None
                self._prune_source_locations()

    def _prune_source_locations(self) -> None:
        """Drop source maps for old snippets unless a retained MANA function needs them."""
        live_ast_ids: set[int] = set()
        seen: set[int] = set()

        def walk(value: Any) -> None:
            if value is None or isinstance(value, (str, bytes, int, float, bool)):
                return
            identity = id(value)
            if identity in seen:
                return
            seen.add(identity)
            if isinstance(value, Environment):
                for child in value.values.values():
                    walk(child)
                walk(value.parent)
                return
            if isinstance(value, FunctionValue):
                walk(value.body)
                walk(value.defaults)
                walk(value.closure)
                return
            if isinstance(value, SpellInstance):
                walk(value.definition)
                walk(value.tuned_operations)
                return
            if isinstance(value, LibraryNamespace):
                walk(value.values)
                return
            if isinstance(value, MagicObject):
                # Object properties are world data; a language function is not
                # permitted as a property through normal assignment, so only
                # inspect values defensively rather than traversing host internals.
                walk(value.properties)
                return
            if isinstance(value, dict):
                for child in value.values():
                    walk(child)
                return
            if isinstance(value, (list, tuple, set, frozenset)):
                for child in value:
                    walk(child)
                return
            if is_dataclass(value) and value.__class__.__module__.endswith(".ast_nodes"):
                live_ast_ids.add(identity)
                for item in fields(value):
                    walk(getattr(value, item.name))

        walk(self.global_env)
        walk(self._library_namespaces)
        walk(self._recent_programs)
        if self._source_locations:
            self._source_locations = {
                identity: location for identity, location in self._source_locations.items()
                if identity in live_ast_ids
            }

    def _charge_allocation(self, amount: int, kind: str = "collection") -> None:
        """Charge both per-run and runtime-lifetime container growth before allocation."""
        if amount <= 0:
            return
        state = getattr(self._budget_context, "state", None)
        if state is None:
            return
        updated = state["allocations"] + amount
        runtime_updated = self._runtime_allocation_units + amount
        if updated > MAX_CUMULATIVE_ALLOCATION_UNITS:
            raise RuntimeErrorML(
                f"program exceeded the cumulative allocation safety limit "
                f"({MAX_CUMULATIVE_ALLOCATION_UNITS:,} {kind} units)"
            )
        if runtime_updated > MAX_RUNTIME_CUMULATIVE_ALLOCATION_UNITS:
            raise RuntimeErrorML(
                f"runtime exceeded its cumulative allocation safety limit "
                f"({MAX_RUNTIME_CUMULATIVE_ALLOCATION_UNITS:,} {kind} units)"
            )
        state["allocations"] = updated
        self._runtime_allocation_units = runtime_updated

    def _charge_statement(self) -> None:
        state = getattr(self._budget_context, "state", None)
        if state is None:
            return
        state["statements"] += 1
        if state["statements"] > MAX_EXECUTION_STATEMENTS:
            raise RuntimeErrorML(
                f"program exceeded the execution statement budget ({MAX_EXECUTION_STATEMENTS:,})"
            )

    def exec_block(self, block: Block, env: Environment):
        result = None
        for stmt in block.statements:
            result = self.exec_stmt(stmt, env)
        return result

    def exec_stmt(self, stmt, env):
        self._check_stop_requested()
        self._charge_statement()
        previous = getattr(self._diagnostic_context, "location", None)
        location = self._source_locations.get(id(stmt))
        if location is not None:
            self._diagnostic_context.location = location
        try:
            return self._exec_stmt_impl(stmt, env)
        except MagicLangError as exc:
            active_location = getattr(self._diagnostic_context, "location", None)
            if active_location is not None:
                exc.attach_location(*active_location)
            raise
        finally:
            self._diagnostic_context.location = previous

    def _exec_stmt_impl(self, stmt, env):
        if self._pure_call_depth and isinstance(
            stmt, (LoadLibrary, SpellModeStatement, TuneAssignment, TargetSet, TargetContext,
                   Simul, Wait, After, Every)
        ):
            raise MagicErrorML(
                "a directly called definition must be pure; move world-changing or scheduling statements into a spell "
                "and execute it with post() or release()"
            )
        if isinstance(stmt, LoadLibrary):
            namespace = self._load_library(stmt.name, env)
            env.set_local(stmt.name, namespace)
            return namespace

        if isinstance(stmt, SpellModeStatement):
            if self._pure_call_depth:
                raise MagicErrorML("a directly called definition must be pure; use post() or release() to execute a spell")
            spell = env.get(stmt.spell.name)
            if not isinstance(spell, (FunctionValue, SpellInstance)):
                raise TypeErrorML(f"{stmt.mode}({stmt.spell.name}) expects a named spell or configured spell instance, not {type(spell).__name__}")
            # The record is available to host tools; MANA source cannot assign it.
            if stmt.mode == "appraise":
                return self.op_appraise(spell, presentation=stmt.presentation)
            if stmt.mode == "cast":
                return self.op_cast(spell)
            return self.op_post(spell, presentation=stmt.presentation) if stmt.mode == "post" else self.op_release(spell)

        if isinstance(stmt, TuneAssignment):
            spell = self.eval_expr(stmt.spell, env)
            if not isinstance(spell, SpellInstance):
                raise TypeErrorML(
                    "tune requires a configured spell instance; create one first, "
                    "for example 'fire_ball = e_ball(Fire)'"
                )
            matches = self._find_tunable_calls(spell.definition.body, stmt.operation, stmt.target_name)
            if not matches:
                raise TypeErrorML(
                    f"cannot tune '{spell.name}.{stmt.operation}' for '{stmt.target_name}': "
                    "that operation and target do not exist in the spell"
                )
            if len(matches) > 1:
                raise TypeErrorML(
                    f"cannot tune '{spell.name}.{stmt.operation}' for '{stmt.target_name}': "
                    "multiple matching operations exist; make the target/operation unambiguous"
                )
            value = self.eval_expr(stmt.value, env)
            spell.tuned_operations[(stmt.operation, stmt.target_name)] = value
            return value

        if isinstance(stmt, WeatherStatement):
            if self._pure_call_depth:
                raise MagicErrorML("weather changes world state; place the statement inside a spell and use post() or release()")
            namespace = env.get("weather")
            if not isinstance(namespace, LibraryNamespace):
                raise RuntimeErrorML("the built-in weather rules are unavailable")
            configure = namespace.values.get("configure")
            if not callable(configure):
                raise RuntimeErrorML("the built-in weather.configure operation is unavailable")
            kwargs = {name: self.eval_expr(value, env) for name, value in stmt.fields}
            return configure(stmt.kind, **kwargs)

        if isinstance(stmt, FunctionDef):
            if stmt.library_function:
                # Library helpers live behind an explicit namespace, so their
                # exported names may reuse a global operation safely (for example
                # my_geometry.distance) without replacing the global name.
                if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", stmt.name) or stmt.name in self.LANGUAGE_KEYWORDS:
                    raise RuntimeErrorML(f"invalid library function name '{stmt.name}'")
            else:
                self.check_name(stmt.name)
            for param in stmt.params:
                self.check_name(param)
            if stmt.is_spell and stmt.params and stmt.params != ["element"]:
                raise TypeErrorML("spell definitions accept no parameters or one base-element selector: use 'spell name(element):'")
            env.assign(stmt.name, FunctionValue(
                stmt.params, stmt.body, env, stmt.name, stmt.defaults,
                library_function=stmt.library_function, is_spell=stmt.is_spell,
            ))
            return None

        if isinstance(stmt, SkipStatement):
            return None

        if isinstance(stmt, WeaveMana):
            if self._pure_call_depth:
                raise MagicErrorML("a directly called definition cannot weave mana; use post() or release()")
            allowed = {"shape", "radius", "energy", "position", "collidable", "anchored"}
            unknown = sorted({name for name, _ in stmt.fields} - allowed)
            if unknown:
                raise TypeErrorML("unknown weave setting(s): " + ", ".join(unknown) + "; supported settings are " + ", ".join(sorted(allowed)))
            kwargs = {
                name: (value.name.casefold() if name == "shape" and isinstance(value, Name)
                       else self.eval_expr(value, env))
                for name, value in stmt.fields
            }
            kwargs["name"] = stmt.name
            mana_namespace = env.get("mana")
            form = mana_namespace.values.get("form") if isinstance(mana_namespace, LibraryNamespace) else None
            if form is None:
                raise RuntimeErrorML("the built-in mana construct helper is unavailable")
            obj = form(**kwargs)
            self.assign(Name(stmt.name), obj, env)
            if self.observer is not None:
                self._observe("entity.changed", entity=self._visual_entity(obj), operation="weave")
                self._observe("activity", label=f"Wove {self._object_label(obj)}", action="weave")
            return obj

        if isinstance(stmt, Assignment):
            value = self.eval_expr(stmt.value, env)
            self.assign(stmt.target, value, env)
            return value

        if isinstance(stmt, ExpressionStatement):
            # show is output-only: it is legal as a standalone statement, never as a value.
            expr = stmt.expression
            if isinstance(expr, Call) and isinstance(expr.callee, Name) and expr.callee.name == "show":
                if self._pure_call_depth:
                    raise MagicErrorML("a directly called definition must be pure; use show from a spell or top-level code")
                args = [self.eval_expr(arg, env) for arg in expr.args]
                kwargs = {key: self.eval_expr(value, env) for key, value in expr.kwargs.items()}
                self.op_show(*args, **kwargs)
                return None
            return self.eval_expr(expr, env)

        if isinstance(stmt, Incant):
            if not self._function_depth:
                raise RuntimeErrorML("incant can only be used inside a def")
            raise IncantSignal(None if stmt.value is None else self.eval_expr(stmt.value, env))

        if isinstance(stmt, TargetContext):
            selected = self.eval_expr(stmt.target, env)
            selected = self.require_object(selected, "tgset target selection")
            if selected.properties.get("targetable") is False:
                raise MagicErrorML(f"target '{self._object_label(selected)}' is not targetable")
            self._target_context_stack.append(selected)
            try:
                return self.exec_block(stmt.body, Environment(parent=env))
            finally:
                self._target_context_stack.pop()

        if isinstance(stmt, TargetSet):
            self.check_name(stmt.name)
            target = MagicObject("Target")
            target.properties["display_name"] = stmt.name
            target.properties["object_kind"] = "target"
            target.properties["target_profile"] = True
            explicit_fields = {field_name for field_name, _ in stmt.fields}
            for field_name, field_expr in stmt.fields:
                value = self.eval_expr(field_expr, env)
                self.assign_target_field(target, field_name, value)
            # tgset can also define ordinary material objects, not only combat
            # profiles. Infer practical defaults from the stated material unless
            # the author explicitly supplied those fields.
            material_value = target.properties.get("material", "Target")
            material_key = material_value.strip().casefold() if isinstance(material_value, str) else "target"
            if "kind" not in explicit_fields and material_key not in {"", "target"}:
                target.properties["kind"] = "material"
            combustible_materials = {
                "wood", "timber", "paper", "cardboard", "straw", "dry grass",
                "dry_grass", "leaves", "cloth", "cotton", "bark", "cane",
            }
            if "combustible" not in explicit_fields:
                target.properties["combustible"] = material_key in combustible_materials
            if "powderable" not in explicit_fields:
                non_solid_materials = {"fire", "water", "air", "mana", "puremana", "thermalrelease", "steam"}
                target.properties["powderable"] = (
                    target.properties.get("state", "solid") == "solid"
                    and material_key not in non_solid_materials
                )
            # A body must be declared as corpse/bones when the object is
            # introduced to the world. Retagging an ordinary Earth object later
            # is not itself a physical transformation into remains.
            body_materials = {"bone", "bones", "skeleton", "corpse", "dead body", "remains"}
            body_states = {"corpse", "dead", "dead body", "remains", "bones"}
            state_key = str(target.properties.get("state", "")).strip().casefold().replace("_", " ")
            kind_key = str(target.properties.get("kind", "")).strip().casefold().replace("_", " ")
            target.properties["body_present"] = (
                material_key.replace("_", " ") in body_materials
                or state_key in body_states
                or kind_key in body_materials
            )
            # In the no-world-view prototype, `distance` alone places a target
            # along the default forward (+X) axis. Explicit/world positions take precedence.
            if "pos" not in explicit_fields and "distance" in explicit_fields:
                distance_value = target.properties.get("distance")
                if isinstance(distance_value, Quantity) and distance_value.value > 0:
                    target.properties["pos"] = Vector3(distance_value.value, 0, 0, M)
            # Combat/distance target profiles remain fixed unless the author opts
            # out with anchored = false. tgset also defines ordinary materials
            # (for example a rock to push), and those must remain movable.
            is_target_profile = (
                target.properties.get("kind", "target") == "target"
                or "distance" in explicit_fields
                or any(name in {"hp", "max_hp", "defence"} or name.startswith("resist_")
                       for name in explicit_fields)
            )
            if is_target_profile and "anchored" not in explicit_fields:
                target.properties["anchored"] = True
            target.properties["anchor_pos"] = target.properties.get("pos")
            if is_target_profile:
                target.properties.setdefault("targetable", True)
            # tgset can represent target profiles as well as ordinary manipulable
            # matter. Recalculate density and energy after custom mass/volume/temp
            # values have been assigned so wood and rock profiles remain coherent.
            mass_q = target.properties.get("mass")
            volume_q = target.properties.get("volume")
            if isinstance(mass_q, Quantity) and isinstance(volume_q, Quantity) and volume_q.value > 0:
                target.properties["density"] = Quantity(mass_q.value / volume_q.value, DENSITY)
            self.update_energy(target)
            self.record_energy_delta(
                "tgset profile", target, self.object_energy_j(target),
                source="existing world state",
            )
            self._record_created(target, reason="tgset profile")
            env.assign(stmt.name, target)
            return target

        if isinstance(stmt, If):
            for cond, block in stmt.branches:
                if self.truthy(self.eval_expr(cond, env)):
                    return self.exec_block(block, Environment(parent=env))
            if stmt.else_block:
                return self.exec_block(stmt.else_block, Environment(parent=env))
            return None

        if isinstance(stmt, While):
            iterations = 0
            while self.truthy(self.eval_expr(stmt.condition, env)):
                self.exec_block(stmt.body, Environment(parent=env))
                iterations += 1
                if iterations > MAX_LOOP_ITERATIONS:
                    raise RuntimeErrorML("while loop exceeded the safety iteration limit")
            return None

        if isinstance(stmt, For):
            iterable = self.eval_expr(stmt.iterable, env)
            if isinstance(iterable, (str, bytes, dict)) or not hasattr(iterable, "__iter__"):
                if not isinstance(iterable, list):
                    raise TypeErrorML("for loop expects a list or span")
            self.check_name(stmt.name)
            iterations = 0
            for value in iterable:
                child = Environment(parent=env)
                child.assign(stmt.name, value)
                self.exec_block(stmt.body, child)
                iterations += 1
                if iterations > MAX_LOOP_ITERATIONS:
                    raise RuntimeErrorML("for loop exceeded the safety iteration limit")
            return None

        if isinstance(stmt, Simul):
            self.validate_simul(stmt, env)
            # The block is deterministic: statements execute in source order.
            # Conflict validation keeps the operations independent, while a
            # snapshot prevents partial state changes if a later operation fails.
            snapshot = self._snapshot_runtime_state([env, self.global_env, self.active_objects])
            try:
                for child_statement in stmt.body.statements:
                    self.exec_stmt(child_statement, env)
            except Exception:
                self._restore_runtime_state(snapshot)
                raise
            return None

        if isinstance(stmt, Wait):
            seconds = self.to_seconds(self.eval_expr(stmt.duration, env))
            if seconds < 0:
                raise PhysicsErrorML("wait duration cannot be negative")
            if seconds > MAX_PERSISTENCE_SECONDS:
                raise RuntimeErrorML(f"wait duration exceeds the {MAX_PERSISTENCE_SECONDS:g}s safety cap")
            self.advance_time(seconds)
            return None

        if isinstance(stmt, After):
            seconds = self.to_seconds(self.eval_expr(stmt.duration, env))
            if seconds < 0:
                raise PhysicsErrorML("after delay cannot be negative")
            if seconds > MAX_PERSISTENCE_SECONDS:
                raise RuntimeErrorML(f"after delay exceeds the {MAX_PERSISTENCE_SECONDS:g}s safety cap")
            self.advance_time(seconds)
            return self.exec_block(stmt.body, Environment(parent=env))

        if isinstance(stmt, Every):
            interval = self.to_seconds(self.eval_expr(stmt.interval, env))
            if interval <= 0:
                raise PhysicsErrorML("every interval must be greater than zero")
            if interval > MAX_PERSISTENCE_SECONDS:
                raise RuntimeErrorML("every interval exceeds the persistent-spell safety cap")
            self.timers.append(TimerRegistration(interval, stmt, env, until_next=interval))
            return None

        if isinstance(stmt, Event):
            if stmt.event_name not in MANA_EVENT_NAMES:
                self._emit_mana_warning(
                    f"unknown MANA event '{stmt.event_name}'; known events: {', '.join(sorted(MANA_EVENT_NAMES))}",
                    statement=stmt,
                )
            self.event_handlers.append(EventRegistration(stmt.event_name, stmt, env))
            return None

        raise RuntimeErrorML(f"unsupported statement {type(stmt).__name__}")

    def assign(self, target, value, env):
        if isinstance(target, Name):
            self.check_name(target.name)
            renamed_object = False
            previous_label = None
            if isinstance(value, MagicObject) and (
                value.properties.get("display_name") in (None, value.element)
                or (value.properties.get("object_kind") == "mana_construct"
                    and str(value.properties.get("display_name", "")).startswith("mana_"))
            ):
                # Named constructs and material objects use the source-level variable name.
                previous_label = self._object_label(value)
                value.properties["display_name"] = target.name
                renamed_object = previous_label != target.name
            if isinstance(value, MagicObject) and value.properties.get("is_summoned", False):
                # Naming the result tames this particular summoned instance.
                # Preserve its first stable name when the same object is aliased.
                if not value.properties.get("is_tamed", False):
                    value.properties["is_tamed"] = True
                    value.properties["tame_name"] = target.name
            if isinstance(value, SpellInstance):
                value.name = target.name
            env.assign(target.name, value)
            # _record_created() happens before this assignment is known. Emit a
            # rename record so a replay shows the source-level name, not an
            # implementation label like "mana_disc".
            if renamed_object and self.observer is not None and self._spell_run_stack:
                self._observe(
                    "entity.changed", entity=self._visual_entity(value), operation="name",
                    previous_name=previous_label, new_name=target.name,
                )
            return
        if isinstance(target, Attribute):
            if self._pure_call_depth:
                raise MagicErrorML("a directly called definition cannot assign object properties; use post() or release()")
            obj = self.eval_expr(target.obj, env)
            self.set_attr(obj, target.name, value)
            return
        if isinstance(target, Subscript):
            if self._pure_call_depth:
                raise MagicErrorML("a directly called definition cannot mutate a list; use post() or release()")
            container = self.eval_expr(target.obj, env)
            index = self.eval_expr(target.index, env)
            if not isinstance(container, list):
                raise TypeErrorML("indexed assignment requires a list; only list items are assignable")
            if isinstance(index, bool) or not isinstance(index, int):
                raise TypeErrorML("list index must be an integer")
            if not -len(container) <= index < len(container):
                raise RuntimeErrorML(f"list index {index} is out of range for a list of length {len(container)}")
            container[index] = value
            return
        raise TypeErrorML("assignment target must be a variable or object property")

    def _require_element_invocation(self, element_name: str) -> None:
        """Permit direct creation only for base elements, Mana, or invoked plane energy."""
        if element_name in FUNDAMENTAL_ELEMENTS or element_name == "Mana":
            return
        if element_name not in NON_BASE_PLANAR_ELEMENTS:
            raise MagicErrorML(
                f"'{element_name}' is not a directly available elemental plane type; "
                "combine fundamental elements or use a registered elemental plane"
            )

        planes_namespace = self._library_namespaces.get("planes")
        if planes_namespace is None:
            raise MagicErrorML(
                f"creating {element_name} requires 'load planes' and "
                f"'planes.invoke(\"{element_name}\")' first"
            )
        has_permission = planes_namespace.values.get("has_permission")
        if not callable(has_permission) or not has_permission(element_name):
            raise MagicErrorML(
                f"creating {element_name} requires 'planes.invoke(\"{element_name}\")' first"
            )

    def eval_expr(self, expr, env):
        depth = getattr(self._evaluation_context, "depth", 0)
        if depth >= MAX_EXPRESSION_DEPTH:
            raise RuntimeErrorML(
                f"expression evaluation exceeds the safety limit ({MAX_EXPRESSION_DEPTH} nested operations)"
            )
        self._evaluation_context.depth = depth + 1
        try:
            return self._eval_expr_impl(expr, env)
        finally:
            self._evaluation_context.depth = depth

    def _eval_expr_impl(self, expr, env):
        if isinstance(expr, Literal):
            return expr.value
        if isinstance(expr, Name):
            # Uppercase registered element identifiers denote types. They are not
            # variables and do not create magical objects until `create` executes.
            if expr.name in ELEMENTS or expr.name in PLANAR_ELEMENT_NAMES or expr.name == "Mana":
                return ElementTypeValue(expr.name)
            try:
                return env.get(expr.name)
            except RuntimeErrorML as exc:
                documented_equivalents = {"range": "span", "len": "length", "True": "true", "False": "false"}
                unsupported_python_words = {"try", "continue", "print", "break", "None", "import", "return", "pass"}
                if expr.name in documented_equivalents:
                    exc.hint = f"Did you mean '{documented_equivalents[expr.name]}'?"
                elif expr.name not in unsupported_python_words:
                    from .shapes import SUPPORTED_SHAPES
                    candidates = (set(self.LANGUAGE_KEYWORDS) | set(self.BUILTIN_NAMES)) - set(SUPPORTED_SHAPES)
                    scope = env
                    while scope is not None:
                        candidates.update(set(scope.values) - set(SUPPORTED_SHAPES))
                        scope = scope.parent
                    matches = difflib.get_close_matches(expr.name, sorted(candidates), n=1, cutoff=0.74)
                    if matches:
                        exc.hint = f"Did you mean '{matches[0]}'?"
                raise
        if isinstance(expr, ListLiteral):
            self._charge_allocation(len(expr.items), "list-item")
            return [self.eval_expr(item, env) for item in expr.items]
        if isinstance(expr, Subscript):
            container = self.eval_expr(expr.obj, env)
            index = self.eval_expr(expr.index, env)
            if not isinstance(container, (list, str, range)):
                raise TypeErrorML("indexing is supported for lists, strings, and spans")
            if isinstance(index, bool) or not isinstance(index, int):
                raise TypeErrorML("index must be an integer")
            if not -len(container) <= index < len(container):
                raise RuntimeErrorML(f"index {index} is out of range for a value of length {len(container)}")
            return container[index]
        if isinstance(expr, Create):
            if self._pure_call_depth:
                raise MagicErrorML("a directly called definition cannot create objects; use post() or release()")
            element_name = expr.type_name
            if element_name not in ELEMENTS and element_name not in PLANAR_ELEMENT_NAMES and element_name != "Mana":
                try:
                    dynamic_type = env.get(element_name)
                except RuntimeErrorML as exc:
                    raise MagicErrorML(f"unknown built-in element or element variable '{element_name}'") from exc
                if isinstance(dynamic_type, ElementTypeValue):
                    element_name = dynamic_type.name
                else:
                    raise MagicErrorML(
                        f"create expects a registered element type; '{element_name}' is not an element selector"
                    )
            if element_name == "Mana":
                raise MagicErrorML("mana is woven, not created; use `construct = weave mana` and add settings beneath `weave mana:` if needed")
            self._require_element_invocation(element_name)
            # MagicObject initializes a coherent energy and integrity baseline;
            # do not recompute that same baseline a second time here.
            obj = MagicObject(element_name)
            # Creation costs only the matter-manifestation rate, not its starting heat/motion energy.
            # Pure mana is a field/energy construct, not manifested matter.
            creation_cost = _DEFAULT_CREATION_MANA_COST
            obj.properties["creation_mana_cost"] = creation_cost
            if element_name != "Mana":
                self.charge_mana(creation_cost, reason=f"create {element_name}", target=obj)
            self.record_energy_delta(
                f"create {element_name}", obj, self.object_energy_j(obj),
                source="matter creation (initial state)",
            )
            self._record_created(obj, reason=f"create {element_name}")
            return obj
        if isinstance(expr, Attribute):
            obj = self.eval_expr(expr.obj, env)
            return self.get_attr(obj, expr.name)
        if isinstance(expr, Unary):
            value = self.eval_expr(expr.operand, env)
            if expr.op == "not":
                return not self.truthy(value)
            try:
                if expr.op == "+":
                    return +value
                if expr.op == "-":
                    return -value
            except MagicLangError:
                raise
            except OverflowError as exc:
                raise PhysicsErrorML("unary arithmetic result is outside the supported numeric range") from exc
            except ValueError as exc:
                raise PhysicsErrorML(f"invalid unary arithmetic operation: {exc}") from exc
            except TypeError as exc:
                raise TypeErrorML(f"unary '{expr.op}' is not supported for {type(value).__name__}") from exc
            raise RuntimeErrorML(f"unknown unary operator {expr.op}")
        if isinstance(expr, Binary):
            # Logical operators short-circuit, like Python.
            left = self.eval_expr(expr.left, env)
            if expr.op == "and" and not self.truthy(left):
                return False
            if expr.op == "or" and self.truthy(left):
                return True
            right = self.eval_expr(expr.right, env)
            return self.binary(expr.op, left, right)
        if isinstance(expr, Call):
            if isinstance(expr.callee, Name) and expr.callee.name in {"show", "post", "release", "tune"}:
                name = expr.callee.name
                raise RuntimeErrorML(
                    f"{name} is a MANA command/special form, not a value-producing function; "
                    f"write it using its documented standalone syntax"
                )
            callee = self.eval_expr(expr.callee, env)
            active_instance = self._spell_instance_stack[-1] if self._spell_instance_stack else None
            tuned_key = None
            if (active_instance is not None and isinstance(expr.callee, Name)
                    and expr.args and isinstance(expr.args[0], Name)):
                candidate_key = (expr.callee.name, expr.args[0].name)
                if candidate_key in active_instance.tuned_operations and len(expr.args) >= 2:
                    tuned_key = candidate_key
            args = []
            for index, argument in enumerate(expr.args):
                if tuned_key is not None and index == 1:
                    args.append(active_instance.tuned_operations[tuned_key])
                else:
                    args.append(self.eval_expr(argument, env))
            kwargs = {k: self.eval_expr(v, env) for k, v in expr.kwargs.items()}
            return self.call(callee, args, kwargs)
        raise RuntimeErrorML(f"unsupported expression {type(expr).__name__}")

    def _bind_function_arguments(self, callee: FunctionValue, args, kwargs) -> list[Any]:
        if callee.is_spell:
            if callee.params == ["element"]:
                if len(args) != 1 or kwargs:
                    raise TypeErrorML(f"spell template '{callee.name}' expects exactly one element: {callee.name}(Fire)")
                value = args[0]
                if not isinstance(value, ElementTypeValue) or value.name not in FUNDAMENTAL_ELEMENTS:
                    raise MagicErrorML(
                        f"'{callee.name}' expects one of the four base element types: Fire, Water, Earth, or Air"
                    )
                return [value]
            if args or kwargs:
                raise TypeErrorML(f"spell '{callee.name}' takes no arguments")
            return []

        if len(args) > len(callee.params):
            raise TypeErrorML(f"function '{callee.name}' takes at most {len(callee.params)} arguments")
        bound: dict[str, Any] = {}
        for name, value in zip(callee.params, args):
            bound[name] = value
        for name, value in kwargs.items():
            if name not in callee.params:
                raise TypeErrorML(f"function '{callee.name}' has no parameter '{name}'")
            if name in bound:
                raise TypeErrorML(f"function '{callee.name}' got multiple values for '{name}'")
            bound[name] = value
        for name in callee.params:
            if name in bound:
                continue
            if name in callee.defaults:
                bound[name] = self.eval_expr(callee.defaults[name], callee.closure)
            else:
                raise TypeErrorML(f"function '{callee.name}' is missing required argument '{name}'")
        return [bound[name] for name in callee.params]

    def _execute_definition(self, callee: FunctionValue, bound_values: list[Any]):
        if self._function_depth >= MAX_FUNCTION_DEPTH:
            raise RuntimeErrorML(f"MANA definition call depth exceeded the safety limit ({MAX_FUNCTION_DEPTH})")
        local = Environment(parent=callee.closure, scope_boundary=True)
        for name, value in zip(callee.params, bound_values):
            local.set_local(name, value)
        self._function_depth += 1
        try:
            try:
                return self.exec_block(callee.body, local)
            except IncantSignal as signal:
                return signal.value
        finally:
            self._function_depth -= 1

    def call(self, callee, args, kwargs):
        if isinstance(callee, FunctionValue):
            if callee.is_spell:
                bound_values = self._bind_function_arguments(callee, args, kwargs)
                # An element-parameterized spell-template call configures an instance; it
                # never executes the spell body during configuration.
                if callee.params == ["element"]:
                    return SpellInstance(callee, bound_values[0])
                raise TypeErrorML(
                    f"spell '{callee.name}' cannot be called as a value; use post({callee.name}) or release({callee.name})"
                )
            bound_values = self._bind_function_arguments(callee, args, kwargs)
            # `def` and library helpers are pure calculation functions. World
            # operations remain restricted to spell bodies run through appraise/cast (or legacy post/release).
            self._pure_call_depth += 1
            try:
                return self._execute_definition(callee, bound_values)
            finally:
                self._pure_call_depth -= 1

        if isinstance(callee, SpellInstance):
            raise TypeErrorML(
                f"configured spell '{callee.name}' is not called directly; use post({callee.name}) or release({callee.name})"
            )

        if callable(callee):
            try:
                if (self._pure_call_depth and self._is_runtime_operation(callee)
                        and getattr(callee, "__name__", "") not in {
                            "op_force", "op_pressure", "op_has_domain", "op_matter_to_mana",
                            "op_mana_to_matter", "op_mana_to_energy", "op_energy_to_mana",
                            "op_sqrt", "op_kinetic_energy", "op_momentum",
                        }):
                    raise MagicErrorML(
                        "a directly called definition must be pure; move world-changing operations into a spell "
                        "and execute it with post() or release()"
                    )
                if self._spell_run_stack and self._is_runtime_operation(callee):
                    return self._call_traced_operation(callee, args, kwargs)
                return callee(*args, **kwargs)
            except (MagicErrorML, PhysicsErrorML, TypeErrorML, UnitErrorML, RuntimeErrorML):
                raise
            except ZeroDivisionError as exc:
                raise PhysicsErrorML("division by zero") from exc
            except OverflowError as exc:
                raise PhysicsErrorML("operation exceeded the supported numeric range") from exc
            except ValueError as exc:
                raise PhysicsErrorML(f"operation rejected the supplied numeric value: {exc}") from exc
            except TypeError as exc:
                raise TypeErrorML(str(exc)) from exc
        raise TypeErrorML(f"value {callee!r} is not callable")

    @staticmethod
    def _find_tunable_calls(body: Block, operation: str, target_name: str) -> list[Call]:
        """Find source-level operation calls matching a (operation, target) pair."""
        found: list[Call] = []
        seen = set()

        def walk(node):
            if node is None or id(node) in seen:
                return
            if isinstance(node, Call):
                if (isinstance(node.callee, Name) and node.callee.name == operation
                        and len(node.args) >= 2 and isinstance(node.args[0], Name)
                        and node.args[0].name == target_name):
                    found.append(node)
            if is_dataclass(node):
                seen.add(id(node))
                for item in fields(node):
                    walk(getattr(node, item.name))
            elif isinstance(node, (list, tuple)):
                seen.add(id(node))
                for item in node:
                    walk(item)
            elif isinstance(node, dict):
                seen.add(id(node))
                for key, item in node.items():
                    walk(key)
                    walk(item)

        walk(body)
        return found

    def binary(self, op, left, right):
        if op == "and":
            return self.truthy(left) and self.truthy(right)
        if op == "or":
            return self.truthy(left) or self.truthy(right)
        if op == "==":
            return left == right
        if op == "!=":
            return left != right
        if op in ("<", "<=", ">", ">="):
            try:
                return {"<": lambda: left < right, "<=": lambda: left <= right,
                        ">": lambda: left > right, ">=": lambda: left >= right}[op]()
            except MagicLangError:
                raise
            except (TypeError, ValueError) as exc:
                raise UnitErrorML(f"cannot compare these values: {exc}") from exc
        try:
            if op == "+":
                if isinstance(left, str) and isinstance(right, str):
                    result_size = len(left) + len(right)
                    if result_size > MAX_COLLECTION_SIZE:
                        raise RuntimeErrorML(
                            f"string result exceeds the MANA size limit ({MAX_COLLECTION_SIZE} characters)"
                        )
                    self._charge_allocation(result_size, "string-character")
                elif isinstance(left, list) and isinstance(right, list):
                    result_size = len(left) + len(right)
                    if result_size > MAX_COLLECTION_SIZE:
                        raise RuntimeErrorML(
                            f"list result exceeds the MANA size limit ({MAX_COLLECTION_SIZE} items)"
                        )
                    self._charge_allocation(result_size, "list-item")
                result = left + right
            elif op == "-":
                result = left - right
            elif op == "*":
                repeated, multiplier = None, None
                if isinstance(left, (str, list)) and isinstance(right, int) and not isinstance(right, bool):
                    repeated, multiplier = left, right
                elif isinstance(right, (str, list)) and isinstance(left, int) and not isinstance(left, bool):
                    repeated, multiplier = right, left
                if repeated is not None:
                    result_size = len(repeated) * max(0, multiplier)
                    if result_size > MAX_COLLECTION_SIZE:
                        kind = "string characters" if isinstance(repeated, str) else "list items"
                        raise RuntimeErrorML(f"repeated {kind} exceed the MANA size limit ({MAX_COLLECTION_SIZE})")
                    self._charge_allocation(
                        result_size, "string-character" if isinstance(repeated, str) else "list-item"
                    )
                result = left * right
            elif op == "/":
                result = left / right
            elif op == "%":
                if right == 0:
                    raise PhysicsErrorML("division by zero")
                result = left % right
            elif op == "**":
                if isinstance(right, int) and not isinstance(right, bool) and abs(right) > MAX_POWER_EXPONENT:
                    raise PhysicsErrorML(
                        f"exponent exceeds the MANA safety limit ({MAX_POWER_EXPONENT}); value is outside the supported numeric range"
                    )
                if isinstance(right, float) and abs(right) > MAX_POWER_EXPONENT:
                    raise PhysicsErrorML(
                        f"exponent exceeds the MANA safety limit ({MAX_POWER_EXPONENT}); value is outside the supported numeric range"
                    )
                if (
                    isinstance(left, int) and not isinstance(left, bool)
                    and isinstance(right, int) and not isinstance(right, bool)
                    and right > 0 and abs(left) > 1
                ):
                    # Estimate the result size before invoking Python's arbitrary-
                    # precision power. This blocks short expressions that could
                    # otherwise allocate gigabytes of integer digits.
                    estimated_bits = math.log2(abs(left)) * right
                    if estimated_bits > MAX_INTEGER_RESULT_BITS:
                        raise PhysicsErrorML(
                            f"integer power result exceeds the MANA size limit ({MAX_INTEGER_RESULT_BITS} bits)"
                        )
                result = left ** right
            else:
                raise RuntimeErrorML(f"unknown binary operator {op}")
        except MagicLangError:
            raise
        except ZeroDivisionError as exc:
            raise PhysicsErrorML("division by zero") from exc
        except OverflowError as exc:
            raise PhysicsErrorML("arithmetic result is outside the supported numeric range") from exc
        except ValueError as exc:
            raise PhysicsErrorML(f"invalid arithmetic operation: {exc}") from exc
        except TypeError as exc:
            raise TypeErrorML(str(exc)) from exc
        if isinstance(result, complex):
            raise PhysicsErrorML("arithmetic result is complex; MANA supports real-valued numbers only")
        if isinstance(result, float) and not math.isfinite(result):
            raise PhysicsErrorML("arithmetic result must be finite; operation produced infinity or NaN")
        return result

    def get_attr(self, obj, name):
        if isinstance(obj, LibraryNamespace):
            if name not in obj.values:
                raise TypeErrorML(f"library '{obj.name}' does not export '{name}'")
            return obj.values[name]
        if isinstance(obj, MagicObject):
            return obj.get(name)
        if isinstance(obj, dict) and name in obj:
            return obj[name]
        # Only expose explicitly documented, read-only fields from small library
        # data records. Never expose general Python methods such as list.extend,
        # str.format, function.__globals__, or host-object internals.
        safe_record_fields = {
            ("magiclang.libraries.planar_registry", "PlaneReference"): {
                "id", "name", "category", "data_library", "parent_plane", "is_region", "qualified_name",
            },
            ("magiclang.libraries.plane_data", "BeingRecord"): {
                "name", "kind", "home_plane", "element", "summoning_requirements", "hp", "max_hp",
                "defence", "attack", "resistance", "is_being_record",
            },
            ("magiclang.materials", "ElementRecord"): {
                "atomic_number", "symbol", "name", "density_kg_m3", "standard_state", "category",
                "estimated_density", "melting_point_k", "boiling_point_k",
            },
        }
        key = (type(obj).__module__, type(obj).__name__)
        if name in safe_record_fields.get(key, ()) and not name.startswith("_"):
            value = getattr(obj, name)
            if not callable(value):
                return value
        raise TypeErrorML(f"object has no MANA property '{name}'")

    def set_attr(self, obj, name, value):
        """Assign one property atomically, including energy/integrity side effects."""
        if not isinstance(obj, MagicObject):
            raise TypeErrorML("properties can only be assigned on magical objects")
        properties_before = dict(obj.properties)
        active_objects_before = list(self.active_objects)
        ledger_before = [dict(entry) for entry in self.energy_ledger]
        mana_before = self.total_mana_used
        energy_input_before = self.energy_input_j
        energy_output_before = self.energy_output_j
        try:
            return self._set_attr_impl(obj, name, value)
        except Exception:
            obj.properties.clear()
            obj.properties.update(properties_before)
            self.active_objects[:] = active_objects_before
            self.energy_ledger = ledger_before
            self.total_mana_used = mana_before
            self.energy_input_j = energy_input_before
            self.energy_output_j = energy_output_before
            raise

    def _set_attr_impl(self, obj, name, value):
        if not isinstance(obj, MagicObject):
            raise TypeErrorML("properties can only be assigned on magical objects")
        if name == "mana":
            raise MagicErrorML("mana is not stored on objects")
        if name in RUNTIME_MANAGED_PROPERTIES:
            if name == "acceleration_persistent":
                raise MagicErrorML("acceleration_persistent is an internal physics flag; use accelerate() or assign .acc")
            if name == "bound_energy":
                raise MagicErrorML("bound_energy is managed by planar energy transfers and cannot be assigned directly")
            if name in {"mana_used", "mana_cost", "creation_mana_cost"}:
                raise MagicErrorML(f"{name} is a runtime-managed cost readout and cannot be assigned directly")
            if name in {
                "released_energy", "released_mana", "energy_origin", "energy_sources",
                "local_released_energy", "local_released_mana", "local_energy_origin", "local_energy_sources",
            }:
                raise MagicErrorML(
                    f"{name} is managed by the energy-release ledger and cannot be assigned directly"
                )
            if name in {"active", "released"}:
                raise MagicErrorML(f"{name} is managed by runtime object lifecycle operations")
            if name.startswith("integrity") or name == "collapsed_into":
                raise MagicErrorML(f"{name} is calculated by the integrity system and cannot be assigned directly")
            raise MagicErrorML(
                f"{name} is derived from mass, temp, and velocity; change those inputs instead"
            )
        if name == "display_name" and (not isinstance(value, str) or not value.strip()):
            raise TypeErrorML("display_name must be non-empty text")
        if name == "object_kind" and (not isinstance(value, str) or not value.strip()):
            raise TypeErrorML("object_kind must be non-empty text")
        if name == "material" and (not isinstance(value, str) or not value.strip()):
            raise TypeErrorML("material must be non-empty text")
        if name == "stabilizers":
            if not isinstance(value, list):
                raise TypeErrorML("stabilizers must be a list of registered element names")
            valid_stabilizers = set(INTEGRITY_THRESHOLD_BONUS) | set(INTEGRITY_THERMAL_FACTORS) | set(INTEGRITY_COLLAPSE_STABILIZERS) | {"Space"}
            normalized = []
            for item in value:
                if isinstance(item, ElementTypeValue):
                    item = item.name
                if not isinstance(item, str) or item not in valid_stabilizers:
                    raise TypeErrorML(
                        "stabilizers may contain only Earth, Water, Air, Order, Light, Space, Time, Entropy, or Death"
                    )
                if item not in normalized:
                    normalized.append(item)
            value = normalized
        if name not in obj.properties and obj.properties.get("object_kind") != "target":
            raise TypeErrorML(f"{obj.element} object has no property '{name}'")
        if name not in obj.properties and obj.properties.get("object_kind") == "target":
            self.assign_target_field(obj, name, value)
            return
        if name in {"mass", "temp", "vel"} and not obj.properties.get("active", True):
            raise MagicErrorML(f"cannot change {name} on an inactive object; separate or reactivate it first")
        if name == "restitution":
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise TypeErrorML("restitution must be a finite number between 0 and 1")
            try:
                value = float(value)
            except (OverflowError, ValueError) as exc:
                raise PhysicsErrorML("restitution is outside the supported numeric range") from exc
            if not math.isfinite(value):
                raise TypeErrorML("restitution must be a finite number between 0 and 1")
            if not 0 <= value <= 1:
                raise PhysicsErrorML("restitution must be between 0 and 1")
        if name == "friction":
            if isinstance(value, Quantity):
                if value.dimension != DIMENSIONLESS:
                    raise UnitErrorML("friction must be dimensionless")
                value = value.value
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(float(value)) or not 0 <= float(value) <= 2:
                raise TypeErrorML("friction must be between 0 and 2")
            value = float(value)
        if name == "collidable" and not isinstance(value, bool):
            raise TypeErrorML("collidable must be true or false")
        old = obj.properties[name]
        old_total_energy = self.object_energy_j(obj)
        old_mass = obj.properties.get("mass")
        if isinstance(old, Quantity):
            value = self.as_quantity(value, old.dimension, f"{obj.element}.{name}")
            self.validate_quantity_property(name, value)
        elif isinstance(old, Vector3):
            if not isinstance(value, Vector3) or value.dimension != old.dimension:
                raise UnitErrorML(f"{obj.element}.{name} requires a vector in {old.dimension}")
        if name in {"pos", "vel", "acc", "direction", "anchor_pos", "force"}:
            value = require_2d_world_vector(value, f"{obj.element}.{name}")
        if name == "mass" and isinstance(old_mass, Quantity):
            if value.value < old_mass.value:
                raise MagicErrorML(
                    "mass cannot be reduced by direct assignment; use a matter-removal operation or Null"
                )
        obj.set(name, value)
        if name == "acc":
            obj.properties["acceleration_persistent"] = True
        if name == "stabilizers":
            self.update_total_energy(obj)
        elif name == "material":
            self.update_total_energy(obj)
        elif name == "mass":
            volume = obj.properties.get("volume")
            if isinstance(volume, Quantity) and volume.value > 0:
                obj.properties["density"] = Quantity(value.value / volume.value, DENSITY)
            mass_added = max(0.0, value.value - old_mass.value) if isinstance(old_mass, Quantity) else 0.0
            if mass_added:
                creation_cost = matter_to_mana(Quantity(mass_added, KG)).value
                obj.properties["creation_mana_cost"] = obj.properties.get("creation_mana_cost", 0.0) + creation_cost
                self.record_mana_cost(creation_cost, reason="direct mass creation", target=obj)
            self.update_energy(obj)
        elif name == "volume":
            mass = obj.properties.get("mass")
            if isinstance(mass, Quantity) and value.value > 0:
                obj.properties["density"] = Quantity(mass.value / value.value, DENSITY)
        elif name == "temp":
            self.update_energy(obj)
        elif name == "vel":
            obj.properties["kinetic_energy"] = kinetic_energy(obj.properties["mass"], value)
            obj.properties["momentum"] = momentum(obj.properties["mass"], value)
            self.update_total_energy(obj)
        new_total_energy = self.object_energy_j(obj)
        delta_energy = new_total_energy - old_total_energy
        if abs(delta_energy) > 1e-9:
            source = "matter creation" if name == "mass" and isinstance(old_mass, Quantity) and value.value > old_mass.value else "magic property assignment"
            self.record_energy_delta(f"assign {name}", obj, delta_energy, source=source)
            if name in {"temp", "vel"}:
                self.record_mana_cost(abs(delta_energy) / JOULES_PER_MANA, reason=f"assign {name}", target=obj)

    def assign_target_field(self, target: MagicObject, name: str, value: Any) -> None:
        """Validate and assign one user-defined target-profile field."""
        if name == "mana":
            raise MagicErrorML("targets cannot store mana; spell mana is reported as a calculated cost")
        if name in {"hp", "max_hp", "defence"}:
            if isinstance(value, Quantity):
                if value.dimension != DIMENSIONLESS:
                    raise UnitErrorML(f"target field '{name}' must be a plain number")
                value = value.value
            if isinstance(value, bool) or not isinstance(value, (int, float)) or value < 0:
                raise TypeErrorML(f"target field '{name}' must be a non-negative number")
            try:
                value = float(value)
            except (OverflowError, ValueError) as exc:
                raise PhysicsErrorML(f"target field '{name}' is outside the supported numeric range") from exc
            if not math.isfinite(value):
                raise PhysicsErrorML(f"target field '{name}' must be finite")
        elif name.startswith("resist_"):
            if isinstance(value, Quantity):
                if value.dimension != DIMENSIONLESS:
                    raise UnitErrorML(f"target field '{name}' must be dimensionless")
                value = value.value
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not 0 <= value <= 1:
                raise TypeErrorML(f"{name} must be between 0 and 1 (0 = none, 1 = full resistance)")
            value = float(value)
        elif name in {"mass", "volume", "area"}:
            dimension = {"mass": KG, "volume": M3, "area": M2}[name]
            value = self.as_quantity(value, dimension, f"target {name}")
            if value.value < 0 or (name == "mass" and value.value <= 0):
                rule = "greater than zero" if name == "mass" else "non-negative"
                raise PhysicsErrorML(f"target {name} must be {rule}")
        elif name == "temp":
            value = self.as_quantity(value, K, "target temp")
            if value.value < 0:
                raise PhysicsErrorML("target temperature cannot be below 0 K")
        elif name == "material":
            if not isinstance(value, str) or not value.strip():
                raise TypeErrorML("target material must be non-empty text")
            value = value.strip()
        elif name == "kind":
            if not isinstance(value, str) or not value.strip():
                raise TypeErrorML("target kind must be non-empty text")
            value = value.strip()
        elif name == "shape":
            if not isinstance(value, str) or not value.strip():
                raise TypeErrorML("target shape must be non-empty text")
            value = value.strip().casefold()
        elif name == "state":
            if not isinstance(value, str) or value.casefold() not in {"solid", "liquid", "gas", "plasma", "powder", "burning"}:
                raise MagicErrorML("target state must be solid, liquid, gas, plasma, powder, or burning")
            value = value.casefold()
        elif name == "combustible":
            if not isinstance(value, bool):
                raise TypeErrorML("target combustible must be true or false")
        elif name == "anchored":
            if not isinstance(value, bool):
                raise TypeErrorML("target anchored must be true or false")
        elif name == "powderable":
            if not isinstance(value, bool):
                raise TypeErrorML("target powderable must be true or false")
        elif name == "ignition_temp":
            value = self.as_quantity(value, K, "target ignition_temp")
            if value.value < 0:
                raise PhysicsErrorML("ignition temperature cannot be below 0 K")
        elif name == "density":
            raise MagicErrorML("target density is derived from mass and volume; set mass and volume instead")
        elif name == "pos":
            if not isinstance(value, Vector3) or value.dimension != M:
                raise UnitErrorML("target pos must be a position vector")
            value = require_2d_world_vector(value, "target position")
        elif name == "area":
            value = self.as_quantity(value, M2, "target area")
            if value.value < 0:
                raise PhysicsErrorML("area cannot be negative")
        elif name == "collision_radius":
            value = self.as_quantity(value, M, "target collision_radius")
            if value.value < 0:
                raise PhysicsErrorML("target collision_radius cannot be negative")
        elif name == "restitution":
            if isinstance(value, Quantity):
                if value.dimension != DIMENSIONLESS:
                    raise UnitErrorML("target restitution must be dimensionless")
                value = value.value
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not 0 <= value <= 1:
                raise TypeErrorML("target restitution must be between 0 and 1")
            value = float(value)
        elif name == "friction":
            if isinstance(value, Quantity):
                if value.dimension != DIMENSIONLESS:
                    raise UnitErrorML("target friction must be dimensionless")
                value = value.value
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(float(value)) or not 0 <= float(value) <= 2:
                raise TypeErrorML("target friction must be between 0 and 2")
            value = float(value)
        elif name == "collidable":
            if not isinstance(value, bool):
                raise TypeErrorML("target collidable must be true or false")
        target.properties[name] = value

    # ---- Primitive magic operations ----

    def op_shape(self, target, geometry, **kwargs):
        target = self.require_object(target, "shape")
        self.require_property(target, "shape", "shape")
        if not isinstance(geometry, str):
            raise TypeErrorML("shape() expects a built-in geometry name")
        from .shapes import SUPPORTED_SHAPES
        geometry = geometry.casefold()
        if geometry not in SUPPORTED_SHAPES:
            raise MagicErrorML(f"unsupported shape '{geometry}'; choose a shape from the MANA shape catalogue")
        self.charge_operation(target, "shape", kwargs, 1.0)
        target.properties["shape"] = geometry
        self._observe("entity.changed", entity=self._visual_entity(target), operation="shape", shape=geometry)
        return target

    def op_move(self, target, distance, direction=None, **kwargs):
        target = self.require_object(target, "move")
        self.require_property(target, "pos", "move")
        self.require_property(target, "direction", "move")
        if target.properties.get("anchored", False):
            raise MagicErrorML("cannot move an anchored object; call unanchor() first")
        distance_m = self.as_quantity(distance, M, "move() distance")
        d = distance_m.value
        direction = target.properties["direction"] if direction is None else direction
        if not isinstance(direction, Vector3):
            raise TypeErrorML("move() direction must be a vector")
        direction = require_2d_world_vector(direction, "move() direction")
        if direction.magnitude() == 0:
            raise PhysicsErrorML("move() cannot use a zero direction")
        unit = direction.normalized()
        self.charge_operation(target, "move", kwargs, 1.0)
        target.properties["pos"] = Vector3(
            target.properties["pos"].x + unit.x * d,
            target.properties["pos"].y + unit.y * d,
            target.properties["pos"].z + unit.z * d, M,
        )
        return target

    def op_heat(self, target, amount, **kwargs):
        target = self.require_object(target, "heat")
        self.require_active_object(target, "heat")
        for prop in ("temp", "mass", "thermal_energy", "kinetic_energy", "energy"):
            self.require_property(target, prop, "heat")
        if isinstance(amount, Quantity) and amount.is_absolute_temperature:
            raise UnitErrorML("heat() expects a temperature change in K, not an absolute Celsius temperature")
        delta = self.as_quantity(amount, K, "heat() temperature increase")
        if delta.value < 0:
            raise PhysicsErrorML("heat() amount cannot be negative; use cool() to decrease temperature")
        old_energy = self.object_energy_j(target)
        new_temp = Quantity(target.properties["temp"].value + delta.value, K)
        self.validate_quantity_property("temp", new_temp)
        cost = delta.value * target.properties["mass"].value * DEFAULT_SPECIFIC_HEAT_J_PER_KG_K / JOULES_PER_MANA
        target.properties["temp"] = new_temp
        self.update_energy(target)
        self._apply_material_phase_law(target)
        if target.properties.get("combustible", False) and not target.properties.get("burning", False):
            ignition = target.properties.get("ignition_temp", Quantity(573.15, K))
            if isinstance(ignition, Quantity) and ignition.dimension == K and new_temp.value >= ignition.value:
                target.properties["state"] = "burning"
                target.properties["burning"] = True
                self.emit_event("object_ignited", target, target.properties.get("material", target.element))
        delta_energy = self.object_energy_j(target) - old_energy
        self.record_energy_delta("heat", target, delta_energy, source="spell energy input; mana-equivalent is readout only")
        self.charge_operation(target, "heat", kwargs, cost)
        return target

    def op_cool(self, target, amount, **kwargs):
        target = self.require_object(target, "cool")
        self.require_active_object(target, "cool")
        for prop in ("temp", "mass", "thermal_energy", "kinetic_energy", "energy"):
            self.require_property(target, prop, "cool")
        if isinstance(amount, Quantity) and amount.is_absolute_temperature:
            raise UnitErrorML("cool() expects a temperature change in K, not an absolute Celsius temperature")
        delta = self.as_quantity(amount, K, "cool() temperature decrease")
        if delta.value < 0:
            raise PhysicsErrorML("cool() amount cannot be negative")
        old_energy = self.object_energy_j(target)
        current = target.properties["temp"].value
        new_temp = current - delta.value
        if new_temp < 0:
            raise PhysicsErrorML("cooling cannot reduce temperature below 0 K")
        cost = delta.value * target.properties["mass"].value * DEFAULT_SPECIFIC_HEAT_J_PER_KG_K / JOULES_PER_MANA
        target.properties["temp"] = Quantity(new_temp, K)
        self.update_energy(target)
        self._apply_material_phase_law(target)
        delta_energy = self.object_energy_j(target) - old_energy
        self.record_energy_delta("cool", target, delta_energy, source="surroundings (heat removed)")
        self.charge_operation(target, "cool", kwargs, cost)
        return target

    def op_accelerate(self, target, acceleration, **kwargs):
        target = self.require_object(target, "accelerate")
        for prop in ("acc", "mass", "force"):
            self.require_property(target, prop, "accelerate")
        if isinstance(acceleration, Vector3):
            if acceleration.dimension != ACCELERATION:
                raise UnitErrorML("accelerate() vector must be in m/s2")
            new_acc = require_2d_world_vector(acceleration, "accelerate() acceleration")
        else:
            a = self.as_quantity(acceleration, ACCELERATION, "accelerate() acceleration")
            new_acc = Vector3(a.value, 0, 0, ACCELERATION)
        new_force = physics_force(target.properties["mass"], new_acc)
        self.charge_operation(target, "accelerate", kwargs, 1.0)
        target.properties["acc"] = new_acc
        target.properties["force"] = new_force
        target.properties["acceleration_persistent"] = True
        return target

    def op_decelerate(self, target, acceleration, **kwargs):
        target = self.require_object(target, "decelerate")
        for prop in ("acc", "mass", "force"):
            self.require_property(target, prop, "decelerate")
        if isinstance(acceleration, Vector3):
            if acceleration.dimension != ACCELERATION:
                raise UnitErrorML("decelerate() vector must be in m/s2")
            acceleration = require_2d_world_vector(acceleration, "decelerate() acceleration")
            new_acc = Vector3(-acceleration.x, -acceleration.y, 0, ACCELERATION)
        else:
            a = self.as_quantity(acceleration, ACCELERATION, "decelerate() acceleration")
            new_acc = Vector3(-a.value, 0, 0, ACCELERATION)
        new_force = physics_force(target.properties["mass"], new_acc)
        self.charge_operation(target, "decelerate", kwargs, 1.0)
        target.properties["acc"] = new_acc
        target.properties["force"] = new_force
        target.properties["acceleration_persistent"] = True
        return target

    def op_impulse(self, target, impulse, **kwargs):
        """Apply a physical impulse vector (change in momentum) to an object.

        This is a general mechanics primitive, not a jump/attack-specific helper.
        The impulse uses kg*m/s, adds to the object's current relativistic momentum,
        then derives a sub-light-speed velocity for a massive object.
        """
        target = self.require_object(target, "impulse")
        self.require_active_object(target, "impulse")
        for prop in ("vel", "mass", "energy", "kinetic_energy", "thermal_energy"):
            self.require_property(target, prop, "impulse")
        if target.properties.get("anchored", False):
            raise MagicErrorML("cannot apply an impulse to an anchored object; call unanchor() first")
        if not isinstance(impulse, Vector3):
            raise TypeErrorML("impulse() expects a momentum vector, for example vector3d.direction(1, 0, 0) * (10 kg*m/s)")
        if impulse.dimension != MOMENTUM:
            raise UnitErrorML(f"impulse() vector must use {MOMENTUM}")
        impulse = require_2d_world_vector(impulse, "impulse() vector")
        impulse_size = impulse.magnitude()
        if impulse_size <= 0:
            raise PhysicsErrorML("impulse() vector must be non-zero")
        mass = self.as_quantity(target.properties["mass"], KG, "impulse() target mass")
        mass_kg = float(mass.value)
        if not math.isfinite(mass_kg) or mass_kg <= 0:
            raise PhysicsErrorML("impulse() requires a target with positive finite mass")

        old_energy = self.object_energy_j(target)
        old_kinetic = target.properties["kinetic_energy"]
        old_velocity = target.properties["vel"]
        if not isinstance(old_velocity, Vector3) or old_velocity.dimension != VELOCITY:
            raise UnitErrorML("impulse() target velocity must be a velocity vector")
        old_momentum = momentum(mass, old_velocity)
        new_momentum = old_momentum + impulse
        p_size = new_momentum.magnitude()
        if p_size <= 0:
            new_velocity = Vector3(0.0, 0.0, 0.0, VELOCITY)
        else:
            # Invert p = gamma*m*v without forming p**2 or (m*c)**2 directly.
            # hypot avoids unnecessary overflow for very large yet finite impulses.
            denominator = math.hypot(mass_kg * C, p_size)
            factor = C / denominator
            new_velocity = Vector3(*(component * factor for component in new_momentum.components), VELOCITY)
        new_velocity = enforce_speed(new_velocity, massive=True)
        new_kinetic = kinetic_energy(mass, new_velocity)
        cost = abs(new_kinetic.value - old_kinetic.value) / JOULES_PER_MANA
        target.properties["vel"] = new_velocity
        target.properties["momentum"] = momentum(mass, new_velocity)
        target.properties["kinetic_energy"] = new_kinetic
        self.update_total_energy(target)
        delta_energy = self.object_energy_j(target) - old_energy
        self.record_energy_delta("impulse", target, delta_energy, source="applied impulse")
        self.charge_operation(target, "impulse", kwargs, cost)
        self._observe("entity.changed", entity=self._visual_entity(target), operation="impulse",
                      impulse=impulse.components, velocity=new_velocity.components,
                      speed_m_s=new_velocity.magnitude())
        self._record_step(f"impulse applied to {self._object_label(target)}; speed={new_velocity.magnitude():g} m/s")
        return target

    def op_velocity(self, target, velocity, **kwargs):
        target = self.require_object(target, "velocity")
        self.require_active_object(target, "velocity")
        for prop in ("vel", "mass", "energy", "kinetic_energy", "thermal_energy"):
            self.require_property(target, prop, "velocity")
        aimed_direction = None
        if isinstance(velocity, Vector3):
            if velocity.dimension != VELOCITY:
                raise UnitErrorML("velocity() vector must be in m/s")
            # Explicit velocity vectors remain available for advanced/manual control.
            vector = require_2d_world_vector(velocity, "velocity() vector")
        else:
            v = self.as_quantity(velocity, VELOCITY, "velocity() speed")
            if v.value < 0:
                raise PhysicsErrorML("velocity() speed cannot be negative")
            if self._target_context_stack:
                selected = self._target_context_stack[-1]
                from_pos = target.properties.get("pos")
                to_pos = selected.properties.get("pos")
                if not isinstance(from_pos, Vector3) or not isinstance(to_pos, Vector3):
                    raise UnitErrorML("targeted velocity requires source and target positions in metres")
                dx, dy = to_pos.x - from_pos.x, to_pos.y - from_pos.y
                distance = math.hypot(dx, dy)
                if distance <= 1e-12:
                    raise PhysicsErrorML(
                        f"cannot aim '{self._object_label(target)}' at '{self._object_label(selected)}': "
                        "they occupy the same position; give the target a distance or position"
                    )
                vector = Vector3(v.value * dx / distance, v.value * dy / distance, 0, VELOCITY)
                aimed_direction = Vector3(dx / distance, dy / distance, 0, DIMENSIONLESS)
            else:
                # Without a selected target, preserve the old scalar-speed default (+X).
                vector = Vector3(v.value, 0, 0, VELOCITY)
        vector = enforce_speed(vector, massive=target.properties["mass"].value > 0)
        old_energy = self.object_energy_j(target)
        old_kinetic = target.properties["kinetic_energy"]
        new_kinetic = kinetic_energy(target.properties["mass"], vector)
        cost = abs(new_kinetic.value - old_kinetic.value) / JOULES_PER_MANA
        # Do not alter aiming state until the requested velocity has passed all
        # speed, dimension, and numeric validation.
        if aimed_direction is not None:
            target.properties["direction"] = aimed_direction
        target.properties["vel"] = vector
        target.properties["kinetic_energy"] = new_kinetic
        target.properties["momentum"] = momentum(target.properties["mass"], vector)
        self.update_total_energy(target)
        self.record_energy_delta("velocity", target, self.object_energy_j(target) - old_energy, source="spell work")
        self.charge_operation(target, "velocity", kwargs, cost)
        return target

    def op_detect(self, target, property_name=None, **kwargs):
        if not isinstance(target, MagicObject):
            raise TypeErrorML("detect() currently expects a magical object")
        if property_name is not None:
            if not isinstance(property_name, str):
                raise TypeErrorML("detect() property name must be text")
            if property_name not in target.properties:
                raise TypeErrorML(f"detect() target has no property '{property_name}'")
        self.charge_operation(target, "detect", kwargs, 0.5)
        if property_name is None:
            return target
        return target.get(property_name)

    def op_release(self, spell):
        """Commit a spell's changes; the legacy source command is release(spell)."""
        resolved = self._resolve_spell(spell, mode="release")
        return self._run_spell_mode("release", resolved)

    def op_cast(self, spell):
        """Native-language synonym for release, with CAST-labelled records."""
        resolved = self._resolve_spell(spell, mode="cast")
        return self._run_spell_mode("release", resolved, report_label="CAST")

    def op_appraise(self, spell, presentation: str = "text"):
        """Appraise a spell by running a non-committing trial and retaining its report."""
        if presentation not in {"text", "visual"}:
            raise TypeErrorML("appraise presentation must be 'text' or 'visual'")
        resolved = self._resolve_spell(spell, mode="appraise")
        return self._run_spell_mode("post", resolved, presentation=presentation, report_label="APPRAISAL")

    def op_post(self, spell, presentation: str = "text"):
        """Trial one named spell and roll back world changes.

        ``text`` is the normal report. ``visual`` retains hypothetical scene events
        in an active recording so the optional Visualiser can replay the cast.
        Neither presentation commits world changes or opens a viewer by itself.
        """
        if presentation not in {"text", "visual"}:
            raise TypeErrorML("post presentation must be 'text' or 'visual'")
        resolved = self._resolve_spell(spell, mode="post")
        return self._run_spell_mode("post", resolved, presentation=presentation)

    def _resolve_spell(self, candidate, *, mode: str):
        if isinstance(candidate, SpellInstance):
            return candidate
        if isinstance(candidate, FunctionValue):
            if not candidate.is_spell:
                raise TypeErrorML(f"'{candidate.name}' is an ordinary function, not a spell; call it normally to calculate a value")
            if candidate.params == ["element"]:
                raise TypeErrorML(
                    f"'{candidate.name}' is a spell template; configure it first, e.g. '{candidate.name}(Fire)'"
                )
            return candidate
        if isinstance(candidate, str):
            try:
                value = self.global_env.get(candidate)
            except RuntimeErrorML:
                value = None
            if isinstance(value, (FunctionValue, SpellInstance)):
                if isinstance(value, FunctionValue) and not value.is_spell:
                    raise TypeErrorML(f"'{candidate}' is an ordinary function, not a spell; call it normally to calculate a value")
                if isinstance(value, FunctionValue) and value.params == ["element"]:
                    raise TypeErrorML(f"'{candidate}' is a spell template; configure it first, e.g. '{candidate}(Fire)'")
                return value
            raise TypeErrorML(f"{mode}() expected a named spell or configured spell instance, got {candidate!r}")
        if isinstance(candidate, MagicObject):
            raise TypeErrorML(f"{mode}() accepts a spell name only, not a magical object; use object operations for objects")
        raise TypeErrorML(f"{mode}() expects one spell name")

    def _run_spell_mode(self, mode: str, spell: FunctionValue | SpellInstance, *, presentation: str = "text", report_label: str | None = None):
        label = report_label or ("POST" if mode == "post" else "RELEASE")
        instance = spell if isinstance(spell, SpellInstance) else None
        definition = instance.definition if instance is not None else spell
        spell_name = instance.name if instance is not None else definition.name
        result = SpellResult(
            mode=mode, spell=spell_name, presentation=presentation,
            mana_used=Quantity(0, MANA), report_label=report_label or ("POST" if mode == "post" else "RELEASE"),
        )
        snapshot_roots = [self.global_env, self.active_objects, spell, *self._target_context_stack]
        snapshot = self._snapshot_runtime_state(snapshot_roots)
        observation_buffer = self._begin_observer_buffer()
        if self.observer is not None:
            self._observe("spell.started", spell=spell_name, mode=mode, presentation=presentation, committed=False)
        mana_before = self.total_mana_used
        ledger_before = len(self.energy_ledger)
        self._spell_run_stack.append(result)
        self._spell_instance_stack.append(instance)
        try:
            try:
                normalized_args = [instance.element] if instance is not None else []
                if mode == "post":
                    values = ", ".join(
                        f"{name}={self._stable_value(value)}"
                        for name, value in zip(definition.params, normalized_args)
                    ) or "no parameters"
                    print(f"[{label} {spell_name}] inputs: {values}")
                result.incant_value = self._execute_definition(definition, normalized_args)
                if self._target_context_stack:
                    self._resolve_targeted_motion(result, self._target_context_stack[-1])
                result.ok = True
                result.trace.append(f"spell {spell_name} completed")
                if mode == "post":
                    print(f"[{label} {spell_name}] spell completed")
            except MagicLangError as exc:
                active_location = getattr(self._diagnostic_context, "location", None)
                if active_location is not None:
                    exc.attach_location(*active_location)
                result.ok = False
                message = str(exc)
                result.errors.append(message)
                result.trace.append(f"ERROR: {message}")
                if mode == "post":
                    print(f"[{label} {spell_name}] ERROR: {message}")
                elif mode == "release":
                    print(f"[{label} {spell_name}] ERROR: {message}")
            except Exception as exc:
                # Do not disguise interpreter defects as ordinary spell failures.
                # Roll back this run, print diagnostics for library-hosted use, and re-raise.
                self._restore_runtime_state(snapshot)
                if self.observer is not None:
                    self._observe("spell.crashed", spell=spell_name, mode=mode, error=str(exc)[:500])
                    self._observe_scene("after_error", mode=mode, presentation=presentation)
                    self._end_observer_buffer(observation_buffer, keep_world_events=False)
                    observation_buffer = None
                if not getattr(exc, "_mana_traceback_printed", False):
                    traceback.print_exc(file=sys.stderr)
                    try:
                        setattr(exc, "_mana_traceback_printed", True)
                    except Exception:
                        pass
                raise
            result.mana_used = Quantity(max(0.0, self.total_mana_used - mana_before), MANA)
            result.energy_transfers = [dict(entry) for entry in self.energy_ledger[ledger_before:]]
        finally:
            self._spell_run_stack.pop()
            self._spell_instance_stack.pop()

        if mode == "release" and report_label == "CAST" and result.ok:
            print(f"[{label} {spell_name}] spell committed")
            print(f"[{label} {spell_name}] mana appraisal: {self._stable_value(result.mana_used)}")
        if mode == "post":
            print(f"[{label} {spell_name}] mana appraisal: {self._stable_value(result.mana_used)}")
            if result.created:
                created_summary = []
                for obj in result.created:
                    mass = obj.properties.get("mass")
                    mass_text = f", {self._stable_value(mass)}" if mass is not None else ""
                    created_summary.append(f"{self._object_label(obj)} ({obj.element}{mass_text})")
                print(f"[{label} {spell_name}] created: {', '.join(created_summary)}")
            if result.hits:
                print(f"[{label} {spell_name}] hits: {', '.join(self._stable_value(x) for x in result.hits)}")
            if result.errors:
                print(f"[{label} {spell_name}] errors: {'; '.join(result.errors)}")
            if presentation == "visual" and self.observer is None:
                print(
                    f"[{label} {spell_name}] visual replay was requested, but no Visualiser recording is active; "
                    "click the Visual button in VS Code or run with --record to view this non-committing preview"
                )

        if mode == "post" or not result.ok:
            # Keep the hypothetical result for inspection while rolling back all
            # changes to objects that existed before the trial.
            if mode == "post" and result.ok:
                preexisting_ids = {id(obj) for obj, _properties in snapshot["objects"]}
                result.incant_value = self._detach_trial_value(result.incant_value, preexisting_ids)
                result.affected = [self._detach_trial_value(obj, preexisting_ids) for obj in result.affected]
                result.hits = [self._detach_trial_value(obj, preexisting_ids) for obj in result.hits]
            self._restore_runtime_state(snapshot)
            result.committed = False
        else:
            result.committed = True
            # A committed spell materializes every still-active object it created,
            # including objects that were not returned as the final incant value.
            committed_objects = list(result.created) + list(result.affected)
            active_ids = {id(existing) for existing in self.active_objects}
            for obj in committed_objects:
                if not isinstance(obj, MagicObject) or not obj.properties.get("active", True):
                    continue
                obj_id = id(obj)
                if obj_id not in active_ids:
                    self.active_objects.append(obj)
                    active_ids.add(obj_id)
        if self.observer is not None:
            self._observe("spell.result", spell=result.spell, mode=result.mode, presentation=result.presentation, ok=result.ok,
                          committed=result.committed, errors=list(result.errors), trace=result.trace[:2000],
                          trace_truncated=len(result.trace) > 2000)
            self._observe_scene("after_" + mode, mode=mode, presentation=presentation)
            self._end_observer_buffer(
                observation_buffer,
                keep_world_events=((mode == "post" and presentation == "visual") or result.committed),
            )
        return result

    def _resolve_targeted_motion(self, result: SpellResult, selected: MagicObject) -> None:
        """Advance a targeted cast through its flight so impact is part of firing."""
        target_pos = selected.properties.get("pos")
        if not isinstance(target_pos, Vector3) or target_pos.dimension != M:
            raise UnitErrorML("selected target needs a world position in metres")
        max_flight_seconds = 0.0
        candidates = []
        for obj in result.created:
            if not isinstance(obj, MagicObject) or obj is selected or not obj.properties.get("active", True):
                continue
            pos = obj.properties.get("pos")
            vel = obj.properties.get("vel")
            if not isinstance(pos, Vector3) or not isinstance(vel, Vector3) or vel.dimension != VELOCITY:
                continue
            speed = vel.magnitude()
            if speed <= 1e-12:
                continue
            dx, dy = target_pos.x - pos.x, target_pos.y - pos.y
            distance = math.hypot(dx, dy)
            if distance <= 1e-9:
                continue
            candidates.append(obj)
            max_flight_seconds = max(max_flight_seconds, distance / speed)
        if not candidates:
            return
        # Add one simulation step so swept-circle collision can resolve contact.
        flight_seconds = max_flight_seconds + DEFAULT_TIMESTEP_SECONDS
        if flight_seconds > 60.0:
            raise PhysicsErrorML(
                "automatic target flight exceeds 60 s; use a closer target or configure motion explicitly"
            )
        self._record_step(
            f"target selected: {self._object_label(selected)}; "
            f"simulating targeted motion for {flight_seconds:g} s"
        )
        self.advance_time(Quantity(flight_seconds, S))

    def _is_runtime_operation(self, callee) -> bool:
        if getattr(callee, "__mana_runtime_operation__", False):
            return True
        return getattr(callee, "__self__", None) is self and (
            getattr(callee, "__name__", "").startswith("op_")
            or getattr(callee, "__name__", "") in {"emit_event", "advance_time"}
        )

    def _record_step(self, detail: str):
        if self.observer is not None:
            location = getattr(self._diagnostic_context, "location", None)
            payload = {"label": detail}
            if location is not None:
                payload.update(filename=location[0], line=location[1], column=location[2])
            self._observe("activity", **payload)
        if not self._spell_run_stack:
            return
        result = self._spell_run_stack[-1]
        result.trace.append(detail)
        if result.mode == "post" and self.trace_detail == "full":
            print(f"[{result.report_label or 'POST'} {result.spell}] {detail}")

    def _record_created(self, obj, reason: str = "created"):
        if not isinstance(obj, MagicObject):
            return
        object_key = obj.object_id
        if object_key not in self._world_object_ids_seen:
            if len(self._world_object_ids_seen) >= MAX_WORLD_OBJECTS_PER_RUNTIME:
                raise RuntimeErrorML(
                    f"runtime exceeded the world-object safety limit ({MAX_WORLD_OBJECTS_PER_RUNTIME:,})"
                )
            state = getattr(self._budget_context, "state", None)
            if state is not None and object_key not in state["world_ids"]:
                if state["world_objects"] >= MAX_WORLD_OBJECTS_PER_EXECUTION:
                    raise RuntimeErrorML(
                        f"program exceeded the world-object safety limit ({MAX_WORLD_OBJECTS_PER_EXECUTION:,})"
                    )
                state["world_objects"] += 1
                state["world_ids"].add(object_key)
            self._world_object_ids_seen.add(object_key)
        if not self._spell_run_stack:
            return
        result = self._spell_run_stack[-1]
        if id(obj) in result._created_ids:
            return
        result._created_ids.add(id(obj))
        result.created.append(obj)
        if self.observer is not None:
            self._observe("entity.created", entity=self._visual_entity(obj), mode=result.mode, committed=False)
        mass = obj.properties.get("mass")
        mass_text = f", {self._stable_value(mass)}" if mass is not None else ""
        if obj.element == "Mana":
            self._record_step(f"{self._object_label(obj)} takes shape")
        else:
            self._record_step(f"created {self._object_label(obj)} ({obj.element}{mass_text}; {reason})")

    @staticmethod
    def _object_label(value: MagicObject) -> str:
        return str(value.properties.get("display_name", value.element))

    @staticmethod
    def _stable_value(value):
        if isinstance(value, Quantity):
            return f"{value.value:g} {value.dimension}"
        if isinstance(value, Vector3):
            return repr(value)
        if isinstance(value, MagicObject):
            return Runtime._object_label(value)
        if isinstance(value, list):
            return "[" + ", ".join(Runtime._stable_value(v) for v in value) + "]"
        if isinstance(value, int) and not isinstance(value, bool):
            try:
                return str(value)
            except ValueError as exc:
                raise RuntimeErrorML("integer is too large to display; reduce its size before using show()") from exc
        return repr(value)

    def _call_traced_operation(self, callee, args, kwargs):
        recorder = self._spell_run_stack[-1]
        method = getattr(callee, "__name__", "operation")
        op_name = method[3:] if method.startswith("op_") else method
        object_args = []
        seen = set()
        def collect(value):
            if isinstance(value, MagicObject) and id(value) not in seen:
                seen.add(id(value))
                object_args.append(value)
            elif isinstance(value, (list, tuple)):
                for item in value:
                    collect(item)
        for item in list(args) + list(kwargs.values()):
            collect(item)
        before = [(obj, dict(obj.properties)) for obj in object_args]
        call_desc = f"{op_name}({', '.join(self._stable_value(x) for x in args)})"
        output = callee(*args, **kwargs)
        changes_found = 0
        for obj, old_props in before:
            for prop in sorted(set(old_props) | set(obj.properties)):
                old = old_props.get(prop, "<unset>")
                new_value = obj.properties.get(prop, "<unset>")
                if self._stable_value(old) != self._stable_value(new_value):
                    change = SpellChange(
                        target=self._object_label(obj), property=prop,
                        before=self._stable_value(old), after=self._stable_value(new_value),
                        operation=op_name,
                    )
                    recorder.changes.append(change)
                    if all(existing is not obj for existing in recorder.affected):
                        recorder.affected.append(obj)
                    self._record_step(repr(change))
                    changes_found += 1
            if self.observer is not None:
                self._observe("entity.changed", entity=self._visual_entity(obj), operation=op_name)
        if method == "op_combine" and isinstance(output, MagicObject):
            self._record_created(output, reason="combine result")
            rule = output.properties.get("interaction", "element interaction")
            details = output.properties.get("display_name", output.element)
            fired = f"{args[0].element} + {args[1].element} => {details} ({rule})"
            recorder.rules_fired.append(fired)
            self._record_step(f"rule fired: {fired}")
        elif method == "op_split" and isinstance(output, list):
            for item in output:
                self._record_created(item, reason="split result")
        elif isinstance(output, MagicObject) and method not in {"op_release", "op_bind", "op_move", "op_heat", "op_cool", "op_accelerate", "op_velocity", "op_shape", "op_scale", "op_rotate", "op_aim", "op_push", "op_pull", "op_anchor", "op_unanchor", "op_reflect", "op_compress", "op_expand", "op_transform", "op_decelerate", "op_dispel"}:
            if output not in object_args:
                self._record_created(output, reason=f"{op_name} result")
        if method == "emit_event" and args:
            event_name = str(args[0]).lower()
            if event_name in {"impact", "hit", "collision", "damaged", "damage"}:
                for item in args[1:]:
                    if isinstance(item, MagicObject):
                        if all(existing is not item for existing in recorder.hits):
                            recorder.hits.append(item)
                        if all(existing is not item for existing in recorder.affected):
                            recorder.affected.append(item)
                self._record_step(f"event {event_name}: {len(recorder.hits)} hit target(s) recorded")
        if changes_found == 0:
            self._record_step(f"executed {call_desc}")
        return output

    def _detach_trial_value(self, value, preexisting_ids):
        """Return a result value that preserves hypothetical state after rollback.

        Objects created during a trial remain the same objects in the result record.
        Existing objects are copied so their hypothetical state can be inspected
        without changing the real object in the runtime.
        """
        if isinstance(value, MagicObject):
            if id(value) in preexisting_ids:
                return copy.deepcopy(value)
            return value
        if isinstance(value, list):
            return [self._detach_trial_value(item, preexisting_ids) for item in value]
        if isinstance(value, tuple):
            return tuple(self._detach_trial_value(item, preexisting_ids) for item in value)
        if isinstance(value, dict):
            return {key: self._detach_trial_value(item, preexisting_ids) for key, item in value.items()}
        return value

    def _snapshot_runtime_state(self, roots):
        envs = []
        objects = []
        functions = []
        spell_instances = []
        containers = []
        seen = set()

        def walk(value):
            if value is None or isinstance(value, (str, int, float, bool, Quantity, Vector3)):
                return
            identity = id(value)
            if identity in seen:
                return
            seen.add(identity)
            if isinstance(value, Environment):
                envs.append((value, dict(value.values)))
                for item in value.values.values():
                    walk(item)
                walk(value.parent)
            elif isinstance(value, FunctionValue):
                functions.append((value, dict(value.tuned_values)))
                for tuned in value.tuned_values.values():
                    walk(tuned)
                walk(value.closure)
            elif isinstance(value, SpellInstance):
                spell_instances.append((value, value.name, dict(value.tuned_operations)))
                walk(value.definition)
                walk(value.element)
                for tuned in value.tuned_operations.values():
                    walk(tuned)
            elif isinstance(value, (ElementTypeValue,)):
                return
            elif isinstance(value, MagicObject):
                objects.append((value, dict(value.properties)))
                for item in value.properties.values():
                    walk(item)
            elif isinstance(value, list):
                containers.append((value, list(value)))
                for item in value:
                    walk(item)
            elif isinstance(value, dict):
                containers.append((value, dict(value)))
                for key, item in value.items():
                    walk(key)
                    walk(item)
            elif isinstance(value, set):
                containers.append((value, set(value)))
                for item in value:
                    walk(item)
            elif isinstance(value, tuple):
                for item in value:
                    walk(item)

        for root_value in roots:
            walk(root_value)
        timer_state = [(t, t.elapsed, t.until_next, t.active, t.interval) for t in self.timers]
        event_state = [(e, e.elapsed, e.active) for e in self.event_handlers]
        planar_registry = getattr(self, "_planar_registry", None)
        if planar_registry is not None:
            from .libraries.planar_registry import snapshot_registry
            planar_registry_state = snapshot_registry(planar_registry)
        else:
            planar_registry_state = None
        return {
            "planar_registry_present": planar_registry is not None,
            "planar_registry_state": planar_registry_state,
            "planar_channels": copy.deepcopy(getattr(self, "_planar_channels", {})),
            "custom_plane_data_present": hasattr(self, "_custom_plane_data"),
            "custom_plane_data": copy.deepcopy(getattr(self, "_custom_plane_data", {})),
            # A library loaded for the first time inside a failed transactional
            # spell must not remain cached after its registry changes roll back.
            "library_namespace_names": set(self._library_namespaces),
            "envs": envs, "objects": objects, "functions": functions,
            "spell_instances": spell_instances, "containers": containers,
            "timers": list(self.timers), "timer_state": timer_state,
            "events": list(self.event_handlers), "event_state": event_state,
            "total_mana_used": self.total_mana_used,
            "energy_ledger": [dict(entry) for entry in self.energy_ledger],
            "energy_input_j": self.energy_input_j,
            "energy_output_j": self.energy_output_j,
            "continuous_energy_batch": copy.deepcopy(self._continuous_energy_batch),
            "elapsed_virtual_time": self.elapsed_virtual_time,
            "environment_state": dict(self.environment_state),
            "weather_regions": copy.deepcopy(self.weather_regions),
            "next_weather_region_id": self._next_weather_region_id,
            "magnetic_fields": copy.deepcopy(self.magnetic_fields),
            "next_magnetic_field_id": self._next_magnetic_field_id,
            "custom_material_profiles": copy.deepcopy(self.custom_material_profiles),
            "custom_item_blueprints": copy.deepcopy(self.custom_item_blueprints),
            "custom_body_forms": copy.deepcopy(self.custom_body_forms),
            "custom_anatomy_species": copy.deepcopy(self.custom_anatomy_species),
            "custom_anatomy_organs": copy.deepcopy(self.custom_anatomy_organs),
            "custom_anatomy_systems": copy.deepcopy(self.custom_anatomy_systems),
            "custom_arcana_schools": copy.deepcopy(self.custom_arcana_schools),
            "world_settings": dict(self.world_settings),
            "last_collisions": [dict(item) for item in self.last_collisions],
        }

    def _restore_runtime_state(self, snapshot):
        for env, values in snapshot["envs"]:
            env.values.clear()
            env.values.update(values)
        for obj, properties in snapshot["objects"]:
            obj.properties.clear()
            obj.properties.update(properties)
        for function, tuned_values in snapshot.get("functions", []):
            function.tuned_values.clear()
            function.tuned_values.update(tuned_values)
        for instance, name, tuned_operations in snapshot.get("spell_instances", []):
            instance.name = name
            instance.tuned_operations.clear()
            instance.tuned_operations.update(tuned_operations)
        for container, contents in snapshot["containers"]:
            if isinstance(container, list):
                container[:] = contents
            elif isinstance(container, dict):
                container.clear()
                container.update(contents)
            elif isinstance(container, set):
                container.clear()
                container.update(contents)
        self.timers = list(snapshot["timers"])
        for timer, elapsed, until_next, active, interval in snapshot["timer_state"]:
            timer.elapsed, timer.until_next, timer.active = elapsed, until_next, active
            timer.interval = interval
        self.event_handlers = list(snapshot["events"])
        for event, elapsed, active in snapshot["event_state"]:
            event.elapsed, event.active = elapsed, active
        self.total_mana_used = snapshot["total_mana_used"]
        self.energy_ledger = [dict(entry) for entry in snapshot["energy_ledger"]]
        self.energy_input_j = snapshot["energy_input_j"]
        self.energy_output_j = snapshot["energy_output_j"]
        self._continuous_energy_batch = copy.deepcopy(snapshot.get("continuous_energy_batch"))
        self.elapsed_virtual_time = snapshot["elapsed_virtual_time"]
        self.environment_state = dict(snapshot.get("environment_state", self.environment_state))
        self.weather_regions = copy.deepcopy(snapshot.get("weather_regions", []))
        self._next_weather_region_id = snapshot.get("next_weather_region_id", self._next_weather_region_id)
        self.magnetic_fields = copy.deepcopy(snapshot.get("magnetic_fields", []))
        self._next_magnetic_field_id = snapshot.get("next_magnetic_field_id", self._next_magnetic_field_id)
        self.custom_material_profiles = copy.deepcopy(snapshot.get("custom_material_profiles", {}))
        self.custom_item_blueprints = copy.deepcopy(snapshot.get("custom_item_blueprints", {}))
        self.custom_body_forms = copy.deepcopy(snapshot.get("custom_body_forms", {}))
        self.custom_anatomy_species = copy.deepcopy(snapshot.get("custom_anatomy_species", {}))
        self.custom_anatomy_organs = copy.deepcopy(snapshot.get("custom_anatomy_organs", {}))
        self.custom_anatomy_systems = copy.deepcopy(snapshot.get("custom_anatomy_systems", {}))
        self.custom_arcana_schools = copy.deepcopy(snapshot.get("custom_arcana_schools", {}))
        self.world_settings = dict(snapshot.get("world_settings", self.world_settings))
        self.last_collisions = [dict(item) for item in snapshot.get("last_collisions", [])]
        if snapshot.get("planar_registry_present"):
            current_registry = getattr(self, "_planar_registry", None)
            if current_registry is None:
                from .libraries.planar_registry import PlaneRegistry
                current_registry = PlaneRegistry({}, {}, {}, {})
                self._planar_registry = current_registry
            from .libraries.planar_registry import restore_registry
            restore_registry(current_registry, snapshot["planar_registry_state"])
        elif hasattr(self, "_planar_registry"):
            delattr(self, "_planar_registry")
        self._planar_channels = copy.deepcopy(snapshot.get("planar_channels", {}))
        if snapshot.get("custom_plane_data_present"):
            self._custom_plane_data = copy.deepcopy(snapshot.get("custom_plane_data", {}))
        elif hasattr(self, "_custom_plane_data"):
            delattr(self, "_custom_plane_data")
        original_names = snapshot.get("library_namespace_names")
        if original_names is not None:
            for name in list(self._library_namespaces):
                if name not in original_names:
                    self._library_namespaces.pop(name, None)

    def op_bind(self, target, anchor=None, **kwargs):
        target = self.require_object(target, "bind")
        self.require_property(target, "bound", "bind")
        self.charge_operation(target, "bind", kwargs, 1.0)
        target.properties["bound"] = anchor if anchor is not None else True
        return target

    def op_combine(self, a, b, **kwargs):
        a = self.require_object(a, "combine")
        b = self.require_object(b, "combine")
        self.require_active_object(a, "combine")
        self.require_active_object(b, "combine")
        if a is b:
            raise MagicErrorML("combine() requires two distinct objects; an object cannot be combined with itself")
        self.require_allowed(a, "combine")
        self.require_allowed(b, "combine")
        for prop in ("mass", "volume", "area"):
            self.require_property(a, prop, "combine")
            self.require_property(b, prop, "combine")
        # Elemental amounts default to each object's configured intensity. These
        # values describe the interaction, not a caster budget or stored mana pool.
        a_mana = self.mana_amount(kwargs.get("mana_a", a.properties.get("mana_intensity", 1.0)), "mana_a")
        b_mana = self.mana_amount(kwargs.get("mana_b", b.properties.get("mana_intensity", 1.0)), "mana_b")
        water_obj = a if a.element == "Water" else b if b.element == "Water" else None
        if {a.element, b.element} == {"Water", "Air"} and water_obj is not None:
            self.require_property(water_obj, "temp", "combine")
        available_heat = bool(
            water_obj and "temp" in water_obj.properties
            and water_obj.properties["temp"].value > 273.15
        )
        result = interaction(a.element, a_mana, b.element, b_mana, available_heat=available_heat)

        if result.kind == "element":
            obj = MagicObject(result.name)
        elif result.kind == "material":
            obj = MagicObject(result.name)
            obj.properties["object_kind"] = "material"
            obj.properties["material"] = result.name
        else:
            obj = MagicObject("Compound")
            obj.properties["object_kind"] = "compound"
            obj.properties["display_name"] = " + ".join(result.components)

        obj.properties["display_name"] = result.name
        obj.properties["components"] = tuple(result.components)
        obj.properties["mana_intensity"] = result.mana
        obj.properties["interaction"] = result.kind
        obj.properties["ratio"] = result.ratio
        obj.properties["sources"] = (a, b)
        inherited_released_mana = float(a.properties.get("released_mana", 0.0)) + float(b.properties.get("released_mana", 0.0))
        obj.properties["released_mana"] = inherited_released_mana + result.released_mana
        new_release_energy = mana_to_energy(Quantity(result.released_mana, MANA))
        obj.properties["local_released_mana"] = result.released_mana
        obj.properties["local_released_energy"] = new_release_energy
        obj.properties["local_energy_origin"] = result.energy_origin
        obj.properties["local_energy_sources"] = ([{
            "origin": result.energy_origin or "mana_to_energy",
            "energy_j": new_release_energy.value,
        }] if new_release_energy.value > 0 else [])
        inherited_released = (
            a.properties.get("released_energy", Quantity(0, ENERGY))
            + b.properties.get("released_energy", Quantity(0, ENERGY))
        )
        obj.properties["released_energy"] = inherited_released + new_release_energy
        # Preserve each release component's origin through subsequent combinations.
        energy_sources = []
        for source_obj in (a, b):
            source_entries = source_obj.properties.get("energy_sources", [])
            if source_entries:
                energy_sources.extend(copy.deepcopy(source_entries))
            else:
                released = source_obj.properties.get("released_energy", Quantity(0, ENERGY))
                if released.value > 0:
                    energy_sources.append({
                        "origin": source_obj.properties.get("energy_origin") or "unspecified",
                        "energy_j": released.value,
                    })
        if new_release_energy.value > 0:
            energy_sources.append({
                "origin": result.energy_origin or "mana_to_energy",
                "energy_j": new_release_energy.value,
            })
        obj.properties["energy_sources"] = energy_sources
        origins = {entry["origin"] for entry in energy_sources}
        obj.properties["energy_origin"] = next(iter(origins)) if len(origins) == 1 else ("mixed" if origins else None)
        # Composition moves existing matter/energy into a new object; it does not
        # create a second copy of the inputs. Preserve their thermal energy and
        # momentum, converting lost bulk kinetic energy into heat.
        mass_a, mass_b = a.properties["mass"], b.properties["mass"]
        total_mass = mass_a + mass_b
        obj.properties["mass"] = total_mass
        obj.properties["volume"] = a.properties["volume"] + b.properties["volume"]
        obj.properties["area"] = a.properties["area"] + b.properties["area"]
        if obj.properties["volume"].value > 0:
            obj.properties["density"] = Quantity(
                total_mass.value / obj.properties["volume"].value, DENSITY
            )
        thermal_in = (
            a.properties.get("thermal_energy", Quantity(0, ENERGY)).value
            + b.properties.get("thermal_energy", Quantity(0, ENERGY)).value
        )
        momentum_a = momentum(mass_a, a.properties["vel"])
        momentum_b = momentum(mass_b, b.properties["vel"])
        total_p = Vector3(
            momentum_a.x + momentum_b.x,
            momentum_a.y + momentum_b.y,
            momentum_a.z + momentum_b.z,
            MOMENTUM,
        )
        p_mag = total_p.magnitude()
        if total_mass.value > 0:
            gamma = math.sqrt(1.0 + (p_mag / (total_mass.value * C)) ** 2)
            final_vel = Vector3(
                total_p.x / (gamma * total_mass.value),
                total_p.y / (gamma * total_mass.value),
                total_p.z / (gamma * total_mass.value),
                VELOCITY,
            )
        else:
            final_vel = Vector3(0, 0, 0, VELOCITY)
        obj.properties["vel"] = final_vel
        obj.properties["momentum"] = momentum(total_mass, final_vel)
        final_kinetic = kinetic_energy(total_mass, final_vel)
        obj.properties["kinetic_energy"] = final_kinetic
        thermal_after_motion = max(
            0.0,
            thermal_in
            + a.properties.get("kinetic_energy", Quantity(0, ENERGY)).value
            + b.properties.get("kinetic_energy", Quantity(0, ENERGY)).value
            - final_kinetic.value,
        )
        obj.properties["state"] = "solid" if result.name == "Ice" else obj.properties.get("state", "solid")
        if result.name == "ThermalRelease":
            obj.properties["state"] = "gas"
        if result.name == "Ice":
            obj.properties["temp"] = Quantity(273.15, K)
            thermal_final = total_mass.value * DEFAULT_SPECIFIC_HEAT_J_PER_KG_K * 273.15
            if thermal_after_motion + 1e-9 < thermal_final:
                raise PhysicsErrorML("not enough thermal energy is available to form Ice")
            heat_removed = thermal_after_motion - thermal_final
            obj.properties["thermal_energy"] = Quantity(thermal_final, ENERGY)
            if heat_removed > 1e-9:
                self.record_energy_delta("combine to Ice", obj, -heat_removed, source="surroundings (removed heat)")
        else:
            obj.properties["thermal_energy"] = Quantity(thermal_after_motion, ENERGY)
            temp_value = thermal_after_motion / (total_mass.value * DEFAULT_SPECIFIC_HEAT_J_PER_KG_K) if total_mass.value > 0 else 0.0
            obj.properties["temp"] = Quantity(temp_value, K)
        obj.properties["energy_state_initialized"] = True
        self.update_total_energy(obj)
        if new_release_energy.value > 0:
            self.record_energy_delta(
                "combine", obj, new_release_energy.value,
                source=result.energy_origin or "elemental interaction",
            )
        self.charge_operation(obj, "combine", kwargs, 0.0)
        a.properties["active"] = False
        b.properties["active"] = False
        return obj

    def op_separate(self, target, **kwargs):
        target = self.require_object(target, "separate")
        self.require_allowed(target, "separate")
        self.require_active_object(target, "separate")
        sources = target.properties.get("sources")
        self.charge_operation(target, "separate", kwargs, 1.0)
        if not sources:
            components = target.properties.get("components", ())
            return list(components) if components else [target]
        restored = list(sources)
        for source in restored:
            if isinstance(source, MagicObject):
                source.properties["active"] = True
                if all(existing is not source for existing in self.active_objects):
                    self.active_objects.append(source)
        # Deactivate the composite before restoring the inputs so world energy
        # is transferred, not duplicated.
        target.properties["active"] = False
        released = target.properties.get("local_released_energy", Quantity(0, ENERGY))
        if isinstance(released, Quantity) and released.value > 0:
            energy_sources = copy.deepcopy(target.properties.get("local_energy_sources", []))
            if not energy_sources:
                energy_sources = [{
                    "origin": target.properties.get("local_energy_origin") or "unspecified",
                    "energy_j": released.value,
                }]
            carrier_props = {
                "object_kind": "material", "material": "ThermalRelease",
                "display_name": "separated_thermal_release",
                "mass": Quantity(0, KG), "volume": Quantity(0, M3),
                "density": Quantity(0, DENSITY), "temp": Quantity(0, K),
                "vel": Vector3(0, 0, 0, VELOCITY),
                "thermal_energy": Quantity(0, ENERGY),
                "kinetic_energy": Quantity(0, ENERGY),
                "momentum": Vector3(0, 0, 0, MOMENTUM),
                "released_energy": released,
                "released_mana": float(target.properties.get("local_released_mana", 0.0)),
                "energy_origin": target.properties.get("local_energy_origin"),
                "energy_sources": energy_sources,
                "local_released_energy": released,
                "local_released_mana": float(target.properties.get("local_released_mana", 0.0)),
                "local_energy_origin": target.properties.get("local_energy_origin"),
                "local_energy_sources": energy_sources,
                "energy_state_initialized": True,
                "energy": released,
                "active": True,
            }
            carrier = MagicObject("ThermalRelease", carrier_props)
            self.update_total_energy(carrier)
            if all(existing is not carrier for existing in self.active_objects):
                self.active_objects.append(carrier)
            self._record_created(carrier, reason="separated released energy")
            restored.append(carrier)
        return restored

    def op_summon(self, being, source_plane=None, *, position=None, requirements=None):
        """Bring a catalogue being through its plane route using native MANA syntax."""
        if self._pure_call_depth:
            raise MagicErrorML("a directly called definition cannot summon a being; put the operation in a spell and use appraise or cast")
        # Native summon is a language construct, so the common operation loads its
        # required namespaces itself. Advanced callers may still use summoning.bring.
        if not self.global_env.contains("planes"):
            self.global_env.set_local("planes", self._load_library("planes"))
        if not self.global_env.contains("summoning"):
            self.global_env.set_local("summoning", self._load_library("summoning"))
        namespace = self.global_env.get("summoning")
        if not isinstance(namespace, LibraryNamespace):
            raise RuntimeErrorML("the built-in summoning rules are unavailable")
        bring = namespace.values.get("bring")
        if not callable(bring):
            raise RuntimeErrorML("the built-in summoning operation is unavailable")
        return bring(being, source_plane, position=position, requirements=requirements)

    def op_conjure(self, source, *, material=None, item=None, mass=None, position=None, shape=None, name=None,
                   temperature=None, density=None, state=None, velocity=None, anchored=False,
                   collidable=True, restitution=None, friction=None, drag_coefficient=None,
                   length=None, width=None, thickness=None, durability=None, payload=None, **kwargs):
        """Create physical matter, optionally using a reusable equipment blueprint.

        ``conjure steel`` creates ordinary matter. ``conjure sword, material=steel``
        creates the same physical matter with a reusable sword profile. Blueprint
        metadata never substitutes for mass, material, collision, or world physics.
        """
        if self._pure_call_depth:
            raise MagicErrorML("a directly called definition cannot conjure matter; use post() or release()")
        if kwargs:
            unknown = ", ".join(sorted(kwargs))
            raise TypeErrorML(f"conjure() got unsupported option(s): {unknown}")
        from .equipment import blueprint as get_blueprint, canonical_item
        if isinstance(source, ElementTypeValue):
            raise MagicErrorML("conjure() creates physical matter; use create for elemental manifestations and summoning for beings")
        if not isinstance(source, str) or not source.strip():
            raise TypeErrorML("conjure() source must be a material name or equipment blueprint")
        def _item_key(value):
            if not isinstance(value, str):
                return None
            standard = canonical_item(value)
            if standard is not None:
                return standard
            custom_key = " ".join(value.casefold().replace("_", " ").replace("-", " ").split())
            return custom_key if custom_key in self.custom_item_blueprints else None
        def _item_blueprint(key):
            if key in self.custom_item_blueprints:
                return copy.deepcopy(self.custom_item_blueprints[key])
            return get_blueprint(key)
        if material is not None and (not isinstance(material, str) or not material.strip()):
            raise TypeErrorML("conjure() material must be non-empty text")
        if item is not None and (not isinstance(item, str) or not item.strip()):
            raise TypeErrorML("conjure() item must be non-empty text")

        source_name = " ".join(source.strip().split())
        source_item = _item_key(source_name)
        explicit_item = _item_key(item) if item is not None else None
        if item is not None and explicit_item is None:
            raise MagicErrorML(f"unknown equipment blueprint '{item}'; inspect armory.blueprints() for supported forms")
        if source_item is not None and item is not None:
            raise MagicErrorML("conjure() cannot specify an item blueprint both as its first word and item=...")
        blueprint_name = source_item or explicit_item
        blueprint_data = _item_blueprint(blueprint_name) if blueprint_name else None
        if item is not None:
            chosen_material = material if material is not None else source_name
        elif source_item is not None:
            chosen_material = material if material is not None else blueprint_data["material"]
        else:
            if material is not None:
                raise MagicErrorML("material=... is only valid when conjuring an equipment blueprint; write 'conjure sword, material=steel'")
            chosen_material = source_name

        material_name = " ".join(chosen_material.strip().replace("_", " ").split())
        element_record = resolve_element(material_name)
        initial_material_key = " ".join(material_name.casefold().replace("-", " ").split())
        custom_profile = self.custom_material_profiles.get(initial_material_key)
        canonical_material = resolve_material(material_name)
        if element_record is not None:
            material_name = element_record.name
        elif custom_profile is not None:
            material_name = str(custom_profile["name"])
        elif canonical_material is not None:
            material_name = canonical_material
        material_key = " ".join(material_name.casefold().replace("-", " ").split())
        if material_key in {"mana", "pure mana", "puremana", "thermalrelease"}:
            raise MagicErrorML("conjure() creates ordinary matter, not pure mana or released-energy carriers; use weave mana for mana constructs")
        magical_names = {entry.casefold() for entry in (set(ELEMENTS) | set(PLANAR_ELEMENT_NAMES))}
        if material_key in magical_names and material_key not in MATERIAL_DENSITIES_KG_M3 and element_record is None:
            raise MagicErrorML("conjure() creates physical matter; use create for elemental manifestations and summoning for beings")
        profile = (dict(custom_profile) if custom_profile is not None else physical_material_profile(material_name))
        if element_record is not None and element_record.density_kg_m3 is None and density is None:
            raise MagicErrorML(f"density for {element_record.name} is not registered; provide density=... explicitly")
        if material_key not in MATERIAL_DENSITIES_KG_M3 and material_key not in self.custom_material_profiles and density is None:
            choices = ", ".join(sorted(k for k in MATERIAL_DENSITIES_KG_M3 if k in {"steel", "iron", "aluminum", "wood", "stone", "glass", "titanium", "mithril", "adamant", "water"}))
            raise MagicErrorML(f"conjure() has no density for '{material_name}'; provide density=... or use a registered material such as {choices}")
        density_kg_m3 = (float(profile["density_kg_m3"]) if profile and profile.get("density_kg_m3") is not None
                         else MATERIAL_DENSITIES_KG_M3.get(material_key, 1000.0))
        if density is not None:
            density_kg_m3 = self.as_quantity(density, DENSITY, "conjure() density").value
        if not math.isfinite(density_kg_m3) or density_kg_m3 <= 0:
            raise PhysicsErrorML("conjure() density must be finite and greater than zero")

        default_mass = float(blueprint_data["mass_kg"]) if blueprint_data else 1.0
        mass_q = Quantity(default_mass, KG) if mass is None else self.as_quantity(mass, KG, "conjure() mass")
        if not math.isfinite(mass_q.value) or mass_q.value <= 0 or mass_q.value > 1e12:
            raise PhysicsErrorML("conjure() mass must be greater than 0 and no more than 1e12 kg")
        volume_value = mass_q.value / density_kg_m3
        area_value = volume_value ** (2.0 / 3.0)
        if not all(math.isfinite(v) and v > 0 for v in (volume_value, area_value)):
            raise PhysicsErrorML("conjure() dimensions are outside the supported range")
        if position is None:
            position = Vector3(self.caster_position.x + 2.0, self.caster_position.y, 0, M)
        if not isinstance(position, Vector3) or position.dimension != M:
            raise UnitErrorML("conjure() position must be a 2D position measured in metres")
        position = require_2d_world_vector(position, "conjure() position")
        from .shapes import SUPPORTED_SHAPES
        chosen_shape = shape if shape is not None else (blueprint_data["shape"] if blueprint_data else "sphere")
        if not isinstance(chosen_shape, str) or chosen_shape.casefold() not in SUPPORTED_SHAPES:
            raise MagicErrorML("conjure() shape must be a supported MANA shape")
        chosen_shape = chosen_shape.casefold()
        if not isinstance(anchored, bool) or not isinstance(collidable, bool):
            raise TypeErrorML("conjure() anchored and collidable options must be true or false")
        if velocity is None:
            velocity = Vector3(0, 0, 0, VELOCITY)
        if not isinstance(velocity, Vector3) or velocity.dimension != VELOCITY:
            raise UnitErrorML("conjure() velocity must be a velocity vector, e.g. velocity=direction(1, 0) * (5 m/s)")
        velocity = enforce_speed(require_2d_world_vector(velocity, "conjure() velocity"), massive=True)

        def _physical_coefficient(value, default, label, maximum=2.5):
            if value is None:
                return default
            if isinstance(value, bool) or not isinstance(value, (int, float, Quantity)):
                raise TypeErrorML(f"conjure() {label} must be a finite number")
            numeric = float(self.as_quantity(value, DIMENSIONLESS, f"conjure() {label}").value) if isinstance(value, Quantity) else float(value)
            if not math.isfinite(numeric) or not 0 <= numeric <= maximum:
                raise PhysicsErrorML(f"conjure() {label} must be between 0 and {maximum:g}")
            return numeric

        object_restitution = _physical_coefficient(restitution, float(self.world_settings.get("default_restitution", 0.2)), "restitution", 1.0)
        object_friction = _physical_coefficient(friction, float(self.world_settings.get("friction_coefficient", 0.35)), "friction", 2.0)
        object_drag = _physical_coefficient(drag_coefficient, 1.0, "drag_coefficient", 2.5)
        temp_k = 293.15 if temperature is None else self.as_quantity(temperature, K, "conjure() temperature").value
        if not math.isfinite(temp_k) or temp_k < 0 or temp_k > 1e7:
            raise PhysicsErrorML("conjure() temperature must be between 0 K and 10000000 K")
        state_value = (MATERIAL_DEFAULT_STATES.get(material_key, element_record.standard_state if element_record else "solid")
                       if state is None else state)
        if not isinstance(state_value, str) or state_value.casefold() not in {"solid", "liquid", "gas", "plasma", "powder"}:
            raise MagicErrorML("conjure() state must be solid, liquid, gas, plasma, or powder")
        if state is None:
            phase = phase_for_temperature(material_name, temp_k, state_value)
            if phase is not None:
                state_value = phase
        state_value = state_value.casefold()

        def _dimension(value, field_name):
            default = float(blueprint_data[f"{field_name}_m"]) if blueprint_data else None
            if value is None:
                return default
            if not isinstance(value, Quantity) or value.dimension != M:
                raise UnitErrorML(f"conjure() {field_name} must be a distance, e.g. {field_name}=0.8 m")
            number = float(value.value)
            if not math.isfinite(number) or not 1e-4 <= number <= 1000:
                raise PhysicsErrorML(f"conjure() {field_name} must be between 0.0001 and 1000 metres")
            return number

        item_length, item_width, item_thickness = _dimension(length, "length"), _dimension(width, "width"), _dimension(thickness, "thickness")
        if blueprint_data:
            if item_length is None or item_width is None or item_thickness is None:
                raise RuntimeErrorML("equipment blueprint is missing a physical dimension")
            area_value = max(area_value, item_length * item_width)
        if durability is not None:
            if isinstance(durability, bool) or not isinstance(durability, (int, float)) or not math.isfinite(float(durability)) or not 0 < float(durability) <= 1e9:
                raise PhysicsErrorML("conjure() durability must be greater than 0 and at most 1e9")
            item_durability = float(durability)
        else:
            item_durability = float(blueprint_data["durability"]) if blueprint_data else None
        if payload is not None:
            if not isinstance(payload, str):
                raise TypeErrorML("conjure() payload must be text")
            payload = payload.strip().casefold().replace("_", " ")
            if payload not in {"none", "binding", "net", "shock", "smoke", "flare", "anchor", "burst", "acid"}:
                raise MagicErrorML("conjure() payload must be none, binding, shock, smoke, flare, anchor, burst, or acid")
            if not blueprint_data or blueprint_data["slot"] != "projectile":
                raise MagicErrorML("payload=... is supported only for projectile blueprints such as arrow, shock arrow, or smoke arrow")
        elif blueprint_data:
            payload = blueprint_data.get("payload", "none")

        composition = (copy.deepcopy(profile.get("composition_record")) if profile.get("composition_record")
                       else composition_for_material(material_name, element_record))
        if profile is None:
            profile = {"name": material_name, "density_kg_m3": density_kg_m3, "state": state_value,
                       "category": "custom material", "hardness_index": 0.35, "toughness_index": 0.4,
                       "strength_mpa": 100.0, "magnetic_response": 0.0, "electrical_conductivity": 0.2,
                       "thermal_conductivity": 0.2, "combustible": False, "brittle": False,
                       "corrosion_resistance": 0.4, "estimated": True, "source": "user-defined-density"}
        else:
            profile = dict(profile)
            profile["density_kg_m3"] = density_kg_m3
        category = str(profile.get("category", "")).casefold()
        is_metal = ("metal" in category or "alloy" in category or float(profile.get("magnetic_response", 0.0)) > 0
                    or material_key in {"iron", "steel", "stainless steel", "gold", "silver", "copper", "aluminum", "aluminium", "bronze", "brass", "lead", "tin", "titanium", "platinum", "mithril", "adamant"})
        props = {
            "object_kind": "material", "kind": "material", "material": material_name,
            "display_name": (name.strip() if isinstance(name, str) and name.strip() else blueprint_name.title().replace(" ", " ") if blueprint_data else material_name.title()),
            "mass": mass_q, "volume": Quantity(volume_value, M3), "area": Quantity(area_value, M2),
            "density": Quantity(density_kg_m3, DENSITY), "pos": position,
            "temp": Quantity(temp_k, K), "vel": velocity,
            "shape": chosen_shape, "state": state_value,
            "anchored": anchored, "collidable": collidable,
            "restitution": object_restitution, "friction": object_friction,
            "drag_coefficient": object_drag,
            "collision_radius": Quantity(max(item_length, item_width, item_thickness) / 2.0 if blueprint_data else math.sqrt(area_value / math.pi), M),
            "created_by_conjure": True, "living": False, "composition": composition,
            "atomic_number": element_record.atomic_number if element_record else None,
            "element_symbol": element_record.symbol if element_record else None,
            "melting_point_k": element_record.melting_point_k if element_record else None,
            "boiling_point_k": element_record.boiling_point_k if element_record else None,
            "estimated_material_data": bool(profile.get("estimated", False)),
            "material_properties": profile, "hardness_index": float(profile.get("hardness_index", 0.35)),
            "toughness_index": float(profile.get("toughness_index", 0.4)), "strength_mpa": float(profile.get("strength_mpa", 100.0)),
            "magnetic_response": float(profile.get("magnetic_response", 0.0)),
            "electrical_conductivity": float(profile.get("electrical_conductivity", 0.0)),
            "thermal_conductivity": float(profile.get("thermal_conductivity", 0.0)),
            "combustible": bool(profile.get("combustible", False)), "brittle": bool(profile.get("brittle", False)),
            "corrosion_resistance": float(profile.get("corrosion_resistance", 0.5)), "is_metal": is_metal,
        }
        if blueprint_data:
            props.update({
                "item_kind": "equipment" if blueprint_data["slot"] != "projectile" else "projectile",
                "equipment_blueprint": blueprint_name,
                "equipment_slot": blueprint_data["slot"],
                "length_m": item_length, "width_m": item_width, "thickness_m": item_thickness,
                "damage_multiplier": float(blueprint_data.get("damage_multiplier", 1.0)),
                "armour_rating": float(blueprint_data.get("armour_rating", 0.0)),
                "attack_style": blueprint_data.get("attack_style"), "launch_speed_m_s": blueprint_data.get("launch_speed_m_s"),
                "payload": payload or "none", "durability": item_durability, "max_durability": item_durability,
                "equipped_to": None,
            })
        elif item_durability is not None:
            props["durability"] = item_durability
            props["max_durability"] = item_durability
        obj = MagicObject("Compound")
        obj.properties.update(props)
        self.update_energy(obj)
        creation_cost = matter_to_mana(mass_q).value
        obj.properties["creation_mana_cost"] = creation_cost
        self.charge_mana(creation_cost, reason=f"conjure {material_name}", target=obj)
        self.record_energy_delta(f"conjure {material_name}", obj, self.object_energy_j(obj), source="matter manifestation")
        self._record_created(obj, reason=f"conjured {'equipment ' + blueprint_name if blueprint_data else 'material ' + material_name}")
        self._observe("magic.effect", effect="construct_formed", entity=self._visual_entity(obj),
                      position=[position.x, position.y], shape=chosen_shape, conjured=True,
                      item=blueprint_name, material=material_name)
        return obj

    def op_transmute(self, target, material, *, preserve_mass=True, density=None, state=None, **kwargs):
        """Change composition and refresh every material-derived world property.

        By default mass is conserved and volume/shape dimensions scale with the
        destination density. All user-controlled values are validated before
        changing the object or recording the operation.
        """
        target = self.require_object(target, "transmute")
        self.require_active_object(target, "transmute")
        self.require_property(target, "material", "transmute")
        if target.element in {"Mana", "ThermalRelease"}:
            raise MagicErrorML("transmute() requires matter; woven mana and released-energy carriers are not materials")
        if not isinstance(material, str) or not material.strip():
            raise TypeErrorML("transmute() material must be a non-empty text name")
        if not isinstance(preserve_mass, bool):
            raise TypeErrorML("transmute() preserve_mass must be true or false")
        if state is not None and (not isinstance(state, str) or state.casefold() not in {"solid", "liquid", "gas", "plasma", "powder"}):
            raise MagicErrorML("transmute() state must be solid, liquid, gas, plasma, or powder")

        material_name = " ".join(material.strip().replace("_", " ").split())
        element_record = resolve_element(material_name)
        initial_material_key = " ".join(material_name.casefold().replace("-", " ").split())
        custom_profile = self.custom_material_profiles.get(initial_material_key)
        canonical = resolve_material(material_name)
        if element_record is not None:
            material_name = element_record.name
        elif custom_profile is not None:
            material_name = str(custom_profile["name"])
        elif canonical is not None:
            material_name = canonical
        material_key = " ".join(material_name.casefold().replace("-", " ").split())
        profile = dict(custom_profile) if custom_profile is not None else physical_material_profile(material_name)
        if density is not None:
            density_value = self.as_quantity(density, DENSITY, "transmute() density").value
        elif element_record is not None:
            density_value = element_record.density_kg_m3
        elif profile is not None:
            density_value = profile.get("density_kg_m3")
        else:
            density_value = MATERIAL_DENSITIES_KG_M3.get(material_key)
        if density_value is None:
            raise MagicErrorML(f"transmute() has no registered density for '{material_name}'; provide density=... or use a registered material/periodic-table element")
        if not math.isfinite(float(density_value)) or float(density_value) <= 0:
            raise PhysicsErrorML("transmute() density must be finite and greater than zero")
        density_value = float(density_value)

        # Unknown-but-explicitly-densified materials are valid custom matter, but
        # they receive a clearly estimated generic profile instead of stale data.
        if profile is None:
            profile = {
                "name": material_name, "density_kg_m3": density_value, "state": "solid",
                "category": "custom material", "hardness_index": 0.35,
                "toughness_index": 0.40, "strength_mpa": 100.0,
                "magnetic_response": 0.0, "electrical_conductivity": 0.2,
                "thermal_conductivity": 0.2, "combustible": False, "brittle": False,
                "corrosion_resistance": 0.4, "estimated": True,
                "source": "user-defined-density",
            }
        else:
            profile = dict(profile)
            profile["density_kg_m3"] = density_value

        old_energy = self.object_energy_j(target)
        old_mass = self.as_quantity(target.properties.get("mass"), KG, "transmute() target mass")
        old_volume = self.as_quantity(target.properties.get("volume"), M3, "transmute() target volume")
        old_area = self.as_quantity(target.properties.get("area"), M2, "transmute() target area")
        if old_mass.value <= 0 or old_volume.value <= 0 or old_area.value <= 0:
            raise PhysicsErrorML("transmute() requires positive mass, volume, and area")
        if preserve_mass:
            new_mass = old_mass.value
            new_volume = new_mass / density_value
        else:
            new_volume = old_volume.value
            new_mass = new_volume * density_value
        if not all(math.isfinite(v) and v > 0 for v in (new_volume, new_mass)):
            raise PhysicsErrorML("transmute() result is outside the supported physical range")
        scale = (new_volume / old_volume.value) ** (1.0 / 3.0)
        new_area = max(new_volume ** (2.0 / 3.0), old_area.value * scale * scale)
        new_state = state.casefold() if state is not None else MATERIAL_DEFAULT_STATES.get(material_key, profile.get("state", element_record.standard_state if element_record else "solid"))

        # Record the operation only after every destination field is validated.
        self.charge_operation(target, "transmute", kwargs, 1.0)
        props = target.properties
        old_hardness_index = max(0.05, float(props.get("hardness_index", 0.35)))
        props["material"] = material_name
        props["composition"] = (copy.deepcopy(profile.get("composition_record")) if profile.get("composition_record")
                                 else composition_for_material(material_name, element_record))
        props["atomic_number"] = element_record.atomic_number if element_record else None
        props["element_symbol"] = element_record.symbol if element_record else None
        props["melting_point_k"] = element_record.melting_point_k if element_record else None
        props["boiling_point_k"] = element_record.boiling_point_k if element_record else None
        props["estimated_material_data"] = bool(profile.get("estimated", False) or (element_record and element_record.estimated_density))
        props["mass"] = Quantity(new_mass, KG)
        props["volume"] = Quantity(new_volume, M3)
        props["area"] = Quantity(new_area, M2)
        props["density"] = Quantity(density_value, DENSITY)
        props["state"] = new_state
        props["material_properties"] = dict(profile)
        props["hardness_index"] = float(profile.get("hardness_index", 0.35))
        props["toughness_index"] = float(profile.get("toughness_index", 0.4))
        props["strength_mpa"] = float(profile.get("strength_mpa", 100.0))
        props["magnetic_response"] = float(profile.get("magnetic_response", 0.0))
        props["electrical_conductivity"] = float(profile.get("electrical_conductivity", 0.0))
        props["thermal_conductivity"] = float(profile.get("thermal_conductivity", 0.0))
        props["combustible"] = bool(profile.get("combustible", False))
        props["brittle"] = bool(profile.get("brittle", False))
        props["corrosion_resistance"] = float(profile.get("corrosion_resistance", 0.5))
        category = str(profile.get("category", "")).casefold()
        props["is_metal"] = ("metal" in category or "alloy" in category or props["magnetic_response"] > 0
                              or material_key in {"iron", "steel", "stainless steel", "gold", "silver", "copper", "aluminum", "bronze", "brass", "lead", "tin", "titanium", "platinum", "mithril", "adamant"})
        for dim_name in ("length_m", "width_m", "thickness_m"):
            dim_value = props.get(dim_name)
            if isinstance(dim_value, (int, float)) and math.isfinite(float(dim_value)) and dim_value > 0:
                props[dim_name] = float(dim_value) * scale
        radius = props.get("collision_radius")
        if isinstance(radius, Quantity) and radius.dimension == M and radius.value > 0:
            props["collision_radius"] = Quantity(radius.value * scale, M)
        if props.get("item_kind"):
            hardness_scale = max(0.35, min(2.0, float(profile.get("hardness_index", 0.35)) / old_hardness_index))
            if props.get("max_durability") is not None:
                props["max_durability"] = max(1.0, float(props["max_durability"]) * math.sqrt(hardness_scale))
                props["durability"] = min(float(props.get("durability", props["max_durability"])), props["max_durability"])
        props["hardness_index_before_transmute"] = props["hardness_index"]
        self.update_energy(target)
        self._apply_material_phase_law(target)
        self.record_energy_delta(f"transmute to {material_name}", target, self.object_energy_j(target) - old_energy, source="transmutation work")
        self._observe("entity.changed", entity=self._visual_entity(target), operation="transmute", material=material_name)
        self._observe("magic.effect", effect="transformation", operation="transmute", entity=self._visual_entity(target), material=material_name)
        return target

    def op_transfigure(self, target, form, *, scale=1.0, **kwargs):
        """Change an object's represented form while retaining the same physical entity."""
        target = self.require_object(target, "transfigure")
        self.require_active_object(target, "transfigure")
        self.require_property(target, "shape", "transfigure")
        props = target.properties
        body_state = str(props.get("life_state", "alive")).casefold()
        is_living = (bool(props.get("living", False)) or props.get("object_kind") in {"being", "living"}
                     or props.get("kind") in {"being", "living", "creature"}) and body_state != "dead"
        is_conjured_matter = bool(props.get("created_by_conjure", False))
        if not (is_living or is_conjured_matter):
            raise MagicErrorML("transfigure() works on living beings or matter made by conjure(); use shape() to change ordinary object geometry")
        if not isinstance(form, str) or not form.strip():
            raise TypeErrorML("transfigure() form must be non-empty text")
        form_key = " ".join(form.strip().casefold().split())
        forms = {
            "wizard": "humanoid", "mage": "humanoid", "person": "humanoid", "human": "humanoid",
            "humanoid": "humanoid", "knight": "knight", "statue": "knight", "guard": "knight",
            "bird": "bird", "raven": "bird", "eagle": "bird", "snake": "serpent", "serpent": "serpent",
            "wolf": "beast", "hound": "beast", "beast": "beast", "golem": "golem", "critter": "beast",
        }
        # A named species profile is a complete body template, not just a visual
        # label. Prefer an explicitly registered physiology form, then resolve a
        # built-in/custom anatomy species so transfiguration can carry the full
        # organ inventory, systems, traits and hybrid metadata into the entity.
        anatomy_template = None
        anatomy_species_key = None
        if form_key in self.custom_body_forms:
            forms[form_key] = form_key
        else:
            from .libraries.anatomy_data import SPECIES as ANATOMY_SPECIES, SPECIES_ALIASES
            requested_species_key = form_key.replace(" ", "_")
            candidate_key = self.custom_anatomy_species.get(requested_species_key)
            if candidate_key is not None:
                anatomy_species_key = requested_species_key
                anatomy_template = candidate_key
            else:
                canonical = SPECIES_ALIASES.get(requested_species_key, SPECIES_ALIASES.get(form_key, requested_species_key))
                if canonical in self.custom_anatomy_species:
                    anatomy_species_key = canonical
                    anatomy_template = self.custom_anatomy_species[canonical]
                elif canonical in ANATOMY_SPECIES:
                    anatomy_species_key = canonical
                    anatomy_template = ANATOMY_SPECIES[canonical]
            if isinstance(anatomy_template, dict):
                profile = anatomy_template
                from .libraries.anatomy import _movement_capabilities as infer_movement_capabilities
                movement_capabilities = list(profile.get("movement_capabilities", [])) or infer_movement_capabilities(profile)
                declared_mode = str(profile.get("movement_mode", "custom")).casefold()
                if declared_mode in {"terrestrial", "flight-capable", "swim-capable", "slither-capable", "amphibious", "burrowing", "climbing", "gliding", "custom", "stationary"}:
                    movement_mode = declared_mode
                elif any("fly" in item or "flight" in item for item in movement_capabilities):
                    movement_mode = "flight-capable"
                elif any("swim" in item or "dive" in item for item in movement_capabilities):
                    movement_mode = "swim-capable"
                elif any("slither" in item for item in movement_capabilities):
                    movement_mode = "slither-capable"
                elif any("burrow" in item for item in movement_capabilities):
                    movement_mode = "burrowing"
                elif any("climb" in item for item in movement_capabilities):
                    movement_mode = "climbing"
                else:
                    movement_mode = "custom"
                anatomy_template = {
                    "name": anatomy_species_key.replace("_", " "),
                    "label": profile.get("label", anatomy_species_key.replace("_", " ").title()),
                    "organs": list(profile.get("organ_names", [])),
                    "systems": copy.deepcopy(profile.get("systems", {})),
                    "movement_mode": movement_mode,
                    "movement_capabilities": movement_capabilities,
                    "trait_factors": copy.deepcopy(profile.get("traits", {})),
                    "anatomy_species_id": anatomy_species_key,
                    "components": copy.deepcopy(profile.get("components", [anatomy_species_key])),
                    "component_profiles": copy.deepcopy(profile.get("component_profiles", [])),
                    "component_sources": copy.deepcopy(profile.get("component_sources", {})),
                    "composition_warnings": copy.deepcopy(profile.get("composition_warnings", [])),
                    "skeleton_type": profile.get("skeleton", {}).get("type", "custom") if isinstance(profile.get("skeleton"), dict) else "custom",
                    "thermoregulation": profile.get("thermoregulation", "custom"),
                    "simulation": copy.deepcopy(profile.get("simulation", {})),
                    "circulation": copy.deepcopy(profile.get("circulation", {})),
                    "respiration": copy.deepcopy(profile.get("respiration", {})),
                    "digestion": copy.deepcopy(profile.get("digestion", {})),
                    "blood": copy.deepcopy(profile.get("blood", {})),
                    "integument": copy.deepcopy(profile.get("integument", {})),
                    "reproduction": copy.deepcopy(profile.get("reproduction", {})),
                }
                forms[form_key] = anatomy_species_key.replace("_", " ")
        if form_key not in forms:
            custom = ", ".join(sorted(self.custom_body_forms))
            suffix = f" Custom forms: {custom}." if custom else ""
            raise MagicErrorML("unsupported transfiguration form; choose humanoid, wizard, knight, bird, serpent, beast, or golem. Use physiology.define_form() or anatomy.define_species() to register a body form, or shape() for geometric forms." + suffix)
        if isinstance(scale, Quantity) and scale.dimension != DIMENSIONLESS:
            raise UnitErrorML("transfigure() scale must be dimensionless")
        try:
            scale_value = scale.value if isinstance(scale, Quantity) else float(scale)
        except (TypeError, ValueError, OverflowError) as exc:
            raise TypeErrorML("transfigure() scale must be a finite dimensionless number") from exc
        if isinstance(scale, bool) or not math.isfinite(scale_value) or not 0.05 <= scale_value <= 20:
            raise PhysicsErrorML("transfigure() scale must be between 0.05 and 20")
        self.charge_operation(target, "transfigure", kwargs, 1.0)
        # Transfiguration changes the entity's represented living/constructed form;
        # the underlying collision geometry remains controlled by shape().
        target.properties["visual_form"] = forms[form_key]
        if is_living:
            from .libraries.physiology import apply_transfigured_form
            templates = copy.deepcopy(self.custom_body_forms)
            if isinstance(anatomy_template, dict):
                templates[forms[form_key]] = anatomy_template
            apply_transfigured_form(target, forms[form_key], now=self.elapsed_virtual_time, templates=templates)
        current_visual_scale = float(target.properties.get("visual_scale", 1.0))
        target.properties["visual_scale"] = max(0.05, min(20.0, current_visual_scale * scale_value))
        if abs(scale_value - 1.0) > 1e-12:
            self.op_scale(target, scale_value)
        if is_living and isinstance(anatomy_template, dict):
            simulation = anatomy_template.get("simulation", {})
            if isinstance(simulation, dict) and simulation.get("body_mass_kg") is not None:
                self.apply_body_physical_profile(target, simulation, reset_temperature=True)
        self._observe("magic.effect", effect="transformation", operation="transfigure",
                      entity=self._visual_entity(target), form=forms[form_key])
        return target

    def op_transform(self, target, state, **kwargs):
        target = self.require_object(target, "transform")
        self.require_property(target, "state", "transform")
        if not isinstance(state, str):
            raise TypeErrorML("transform() state must be text")
        state = state.strip().casefold()
        allowed = {"solid", "liquid", "gas", "plasma", "powder"}
        if state not in allowed:
            raise MagicErrorML(f"unsupported matter state '{state}'")
        if state == "powder" and target.properties.get("powderable", True) is not True:
            raise MagicErrorML(f"{self._object_label(target)} is not defined as powderable")
        self.charge_operation(target, "transform", kwargs, 1.0)
        # Powder denotes a powder aggregate: its mass and energy remain on the
        # same object. This is not a destructive deletion or a mass-splitting op.
        target.properties["state"] = state
        return target

    def op_compress(self, target, pressure_value, **kwargs):
        target = self.require_object(target, "compress")
        self.require_property(target, "pressure", "compress")
        p = self.as_quantity(pressure_value, PRESSURE, "compress() pressure")
        if p.value < 0:
            raise PhysicsErrorML("absolute pressure cannot be negative")
        self.charge_operation(target, "compress", kwargs, 1.0)
        target.properties["pressure"] = p
        return target

    def op_expand(self, target, volume_value, **kwargs):
        target = self.require_object(target, "expand")
        self.require_property(target, "volume", "expand")
        v = self.as_quantity(volume_value, M3, "expand() volume")
        if v.value < 0:
            raise PhysicsErrorML("volume cannot be negative")
        self.charge_operation(target, "expand", kwargs, 1.0)
        target.properties["volume"] = v
        return target

    def op_show(self, *values, separator=" "):
        # Internal terminal output uses the host runtime; Mana source calls show().
        if not isinstance(separator, str):
            raise TypeErrorML("show() separator must be text")
        chunks: list[str] = []
        char_count = 0
        for index, value in enumerate(values):
            if index:
                chunks.append(separator)
                char_count += len(separator)
            remaining = max(0, MAX_DISPLAY_CHARS - char_count)
            if remaining <= 0:
                chunks.append("…")
                break
            rendered = self.display_value(value)
            if len(rendered) > remaining:
                chunks.append(rendered[:remaining] + "…")
                char_count += remaining + 1
                break
            chunks.append(rendered)
            char_count += len(rendered)
        line = "".join(chunks)
        budget = getattr(self._budget_context, "state", None)
        if budget is not None:
            addition = len(line) + 1
            output_total = budget["output_chars"] + addition
            runtime_output_total = self._runtime_output_chars + addition
            if output_total > MAX_CUMULATIVE_OUTPUT_CHARS:
                raise RuntimeErrorML(
                    f"program exceeded the cumulative output safety limit "
                    f"({MAX_CUMULATIVE_OUTPUT_CHARS:,} characters)"
                )
            if runtime_output_total > MAX_RUNTIME_CUMULATIVE_OUTPUT_CHARS:
                raise RuntimeErrorML(
                    f"runtime exceeded its cumulative output safety limit "
                    f"({MAX_RUNTIME_CUMULATIVE_OUTPUT_CHARS:,} characters)"
                )
            budget["output_chars"] = output_total
            self._runtime_output_chars = runtime_output_total
        if self.observer is not None and self._spell_run_stack and self._spell_run_stack[-1].mode == "post":
            self._observe("preview.output", text=line[:2000], label="PREVIEW")
        print(line)
        return None

    @staticmethod
    def display_value(value):
        """Render values with shared character/item/depth budgets and cycle protection."""
        parts: list[str] = []
        state = {"chars": 0, "items": 0, "seen": set(), "truncated": False}

        def emit(text: str) -> None:
            if state["chars"] >= MAX_DISPLAY_CHARS:
                state["truncated"] = True
                return
            remaining = MAX_DISPLAY_CHARS - state["chars"]
            if len(text) > remaining:
                parts.append(text[:remaining])
                state["chars"] += remaining
                state["truncated"] = True
                return
            parts.append(text)
            state["chars"] += len(text)

        def render(item, depth: int = 0, repr_mode: bool = False) -> None:
            if state["chars"] >= MAX_DISPLAY_CHARS or state["items"] >= MAX_DISPLAY_ITEMS:
                state["truncated"] = True
                return
            state["items"] += 1
            if depth > MAX_DISPLAY_DEPTH:
                emit("…")
                return
            if isinstance(item, SpellResult):
                emit(f"SpellResult: {item.spell}\nmode: {item.mode}\nok: {item.ok}\ncommitted: {item.committed}\n")
                for label, child in (
                    ("incant_value", item.incant_value), ("created", item.created),
                    ("affected", item.affected), ("changes", item.changes),
                    ("hits", item.hits), ("mana_cost_readout", item.mana_used),
                    ("rules_fired", item.rules_fired), ("errors", item.errors), ("trace", item.trace),
                ):
                    emit(f"{label}: ")
                    render(child, depth + 1)
                    emit("\n")
                return
            if isinstance(item, (list, tuple, dict, set)):
                identity = id(item)
                if identity in state["seen"]:
                    emit("…" if not repr_mode else "'…'")
                    return
                state["seen"].add(identity)
                is_mapping = isinstance(item, dict)
                if is_mapping:
                    emit("{")
                    iterable = item.items()
                elif isinstance(item, set):
                    emit("{" if item else "set()")
                    iterable = ((v, None) for v in item)
                else:
                    emit("[" if isinstance(item, list) else "(")
                    iterable = ((v, None) for v in item)
                count_items = 0
                try:
                    for key, mapped in iterable:
                        if count_items:
                            emit(", ")
                        if is_mapping:
                            emit(repr(key) + ": ")
                            render(mapped, depth + 1, True)
                        else:
                            render(key, depth + 1, isinstance(item, set) or repr_mode)
                        count_items += 1
                        if count_items >= MAX_DISPLAY_ITEMS or state["chars"] >= MAX_DISPLAY_CHARS:
                            if len(item) > count_items:
                                emit(", …")
                                state["truncated"] = True
                            break
                    if isinstance(item, list):
                        emit("]")
                    elif isinstance(item, tuple):
                        if len(item) == 1 and count_items == 1:
                            emit(",")
                        emit(")")
                    elif isinstance(item, dict) or isinstance(item, set) and len(item) > 0:
                        emit("}")
                finally:
                    state["seen"].discard(identity)
                return
            try:
                text = repr(item) if repr_mode else str(item)
            except Exception:
                text = f"<{type(item).__name__}>"
            if isinstance(item, int) and not isinstance(item, bool):
                # Python can reject extremely large decimal conversions depending
                # on interpreter limits; emit a MANA error instead of a host trace.
                try:
                    text = str(item)
                except ValueError as exc:
                    raise RuntimeErrorML("integer is too large to display; reduce its size before using show()") from exc
            emit(text)

        render(value)
        if state["truncated"] and state["chars"] < MAX_DISPLAY_CHARS:
            emit("…")
        return "".join(parts)

    def op_active_objects(self):
        """Return active object values known to the current runtime, without a renderer."""
        objects = self._collect_physics_objects()
        active_count = sum(1 for obj in objects if obj.properties.get("active", True))
        self._charge_allocation(active_count, "world-object reference")
        return [obj for obj in objects if obj.properties.get("active", True)]

    def op_last_collisions(self):
        """Return readable summaries of recent physical contacts for inspection."""
        return [
            f"{item['object_a']} hit {item['object_b']}: impact={item['impact_energy_j']:g} J, "
            f"converted_to_heat={item['converted_to_heat_j']:g} J, time={item['time_s']:g} s"
            for item in self.last_collisions
        ]

    def op_direction(self, x, y, z=0):
        """Create a dimensionless direction vector from numeric components."""
        converted = []
        for value in (x, y, z):
            if isinstance(value, Quantity):
                if value.dimension != DIMENSIONLESS:
                    raise UnitErrorML("direction() components must be dimensionless")
                converted.append(value.value)
            elif isinstance(value, bool) or not isinstance(value, (int, float)):
                raise TypeErrorML("direction() components must be numbers")
            else:
                try:
                    numeric_value = float(value)
                except (OverflowError, ValueError) as exc:
                    raise PhysicsErrorML("direction() component is outside the supported numeric range") from exc
                if not math.isfinite(numeric_value):
                    raise PhysicsErrorML("direction() components must be finite")
                converted.append(numeric_value)
        vector = Vector3(*converted, dimension=DIMENSIONLESS)
        if vector.magnitude() == 0:
            raise PhysicsErrorML("direction() cannot be the zero vector")
        normalized = vector.normalized()
        return Vector3(normalized.x, normalized.y, normalized.z, DIMENSIONLESS)

    def op_aim(self, target, direction, **kwargs):
        target = self.require_object(target, "aim")
        self.require_property(target, "direction", "aim")
        if target.properties.get("anchored", False):
            raise MagicErrorML("cannot aim an anchored object; call unanchor() first")
        if not isinstance(direction, Vector3):
            raise TypeErrorML("aim() direction must be a vector created by direction()")
        direction = require_2d_world_vector(direction, "aim() direction")
        if direction.magnitude() == 0:
            raise PhysicsErrorML("aim() direction cannot be zero")
        self.charge_operation(target, "aim", kwargs, 0.5)
        norm = direction.normalized()
        target.properties["direction"] = Vector3(norm.x, norm.y, norm.z, DIMENSIONLESS)
        return target.properties["direction"]

    def _apply_force(self, target, force_value, direction, operation, kwargs, duration_seconds: float = 1.0):
        target = self.require_object(target, operation)
        self.require_active_object(target, operation)
        for prop in ("force", "acc", "mass", "vel", "kinetic_energy", "energy", "thermal_energy"):
            self.require_property(target, prop, operation)
        if target.properties.get("anchored", False):
            raise MagicErrorML(f"cannot {operation} an anchored object; call unanchor() first")
        force_q = self.as_quantity(force_value, FORCE, f"{operation}() force")
        if isinstance(duration_seconds, bool) or not isinstance(duration_seconds, (int, float)):
            raise PhysicsErrorML(f"{operation}() duration must be between 0 and {MAX_PERSISTENCE_SECONDS:g} seconds")
        try:
            duration_seconds = float(duration_seconds)
        except (OverflowError, ValueError) as exc:
            raise PhysicsErrorML(f"{operation}() duration is outside the supported numeric range") from exc
        if not math.isfinite(duration_seconds) or duration_seconds < 0 or duration_seconds > MAX_PERSISTENCE_SECONDS:
            raise PhysicsErrorML(f"{operation}() duration must be between 0 and {MAX_PERSISTENCE_SECONDS:g} seconds")
        if force_q.value < 0:
            raise PhysicsErrorML(f"{operation}() force magnitude cannot be negative")
        if not isinstance(direction, Vector3):
            raise TypeErrorML(f"{operation}() direction must be a vector")
        direction = require_2d_world_vector(direction, f"{operation}() direction")
        if direction.magnitude() == 0:
            raise PhysicsErrorML(f"{operation}() direction cannot be zero")
        unit = direction.normalized()
        unit = Vector3(unit.x, unit.y, 0, DIMENSIONLESS)
        force_vector = unit.scaled(force_q.value, FORCE)
        mass = target.properties["mass"].value
        if mass <= 0:
            raise PhysicsErrorML(f"{operation}() target must have positive mass")
        acceleration = Vector3(
            force_vector.x / mass, force_vector.y / mass, 0, ACCELERATION
        )
        old_energy = self.object_energy_j(target)
        target.properties["force"] = force_vector
        target.properties["acc"] = acceleration
        target.properties["acceleration_persistent"] = False
        # The standalone interpreter applies this as a one-second action impulse now.
        new_velocity = Vector3(
            target.properties["vel"].x + acceleration.x * duration_seconds,
            target.properties["vel"].y + acceleration.y * duration_seconds,
            0,
            VELOCITY,
        )
        target.properties["vel"] = enforce_speed(new_velocity, massive=mass > 0)
        target.properties["kinetic_energy"] = kinetic_energy(target.properties["mass"], target.properties["vel"])
        target.properties["momentum"] = momentum(target.properties["mass"], target.properties["vel"])
        self.update_total_energy(target)
        delta_energy = self.object_energy_j(target) - old_energy
        self.record_energy_delta(operation, target, delta_energy, source="spell work")
        self.charge_operation(target, operation, kwargs, abs(delta_energy) / JOULES_PER_MANA)
        return target

    def op_push(self, target, force_value, direction=None, **kwargs):
        target = self.require_object(target, "push")
        if direction is None:
            direction = target.properties.get("direction")
        return self._apply_force(target, force_value, direction, "push", kwargs)

    def op_pull(self, target, source, force_value, **kwargs):
        target = self.require_object(target, "pull")
        source = self.require_object(source, "pull")
        target_pos, source_pos = target.properties.get("pos"), source.properties.get("pos")
        if not isinstance(target_pos, Vector3) or not isinstance(source_pos, Vector3):
            raise TypeErrorML("pull() needs position vectors on both objects")
        direction = Vector3(source_pos.x-target_pos.x, source_pos.y-target_pos.y, source_pos.z-target_pos.z, M)
        return self._apply_force(target, force_value, direction, "pull", kwargs)

    def op_rotate(self, target, angle, **kwargs):
        target = self.require_object(target, "rotate")
        self.require_property(target, "rot", "rotate")
        if isinstance(angle, Quantity):
            if angle.dimension != DIMENSIONLESS:
                raise UnitErrorML("rotate() angle is dimensionless and interpreted in radians")
            angle = angle.value
        if isinstance(angle, bool) or not isinstance(angle, (int, float)):
            raise TypeErrorML("rotate() angle must be a finite number of radians")
        try:
            angle = float(angle)
        except (OverflowError, ValueError) as exc:
            raise PhysicsErrorML("rotate() angle is outside the supported numeric range") from exc
        if not math.isfinite(angle):
            raise TypeErrorML("rotate() angle must be a finite number of radians")
        self.charge_operation(target, "rotate", kwargs, max(0.1, abs(angle) * 0.1))
        target.properties["rot"] = (target.properties["rot"] + angle) % (2 * math.pi)
        return Quantity(target.properties["rot"], DIMENSIONLESS)

    def op_scale(self, target, factor, **kwargs):
        target = self.require_object(target, "scale")
        for prop in ("scale", "mass", "volume", "area", "density"):
            self.require_property(target, prop, "scale")
        if isinstance(factor, Quantity):
            if factor.dimension != DIMENSIONLESS:
                raise UnitErrorML("scale() factor must be dimensionless")
            factor = factor.value
        if isinstance(factor, bool) or not isinstance(factor, (int, float)):
            raise PhysicsErrorML("scale() factor must be finite and greater than zero")
        try:
            factor = float(factor)
        except (OverflowError, ValueError) as exc:
            raise PhysicsErrorML("scale() factor is outside the supported numeric range") from exc
        if not math.isfinite(factor) or factor <= 0:
            raise PhysicsErrorML("scale() factor must be finite and greater than zero")
        current_scale = target.properties["scale"]
        try:
            new_scale = current_scale * factor
            new_volume = target.properties["volume"].value * factor ** 3
            new_area = target.properties["area"].value * factor ** 2
            if not math.isfinite(new_scale) or not math.isfinite(new_volume) or not math.isfinite(new_area):
                raise PhysicsErrorML("scale() result is outside the supported numeric range")
            if new_volume <= 0:
                raise PhysicsErrorML("scale() would reduce volume to zero; choose a larger factor")
            volume_q = Quantity(new_volume, M3)
            area_q = Quantity(new_area, M2)
            density_q = Quantity(target.properties["mass"].value / new_volume, DENSITY)
            explicit_radius = target.properties.get("collision_radius")
            radius_q = None
            if isinstance(explicit_radius, Quantity) and explicit_radius.value > 0:
                radius_q = Quantity(explicit_radius.value * factor, M)
        except (OverflowError, ValueError) as exc:
            raise PhysicsErrorML("scale() result is outside the supported numeric range") from exc
        self.charge_operation(target, "scale", kwargs, max(0.1, abs(factor - 1.0)))
        target.properties["scale"] = new_scale
        target.properties["volume"] = volume_q
        target.properties["area"] = area_q
        if radius_q is not None:
            target.properties["collision_radius"] = radius_q
        target.properties["density"] = density_q
        return target

    def op_reflect(self, target, normal, **kwargs):
        target = self.require_object(target, "reflect")
        self.require_active_object(target, "reflect")
        self.require_property(target, "vel", "reflect")
        if not isinstance(normal, Vector3) or normal.magnitude() == 0:
            raise TypeErrorML("reflect() needs a non-zero direction vector as surface normal")
        normal = require_2d_world_vector(normal, "reflect() normal")
        old_energy = self.object_energy_j(target)
        velocity = target.properties["vel"]
        n = normal.normalized()
        dot = velocity.x*n.x + velocity.y*n.y + velocity.z*n.z
        reflected = Vector3(velocity.x-2*dot*n.x, velocity.y-2*dot*n.y, 0, VELOCITY)
        reflected = enforce_speed(reflected, massive=target.properties["mass"].value > 0)
        target.properties["vel"] = reflected
        target.properties["kinetic_energy"] = kinetic_energy(target.properties["mass"], reflected)
        target.properties["momentum"] = momentum(target.properties["mass"], reflected)
        self.update_total_energy(target)
        self.record_energy_delta("reflect", target, self.object_energy_j(target) - old_energy, source="surroundings")
        self.charge_operation(target, "reflect", kwargs, abs(self.object_energy_j(target) - old_energy) / JOULES_PER_MANA)
        return target

    def op_split(self, target, parts, **kwargs):
        target = self.require_object(target, "split")
        self.require_active_object(target, "split")
        for prop in ("mass", "volume", "area", "density", "energy", "thermal_energy", "kinetic_energy", "active"):
            self.require_property(target, prop, "split")
        if isinstance(parts, bool) or not isinstance(parts, int) or not 2 <= parts <= 10000:
            raise TypeErrorML("split() parts must be an integer between 2 and 10000")
        self.charge_operation(target, "split", kwargs, float(parts))
        original_mass, original_volume = target.properties["mass"].value, target.properties["volume"].value
        original_area = target.properties["area"].value
        pieces = []
        for index in range(parts):
            props = copy.deepcopy(target.properties)
            props["mass"] = Quantity(original_mass / parts, KG)
            props["volume"] = Quantity(original_volume / parts, M3)
            props["area"] = Quantity(original_area / parts, M2)
            props["density"] = Quantity(original_mass / original_volume, DENSITY)
            for key in ("energy", "thermal_energy", "kinetic_energy", "released_energy"):
                q = target.properties.get(key)
                if isinstance(q, Quantity):
                    props[key] = Quantity(q.value / parts, q.dimension)
            props["energy_sources"] = [
                {**entry, "energy_j": float(entry.get("energy_j", 0.0)) / parts}
                for entry in target.properties.get("energy_sources", [])
            ]
            local_release = target.properties.get("local_released_energy", Quantity(0, ENERGY))
            if isinstance(local_release, Quantity):
                props["local_released_energy"] = Quantity(local_release.value / parts, ENERGY)
            props["local_released_mana"] = float(target.properties.get("local_released_mana", 0.0)) / parts
            props["local_energy_sources"] = [
                {**entry, "energy_j": float(entry.get("energy_j", 0.0)) / parts}
                for entry in target.properties.get("local_energy_sources", [])
            ]
            if "released_mana" in props:
                props["released_mana"] = float(props["released_mana"]) / parts
            props["momentum"] = momentum(props["mass"], props["vel"])
            props["active"] = True
            props["display_name"] = f"{target.element}_part_{index+1}"
            props["split_index"] = index
            piece = MagicObject(target.element, props)
            self.update_energy(piece)
            pieces.append(piece)
        target.properties["active"] = False
        target.properties["split_into"] = pieces
        return pieces

    def op_anchor(self, target, position=None, **kwargs):
        target = self.require_object(target, "anchor")
        self.require_property(target, "anchored", "anchor")
        self.require_property(target, "anchor_pos", "anchor")
        if position is not None:
            if not isinstance(position, Vector3) or position.dimension != M:
                raise UnitErrorML("anchor() position must be a position vector in metres")
            target.properties["pos"] = require_2d_world_vector(position, "anchor() position")
        target.properties["anchor_pos"] = target.properties["pos"]
        self.charge_operation(target, "anchor", kwargs, 1.0)
        target.properties["anchored"] = True
        return target

    def op_unanchor(self, target, **kwargs):
        target = self.require_object(target, "unanchor")
        self.require_property(target, "anchored", "unanchor")
        self.charge_operation(target, "unanchor", kwargs, 0.25)
        target.properties["anchored"] = False
        return target

    def op_dispel(self, target, **kwargs):
        target = self.require_object(target, "dispel")
        self.require_active_object(target, "dispel")
        self.require_property(target, "active", "dispel")
        self.charge_operation(target, "dispel", kwargs, 1.0)
        self.record_energy_delta("dispel", target, -self.object_energy_j(target), source="left active runtime world")
        target.properties["active"] = False
        target.properties["released"] = True
        return target

    def op_distance(self, a, b):
        a = self.require_object(a, "distance")
        b = self.require_object(b, "distance")
        self.require_property(a, "pos", "distance")
        self.require_property(b, "pos", "distance")
        pa, pb = a.properties["pos"], b.properties["pos"]
        dx, dy, dz = pa.x-pb.x, pa.y-pb.y, pa.z-pb.z
        return Quantity(math.hypot(dx, dy, dz), M)

    def op_momentum(self, target):
        target = self.require_object(target, "momentum")
        self.require_property(target, "mass", "momentum")
        self.require_property(target, "vel", "momentum")
        value = momentum(target.properties["mass"], target.properties["vel"])
        target.properties["momentum"] = value
        return value

    def op_kinetic_energy(self, target):
        target = self.require_object(target, "kinetic_energy")
        self.require_property(target, "mass", "kinetic_energy")
        self.require_property(target, "vel", "kinetic_energy")
        self.require_property(target, "kinetic_energy", "kinetic_energy")
        value = kinetic_energy(target.properties["mass"], target.properties["vel"])
        target.properties["kinetic_energy"] = value
        target.properties["momentum"] = momentum(target.properties["mass"], target.properties["vel"])
        self.update_total_energy(target)
        return value

    def op_force(self, target):
        target = self.require_object(target, "force")
        self.require_property(target, "mass", "force")
        self.require_property(target, "acc", "force")
        value = physics_force(target.properties["mass"], target.properties["acc"])
        target.properties["force"] = value
        return value

    def op_pressure(self, target, area):
        target = self.require_object(target, "pressure")
        self.require_property(target, "force", "pressure")
        force_vector = target.properties["force"]
        area_q = self.as_quantity(area, M2, "pressure() area")
        return physics_pressure(force_vector, area_q)

    def op_sqrt(self, value):
        """Square root of a non-negative plain or dimensionless numeric value."""
        if isinstance(value, bool):
            raise TypeErrorML("sqrt() expects a non-negative number")
        if isinstance(value, Quantity):
            if value.dimension != DIMENSIONLESS:
                raise UnitErrorML("sqrt() currently accepts only dimensionless quantities")
            value = value.value
        if not isinstance(value, (int, float)):
            raise TypeErrorML("sqrt() expects a non-negative number")
        if value < 0:
            raise PhysicsErrorML("sqrt() cannot calculate the real square root of a negative value")
        return math.sqrt(value)

    def op_magnitude(self, value):
        if isinstance(value, Vector3):
            return value.magnitude()
        if isinstance(value, Quantity):
            return Quantity(abs(value.value), value.dimension)
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise TypeErrorML("magnitude() expects a vector or numeric quantity")
        return abs(value)

    def op_has_domain(self, target, domain):
        target = self.require_object(target, "has_domain")
        if not isinstance(domain, str):
            raise TypeErrorML("has_domain() domain must be text")
        return can_influence(target.element, domain)

    def op_matter_to_mana(self, mass):
        return matter_to_mana(self.as_quantity(mass, KG, "matter_to_mana() mass"))

    def op_mana_to_matter(self, amount):
        return mana_to_matter(self.as_quantity(amount, MANA, "mana_to_matter() amount"))

    def op_mana_to_energy(self, amount):
        return mana_to_energy(self.as_quantity(amount, MANA, "mana_to_energy() amount"))

    def op_energy_to_mana(self, amount):
        return energy_to_mana(self.as_quantity(amount, ENERGY, "energy_to_mana() amount"))

    # ---- Mana accounting ----

    def charge_operation(self, target: MagicObject, operation: str, kwargs: dict[str, Any], default_cost: float):
        if "mana" in kwargs:
            raise MagicErrorML("mana appraisal is calculated internally; do not pass mana= to an operation")
        energy_costed = {"heat", "cool", "velocity", "impulse", "push", "pull", "reflect"}
        if operation.startswith("mana.control "):
            energy_costed.add(operation)
        if operation.startswith("mana.control "):
            energy_costed.add(operation)
        # Non-energy operations do not consume or charge mana. For energy-changing
        # operations, default_cost is a displayed mana-equivalent, not a limit.
        cost = float(default_cost) if operation in energy_costed else 0.0
        self.record_mana_cost(cost, reason=operation, target=target)

    def charge_mana(self, amount: float, *, reason: str, target: MagicObject | None = None):
        """Record matter-creation cost; there is no mana pool or spendable budget."""
        self.record_mana_cost(amount, reason=reason, target=target)

    def record_mana_cost(self, amount: float, *, reason: str, target: MagicObject | None = None):
        if isinstance(amount, bool) or not isinstance(amount, (int, float)) or amount < 0:
            raise MagicErrorML("mana appraisal readout must be a finite non-negative number")
        try:
            amount = float(amount)
        except (OverflowError, ValueError) as exc:
            raise MagicErrorML("mana appraisal readout is outside the supported numeric range") from exc
        if not math.isfinite(amount):
            raise MagicErrorML("mana appraisal readout must be a finite non-negative number")
        with self._mana_lock:
            self.total_mana_used += amount
            if target is not None:
                target.properties["mana_used"] = target.properties.get("mana_used", 0.0) + amount
                target.properties["mana_cost"] = target.properties.get("mana_cost", 0.0) + amount

    def record_planar_energy_transfer(self, source_plane: str, target_plane: str, amount_j: float,
                                      path: list[str], *, kind: str | None = None) -> dict[str, Any]:
        """Record internal energy transport across a planar pathway.

        This is an internal transfer, not external energy input/output, so it is
        added to the ledger without changing the world's input/output totals.
        """
        amount = float(amount_j)
        if not math.isfinite(amount) or amount < 0:
            raise PhysicsErrorML("planar energy transfer must be finite and non-negative")
        entry = {
            "operation": "planar_transfer",
            "direction": "transfer",
            "source": source_plane,
            "target": target_plane,
            "amount_j": amount,
            "source_delta_j": -amount,
            "target_delta_j": amount,
            "delta_j": 0.0,
            "path": list(path),
            "kind": kind,
            "accounting": "internal transfer; no external energy input or output",
        }
        self.energy_ledger.append(entry)
        if self._spell_run_stack:
            self._record_step(
                f"planar energy transfer: {amount:g} J ({source_plane} -> {target_plane})"
            )
        return entry

    def record_energy_delta(self, operation: str, target: MagicObject | None, delta_j: float, *, source: str):
        """Record energy entering/leaving an object as an explicit ledger transfer.

        Repeated continuous-physics updates are aggregated during ``advance_time``.
        Counters still receive every exact delta; the readable ledger stores one
        summary per operation/direction, preventing long simulations from growing
        millions of redundant entries in memory.
        """
        try:
            delta = float(delta_j)
        except (TypeError, ValueError, OverflowError) as exc:
            raise PhysicsErrorML("energy transfer must be a finite number") from exc
        if not math.isfinite(delta):
            raise PhysicsErrorML("energy transfer must be a finite number")
        if abs(delta) <= 1e-9:
            return
        amount = abs(delta)
        direction = "input" if delta > 0 else "output"
        if delta > 0:
            self.energy_input_j += amount
        else:
            self.energy_output_j += amount

        batch = self._continuous_energy_batch
        batchable = operation in {
            "physics integration", "wind work", "atmospheric thermal exchange",
        }
        if batch is not None and batchable:
            detail = batch.setdefault(operation, {}).setdefault(
                direction, {"amount_j": 0.0, "updates": 0, "source": source}
            )
            detail["amount_j"] += amount
            detail["updates"] += 1
            return

        label = self._object_label(target) if isinstance(target, MagicObject) else "world"
        if delta > 0:
            entry = {"operation": operation, "direction": "input", "source": source,
                     "target": label, "amount_j": amount, "delta_j": delta}
        else:
            entry = {"operation": operation, "direction": "output", "source": label,
                     "target": source, "amount_j": amount, "delta_j": delta}
        self.energy_ledger.append(entry)
        if self._spell_run_stack:
            self._record_step(f"energy {direction}: {amount:g} J ({operation}; {source})")

    def _flush_continuous_energy_batch(self, batch, *, duration: float, step_count: int) -> None:
        """Commit compact summaries for exact continuous energy exchanges."""
        for operation in sorted(batch):
            for direction in ("input", "output"):
                detail = batch[operation].get(direction)
                if not detail or detail["amount_j"] <= 1e-9:
                    continue
                amount = float(detail["amount_j"])
                source_name = str(detail["source"])
                aggregate_label = f"world simulation ({detail['updates']} updates)"
                if direction == "input":
                    entry = {
                        "operation": operation, "direction": direction,
                        "source": source_name, "target": aggregate_label,
                        "amount_j": amount, "delta_j": amount,
                    }
                else:
                    entry = {
                        "operation": operation, "direction": direction,
                        "source": aggregate_label, "target": source_name,
                        "amount_j": amount, "delta_j": -amount,
                    }
                entry.update({
                    "aggregation": "advance_time", "duration_s": duration,
                    "physics_steps": step_count, "updates": detail["updates"],
                })
                self.energy_ledger.append(entry)
                if self._spell_run_stack:
                    self._record_step(
                        f"energy {direction}: {amount:g} J ({operation}; aggregated over "
                        f"{detail['updates']} world updates)"
                    )

    @staticmethod
    def object_energy_j(target: MagicObject) -> float:
        energy = target.properties.get("energy", Quantity(0, ENERGY))
        return energy.value if isinstance(energy, Quantity) else 0.0

    def mana_amount(self, value, label: str) -> float:
        if isinstance(value, Quantity):
            if value.dimension != MANA:
                raise UnitErrorML(f"{label} must be measured in mana")
            value = value.value
        if isinstance(value, bool) or not isinstance(value, (int, float)) or value < 0:
            raise MagicErrorML(f"{label} must be a non-negative mana amount")
        try:
            amount = float(value)
        except (OverflowError, ValueError) as exc:
            raise MagicErrorML(f"{label} is outside the supported numeric range") from exc
        if not math.isfinite(amount):
            raise MagicErrorML(f"{label} must be finite")
        return amount

    def apply_body_physical_profile(self, target: MagicObject, simulation: dict[str, Any], *,
                                    body_mass_kg: float | None = None,
                                    reset_temperature: bool = False) -> dict[str, float]:
        """Apply a validated anatomy template's coarse physical envelope to a being.

        Anatomy references used to affect health metadata while leaving summoned
        beings at the generic 1 kg default. This bridge makes body plans matter to
        the existing 2D physical model without pretending that the circle collider
        is a full articulated skeleton or locomotion solver.
        """
        target = self.require_object(target, "anatomy physical profile")
        if not isinstance(simulation, dict):
            return {}

        def positive(name: str, fallback: float) -> float:
            raw = simulation.get(name, fallback)
            try:
                value = float(raw)
            except (TypeError, ValueError, OverflowError):
                value = fallback
            return value if math.isfinite(value) and value > 0 else fallback

        mass_base = body_mass_kg if body_mass_kg is not None else positive("body_mass_kg", 70.0)
        try:
            mass_base = float(mass_base)
        except (TypeError, ValueError, OverflowError) as exc:
            raise PhysicsErrorML("body mass must be a positive finite number of kilograms") from exc
        if not math.isfinite(mass_base) or mass_base <= 0 or mass_base > 1e12:
            raise PhysicsErrorML("body mass must be greater than 0 and no greater than 1e12 kg")

        density_base = positive("body_density_kg_m3", 990.0)
        scale = target.properties.get("scale", 1.0)
        try:
            scale = float(scale)
        except (TypeError, ValueError, OverflowError):
            scale = 1.0
        if not math.isfinite(scale) or scale <= 0:
            scale = 1.0
        if scale > 1e4:
            raise PhysicsErrorML("current body scale is outside the supported physical-profile range")
        scale_cubed = scale ** 3
        mass = mass_base * scale_cubed
        volume_base = positive("body_volume_m3", mass_base / density_base)
        # A custom mass override keeps the selected body's approximate density;
        # it does not retain a stale volume from the base species.
        volume = (mass / density_base) if body_mass_kg is not None else volume_base * scale_cubed
        if not math.isfinite(mass) or not math.isfinite(volume) or mass <= 0 or volume <= 0:
            raise PhysicsErrorML("body physical dimensions exceed the supported numeric range")
        radius_base = positive("collision_radius_m", max(0.01, (3.0 * volume_base / (4.0 * math.pi)) ** (1.0 / 3.0)))
        radius = radius_base * scale
        if not math.isfinite(radius) or radius <= 0:
            raise PhysicsErrorML("body collision radius must be positive and finite")

        props = target.properties
        # Commit only after all profile values and derived quantities validate.
        props["mass"] = Quantity(mass, KG)
        props["volume"] = Quantity(volume, M3)
        props["density"] = Quantity(mass / volume, DENSITY)
        props["collision_radius"] = Quantity(radius, M)
        props["area"] = Quantity(math.pi * radius * radius, M2)
        props["body_base_mass_kg"] = mass_base
        props["body_mass_kg"] = mass
        props["body_density_kg_m3"] = mass / volume
        props["body_volume_m3"] = volume
        props["body_collision_radius_m"] = radius
        dimensions = {}
        for field_name in ("body_length_m", "body_width_m", "body_height_m"):
            raw = simulation.get(field_name)
            if isinstance(raw, (int, float)) and not isinstance(raw, bool) and math.isfinite(float(raw)) and float(raw) > 0:
                dimensions[field_name.removeprefix("body_").removesuffix("_m")] = float(raw) * scale
        props["body_dimensions_m"] = dimensions
        body_temperature = simulation.get("body_temperature_c")
        if reset_temperature and isinstance(body_temperature, (int, float)) and not isinstance(body_temperature, bool) and math.isfinite(float(body_temperature)):
            props["body_temperature_c"] = float(body_temperature)
            props["temp"] = Quantity(float(body_temperature) + 273.15, K)
        self.update_energy(target)
        return {"mass_kg": mass, "volume_m3": volume, "density_kg_m3": mass / volume,
                "collision_radius_m": radius, **dimensions}

    def update_energy(self, target: MagicObject):
        """Recompute energy from canonical state; released energy retains its provenance."""
        self.require_property(target, "mass", "update energy")
        self.require_property(target, "temp", "update energy")
        mass = target.properties["mass"]
        temperature = target.properties["temp"]
        thermal = mass.value * DEFAULT_SPECIFIC_HEAT_J_PER_KG_K * temperature.value
        target.properties["thermal_energy"] = Quantity(max(0.0, thermal), ENERGY)

        velocity = target.properties.get("vel")
        if isinstance(velocity, Vector3):
            target.properties["kinetic_energy"] = kinetic_energy(mass, velocity)
            target.properties["momentum"] = momentum(mass, velocity)
        self.update_total_energy(target)

    def update_total_energy(self, target: MagicObject):
        thermal = target.properties.get("thermal_energy", Quantity(0, ENERGY))
        kinetic = target.properties.get("kinetic_energy", Quantity(0, ENERGY))
        released = target.properties.get("released_energy", Quantity(0, ENERGY))
        mana_energy = target.properties.get("mana_energy", Quantity(0, ENERGY))
        bound_energy = target.properties.get("bound_energy", Quantity(0, ENERGY))
        target.properties["energy"] = thermal + kinetic + released + mana_energy + bound_energy
        self.update_integrity(target)

    def update_integrity(self, target: MagicObject, *, allow_collapse: bool = True) -> float:
        """Recalculate an object's integrity and collapse it at its breaking point.

        Physical energy remains unchanged by integrity. Stabilizers affect the
        integrity score only: structural stabilizers raise the threshold; Water,
        Air and Light mitigate thermal stress; Space spreads the effective load;
        Time dampens later positive increases in the score. Entropy and Death
        lower the threshold. Repeated stabilizers count only once.
        """
        props = target.properties
        if target.element in {"ThermalRelease", "Mana"} or props.get("integrity_collapsed", False):
            return float(props.get("integrity", 0.0))

        mass = props.get("mass", Quantity(1, KG))
        mass_kg = max(0.0, mass.value) if isinstance(mass, Quantity) else 1.0
        material = props.get("material", target.element)
        if not isinstance(material, str):
            material = target.element
        break_per_kg = INTEGRITY_BREAK_ENERGY_J_PER_KG.get(
            material, INTEGRITY_BREAK_ENERGY_J_PER_KG.get(target.element, DEFAULT_INTEGRITY_BREAK_ENERGY_J_PER_KG)
        )
        stabilizers = props.get("stabilizers", [])
        if not isinstance(stabilizers, list):
            stabilizers = []
        stabilizer_set = set(stabilizers)

        threshold_multiplier = 1.0
        structural = sorted(stabilizer_set & set(INTEGRITY_THRESHOLD_BONUS))
        bonus = 0.0
        for index, name in enumerate(structural):
            bonus += INTEGRITY_THRESHOLD_BONUS[name] / (1.0 + 0.5 * index)
        threshold_multiplier = min(INTEGRITY_MAX_THRESHOLD_MULTIPLIER, threshold_multiplier + bonus)
        for name, factor in INTEGRITY_COLLAPSE_STABILIZERS.items():
            if name in stabilizer_set:
                threshold_multiplier *= factor
        break_energy = max(0.0, mass_kg * break_per_kg * threshold_multiplier)

        thermal_q = props.get("thermal_energy", Quantity(0, ENERGY))
        kinetic_q = props.get("kinetic_energy", Quantity(0, ENERGY))
        released_q = props.get("released_energy", Quantity(0, ENERGY))
        thermal_j = thermal_q.value if isinstance(thermal_q, Quantity) else 0.0
        kinetic_j = kinetic_q.value if isinstance(kinetic_q, Quantity) else 0.0
        released_j = released_q.value if isinstance(released_q, Quantity) else 0.0
        bound_q = props.get("bound_energy", Quantity(0, ENERGY))
        bound_j = bound_q.value if isinstance(bound_q, Quantity) else 0.0
        thermal_factor = 1.0
        for name, factor in INTEGRITY_THERMAL_FACTORS.items():
            if name in stabilizer_set:
                thermal_factor *= factor
        # An explicitly declared arcane movement envelope separates a being's
        # bulk translational motion from stresses that damage its own structure.
        # Relativistic kinetic energy remains in the energy ledger and collisions
        # still use the actual velocity; only self-integrity scoring omits bulk
        # translation while that magical mode is active.
        integrity_kinetic_j = 0.0 if props.get("motion_energy_mode") == "arcane" else kinetic_j
        score_j = (thermal_j * thermal_factor + integrity_kinetic_j + released_j + bound_j)
        if "Space" in stabilizer_set:
            score_j *= 0.80

        previous_score = props.get("integrity_last_score_j")
        previous_effective = props.get("integrity_effective_energy_j")
        if not isinstance(previous_score, (int, float)) or not isinstance(previous_effective, (int, float)):
            effective_energy_j = score_j
        else:
            delta = score_j - float(previous_score)
            if delta > 0 and "Time" in stabilizer_set:
                delta *= 0.50
            effective_energy_j = max(0.0, float(previous_effective) + delta)
        props["integrity_last_score_j"] = score_j
        props["integrity_effective_energy_j"] = effective_energy_j
        props["integrity_energy"] = Quantity(effective_energy_j, ENERGY)
        props["integrity_break_energy"] = Quantity(break_energy, ENERGY)

        if break_energy <= 0:
            integrity = 1.0 if effective_energy_j <= 0 else 0.0
        elif effective_energy_j <= 0:
            integrity = 1.0
        else:
            integrity = max(0.0, min(1.0, 1.0 - (effective_energy_j / break_energy) ** (1.0 / 3.0)))
        props["integrity"] = integrity
        if integrity <= 0.0 and allow_collapse and effective_energy_j > 0:
            self._collapse_object(target)
        return integrity

    def _collapse_object(self, target: MagicObject) -> MagicObject:
        """Transfer an unstable object's energy into a ThermalRelease carrier."""
        props = target.properties
        if target.element == "ThermalRelease" or props.get("integrity_collapsed", False):
            return props.get("collapsed_into", target)
        energy_j = max(0.0, self.object_energy_j(target))
        energy_q = Quantity(energy_j, ENERGY)
        target.properties["active"] = False
        target.properties["integrity_collapsed"] = True
        target.properties["integrity"] = 0.0
        carrier_props = {
            "object_kind": "material", "material": "ThermalRelease",
            "display_name": f"{props.get('display_name', target.element)}_collapse_release",
            "mass": Quantity(0, KG), "volume": Quantity(0, M3),
            "area": Quantity(0, M2), "density": Quantity(0, DENSITY),
            "temp": Quantity(0, K), "vel": Vector3(0, 0, 0, VELOCITY),
            "thermal_energy": Quantity(0, ENERGY), "kinetic_energy": Quantity(0, ENERGY),
            "momentum": Vector3(0, 0, 0, MOMENTUM), "released_energy": energy_q,
            "energy": energy_q, "energy_state_initialized": True,
            "local_released_energy": energy_q, "energy_origin": "integrity_collapse",
            "local_energy_origin": "integrity_collapse",
            "energy_sources": [{"origin": "integrity_collapse", "energy_j": energy_j}] if energy_j else [],
            "local_energy_sources": [{"origin": "integrity_collapse", "energy_j": energy_j}] if energy_j else [],
            "released_mana": 0.0, "local_released_mana": 0.0,
            "integrity": 0.0, "integrity_break_energy": Quantity(0, ENERGY),
            "integrity_energy": energy_q, "stabilizers": [], "integrity_collapsed": True,
        }
        carrier = MagicObject("ThermalRelease", carrier_props)
        props["collapsed_into"] = carrier
        # Preserve committed-object membership by replacing the old object in
        # place. During post/release the new carrier is tracked by the spell and
        # committed only after the normal transaction succeeds.
        for index, existing in enumerate(self.active_objects):
            if existing is target:
                self.active_objects[index] = carrier
                break
        self._record_created(carrier, reason="integrity collapse")
        return carrier

    @staticmethod
    def require_object(value, operation):
        if not isinstance(value, MagicObject):
            raise TypeErrorML(f"{operation}() expects a magical object")
        return value

    @staticmethod
    def require_active_object(target: MagicObject, operation: str):
        if not target.properties.get("active", True):
            raise MagicErrorML(f"{operation}() cannot modify an inactive object")
        return target

    def require_allowed(self, target: MagicObject, operation: str):
        forbidden = target.properties.get("forbidden_ops", set())
        if operation in forbidden:
            raise MagicErrorML(f"{operation}() is forbidden for this target")

    def require_property(self, target: MagicObject, prop: str, operation: str):
        self.require_allowed(target, operation)
        if prop not in target.properties:
            raise TypeErrorML(f"{operation}() requires target property '{prop}'")

    @staticmethod
    def as_quantity(value, dimension, label):
        if isinstance(value, Quantity):
            from .units import as_dimension
            expected = as_dimension(dimension) if isinstance(dimension, str) else dimension
            if value.dimension != expected:
                raise UnitErrorML(f"{label} requires {expected}, got {value.dimension}")
            return value
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise TypeErrorML(f"{label} requires a numeric value")
        if isinstance(dimension, str):
            from .units import as_dimension
            dimension = as_dimension(dimension)
        try:
            numeric_value = float(value)
        except (OverflowError, ValueError) as exc:
            raise PhysicsErrorML(f"{label} is outside the supported numeric range") from exc
        if not math.isfinite(numeric_value):
            raise PhysicsErrorML(f"{label} must be finite")
        return Quantity(numeric_value, dimension)

    @staticmethod
    def truthy(value):
        return bool(value)

    @staticmethod
    def to_seconds(value):
        if isinstance(value, Quantity):
            if value.dimension != S:
                raise UnitErrorML(f"timing requires seconds, got {value.dimension}")
            return float(value.value)
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise TypeErrorML("timing requires a numeric duration")
        try:
            seconds = float(value)
        except (OverflowError, ValueError) as exc:
            raise RuntimeErrorML("timing value is outside the supported numeric range") from exc
        if not math.isfinite(seconds):
            raise RuntimeErrorML("timing value must be finite")
        return seconds

    def validate_quantity_property(self, name: str, value: Quantity):
        if name == "mass" and value.value < 0:
            raise PhysicsErrorML("mass cannot be negative")
        if name == "volume" and value.value < 0:
            raise PhysicsErrorML("volume cannot be negative")
        if name == "area" and value.value < 0:
            raise PhysicsErrorML("area cannot be negative")
        if name == "collision_radius" and value.value < 0:
            raise PhysicsErrorML("collision_radius cannot be negative; use 0 m for area-derived 2D bounds")
        if name == "temp":
            if value.value < 0:
                raise PhysicsErrorML("temperature cannot be below 0 K")
            if value.value > PLANCK_TEMPERATURE_K:
                raise PhysicsErrorML(
                    "temperature exceeds the Planck temperature; this requires the causality library"
                )
        if name == "pressure" and value.value < 0:
            raise PhysicsErrorML("absolute pressure cannot be negative")

    def validate_simul(self, statement: Simul, env: Environment):
        writes: dict[tuple[int, str], str] = {}
        property_map = {
            "shape": {"shape"},
            "move": {"pos"},
            "heat": {"temp", "thermal_energy", "energy"},
            "cool": {"temp", "thermal_energy", "energy"},
            "accelerate": {"acc", "force"},
            "decelerate": {"acc", "force"},
            "velocity": {"vel", "kinetic_energy", "energy"},
            "impulse": {"vel", "momentum", "kinetic_energy", "energy"},
            "compress": {"pressure"},
            "expand": {"volume"},
            "transform": {"state"},
            "bind": {"bound"},
        }
        allowed_pure = {"sqrt", "magnitude", "distance", "detect", "has_domain"}
        for stmt in statement.body.statements:
            expr = stmt.expression if isinstance(stmt, ExpressionStatement) else None
            if not isinstance(expr, Call) or not isinstance(expr.callee, Name):
                raise MagicErrorML("simul blocks currently require direct operation calls; nested control flow is ambiguous")
            op_name = expr.callee.name
            if op_name in allowed_pure:
                continue
            if op_name not in property_map:
                raise MagicErrorML(f"simul cannot verify write conflicts for '{op_name}'")
            if not expr.args:
                raise MagicErrorML(f"{op_name}() needs a target inside simul")
            target = self.eval_expr(expr.args[0], env)
            target = self.require_object(target, op_name)
            for prop in property_map[op_name]:
                key = (id(target), prop)
                if key in writes:
                    raise MagicErrorML(
                        f"simul conflict: {writes[key]} and {op_name}() both write the same {prop} property"
                    )
                writes[key] = op_name

    def _collect_physics_objects(self) -> list[MagicObject]:
        """Find objects reachable from globals, the committed world, and active spell results."""
        found: list[MagicObject] = []
        seen: set[int] = set()

        def visit(value):
            if value is None or isinstance(value, (str, int, float, bool, Quantity, Vector3, ElementTypeValue)):
                return
            identity = id(value)
            if identity in seen:
                return
            seen.add(identity)
            if isinstance(value, MagicObject):
                found.append(value)
                for item in value.properties.values():
                    visit(item)
            elif isinstance(value, Environment):
                for item in value.values.values():
                    visit(item)
                visit(value.parent)
            elif isinstance(value, FunctionValue):
                visit(value.closure)
            elif isinstance(value, SpellInstance):
                visit(value.definition)
                visit(value.element)
                for item in value.tuned_operations.values():
                    visit(item)
            elif isinstance(value, (list, tuple, set)):
                for item in value:
                    visit(item)
            elif isinstance(value, dict):
                for item in value.values():
                    visit(item)

        visit(self.global_env)
        visit(self.active_objects)
        for result in self._spell_run_stack:
            visit(result.created)
            visit(result.affected)
            visit(result.hits)
        unique, ids = [], set()
        for obj in found:
            if id(obj) not in ids:
                ids.add(id(obj))
                unique.append(obj)
        return unique

    def _advance_schedulers_one_step(self, seconds: float, fires: list[int]) -> None:
        for timer in list(self.timers):
            if not timer.active:
                continue
            elapsed_to_use = min(seconds, max(0.0, MAX_PERSISTENCE_SECONDS - timer.elapsed))
            if elapsed_to_use <= 0:
                timer.active = False
                continue
            if elapsed_to_use >= MAX_PERSISTENCE_SECONDS - timer.elapsed - 1e-9:
                timer.elapsed = MAX_PERSISTENCE_SECONDS
            else:
                timer.elapsed += elapsed_to_use
            timer.until_next -= elapsed_to_use
            while timer.until_next <= 1e-12 and timer.active:
                fires[0] += 1
                if fires[0] > MAX_TIMER_FIRES_PER_ADVANCE:
                    raise RuntimeErrorML("timer execution exceeded the per-advance safety limit")
                try:
                    self.exec_block(timer.statement.body, Environment(parent=timer.env))
                except IncantSignal as exc:
                    raise RuntimeErrorML("incant cannot escape from a persistent timer") from exc
                timer.until_next += timer.interval
                if timer.elapsed >= MAX_PERSISTENCE_SECONDS:
                    timer.active = False
            if timer.elapsed >= MAX_PERSISTENCE_SECONDS:
                timer.active = False

        for handler in list(self.event_handlers):
            if not handler.active:
                continue
            elapsed_to_use = min(seconds, max(0.0, MAX_PERSISTENCE_SECONDS - handler.elapsed))
            if elapsed_to_use <= 0:
                handler.active = False
                continue
            if elapsed_to_use >= MAX_PERSISTENCE_SECONDS - handler.elapsed - 1e-9:
                handler.elapsed = MAX_PERSISTENCE_SECONDS
            else:
                handler.elapsed += elapsed_to_use
            if handler.elapsed >= MAX_PERSISTENCE_SECONDS:
                handler.active = False

    def advance_time(self, duration, *, timestep=None, gravity=None):
        """Advance virtual world time with deterministic physics steps and scheduled effects.

        Gravity defaults to the vector stored in world settings (zero unless configured).
        Pass gravity explicitly to override it for one advance step.
        """
        seconds = self.to_seconds(duration)
        if not math.isfinite(seconds) or seconds < 0:
            raise PhysicsErrorML("time advancement requires a finite non-negative duration")
        if seconds == 0:
            return self.elapsed_virtual_time
        dt = DEFAULT_TIMESTEP_SECONDS if timestep is None else self.to_seconds(timestep)
        if not math.isfinite(dt) or dt <= 0:
            raise PhysicsErrorML("physics timestep must be a finite positive duration")
        if dt > MAX_TIMESTEP_SECONDS:
            raise PhysicsErrorML(
                f"physics timestep cannot exceed {MAX_TIMESTEP_SECONDS:g} s; smaller steps reduce missed collisions"
            )
        if gravity is None:
            gravity_vector = self.world_settings.get("gravity", Vector3(0, 0, 0, ACCELERATION))
        elif isinstance(gravity, Vector3) and gravity.dimension == ACCELERATION:
            gravity_vector = require_2d_world_vector(gravity, "advance_time() gravity")
        else:
            raise UnitErrorML("advance_time() gravity must be an acceleration vector in m/s2")
        step_count = math.ceil(seconds / dt)
        if step_count > MAX_PHYSICS_STEPS_PER_ADVANCE:
            raise RuntimeErrorML(
                f"advance_time() requires {step_count} physics steps; the safety cap is {MAX_PHYSICS_STEPS_PER_ADVANCE}"
            )

        snapshot = self._snapshot_runtime_state([self.global_env, self.active_objects])
        energy_batch_before = copy.deepcopy(self._continuous_energy_batch)
        owns_energy_batch = self._continuous_energy_batch is None
        if owns_energy_batch:
            self._continuous_energy_batch = {}
        fires = [0]
        remaining = seconds
        pair_check_budget = MAX_COLLISION_PAIR_CHECKS_PER_ADVANCE // step_count
        observer_buffer = self._begin_observer_buffer()
        # Keep long advances replayable without retaining thousands of full-world
        # snapshots in memory. Short advances retain the normal 10 Hz cadence.
        snapshot_interval = max(0.1, seconds / (MAX_OBSERVER_SNAPSHOTS_PER_ADVANCE - 1))
        next_observer_snapshot = self.elapsed_virtual_time + snapshot_interval
        try:
            for _ in range(step_count):
                self._check_stop_requested()
                step = min(dt, remaining)
                # Collect the active world once per substep and share the list with
                # motion, environment and energy refresh. Objects spawned by event
                # handlers enter the next substep, when they first receive motion.
                physics_objects = self._collect_physics_objects()
                step_world(self, step, gravity_vector, max_pair_checks=pair_check_budget,
                           objects=physics_objects)
                self._apply_environment_step(step, physics_objects)
                # Physics integration updates canonical energy outside language
                # operations, so refresh integrity after every completed step.
                for obj in physics_objects:
                    if obj.properties.get("active", True):
                        self.update_total_energy(obj)
                self.elapsed_virtual_time += step
                if any(obj.properties.get("body_model_initialized") for obj in physics_objects):
                    from .libraries.physiology import advance_runtime as advance_physiology
                    advance_physiology(self, step, physics_objects)
                self._apply_timed_world_effects(step, physics_objects)
                self._advance_planar_channels(step)
                self._advance_schedulers_one_step(step, fires)
                remaining = max(0.0, remaining - step)
                self.timers = [timer for timer in self.timers if timer.active]
                self.event_handlers = [handler for handler in self.event_handlers if handler.active]
                # Recording samples at 10 Hz is enough for readable replay and
                # bounds file growth; normal headless runs do no snapshot work.
                if self.observer is not None and (
                    self.elapsed_virtual_time + 1e-9 >= next_observer_snapshot or remaining <= 0
                ):
                    self._observe_scene("time_advance")
                    next_observer_snapshot = self.elapsed_virtual_time + snapshot_interval
            if owns_energy_batch:
                self._flush_continuous_energy_batch(
                    self._continuous_energy_batch or {}, duration=seconds, step_count=step_count
                )
                self._continuous_energy_batch = None
        except Exception:
            self._restore_runtime_state(snapshot)
            self._continuous_energy_batch = energy_batch_before
            if observer_buffer is not None:
                self._end_observer_buffer(observer_buffer, keep_world_events=False)
            raise
        else:
            if observer_buffer is not None:
                self._end_observer_buffer(observer_buffer, keep_world_events=True)
            return self.elapsed_virtual_time

    def _apply_material_phase_law(self, obj: MagicObject, *, observe: bool = True) -> bool:
        """Apply the catalogue's simple temperature/phase rule to known materials.

        This is a coarse 1-atm world rule, not a molecular simulation. Powder is an
        aggregate form and is left alone; callers can explicitly choose it with
        transform().
        """
        props = obj.properties
        material = props.get("material")
        temperature = props.get("temp")
        if not self.world_settings.get("phase_changes_enabled", True):
            return False
        if not isinstance(material, str) or not isinstance(temperature, Quantity) or temperature.dimension != K:
            return False
        if props.get("burning", False) or props.get("state") in {"powder", "plasma"}:
            return False
        desired = phase_for_temperature(material, temperature.value, props.get("state"))
        if desired is None or desired == props.get("state"):
            return False
        previous = props.get("state", "solid")
        props["state"] = desired
        if observe:
            self._observe("entity.changed", entity=self._visual_entity(obj), operation="phase_change",
                          from_state=previous, to_state=desired, material=material,
                          temperature_k=temperature.value)
        if self._spell_run_stack:
            self._record_step(f"phase change: {self._object_label(obj)} {previous} -> {desired}")
        return True

    def _weather_for_object(self, obj: MagicObject, now: float) -> dict[str, Any]:
        """Choose the newest active area weather covering this object's position."""
        pos = obj.properties.get("pos")
        if isinstance(pos, Vector3) and pos.dimension == M and abs(pos.z) <= 1e-12:
            for region in reversed(self.weather_regions):
                until = region.get("until")
                if until is not None and float(until) <= now:
                    continue
                radius = region.get("radius_m")
                cx, cy = region.get("center_x_m"), region.get("center_y_m")
                if radius is None or cx is None or cy is None:
                    continue
                dx, dy = pos.x - float(cx), pos.y - float(cy)
                if dx * dx + dy * dy <= float(radius) * float(radius):
                    return region
        return self.environment_state

    def _apply_timed_world_effects(self, seconds: float, objects: list[MagicObject]) -> None:
        """Advance bounded material fields and temporary physiological effects."""
        if seconds <= 0:
            return
        now = self.elapsed_virtual_time
        start = max(0.0, now - seconds)

        # Expire contact effects exactly once and restore the object's original
        # anchor state instead of assuming every bound target was movable.
        for obj in objects:
            props = obj.properties
            restore = props.get("temporary_anchor_restore")
            if isinstance(restore, dict) and float(restore.get("until", math.inf)) <= now + 1e-9:
                props["anchored"] = bool(restore.get("anchored", False))
                props.pop("temporary_anchor_restore", None)
                props.pop("bound_until", None)
                props.pop("bound", None)
                self._observe("entity.changed", entity=self._visual_entity(obj), operation="temporary_anchor_expired")
            for expiry_key, active_key in (("shocked_until", "shocked"), ("obscured_until", "obscured"),
                                           ("illuminated_until", "illuminated"), ("corroded_until", "corroded")):
                expiry = props.get(expiry_key)
                if isinstance(expiry, (int, float)) and expiry <= now + 1e-9:
                    props.pop(expiry_key, None)
                    props.pop(active_key, None)
                    self._observe("entity.changed", entity=self._visual_entity(obj), operation=f"{active_key}_expired")

            enhancements = props.get("body_enhancements")
            if isinstance(enhancements, list):
                from .libraries.physiology import refresh_effective_properties
                had_effects = bool(enhancements)
                refresh_effective_properties(obj, now)
                if had_effects and not enhancements:
                    self._observe("entity.changed", entity=self._visual_entity(obj), operation="body_enhancements_expired")
            regen = props.get("regeneration_rate_hp_s", 0.0)
            hp, max_hp = props.get("hp"), props.get("max_hp")
            if (isinstance(regen, (int, float)) and not isinstance(regen, bool) and regen > 0
                    and isinstance(hp, (int, float)) and isinstance(max_hp, (int, float))
                    and 0 < float(hp) < float(max_hp) and props.get("active", True)):
                healed = min(float(max_hp) - float(hp), float(regen) * seconds)
                if healed > 0:
                    props["hp"] = float(hp) + healed
                    props["last_healing"] = healed
                    self._observe("entity.changed", entity=self._visual_entity(obj), operation="regeneration", healed=healed)

        # Each active field contributes a bounded force with linear radial
        # falloff. This is a gameplay magnetic model, not a Maxwell solver.
        if self.magnetic_fields:
            for field_record in self.magnetic_fields:
                until = float(field_record.get("until", 0.0))
                active_duration = min(seconds, max(0.0, until - start))
                if active_duration <= 0 or until <= start:
                    continue
                center = field_record.get("center")
                if not isinstance(center, Vector3) or center.dimension != M:
                    continue
                radius = float(field_record.get("radius_m", 0.0))
                strength = float(field_record.get("strength_n", 0.0))
                if radius <= 0 or strength <= 0:
                    continue
                polarity_sign = -1.0 if field_record.get("polarity") == "attract" else 1.0
                for obj in objects:
                    props = obj.properties
                    if not props.get("active", True) or props.get("anchored", False) or obj.element in {"Mana", "ThermalRelease"}:
                        continue
                    response = props.get("magnetic_response", 0.0)
                    mass = props.get("mass")
                    pos = props.get("pos")
                    vel = props.get("vel")
                    if (not isinstance(response, (int, float)) or isinstance(response, bool) or response <= 0
                            or not isinstance(mass, Quantity) or mass.value <= 0
                            or not isinstance(pos, Vector3) or pos.dimension != M
                            or not isinstance(vel, Vector3) or vel.dimension != VELOCITY):
                        continue
                    dx, dy = pos.x - center.x, pos.y - center.y
                    distance = math.hypot(dx, dy)
                    if distance <= 1e-9 or distance >= radius:
                        continue
                    radial = (1.0 - distance / radius) * min(1.0, float(response))
                    force = min(1_000_000.0, strength * radial)
                    accel = min(250.0, force / mass.value) * polarity_sign
                    old_energy = self.object_energy_j(obj)
                    next_velocity = enforce_speed(Vector3(
                        vel.x + (dx / distance) * accel * active_duration,
                        vel.y + (dy / distance) * accel * active_duration,
                        0.0, VELOCITY,
                    ), massive=True)
                    props["vel"] = next_velocity
                    props["kinetic_energy"] = kinetic_energy(mass, next_velocity)
                    props["momentum"] = momentum(mass, next_velocity)
                    self.update_total_energy(obj)
                    delta = self.object_energy_j(obj) - old_energy
                    self.record_energy_delta("magnetic field work", obj, delta, source=f"magnetic field:{field_record.get('id', 'unknown')}")
            expired = [item for item in self.magnetic_fields if float(item.get("until", 0.0)) <= now + 1e-9]
            if expired:
                expired_ids = {item.get("id") for item in expired}
                self.magnetic_fields = [item for item in self.magnetic_fields if item.get("id") not in expired_ids]
                for item in expired:
                    self._observe("world.changed", operation="magnetic_field_expired", field_id=item.get("id"))

    def _apply_environment_step(self, seconds: float, objects: list[MagicObject]) -> None:
        """Apply global and local weather to objects using the shared world rules."""
        if seconds <= 0:
            return
        now = self.elapsed_virtual_time

        for obj in objects:
            props = obj.properties
            if not props.get("active", True) or obj.element in {"Mana", "ThermalRelease"}:
                continue
            env = self._weather_for_object(obj, now)
            until = env.get("until")
            active_seconds = (min(seconds, max(0.0, float(until) - now))
                              if until is not None else seconds)
            if active_seconds <= 0:
                continue

            kind = env.get("kind", "clear")
            temperature = float(env.get("temperature_k", 293.15))
            wind_x = float(env.get("wind_x_mps", 0.0))
            wind_y = float(env.get("wind_y_mps", 0.0))
            precipitation = str(env.get("precipitation", "none"))
            intensity = max(0.0, min(1.0, float(env.get("intensity", 0.0))))
            is_wet = precipitation in {"rain", "snow", "hail"}
            is_dry_fall = precipitation in {"dust", "ash"}
            humidity = float(env.get("humidity", 0.45))
            clouds = float(env.get("clouds", 0.0))
            fog = float(env.get("fog", 0.0))
            heat = float(env.get("heat", 0.0))
            lightning = float(env.get("lightning", 0.0))
            weather_active = (
                kind != "clear" or intensity > 1e-9
                or abs(temperature - 293.15) > 1e-9
                or abs(wind_x) > 1e-9 or abs(wind_y) > 1e-9
                or precipitation != "none" or abs(humidity - 0.45) > 1e-9
                or abs(clouds) > 1e-9 or abs(fog) > 1e-9
                or abs(heat) > 1e-9 or abs(lightning) > 1e-9
            )
            if not weather_active:
                continue

            # Capped interval keeps large time advances numerically stable.
            dt = min(active_seconds, 5.0)
            thermal_exposure = max(intensity, min(1.0, abs(temperature - 293.15) / 45.0))
            thermal_fraction = (min(0.08, 0.025 * thermal_exposure * active_seconds)
                                if self.world_settings.get("thermal_exchange_enabled", True) else 0.0)
            wet_gain = (min(1.0, 0.12 * intensity * active_seconds)
                        if self.world_settings.get("wetting_enabled", True) else 0.0)
            drying = min(1.0, 0.015 * active_seconds)
            dust_gain = min(1.0, 0.025 * intensity * active_seconds)
            changed = False

            if self.world_settings.get("drag_enabled", True) and not props.get("anchored", False) and (abs(wind_x) > 1e-9 or abs(wind_y) > 1e-9):
                velocity = props.get("vel")
                mass = props.get("mass")
                area = props.get("area")
                if (isinstance(velocity, Vector3) and velocity.dimension == VELOCITY
                        and isinstance(mass, Quantity) and mass.value > 0
                        and isinstance(area, Quantity) and area.value > 0):
                    rx, ry = wind_x - velocity.x, wind_y - velocity.y
                    relative_speed = math.hypot(rx, ry)
                    if relative_speed > 1e-9:
                        drag_coefficient = max(0.05, min(2.5, float(props.get("drag_coefficient", 1.0))))
                        air_density = max(0.0, float(self.world_settings.get("air_density_kg_m3", 1.225)))
                        wind_force = 0.5 * air_density * drag_coefficient * area.value * relative_speed * relative_speed
                        acceleration = wind_force / mass.value
                        wind_strength = max(intensity, min(1.0, math.hypot(wind_x, wind_y) / 20.0))
                        delta_speed = min(relative_speed, acceleration * dt * wind_strength)
                        if delta_speed > 0:
                            next_velocity = enforce_speed(Vector3(
                                velocity.x + rx / relative_speed * delta_speed,
                                velocity.y + ry / relative_speed * delta_speed, 0, VELOCITY
                            ), massive=True)
                            if abs(next_velocity.x - velocity.x) > 1e-12 or abs(next_velocity.y - velocity.y) > 1e-12:
                                old_kinetic = props.get("kinetic_energy", Quantity(0, ENERGY))
                                old_kinetic_j = old_kinetic.value if isinstance(old_kinetic, Quantity) else 0.0
                                props["vel"] = next_velocity
                                props["kinetic_energy"] = kinetic_energy(mass, next_velocity)
                                props["momentum"] = momentum(mass, next_velocity)
                                self.record_energy_delta(
                                    "wind work", obj, props["kinetic_energy"].value - old_kinetic_j,
                                    source=f"weather field:{env.get('scope', 'world')}:{env.get('region_id', 'global')}",
                                )
                                changed = True

            wetness = float(props.get("wetness", 0.0))
            dust = float(props.get("dust_coating", 0.0))
            if self.world_settings.get("wetting_enabled", True):
                if is_wet:
                    wetness = min(1.0, wetness + wet_gain)
                    props["wetness"] = wetness
                    if props.get("burning", False) and wetness >= 0.35:
                        props["burning"] = False
                        if props.get("state") == "burning":
                            props["state"] = "solid"
                        self._observe("entity.changed", entity=self._visual_entity(obj), operation="weather.extinguish")
                        changed = True
                elif wetness > 0:
                    props["wetness"] = max(0.0, wetness - drying)
                if is_dry_fall:
                    props["dust_coating"] = min(1.0, dust + dust_gain)
                elif dust > 0:
                    props["dust_coating"] = max(0.0, dust - min(0.05, 0.005 * active_seconds))
            if temperature > 0 and thermal_fraction > 0:
                temp = props.get("temp")
                mass = props.get("mass")
                if isinstance(temp, Quantity) and temp.dimension == K and isinstance(mass, Quantity) and mass.value > 0:
                    next_temp = max(0.0, temp.value + (temperature - temp.value) * thermal_fraction)
                    if abs(next_temp - temp.value) > 1e-10:
                        old_thermal = props.get("thermal_energy", Quantity(0, ENERGY))
                        old_thermal_j = old_thermal.value if isinstance(old_thermal, Quantity) else 0.0
                        props["temp"] = Quantity(next_temp, K)
                        props["thermal_energy"] = Quantity(mass.value * DEFAULT_SPECIFIC_HEAT_J_PER_KG_K * next_temp, ENERGY)
                        self.record_energy_delta(
                            "atmospheric thermal exchange", obj,
                            props["thermal_energy"].value - old_thermal_j,
                            source=f"atmosphere:{env.get('scope', 'world')}:{env.get('region_id', 'global')}",
                        )
                        changed = True
                        changed = self._apply_material_phase_law(obj) or changed
            if changed:
                self.update_total_energy(obj)

        if (self.environment_state.get("until") is not None
                and now + seconds >= float(self.environment_state["until"])):
            self._expire_weather()

        expired = [region for region in self.weather_regions
                   if region.get("until") is not None and now + seconds >= float(region["until"])]
        if expired:
            expired_ids = {region.get("region_id") for region in expired}
            self.weather_regions = [region for region in self.weather_regions
                                    if region.get("region_id") not in expired_ids]
            for region in expired:
                self._observe("weather.changed", scope="area", action="expired",
                              region_id=region.get("region_id"),
                              center=[region.get("center_x_m"), region.get("center_y_m")],
                              radius_m=region.get("radius_m"), kind=region.get("kind", "custom"))

    def _expire_weather(self) -> None:
        """End a timed weather condition exactly once."""
        previous = self.environment_state
        already_clear = (
            previous.get("kind") == "clear"
            and abs(float(previous.get("intensity", 0.0))) < 1e-9
            and previous.get("precipitation", "none") == "none"
            and abs(float(previous.get("wind_x_mps", 0.0))) < 1e-9
            and abs(float(previous.get("wind_y_mps", 0.0))) < 1e-9
            and abs(float(previous.get("temperature_k", 293.15)) - 293.15) < 1e-9
            and abs(float(previous.get("humidity", 0.45)) - 0.45) < 1e-9
            and abs(float(previous.get("clouds", 0.0))) < 1e-9
            and abs(float(previous.get("fog", 0.0))) < 1e-9
            and abs(float(previous.get("heat", 0.0))) < 1e-9
            and abs(float(previous.get("lightning", 0.0))) < 1e-9
        )
        if already_clear:
            return
        self.environment_state = {
            "kind": "clear", "intensity": 0.0, "precipitation": "none",
            "wind_speed_mps": 0.0, "wind_x_mps": 0.0, "wind_y_mps": 0.0,
            "wind_direction_name": "east", "wind": 0.0, "wind_direction": 1.0,
            "temperature_k": 293.15, "humidity": 0.45, "clouds": 0.0, "fog": 0.0,
            "heat": 0.0, "lightning": 0.0, "started_at": self.elapsed_virtual_time,
            "until": None, "duration": None, "indefinite": True,
        }
        self._observe("weather.changed", weather=dict(self.environment_state))

    def _advance_planar_channels(self, seconds: float) -> None:
        """Transfer energy through active planar channels for one virtual-time step."""
        if seconds <= 0 or not getattr(self, "_planar_channels", None):
            return
        from .libraries.planes import _route_ids, _label, _needs_invocation
        from .libraries.planar_registry import get_registry
        registry = get_registry(self)
        for (source_id, destination_id), channel in list(self._planar_channels.items()):
            source = registry.reference(source_id)
            destination = registry.reference(destination_id)
            if source is None or destination is None:
                self._planar_channels.pop((source_id, destination_id), None)
                continue
            if _needs_invocation(self, source) and source_id not in registry.permissions:
                self._planar_channels.pop((source_id, destination_id), None)
                continue
            route_ids = _route_ids(registry, source_id, destination_id)
            if not route_ids:
                self._planar_channels.pop((source_id, destination_id), None)
                continue
            amount_j = float(channel["rate_w"]) * seconds
            if not math.isfinite(amount_j) or amount_j < 0:
                raise PhysicsErrorML("planar channel produced an invalid energy amount")
            route = [_label(registry.reference(plane_id)) for plane_id in route_ids]
            self.record_planar_energy_transfer(
                _label(source), _label(destination), amount_j, route, kind=channel.get("kind")
            )
            self.emit_event("energy_arrived", _label(source), _label(destination), amount_j, channel.get("kind"))

    def _emit_mana_warning(self, message: str, *, statement: Any | None = None) -> None:
        """Emit a stable MANA-format warning, with its source location."""
        location = self._source_locations.get(id(statement)) if statement is not None else None
        if location is None:
            location = getattr(self._diagnostic_context, "location", None)
        if location is None:
            print(f"Warning: {message}", file=sys.stderr)
            return
        filename, line, column = location
        print(f"Warning: {filename}:{line}:{column}: {message}", file=sys.stderr)

    def emit_event(self, event_name: str, *args):
        if not isinstance(event_name, str):
            raise TypeErrorML("emit() event name must be text")
        if event_name not in MANA_EVENT_NAMES:
            self._emit_mana_warning(
                f"unknown MANA event '{event_name}'; known events: {', '.join(sorted(MANA_EVENT_NAMES))}"
            )
        else:
            try:
                self._observe("mana.event", name=event_name, args=[self._observer_value(arg) for arg in args])
            except Exception:
                # Observation is diagnostic only and must never change MANA execution.
                pass
        fired = 0
        for registration in list(self.event_handlers):
            if registration.active and registration.name == event_name:
                fired += 1
                child = Environment(parent=registration.env)
                child.set_local("event_args", list(args))
                self.exec_block(registration.statement.body, child)
        return fired

    def safe_span(self, *args):
        if not 1 <= len(args) <= 3:
            raise TypeErrorML("span() expects 1 to 3 integer arguments")
        if any(isinstance(a, bool) or not isinstance(a, int) for a in args):
            raise TypeErrorML("span() arguments must be integers")
        if len(args) == 3 and args[2] == 0:
            raise RuntimeErrorML("span() step cannot be zero")
        if len(args) == 1:
            start, stop, step = 0, args[0], 1
        elif len(args) == 2:
            start, stop = args
            step = 1
        else:
            start, stop, step = args
        if step > 0:
            count = max(0, (stop - start + step - 1) // step)
        else:
            count = max(0, (start - stop + (-step) - 1) // (-step))
        if count > MAX_LOOP_ITERATIONS:
            raise RuntimeErrorML("span() exceeds the safety iteration limit")
        return range(*args)

    @staticmethod
    def safe_length(value):
        """Length for supported MANA sequence values; no implicit containers."""
        if not isinstance(value, (list, str, range)):
            raise TypeErrorML("length() expects a list, string, or span")
        return len(value)

    def check_name(self, name: str, *, allow_mana_parameter: bool = False):
        if allow_mana_parameter and name == "mana":
            return
        if name in self.RESERVED_IDENTIFIERS:
            raise RuntimeErrorML(f"'{name}' is reserved and cannot be used as an identifier")
