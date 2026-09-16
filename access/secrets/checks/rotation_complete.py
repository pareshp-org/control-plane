#!/usr/bin/env python3
"""The rotation-completion gate.

Section 40.1 line 3683: after any rotation a manual reconciliation run must
complete clean before the rotation is recorded as done - "a credential that
rotates but no longer reconciles has not been rotated, it has been broken."
AT-110 lines 9438-9439: re-executed at every rotation, on the same gate.
Section 14.4 line 1266: re-escrow is a blocking step; a rotation is not
recordable as done until the replacement is escrowed.

Fail-closed (invariant 80): an unreadable or malformed record is exit 2.

Usage: rotation_complete.py <rotation-record.yaml>
Exit 0 done permitted, 1 not done, 2 input fault.
"""
import os
import sys

import yaml

STAMP_LEN = 20   # YYYY-MM-DDTHH:MM:SSZ


def stamp_ok(value):
    text = str(value or "")
    return len(text) == STAMP_LEN and text.endswith("Z") and text[10] == "T"


def main(argv):
    if len(argv) != 2:
        print("RESULT FAIL usage rotation_complete.py <rotation-record.yaml>")
        return 2
    path = argv[1]
    if not os.path.isfile(path):
        print("RESULT FAIL record-unreadable %s" % path)
        return 2
    try:
        with open(path, "r", encoding="utf-8") as handle:
            rec = yaml.safe_load(handle) or {}
    except Exception as exc:                                    # fail closed
        print("RESULT FAIL record-unparseable %s" % exc)
        return 2
    if not isinstance(rec, dict):
        print("RESULT FAIL record-not-a-mapping %s" % path)
        return 2
    for key in ("rotation_id", "credential_id", "rotator", "rotated_at",
                "reconciliation", "at110", "re_escrow"):
        if key not in rec:
            print("RESULT FAIL record-missing-key %s" % key)
            return 2
    rotated_at = str(rec.get("rotated_at") or "")
    if not stamp_ok(rotated_at):
        print("RESULT FAIL bad-rotated_at %r" % rotated_at)
        return 2

    blocked = []
    recon = rec.get("reconciliation") or {}
    if str(recon.get("result") or "") != "clean":
        blocked.append("G1 reconciliation.result is %r, not 'clean' - the credential is broken, not rotated"
                       % recon.get("result"))
    elif not stamp_ok(recon.get("completed_at")):
        blocked.append("G1 reconciliation.completed_at is not a UTC stamp")
    elif str(recon.get("completed_at")) < rotated_at:
        blocked.append("G1 reconciliation completed BEFORE the rotation (%s < %s)"
                       % (recon.get("completed_at"), rotated_at))

    at110 = rec.get("at110") or {}
    if str(at110.get("result") or "") != "pass":
        blocked.append("G2 at110.result is %r, not 'pass'" % at110.get("result"))
    elif int(at110.get("attempts_failed") or 0) != 6:
        blocked.append("G2 at110.attempts_failed is %r; AT-110 makes six attempts and all six must fail"
                       % at110.get("attempts_failed"))
    elif not stamp_ok(at110.get("executed_at")):
        blocked.append("G2 at110.executed_at is not a UTC stamp")
    elif str(at110.get("executed_at")) < rotated_at:
        blocked.append("G2 AT-110 was executed BEFORE this rotation (%s < %s) - it must be RE-executed"
                       % (at110.get("executed_at"), rotated_at))

    escrow = rec.get("re_escrow") or {}
    if escrow.get("confirmed") is not True:
        blocked.append("G3 re_escrow.confirmed is not true - Section 14.4 line 1266")
    elif not str(escrow.get("custodian") or "").strip():
        blocked.append("G3 re_escrow.custodian is empty - the escrow has a named custodian")
    elif not stamp_ok(escrow.get("confirmed_at")):
        blocked.append("G3 re_escrow.confirmed_at is not a UTC stamp")
    elif str(escrow.get("confirmed_at")) < rotated_at:
        blocked.append("G3 re-escrow was confirmed BEFORE the rotation (%s < %s)"
                       % (escrow.get("confirmed_at"), rotated_at))

    for line in blocked:
        print("BLOCKED %s" % line)
    print("GATES-BLOCKED %d" % len(blocked))
    if blocked:
        print("ROTATION-NOT-DONE")
        print("RESULT FAIL")
        return 1
    print("ROTATION-DONE-PERMITTED")
    print("RESULT PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
