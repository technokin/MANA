"""Optional three-dimensional vector and physics calculations for MANA.

This module is not the world engine. MANA's default world simulation remains
2D; imported 3D values are for geometry, planning, and calculations unless a
future world engine explicitly adds 3D motion support.
"""
from __future__ import annotations

import math
from typing import Any

from ..errors import PhysicsErrorML, TypeErrorML, UnitErrorML
from ..physics import (
    C, PLANCK_TEMPERATURE_K, Vector3, as_vector as as_vector, clamp_speed, displacement,
    enforce_speed, force, kinetic_energy, momentum, scalar as scalar,
)
from ..units import ACCELERATION, DIMENSIONLESS, FORCE, M, M2, VELOCITY, Quantity


def _component(value: Any, dimension, label: str) -> float:
    if isinstance(value, Quantity):
        if value.dimension != dimension:
            raise UnitErrorML(f"{label} must use {dimension}, not {value.dimension}")
        return value.value
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeErrorML(f"{label} must be a finite number or a {dimension} quantity")
    try:
        result = float(value)
    except (OverflowError, ValueError) as exc:
        raise PhysicsErrorML(f"{label} is outside the supported numeric range") from exc
    if not math.isfinite(result):
        raise TypeErrorML(f"{label} must be a finite number or a {dimension} quantity")
    return result


def vector(x, y, z) -> Vector3:
    """Create a dimensionless vector for general 3D mathematics."""
    return Vector3(_component(x, DIMENSIONLESS, "x"),
                   _component(y, DIMENSIONLESS, "y"),
                   _component(z, DIMENSIONLESS, "z"), DIMENSIONLESS)


def position(x, y, z) -> Vector3:
    """Create a position vector; plain numbers are interpreted as metres."""
    return Vector3(_component(x, M, "x"), _component(y, M, "y"), _component(z, M, "z"), M)


def velocity_vector(x, y, z) -> Vector3:
    return Vector3(_component(x, VELOCITY, "x velocity"),
                   _component(y, VELOCITY, "y velocity"),
                   _component(z, VELOCITY, "z velocity"), VELOCITY)


def acceleration_vector(x, y, z) -> Vector3:
    return Vector3(_component(x, ACCELERATION, "x acceleration"),
                   _component(y, ACCELERATION, "y acceleration"),
                   _component(z, ACCELERATION, "z acceleration"), ACCELERATION)


def magnitude(value):
    if not isinstance(value, Vector3):
        raise TypeErrorML("vector3d.magnitude() expects a vector")
    result = value.magnitude()
    return result if value.dimension == DIMENSIONLESS else Quantity(result, value.dimension)


def direction(x, y, z) -> Vector3:
    """Create a normalized, dimensionless 3D direction vector."""
    return normalize(vector(x, y, z))


def normalize(value) -> Vector3:
    if not isinstance(value, Vector3):
        raise TypeErrorML("vector3d.normalize() expects a vector")
    scale_value = max(abs(value.x), abs(value.y), abs(value.z))
    if scale_value <= 1e-15:
        raise PhysicsErrorML("cannot normalize a zero vector")
    x, y, z = value.x / scale_value, value.y / scale_value, value.z / scale_value
    norm = math.sqrt(x*x + y*y + z*z)
    return Vector3(x / norm, y / norm, z / norm, DIMENSIONLESS)


def rotate(value: Vector3, x=0, y=0, z=0) -> Vector3:
    """Rotate a vector by Euler angles (radians), in X then Y then Z order.

    Rotation changes direction only and preserves the vector's units. It is a
    calculation helper; it does not rotate or mutate a world object.
    """
    if not isinstance(value, Vector3):
        raise TypeErrorML("vector3d.rotate() expects a vector")
    ax = _component(x, DIMENSIONLESS, "x rotation")
    ay = _component(y, DIMENSIONLESS, "y rotation")
    az = _component(z, DIMENSIONLESS, "z rotation")
    cx, sx = math.cos(ax), math.sin(ax)
    cy, sy = math.cos(ay), math.sin(ay)
    cz, sz = math.cos(az), math.sin(az)
    # X rotation, then Y, then Z.
    x1, y1, z1 = value.x, value.y * cx - value.z * sx, value.y * sx + value.z * cx
    x2, y2, z2 = x1 * cy + z1 * sy, y1, -x1 * sy + z1 * cy
    return Vector3(x2 * cz - y2 * sz, x2 * sz + y2 * cz, z2, value.dimension)


def lerp(a: Vector3, b: Vector3, amount) -> Vector3:
    """Interpolate between matching-unit 3D vectors; amount is not clamped."""
    if not isinstance(a, Vector3) or not isinstance(b, Vector3):
        raise TypeErrorML("vector3d.lerp() expects two vectors")
    if a.dimension != b.dimension:
        raise UnitErrorML("vector3d.lerp() requires matching vector dimensions")
    t = _component(amount, DIMENSIONLESS, "interpolation amount")
    if 0.0 <= t <= 1.0:
        return Vector3((1-t)*a.x+t*b.x, (1-t)*a.y+t*b.y, (1-t)*a.z+t*b.z, a.dimension)
    return Vector3(a.x+(b.x-a.x)*t, a.y+(b.y-a.y)*t, a.z+(b.z-a.z)*t, a.dimension)


def midpoint(a: Vector3, b: Vector3) -> Vector3:
    """Return the midpoint of two matching-unit 3D vectors."""
    return lerp(a, b, 0.5)


def dot(a, b) -> Quantity:
    if not isinstance(a, Vector3) or not isinstance(b, Vector3):
        raise TypeErrorML("vector3d.dot() expects two vectors")
    # Dot products multiply units, so unlike vector addition they do not
    # require the input vectors to have matching dimensions.
    return a.dot(b)


def cross(a, b) -> Vector3:
    if not isinstance(a, Vector3) or not isinstance(b, Vector3):
        raise TypeErrorML("vector3d.cross() expects two vectors")
    dim = a.dimension * b.dimension
    return Vector3(a.y * b.z - a.z * b.y,
                   a.z * b.x - a.x * b.z,
                   a.x * b.y - a.y * b.x, dim)


def distance(a, b) -> Quantity:
    if not isinstance(a, Vector3) or not isinstance(b, Vector3):
        raise TypeErrorML("vector3d.distance() expects two vectors")
    if a.dimension != b.dimension:
        raise UnitErrorML("vector3d.distance() requires matching coordinate units")
    return Quantity((a - b).magnitude(), a.dimension)


def angle_between(a, b) -> float:
    if not isinstance(a, Vector3) or not isinstance(b, Vector3):
        raise TypeErrorML("vector3d.angle_between() expects two vectors")
    if a.dimension != b.dimension:
        raise UnitErrorML("angle_between() requires matching vector dimensions")
    scale_a = max(abs(a.x), abs(a.y), abs(a.z))
    scale_b = max(abs(b.x), abs(b.y), abs(b.z))
    if scale_a <= 1e-15 or scale_b <= 1e-15:
        raise PhysicsErrorML("angle_between() is undefined for a zero vector")
    ax, ay, az = a.x / scale_a, a.y / scale_a, a.z / scale_a
    bx, by, bz = b.x / scale_b, b.y / scale_b, b.z / scale_b
    norm_a = math.sqrt(ax*ax + ay*ay + az*az)
    norm_b = math.sqrt(bx*bx + by*by + bz*bz)
    ax, ay, az = ax / norm_a, ay / norm_a, az / norm_a
    bx, by, bz = bx / norm_b, by / norm_b, bz / norm_b
    cosine = ax*bx + ay*by + az*bz
    return math.acos(max(-1.0, min(1.0, cosine)))


def project(value, onto) -> Vector3:
    if not isinstance(value, Vector3) or not isinstance(onto, Vector3):
        raise TypeErrorML("vector3d.project() expects two vectors")
    scale_value = max(abs(onto.x), abs(onto.y), abs(onto.z))
    if scale_value <= 1e-15:
        raise PhysicsErrorML("cannot project onto a zero vector")
    sx, sy, sz = onto.x / scale_value, onto.y / scale_value, onto.z / scale_value
    norm = math.sqrt(sx*sx + sy*sy + sz*sz)
    ux, uy, uz = sx/norm, sy/norm, sz/norm
    value_scale = max(abs(value.x), abs(value.y), abs(value.z))
    if value_scale == 0:
        return Vector3(0, 0, 0, value.dimension)
    vx, vy, vz = value.x / value_scale, value.y / value_scale, value.z / value_scale
    amount_scaled = vx*ux + vy*uy + vz*uz
    return Vector3((amount_scaled*ux)*value_scale,
                   (amount_scaled*uy)*value_scale,
                   (amount_scaled*uz)*value_scale, value.dimension)


def reflect(value, normal) -> Vector3:
    if not isinstance(value, Vector3) or not isinstance(normal, Vector3):
        raise TypeErrorML("vector3d.reflect() expects vectors")
    unit = normalize(normal)
    value_scale = max(abs(value.x), abs(value.y), abs(value.z))
    if value_scale == 0:
        return Vector3(0, 0, 0, value.dimension)
    vx, vy, vz = value.x/value_scale, value.y/value_scale, value.z/value_scale
    twice_scaled = 2 * (vx*unit.x + vy*unit.y + vz*unit.z)
    return Vector3((vx - twice_scaled*unit.x)*value_scale,
                   (vy - twice_scaled*unit.y)*value_scale,
                   (vz - twice_scaled*unit.z)*value_scale, value.dimension)


def scale(value, factor) -> Vector3:
    if not isinstance(value, Vector3):
        raise TypeErrorML("vector3d.scale() expects a vector")
    amount = _component(factor, DIMENSIONLESS, "scale factor")
    return Vector3(value.x*amount, value.y*amount, value.z*amount, value.dimension)


def components(value) -> list[Quantity]:
    if not isinstance(value, Vector3):
        raise TypeErrorML("vector3d.components() expects a vector")
    return [Quantity(value.x, value.dimension), Quantity(value.y, value.dimension), Quantity(value.z, value.dimension)]


def is_zero(value, tolerance=1e-12) -> bool:
    if not isinstance(value, Vector3):
        raise TypeErrorML("vector3d.is_zero() expects a vector")
    tolerance_value = _component(tolerance, value.dimension, "tolerance")
    if tolerance_value < 0:
        raise PhysicsErrorML("vector3d.is_zero() tolerance cannot be negative")
    return value.magnitude() <= tolerance_value


def planar(value: Vector3) -> Vector3:
    """Explicitly project a 3D vector onto the x-y plane, preserving units.

    This is the deliberate bridge between vector3d calculations and MANA's
    current 2D world simulation. It is not a 3D-to-2D world teleport; it returns
    a new vector with z=0 for use by motion/control operations.
    """
    if not isinstance(value, Vector3):
        raise TypeErrorML("vector3d.planar() expects a vector")
    return Vector3(value.x, value.y, 0.0, value.dimension)


def is_planar(value: Vector3, tolerance=1e-12) -> bool:
    """Return whether a vector's z component is within the supplied tolerance."""
    if not isinstance(value, Vector3):
        raise TypeErrorML("vector3d.is_planar() expects a vector")
    tolerance_value = _component(tolerance, value.dimension, "tolerance")
    if tolerance_value < 0:
        raise PhysicsErrorML("vector3d.is_planar() tolerance cannot be negative")
    return abs(value.z) <= tolerance_value


def object_vector(value: Any, field: str = "pos") -> Vector3:
    """Read a vector-valued property from a MANA world object or return a vector.

    This is read-only. Mutations still go through MANA operations so the runtime
    can enforce 2D-world constraints and maintain energy accounting.
    """
    if isinstance(value, Vector3):
        return value
    properties = getattr(value, "properties", None)
    if not isinstance(properties, dict):
        raise TypeErrorML("vector3d.object_vector() expects a vector or MANA object")
    allowed = {"pos", "vel", "acc", "force", "momentum", "direction", "anchor_pos"}
    if not isinstance(field, str) or field not in allowed:
        raise TypeErrorML("vector3d.object_vector() field must be pos, vel, acc, force, momentum, direction, or anchor_pos")
    result = properties.get(field)
    if not isinstance(result, Vector3):
        raise UnitErrorML(f"object has no vector-valued '{field}' property")
    return result


def pressure(force_value, area) -> Quantity:
    """Calculate pressure from a force magnitude/vector and a positive area."""
    if isinstance(force_value, Vector3):
        if force_value.dimension != FORCE:
            raise UnitErrorML(f"vector3d.pressure() force vector must use N, not {force_value.dimension}")
        force_magnitude = force_value.magnitude()
    elif isinstance(force_value, Quantity):
        if force_value.dimension != FORCE:
            raise UnitErrorML(f"vector3d.pressure() force must use N, not {force_value.dimension}")
        force_magnitude = abs(force_value.value)
    elif isinstance(force_value, bool) or not isinstance(force_value, (int, float)):
        raise TypeErrorML("vector3d.pressure() force must be a force quantity or force vector")
    else:
        raise UnitErrorML("vector3d.pressure() force must include N units")
    if not isinstance(area, Quantity) or area.dimension != M2:
        actual = area.dimension if isinstance(area, Quantity) else "a plain number"
        raise UnitErrorML(f"vector3d.pressure() area must use m2, not {actual}")
    if area.value <= 0:
        raise PhysicsErrorML("vector3d.pressure() area must be greater than zero")
    return Quantity(force_magnitude / area.value, FORCE / M2)


def build_library() -> dict[str, Any]:
    """Return the public API exposed by ``import vector3d`` inside MANA."""
    return {
        "C": Quantity(C, VELOCITY),
        "PLANCK_TEMPERATURE_K": PLANCK_TEMPERATURE_K,
        "vector": vector,
        "direction": direction,
        "position": position,
        "velocity_vector": velocity_vector,
        "acceleration_vector": acceleration_vector,
        "magnitude": magnitude,
        "normalize": normalize,
        "rotate": rotate,
        "lerp": lerp,
        "midpoint": midpoint,
        "dot": dot,
        "cross": cross,
        "distance": distance,
        "angle_between": angle_between,
        "project": project,
        "reflect": reflect,
        "scale": scale,
        "components": components,
        "is_zero": is_zero,
        "planar": planar,
        "is_planar": is_planar,
        "object_vector": object_vector,
        "clamp_speed": clamp_speed,
        "enforce_speed": enforce_speed,
        "displacement": displacement,
        "kinetic_energy": kinetic_energy,
        "momentum": momentum,
        "force": force,
        "pressure": pressure,
    }


__all__ = ["Vector3", "as_vector", "clamp_speed", "displacement", "enforce_speed",
           "force", "kinetic_energy", "momentum", "pressure", "scalar",
           "vector", "direction", "position", "velocity_vector", "acceleration_vector", "magnitude",
           "normalize", "rotate", "lerp", "midpoint", "dot", "cross", "distance", "angle_between", "project", "reflect",
           "scale", "components", "is_zero", "planar", "is_planar", "object_vector", "build_library"]
