# Documentation archive

This folder stores superseded material so it remains available for history without being mistaken for the current language specification.

## Contents

- `audits/` — release-specific code audits, verification reports, and historical coverage results.
- `v0.6/`, `v0.7/`, and other version-named folders — specifications or notes superseded by later versions.

## Which document should I trust?

Use [`../current/INDEX.md`](../current/INDEX.md) for the documentation that matches the current source tree. The audit for a named old release describes only that release. It may mention functions or behavior that were subsequently removed or changed; those details are historical, not current API promises.

When moving a document here, preserve its original release identifier and do not rewrite it to claim it describes current behavior. Current audits should be stored in `audits/` with the version in the filename.
