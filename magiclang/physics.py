from __future__ import annotations

import math
from dataclasses import dataclass

from .errors import PhysicsErrorML, TypeErrorML, UnitErrorML
from .units import (
    ACCELERATION, ENERGY, FORCE, KG, M, MOMENTUM, PRESSURE, VELOCITY,
    Dimension, Quantity, as_dimension,
)

C = 299_792_458.0
PLANCK_TEMPERATURE_K = 1.416784e32
SPEED_TOLERANCE = 1e-12


@dataclass(frozen=True, slots=True)
class Vector3:
    x: float
    y: float
    z: float
    dimension: Dimension = M

    def __post_init__(self):
        converted = []
        for item in (self.x, self.y, self.z):
            if isinstance(item, bool) or not isinstance(item, (int, float)):
                raise TypeErrorML("vector components must be finite numeric values")
            try:
                numeric = float(item)
            except (OverflowError, ValueError) as exc:
                raise PhysicsErrorML("vector component is outside the supported numeric range") from exc
            if not math.isfinite(numeric):
                raise TypeErrorML("vector components must be finite numeric values")
            converted.append(numeric)
        object.__setattr__(self, "x", converted[0])
        object.__setattr__(self, "y", converted[1])
        object.__setattr__(self, "z", converted[2])
        object.__setattr__(self, "dimension", as_dimension(self.dimension))

    @property
    def components(self) -> tuple[float, float, float]:
        return (self.x, self.y, self.z)

    def magnitude(self) -> float:
        value = math.hypot(self.x, self.y, self.z)
        if not math.isfinite(value):
            raise PhysicsErrorML("vector magnitude exceeds the supported numeric range")
        return value

    def _same(self, other: "Vector3"):
        if not isinstance(other, Vector3):
            raise TypeErrorML("vector operation requires another vector")
        if self.dimension != other.dimension:
            raise UnitErrorML(f"vector dimensions differ: {self.dimension} and {other.dimension}")

    def __add__(self, other):
        self._same(other)
        return Vector3(self.x + other.x, self.y + other.y, self.z + other.z, self.dimension)

    def __sub__(self, other):
        self._same(other)
        return Vector3(self.x - other.x, self.y - other.y, self.z - other.z, self.dimension)

    def __mul__(self, other):
        if isinstance(other, bool):
            raise TypeErrorML("boolean values cannot scale a vector")
        if isinstance(other, Quantity):
            return Vector3(self.x * other.value, self.y * other.value, self.z * other.value,
                           self.dimension * other.dimension)
        if isinstance(other, (int, float)):
            try:
                scale = float(other)
            except (OverflowError, ValueError) as exc:
                raise PhysicsErrorML("vector scale is outside the supported numeric range") from exc
            if not math.isfinite(scale):
                raise PhysicsErrorML("vector scale must be finite")
            return Vector3(self.x * scale, self.y * scale, self.z * scale, self.dimension)
        return NotImplemented

    def __rmul__(self, other):
        return self.__mul__(other)

    def __truediv__(self, other):
        if isinstance(other, bool):
            raise TypeErrorML("boolean values cannot scale a vector")
        if isinstance(other, Quantity):
            if other.value == 0:
                raise PhysicsErrorML("division by zero")
            return Vector3(self.x / other.value, self.y / other.value, self.z / other.value,
                           self.dimension / other.dimension)
        if isinstance(other, (int, float)):
            try:
                divisor = float(other)
            except (OverflowError, ValueError) as exc:
                raise PhysicsErrorML("vector divisor is outside the supported numeric range") from exc
            if not math.isfinite(divisor):
                raise PhysicsErrorML("vector divisor must be finite")
            if divisor == 0:
                raise PhysicsErrorML("division by zero")
            return Vector3(self.x / divisor, self.y / divisor, self.z / divisor, self.dimension)
        return NotImplemented

    def dot(self, other: "Vector3") -> Quantity:
        if not isinstance(other, Vector3):
            raise TypeErrorML("vector dot product requires another vector")
        return Quantity(self.x * other.x + self.y * other.y + self.z * other.z,
                        self.dimension * other.dimension)

    def scaled(self, scale: float, dimension: Dimension | None = None) -> "Vector3":
        return Vector3(self.x * scale, self.y * scale, self.z * scale, dimension or self.dimension)

    def normalized(self) -> "Vector3":
        # Scale before normalization to avoid overflow for very large finite
        # components. The vector's physical dimension is preserved.
        scale = max(abs(self.x), abs(self.y), abs(self.z))
        if scale == 0:
            raise PhysicsErrorML("cannot normalize a zero-length vector")
        x, y, z = self.x / scale, self.y / scale, self.z / scale
        norm = math.sqrt(x*x + y*y + z*z)
        return Vector3(x / norm, y / norm, z / norm, self.dimension)

    def __repr__(self):
        return f"Vector3({self.x:g}, {self.y:g}, {self.z:g}) [{self.dimension}]"


WORLD_PLANE_TOLERANCE = 1e-12


def require_2d_world_vector(vector: Vector3, label: str) -> Vector3:
    """Validate a vector used by the primary 2D world simulation.

    MANA keeps its general three-dimensional vector maths available for library
    calculations, but world objects move in the x-y plane. A tiny floating
    point residual is normalized to exactly zero; a meaningful z component is
    rejected rather than silently projected away.
    """
    if not isinstance(vector, Vector3):
        raise TypeErrorML(f"{label} requires a vector")
    if abs(vector.z) > WORLD_PLANE_TOLERANCE:
        raise PhysicsErrorML(
            f"{label} must lie in the 2D x-y world plane (z must be 0); "
            "3D vector calculations remain available outside world simulation"
        )
    if vector.z != 0.0:
        return Vector3(vector.x, vector.y, 0.0, vector.dimension)
    return vector


def scalar(value, dimension: Dimension | str | None = None) -> float:
    if isinstance(value, bool):
        raise TypeErrorML("boolean values are not numeric physical quantities")
    if isinstance(value, Quantity):
        if dimension is not None:
            from .units import as_dimension
            expected = as_dimension(dimension)
            if value.dimension != expected:
                raise UnitErrorML(f"expected {expected}, got {value.dimension}")
        return float(value.value)
    if isinstance(value, (int, float)):
        try:
            result = float(value)
        except (OverflowError, ValueError) as exc:
            raise PhysicsErrorML("numeric physical quantity is outside the supported range") from exc
        if not math.isfinite(result):
            raise PhysicsErrorML("numeric physical quantity must be finite")
        return result
    raise TypeErrorML(f"expected numeric value, got {type(value).__name__}")


def as_vector(value, dimension: Dimension, label: str) -> Vector3:
    if not isinstance(value, Vector3):
        raise TypeErrorML(f"{label} requires a vector")
    if value.dimension != dimension:
        raise UnitErrorML(f"{label} expects {dimension}, got {value.dimension}")
    return value


def kinetic_energy(mass: Quantity, velocity: Vector3) -> Quantity:
    m = scalar(mass, KG)
    v = as_vector(velocity, VELOCITY, "kinetic_energy velocity").magnitude()
    if v > C * (1 + SPEED_TOLERANCE):
        raise PhysicsErrorML("speed cannot exceed c")
    if m == 0:
        return Quantity(0, ENERGY)
    if v >= C:
        raise PhysicsErrorML("a massive object cannot reach c; relativistic energy diverges")
    beta = v / C
    beta2 = beta * beta
    # (1 - beta) * (1 + beta) retains precision much closer to c than
    # 1 - beta**2, which can round to zero before v reaches c.
    root = math.sqrt((1.0 - beta) * (1.0 + beta))
    # Stable form of (gamma - 1)mc²: avoids cancellation at low speeds.
    gamma_minus_one = beta2 / (root * (1.0 + root))
    return Quantity(gamma_minus_one * m * C * C, ENERGY)


def momentum(mass: Quantity, velocity: Vector3) -> Vector3:
    m = scalar(mass, KG)
    v = as_vector(velocity, VELOCITY, "momentum velocity")
    speed = v.magnitude()
    if speed > C * (1 + SPEED_TOLERANCE):
        raise PhysicsErrorML("speed cannot exceed c")
    if speed >= C:
        raise PhysicsErrorML("a massive object cannot reach c")
    beta = speed / C
    gamma = 1.0 / math.sqrt((1.0 - beta) * (1.0 + beta)) if m else 1.0
    return Vector3(*(gamma * m * x for x in v.components), dimension=MOMENTUM)


def force(mass: Quantity, acceleration: Vector3) -> Vector3:
    m = scalar(mass, KG)
    a = as_vector(acceleration, ACCELERATION, "force acceleration")
    return Vector3(*(m * x for x in a.components), dimension=FORCE)


def pressure(force_value: Vector3, area: Quantity) -> Quantity:
    force_vector = as_vector(force_value, FORCE, "pressure force")
    area_value = scalar(area, "m2")
    if area_value <= 0:
        raise PhysicsErrorML("area must be greater than zero")
    return Quantity(force_vector.magnitude() / area_value, PRESSURE)


def displacement(position: Vector3, direction: Vector3, distance: Quantity) -> Vector3:
    position = as_vector(position, M, "displacement position")
    distance_m = scalar(distance, M)
    if not isinstance(direction, Vector3):
        raise TypeErrorML("displacement direction must be a vector")
    if direction.magnitude() == 0:
        raise PhysicsErrorML("cannot move in a zero-length direction")
    unit = direction.normalized()
    return Vector3(
        position.x + unit.x * distance_m,
        position.y + unit.y * distance_m,
        position.z + unit.z * distance_m,
        M,
    )


def enforce_speed(velocity: Vector3, *, massive: bool = True) -> Vector3:
    speed = velocity.magnitude()
    if speed > C * (1 + SPEED_TOLERANCE):
        raise PhysicsErrorML(f"speed {speed:g} m/s exceeds c ({C:g} m/s)")
    if speed > C:
        scale = C / speed
        velocity = velocity.scaled(scale)
    if massive and speed >= C:
        raise PhysicsErrorML("a massive object cannot reach c")
    return velocity


def clamp_speed(velocity: Vector3) -> Vector3:
    """Compatibility helper: reject meaningful violations; normalize tiny float overshoot."""
    if not isinstance(velocity, Vector3) or velocity.dimension != VELOCITY:
        raise UnitErrorML("clamp_speed() expects a velocity vector")
    speed = velocity.magnitude()
    if speed > C * (1.0 + SPEED_TOLERANCE):
        raise PhysicsErrorML(f"speed {speed:g} m/s exceeds c ({C:g} m/s)")
    if speed > C:
        return velocity.scaled(C / speed)
    return velocity
