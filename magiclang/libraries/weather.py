"""Parameter-driven world weather controls.

Weather is an environment system, not a spell catalogue. The namespace mutates
runtime climate parameters; the world engine applies the physical subset during
``advance_time`` and the optional observer records the same parameters for replay.
"""
from __future__ import annotations

import math
from typing import Any

from ..errors import MagicErrorML, PhysicsErrorML, TypeErrorML, UnitErrorML
from ..physics import Vector3, require_2d_world_vector
from ..units import DIMENSIONLESS, K, M, S, VELOCITY, Quantity


_PRESETS: dict[str, dict[str, Any]] = {
    "clear":     {"precipitation": "none", "intensity": 0.0, "wind_speed": 0.0, "temperature": 293.15, "humidity": 0.45, "clouds": 0.0, "fog": 0.0, "heat": 0.0, "lightning": 0.0},
    "rain":      {"precipitation": "rain", "intensity": 0.75, "wind_speed": 3.0, "temperature": 286.15, "humidity": 0.95, "clouds": 0.86, "fog": 0.12, "heat": -0.15, "lightning": 0.0},
    "snow":      {"precipitation": "snow", "intensity": 0.7, "wind_speed": 5.0, "temperature": 268.15, "humidity": 0.8, "clouds": 0.95, "fog": 0.22, "heat": -0.65, "lightning": 0.0},
    "storm":     {"precipitation": "rain", "intensity": 0.9, "wind_speed": 16.0, "temperature": 280.15, "humidity": 0.95, "clouds": 1.0, "fog": 0.16, "heat": -0.25, "lightning": 0.85},
    "blizzard":  {"precipitation": "snow", "intensity": 0.95, "wind_speed": 14.0, "temperature": 258.15, "humidity": 0.9, "clouds": 1.0, "fog": 0.35, "heat": -0.9, "lightning": 0.0},
    "heatwave":  {"precipitation": "none", "intensity": 0.8, "wind_speed": 2.0, "temperature": 315.15, "humidity": 0.2, "clouds": 0.08, "fog": 0.02, "heat": 0.95, "lightning": 0.0},
    "sandstorm": {"precipitation": "dust", "intensity": 0.85, "wind_speed": 18.0, "temperature": 305.15, "humidity": 0.15, "clouds": 0.72, "fog": 0.44, "heat": 0.25, "lightning": 0.0},
    "fog":       {"precipitation": "none", "intensity": 0.75, "wind_speed": 0.8, "temperature": 285.15, "humidity": 1.0, "clouds": 0.6, "fog": 1.0, "heat": -0.1, "lightning": 0.0},
    "wind":      {"precipitation": "none", "intensity": 0.8, "wind_speed": 14.0, "temperature": 293.15, "humidity": 0.4, "clouds": 0.25, "fog": 0.0, "heat": 0.0, "lightning": 0.0},
    "ashfall":   {"precipitation": "ash", "intensity": 0.7, "wind_speed": 8.0, "temperature": 303.15, "humidity": 0.15, "clouds": 0.65, "fog": 0.2, "heat": 0.35, "lightning": 0.0},
    "aurora":    {"precipitation": "none", "intensity": 0.7, "wind_speed": 1.0, "temperature": 270.15, "humidity": 0.4, "clouds": 0.3, "fog": 0.05, "heat": -0.5, "lightning": 0.0},
    # The custom profile starts from current world parameters and changes only the
    # fields explicitly supplied by the program. It is useful for composing weather.
    "custom":    {"precipitation": "none", "intensity": 0.0, "wind_speed": 0.0, "temperature": 293.15, "humidity": 0.45, "clouds": 0.0, "fog": 0.0, "heat": 0.0, "lightning": 0.0},
}
_DIRECTIONS = {
    "east": (1.0, 0.0), "west": (-1.0, 0.0), "north": (0.0, 1.0), "south": (0.0, -1.0),
    "northeast": (math.sqrt(.5), math.sqrt(.5)), "northwest": (-math.sqrt(.5), math.sqrt(.5)),
    "southeast": (math.sqrt(.5), -math.sqrt(.5)), "southwest": (-math.sqrt(.5), -math.sqrt(.5)),
}
_PRECIPITATION = {"none", "rain", "snow", "dust", "ash", "hail"}


def _finite(value: Any, label: str) -> float:
    if isinstance(value, Quantity):
        if value.dimension != DIMENSIONLESS:
            raise UnitErrorML(f"{label} must be dimensionless")
        value = value.value
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeErrorML(f"{label} must be a finite number")
    result = float(value)
    if not math.isfinite(result):
        raise PhysicsErrorML(f"{label} must be finite")
    return result


def _quantity(value: Any, dimension: str, label: str) -> float:
    if isinstance(value, Quantity):
        if value.dimension != dimension:
            raise UnitErrorML(f"{label} must use {dimension}, not {value.dimension}")
        result = float(value.value)
    elif isinstance(value, (int, float)) and not isinstance(value, bool):
        result = float(value)
    else:
        raise TypeErrorML(f"{label} must be a number with compatible units")
    if not math.isfinite(result):
        raise PhysicsErrorML(f"{label} must be finite")
    return result


def _direction(value: Any) -> tuple[float, float, str]:
    if isinstance(value, str):
        key = value.strip().casefold()
        if key not in _DIRECTIONS:
            raise MagicErrorML("wind_direction must be east, west, north, south, northeast, northwest, southeast, or southwest")
        x, y = _DIRECTIONS[key]
        return x, y, key
    if isinstance(value, Vector3):
        if value.dimension != DIMENSIONLESS or abs(value.z) > 1e-12:
            raise UnitErrorML("wind_direction vector must be a planar, dimensionless direction")
        magnitude = math.hypot(value.x, value.y)
        if magnitude <= 1e-12:
            raise PhysicsErrorML("wind_direction cannot be the zero vector")
        return value.x / magnitude, value.y / magnitude, "vector"
    raise TypeErrorML("wind_direction must be a compass direction or planar direction vector")


def build_library(runtime: Any) -> dict[str, Any]:
    """Return the standard, parameter-driven weather control namespace."""

    def current() -> dict[str, Any]:
        """Return the global climate parameters (local zones are listed by areas())."""
        return dict(runtime.environment_state)

    def areas() -> list[dict[str, Any]]:
        """Return active area-scoped weather zones without exposing mutable engine state."""
        now = float(getattr(runtime, "elapsed_virtual_time", 0.0))
        result = []
        for region in getattr(runtime, "weather_regions", []):
            until = region.get("until")
            if until is not None and float(until) <= now:
                continue
            result.append(dict(region))
        return result

    def _matching_area(radius: Any, center: Any = None) -> dict[str, Any] | None:
        if radius is None:
            return None
        radius_m = _quantity(radius, M, "weather area radius")
        center_value = getattr(runtime, "caster_position", Vector3(0.0, 0.0, 0.0, M)) if center is None else center
        if hasattr(center_value, "properties"):
            center_value = center_value.properties.get("pos")
        if not isinstance(center_value, Vector3) or center_value.dimension != M:
            raise UnitErrorML("weather area center must be a 2D position in metres or a positioned object")
        center_value = require_2d_world_vector(center_value, "weather area center")
        now = float(getattr(runtime, "elapsed_virtual_time", 0.0))
        for region in reversed(getattr(runtime, "weather_regions", [])):
            until = region.get("until")
            if until is not None and float(until) <= now:
                continue
            if (abs(float(region.get("radius_m", -1)) - radius_m) <= 1e-9
                    and abs(float(region.get("center_x_m", float("inf"))) - center_value.x) <= 1e-9
                    and abs(float(region.get("center_y_m", float("inf"))) - center_value.y) <= 1e-9):
                return dict(region)
        return None

    def clear() -> dict[str, Any]:
        """Clear weather and restore calm ambient defaults."""
        return configure("clear")

    def configure(
        kind: str = "rain", *, intensity: Any = None, precipitation: str | None = None,
        wind_speed: Any = None, wind_direction: Any = None, temperature: Any = None,
        humidity: Any = None, clouds: Any = None, fog: Any = None, heat: Any = None,
        lightning: Any = None, duration: Any = None, radius: Any = None, center: Any = None,
    ) -> dict[str, Any]:
        """Set atmosphere properties; any combination can be made without a spell per weather type."""
        if getattr(runtime, "_pure_call_depth", 0):
            raise MagicErrorML("weather.configure() changes world state; call it from a spell with post() or release()")
        if not isinstance(kind, str) or kind.strip().casefold() not in _PRESETS:
            raise MagicErrorML("weather kind must be one of: " + ", ".join(_PRESETS))
        name = kind.strip().casefold()
        if name == "custom":
            previous = dict(_matching_area(radius, center) or runtime.environment_state)
            preset = {
                "precipitation": previous.get("precipitation", "none"),
                "intensity": previous.get("intensity", 0.0),
                "wind_speed": previous.get("wind_speed_mps", 0.0),
                "temperature": previous.get("temperature_k", 293.15),
                "humidity": previous.get("humidity", 0.45),
                "clouds": previous.get("clouds", 0.0), "fog": previous.get("fog", 0.0),
                "heat": previous.get("heat", 0.0), "lightning": previous.get("lightning", 0.0),
            }
            previous_direction = previous.get("wind_direction_name", "east")
        else:
            preset = _PRESETS[name]
            previous_direction = runtime.environment_state.get("wind_direction_name", "east")
        direction_x, direction_y, direction_name = _direction(previous_direction if wind_direction is None else wind_direction)

        if intensity is None:
            raw_intensity = preset["intensity"]
            if name == "custom" and isinstance(precipitation, str) and precipitation.casefold() != "none" and raw_intensity <= 0:
                raw_intensity = 0.75
        else:
            raw_intensity = _finite(intensity, "weather intensity")
        if not 0 <= raw_intensity <= 1:
            raise PhysicsErrorML("weather intensity must be between 0 and 1")
        precip = preset["precipitation"] if precipitation is None else precipitation
        if not isinstance(precip, str) or precip.casefold() not in _PRECIPITATION:
            raise MagicErrorML("precipitation must be none, rain, snow, dust, ash, or hail")
        precip = precip.casefold()
        speed = float(preset["wind_speed"]) if wind_speed is None else _quantity(wind_speed, VELOCITY, "wind_speed")
        if speed < 0 or speed > 250:
            raise PhysicsErrorML("wind_speed must be between 0 and 250 m/s")
        temp = preset["temperature"] if temperature is None else _quantity(temperature, K, "temperature")
        if temp < 0 or temp > 10000:
            raise PhysicsErrorML("weather temperature must be between 0 K and 10000 K")
        humid = preset["humidity"] if humidity is None else _finite(humidity, "humidity")
        cloud = preset["clouds"] if clouds is None else _finite(clouds, "clouds")
        fog_value = preset["fog"] if fog is None else _finite(fog, "fog")
        heat_value = preset["heat"] if heat is None else _finite(heat, "heat")
        lightning_value = preset["lightning"] if lightning is None else _finite(lightning, "lightning")
        if not 0 <= humid <= 1 or not 0 <= cloud <= 1 or not 0 <= fog_value <= 1 or not 0 <= lightning_value <= 1:
            raise PhysicsErrorML("humidity, clouds, fog, and lightning must be between 0 and 1")
        if not -1 <= heat_value <= 1:
            raise PhysicsErrorML("heat must be between -1 and 1")

        seconds: float | None
        if duration is None:
            # Composable controls (wind, precipitation, clouds, etc.) retain an
            # existing countdown instead of silently turning a timed storm into
            # permanent weather. A fresh custom profile remains indefinite.
            previous_until = runtime.environment_state.get("until") if name == "custom" else None
            seconds = (max(0.001, float(previous_until) - float(runtime.elapsed_virtual_time))
                       if previous_until is not None and float(previous_until) > float(runtime.elapsed_virtual_time)
                       else None)
        else:
            seconds = _quantity(duration, S, "duration")
            if seconds <= 0 or seconds > 86400:
                raise PhysicsErrorML("weather duration must be greater than 0 and at most 86400 seconds")

        now = float(runtime.elapsed_virtual_time)
        state = {
            "kind": name, "intensity": raw_intensity, "precipitation": precip,
            "wind_speed_mps": speed, "wind_x_mps": direction_x * speed,
            "wind_y_mps": direction_y * speed, "wind_direction_name": direction_name,
            # The visualiser uses normalised wind intensity; the engine uses m/s above.
            "wind": min(1.0, speed / 20.0), "wind_direction": direction_x if abs(direction_x) >= abs(direction_y) else direction_y,
            "temperature_k": temp, "humidity": humid, "clouds": cloud, "fog": fog_value,
            "heat": heat_value, "lightning": lightning_value,
            "started_at": now, "until": None if seconds is None else now + seconds,
            "duration": seconds, "indefinite": seconds is None,
        }
        if radius is not None:
            radius_m = _quantity(radius, M, "weather area radius")
            if radius_m <= 0 or radius_m > 1_000_000:
                raise PhysicsErrorML("weather area radius must be greater than 0 and at most 1000000 m")
            center_value = getattr(runtime, "caster_position", Vector3(0.0, 0.0, 0.0, M)) if center is None else center
            if hasattr(center_value, "properties"):
                center_value = center_value.properties.get("pos")
            if not isinstance(center_value, Vector3) or center_value.dimension != M:
                raise UnitErrorML("weather area center must be a 2D position in metres or a positioned object")
            center_value = require_2d_world_vector(center_value, "weather area center")
            now = float(runtime.elapsed_virtual_time)
            existing = _matching_area(radius_m, center_value)
            regions = [region for region in getattr(runtime, "weather_regions", [])
                       if region.get("until") is None or float(region["until"]) > now]
            if existing is None and len(regions) >= 256:
                raise MagicErrorML("active local weather-zone limit (256) reached; wait for a zone to expire or clear an area")
            region_id = int(existing.get("region_id")) if existing is not None else int(getattr(runtime, "_next_weather_region_id", 1))
            if existing is None:
                runtime._next_weather_region_id = region_id + 1
            elif duration is None and name == "custom":
                # Parameter updates to an existing zone retain its prior expiry.
                state["until"] = existing.get("until")
                state["duration"] = existing.get("duration")
                state["indefinite"] = bool(existing.get("indefinite", state["until"] is None))
            state.update({
                "scope": "area", "region_id": region_id, "center_x_m": center_value.x,
                "center_y_m": center_value.y, "radius_m": radius_m,
                "center": [center_value.x, center_value.y],
            })
            if existing is not None:
                regions = [region for region in regions if int(region.get("region_id", -1)) != region_id]
            runtime.weather_regions = regions + [dict(state)]
            runtime._observe("weather.changed", scope="area", action="created", weather=dict(state))
            if runtime._spell_run_stack:
                runtime._record_step(
                    f"local weather configured: {name} (radius {radius_m:g} m, intensity {raw_intensity:g})"
                )
            return dict(state)

        runtime.environment_state = state
        # Weather controls are independent of spells. The observer only records
        # the parameters passed to the engine; it never decides the physics.
        runtime._observe("weather.changed", scope="world", weather=dict(state))
        if runtime._spell_run_stack:
            runtime._record_step(
                f"weather configured: {name} (intensity {raw_intensity:g}, {precip}, wind {speed:g} m/s)"
            )
        return dict(state)

    def patch_weather(*, duration: Any = None, radius: Any = None, center: Any = None, **updates: Any) -> dict[str, Any]:
        """Change selected weather parameters without resetting the others."""
        prior = _matching_area(radius, center) or current()
        values: dict[str, Any] = {
            "intensity": prior.get("intensity", 0.0),
            "precipitation": prior.get("precipitation", "none"),
            "wind_speed": Quantity(prior.get("wind_speed_mps", 0.0), VELOCITY),
            "wind_direction": prior.get("wind_direction_name", "east"),
            "temperature": Quantity(prior.get("temperature_k", 293.15), K),
            "humidity": prior.get("humidity", 0.45),
            "clouds": prior.get("clouds", 0.0),
            "fog": prior.get("fog", 0.0),
            "heat": prior.get("heat", 0.0),
            "lightning": prior.get("lightning", 0.0),
        }
        values.update(updates)
        local_duration = duration
        if local_duration is None and radius is not None and prior.get("until") is not None:
            remaining = float(prior["until"]) - float(runtime.elapsed_virtual_time)
            if remaining > 0:
                local_duration = Quantity(remaining, S)
        return configure("custom", **values, duration=local_duration, radius=radius, center=center)

    def wind(speed: Any, direction: Any = None, *, intensity: Any = None, duration: Any = None, radius: Any = None, center: Any = None) -> dict[str, Any]:
        """Set wind speed and direction while preserving other atmosphere controls."""
        updates: dict[str, Any] = {"wind_speed": speed}
        if direction is not None:
            updates["wind_direction"] = direction
        if intensity is not None:
            updates["intensity"] = intensity
        return patch_weather(duration=duration, radius=radius, center=center, **updates)

    def precipitation(kind: str = "rain", *, intensity: Any = None, duration: Any = None, radius: Any = None, center: Any = None) -> dict[str, Any]:
        """Set rain, snow, dust, ash or hail without defining a spell per weather type."""
        if not isinstance(kind, str) or kind.strip().casefold() not in _PRECIPITATION:
            raise MagicErrorML("precipitation kind must be rain, snow, dust, ash, hail, or none")
        precip = kind.strip().casefold()
        updates: dict[str, Any] = {"precipitation": precip}
        if intensity is not None:
            updates["intensity"] = intensity
        elif precip != "none":
            prior = _matching_area(radius, center) or current()
            updates["intensity"] = max(float(prior.get("intensity", 0.0)), 0.75)
        return patch_weather(duration=duration, radius=radius, center=center, **updates)

    def ambient_temperature(value: Any, *, duration: Any = None, radius: Any = None, center: Any = None) -> dict[str, Any]:
        """Change ambient temperature independently of precipitation or wind."""
        temp = _quantity(value, K, "temperature")
        if temp < 0 or temp > 10000:
            raise PhysicsErrorML("weather temperature must be between 0 K and 10000 K")
        heat_value = max(-1.0, min(1.0, (temp - 293.15) / 45.0))
        return patch_weather(duration=duration, radius=radius, center=center, temperature=value, heat=heat_value)

    def humidity(value: Any, *, duration: Any = None, radius: Any = None, center: Any = None) -> dict[str, Any]:
        """Set relative humidity from 0 to 1."""
        return patch_weather(duration=duration, radius=radius, center=center, humidity=value)

    def fog(density: Any = 0.8, *, duration: Any = None, radius: Any = None, center: Any = None) -> dict[str, Any]:
        """Set fog density without defining a dedicated fog spell."""
        return patch_weather(duration=duration, radius=radius, center=center, fog=density)

    def clouds(coverage: Any = 0.8, *, duration: Any = None, radius: Any = None, center: Any = None) -> dict[str, Any]:
        """Set cloud cover from 0 (clear) to 1 (overcast)."""
        return patch_weather(duration=duration, radius=radius, center=center, clouds=coverage)

    def heat(value: Any, *, duration: Any = None, radius: Any = None, center: Any = None) -> dict[str, Any]:
        """Set a normalised world heat factor from -1 (cold) to 1 (hot)."""
        normalized = _finite(value, "heat")
        if not -1 <= normalized <= 1:
            raise PhysicsErrorML("heat must be between -1 and 1")
        temperature = 293.15 + normalized * 45.0
        return patch_weather(duration=duration, radius=radius, center=center, heat=normalized, temperature=Quantity(temperature, K))

    def lightning(intensity: Any = 0.5, *, duration: Any = None, radius: Any = None, center: Any = None) -> dict[str, Any]:
        """Set atmospheric lightning intensity from 0 to 1."""
        return patch_weather(duration=duration, radius=radius, center=center, lightning=intensity)

    return {
        "set": configure,
        "configure": configure,
        "clear": clear,
        "current": current,
        "areas": areas,
        "wind": wind,
        "precipitation": precipitation,
        "temperature": ambient_temperature,
        "humidity": humidity,
        "fog": fog,
        "clouds": clouds,
        "heat": heat,
        "lightning": lightning,
    }
