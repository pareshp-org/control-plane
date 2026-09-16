"""
Integration test: C-EVT-ENUM-1 closed event_type enum (D114-D / REG-021).

Validates the event_type identifier set defined by run-phase-0.sh's
L0-P0-011 task (contracts/records/event-type.enum.v1.yaml, C-EVT-ENUM-1)
against the human-readable companion authored by L0-P0-025
(contracts/event-types.yaml, C-EVT-TYPES-1).

The expected content below is HARDCODED as literal Python strings, copied
verbatim from the heredoc bodies in run-phase-0.sh (as of the version at
the time this test was written). This is intentional: the test must not
depend on run-phase-0.sh's exact heredoc syntax remaining parseable by an
extraction script, and it must not re-run/re-parse the shell script on
every test invocation. If C-EVT-ENUM-1 or C-EVT-TYPES-1 changes (a new
D-series decision, a taxonomy revision), the fixtures below must be
updated by hand to match the new run-phase-0.sh content, and this
docstring's provenance note updated accordingly.

Provenance: run-phase-0.sh, L0-P0-011 heredoc (lines ~628-722,
'cat > contracts/records/event-type.enum.v1.yaml <<ENUMEOF' ... 'ENUMEOF')
and L0-P0-025 heredoc (lines ~1026-1145,
'cat > contracts/event-types.yaml <<ETEOF' ... 'ETEOF'), read fresh from
the repository on 2026-09-09.
"""
import io

import yaml

# ─────────────────────────────────────────────────────────────────────────────
# Fixture 1: C-EVT-ENUM-1 — contracts/records/event-type.enum.v1.yaml
# Verbatim body of the L0-P0-011 heredoc (between ENUMEOF markers).
# ─────────────────────────────────────────────────────────────────────────────
EVENT_TYPE_ENUM_V1_YAML = """\
# C-EVT-ENUM-1 — closed event_type enum, 89 identifiers (D-L0-03 / Section 97.3; D114-D raises 86->89, REG-021)
schema_version: 1
enum_version: "1.0"
event_types:
  - {id: work_item_created, taxonomy_entry: "Work item created", payload_fields: [], retired: false}
  - {id: work_item_moved_to_ready, taxonomy_entry: "moved to Ready", payload_fields: [], retired: false}
  - {id: work_item_assigned, taxonomy_entry: "assigned", payload_fields: [], retired: false}
  - {id: ready_queue_miss_recorded, taxonomy_entry: "Ready-queue miss recorded", payload_fields: [], retired: false}
  - {id: plan_submitted, taxonomy_entry: "plan submitted", payload_fields: [], retired: false}
  - {id: plan_rejected, taxonomy_entry: "plan rejected with reason", payload_fields: [], retired: false}
  - {id: plan_approved, taxonomy_entry: "plan approved (Gate 1) with agent_authored flag", payload_fields: [agent_authored], retired: false}
  - {id: change_class_assigned, taxonomy_entry: "change class assigned", payload_fields: [], retired: false}
  - {id: impact_scope_assigned, taxonomy_entry: "impact scope assigned", payload_fields: [], retired: false}
  - {id: reversibility_class_assigned, taxonomy_entry: "reversibility class assigned", payload_fields: [], retired: false}
  - {id: requirement_changed_materially, taxonomy_entry: "requirement changed materially", payload_fields: [], retired: false}
  - {id: replan_triggered, taxonomy_entry: "re-plan triggered", payload_fields: [], retired: false}
  - {id: execute_started, taxonomy_entry: "execute started", payload_fields: [], retired: false}
  - {id: pr_opened, taxonomy_entry: "PR opened with agent_authored flag", payload_fields: [agent_authored], retired: false}
  - {id: review_requested, taxonomy_entry: "review requested", payload_fields: [], retired: false}
  - {id: gate2_approved, taxonomy_entry: "Gate 2 approval with reviewer role", payload_fields: [reviewer_role], retired: false}
  - {id: ci_check_completed, taxonomy_entry: "CI pass or fail per check", payload_fields: [state], retired: false}
  - {id: parity_check_completed, taxonomy_entry: "parity check result", payload_fields: [], retired: false}
  - {id: artifact_built, taxonomy_entry: "artifact built with digest", payload_fields: [digest], retired: false}
  - {id: staging_deployed, taxonomy_entry: "staging deployed", payload_fields: [], retired: false}
  - {id: staging_smoke_completed, taxonomy_entry: "staging smoke result", payload_fields: [], retired: false}
  - {id: uat_executed, taxonomy_entry: "UAT executed with result", payload_fields: [], retired: false}
  - {id: pr_merged, taxonomy_entry: "merge", payload_fields: [], retired: false}
  - {id: production_approval_granted, taxonomy_entry: "production approval granted with approver", payload_fields: [approver], retired: false}
  - {id: production_deployed, taxonomy_entry: "production deployed with digest", payload_fields: [digest], retired: false}
  - {id: production_smoke_completed, taxonomy_entry: "production smoke result", payload_fields: [], retired: false}
  - {id: version_digest_confirmed, taxonomy_entry: "/version digest confirmed", payload_fields: [], retired: false}
  - {id: health_check_completed, taxonomy_entry: "health check result", payload_fields: [], retired: false}
  - {id: feature_flag_toggled, taxonomy_entry: "feature flag enabled or disabled", payload_fields: [state], retired: false}
  - {id: rollback_initiated, taxonomy_entry: "rollback initiated with from-digest and to-digest", payload_fields: [from_digest, to_digest], retired: false}
  - {id: hotfix_authorised, taxonomy_entry: "hotfix authorised", payload_fields: [], retired: false}
  - {id: incident_opened, taxonomy_entry: "incident opened with severity", payload_fields: [severity], retired: false}
  - {id: incident_resolved, taxonomy_entry: "incident resolved", payload_fields: [], retired: false}
  - {id: postmortem_completed, taxonomy_entry: "postmortem completed", payload_fields: [], retired: false}
  - {id: regression_test_added, taxonomy_entry: "regression test added for a production bug", payload_fields: [], retired: false}
  - {id: security_incident_opened, taxonomy_entry: "security incident opened", payload_fields: [], retired: false}
  - {id: credential_rotated, taxonomy_entry: "credential rotated", payload_fields: [], retired: false}
  - {id: restore_test_executed, taxonomy_entry: "restore test executed with result", payload_fields: [], retired: false}
  - {id: asset_expiry_alerted, taxonomy_entry: "secret or certificate expiry alert", payload_fields: [], retired: false}
  - {id: asset_owner_reassigned, taxonomy_entry: "asset owner reassigned", payload_fields: [], retired: false}
  - {id: lifecycle_transitioned, taxonomy_entry: "lifecycle transition", payload_fields: [], retired: false}
  - {id: launch_readiness_signed_off, taxonomy_entry: "launch readiness signed off", payload_fields: [], retired: false}
  - {id: reviewer_matrix_changed, taxonomy_entry: "reviewer matrix change", payload_fields: [], retired: false}
  - {id: knowledge_redundancy_status_changed, taxonomy_entry: "knowledge redundancy status change", payload_fields: [], retired: false}
  - {id: person_added, taxonomy_entry: "person added", payload_fields: [], retired: false}
  - {id: person_role_changed, taxonomy_entry: "person role changed", payload_fields: [], retired: false}
  - {id: person_departed, taxonomy_entry: "person departed", payload_fields: [], retired: false}
  - {id: orphan_detected, taxonomy_entry: "orphan detected", payload_fields: [], retired: false}
  - {id: orphan_resolved, taxonomy_entry: "orphan resolved", payload_fields: [], retired: false}
  - {id: temporary_assignment_state_changed, taxonomy_entry: "temporary assignment created and expired", payload_fields: [state], retired: false}
  - {id: acting_team_lead_state_changed, taxonomy_entry: "acting team lead activated and deactivated", payload_fields: [state], retired: false}
  - {id: drift_detected, taxonomy_entry: "drift detected by severity", payload_fields: [severity], retired: false}
  - {id: drift_repaired, taxonomy_entry: "drift repaired", payload_fields: [], retired: false}
  - {id: product_created, taxonomy_entry: "product created", payload_fields: [], retired: false}
  - {id: product_split, taxonomy_entry: "product split", payload_fields: [], retired: false}
  - {id: product_merged, taxonomy_entry: "product merged", payload_fields: [], retired: false}
  - {id: product_transferred, taxonomy_entry: "product transferred", payload_fields: [], retired: false}
  - {id: shared_service_created, taxonomy_entry: "shared service created", payload_fields: [], retired: false}
  - {id: shared_service_breaking_change_released, taxonomy_entry: "shared service breaking change released", payload_fields: [], retired: false}
  - {id: platform_change_proposed, taxonomy_entry: "platform change proposed", payload_fields: [], retired: false}
  - {id: canary_started, taxonomy_entry: "canary started", payload_fields: [], retired: false}
  - {id: canary_completed, taxonomy_entry: "canary result", payload_fields: [state], retired: false}
  - {id: fleet_rollout_started, taxonomy_entry: "fleet rollout started", payload_fields: [], retired: false}
  - {id: platform_rollback_initiated, taxonomy_entry: "platform rollback initiated", payload_fields: [], retired: false}
  - {id: contract_version_migrated, taxonomy_entry: "contract version migrated", payload_fields: [], retired: false}
  - {id: compatibility_state_changed, taxonomy_entry: "compatibility state changed", payload_fields: [], retired: false}
  - {id: background_pr_created, taxonomy_entry: "background layer PR created", payload_fields: [], retired: false}
  - {id: background_pr_dispositioned, taxonomy_entry: "accepted or rejected with task-class reason", payload_fields: [state, task_class_reason], retired: false}
  - {id: task_class_state_changed, taxonomy_entry: "task class suspended or restored", payload_fields: [state], retired: false}
  - {id: ai_runtime_changed, taxonomy_entry: "AI runtime changed", payload_fields: [], retired: false}
  - {id: ai_provider_outage_recorded, taxonomy_entry: "AI provider outage recorded", payload_fields: [], retired: false}
  - {id: model_benchmark_completed, taxonomy_entry: "model benchmark completed", payload_fields: [], retired: false}
  - {id: status_request_received, taxonomy_entry: "status request received (Coordination category)", payload_fields: [], retired: false}
  - {id: plan_approver_notified, taxonomy_entry: "plan submitted-to-approver notification sent", payload_fields: [], retired: false}
  - {id: verification_block_state_changed, taxonomy_entry: "verification blocked and unblocked", payload_fields: [state], retired: false}
  - {id: degraded_mode_state_changed, taxonomy_entry: "degraded mode entered and exited", payload_fields: [state], retired: false}
  - {id: gap_procedure_run, taxonomy_entry: "gap procedure run", payload_fields: [], retired: false}
  - {id: eval_regression_detected, taxonomy_entry: "eval regression detected", payload_fields: [], retired: false}
  - {id: pending_decision_state_changed, taxonomy_entry: "pending decision opened and closed", payload_fields: [state], retired: false}
  - {id: onboarding_phase_completed, taxonomy_entry: "onboarding phase completed", payload_fields: [], retired: false}
  - {id: support_item_ingested, taxonomy_entry: "support item ingested", payload_fields: [], retired: false}
  - {id: support_first_touch_breached, taxonomy_entry: "support first-touch breach", payload_fields: [], retired: false}
  - {id: delegation_expiry_warned, taxonomy_entry: "delegation expiry warning issued", payload_fields: [], retired: false}
  - {id: temporary_person_expiry_warned, taxonomy_entry: "temporary-person expiry warning issued", payload_fields: [], retired: false}
  - {id: launch_signoff_requested, taxonomy_entry: "launch sign-off requested", payload_fields: [], retired: false}
  - {id: weekend_exception_state_changed, taxonomy_entry: "weekend exception requested, authorised, worked, TOIL scheduled and taken", payload_fields: [state], retired: false}
  - {id: support_loop_closure, taxonomy_entry: "support loop closed", payload_fields: [], retired: false}
  - {id: deletion_request_recorded, taxonomy_entry: "deletion request recorded", payload_fields: [], retired: false}
  - {id: work_item_closed, taxonomy_entry: "work item closed", payload_fields: [], retired: false}
"""

# ─────────────────────────────────────────────────────────────────────────────
# Fixture 2: C-EVT-TYPES-1 — contracts/event-types.yaml
# Verbatim body of the L0-P0-025 heredoc (between ETEOF markers).
# ─────────────────────────────────────────────────────────────────────────────
EVENT_TYPES_YAML = """\
# Canonical event_type enum — authoritative source for all lanes (FD-Q12 2026-09-02)
# DO NOT edit in L3/L4/L5 — update here only
# D114-D (REG-021, 2026-09-02) raises C-EVT-ENUM-1 from 86 to 89 identifiers.
event_types:
  - product_created
  - product_updated
  - product_deleted
  - product_activated
  - product_deactivated
  - schema_validated
  - schema_rejected
  - attention_raised
  - attention_cleared
  - lane_started
  - lane_completed
  - lane_blocked
  - gate_passed
  - gate_failed
  - merge_train_started
  - merge_train_completed
  - merge_train_rejected
  - rollback_initiated
  - rollback_completed
  - foreign_path_violation
  - unassigned_path_violation
  - phase_transition
  - doc_retired
  - doc_superseded
  # --- all 89 identifiers from C-EVT-ENUM-1 (L0-P0-011, D114-D) follow ---
  - work_item_created
  - work_item_moved_to_ready
  - work_item_assigned
  - ready_queue_miss_recorded
  - plan_submitted
  - plan_rejected
  - plan_approved
  - change_class_assigned
  - impact_scope_assigned
  - reversibility_class_assigned
  - requirement_changed_materially
  - replan_triggered
  - execute_started
  - pr_opened
  - review_requested
  - gate2_approved
  - ci_check_completed
  - parity_check_completed
  - artifact_built
  - staging_deployed
  - staging_smoke_completed
  - uat_executed
  - pr_merged
  - production_approval_granted
  - production_deployed
  - production_smoke_completed
  - version_digest_confirmed
  - health_check_completed
  - feature_flag_toggled
  # rollback_initiated already listed above (system meta-event subset, FD-Q12)
  - hotfix_authorised
  - incident_opened
  - incident_resolved
  - postmortem_completed
  - regression_test_added
  - security_incident_opened
  - credential_rotated
  - restore_test_executed
  - asset_expiry_alerted
  - asset_owner_reassigned
  - lifecycle_transitioned
  - launch_readiness_signed_off
  - reviewer_matrix_changed
  - knowledge_redundancy_status_changed
  - person_added
  - person_role_changed
  - person_departed
  - orphan_detected
  - orphan_resolved
  - temporary_assignment_state_changed
  - acting_team_lead_state_changed
  - drift_detected
  - drift_repaired
  # product_created already listed above (system meta-event subset, FD-Q12)
  - product_split
  - product_merged
  - product_transferred
  - shared_service_created
  - shared_service_breaking_change_released
  - platform_change_proposed
  - canary_started
  - canary_completed
  - fleet_rollout_started
  - platform_rollback_initiated
  - contract_version_migrated
  - compatibility_state_changed
  - background_pr_created
  - background_pr_dispositioned
  - task_class_state_changed
  - ai_runtime_changed
  - ai_provider_outage_recorded
  - model_benchmark_completed
  - status_request_received
  - plan_approver_notified
  - verification_block_state_changed
  - degraded_mode_state_changed
  - gap_procedure_run
  - eval_regression_detected
  - pending_decision_state_changed
  - onboarding_phase_completed
  - support_item_ingested
  - support_first_touch_breached
  - delegation_expiry_warned
  - temporary_person_expiry_warned
  - launch_signoff_requested
  - weekend_exception_state_changed
  - support_loop_closure
  - deletion_request_recorded
  - work_item_closed
"""

# The three identifiers added by D114-D (REG-021, 2026-09-02), raising the
# taxonomy from 86 to 89 identifiers.
D114_D_IDENTIFIERS = [
    "support_loop_closure",
    "deletion_request_recorded",
    "work_item_closed",
]

EXPECTED_ENUM_COUNT = 89


def _load_enum_ids():
    """Parse EVENT_TYPE_ENUM_V1_YAML and return the list of `id` values,
    in document order, exactly as C-EVT-ENUM-1 declares them."""
    data = yaml.safe_load(io.StringIO(EVENT_TYPE_ENUM_V1_YAML))
    return [entry["id"] for entry in data["event_types"]]


def _load_event_types_list():
    """Parse EVENT_TYPES_YAML and return the list of event_type strings,
    in document order, exactly as contracts/event-types.yaml declares them."""
    data = yaml.safe_load(io.StringIO(EVENT_TYPES_YAML))
    return data["event_types"]


def test_fixtures_parse_as_yaml():
    """Sanity check: both hardcoded fixtures are well-formed YAML with the
    expected top-level shape, so a copy/paste error in the fixture itself
    surfaces clearly rather than masquerading as a taxonomy failure."""
    enum_data = yaml.safe_load(io.StringIO(EVENT_TYPE_ENUM_V1_YAML))
    assert isinstance(enum_data, dict)
    assert "event_types" in enum_data
    assert isinstance(enum_data["event_types"], list)
    for entry in enum_data["event_types"]:
        assert "id" in entry

    types_data = yaml.safe_load(io.StringIO(EVENT_TYPES_YAML))
    assert isinstance(types_data, dict)
    assert "event_types" in types_data
    assert isinstance(types_data["event_types"], list)


def test_enum_has_exactly_89_unique_ids():
    """C-EVT-ENUM-1 (L0-P0-011) must declare exactly 89 identifiers, and
    none of them may be duplicates (the enum is closed per D-L0-03 /
    Section 97.3, raised 86->89 by D114-D / REG-021)."""
    ids = _load_enum_ids()
    assert len(ids) == EXPECTED_ENUM_COUNT, (
        f"expected exactly {EXPECTED_ENUM_COUNT} identifiers in "
        f"C-EVT-ENUM-1, got {len(ids)}"
    )
    unique_ids = set(ids)
    assert len(unique_ids) == EXPECTED_ENUM_COUNT, (
        f"expected {EXPECTED_ENUM_COUNT} unique identifiers in "
        f"C-EVT-ENUM-1, got {len(unique_ids)} unique out of {len(ids)} total"
    )


def test_no_duplicate_ids_in_enum():
    """Explicit duplicate check with a clear failure message identifying
    which id(s) recur, independent of the count assertion above."""
    ids = _load_enum_ids()
    seen = set()
    duplicates = set()
    for i in ids:
        if i in seen:
            duplicates.add(i)
        seen.add(i)
    assert not duplicates, f"duplicate id(s) found in C-EVT-ENUM-1: {sorted(duplicates)}"


def test_no_duplicate_ids_in_event_types_list():
    """The 111 non-comment entries in contracts/event-types.yaml include
    two deliberate overlaps (product_created, rollback_initiated) that are
    listed once each — not as literal duplicate list entries. The parsed
    list itself must therefore contain no duplicate strings."""
    types_list = _load_event_types_list()
    seen = set()
    duplicates = set()
    for t in types_list:
        if t in seen:
            duplicates.add(t)
        seen.add(t)
    assert not duplicates, (
        f"duplicate event_type entries found in contracts/event-types.yaml: "
        f"{sorted(duplicates)}"
    )


def test_all_89_enum_ids_present_in_event_types_yaml():
    """Every identifier in the closed C-EVT-ENUM-1 enum (L0-P0-011) must
    also appear in the human-readable canonical list authored by
    L0-P0-025 (contracts/event-types.yaml) — the two are meant to stay in
    lockstep per D114-D / REG-021."""
    enum_ids = set(_load_enum_ids())
    assert len(enum_ids) == EXPECTED_ENUM_COUNT

    types_list = set(_load_event_types_list())
    missing = enum_ids - types_list
    assert not missing, (
        f"C-EVT-ENUM-1 identifier(s) missing from contracts/event-types.yaml: "
        f"{sorted(missing)}"
    )


def test_d114_d_identifiers_present_in_enum():
    """The three D114-D (REG-021, 2026-09-02) additions — which raised the
    taxonomy from 86 to 89 identifiers — must be present in C-EVT-ENUM-1."""
    ids = set(_load_enum_ids())
    for identifier in D114_D_IDENTIFIERS:
        assert identifier in ids, (
            f"D114-D identifier '{identifier}' missing from C-EVT-ENUM-1"
        )


def test_d114_d_identifiers_present_in_event_types_yaml():
    """The three D114-D additions must also be present in the
    human-readable contracts/event-types.yaml list."""
    types_list = set(_load_event_types_list())
    for identifier in D114_D_IDENTIFIERS:
        assert identifier in types_list, (
            f"D114-D identifier '{identifier}' missing from "
            f"contracts/event-types.yaml"
        )


def test_enum_ids_are_well_formed():
    """Every id in C-EVT-ENUM-1 is a non-empty lowercase snake_case token
    (defensive check against a stray typo surviving a hand-edit of the
    fixture)."""
    ids = _load_enum_ids()
    for i in ids:
        assert isinstance(i, str) and i, f"empty or non-string id: {i!r}"
        assert i == i.lower(), f"id is not lowercase: {i!r}"
        assert " " not in i, f"id contains whitespace: {i!r}"
