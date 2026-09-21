# Handoff: the drill record lands in `records/`

Section 45.4 requires each drill to write a drill record to `records/`. The
records repository is **lane L4's** in full under the FROZEN partition; lane L5
does not write it.

L5 produces the record **content** at `ops-vm/drill/drill-record.template.yaml`
and three checks that grade it:

| Check | What it enforces |
| --- | --- |
| `ops-vm/checks/drill-clock.sh` | Clock starts at provision-start, stops at dashboards-green, includes the Layer B restore, under 4 hours, no omitted step |
| `ops-vm/checks/drill-offvm-legs-fired.sh` | Both off-VM legs fired **while the VM was stopped**, routed to the messaging channel and the phone path |
| `ops-vm/checks/drill-zero-resources.sh` | Provider listing for the drill tag shows zero resources; volume snapshots and provider-side backups are explicitly named as deleted; no document was opened |

L4 owns the write path and the record schema. The confirmation lands through the
**RECORD-VERIFICATION-RESULT dispatch (Section 97.2)** with a named executor -
never as free text a person writes about their own actions. A drill record filed
without its zero-resources evidence is **Blocking drift** (Section 45.4), which
is why `drill-zero-resources.sh` exits 4 rather than 1.

Note: this drill's rebuild step validates against `ops-vm/rebuild/runbook.src.md`
via `ops-vm/tools/rebuild_clock.py --validate` (the manifest L5-04-16 actually
shipped), not a `rebuild-driver/` path.
