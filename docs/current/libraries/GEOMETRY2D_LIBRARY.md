# `geometry2d` — Advanced 2D Geometry Library

**Page kind:** Reference  

**MANA version:** 2.0.0
**Import:** `load geometry2d`

The 2D world engine always works without importing anything. It already integrates motion, selects a target-directed heading for scalar `velocity` inside `tgset(target):`, detects circular collisions, and applies the configured collision response. `geometry2d` adds direct access to planar calculations for spell authors who want more precise control.

All calls are namespaced: use `geometry2d.distance(...)`, not a bare `distance(...)`. This prevents collisions with other libraries. All points must lie in the x-y plane (`z = 0`). Positions use metres, speed uses metres per second, and angles are plain numbers in **radians** unless a conversion function is used.

## Quick example

```mana
load geometry2d

origin = geometry2d.point(0 m, 0 m)
corner = geometry2d.point(3 m, 4 m)
separation = geometry2d.distance(origin, corner)
north = geometry2d.direction(0, 1)
turn = geometry2d.to_radians(45)
rotated = geometry2d.rotate_vector(north, turn)
show separation
```

Expected output:

```text
5 m
```

## Vector and direction helpers

| Function | What it does |
|---|---|
| `direction(x, y[, z=0])` | Returns a normalized planar direction. A non-zero `z` or a zero vector raises an error. |
| `point(x, y)` | Creates a position vector in metres. Bare numbers are treated as metre coordinates. |
| `coordinates(vector)` | Returns a two-item list containing the vector's x and y quantities with their units preserved. |
| `angle(vector)` | Returns the direction angle from positive x, in radians. |
| `angle_between(a, b)` | Returns the unsigned angle between nonzero planar vectors, in radians. |
| `rotate_vector(vector, radians)` / `rotate(vector, radians)` | Rotates a vector counter-clockwise while preserving its units. `rotate` is a concise alias. |
| `scale(vector, factor)` | Multiplies both planar components by a finite dimensionless factor while preserving the vector units. |
| `normalize(vector)` | Returns a unit direction from a nonzero vector. |
| `perpendicular(vector)` | Rotates a vector 90 degrees counter-clockwise without changing its magnitude or units. |
| `dot(a, b)` | Returns the scalar dot product, including the product of the input units. |
| `cross(a, b)` | Returns the signed scalar 2D cross product, including the product of the input units. |
| `midpoint(a, b)` | Returns the point halfway between two positions or positioned objects. |
| `lerp(a, b, t)` | Interpolates between matching-dimensional planar vectors. `t` is a plain numeric fraction; values outside 0–1 extrapolate. |
| `project(vector, onto)` | Returns the projection of one planar vector onto another nonzero vector. |
| `reflect_vector(vector, normal)` | Reflects a vector across a supplied nonzero planar normal. |
| `polar(length, radians)` | Creates a vector from a length and angle. The angle is in radians. |

## Angle conversion

| Function | What it does |
|---|---|
| `to_radians(degrees)` | Converts degrees to radians. |
| `to_degrees(radians)` | Converts radians to degrees. |

## Length, area, and shape calculations

| Function | What it does |
|---|---|
| `distance(a, b)` | Returns the separation in metres between two positions or objects with positions. |
| `circle_area(radius)` | Calculates the area of a circle in square metres from a non-negative radius in metres. |
| `circle_circumference(radius)` | Returns the perimeter of a circle in metres. |
| `polygon_area(points)` | Returns the absolute area of a polygon specified by a list of at least three planar points. |
| `closest_point_on_segment(point, a, b)` | Finds the nearest point on the closed segment from `a` to `b`. |
| `point_in_circle(point, centre, radius)` | Checks whether a point lies inside or on a circle. |
| `circles_intersect(centre_a, radius_a, centre_b, radius_b)` | Checks whether two circles overlap or touch. |
| `line_intersection(a1, a2, b1, b2)` | Calculates where two infinite lines intersect; parallel lines return `false`. |
| `segment_intersection(a1, a2, b1, b2)` | Calculates an intersection limited to the two finite segments; non-intersecting segments return `false`; collinear segments return a deterministic shared endpoint when they overlap or touch. |
| `point_in_polygon(point, vertices)` | Tests whether a point lies inside a polygon or on its boundary. |

## Explicit aiming helper

| Function | What it does |
|---|---|
| `aim(object, direction_vector)` | Sets a normalized planar direction on an object. It is an explicit, advanced helper; normal target-directed casting does not require it. |

For a manually specified direction, use `velocity(object, speed_vector)`. For target-directed casting, select the target outside the spell:

```mana
npc = tgset:
    hp = 100
    max_hp = 100
    distance = 10 m

spell fireball():
    projectile = create Fire
    shape(projectile, circle)
    velocity(projectile, 300 m/s)
    incant projectile

tgset(npc):
    release(fireball)
```

Expected output:

```text
(no output)
```

Then `velocity(projectile, 300 m/s)` inside the spell aims toward the selected target automatically. The engine computes the geometry and flight.

## Numerical stability

- Direction normalization and angle-between calculations scale components before forming a magnitude, avoiding avoidable overflow for very large finite vectors.
- `midpoint()` and `lerp()` use overflow-resistant interpolation when computing between endpoints; `project()` and `reflect_vector()` scale intermediate dot products.
- `closest_point_on_segment()` scales its projection calculation to avoid overflowing squared segment lengths and supports extremely distant points without dividing by a tiny segment length.
- These changes do not provide arbitrary-precision geometry. Intersection routines still use floating-point tolerances, so nearly parallel or extremely differently scaled coordinates can remain numerically sensitive.

## Errors and limits

- A nonzero z coordinate raises `PhysicsErrorML`; use `vector3d` for standalone 3D calculations.
- A zero vector cannot be normalized or used as a direction.
- Functions that require lengths enforce metre units; vector operations require compatible dimensions.
- These functions calculate geometry; they do not add exact polygon collision to the world physics engine. World collision bounds are currently circles derived from projected area or an explicit collision radius.
- Importing this library does not enable or disable physics. It only makes these extra calculation tools accessible.
