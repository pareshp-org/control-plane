# What the organisation export does not carry

Stated here so a responder discovers it before the restore, not during one.

| Excluded | Why | Dependent control |
| --- | --- | --- |
| The organisation audit log | Its API is Enterprise-only; on the Team plan it cannot be exported (Section 45.3, D80) | A recorded accepted risk whose compensating cadence is the manual audit-log review of Section 45.3 - owned by the escalation role, written to `records/security-reviews/`, raising SIG-44 when stale. That record and that policy entry are subsystem O and are not created by this lane |
| Layer B people data | The export is organisation-readable in restore; Section 51.4 forbids Layer B content in an organisation-readable repository | The Layer B recovery baseline is the Section 45.4 restore, recorded as a decision |
| Secret values | Section 45.1: the reconstruction set carries secret *references* - names, scopes and locations - never values | `ops-vm/checks/export-no-secret-values.sh` fails the run rather than shipping a value |

Two classes travel by their own mechanism, not by the migrations archive:

* Projects v2 boards are **not** included in migration archives and are captured
  by a separate GraphQL dump (Section 45.3, D80).
* Issues, pull requests and review records travel through the migrations REST
  API alongside the repositories.
