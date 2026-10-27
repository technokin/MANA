# Ten-Minute MANA Tutorial

**Page kind:** Tutorial

This tutorial builds from a calculation to a spell. Run each step as a separate `.mana` file or replace the file contents with the next step. Expected output is shown directly after each runnable example.

## 1. Display a value

```mana
show("MANA is running")
```

Expected output:

```text
MANA is running
```

## 2. Calculate with a definition

```mana
def midpoint(a, b):
    incant (a + b) / 2

show(midpoint(2, 6))
```

Expected output:

```text
4.0
```

## 3. Create an object

```mana
stone = create Earth
show(stone.material)
```

Expected output:

```text
Earth
```

## 4. Define a spell

A spell definition describes behaviour; it does not execute until a spell mode is invoked.

```mana
spell spark():
    flame = create Fire
    heat(flame, 500 K)
    incant flame

release(spark)
show("spell released")
```

Expected output:

```text
spell released
```

`release(spark)` commits the spell's world-state changes. A `post(spark)` trial prints its detailed execution trace and rolls world changes back.

## 5. Check before running

Save the file as `tutorial.mana`, then run:

```powershell
python mana.py --check tutorial.mana
python mana.py tutorial.mana
```

The check command parses the file without executing it. See the [Cheat Sheet](../reference/MANA_CHEAT_SHEET.md), [Function Reference](../reference/FUNCTION_REFERENCE.md), and [Error Catalogue](../reference/ERROR_CATALOGUE.md) when you need exact syntax or diagnostics.
