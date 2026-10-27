# MANA 2.0.0 — Release Summary

**Version:** 2.0.0  
**Prepared:** 23 October 2026

This is the plain-English summary of the MANA 2.0.0 release package. It describes what was improved, what the program can do, and what is deliberately outside its scope.

## Release and installation improvements

- Updated the main project and both Visual Studio Code add-ons to version **2.0.0** so the displayed version, instructions, and download names agree.
- Fixed the version checker so it checks both add-ons, not just the main language support.
- Preserved the older 1.0.0 release on GitHub, while removing its outdated installers from the new package so people do not accidentally install the wrong version.
- Made the new download archive cleaner: it contains the current installers, the documentation, and the plain-English change log, without temporary files and caches.
- Added automatic release steps. When the matching version tag is pushed, GitHub will check the version, run tests, build the downloads, and attach them to the release page.
- Added a separate release report and updated the project guide so current features and known limitations are easier to tell apart.

## Language and editor improvements

- Kept MANA programs as their own kind of source file. The interpreter is still built with Python, but people write MANA spells in MANA itself.
- Kept the editor add-ons optional. MANA can still run without either add-on, and ordinary Run remains separate from opening the visual viewer.
- Kept the expanded editor suggestions, help, shortcuts, examples, spell guide, and library references together with the current release.
- Fixed a test that referred to an old download name so it now follows the release version automatically.

## Visual viewer and world simulation

- Kept the visual viewer focused on magical 2D scenes made from recorded runs. It remains optional and does not need to be installed to run MANA.
- Retained the larger scene view, adjustable camera, zoom and movement controls, object selection, character inspection, visual layers, and reduced-motion setting.
- Kept the pictures tied to what the program actually recorded. Viewing a scene does not invent collisions or alter the real simulation.
- Kept the world simulation two-dimensional. Three-dimensional calculations remain available for planning and mathematics, but they do not imply three-dimensional movement or collisions.
- Kept the distinction between trying a spell and committing its effects to the world.

## Improvements included in this project snapshot

- Expanded and aligned the geometry helpers, material catalogue, creature anatomy records, and library naming rules.
- Kept the broad set of magic systems connected through shared rules rather than making each creature or spell depend on a separate special case.
- Retained safer handling for malformed inputs and recordings, limits for unusually large scenes, rollback when a trial spell fails, and tests for physics and world-state consistency.
- Kept examples and reference pages close to the behaviour that is actually implemented. A name in a catalogue is not presented as a promise that the entire effect is simulated.

## Visualiser focus upgrade

- Fixed the main direction-change problem: projectile tracks now preserve and follow recorded intermediate world positions, including bends from spells that change velocity mid-flight. The path is sampled using world timestamps when available instead of assuming every log entry represents the same amount of time.
- Improved long recordings without letting one projectile consume unlimited memory. Recent path points remain detailed, and sharp bends are kept when older path history is reduced.
- Animated moving humanoids and knights with a walking gait; characters face their recorded travel direction. Existing dragon, bird, serpent, dinosaur, ant, minotaur and slime designs keep their individual movement cues. Characters briefly recoil only when a real collision is recorded.
- Replaced the generic-glow feel with distinct 2D effects: flame tongues, water ribbons/droplets, ice shards, branched lightning, earth/metal fragments, flowing air, plant-like life effects, dark tendrils and geometric mana seals.
- Added clearer presentations for beams, radial bursts and impact rings, summoning/reanimation, shaped mana constructs, transformations, body-state changes, metal manipulation, magnetic fields, smoke and flares. Effect positions, times and contacts are taken from recorded events; the viewer never decides whether a spell succeeded.
- Made effect animation follow the recorded world clock during playback and continue gentle idle movement when playback is paused. Reduced-motion preference remains respected.
- Added `examples/visualiser_steering_firebolt.mana`, a runnable example whose projectile changes direction repeatedly while moving, plus regression tests for curved motion, timestamp-aware interpolation, long paths, character contact reactions and concrete spell-effect drawing.
- Updated the Visualiser guide and extension README to explain how to try the new motion example and what is—and is not—simulated.

## What this release does not add

- No full three-dimensional world or three-dimensional collision engine.
- No live editor that changes the real world by dragging objects in the viewer.
- No public plug-in for a separate game engine; the viewer's recordings are for the viewer itself.
- No complete fluid, chemistry, biological, or autonomous-creature simulation.

## Verification

The final project test suite passed **480 tests**. All **62** example programs passed CLI syntax checks and the project's smoke checks, including the new steering-firebolt example. The focused Visualiser suite passed **36 tests**. The large-object benchmark successfully created **9,999 objects in 0.187 seconds** on the build machine; results vary by computer. Both editor add-ons were rebuilt and verified; the generated documentation, version checks, local documentation file links and Markdown heading anchors, Python compilation, and JavaScript syntax checks passed. The headless webview harness exercised the actual viewer script against generated recordings. A pixel screenshot could not be inspected in this environment because the browser sandbox blocks local and loopback preview pages. The source archive was built and its contents and integrity were inspected. The root `CHANGELOG.md` is the cumulative release history; this file is the shorter plain-English summary for the 2.0.0 release.

The local environment could not run the optional static-analysis and dependency-audit tools because they were not installed and the package index was unreachable. The release workflow installs those tools and checks Linux and Windows on Python 3.12–3.15; its publish job waits for all eight verification jobs to succeed.

## Public release status

The source package and both editor add-ons are prepared as version 2.0.0. The already published 1.0.0 GitHub release remains unchanged. This working session did not publish a new GitHub release; the public 2.0.0 release is created by pushing the matching tag and allowing the release workflow to finish successfully.


## Current source snapshot addendum (2.0.0)

The current working source snapshot remains version **2.0.0**. Since the original release-log baseline, the 2D Visualiser gained a spell-first body layer, the Visual Lab gained expanded palettes and independent colour channels, and the renderer moved to one adaptive graphics policy with bounded canvas/cache use. The current set contains 67 executable examples, including five additional integration programs for preview/commit boundaries, plane-path lifecycle, energy accounting, selective targets, and runtime-reported impacts. The current test and audit result is recorded in `docs/current/RELEASE_V2_0_0_REPORT.md`; this addendum does not claim a public release has been published.
