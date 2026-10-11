from __future__ import annotations

import copy
import difflib
import json
import math
import os
import re
import sys
import threading
import traceback
import zipfile
from pathlib import Path
from itertools import count
from dataclasses import dataclass, field, fields, is_dataclass
from typing import Any

from .ast_nodes import (
    Program, Block, LoadLibrary, Literal, Name, ListLiteral, Attribute, Subscript, Unary,
    Binary, Call, Create, Assignment, ExpressionStatement, FunctionDef, Incant,
    TargetSet, TargetContext, If, While, For, Simul, Wait, After, Event, Every,
    SpellModeStatement, TuneAssignment, SkipStatement,
)
from .elements import (
    ELEMENTS, FUNDAMENTAL_ELEMENTS, interaction, can_influence,
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
MAX_FUNCTION_DEPTH = 25
MAX_EXPRESSION_DEPTH = 256
MAX_POWER_EXPONENT = 100_000
MAX_INTEGER_RESULT_BITS = 1_000_000
MAX_COLLECTION_SIZE = 1_000_000
MAX_LIBRARY_ARCHIVE_MEMBERS = 128
MAX_LIBRARY_UNCOMPRESSED_BYTES = 2_000_000
MANA_EVENT_NAMES = {"impact", "collision", "damaged", "path_opened", "path_closed", "energy_arrived", "plane_created", "being_summoned", "being_returned", "being_tamed", "being_reanimated", "being_animated", "mana_formed", "mana_burst", "mana_emitted", "object_ignited"}
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


_OBJECT_IDS = count(1)


@dataclass(slots=True)
class MagicObject:
    element: str
    properties: dict[str, Any] = field(default_factory=dict)
    object_id: int = field(default_factory=lambda: next(_OBJECT_IDS), init=False)

    def __post_init__(self):
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
            "restitution": 0.2,
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
            if value is not None or key == "collapsed_into":
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

    def get(self, name: str):
        if name == "mana":
            raise RuntimeErrorML("mana is not stored on objects; inspect the spell's mana cost readout")
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
    ok: bool = True
    committed: bool = False
    incant_value: Any = None
    created: list[Any] = field(default_factory=list)
    affected: list[Any] = field(default_factory=list)
    changes: list[SpellChange] = field(default_factory=list)
    hits: list[Any] = field(default_factory=list)
    mana_used: Any = None  # retained field name; represents a calculated cost readout
    energy_transfers: list[dict[str, Any]] = field(default_factory=list)
    rules_fired: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    trace: list[str] = field(default_factory=list)
    _created_ids: set[int] = field(default_factory=set, repr=False)

    def __repr__(self):
        status = "ok" if self.ok else "failed"
        return (f"<SpellResult {self.spell!r} mode={self.mode} {status}, "
                f"created={len(self.created)}, affected={len(self.affected)}, changes={len(self.changes)}, "
                f"hits={len(self.hits)}, mana_cost_readout={self.mana_used}>")


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
        "def", "spldef", "load", "incant", "tgset", "if", "elif", "else", "while", "for", "in",
        "and", "or", "not", "true", "false", "create", "simul",
        "wait", "after", "every", "when", "skip", "tune",
    }
    RESERVED_PROPERTIES = {
        "mass", "volume", "area", "density", "pos", "vel", "acc", "force",
        "energy", "temp", "pressure", "state", "material", "mana",
        "integrity", "integrity_break_energy", "integrity_energy", "stabilizers", "bound_energy",
        "rot", "scale", "anchored", "anchor_pos", "direction", "active", "released", "bound",
        "collision_radius", "restitution", "collidable", "acceleration_persistent", "combustible",
        "powderable", "ignition_temp", "kind", "hp", "max_hp", "defence",
    }
    BUILTIN_NAMES = {
        "shape", "move", "heat", "cool", "accelerate", "decelerate", "velocity",
        "detect", "release", "bind", "combine", "separate", "transform", "compress",
        "expand", "momentum", "kinetic_energy", "force", "pressure",
        "has_domain", "matter_to_mana", "mana_to_matter", "mana_to_energy",
        "energy_to_mana", "show", "post", "active_objects", "sqrt", "span", "length", "advance_time", "emit",
        "rotate", "scale", "push", "pull", "reflect", "split",
        "anchor", "unanchor", "dispel", "last_collisions",
        "point", "line", "ray", "segment", "circle", "round", "arc", "ellipse",
        "ring", "polygon", "beam", "wave", "disc", "spiral", "fan", "wall", "field",
        "dome", "cage", "chain", "tendril", "cone", "corridor", "c",
        "pi", "geometry2d", "vector3d", "planes", "elemental_planes", "hell",
        "heaven", "atlantis", "fae_paradise", "lineage_halls", "wild_realm",
        "summoning", "drafter", "necromancy", "mana", "Mana",
    }

    def __init__(self, project_root: str | Path | None = None):
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
        self._planar_channels: dict[tuple[str, str], dict[str, Any]] = {}
        self.energy_input_j = 0.0
        self.energy_output_j = 0.0
        self.elapsed_virtual_time = 0.0
        self.last_collisions: list[dict[str, Any]] = []
        self._spell_run_stack: list[SpellResult] = []
        self._spell_instance_stack: list[SpellInstance | None] = []
        self._target_context_stack: list[MagicObject] = []
        self._function_depth = 0
        self._pure_call_depth = 0
        self._stop_requested = threading.Event()
        self._source_locations: dict[int, tuple[str, int, int]] = {}
        self._diagnostic_context = threading.local()
        self._evaluation_context = threading.local()
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
        self.caster_position = Vector3(0, 0, 0, M)

    def _install_builtins(self):
        builtins = {
            "shape": self.op_shape,
            "move": self.op_move,
            "heat": self.op_heat,
            "cool": self.op_cool,
            "accelerate": self.op_accelerate,
            "decelerate": self.op_decelerate,
            "velocity": self.op_velocity,
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

        if name in {"geometry2d", "vector3d", "planes", "mana", "drafter", "summoning", "necromancy"} or name in builtin_dependencies:
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

        self._libraries_loading.add(name)
        self._library_load_stack.append(name)
        try:
            with zipfile.ZipFile(package_path, "r") as archive:
                infos = archive.infolist()
                if len(infos) > MAX_LIBRARY_ARCHIVE_MEMBERS:
                    raise RuntimeErrorML(
                        f"library '{name}' exceeds the {MAX_LIBRARY_ARCHIVE_MEMBERS}-member archive limit"
                    )
                total_uncompressed = sum(info.file_size for info in infos)
                if total_uncompressed > MAX_LIBRARY_UNCOMPRESSED_BYTES:
                    raise RuntimeErrorML(
                        f"library '{name}' exceeds the {MAX_LIBRARY_UNCOMPRESSED_BYTES}-byte uncompressed size limit"
                    )
                bad_member = archive.testzip()
                if bad_member is not None:
                    raise RuntimeErrorML(f"library package '{name}' is corrupt at {bad_member}")
                try:
                    manifest = json.loads(archive.read("mana-library.json").decode("utf-8-sig"))
                except (KeyError, UnicodeDecodeError, json.JSONDecodeError) as exc:
                    raise RuntimeErrorML(f"library '{name}' has no valid mana-library.json manifest") from exc
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
        self._source_locations.update(program.locations)
        return self.exec_block(Block(program.statements), self.global_env)

    def exec_block(self, block: Block, env: Environment):
        result = None
        for stmt in block.statements:
            result = self.exec_stmt(stmt, env)
        return result

    def exec_stmt(self, stmt, env):
        self._check_stop_requested()
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
            return self.op_post(spell) if stmt.mode == "post" else self.op_release(spell)

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
                raise TypeErrorML("spell definitions accept no parameters or one base-element selector: use 'spldef name(element):'")
            env.assign(stmt.name, FunctionValue(
                stmt.params, stmt.body, env, stmt.name, stmt.defaults,
                library_function=stmt.library_function, is_spell=stmt.is_spell,
            ))
            return None

        if isinstance(stmt, SkipStatement):
            return None

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
            if isinstance(value, MagicObject) and value.properties.get("display_name") in (None, value.element):
                # Give trace reports the source-level name when an object is assigned.
                value.properties["display_name"] = target.name
            if isinstance(value, MagicObject) and value.properties.get("is_summoned", False):
                # Naming the result tames this particular summoned instance.
                # Preserve its first stable name when the same object is aliased.
                if not value.properties.get("is_tamed", False):
                    value.properties["is_tamed"] = True
                    value.properties["tame_name"] = target.name
            if isinstance(value, SpellInstance):
                value.name = target.name
            env.assign(target.name, value)
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
                candidates = set(self.LANGUAGE_KEYWORDS) | set(self.BUILTIN_NAMES)
                scope = env
                while scope is not None:
                    candidates.update(scope.values)
                    scope = scope.parent
                matches = difflib.get_close_matches(expr.name, sorted(candidates), n=1, cutoff=0.65)
                if matches:
                    exc.hint = f"Did you mean '{matches[0]}'?"
                raise
        if isinstance(expr, ListLiteral):
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
            self._require_element_invocation(element_name)
            # MagicObject initializes a coherent energy and integrity baseline;
            # do not recompute that same baseline a second time here.
            obj = MagicObject(element_name)
            # Creation costs only the matter-manifestation rate, not its starting heat/motion energy.
            # Pure mana is a field/energy construct, not manifested matter.
            creation_cost = 0.0 if element_name == "Mana" else matter_to_mana(obj.properties["mass"]).value
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
                # An element-parameterized spldef call configures an instance; it
                # never executes the spell body during configuration.
                if callee.params == ["element"]:
                    return SpellInstance(callee, bound_values[0])
                raise TypeErrorML(
                    f"spell '{callee.name}' cannot be called as a value; use post({callee.name}) or release({callee.name})"
                )
            bound_values = self._bind_function_arguments(callee, args, kwargs)
            # `def` and library helpers are pure calculation functions. World
            # operations remain restricted to spldef bodies run through post/release.
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
                    if len(left) + len(right) > MAX_COLLECTION_SIZE:
                        raise RuntimeErrorML(
                            f"string result exceeds the MANA size limit ({MAX_COLLECTION_SIZE} characters)"
                        )
                elif isinstance(left, list) and isinstance(right, list):
                    if len(left) + len(right) > MAX_COLLECTION_SIZE:
                        raise RuntimeErrorML(
                            f"list result exceeds the MANA size limit ({MAX_COLLECTION_SIZE} items)"
                        )
                result = left + right
            elif op == "-":
                result = left - right
            elif op == "*":
                repeated, multiplier = None, None
                if isinstance(left, (str, list)) and isinstance(right, int) and not isinstance(right, bool):
                    repeated, multiplier = left, right
                elif isinstance(right, (str, list)) and isinstance(left, int) and not isinstance(left, bool):
                    repeated, multiplier = right, left
                if repeated is not None and multiplier > 0 and len(repeated) * multiplier > MAX_COLLECTION_SIZE:
                    kind = "string characters" if isinstance(repeated, str) else "list items"
                    raise RuntimeErrorML(f"repeated {kind} exceed the MANA size limit ({MAX_COLLECTION_SIZE})")
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
        if hasattr(obj, name) and not name.startswith("_"):
            return getattr(obj, name)
        raise TypeErrorML(f"object has no property '{name}'")

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
        self.charge_operation(target, "shape", kwargs, 1.0)
        target.properties["shape"] = geometry
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
        """Fire one named spell and commit its changes; source syntax is standalone."""
        resolved = self._resolve_spell(spell, mode="release")
        return self._run_spell_mode("release", resolved)

    def op_post(self, spell):
        """Trial one named spell, print its trace, and roll back world changes."""
        resolved = self._resolve_spell(spell, mode="post")
        return self._run_spell_mode("post", resolved)

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

    def _run_spell_mode(self, mode: str, spell: FunctionValue | SpellInstance):
        instance = spell if isinstance(spell, SpellInstance) else None
        definition = instance.definition if instance is not None else spell
        spell_name = instance.name if instance is not None else definition.name
        result = SpellResult(mode=mode, spell=spell_name, mana_used=Quantity(0, MANA))
        snapshot_roots = [self.global_env, self.active_objects, spell, *self._target_context_stack]
        snapshot = self._snapshot_runtime_state(snapshot_roots)
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
                    print(f"[POST {spell_name}] inputs: {values}")
                result.incant_value = self._execute_definition(definition, normalized_args)
                if self._target_context_stack:
                    self._resolve_targeted_motion(result, self._target_context_stack[-1])
                result.ok = True
                result.trace.append(f"spell {spell_name} completed")
                if mode == "post":
                    print(f"[POST {spell_name}] spell completed")
            except MagicLangError as exc:
                active_location = getattr(self._diagnostic_context, "location", None)
                if active_location is not None:
                    exc.attach_location(*active_location)
                result.ok = False
                message = str(exc)
                result.errors.append(message)
                result.trace.append(f"ERROR: {message}")
                if mode == "post":
                    print(f"[POST {spell_name}] ERROR: {message}")
                elif mode == "release":
                    print(f"[RELEASE {spell_name}] ERROR: {message}")
            except Exception as exc:
                # Do not disguise interpreter defects as ordinary spell failures.
                # Roll back this run, print diagnostics for library-hosted use, and re-raise.
                self._restore_runtime_state(snapshot)
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

        if mode == "post":
            print(f"[POST {spell_name}] mana cost: {self._stable_value(result.mana_used)}")
            if result.created:
                created_summary = []
                for obj in result.created:
                    mass = obj.properties.get("mass")
                    mass_text = f", {self._stable_value(mass)}" if mass is not None else ""
                    created_summary.append(f"{self._object_label(obj)} ({obj.element}{mass_text})")
                print(f"[POST {spell_name}] created: {', '.join(created_summary)}")
            if result.hits:
                print(f"[POST {spell_name}] hits: {', '.join(self._stable_value(x) for x in result.hits)}")
            if result.errors:
                print(f"[POST {spell_name}] errors: {'; '.join(result.errors)}")

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
        if not self._spell_run_stack:
            return
        result = self._spell_run_stack[-1]
        result.trace.append(detail)
        if result.mode == "post" and self.trace_detail == "full":
            print(f"[POST {result.spell}] {detail}")

    def _record_created(self, obj, reason: str = "created"):
        if not isinstance(obj, MagicObject) or not self._spell_run_stack:
            return
        result = self._spell_run_stack[-1]
        if id(obj) in result._created_ids:
            return
        result._created_ids.add(id(obj))
        result.created.append(obj)
        mass = obj.properties.get("mass")
        mass_text = f", {self._stable_value(mass)}" if mass is not None else ""
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
            "elapsed_virtual_time": self.elapsed_virtual_time,
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
        self.elapsed_virtual_time = snapshot["elapsed_virtual_time"]
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
        print(separator.join(self.display_value(value) for value in values))
        return None

    @staticmethod
    def display_value(value):
        if isinstance(value, list):
            return "[" + ", ".join(Runtime.display_value(item) for item in value) + "]"
        if isinstance(value, int) and not isinstance(value, bool):
            try:
                return str(value)
            except ValueError as exc:
                raise RuntimeErrorML("integer is too large to display; reduce its size before using show()") from exc
        if isinstance(value, SpellResult):
            fields = [
                f"SpellResult: {value.spell}",
                f"mode: {value.mode}",
                f"ok: {value.ok}",
                f"committed: {value.committed}",
                f"incant_value: {Runtime.display_value(value.incant_value)}",
                f"created: {Runtime.display_value(value.created)}",
                f"affected: {Runtime.display_value(value.affected)}",
                f"changes: {Runtime.display_value(value.changes)}",
                f"hits: {Runtime.display_value(value.hits)}",
                f"mana_cost_readout: {Runtime.display_value(value.mana_used)}",
                f"rules_fired: {Runtime.display_value(value.rules_fired)}",
                f"errors: {Runtime.display_value(value.errors)}",
                f"trace: {Runtime.display_value(value.trace)}",
            ]
            return "\n".join(fields)
        return str(value)

    def op_active_objects(self):
        """Return active object values known to the current runtime, without a renderer."""
        return [obj for obj in self._collect_physics_objects() if obj.properties.get("active", True)]

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
            raise MagicErrorML("mana cost is calculated internally; do not pass mana= to an operation")
        energy_costed = {"heat", "cool", "velocity", "push", "pull", "reflect"}
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
            raise MagicErrorML("mana cost readout must be a finite non-negative number")
        try:
            amount = float(amount)
        except (OverflowError, ValueError) as exc:
            raise MagicErrorML("mana cost readout is outside the supported numeric range") from exc
        if not math.isfinite(amount):
            raise MagicErrorML("mana cost readout must be a finite non-negative number")
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
        """Record energy entering/leaving an object as an explicit ledger transfer."""
        if abs(float(delta_j)) <= 1e-9:
            return
        amount = abs(float(delta_j))
        label = self._object_label(target) if isinstance(target, MagicObject) else "world"
        if delta_j > 0:
            entry = {"operation": operation, "direction": "input", "source": source,
                     "target": label, "amount_j": amount, "delta_j": float(delta_j)}
            self.energy_input_j += amount
        else:
            entry = {"operation": operation, "direction": "output", "source": label,
                     "target": source, "amount_j": amount, "delta_j": float(delta_j)}
            self.energy_output_j += amount
        self.energy_ledger.append(entry)
        if self._spell_run_stack:
            direction = "input" if delta_j > 0 else "output"
            self._record_step(f"energy {direction}: {amount:g} J ({operation}; {source})")

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
        score_j = (thermal_j * thermal_factor + kinetic_j + released_j + bound_j)
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

        Gravity is an optional acceleration vector. No planetary gravity is assumed;
        pass it explicitly, for example direction(0, -1, 0) * 9.81 m/s2.
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
            gravity_vector = Vector3(0, 0, 0, ACCELERATION)
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
        fires = [0]
        remaining = seconds
        pair_check_budget = MAX_COLLISION_PAIR_CHECKS_PER_ADVANCE // step_count
        try:
            for _ in range(step_count):
                self._check_stop_requested()
                step = min(dt, remaining)
                step_world(self, step, gravity_vector, max_pair_checks=pair_check_budget)
                # Physics integration updates canonical energy outside language
                # operations, so refresh integrity after every completed step.
                for obj in self._collect_physics_objects():
                    if obj.properties.get("active", True):
                        self.update_total_energy(obj)
                self.elapsed_virtual_time += step
                self._advance_planar_channels(step)
                self._advance_schedulers_one_step(step, fires)
                remaining = max(0.0, remaining - step)
                self.timers = [timer for timer in self.timers if timer.active]
                self.event_handlers = [handler for handler in self.event_handlers if handler.active]
            return self.elapsed_virtual_time
        except Exception:
            self._restore_runtime_state(snapshot)
            raise

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
        reserved = (self.LANGUAGE_KEYWORDS | self.RESERVED_PROPERTIES | self.BUILTIN_NAMES
                    | set(ELEMENTS) | set(PLANAR_ELEMENT_NAMES) | {"Mana"})
        if allow_mana_parameter and name == "mana":
            return
        if name in reserved or name in {"distance", "magnitude", "aim"}:
            raise RuntimeErrorML(f"'{name}' is reserved and cannot be used as an identifier")
