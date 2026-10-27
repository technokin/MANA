"""Shared shape names accepted by MANA's shape operations and mana constructs."""

SUPPORTED_SHAPES = frozenset({
    "point", "line", "ray", "segment", "circle", "round", "arc", "ellipse",
    "ring", "polygon", "beam", "wave", "disc", "spiral", "fan", "wall",
    "field", "dome", "cage", "chain", "tendril", "cone", "corridor",
    "sphere", "ball", "projectile", "barrier", "shield",
})

# These labels default to a contact-capable construct in the current 2D engine.
DEFAULT_COLLIDABLE_MANA_SHAPES = frozenset({
    "sphere", "ball", "projectile", "barrier", "wall", "shield", "disc",
})
DEFAULT_ANCHORED_MANA_SHAPES = frozenset({"barrier", "wall", "shield", "disc"})
