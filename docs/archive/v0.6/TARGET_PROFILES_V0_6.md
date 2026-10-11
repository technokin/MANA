# Target profiles with `tgset`

`tgset` defines a configurable target object. It is not a spell and does not execute magical operations.

```mana
guard = tgset:
    hp = 250
    max_hp = 250
    defence = 40
    resist_fire = 0.6
    resist_water = 0.1
    distance = 12 m

show(guard.hp)
show(guard.resist_fire)
```

The standard fields are `hp`, `max_hp`, `defence`, `resist_fire`, `resist_water`, `resist_earth`, `resist_air`, and `distance`. Resistance is a fraction: 0 means no resistance, 1 means full resistance. A target profile can also carry additional custom fields. It cannot store mana.
