"""Configurable global physical laws for a MANA world.

These are simulation rules, not spell effects. Configuration is world state and
is committed/rolled back with spell execution, recorded for replay, and applied
by the runtime's physics and material systems.
"""
from __future__ import annotations

import math
from typing import Any

from ..errors import MagicErrorML, PhysicsErrorML, TypeErrorML, UnitErrorML
from ..physics import Vector3, require_2d_world_vector
from ..units import ACCELERATION, DENSITY, DIMENSIONLESS, Quantity

DEFAULTS: dict[str, Any] = {
    "gravity": Vector3(0, 0, 0, ACCELERATION),
    "air_density_kg_m3": 1.225,
    "default_restitution": 0.2,
    "friction_coefficient": 0.35,
    "drag_enabled": True,
    "thermal_exchange_enabled": True,
    "phase_changes_enabled": True,
    "wetting_enabled": True,
}


def _number(value: Any, label: str) -> float:
    if isinstance(value, Quantity):
        if value.dimension != DIMENSIONLESS:
            raise UnitErrorML(f"{label} must be dimensionless")
        value = value.value
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeErrorML(f"{label} must be a finite number")
    value = float(value)
    if not math.isfinite(value):
        raise PhysicsErrorML(f"{label} must be finite")
    return value


def _serialise(settings: dict[str, Any]) -> dict[str, Any]:
    gravity = settings["gravity"]
    return {
        "gravity_m_s2": [gravity.x, gravity.y],
        "air_density_kg_m3": settings["air_density_kg_m3"],
        "default_restitution": settings["default_restitution"],
        "friction_coefficient": settings["friction_coefficient"],
        "drag_enabled": settings["drag_enabled"],
        "thermal_exchange_enabled": settings["thermal_exchange_enabled"],
        "phase_changes_enabled": settings["phase_changes_enabled"],
        "wetting_enabled": settings["wetting_enabled"],
    }


def build_library(runtime: Any) -> dict[str, Any]:
    def current() -> dict[str, Any]:
        """Return the active world-law settings in a serialisable form."""
        return _serialise(runtime.world_settings)

    def laws() -> list[dict[str, Any]]:
        """Describe the world rules that the engine actually applies."""
        s = runtime.world_settings
        return [
            {"name": "Newton's second law", "rule": "F = m a", "active": True,
             "detail": "Forces change velocity according to mass."},
            {"name": "Swept collision", "rule": "first contact along the integration step", "active": True,
             "detail": "Projectile/object contact is resolved before an object can pass through a target."},
            {"name": "Restitution", "rule": f"e = {s['default_restitution']:g} by default", "active": True,
             "detail": "Objects may override restitution individually."},
            {"name": "Contact friction", "rule": f"mu = {s['friction_coefficient']:g} by default", "active": s["friction_coefficient"] > 0,
             "detail": "Coulomb-style tangential impulse is capped by friction coefficient times the normal impulse; spin/rolling friction are not modelled."},
            {"name": "Gravity", "rule": f"g = ({s['gravity'].x:g}, {s['gravity'].y:g}) m/s²", "active": True},
            {"name": "Aerodynamic drag", "rule": f"rho = {s['air_density_kg_m3']:g} kg/m³", "active": s["drag_enabled"],
             "detail": "Wind drag uses relative velocity, area, mass, air density and drag coefficient."},
            {"name": "Material phase", "rule": "temperature crosses material transition points", "active": s["phase_changes_enabled"],
             "detail": "Known melting/boiling points apply at the catalogue's reference pressure."},
            {"name": "Thermal exchange", "rule": "object temperature approaches ambient temperature", "active": s["thermal_exchange_enabled"]},
            {"name": "Wetness exchange", "rule": "precipitation wets and dry weather dries surfaces", "active": s["wetting_enabled"]},
            {"name": "Matter conservation", "rule": "transmute() preserves mass by default", "active": True,
             "detail": "Use preserve_mass=false only when you explicitly want volume preserved instead."},
            {"name": "Identity conservation", "rule": "shape/transmute/transfigure keep the same entity ID", "active": True},
        ]

    def configure(*, gravity: Any = None, air_density: Any = None, restitution: Any = None,
                  friction: Any = None, drag: Any = None, thermal_exchange: Any = None, phase_changes: Any = None,
                  wetting: Any = None) -> dict[str, Any]:
        """Change global physical defaults; omitted options retain their values."""
        if getattr(runtime, "_pure_call_depth", 0):
            raise MagicErrorML("world.configure() changes world laws; call it from a spell with post() or release()")
        # Validate against a staged copy. A bad later argument must not leave
        # earlier settings partially applied (for example valid gravity followed
        # by a negative air density).
        s = dict(runtime.world_settings)
        if gravity is not None:
            if not isinstance(gravity, Vector3) or gravity.dimension != ACCELERATION:
                raise UnitErrorML("world.configure() gravity must be an acceleration vector in m/s²")
            gravity = require_2d_world_vector(gravity, "world.configure() gravity")
            s["gravity"] = gravity
        if air_density is not None:
            if isinstance(air_density, Quantity):
                if air_density.dimension != DENSITY:
                    raise UnitErrorML("world.configure() air_density must use kg/m³")
                density = float(air_density.value)
            else:
                density = _number(air_density, "air_density")
            if not math.isfinite(density) or not 0 <= density <= 100:
                raise PhysicsErrorML("world.configure() air_density must be between 0 and 100 kg/m³")
            s["air_density_kg_m3"] = density
        if restitution is not None:
            value = _number(restitution, "restitution")
            if not 0 <= value <= 1:
                raise PhysicsErrorML("world.configure() restitution must be between 0 and 1")
            s["default_restitution"] = value
        if friction is not None:
            value = _number(friction, "friction")
            if not 0 <= value <= 2:
                raise PhysicsErrorML("world.configure() friction must be between 0 and 2")
            s["friction_coefficient"] = value
        for arg, key in ((drag, "drag_enabled"), (thermal_exchange, "thermal_exchange_enabled"),
                         (phase_changes, "phase_changes_enabled"), (wetting, "wetting_enabled")):
            if arg is not None:
                if not isinstance(arg, bool):
                    raise TypeErrorML(f"world.configure() {key} must be true or false")
                s[key] = arg
        runtime.world_settings = s
        result = current()
        runtime._observe("world.changed", operation="configure", settings=result)
        if getattr(runtime, "_spell_run_stack", None):
            runtime._record_step("world laws updated")
        return result

    def reset() -> dict[str, Any]:
        """Restore the engine's built-in physical defaults."""
        if getattr(runtime, "_pure_call_depth", 0):
            raise MagicErrorML("world.reset() changes world laws; call it from a spell with post() or release()")
        runtime.world_settings = dict(DEFAULTS)
        result = current()
        runtime._observe("world.changed", operation="reset", settings=result)
        return result

    def set_gravity(value: Any) -> dict[str, Any]:
        return configure(gravity=value)

    def set_air_density(value: Any) -> dict[str, Any]:
        return configure(air_density=value)

    def set_restitution(value: Any) -> dict[str, Any]:
        return configure(restitution=value)

    return {
        "current": current,
        "laws": laws,
        "configure": configure,
        "reset": reset,
        "set_gravity": set_gravity,
        "set_air_density": set_air_density,
        "set_restitution": set_restitution,
        "set_friction": lambda value: configure(friction=value),
    }
