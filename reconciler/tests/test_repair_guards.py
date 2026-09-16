"""L3-P6-09: prohibited-repair guards."""

from __future__ import annotations

from reconciler.repair import enablement, guards

# A deliberately non-compliant module: constructs Repair(...) without
# ever calling permitted() first. Used only via audit_source() below -
# never written to disk under reconciler/repair/**, so it never
# perturbs audit_package()'s five-module count.
_NO_PERMITTED_CHECK_SOURCE = '''
from reconciler.repair import Repair

def repair(findings, *, enabled):
    repairs = []
    for finding in findings:
        repairs.append(
            Repair(
                repair_class="rogue",
                finding_id=finding.id,
                scope=finding.scope,
                before={},
                after={},
                permitted_reason="skipped the gate",
                compensating_action="none",
            )
        )
    return repairs
'''

# Calls a mutating verb against a GitHub Actions secret - one of spec
# 53.3's absolute refusals - even though it also calls permitted()
# first, so this isolates the forbidden-write check from the ordering
# check above.
_SECRET_WRITE_SOURCE = '''
from reconciler.repair import Repair
from reconciler.repair.stricter import permitted

def repair(findings, *, enabled):
    repairs = []
    for finding in findings:
        ok, reason = permitted(True, False, "team_membership")
        if not ok:
            continue
        client.rotate_secret(finding.scope)
        repairs.append(
            Repair(
                repair_class="rogue",
                finding_id=finding.id,
                scope=finding.scope,
                before={},
                after={},
                permitted_reason=reason,
                compensating_action="none",
            )
        )
    return repairs
'''

# Calls a mutating verb against records/** - the other absolute
# refusal this task names by name.
_RECORDS_WRITE_SOURCE = '''
from reconciler.repair import Repair
from reconciler.repair.stricter import permitted

def repair(findings, *, enabled):
    repairs = []
    for finding in findings:
        ok, reason = permitted(True, False, "team_membership")
        if not ok:
            continue
        client.records_write(finding.scope, {})
        repairs.append(
            Repair(
                repair_class="rogue",
                finding_id=finding.id,
                scope=finding.scope,
                before={},
                after={},
                permitted_reason=reason,
                compensating_action="none",
            )
        )
    return repairs
'''


def test_audit_package_finds_exactly_five_repair_class_modules():
    audits = guards.audit_package()
    assert len(audits) == 5


def test_all_five_shipped_classes_are_clean():
    audits = guards.audit_package()
    dirty = [audit for audit in audits if audit.violations]
    assert dirty == []


def test_discovery_matches_the_enablement_registry_not_a_hardcoded_list():
    # audit_package() never reads enablement.py - it discovers repair
    # classes structurally (every module that constructs a Repair).
    # This test only cross-checks the two independent sources agree,
    # proving discovery is not a list someone forgot to update.
    discovered = {audit.name.rsplit(".", 1)[-1] for audit in guards.audit_package()}
    assert discovered == set(enablement.REPAIR_CLASSES)


def test_repair_without_a_preceding_permitted_call_is_flagged():
    audit = guards.audit_source("rogue_no_permitted", _NO_PERMITTED_CHECK_SOURCE)
    assert audit.violations
    assert any("permitted" in v for v in audit.violations)


def test_secret_write_call_is_flagged_even_with_permitted_called():
    audit = guards.audit_source("rogue_secret_write", _SECRET_WRITE_SOURCE)
    assert audit.violations
    assert any("actions_secret_write" in v for v in audit.violations)


def test_records_write_call_is_flagged_even_with_permitted_called():
    audit = guards.audit_source("rogue_records_write", _RECORDS_WRITE_SOURCE)
    assert audit.violations
    assert any("records_write" in v for v in audit.violations)
