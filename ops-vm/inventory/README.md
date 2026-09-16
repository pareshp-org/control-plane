# The operations VM and the asset inventory

The inventory itself lives at `assets/inventory/` (one file per asset) and
`assets/deadlines/` (one file per announced external deadline). Its schema, its
field table and its validator are built by the lane's asset phase. The
operations VM is a **reader**: the daily sweep in `ops-vm/jobs/` opens those
files, computes days-to-expiry, and writes a report and Prometheus text under
`/var/lib/ops-vm/inventory/`. It never creates, edits or deletes an entry.

Field names used by the sweep are the binding common fields of Section 49.1:
`asset_id`, `asset_class`, `owner`, `expiry_date`, `alert_days`, `cost_band`,
`spec_reference`.

Two rules the sweep enforces rather than assumes:

* `alert_days` is at least 30 (Section 49.1). The floor is a specification
  constant; the value above the floor is owner-set at entry creation and is
  longer wherever the migration behind the deadline is large (Section 49.2).
* The sweep is a **wait surface** (Section 92.11). Reaching an alert threshold
  renders on the report and in the metric; it does not page anyone. Only the
  sweep's own failure is a push event, on the job-failure discipline of
  Section 44.3.

Every run writes its result and a clean run is recorded as clean (Section 53.1).
