from __future__ import annotations

from dataclasses import dataclass, field
from functools import lru_cache
import math
from typing import Union

from .errors import PhysicsErrorML, TypeErrorML, UnitErrorML

# Base dimensions: kg, m, s, K, mana. Mana is deliberately independent of joules;
# the conversion rates are explicit runtime rules, not a claim that mana is SI energy.
_EXPONENT_NAMES = ("kg", "m", "s", "K", "mana")


@dataclass(frozen=True, slots=True)
class Dimension:
    exponents: tuple[int, int, int, int, int]

    def __mul__(self, other: "Dimension") -> "Dimension":
        return Dimension(tuple(a + b for a, b in zip(self.exponents, other.exponents)))

    def __truediv__(self, other: "Dimension") -> "Dimension":
        return Dimension(tuple(a - b for a, b in zip(self.exponents, other.exponents)))

    def __pow__(self, power: int) -> "Dimension":
        return Dimension(tuple(a * power for a in self.exponents))

    def __str__(self) -> str:
        # Do not pass _format_dimension() as dict.get's default: Python would
        # evaluate it even for the common, already-labelled SI dimensions.
        label = _DIMENSION_LABELS.get(self)
        return label if label is not None else _format_dimension(self.exponents)


@lru_cache(maxsize=256)
def _format_dimension(exponents: tuple[int, int, int, int, int]) -> str:
    num, den = [], []
    for name, power in zip(_EXPONENT_NAMES, exponents):
        if power > 0:
            num.append(name if power == 1 else f"{name}{power}")
        elif power < 0:
            den.append(name if power == -1 else f"{name}{-power}")
    if not num:
        num = ["1"]
    return "*".join(num) + ("/" + "*".join(den) if den else "")


DIMENSIONLESS = Dimension((0, 0, 0, 0, 0))
KG = Dimension((1, 0, 0, 0, 0))
M = Dimension((0, 1, 0, 0, 0))
S = Dimension((0, 0, 1, 0, 0))
K = Dimension((0, 0, 0, 1, 0))
MANA = Dimension((0, 0, 0, 0, 1))
M2 = M ** 2
M3 = M ** 3
VELOCITY = M / S
ACCELERATION = M / (S ** 2)
FORCE = KG * ACCELERATION
ENERGY = FORCE * M
PRESSURE = FORCE / M2
POWER = ENERGY / S
DENSITY = KG / M3
MOMENTUM = KG * VELOCITY
MANA_RATE = MANA / S

_DIMENSION_LABELS = {
    DIMENSIONLESS: "dimensionless", KG: "kg", M: "m", S: "s", K: "K",
    MANA: "mana", M2: "m2", M3: "m3", VELOCITY: "m/s",
    ACCELERATION: "m/s2", FORCE: "N", ENERGY: "J", PRESSURE: "Pa",
    POWER: "W", DENSITY: "kg/m3", MOMENTUM: "kg*m/s", MANA_RATE: "mana/s",
}

UNIT_DIMENSIONS: dict[str, Dimension] = {
    "1": DIMENSIONLESS,
    "kg": KG, "m": M, "s": S, "K": K, "mana": MANA,
    "m2": M2, "m^2": M2, "m3": M3, "m^3": M3,
    "m/s": VELOCITY, "m/s2": ACCELERATION, "m/s^2": ACCELERATION,
    "kg/m3": DENSITY, "kg/m^3": DENSITY,
    "N": FORCE, "J": ENERGY, "Pa": PRESSURE, "W": POWER,
    "kg*m/s": MOMENTUM, "mana/s": MANA_RATE,
}


def as_dimension(value: Union[str, Dimension]) -> Dimension:
    if isinstance(value, Dimension):
        return value
    if value in UNIT_DIMENSIONS:
        return UNIT_DIMENSIONS[value]
    raise UnitErrorML(f"unknown or unsupported dimension/unit '{value}'")


def parse_unit(text: str) -> Dimension:
    """Return the dimension of a unit, including supported SI-prefixed forms."""
    dimension, _scale = parse_unit_info(text)
    return dimension


_PREFIXES = {
    "k": 1e3,
    "M": 1e6,
    "G": 1e9,
    "m": 1e-3,
    "u": 1e-6,
    "n": 1e-9,
}


def _simple_unit_info(text: str) -> tuple[Dimension, float]:
    """Return (dimension, SI multiplier) for a simple unit token."""
    if text in UNIT_DIMENSIONS:
        return UNIT_DIMENSIONS[text], 1.0
    if text == "g":
        return KG, 1e-3
    for prefix, multiplier in _PREFIXES.items():
        if text.startswith(prefix) and len(text) > len(prefix):
            suffix = text[len(prefix):]
            if suffix in UNIT_DIMENSIONS:
                return UNIT_DIMENSIONS[suffix], multiplier
            if suffix == "g":
                return KG, multiplier * 1e-3
    raise UnitErrorML(f"unknown unit '{text}'")


def parse_unit_info(text: str) -> tuple[Dimension, float]:
    """Parse a supported unit expression and return its dimension and SI scale.

    Exact registered units take precedence over prefix parsing, so ``m`` remains
    metres and ``kg`` remains kilograms. Prefixes are accepted on registered
    simple units; gram is supported as a convenient submultiple of kilogram.
    Compound units with one slash can use prefixes on either simple component.
    """
    # Celsius is an affine absolute-temperature literal, not a scale unit.
    # It is permitted only as a standalone numeric literal (e.g. `20 C`),
    # never inside a compound unit such as `J/C`.
    if text == "C":
        return K, 1.0
    if "C" in text:
        raise UnitErrorML(f"C is only supported as a standalone absolute-temperature literal, not '{text}'")
    if text in UNIT_DIMENSIONS:
        return UNIT_DIMENSIONS[text], 1.0
    if text.count("/") == 1:
        numerator, denominator = text.split("/", 1)
        try:
            numerator_dim, numerator_scale = _simple_unit_info(numerator)
            denominator_dim, denominator_scale = _simple_unit_info(denominator)
        except UnitErrorML as exc:
            raise UnitErrorML(f"unknown unit '{text}'") from exc
        return numerator_dim / denominator_dim, numerator_scale / denominator_scale
    return _simple_unit_info(text)


@dataclass(frozen=True, slots=True)
class Quantity:
    value: float
    dimension: Union[str, Dimension] = DIMENSIONLESS
    is_absolute_temperature: bool = field(default=False, compare=False, repr=False)
    celsius_input_value: float | None = field(default=None, compare=False, repr=False)

    def __post_init__(self):
        if isinstance(self.value, bool) or not isinstance(self.value, (int, float)):
            raise TypeErrorML("quantity value must be numeric, not boolean or text")
        try:
            value = float(self.value)
        except (OverflowError, ValueError) as exc:
            raise PhysicsErrorML("quantity is outside the supported numeric range") from exc
        if not math.isfinite(value):
            raise PhysicsErrorML("quantity must be finite")
        dim = as_dimension(self.dimension)
        if dim == KG and value < 0:
            raise PhysicsErrorML("mass cannot be negative")
        if dim == M3 and value < 0:
            raise PhysicsErrorML("volume cannot be negative")
        if dim == K and self.is_absolute_temperature and value < 0:
            raise PhysicsErrorML("absolute temperature cannot be below 0 K")
        object.__setattr__(self, "value", value)
        object.__setattr__(self, "dimension", dim)

    def _other(self, other: object) -> "Quantity":
        if not isinstance(other, Quantity):
            other_kind = "a boolean" if isinstance(other, bool) else "a plain number" if isinstance(other, (int, float)) else type(other).__name__
            raise TypeErrorML(
                f"cannot combine a quantity in {self.dimension} with {other_kind}; "
                f"expected another quantity in {self.dimension}"
            )
        if self.dimension != other.dimension:
            raise UnitErrorML(f"incompatible dimensions: {self.dimension} and {other.dimension}")
        return other

    def __add__(self, other):
        other = self._other(other)
        if self.is_absolute_temperature and other.is_absolute_temperature:
            raise UnitErrorML("two absolute temperatures cannot be added")
        return Quantity(
            self.value + other.value,
            self.dimension,
            is_absolute_temperature=self.is_absolute_temperature or other.is_absolute_temperature,
        )

    def __sub__(self, other):
        other = self._other(other)
        if not self.is_absolute_temperature and other.is_absolute_temperature:
            raise UnitErrorML("an absolute temperature cannot be subtracted from a temperature change")
        # Absolute - absolute yields a temperature difference. Absolute - delta
        # stays absolute; delta - delta stays a delta.
        return Quantity(
            self.value - other.value,
            self.dimension,
            is_absolute_temperature=self.is_absolute_temperature and not other.is_absolute_temperature,
        )

    def __mul__(self, other):
        if isinstance(other, bool):
            raise TypeErrorML("boolean values cannot be used as quantities")
        if self.is_absolute_temperature or (isinstance(other, Quantity) and other.is_absolute_temperature):
            raise UnitErrorML("absolute temperatures cannot be multiplied; use a temperature difference in K")
        if isinstance(other, (int, float)):
            return Quantity(self.value * other, self.dimension)
        if isinstance(other, Quantity):
            return Quantity(self.value * other.value, self.dimension * other.dimension)
        return NotImplemented

    def __rmul__(self, other):
        return self.__mul__(other)

    def __truediv__(self, other):
        if isinstance(other, bool):
            raise TypeErrorML("boolean values cannot be used as quantities")
        if self.is_absolute_temperature or (isinstance(other, Quantity) and other.is_absolute_temperature):
            raise UnitErrorML("absolute temperatures cannot be divided; use a temperature difference in K")
        if isinstance(other, (int, float)):
            if other == 0:
                raise PhysicsErrorML("division by zero")
            return Quantity(self.value / other, self.dimension)
        if isinstance(other, Quantity):
            if other.value == 0:
                raise PhysicsErrorML("division by zero")
            return Quantity(self.value / other.value, self.dimension / other.dimension)
        return NotImplemented

    def __rtruediv__(self, other):
        if isinstance(other, bool):
            raise TypeErrorML("boolean values cannot be used as quantities")
        if self.is_absolute_temperature:
            raise UnitErrorML("absolute temperatures cannot be divided; use a temperature difference in K")
        if isinstance(other, (int, float)):
            if self.value == 0:
                raise PhysicsErrorML("division by zero")
            return Quantity(other / self.value, DIMENSIONLESS / self.dimension)
        return NotImplemented

    def __pow__(self, power):
        if self.is_absolute_temperature:
            raise UnitErrorML("absolute temperatures cannot be exponentiated; use a temperature difference in K")
        if isinstance(power, bool) or not isinstance(power, int):
            raise TypeErrorML("quantity exponent must be an integer")
        return Quantity(self.value ** power, self.dimension ** power)

    def __neg__(self):
        if self.is_absolute_temperature:
            if self.celsius_input_value is None:
                raise UnitErrorML("an absolute temperature cannot be negated; use a signed Celsius literal such as -10 C")
            return Quantity(
                273.15 - self.celsius_input_value,
                K,
                is_absolute_temperature=True,
                celsius_input_value=-self.celsius_input_value,
            )
        return Quantity(-self.value, self.dimension)

    def __pos__(self):
        return self

    def __lt__(self, other):
        return self.value < self._other(other).value

    def __le__(self, other):
        return self.value <= self._other(other).value

    def __gt__(self, other):
        return self.value > self._other(other).value

    def __ge__(self, other):
        return self.value >= self._other(other).value

    def __repr__(self):
        return f"{self.value:g} {self.dimension}"


# Default conversion rates requested for the prototype. Keep configurable later.
MANA_PER_KG = 0.1       # 1 mana manifests 10 kg of matter
JOULES_PER_MANA = 1.0   # 1 mana corresponds to 1 J in mana/energy conversions


def matter_to_mana(mass: Quantity) -> Quantity:
    if mass.dimension != KG:
        raise UnitErrorML("matter_to_mana() expects mass in kg")
    return Quantity(mass.value * MANA_PER_KG, MANA)


def mana_to_matter(mana: Quantity) -> Quantity:
    if mana.dimension != MANA:
        raise UnitErrorML("mana_to_matter() expects a mana quantity")
    return Quantity(mana.value / MANA_PER_KG, KG)


def mana_to_energy(mana: Quantity) -> Quantity:
    if mana.dimension != MANA:
        raise UnitErrorML("mana_to_energy() expects a mana quantity")
    return Quantity(mana.value * JOULES_PER_MANA, ENERGY)


def energy_to_mana(energy: Quantity) -> Quantity:
    if energy.dimension != ENERGY:
        raise UnitErrorML("energy_to_mana() expects energy in joules")
    return Quantity(energy.value / JOULES_PER_MANA, MANA)

