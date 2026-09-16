# Rotate a fifth-tier machine credential

Section 40.1 line 3683. One page. Applies to all five control-plane machine
credentials without variation. Cadence: quarterly (calibrated configuration,
initial value). On a workstation compromise this runbook is executed for ALL
five credentials as a named step (Section 43.4; access/secrets/incident/).

Inputs: the credential id, its entry in access/secrets/fifth-tier/, its envelope
in access/secrets/envelope/. Actor: the entry's named `rotator`.

STEP-01 Confirm you are the named rotator for this credential and that you hold
the DevOps capability. If you are not, stop; a rotation by anyone else is not a
rotation, it is an unrecorded credential change.

STEP-02 Open the rotation record from
access/secrets/runbooks/rotation-record.template.yaml. Fill rotation_id,
credential_id, rotator and rotated_at before touching the credential. State is
`in-progress` until the gate of L5-02-08 permits `done`.

STEP-03 If this rotation follows a suspected compromise, capture evidence FIRST:
logs, audit records, artifact digests, access history. Section 43.1 - "Do not
delete. Do not force-push. Do not rotate before capturing."

STEP-04 Issue the replacement with EXACTLY the permission set published in the
credential's fifth-tier entry. Do not widen it "while you are in there". A
widened permission set is drift the moment it is issued.

STEP-05 Install the replacement into the fifth-tier store on the credential's
expected source host, under the separate OS user or secret agent declared in
access/secrets/host/credential-store.yaml. Never onto a workstation.

STEP-06 BLOCKING - Re-escrow. Deposit the replacement with the Section 14.4
escrow custodian and record the confirmation in the rotation record. Section
14.4 line 1266: a rotation is not recordable as done until the replacement is
escrowed. Re-escrow the encryption key too where the credential has one.

STEP-07 BLOCKING - Run a manual reconciliation run to completion. It must
complete CLEAN. Section 40.1: a credential that rotates but no longer
reconciles has not been rotated, it has been broken. Record the run id and its
result in the rotation record.

STEP-08 BLOCKING - Re-execute AT-110. Six attempts from the credential itself -
a GitHub Actions secret write, an environment write, a workflow-file change, an
organisation-settings change, a records/** write, and any Layer B access - and
all six must FAIL; the credential must then still complete a normal
reconciliation run. Record executed_at, result and attempts_failed.

STEP-09 Revoke the superseded credential and confirm the revocation. Until this
step both credentials authenticate, and the envelope's run-count ceiling is the
only thing standing between you and an unnoticed second user.

STEP-10 Run the rotation-completion gate:
  bash access/secrets/checks/rotation-complete.sh <rotation-record.yaml>
Only when it prints ROTATION-DONE-PERMITTED may the record be set to `done`.
If the schedule changed as part of this rotation, re-run
access/secrets/tools/emit_envelopes.py so the run-count ceiling is recalibrated,
and commit the regenerated envelope.

If any blocking step above fails: the rotation is NOT done. The credential is
broken, not rotated. Restore the previous credential from the Section 14.4
escrow, leave the rotation record at `in-progress`, and file a blocker.
