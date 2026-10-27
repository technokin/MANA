> **Historical pre-release snapshot:** This document records the working copy before MANA 2.0.0. Its version numbers and test counts describe that earlier snapshot. Use the [current MANA 2.0.0 verification report](../../../current/RELEASE_V2_0_0_REPORT.md) for the present checks.

**Page kind:** Change log  
**Audience:** Project users  

# MANA v2 — Change log in plain English

**Starting point:** the `MANA_v2.zip` file supplied for this review. It still identifies the project as version **1.0.0**. The archive name does not mean a formal 2.0.0 release has been published.

## What was improved

### The scene viewer

- The scene opens in a much larger editor area by default, so it feels closer to a dedicated window.
- The expand and restore button now calls the correct Visual Studio Code command. Closing the scene returns to the normal editor layout.
- The large-view option can be switched off in settings.
- The camera can zoom out far enough to show much larger worlds. The background grid follows the camera instead of making distant scenes feel stuck close up.
- The file chooser no longer offers ordinary files that the viewer cannot open; it lists only the recording type the viewer supports.
- The viewer is more tolerant of damaged or unexpected recording details. In particular, unusual collision, weather, creature, and world-snapshot information no longer triggers several playback crashes.

### Help while writing MANA

- The editor now suggests two missing reference values from the 3D calculation library and correctly labels them as values rather than actions.
- Existing 2D and 3D calculation tools are still clearly distinguished from a complete 3D world. This update does not claim that full 3D movement or collisions exist.

### Safety and reliability

- Added repeatable tests that try large numbers of deliberately malformed MANA statements and check that errors are handled cleanly.
- Added a test recording with incorrect field types, missing details, and empty weather information to make sure the viewer does not crash.
- Replayed a separate test recording with **500 deliberately malformed scene events**; the viewer completed the test without an unexpected crash.
- Kept existing protections for oversized source files, long-running programs, excessive output, and large or deeply nested recordings.
- Reviewed the boundary clearly: running a MANA program still gives it the permissions of the user who starts it. MANA is not an operating-system security sandbox.

## What was already in the supplied project

The project already includes its own MANA language, the Python-based engine, a 2D world with movement and collisions, material and anatomy catalogues, plane routing, the VS Code language extension, and an optional viewer for recorded spell results. Those systems were kept and tested rather than replaced. Before this update, **463 tests passed**.

## What remains unfinished

These are still open tasks and are not being presented as completed:

- **A real 3D world:** objects would need depth-aware movement, collisions, targeting, and rendering.
- **A live world editor:** the viewer can replay results, but moving things in it does not change the actual simulation.
- **Saved custom planes:** user-created plane definitions do not yet automatically persist between separate sessions.
- **Complete magic interactions:** the rules are not yet comprehensive for every kind of reflection, absorption, counterspell, or adaptation.
- **Full creature behaviour:** creature catalogues are broader than the current movement, decision-making, and biological simulation.

These require substantial engine work. Pretending they were already done would make the project harder to trust.

## External safety guidance checked

The review considered current guidance from OWASP, the official Visual Studio Code documentation, and Python's security policy. Their main practical lessons are to validate imported information, put limits on work and file sizes, restrict what a viewer can access, and never treat ordinary Python execution as a secure sandbox.

- [OWASP: Input Validation](https://cheatsheetseries.owasp.org/cheatsheets/Input_Validation_Cheat_Sheet.html)
- [OWASP: Denial of Service](https://cheatsheetseries.owasp.org/cheatsheets/Denial_of_Service_Cheat_Sheet.html)
- [Visual Studio Code: Webview security](https://code.visualstudio.com/api/extension-guides/webview)
- [Python: Security policy](https://devguide.python.org/security/policy/)

## Final checks

- **468 tests passed** in the complete test suite.
- **69 focused tests passed** for safety checks, scene recordings, and editor suggestions.
- Both VS Code extensions were rebuilt and verified.
- Python compilation, JavaScript syntax, project version checks, generated documentation, and example-output checks passed.
- A stress run created **9,999 objects** successfully within the project's existing limits.
- Two optional automatic code-style checks could not be run because their tools were not installed in this environment.
- The project remains version **1.0.0**. No public release was created.
