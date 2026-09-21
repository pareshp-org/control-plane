# Event-type retirement policy

Master Spec v4.0 Section 97.3, line 8959: *"Every entry in the taxonomy below has exactly
one stable `event_type` identifier — lower-case, underscore-separated, never renamed once
shipped."* Line 8961: *"Retiring an identifier marks it retired in the enum and never
removes it."*

## The rule

- An `event_type` identifier, once it ships in `metrics/taxonomy/event-types.yaml`, is never
  deleted from that file. Events already written under it stay readable forever and its
  `event_type` value is honoured for the life of the records repository.
- Retiring an identifier means adding `retired: true` to its row. The row's `id`, `n`
  position and `entry` text stay exactly as shipped.
- A governed addition appends a new row at the next `n`. It never reuses a retired `id`.
- `identifier_count` and the strict 1..N `n` ordering (checked by
  `validate-taxonomy.sh`'s default `--taxonomy` mode) are unaffected by retirement — a
  retired row is still counted, still present, still in order.

## Enforcement

`tools/records/validate-taxonomy.sh --retirement [<baseline-ref>]` proves the rule
mechanically. `<baseline-ref>` defaults to `origin/integration`.

1. It reads the `id` set of the working copy of `metrics/taxonomy/event-types.yaml`.
2. It reads the `id` set of the same path as it existed at `<baseline-ref>`
   (`git show <baseline-ref>:metrics/taxonomy/event-types.yaml`).
3. Any identifier present at the baseline and absent from the working copy is Blocking
   drift: the check fails closed and prints
   `RETIREMENT FAIL: removed identifier(s) that previously shipped: <ids>`, exit `1`.
4. An identifier that is present at both ends — retired or not — is accepted. The check
   prints `RETIREMENT OK <n>` and exits `0`.
5. If `<baseline-ref>` carries no `event-types.yaml` at all (the first publication), there
   is nothing yet that could have been removed; the check passes trivially with
   `RETIREMENT OK 0`.

This is a fail-closed comparison, not a rename or content diff: changing an entry's
`entry:` wording, `payload_required`, or adding `retired: true` never trips it. Only the
disappearance of a previously-shipped `id` does.

See `tools/records/checks/L4-P3-03.sh` for the proving fixtures: one case that retires an
identifier (accepted) and one case that deletes an identifier outright (rejected).
