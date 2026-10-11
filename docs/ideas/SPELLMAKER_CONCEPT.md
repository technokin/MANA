# Spell Maker — planned feature

The Spell Maker is independent of any world renderer. It takes a named Mana `def`, validates it and creates an invocation phrase such as `arin mikal nhuj ine`.

The first mode binds the unique phrase to a compiled/validated spell identifier and version. Saying or entering the phrase resolves that mapping and executes the same spell. Later, syllables can have documented compositional meanings for operation families, targets, modifiers and timing. The same tool can support both compact aliases and longer encoded chants.

Build it after the language grammar/runtime is stable. It can be built before a world engine because it maps source code to an invocation; it does not need visualization.
