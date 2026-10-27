# Documentation archive

This folder stores superseded material so it remains available for history without being mistaken for the current language specification.

## Contents

- `audits/` — release-specific code audits, verification reports, and historical coverage results.
- [`MANA_V2_PRE_RELEASE_AUDIT.md`](audits/release_reports/MANA_V2_PRE_RELEASE_AUDIT.md) and [`PROJECT_AUDIT_AND_CONSOLIDATION_PRE_RELEASE.md`](audits/release_reports/PROJECT_AUDIT_AND_CONSOLIDATION_PRE_RELEASE.md) — pre-v2.0 working-copy notes; they are not current API or verification documents. [`MANA_2_0_2_LOCAL_PACKAGE_REPORT.md`](audits/release_reports/MANA_2_0_2_LOCAL_PACKAGE_REPORT.md) preserves the prior 2.0.2 package verification snapshot.
- `v0.6/`, `v0.7/`, and other version-named folders — specifications or notes superseded by later versions.

## Which document should I trust?

Use [`../current/INDEX.md`](../current/INDEX.md) for the documentation that matches the current source tree. The audit for a named old release describes only that release. It may mention functions or behavior that were subsequently removed or changed; those details are historical, not current API promises.

When moving a document here, preserve its original release identifier and do not rewrite it to claim it describes current behavior. Current audits should be stored in `audits/` with the version in the filename.
