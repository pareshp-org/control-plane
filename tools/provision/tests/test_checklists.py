"""L3-P4-08: CONFIGURE checklist and manual-step issue emitter."""

from __future__ import annotations

import pytest

from tools.provision.checklists import (
    BUDGET_BAND_NOTE,
    CONFIGURE_ITEMS,
    CREATE_PRODUCT_MANUAL_STEPS,
    ManualStep,
    PostingRefused,
    configure_checklist,
    manual_step_issue,
    manual_step_issues,
    post_issue,
)


def test_configure_checklist_has_exactly_seven_items_verbatim():
    assert CONFIGURE_ITEMS == (
        "environments",
        "verification contract",
        "observability",
        "backups",
        "classification",
        "budget band",
        "support intake",
    )
    body = configure_checklist("alpha")
    for item in CONFIGURE_ITEMS:
        assert f"- [ ] {item}" in body or item in body
    assert body.count("- [ ] ") == 7


def test_configure_checklist_budget_band_note_is_verbatim():
    body = configure_checklist("alpha")
    assert BUDGET_BAND_NOTE in body
    assert "budget band" in body


def test_two_manual_step_issues_rendered_for_create_product_plan():
    steps = [
        ManualStep(id="alert_channel", description="Create the alert channel."),
        ManualStep(id="support_intake_mailbox", description="Create the support intake mailbox."),
    ]
    assert [s.id for s in steps] == list(CREATE_PRODUCT_MANUAL_STEPS)
    issues = manual_step_issues(steps)
    assert len(issues) == 2
    assert "alert_channel" in issues[0]
    assert "support_intake_mailbox" in issues[1]


def test_manual_step_issue_names_step_id_and_description():
    step = ManualStep(id="alert_channel", description="Create the #alpha-alerts channel.")
    body = manual_step_issue(step)
    assert "alert_channel" in body
    assert "Create the #alpha-alerts channel." in body


def test_post_issue_refused_without_both_apply_and_live():
    with pytest.raises(PostingRefused):
        post_issue("body", apply=False, live=False)
    with pytest.raises(PostingRefused):
        post_issue("body", apply=True, live=False)
    with pytest.raises(PostingRefused):
        post_issue("body", apply=False, live=True)
