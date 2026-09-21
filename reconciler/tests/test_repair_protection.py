"""L3-P6-05: repair class: re-apply declared branch protection (AT-033)."""

from __future__ import annotations

from datetime import date

from reconciler.cli import DeclaredState
from reconciler.comparators.branch_protection import compare
from reconciler.model import DriftClass, Finding, Level
from reconciler.repair import protection_reapply
from reconciler.state.fixture_adapter import FixtureState

AS_OF = date(2026, 8, 27)


def _fixture_a():
    declared = DeclaredState("fixture-a")
    actual = FixtureState("fixture-a")
    findings, _ = compare(declared, actual, AS_OF)
    template = declared.templates["branch-protection"]
    actual_by_repo = {repo: actual.branch_protection(repo) for repo in declared.products}
    return findings, template, actual_by_repo


def test_fixture_a_beta_weakened_finding_is_repaired_to_declared_template():
    findings, template, actual_by_repo = _fixture_a()
    repairs = protection_reapply.repair(findings, template, actual_by_repo, enabled=True)
    assert len(repairs) == 1
    repair = repairs[0]
    assert repair.scope == "beta"
    assert repair.repair_class == "protection_reapply"
    assert repair.after == template
    assert repair.after["required_pull_request_reviews"]["require_code_owner_reviews"] is True
    assert repair.before["required_pull_request_reviews"]["require_code_owner_reviews"] is False


def test_disabled_class_yields_no_repairs():
    findings, template, actual_by_repo = _fixture_a()
    repairs = protection_reapply.repair(findings, template, actual_by_repo, enabled=False)
    assert repairs == []


def test_stricter_than_declared_finding_is_never_touched():
    """AT-033: a `:stricter_than_declared` finding is filtered out
    before permitted() is even asked, and no repair is produced."""
    template = {"required_pull_request_reviews": {"required_approving_review_count": 1}}
    actual_by_repo = {"solo": {"required_pull_request_reviews": {"required_approving_review_count": 2}}}
    finding = Finding(
        id="branch_protection:solo:stricter_than_declared",
        comparator="branch_protection",
        scope="solo",
        drift_class=DriftClass.AMBER,
        level=Level.WARN,
        evidence="solo stricter than declared",
        first_seen=f"{AS_OF.isoformat()}T00:00:00Z",
    )
    repairs = protection_reapply.repair([finding], template, actual_by_repo, enabled=True)
    assert repairs == []


def test_findings_from_other_comparators_are_ignored():
    template = {"enforce_admins": True}
    actual_by_repo = {"solo": {"enforce_admins": False}}
    finding = Finding(
        id="codeowners:solo:hand_edited",
        comparator="codeowners",
        scope="solo",
        drift_class=DriftClass.AMBER,
        level=Level.WARN,
        evidence="unrelated",
        first_seen=f"{AS_OF.isoformat()}T00:00:00Z",
    )
    repairs = protection_reapply.repair([finding], template, actual_by_repo, enabled=True)
    assert repairs == []


def test_contexts_never_shortened_when_actual_has_an_extra_context():
    """A repository that is weaker on one field but has *more*
    required-status-check contexts than declared must not be repaired
    at all - re-applying declared_template wholesale would drop the
    actual-only context, which is exactly the shortening this class
    must never perform."""
    template = {
        "required_pull_request_reviews": {"require_code_owner_reviews": True},
        "required_status_checks": {"contexts": ["control-plane/blocking-drift"]},
    }
    actual = {
        "required_pull_request_reviews": {"require_code_owner_reviews": False},
        "required_status_checks": {"contexts": ["control-plane/blocking-drift", "extra-check"]},
    }
    finding = Finding(
        id="branch_protection:solo:weakened",
        comparator="branch_protection",
        scope="solo",
        drift_class=DriftClass.BLOCKING,
        level=Level.BLOCK,
        evidence="solo weakened",
        first_seen=f"{AS_OF.isoformat()}T00:00:00Z",
    )
    repairs = protection_reapply.repair([finding], template, {"solo": actual}, enabled=True)
    assert repairs == []


def test_already_matching_state_yields_no_repair():
    template = {"enforce_admins": True}
    finding = Finding(
        id="branch_protection:solo:weakened",
        comparator="branch_protection",
        scope="solo",
        drift_class=DriftClass.BLOCKING,
        level=Level.BLOCK,
        evidence="solo weakened",
        first_seen=f"{AS_OF.isoformat()}T00:00:00Z",
    )
    repairs = protection_reapply.repair([finding], template, {"solo": dict(template)}, enabled=True)
    assert repairs == []


def test_compensating_action_names_the_prior_state():
    findings, template, actual_by_repo = _fixture_a()
    repairs = protection_reapply.repair(findings, template, actual_by_repo, enabled=True)
    assert "prior branch protection" in repairs[0].compensating_action
    assert "beta" in repairs[0].compensating_action


def test_missing_actual_state_fails_closed_rather_than_guessing():
    """A repository absent from `actual_by_repo` compares an empty dict
    against the template. `stricter.permitted()` treats a key present
    on one side and absent on the other as an unrecognised shape and
    refuses (fail-closed) rather than guessing that "absent" means
    "fully unprotected" - the same fail-closed discipline spec 64.2
    applies to an unclassified control."""
    template = {"enforce_admins": True}
    finding = Finding(
        id="branch_protection:ghost:weakened",
        comparator="branch_protection",
        scope="ghost",
        drift_class=DriftClass.BLOCKING,
        level=Level.BLOCK,
        evidence="ghost weakened",
        first_seen=f"{AS_OF.isoformat()}T00:00:00Z",
    )
    repairs = protection_reapply.repair([finding], template, {}, enabled=True)
    assert repairs == []
