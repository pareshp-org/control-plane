# access/secrets — the five secret tiers and the two trust boundaries

Spec: Section 40 (Secrets and Production Access), lines 3644-3704 of
Research/MultiProduct_MasterSpec_v4.0.md.

This tree is DECLARATION plus CHECKS. It holds no secret value, no credential
handle and no host address that is not already public configuration. Nothing
here is provisioned by this tree: Lane 5 phase 4 provisions the fifth-tier
store on the operations VM, Lane 2 executes the checks in CI, Lane 3 reconciles
declared state against actual state.

Layout:

  tiers/       one file per secret tier (five files, Section 40.1)
  fifth-tier/  one file per control-plane machine credential (five files)
  envelope/    the behavioural envelope per credential, plus its evaluator (D96)
  runbooks/    the one-page rotation runbook and the rotation record shape
  checks/      the executable boundary and hygiene checks
  boundaries/  the two Section 40.3 trust boundaries, declared and checkable
  separation/  rotator / host-root separation, or the recorded accepted risk
  host/        what the operations VM must do with the fifth tier (D95)
  incident/    the Section 43.4 containment hook
  gate/        the phase exit gate
  testdata/    fixtures, including every negative test this phase executes

Two rules govern every file here.

1. A secret never moves down a tier. A production credential appearing anywhere
   below the production tier is a security incident under Section 43, not a
   cleanup task (Section 40.1, line 3656).
2. Every control in this tree carries exactly one classification, fail-closed or
   fail-open, in access/fail-closed/ (Section 64.2, invariant 80). Where a check
   cannot read its input it fails closed: it reports a failure, never a pass.
