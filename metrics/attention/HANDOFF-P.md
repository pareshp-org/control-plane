# What the attention ledger emits for subsystem P

Written by lane L4, phase 4 (`implementation/lanes/L4-04-attention-ledger.md`, task L4-T413).
Authority: MasterSpec v4.0 Section 97.4 lines 8975-8976; Section 69.2 line 5720; Section 83.1
line 7280; Section 93; Section 99.2 line 9203.

## The boundary

Subsystem P — people intelligence: capacity profiles, utilisation composition, bandwidth states,
overload and under-utilisation detection, staffing diagnosis (Section 99.2, line 9203) — is
assigned to no lane in PARTITION v1. L4 does not claim it and builds none of it. L4 owns the
ledger; P owns every surface the ledger feeds. See L4-04-attention-ledger.md section 5,
DECISION REQUIRED D-L4-P4-04, routed to L0.

## What L4 emits, and where it comes from

| Emitted field | Emitted by | Meaning | Spec |
| --- | --- | --- | --- |
| `hours` / `hours_by_category` | metrics/attention/derive.py | Derived attention hours in the eight-category taxonomy, one category per hour | 67.1 line 5573; 67.2 line 5579 |
| `total_hours` | metrics/attention/derive.py | The person-day total AFTER the daily reconciliation | 97.4 line 8975 |
| `truncations`, `truncation_detail` | metrics/attention/derive.py | Every truncation the reconciliation applied, category and hours removed. "each truncation is recorded" | 97.4 line 8975 |
| `instrument_defect` | metrics/attention/derive.py | The day exceeded scheduled availability BEFORE truncation | 97.4 line 8976 |
| `capacity_profile_eligible` | metrics/attention/derive.py | false on a defect day | 97.4 line 8976 |
| `workload_state_eligible` | metrics/attention/derive.py | false on a defect day; the Section 83 consumer | 97.4 line 8976; 83.1 line 7280 |
| `founder_view_eligible` | metrics/attention/derive.py | false on a defect day; the Section 93 consumer | 97.4 line 8976 |
| `provenance: self-reported` | metrics/attention/derive.py | Carried permanently on any figure including self-reported hours | 97.4 line 8980 |
| `scheduled_availability_hours` | metrics/attention/scheduled-availability.py | The declared cap, from work_arrangement | 69.2 line 5720; 7.3 |

## Four obligations P inherits, each already stated in the spec

1. **Honour the three eligibility flags.** A day with `instrument_defect: true` never enters a
   Capacity Profile, a workload state or the Founder view (line 8976). It is an instrument
   finding, never a workload finding about a person.
2. **Carry the self-reported label wherever the figure renders, permanently** (line 8980).
   Coordination is never presented beside genuinely derived categories without it.
3. **Never render attention hours as individual performance evidence**, and never as a per-person
   drill-down on a general surface. Aggregate at product and portfolio level only
   (Section 67.3 line 5605; Section 91.2 lines 8083-8092).
4. **Declare the eight metric attributes** for anything built on these fields: definition, source,
   time window, baseline, expected interpretation, known limitations, owner, action on breach
   (Section 84.6 line 7471). The ledger's own declared limitation is Section 97.4 line 8978: it is
   a LOWER BOUND on attention, and Architecture and Coordination are systematically under-counted.

## What L4 does NOT emit, and will not

A Capacity Profile; a workload state; a bandwidth state; a Founder view; a utilisation
composition; a staffing diagnosis; any per-person surface. The drift finding a defect day raises
(line 8976) is also not L4's: `validators/drift/**` belongs to L3 (PARTITION.md line 19). L4
emits the flag; L3 raises the finding; P renders nothing until it has an owner.
