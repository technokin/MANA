"""Reusable item blueprints and equipment integration for MANA.

This library uses ordinary conjured material objects; equipment is not a second
object-creation path. It adds item metadata, simple armour mitigation, and reusable
projectile payloads to the same physical entities handled by the world engine.
"""
from __future__ import annotations

import copy
import math
from typing import Any

from ..errors import MagicErrorML, PhysicsErrorML, TypeErrorML, UnitErrorML
from ..equipment import all_blueprints, blueprint, canonical_item
from ..materials import physical_material_profile
from ..physics import Vector3
from ..units import ENERGY, FORCE, KG, M, VELOCITY, Quantity


def _object(value: Any, label: str):
    from ..runtime import MagicObject
    if not isinstance(value, MagicObject):
        raise TypeErrorML(f"armory.{label}() expects a MANA world object")
    return value


def _being(value: Any, label: str):
    obj = _object(value, label)
    props = obj.properties
    if not (props.get("living") or props.get("is_being") or props.get("is_summoned") or props.get("targetable")):
        raise MagicErrorML(f"armory.{label}() expects a living being or target profile")
    if not props.get("active", True):
        raise MagicErrorML(f"armory.{label}() cannot use an inactive target")
    return obj


def build_library(runtime: Any) -> dict[str, Any]:
    def blueprints() -> list[dict[str, Any]]:
        defaults = all_blueprints()
        custom = [copy.deepcopy(value) for value in runtime.custom_item_blueprints.values()]
        return sorted(defaults + custom, key=lambda value: str(value.get("name", "")).casefold())

    def inspect(item: Any) -> dict[str, Any]:
        if isinstance(item, str):
            key = " ".join(item.casefold().replace("_", " ").replace("-", " ").split())
            data = copy.deepcopy(runtime.custom_item_blueprints.get(key))
            if data is None:
                data = blueprint(item)
            if data is None:
                raise MagicErrorML(f"unknown item blueprint '{item}'; use armory.blueprints()")
            return {"name": data.get("name"), "material": data.get("material"),
                    "slot": data.get("slot"), "shape": data.get("shape"),
                    "mass_kg": data.get("mass_kg"), "length_m": data.get("length_m"),
                    "width_m": data.get("width_m"), "thickness_m": data.get("thickness_m"),
                    "damage_multiplier": data.get("damage_multiplier", 1.0),
                    "armour_rating": data.get("armour_rating", 0.0),
                    "durability": data.get("durability"), "payload": data.get("payload", "none"),
                    "launch_speed_m_s": data.get("launch_speed_m_s"),
                    "custom": bool(data.get("custom", False)), "description": data.get("description", "")}
        obj = _object(item, "inspect")
        props = obj.properties
        return {
            "object_id": obj.object_id, "name": props.get("display_name", obj.element),
            "material": props.get("material"), "item_kind": props.get("item_kind"),
            "slot": props.get("equipment_slot"), "shape": props.get("shape"),
            "mass_kg": getattr(props.get("mass"), "value", None),
            "length_m": props.get("length_m"), "width_m": props.get("width_m"),
            "thickness_m": props.get("thickness_m"), "damage_multiplier": props.get("damage_multiplier", 1.0),
            "armour_rating": props.get("armour_rating", 0.0),
            "durability": props.get("durability"), "max_durability": props.get("max_durability"),
            "payload": props.get("payload", "none"), "launch_speed_m_s": props.get("launch_speed_m_s"),
            "magnetic_response": props.get("magnetic_response", 0.0), "equipped_to": props.get("equipped_to"),
        }

    def define(name: Any, *, slot: Any, material: Any, mass: Any = None, shape: Any = "polygon",
               length: Any = None, width: Any = None, thickness: Any = None,
               damage_multiplier: Any = 1.0, armour_rating: Any = 0.0, durability: Any = 100.0,
               payload: Any = "none", attack_style: Any = "custom", launch_speed: Any = None,
               description: Any = "User-defined equipment blueprint") -> dict[str, Any]:
        """Register a reusable user blueprint. It creates nothing until conjure() is called."""
        if getattr(runtime, "_pure_call_depth", 0):
            raise MagicErrorML("armory.define() changes the world catalogue; call it in an executable spell")
        if not isinstance(name, str) or not name.strip():
            raise TypeErrorML("armory.define() name must be non-empty text")
        display = " ".join(name.strip().replace("_", " ").split())
        key = " ".join(display.casefold().replace("-", " ").split())
        if len(display) > 64 or not display[0].isalpha() or not all(ch.isalnum() or ch in " -" for ch in display):
            raise MagicErrorML("armory.define() name must be 1–64 letters, digits, spaces, or hyphens and start with a letter")
        if canonical_item(display) is not None or key in runtime.custom_item_blueprints:
            raise MagicErrorML(f"item blueprint '{display}' is already registered")
        if not isinstance(slot, str) or slot.strip().casefold() not in {"weapon", "shield", "body_armour", "head", "hands", "legs", "projectile", "tool", "resource"}:
            raise MagicErrorML("armory.define() slot must be weapon, shield, body_armour, head, hands, legs, projectile, tool, or resource")
        if not isinstance(material, str) or not material.strip():
            raise TypeErrorML("armory.define() material must be non-empty text")
        material_key = " ".join(material.casefold().replace("_", " ").replace("-", " ").split())
        material_profile = runtime.custom_material_profiles.get(material_key) or physical_material_profile(material)
        if material_profile is None:
            raise MagicErrorML(f"unknown material '{material}'; inspect materials.all() or define it with materials.define() first")
        if mass is None:
            mass = Quantity(1.0, KG)
        if not isinstance(mass, Quantity) or mass.dimension != KG or not math.isfinite(float(mass.value)) or not 0.001 <= float(mass.value) <= 100_000:
            raise PhysicsErrorML("armory.define() mass must be between 0.001 and 100000 kg")
        if not isinstance(shape, str):
            raise TypeErrorML("armory.define() shape must be text")
        from ..shapes import SUPPORTED_SHAPES
        shape_key = shape.casefold()
        if shape_key not in SUPPORTED_SHAPES:
            raise MagicErrorML("armory.define() shape must be a supported MANA shape")
        def dimension(value: Any, fallback: float, label: str) -> float:
            if value is None:
                return fallback
            if not isinstance(value, Quantity) or value.dimension != M:
                raise UnitErrorML(f"armory.define() {label} must use metres")
            number = float(value.value)
            if not math.isfinite(number) or not 0.001 <= number <= 1000:
                raise PhysicsErrorML(f"armory.define() {label} must be between 0.001 and 1000 metres")
            return number
        length_m = dimension(length, 0.75, "length")
        width_m = dimension(width, 0.08, "width")
        thickness_m = dimension(thickness, 0.01, "thickness")
        def coefficient(value: Any, label: str, lower: float, upper: float) -> float:
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise TypeErrorML(f"armory.define() {label} must be a number")
            number = float(value)
            if not math.isfinite(number) or not lower <= number <= upper:
                raise PhysicsErrorML(f"armory.define() {label} must be between {lower:g} and {upper:g}")
            return number
        damage = coefficient(damage_multiplier, "damage_multiplier", 0.1, 10.0)
        armour = coefficient(armour_rating, "armour_rating", 0.0, 500.0)
        durability_value = coefficient(durability, "durability", 0.1, 1e9)
        if not isinstance(payload, str):
            raise TypeErrorML("armory.define() payload must be text")
        payload_key = payload.strip().casefold().replace("_", " ")
        if payload_key not in {"none", "binding", "net", "shock", "smoke", "flare", "anchor", "burst", "acid"}:
            raise MagicErrorML("armory.define() payload is unsupported")
        slot_key = slot.strip().casefold()
        if slot_key != "projectile" and payload_key != "none":
            raise MagicErrorML("only projectile blueprints may have a payload")
        if not isinstance(attack_style, str) or not attack_style.strip() or len(attack_style) > 40:
            raise TypeErrorML("armory.define() attack_style must be non-empty text no longer than 40 characters")
        if not isinstance(description, str) or len(description) > 280:
            raise TypeErrorML("armory.define() description must be text no longer than 280 characters")
        style_key = attack_style.strip().casefold()
        launch_speed_value = None
        if launch_speed is not None:
            if not isinstance(launch_speed, Quantity) or launch_speed.dimension != VELOCITY:
                raise UnitErrorML("armory.define() launch_speed must use m/s")
            launch_speed_value = float(launch_speed.value)
            if not math.isfinite(launch_speed_value) or not 0 < launch_speed_value <= 2000:
                raise PhysicsErrorML("armory.define() launch_speed must be greater than 0 and no more than 2000 m/s")
        if style_key == "ranged" and launch_speed_value is None:
            launch_speed_value = 50.0
        if style_key != "ranged" and launch_speed_value is not None:
            raise MagicErrorML('launch_speed is only supported by equipment with attack_style="ranged"')
        data = {"name": key, "slot": slot_key, "material": material_profile.get("name", material_key),
                "mass_kg": float(mass.value), "shape": shape_key, "length_m": length_m,
                "width_m": width_m, "thickness_m": thickness_m, "damage_multiplier": damage,
                "armour_rating": armour, "durability": durability_value, "payload": payload_key,
                "attack_style": style_key, "launch_speed_m_s": launch_speed_value,
                "description": description, "custom": True}
        runtime.custom_item_blueprints[key] = copy.deepcopy(data)
        runtime._observe("world.changed", operation="item_blueprint_defined", blueprint={k: v for k, v in data.items() if k != "description"})
        return copy.deepcopy(data)

    def equip(wearer: Any, item: Any):
        wearer_obj = _being(wearer, "equip")
        item_obj = _object(item, "equip")
        wp, ip = wearer_obj.properties, item_obj.properties
        if not ip.get("created_by_conjure") or not ip.get("item_kind"):
            raise MagicErrorML("armory.equip() requires an item made from a conjure equipment blueprint")
        if ip.get("equipment_slot") == "projectile":
            raise MagicErrorML("projectiles are ammunition; launch them instead of equipping them as worn gear")
        if not ip.get("active", True):
            raise MagicErrorML("armory.equip() cannot equip an inactive item")
        existing_owner = ip.get("equipped_to")
        if existing_owner is not None and existing_owner != wearer_obj.object_id:
            raise MagicErrorML("this item is already equipped by another entity; unequip it first")
        equipment = wp.setdefault("equipment", [])
        if any(current is item_obj for current in equipment):
            return item_obj
        slot = str(ip.get("equipment_slot", "item"))
        for current in equipment:
            if current.properties.get("equipment_slot") == slot:
                raise MagicErrorML(f"{slot} slot is already occupied; unequip its current item first")
        position = wp.get("pos")
        if isinstance(position, Vector3) and position.dimension == M:
            ip["pos"] = position
        ip["vel"] = Vector3(0, 0, 0, VELOCITY)
        ip["anchored"] = True
        ip["collidable"] = False
        ip["equipped_to"] = wearer_obj.object_id
        ip["active"] = True
        equipment.append(item_obj)
        runtime._observe("equipment.changed", operation="equip", wearer=runtime._visual_entity(wearer_obj), item=runtime._visual_entity(item_obj), slot=slot)
        return item_obj

    def unequip(wearer: Any, item: Any):
        wearer_obj = _being(wearer, "unequip")
        item_obj = _object(item, "unequip")
        equipment = wearer_obj.properties.get("equipment", [])
        if not any(current is item_obj for current in equipment):
            raise MagicErrorML("this item is not equipped by that wearer")
        wearer_obj.properties["equipment"] = [current for current in equipment if current is not item_obj]
        ip = item_obj.properties
        ip["equipped_to"] = None
        ip["anchored"] = False
        ip["collidable"] = True
        position = wearer_obj.properties.get("pos")
        if isinstance(position, Vector3) and position.dimension == M:
            ip["pos"] = position
        runtime._observe("equipment.changed", operation="unequip", wearer=runtime._visual_entity(wearer_obj), item=runtime._visual_entity(item_obj))
        return item_obj

    def imbue(item: Any, payload: Any):
        obj = _object(item, "imbue")
        if obj.properties.get("equipment_slot") != "projectile":
            raise MagicErrorML("armory.imbue() currently supports conjured projectile blueprints only")
        if not isinstance(payload, str):
            raise TypeErrorML("armory.imbue() payload must be text")
        allowed = {"none", "binding", "net", "shock", "smoke", "flare", "anchor", "burst", "acid"}
        key = payload.strip().casefold().replace("_", " ")
        if key not in allowed:
            raise MagicErrorML("unsupported projectile payload; choose none, binding, net, shock, smoke, flare, anchor, burst, or acid")
        obj.properties["payload"] = key
        runtime._observe("entity.changed", entity=runtime._visual_entity(obj), operation="imbue", payload=key)
        return obj

    def has_slot(wearer: Any, slot: Any) -> bool:
        obj = _being(wearer, "has_slot")
        if not isinstance(slot, str):
            raise TypeErrorML("armory.has_slot() slot must be text")
        return any(item.properties.get("equipment_slot") == slot.strip().casefold()
                   for item in obj.properties.get("equipment", []) if getattr(item, "properties", {}).get("durability", 1) > 0)

    def launch(wielder: Any, projectile: Any, target: Any, *, launcher: Any = None, speed: Any = None):
        """Launch a conjured projectile through world physics toward a target.

        The launcher must be an equipped ranged blueprint. The projectile remains
        a normal physical object and stops on actual physics contact.
        """
        actor = _being(wielder, "launch")
        shot = _object(projectile, "launch")
        victim = _being(target, "launch")
        if shot.properties.get("equipment_slot") != "projectile" or shot.properties.get("item_kind") != "projectile":
            raise MagicErrorML("armory.launch() requires a projectile created from a conjure blueprint")
        if shot.properties.get("equipped_to") is not None or shot.properties.get("launched_at") is not None:
            raise MagicErrorML("armory.launch() requires unused, unequipped ammunition")
        if launcher is None:
            launcher = next((gear for gear in actor.properties.get("equipment", [])
                             if gear.properties.get("attack_style") == "ranged" and gear.properties.get("active", True)), None)
        launch_item = _object(launcher, "launch")
        lp = launch_item.properties
        if lp.get("equipped_to") != actor.object_id or lp.get("attack_style") != "ranged":
            raise MagicErrorML("armory.launch() requires a ranged launcher equipped by the wielder")
        apos, tpos = actor.properties.get("pos"), victim.properties.get("pos")
        if not isinstance(apos, Vector3) or not isinstance(tpos, Vector3):
            raise MagicErrorML("armory.launch() requires positioned wielder and target")
        dx, dy = tpos.x - apos.x, tpos.y - apos.y
        distance = math.hypot(dx, dy)
        if distance <= 0.1:
            raise PhysicsErrorML("armory.launch() needs a positive target separation greater than 0.1 m")
        if speed is None:
            speed_value = float(lp.get("launch_speed_m_s") or 50.0)
        elif isinstance(speed, Quantity) and speed.dimension == VELOCITY:
            speed_value = float(speed.value)
        else:
            raise UnitErrorML("armory.launch() speed must use m/s")
        if not math.isfinite(speed_value) or not 0 < speed_value <= 2000:
            raise PhysicsErrorML("armory.launch() speed must be greater than 0 and no more than 2000 m/s")
        ux, uy = dx / distance, dy / distance
        radius = float(getattr(shot.properties.get("collision_radius"), "value", 0.05))
        if not math.isfinite(radius) or radius < 0:
            raise PhysicsErrorML("armory.launch() projectile collision radius is invalid")
        # Place the projectile near the wielder, but never beyond the target or
        # inside the wielder's own collision origin when firing at short range.
        muzzle_offset = min(0.8 + radius, max(0.02, distance * 0.45))
        original = copy.deepcopy(shot.properties)
        try:
            shot.properties["pos"] = Vector3(apos.x + ux * muzzle_offset, apos.y + uy * muzzle_offset, 0.0, M)
            shot.properties["anchored"] = False
            shot.properties["collidable"] = True
            shot.properties["owner_id"] = actor.object_id
            shot.properties["launched_by"] = runtime._object_label(actor)
            shot.properties["launched_at"] = runtime.elapsed_virtual_time
            shot.properties["launch_target_id"] = victim.object_id
            shot.properties["strength_multiplier"] = float(actor.properties.get("strength_multiplier", 1.0))
            vector = Vector3(ux * speed_value, uy * speed_value, 0.0, VELOCITY)
            runtime.op_velocity(shot, vector)
        except Exception:
            shot.properties.clear()
            shot.properties.update(original)
            raise
        runtime._observe("combat.projectile_launched", attacker=runtime._visual_entity(actor), target=runtime._visual_entity(victim),
                         projectile=runtime._visual_entity(shot), launcher=runtime._visual_entity(launch_item), speed_m_s=speed_value)
        runtime._record_step(f"{runtime._object_label(actor)} launched {runtime._object_label(shot)} toward {runtime._object_label(victim)}")
        return shot

    def strike(wielder: Any, target: Any, weapon: Any, *, force: Any = None):
        """Resolve a bounded melee strike; projectiles continue to use physics contacts."""
        actor = _being(wielder, "strike")
        victim = _being(target, "strike")
        item = _object(weapon, "strike")
        props = item.properties
        if props.get("equipment_slot") not in {"weapon", "shield"}:
            raise MagicErrorML("armory.strike() requires a conjured melee weapon blueprint")
        if props.get("equipped_to") != actor.object_id:
            raise MagicErrorML("armory.strike() requires the weapon to be equipped by the wielder")
        if force is None:
            attack_force = 900.0
        elif isinstance(force, Quantity) and force.dimension == FORCE:
            attack_force = float(force.value)
        elif isinstance(force, (int, float)) and not isinstance(force, bool):
            # Bare numbers are interpreted as newtons for concise game scripts.
            attack_force = float(force)
        else:
            raise TypeErrorML("armory.strike() force must be a force in newtons (e.g. force=900 N)")
        if not math.isfinite(attack_force) or not 0 < attack_force <= 100_000:
            raise PhysicsErrorML("armory.strike() force must be greater than 0 and no more than 100000 N")
        apos, tpos = actor.properties.get("pos"), victim.properties.get("pos")
        if not isinstance(apos, Vector3) or not isinstance(tpos, Vector3):
            raise MagicErrorML("armory.strike() requires positioned entities")
        reach = float(props.get("length_m", 1.0)) + 0.5
        distance = math.hypot(apos.x - tpos.x, apos.y - tpos.y)
        if distance > reach:
            raise MagicErrorML(f"target is out of weapon reach ({distance:.2f} m > {reach:.2f} m)")
        hit_points = victim.properties.get("hp")
        if hit_points is None or victim.properties.get("targetable") is False:
            raise MagicErrorML("armory.strike() target needs an active hit-point profile")
        mass = getattr(props.get("mass"), "value", 1.0)
        impact_energy = 0.5 * max(0.01, float(mass)) * (attack_force / max(1.0, float(mass) * 12.0)) ** 2
        base_damage = (impact_energy / 100.0) * float(props.get("damage_multiplier", 1.0))
        strength = float(actor.properties.get("strength_multiplier", 1.0))
        region = str(victim.properties.get("last_hit_region", "torso")).casefold()
        slot_weights = {"torso": {"body_armour": 1.0, "shield": 0.45},
                        "head": {"head": 1.0, "body_armour": 0.25, "shield": 0.25},
                        "hands": {"hands": 1.0, "body_armour": 0.1},
                        "legs": {"legs": 1.0, "body_armour": 0.2}}
        weights = slot_weights.get(region, slot_weights["torso"])
        protective = []
        for gear in victim.properties.get("equipment", []):
            gp = gear.properties
            slot = gp.get("equipment_slot")
            current_durability = float(gp.get("durability", 0.0))
            max_durability = float(gp.get("max_durability", current_durability))
            if slot in weights and current_durability > 0:
                condition = min(1.0, current_durability / max_durability) if max_durability > 0 else 1.0
                effective = max(0.0, float(gp.get("armour_rating", 0.0))) * weights[slot] * condition
                if effective > 0:
                    protective.append((gear, effective))
        armour = sum(value for _, value in protective)
        defence = max(0.0, float(victim.properties.get("defence", 0.0))) + armour
        resistance = max(0.0, min(1.0, float(victim.properties.get("resist_physical", 0.0))))
        body_reduction = min(0.9, max(0.0, float(victim.properties.get("body_damage_reduction", 0.0))))
        body_taken = max(0.2, min(5.0, float(victim.properties.get("body_damage_taken_multiplier", 1.0))))
        penetration = 0.65 if props.get("attack_style") in {"pierce", "thrust", "thrown_pierce"} else 1.0
        damage = max(0.0, base_damage * strength * (1.0 - resistance) * (1.0 - body_reduction) * body_taken - defence - armour * penetration)
        if damage <= 0:
            if protective:
                gear, _ = max(protective, key=lambda pair: pair[1])
                gear.properties["durability"] = max(0.0, float(gear.properties.get("durability", 0.0)) - max(0.1, impact_energy / 100_000.0))
            return {"hit": True, "damage": 0.0, "reason": "defended", "target_hp": float(hit_points), "armour_rating": armour}
        old_hp = float(hit_points)
        if old_hp - damage <= 0 and not victim.properties.get("body_model_initialized"):
            from .physiology import _initialize as initialize_body
            initialize_body(victim)
        victim.properties["hp"] = max(0.0, old_hp - damage)
        victim.properties["last_damage"] = min(old_hp, damage)
        if victim.properties["hp"] <= 0 and victim.properties.get("body_model_initialized"):
            from .physiology import _die as mark_body_dead
            mark_body_dead(runtime, victim, "weapon_strike")
        victim.properties["last_impact_energy"] = impact_energy
        if protective:
            gear, _ = max(protective, key=lambda pair: pair[1])
            gear.properties["durability"] = max(0.0, float(gear.properties.get("durability", 0.0)) - max(0.1, impact_energy / 100_000.0))
        durability = float(props.get("durability", 0.0))
        if durability > 0:
            toughness = max(0.1, min(1.0, float(props.get("toughness_index", 0.4))))
            wear_amount = max(0.05, impact_energy / 250_000.0) / toughness
            props["durability"] = max(0.0, durability - wear_amount)
            if props["durability"] <= 0:
                runtime._observe("equipment.changed", operation="broken", item=runtime._visual_entity(item), wearer=runtime._visual_entity(actor))
        runtime._observe("combat.strike", attacker=runtime._visual_entity(actor), target=runtime._visual_entity(victim), weapon=runtime._visual_entity(item), damage=min(old_hp, damage), impact_energy_j=impact_energy)
        runtime.emit_event("damaged", victim, actor, Quantity(impact_energy, ENERGY), min(old_hp, damage))
        return {"hit": True, "damage": min(old_hp, damage), "target_hp": victim.properties["hp"], "impact_energy_j": impact_energy}

    def make(wielder: Any, target: Any, weapon: Any, *, force: Any = None):
        """Compatibility alias for the clearer armory.strike() operation."""
        return strike(wielder, target, weapon, force=force)

    # These helpers change either the world registry or world objects. Tag them
    # so ordinary pure def helpers cannot mutate the simulation behind the
    # appraisal/commit boundary. `make` is retained as a backwards-compatible alias.
    for operation in (define, equip, unequip, imbue, launch, strike, make):
        operation.__mana_runtime_operation__ = True

    return {
        "blueprints": blueprints,
        "inspect": inspect,
        "define": define,
        "equip": equip,
        "unequip": unequip,
        "imbue": imbue,
        "has_slot": has_slot,
        "launch": launch,
        "strike": strike,
        "make": make,
    }
