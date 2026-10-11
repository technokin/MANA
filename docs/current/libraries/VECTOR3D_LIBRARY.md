# `vector3d` — Three-Dimensional Calculation Library

**Page kind:** Reference  

**MANA version:** 1.0.0
**Import:** `load vector3d`

This library makes standalone three-dimensional vector mathematics available in MANA. It does **not** create a 3D world: the main simulation, object movement, targeting, collisions, and world gravity remain restricted to the x-y plane. A vector with a nonzero z component cannot move a world object.

Every function is namespaced, such as `vector3d.cross(a, b)`. This avoids accidentally colliding with the 2D API or global MANA operations.

## Constructors

| Function or value | What it does |
|---|---|
| `vector3d.vector(x, y, z)` | Creates a dimensionless 3D vector from numeric components. |
| `vector3d.direction(x, y, z)` | Creates a normalized 3D direction; the zero vector is invalid. |
| `vector3d.position(x, y, z)` | Creates a position vector in metres; plain numbers are interpreted as metres. |
| `vector3d.velocity_vector(x, y, z)` | Creates a velocity vector with all three components in m/s. |
| `vector3d.acceleration_vector(x, y, z)` | Creates an acceleration vector with all components in m/s². |
| `vector3d.C` | Speed of light in m/s. |
| `vector3d.PLANCK_TEMPERATURE_K` | Planck-temperature constant used by the physics model. |

## Vector operations

| Function | What it does |
|---|---|
| `magnitude(vector)` | Returns a plain number for dimensionless vectors, otherwise a `Quantity` using the vector's dimension. |
| `normalize(vector)` | Returns a unit vector in the same direction. |
| `dot(a, b)` | Returns the dot product with units composed from the input dimensions; unlike vector addition, the inputs do not need matching dimensions. |
| `cross(a, b)` | Returns the vector cross product. |
| `distance(a, b)` | Returns the Euclidean distance between two vectors with matching dimensions. |
| `angle_between(a, b)` | Returns the unsigned angle in radians between two nonzero vectors. |
| `project(vector, onto)` | Projects a vector onto another nonzero vector. |
| `reflect(vector, normal)` | Reflects a vector around a supplied normal. |
| `scale(vector, factor)` | Scales a vector by a dimensionless factor. |
| `components(vector)` | Returns the x, y and z components as quantities preserving units. |
| `is_zero(vector[, tolerance])` | Checks whether its magnitude is within a tolerance; a dimensional vector requires a tolerance in the same dimension. |

## Physical calculation helpers

| Function | What it does |
|---|---|
| `clamp_speed(vector)` | Returns the vector with magnitude limited below the speed-of-light limit, following the host physics helper's tolerance. |
| `enforce_speed(vector)` | Validates speed against the universal limit and raises a physics error if invalid. |
| `displacement(position, direction, distance)` | Returns a new metre-based position offset from `position` along `direction` by `distance`. Direction must be nonzero. |
| `kinetic_energy(mass, velocity)` | Calculates relativistic kinetic energy for the supplied mass and 3D velocity vector. |
| `momentum(mass, velocity)` | Calculates relativistic momentum. |
| `force(mass, acceleration)` | Calculates force from mass and acceleration. |
| `pressure(force, area)` | Accepts a force quantity in N or a force vector in N, and a positive area in m²; returns pressure in Pa. Bare numeric force/area values are rejected. |

## Example

```mana
load vector3d

v = vector3d.velocity_vector(3 m/s, 4 m/s, 12 m/s)
show vector3d.magnitude(v)
show vector3d.components(v)
show vector3d.displacement(vector3d.position(0, 0, 0), v, 2 m)
show vector3d.pressure(10 N, 2 m2)
```

Expected output:

```text
13 m/s
[3 m/s, 4 m/s, 12 m/s]
Vector3(0.461538, 0.615385, 1.84615) [m]
5 Pa
```

This is a calculation-only example. Do not assign this vector as the velocity of a world object if its z component is nonzero; the 2D world engine will reject it.

## Numerical stability

- Magnitude uses a scaled hypotenuse implementation. `normalize()`, `angle_between()`, and `project()` avoid forming an unnecessarily large intermediate magnitude.
- Projection and reflection scale the input before dot-product operations, so representable output components are not lost solely because an intermediate scalar projection overflows.
- A requested result whose actual component or magnitude cannot be represented as a finite float still raises a numeric error; these routines are not arbitrary-precision arithmetic.

## Compatibility with `geometry2d`

The libraries can be imported in the same program:

```mana
load geometry2d
load vector3d

north = geometry2d.direction(0, 1)
three_d = vector3d.direction(1, 2, 3)
```

Expected output:

```text
(no output)
```

Their functions remain isolated under `geometry2d` and `vector3d`. Importing 3D math never changes the world's dimensionality.


## Interoperation with the world and planar libraries

The world simulation is still 2D. The following functions help 3D calculations work with ordinary MANA objects without pretending the simulation has 3D collisions or motion:

| Function | Behaviour |
|---|---|
| `vector3d.planar(vector)` | Returns a copy with z=0, preserving the vector's units. Use this explicitly before passing a 3D position to operations that affect the 2D world. |
| `vector3d.is_planar(vector[, tolerance])` | Returns true if z is within the supplied tolerance. Dimensional vectors use a tolerance in the same dimension. |
| `vector3d.object_vector(object[, field="pos"])` | Reads a vector-valued field from a world object, such as the position, velocity or momentum of a being returned by `summoning` or `necromancy`. Valid fields are `pos`, `vel`, `acc`, `force`, `momentum`, `direction`, and `anchor_pos`. It is read-only. |

Example combining plane access, summoning, and 3D calculations:

```mana
load planes
load summoning
load vector3d

planes.open_path("Wild Realm", "Mortal Plane")
start3 = vector3d.position(2 m, 5 m, 0 m)
start2 = vector3d.planar(start3)
griffin = summoning.bring("Griffin", position=start2)
position = vector3d.object_vector(griffin)
show vector3d.is_planar(position)
```

Expected output:

```text
True
```

`planar()` only sets z to zero in a returned vector. It does not silently move an object or change the original vector. An input position with non-zero z is rejected by summoning/world placement until a future 3D world engine exists.
