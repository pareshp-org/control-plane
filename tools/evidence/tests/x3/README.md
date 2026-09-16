X3 — the workflow_dispatch harness.

X3 dispatches the REAL reusable workflows at synthetic product repositories in
the sandbox organisation, and asserts three things about each run:

  1. the run conclusion is `failure`, not `success` and not `skipped`
  2. the failing step's log carries the gate's own token
  3. no environment secret was materialised into the job

Point 2 is why X3 is not just "the run went red": a run that fails for the wrong
reason is a green gate wearing a red badge.

BLOCKED: D-L2-11. FD-021 (2026-09-02) decided the sandbox-org question (option
A: one Team-tier organisation, shared with L3-04's $PROVISION_SANDBOX_ORG), but
no contracts/** file yet publishes the resolved sandbox_org_slug,
sandbox_dispatch_secret_name or fixture_repo_prefix values. Every gate whose
tier is X3 therefore still reports UNARMED under rule S10 and is RED until L0
publishes those three keys in contracts/**. An unarmed gate is never reported
as passing and never deleted - protocol/00-test-strategy.md section 0 quotes
Section 99.6 risk 5: "An unavailable protection feature reproduces the
silent-gate failure."
