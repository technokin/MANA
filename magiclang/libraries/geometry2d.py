"""Optional 2D geometry helpers exposed to MANA through ``import geometry2d``.

The world engine itself remains 2D without importing this module. Importing the
module only exposes additional coordinates, angles, shape math and explicit
trajectory helpers. The public API is intentionally written in plain Python so
it can also be tested independently of the MANA parser.
"""
from __future__ import annotations

import math
from typing import Any

from ..errors import PhysicsErrorML, TypeErrorML, UnitErrorML
from ..physics import Vector3
from ..units import DIMENSIONLESS, M, M2, Quantity


def _number(value: Any, label: str) -> float:
    if isinstance(value, Quantity):
        if value.dimension != DIMENSIONLESS:
            raise UnitErrorML(f"{label} must be a plain number, not {value.dimension}")
        return value.value
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeErrorML(f"{label} must be a finite number")
    try:
        result = float(value)
    except (OverflowError, ValueError) as exc:
        raise PhysicsErrorML(f"{label} is outside the supported numeric range") from exc
    if not math.isfinite(result):
        raise TypeErrorML(f"{label} must be a finite number")
    return result


def _length(value: Any, label: str) -> float:
    if isinstance(value, Quantity):
        if value.dimension != M:
            raise UnitErrorML(f"{label} must be measured in metres")
        return value.value
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeErrorML(f"{label} must be a finite distance in metres")
    try:
        result = float(value)
    except (OverflowError, ValueError) as exc:
        raise PhysicsErrorML(f"{label} is outside the supported numeric range") from exc
    if not math.isfinite(result):
        raise TypeErrorML(f"{label} must be a finite distance in metres")
    return result


def _position(value: Any, label: str = "point") -> Vector3:
    # For object arguments, positions are read from the object's current state.
    if hasattr(value, "properties") and isinstance(value.properties.get("pos"), Vector3):
        value = value.properties["pos"]
    if not isinstance(value, Vector3):
        raise TypeErrorML(f"{label} must be a 2D point or an object with a position")
    if value.dimension != M:
        raise UnitErrorML(f"{label} must use metre coordinates")
    if abs(value.z) > 1e-12:
        raise PhysicsErrorML(f"{label} must lie in the 2D x-y plane (z must be 0)")
    return Vector3(value.x, value.y, 0, M)


def _vector(value: Any, label: str = "vector") -> Vector3:
    if not isinstance(value, Vector3):
        raise TypeErrorML(f"{label} must be a vector")
    if abs(value.z) > 1e-12:
        raise PhysicsErrorML(f"{label} must lie in the 2D x-y plane (z must be 0)")
    return Vector3(value.x, value.y, 0, value.dimension)


def _radius(value: Any, label: str = "radius") -> float:
    radius = _length(value, label)
    if radius < 0:
        raise PhysicsErrorML(f"{label} cannot be negative")
    return radius


def _unit_xy(value: Vector3, label: str = "vector") -> tuple[float, float]:
    """Return a stable unit direction without forming an overflowing magnitude."""
    scale = max(abs(value.x), abs(value.y))
    if scale <= 1e-15:
        raise PhysicsErrorML(f"{label} is undefined for the zero vector")
    x, y = value.x / scale, value.y / scale
    norm = math.hypot(x, y)
    return x / norm, y / norm


def direction(x: Any, y: Any, z: Any = 0) -> Vector3:
    """Return a normalized, dimensionless 2D direction vector; z must be zero."""
    x_value, y_value, z_value = _number(x, "direction x"), _number(y, "direction y"), _number(z, "direction z")
    if abs(z_value) > 1e-12:
        raise PhysicsErrorML("geometry2d.direction() requires z = 0; import vector3d for 3D vectors")
    ux, uy = _unit_xy(Vector3(x_value, y_value, 0, DIMENSIONLESS), "direction()")
    return Vector3(ux, uy, 0, DIMENSIONLESS)


def point(x: Any, y: Any) -> Vector3:
    """Create a 2D position; unitless coordinates are interpreted as metres."""
    return Vector3(_length(x, "point x"), _length(y, "point y"), 0, M)


def coordinates(value: Any) -> list[Quantity]:
    """Return a 2D vector's x and y components as quantities preserving units."""
    vector = _vector(value, "coordinates input")
    return [Quantity(vector.x, vector.dimension), Quantity(vector.y, vector.dimension)]


def angle(vector: Any) -> float:
    """Return the vector's planar angle from +X in radians."""
    value = _vector(vector)
    if math.hypot(value.x, value.y) <= 1e-15:
        raise PhysicsErrorML("angle() is undefined for the zero vector")
    return math.atan2(value.y, value.x)


def angle_between(a: Any, b: Any) -> float:
    """Return the unsigned angle between two vectors in radians."""
    va, vb = _vector(a, "first vector"), _vector(b, "second vector")
    if va.dimension != vb.dimension:
        raise UnitErrorML("angle_between() requires vectors with matching dimensions")
    # Normalize by each vector's largest component before calculating its
    # magnitude. math.hypot() can legitimately overflow when the true magnitude
    # exceeds the largest representable float, even though its direction exists.
    ax, ay = _unit_xy(va, "first vector")
    bx, by = _unit_xy(vb, "second vector")
    cosine = ax * bx + ay * by
    return math.acos(max(-1.0, min(1.0, cosine)))


def rotate_vector(vector: Any, radians: Any) -> Vector3:
    """Rotate a 2D vector counter-clockwise by an angle in radians."""
    value, theta = _vector(vector), _number(radians, "rotation angle")
    cosine, sine = math.cos(theta), math.sin(theta)
    return Vector3(value.x * cosine - value.y * sine,
                   value.x * sine + value.y * cosine, 0, value.dimension)


def normalize(vector: Any) -> Vector3:
    """Return a dimensionless unit direction from a non-zero 2D vector."""
    value = _vector(vector)
    ux, uy = _unit_xy(value, "normalize()")
    return Vector3(ux, uy, 0, DIMENSIONLESS)


def perpendicular(vector: Any) -> Vector3:
    """Return a 90-degree counter-clockwise vector with the same units."""
    value = _vector(vector)
    return Vector3(-value.y, value.x, 0, value.dimension)


def dot(a: Any, b: Any) -> Quantity:
    va, vb = _vector(a, "first vector"), _vector(b, "second vector")
    return Quantity(va.x * vb.x + va.y * vb.y, va.dimension * vb.dimension)


def cross(a: Any, b: Any) -> Quantity:
    """Return the signed 2D cross product (a scalar with product units)."""
    va, vb = _vector(a, "first vector"), _vector(b, "second vector")
    return Quantity(va.x * vb.y - va.y * vb.x, va.dimension * vb.dimension)


def distance(a: Any, b: Any) -> Quantity:
    """Return metre distance between two points or positioned objects."""
    pa, pb = _position(a, "first point"), _position(b, "second point")
    return Quantity(math.hypot(pa.x - pb.x, pa.y - pb.y), M)


def midpoint(a: Any, b: Any) -> Vector3:
    pa, pb = _position(a, "first point"), _position(b, "second point")

    def mid(x: float, y: float) -> float:
        # Same-sign differences cannot exceed the larger magnitude. Opposite-
        # sign sums cannot overflow, so branch to keep both cases safe.
        if (x < 0) != (y < 0):
            return (x + y) / 2
        return x + (y - x) / 2

    return Vector3(mid(pa.x, pb.x), mid(pa.y, pb.y), 0, M)


def lerp(a: Any, b: Any, amount: Any) -> Vector3:
    """Interpolate between same-unit 2D vectors; amount is normally from 0 to 1."""
    va, vb = _vector(a, "first vector"), _vector(b, "second vector")
    if va.dimension != vb.dimension:
        raise UnitErrorML("lerp() requires vectors with matching dimensions")
    t = _number(amount, "interpolation amount")
    if 0.0 <= t <= 1.0:
        # A weighted sum avoids overflowing vb - va for opposite-sign endpoints.
        x = (1.0 - t) * va.x + t * vb.x
        y = (1.0 - t) * va.y + t * vb.y
    else:
        x = va.x + (vb.x - va.x) * t
        y = va.y + (vb.y - va.y) * t
    return Vector3(x, y, 0, va.dimension)


def project(vector: Any, onto: Any) -> Vector3:
    """Project one 2D vector onto the direction of another; preserve first units."""
    value, axis = _vector(vector), _vector(onto, "projection axis")
    ux, uy = _unit_xy(axis, "project() axis")
    value_scale = max(abs(value.x), abs(value.y))
    if value_scale == 0:
        return Vector3(0, 0, 0, value.dimension)
    # Keep the dot product scaled. The unscaled scalar projection may exceed
    # the float range even where each resulting vector component is representable.
    amount_scaled = (value.x / value_scale) * ux + (value.y / value_scale) * uy
    return Vector3((amount_scaled * ux) * value_scale,
                   (amount_scaled * uy) * value_scale, 0, value.dimension)


def reflect_vector(vector: Any, normal: Any) -> Vector3:
    """Reflect a vector about a surface normal."""
    value, n = _vector(vector), normalize(normal)
    value_scale = max(abs(value.x), abs(value.y))
    if value_scale == 0:
        return Vector3(0, 0, 0, value.dimension)
    vx, vy = value.x / value_scale, value.y / value_scale
    projection_twice_scaled = 2 * (vx * n.x + vy * n.y)
    return Vector3((vx - projection_twice_scaled * n.x) * value_scale,
                   (vy - projection_twice_scaled * n.y) * value_scale, 0, value.dimension)


def polar(magnitude: Any, radians: Any) -> Vector3:
    """Build a vector from magnitude and angle in radians; magnitude units are retained."""
    theta = _number(radians, "polar angle")
    if isinstance(magnitude, Quantity):
        size, dim = magnitude.value, magnitude.dimension
    else:
        size, dim = _number(magnitude, "vector magnitude"), DIMENSIONLESS
    return Vector3(size * math.cos(theta), size * math.sin(theta), 0, dim)


def to_radians(degrees: Any) -> float:
    return math.radians(_number(degrees, "degrees"))


def to_degrees(radians: Any) -> float:
    return math.degrees(_number(radians, "radians"))


def circle_area(radius: Any) -> Quantity:
    r = _radius(radius)
    return Quantity(math.pi * r * r, M2)


def circle_circumference(radius: Any) -> Quantity:
    return Quantity(2 * math.pi * _radius(radius), M)


def polygon_area(points: Any) -> Quantity:
    if not isinstance(points, list) or len(points) < 3:
        raise TypeErrorML("polygon_area() expects a list of at least three 2D points")
    coords = [_position(point, "polygon point") for point in points]
    total = 0.0
    for index, current in enumerate(coords):
        nxt = coords[(index + 1) % len(coords)]
        total += current.x * nxt.y - nxt.x * current.y
    return Quantity(abs(total) / 2, M2)


def closest_point_on_segment(point_value: Any, start: Any, end: Any) -> Vector3:
    p, a, b = (_position(point_value, "point"), _position(start, "segment start"), _position(end, "segment end"))
    dx, dy = b.x - a.x, b.y - a.y
    if math.isfinite(dx) and math.isfinite(dy):
        segment_scale = max(abs(dx), abs(dy))
        if segment_scale == 0:
            return a
        ux, uy = dx / segment_scale, dy / segment_scale
        ratio_scale = segment_scale
    else:
        # Opposite-sign endpoints can overflow while subtracting. Normalize
        # endpoint coordinates first, retaining a factored segment scale.
        endpoint_scale = max(abs(a.x), abs(a.y), abs(b.x), abs(b.y))
        if endpoint_scale == 0:
            return a
        dx_scaled = b.x / endpoint_scale - a.x / endpoint_scale
        dy_scaled = b.y / endpoint_scale - a.y / endpoint_scale
        direction_scale = max(abs(dx_scaled), abs(dy_scaled))
        if direction_scale == 0:
            return a
        ux, uy = dx_scaled / direction_scale, dy_scaled / direction_scale
        ratio_scale = (endpoint_scale, direction_scale)
    denominator = ux * ux + uy * uy

    rx, ry = p.x - a.x, p.y - a.y
    if math.isfinite(rx) and math.isfinite(ry):
        point_scale = max(abs(rx), abs(ry))
        if point_scale == 0:
            return a
        rx_unit, ry_unit = rx / point_scale, ry / point_scale
        if isinstance(ratio_scale, tuple):
            ratio = (point_scale / ratio_scale[0]) / ratio_scale[1]
        else:
            ratio = point_scale / ratio_scale
    else:
        # Difference overflow implies widely separated magnitudes. Work with a
        # bounded normalized difference and keep its scale as a separate factor.
        coordinate_scale = max(abs(p.x), abs(p.y), abs(a.x), abs(a.y))
        if coordinate_scale == 0:
            return a
        rx_scaled = p.x / coordinate_scale - a.x / coordinate_scale
        ry_scaled = p.y / coordinate_scale - a.y / coordinate_scale
        point_delta_scale = max(abs(rx_scaled), abs(ry_scaled))
        if point_delta_scale == 0:
            return a
        rx_unit, ry_unit = rx_scaled / point_delta_scale, ry_scaled / point_delta_scale
        if isinstance(ratio_scale, tuple):
            ratio = ((coordinate_scale / ratio_scale[0]) / ratio_scale[1]) * point_delta_scale
        else:
            ratio = (coordinate_scale / ratio_scale) * point_delta_scale

    projection = rx_unit * ux + ry_unit * uy
    if projection <= 0:
        t = 0.0
    elif ratio >= denominator / projection:
        t = 1.0
    else:
        t = ratio * projection / denominator
    # Convex interpolation avoids overflowing b-a for opposite-sign endpoints.
    x = (1.0 - t) * a.x + t * b.x
    y = (1.0 - t) * a.y + t * b.y
    return Vector3(x, y, 0, M)

def point_in_circle(point_value: Any, center: Any, radius: Any) -> bool:
    return distance(point_value, center).value <= _radius(radius) + 1e-12


def circles_intersect(center_a: Any, radius_a: Any, center_b: Any, radius_b: Any) -> bool:
    return distance(center_a, center_b).value <= _radius(radius_a) + _radius(radius_b) + 1e-12


def _line_params(p1: Vector3, p2: Vector3, p3: Vector3, p4: Vector3):
    x1, y1, x2, y2 = p1.x, p1.y, p2.x, p2.y
    x3, y3, x4, y4 = p3.x, p3.y, p4.x, p4.y
    dx1, dy1, dx2, dy2 = x2 - x1, y2 - y1, x4 - x3, y4 - y3
    denominator = dx1 * dy2 - dy1 * dx2
    if abs(denominator) <= 1e-12:
        return None
    qx, qy = x3 - x1, y3 - y1
    t = (qx * dy2 - qy * dx2) / denominator
    u = (qx * dy1 - qy * dx1) / denominator
    return t, u, x1 + t * dx1, y1 + t * dy1


def line_intersection(a1: Any, a2: Any, b1: Any, b2: Any):
    """Return the intersection point of infinite lines, or False for parallel lines."""
    values = [_position(v, "line point") for v in (a1, a2, b1, b2)]
    result = _line_params(*values)
    if result is None:
        return False
    _t, _u, x, y = result
    return Vector3(x, y, 0, M)


def segment_intersection(a1: Any, a2: Any, b1: Any, b2: Any):
    """Return intersection point of two segments, or False if they do not cross."""
    values = [_position(v, "segment point") for v in (a1, a2, b1, b2)]
    result = _line_params(*values)
    if result is None:
        # Parallel lines may still be collinear. Return a deterministic shared
        # endpoint for touching/overlapping collinear segments.
        p1, p2, p3, p4 = values
        cross_value = (p2.x - p1.x) * (p3.y - p1.y) - (p2.y - p1.y) * (p3.x - p1.x)
        if abs(cross_value) > 1e-12:
            return False

        def on_segment(p, a, b):
            cross_ab = (b.x - a.x) * (p.y - a.y) - (b.y - a.y) * (p.x - a.x)
            if abs(cross_ab) > 1e-12:
                return False
            return (min(a.x, b.x) - 1e-12 <= p.x <= max(a.x, b.x) + 1e-12
                    and min(a.y, b.y) - 1e-12 <= p.y <= max(a.y, b.y) + 1e-12)

        shared = [p for p in (p1, p2, p3, p4)
                  if on_segment(p, p1, p2) and on_segment(p, p3, p4)]
        if not shared:
            return False
        shared.sort(key=lambda p: (p.x, p.y))
        return Vector3(shared[0].x, shared[0].y, 0, M)
    t, u, x, y = result
    if -1e-12 <= t <= 1 + 1e-12 and -1e-12 <= u <= 1 + 1e-12:
        return Vector3(x, y, 0, M)
    return False


def point_in_polygon(point_value: Any, points: Any) -> bool:
    p = _position(point_value, "point")
    if not isinstance(points, list) or len(points) < 3:
        raise TypeErrorML("point_in_polygon() expects a list of at least three points")
    polygon = [_position(item, "polygon point") for item in points]
    # Boundary points count as inside, including vertices and points on edges.
    for index, current in enumerate(polygon):
        nxt = polygon[(index + 1) % len(polygon)]
        closest = closest_point_on_segment(p, current, nxt)
        if math.hypot(closest.x - p.x, closest.y - p.y) <= 1e-12:
            return True
    inside = False
    j = len(polygon) - 1
    for i, current in enumerate(polygon):
        previous = polygon[j]
        if ((current.y > p.y) != (previous.y > p.y)) and (
            p.x < (previous.x - current.x) * (p.y - current.y) / (previous.y - current.y) + current.x
        ):
            inside = not inside
        j = i
    return inside


def build_library(runtime):
    """Return the public API exposed by ``import geometry2d`` inside MANA."""
    values = {
        "direction": direction,
        "point": point,
        "coordinates": coordinates,
        "angle": angle,
        "angle_between": angle_between,
        "rotate_vector": rotate_vector,
        "normalize": normalize,
        "perpendicular": perpendicular,
        "dot": dot,
        "cross": cross,
        "distance": distance,
        "midpoint": midpoint,
        "lerp": lerp,
        "project": project,
        "reflect_vector": reflect_vector,
        "polar": polar,
        "to_radians": to_radians,
        "to_degrees": to_degrees,
        "circle_area": circle_area,
        "circle_circumference": circle_circumference,
        "polygon_area": polygon_area,
        "closest_point_on_segment": closest_point_on_segment,
        "point_in_circle": point_in_circle,
        "circles_intersect": circles_intersect,
        "line_intersection": line_intersection,
        "segment_intersection": segment_intersection,
        "point_in_polygon": point_in_polygon,
        "aim": runtime.op_aim,
    }
    return values
