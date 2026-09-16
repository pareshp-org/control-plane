# metrics/ingest - collector declarations (Lane 4, subsystem I)

Master Spec section 99.2 line 9196 assigns to subsystem I:
"DevLake nightly ingest; Prometheus scraping /health, /version, /metrics;
Scorecard scheduled scan with drop detection; the event-log taxonomy;
attention ledger; metric source discipline".

## What lives here

One file per collector. Declarations only - what each collector is allowed to
source, at what cadence, under what confirmation state, and how a metric reading
from it must be armed. No file here installs, configures or contacts anything.

## Who consumes it, and who does not

| Consumer | What it takes | Owner |
| --- | --- | --- |
| Operations VM install and collector configuration | cadence, targets, credentials shape | L5, ops-vm/** (subsystem M, spec line 9200) |
| Grafana surfaces of Section 92 | the armed set and the source kinds | subsystem H - UNASSIGNED in PARTITION v1, see D-L4-P5-03 |
| The metric register and the Section 103 computations | source-kinds.yaml, devlake-coverage.yaml | Lane 4 Phase 7, L4-P7-01 and L4-P7-02 |
| The reconciler drift rows | nothing in this directory | L3 |

L4 declares. L5 installs. H renders. Lane 4 opens no Grafana file and no
ops-vm/** file (PARTITION.md rule 1, line 25).

## The rule that binds every file here

Invariant 46 (spec line 9513): "Derived data is computed, never hand-maintained.
Metrics derive from the canonical record stores of Section 97, never from
hand-maintained numbers." DevLake, Prometheus and Scorecard are not Section 97
record stores. source-kinds.yaml (L4-P5-22) states what that means mechanically.
