# MANA branding assets

- `mana-logo.png` is the supplied high-resolution MANA logo with a transparent background. Keep this source artwork for project branding.
- `mana-icon.png` is the 512 × 512 PNG export used in the GitHub README and the VS Code extension icon.

The VSIX builder automatically copies `mana-icon.png` into the extension package and sets its `icon` metadata. Rebuild and verify the extension after changing either icon or extension metadata:

```powershell
python tools/vscode/build_mana_vsix.py
python tools/vscode/build_mana_vsix.py --check
```
