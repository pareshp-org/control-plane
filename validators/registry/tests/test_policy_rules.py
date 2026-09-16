"""Tests for R-POL-01..04, the Section 55.3 policy stage-ladder rules
(L1-604).

Exercises the rule functions directly against the fixtures in
validators/registry/fixtures/pol/, rather than the L1-005
discover()/RULE_ID/APPLIES_TO harness or the CLI "OK: N file(s)
validated" / "ERROR <rule>" grammar in lanes/L1-05-tasks.md's L1-604
ACCEPTANCE table and literal SELF-VERIFY block -- FD-094 (DECIDED)
supersedes that harness and grammar in favour of Option B
(validators/registry/cli.py, R01-R18). This mirrors the adaptation
already made for L1-404 (test_service_schema.py), L1-606
(test_tools_schema.py) and L1-603 (test_policies_schema.py). The four
rule modules (r_pol_01..04.py) are standalone functions, not wired
into the frozen R01-R18 dispatch table -- see r_pol_01.py's module
docstring for why extending that frozen catalogue is out of scope here.

18 test functions, matching the task's own case table: 8 valid + 10
invalid.

One deviation from the task's literal fixture plan, required to
implement it faithfully rather than force an impossible fixture: the
invalid-case table names `all_four_fire/` as "one policy violating all
four" rules. Under the condition table above (also given verbatim in
this task and reproduced in each rule module's docstring), R-POL-01 and
R-POL-03 require `enforcement_stage == enforce`; R-POL-02 requires
`enforcement_stage == pilot`; R-POL-04 never fires at `enforce` (only
`warn`/`pilot`). `enforcement_stage` is a single scalar field, so no one
policy entry can simultaneously be `enforce` (for R-POL-01/03) and
`pilot` (for R-POL-02 and R-POL-04's pilot branch) -- all four rules
firing on one policy is impossible by the rules' own stated conditions,
not a bug in this implementation. `all_four_fire/policies.yaml` instead
carries two policy entries -- one at `enforce` violating R-POL-01 and
R-POL-03, one at `pilot` violating R-POL-02 and R-POL-04 -- for four
total findings from the one fixture file, which is the part of the
case ("four errors") this test can faithfully assert.
"""
import datetime
import os

import yaml

from validators.registry.rules import r_pol_01, r_pol_02, r_pol_03, r_pol_04

FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "..", "fixtures", "pol")
TODAY = datetime.date(2026, 8, 27)


def _load(case):
    path = os.path.join(FIXTURES_DIR, case, "policies.yaml")
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def _all_findings(doc):
    findings = []
    for mod in (r_pol_01, r_pol_02, r_pol_03):
        _, mod_findings = mod.check_document(doc)
        findings.extend(mod_findings)
    _, dwell_findings = r_pol_04.check_document(doc, TODAY)
    findings.extend(dwell_findings)
    return findings


# ---------------------------------------------------------------------------
# valid (8)
# ---------------------------------------------------------------------------


def test_valid_enforce_with_window():
    doc = _load(os.path.join("valid", "enforce_with_window"))
    assert _all_findings(doc) == []


def test_valid_enforce_direct_with_justification():
    doc = _load(os.path.join("valid", "enforce_direct_with_justification"))
    policy = doc["policies"][0]
    assert policy["entered_at_enforce_directly"] is True
    assert policy["justification"]
    assert _all_findings(doc) == []


def test_valid_pilot_with_products():
    doc = _load(os.path.join("valid", "pilot_with_products"))
    assert doc["policies"][0]["pilot_products"] == ["product-1"]
    assert _all_findings(doc) == []


def test_valid_warn_after_dwell():
    doc = _load(os.path.join("valid", "warn_after_dwell"))
    policy = doc["policies"][0]
    elapsed = (TODAY - datetime.date.fromisoformat(policy["effective_date"])).days
    assert elapsed >= policy["min_dwell"]["warn"]
    assert _all_findings(doc) == []


def test_valid_at027_new_policy_no_product_edit():
    """AT-027 (Lane 1 half): a new platform policy flows from a one-entry
    policies.yaml with no product.yaml edit required."""
    doc = _load(os.path.join("valid", "at027_new_policy_no_product_edit"))
    assert len(doc["policies"]) == 1
    assert _all_findings(doc) == []


def test_at027_product_bytes_identical():
    """AT-027 (Lane 1 half), continued: a second, otherwise-identical case
    whose policies.yaml carries two entries has a byte-identical
    product.yaml to the one-entry case -- introducing a platform policy
    never touches product.yaml."""
    doc = _load(os.path.join("valid", "at027_two_policies_same_product"))
    assert len(doc["policies"]) == 2
    assert _all_findings(doc) == []

    one_entry_product = os.path.join(
        FIXTURES_DIR, "valid", "at027_new_policy_no_product_edit", "product.yaml"
    )
    two_entry_product = os.path.join(
        FIXTURES_DIR, "valid", "at027_two_policies_same_product", "product.yaml"
    )
    with open(one_entry_product, "rb") as f:
        digest_one = f.read()
    with open(two_entry_product, "rb") as f:
        digest_two = f.read()
    assert digest_one == digest_two


def test_valid_retired_policy():
    """A retired policy at Pilot with no pilot_products is not "in force"
    (Section 55.3's ladder governs a policy that is) -- all four rules
    are silent."""
    doc = _load(os.path.join("valid", "retired_policy"))
    policy = doc["policies"][0]
    assert policy["status"] == "retired"
    assert policy["pilot_products"] == []
    assert _all_findings(doc) == []


def test_valid_withdrawn_policy():
    doc = _load(os.path.join("valid", "withdrawn_policy"))
    assert doc["policies"][0]["status"] == "withdrawn"
    assert _all_findings(doc) == []


# ---------------------------------------------------------------------------
# invalid (10)
# ---------------------------------------------------------------------------


def test_enforce_direct_no_justification():
    doc = _load("enforce_direct_no_justification")
    findings = _all_findings(doc)
    assert len(findings) == 1
    assert findings[0].startswith("R-POL-01")
    assert "entered directly at Enforce with no justification" in findings[0]


def test_enforce_direct_justification_empty():
    doc = _load("enforce_direct_justification_empty")
    findings = _all_findings(doc)
    assert len(findings) == 1
    assert findings[0].startswith("R-POL-01")


def test_pilot_no_products():
    doc = _load("pilot_no_products")
    findings = _all_findings(doc)
    assert len(findings) == 1
    assert findings[0].startswith("R-POL-02")
    assert "names no pilot_products" in findings[0]


def test_enforce_no_window():
    doc = _load("enforce_no_window")
    findings = _all_findings(doc)
    assert len(findings) == 1
    assert findings[0].startswith("R-POL-03")
    assert "names no exception_window_closes" in findings[0]


def test_warn_dwell_not_elapsed():
    doc = _load("warn_dwell_not_elapsed")
    findings = _all_findings(doc)
    assert len(findings) == 1
    assert findings[0].startswith("R-POL-04")
    assert "'warn' 3 days after its effective_date" in findings[0]
    assert "min_dwell for that stage is 14 days" in findings[0]


def test_pilot_dwell_not_elapsed():
    doc = _load("pilot_dwell_not_elapsed")
    findings = _all_findings(doc)
    assert len(findings) == 1
    assert findings[0].startswith("R-POL-04")
    assert "'pilot' 0 days after its effective_date" in findings[0]
    assert "min_dwell for that stage is 1 days" in findings[0]


def test_direct_enforce_and_no_window():
    doc = _load("direct_enforce_and_no_window")
    findings = _all_findings(doc)
    assert len(findings) == 2
    rule_ids = sorted(f.split(" ", 1)[0] for f in findings)
    assert rule_ids == ["R-POL-01", "R-POL-03"]


def test_pilot_no_products_and_dwell_short():
    doc = _load("pilot_no_products_and_dwell_short")
    findings = _all_findings(doc)
    assert len(findings) == 2
    rule_ids = sorted(f.split(" ", 1)[0] for f in findings)
    assert rule_ids == ["R-POL-02", "R-POL-04"]


def test_all_four_fire():
    """See this module's docstring for why this fixture carries two policy
    entries rather than the task's literal "one policy" framing -- one
    policy cannot be simultaneously at `enforce` (for R-POL-01/03) and
    `pilot` (for R-POL-02/04)."""
    doc = _load("all_four_fire")
    assert len(doc["policies"]) == 2
    findings = _all_findings(doc)
    assert len(findings) == 4
    rule_ids = sorted(f.split(" ", 1)[0] for f in findings)
    assert rule_ids == ["R-POL-01", "R-POL-02", "R-POL-03", "R-POL-04"]


def test_two_policies_two_offenders():
    doc = _load("two_policies_two_offenders")
    assert len(doc["policies"]) == 2
    findings = _all_findings(doc)
    assert len(findings) == 2
    rule_ids = sorted(f.split(" ", 1)[0] for f in findings)
    assert rule_ids == ["R-POL-02", "R-POL-03"]
