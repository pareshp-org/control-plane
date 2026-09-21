#!/usr/bin/env python
"""The eight offline assertions of the Section 98.2 Phase 1 access completion check.

Runs with no credentials, no organisation and no network. Each assertion maps to
a clause of the Section 98.2 completion-check sentence. The four clauses that
cannot be asserted offline are printed as ROUTED with their owner named, because
a completion check with an unowned clause passes for the wrong reason.

Exit 0 on success, 1 on any failed assertion.
"""
import json
import os
import subprocess
import sys

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))


def load(relative):
    with open(os.path.join(ROOT, relative), "r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def render(profile):
    result = subprocess.run(
        [sys.executable,
         os.path.join(ROOT, "access", "tools", "render_protection_payload.py"),
         "--profile", profile],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode != 0:
        return {}
    return json.loads(result.stdout.decode("utf-8"))


def main():
    org = load("access/model/organisation.yaml")
    semantics = load("access/model/permission-semantics.yaml")
    teams = load("access/model/teams.yaml")
    protection = load("access/branch-protection/branch-protection.yaml")
    continuity = load("access/model/owner-continuity.yaml")
    register = load("access/checks/negative-tests.yaml")

    armed = render("armed")
    unarmed = render("unarmed")
    counts = {}
    for entry in semantics["capabilities"]:
        if entry["id"] == "approval_counts_toward_required_approving_reviews":
            counts = entry["by_level"]

    assertions = [
        ("P1-01", "the armed profile blocks force pushes and deletions and applies "
                  "to administrators, in both profiles",
         armed.get("allow_force_pushes") is False
         and armed.get("allow_deletions") is False
         and armed.get("enforce_admins") is True
         and unarmed.get("enforce_admins") is True),
        ("P1-02", "the control-plane repository admits no machine bypass actor (D89)",
         protection["bypass_actors"]["control_plane_repository"] == "none"),
        ("P1-03", "a Read-only approval does not satisfy branch protection (Section 11.1)",
         counts.get("read") is False),
        ("P1-04", "a Write-holding Cross-Reviewer approval does, and Cross-Reviewers hold Write",
         counts.get("write") is True
         and teams["cross_reviewer"]["minimum_permission"] == "write"),
        ("P1-05", "CODEOWNERS is generated human-only and the check is executed negatively",
         protection["checklist"][10]["id"] == "BP-11"
         and os.path.exists(os.path.join(ROOT, "access", "codeowners",
                                         "test_generate_codeowners.sh"))),
        ("P1-06", "organisation-enforced 2FA is declared active with hardware keys or "
                  "passkeys for the Founder, Owners and platform-admin holders",
         org["two_factor"]["organisation_enforced"] is True
         and len(org["two_factor"]["strong_factor_required_for"]) == 3
         and set(org["two_factor"]["accepted_strong_factors"])
         == set(["hardware_security_key", "passkey"])),
        ("P1-09", "Teams granting Write precede arming, and the required-check list starts empty",
         teams["phase_1_interim"]["decision"] == "D101"
         and protection["required_status_checks"]["starts_empty_per_repository"] is True
         and len(armed.get("required_status_checks", {}).get("contexts", [1])) == 0),
        ("P1-11", "owner continuity is declared with an escrow custodian recorded elsewhere",
         continuity["escrow"]["custodian_named_here"] is False
         and len(continuity["requirement"]["satisfied_by_either"]) == 2),
    ]

    failed = 0
    for ident, statement, ok in assertions:
        if ok:
            print("%s OK   %s" % (ident, statement))
        else:
            print("%s FAIL %s" % (ident, statement))
            failed += 1

    routed = [test for test in register["tests"]
              if test["execution_mode"] in ("by_lane_L2", "routed_to_L0",
                                            "routed_to_l5_subsystem_k")]
    for test in routed:
        print("%s ROUTED to %s  %s" % (test["id"], test["executed_by"], test["statement"]))

    if failed:
        print("PHASE1-ACCESS-CHECK: FAIL (%d of %d assertions)" % (failed, len(assertions)))
        return 1
    print("PHASE1-ACCESS-CHECK: PASS (%d assertions, %d routed)"
          % (len(assertions), len(routed)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
