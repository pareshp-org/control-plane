#!/usr/bin/env python3
"""Check the repository-side half of the two Section 40.3 trust boundaries.

Section 40.3 lines 3695-3704; D95 line 10188; Section 51.5 line 4502.

Phases:
  --phase declare   run only the assertions whose inputs exist once T09 lands
  --phase complete  run every assertion (the default; used by the T14 gate)

The phase is always printed, because a checker that passes silently only
because its target file does not exist yet is the failure this whole file
exists to prevent.

Fail-closed (invariant 80): a missing boundary declaration is exit 2.

Usage:  check_boundaries.py [--phase declare|complete]
Exit 0 all assertions hold, 1 an assertion fails, 2 input fault.
"""
import glob
import os
import sys

import yaml

B1 = os.path.join("access", "secrets", "boundaries", "boundary-1-production.yaml")
B2 = os.path.join("access", "secrets", "boundaries", "boundary-2-control-plane.yaml")
TIERS = os.path.join("access", "secrets", "tiers")
FIFTH = os.path.join("access", "secrets", "fifth-tier")
STORE = os.path.join("access", "secrets", "host", "credential-store.yaml")
GATE = os.path.join("infra", "network", "ops-vm-shell-gate.yaml")
SEP = os.path.join("access", "secrets", "separation", "separation.result.yaml")
WORKSTATION_MARKERS = ("laptop", "workstation", "macbook", "desktop", "dev-machine")
LEAK_MARKERS = ("BEGIN OPENSSH PRIVATE KEY", "BEGIN RSA PRIVATE KEY",
                "BEGIN EC PRIVATE KEY", "ghp_", "github_pat_", "ghs_")
SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv", "venv"}


def load(path):
    with open(path, "r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def main(argv):
    phase = "complete"
    if "--phase" in argv:
        idx = argv.index("--phase")
        if idx + 1 >= len(argv):
            print("RESULT FAIL usage --phase declare|complete")
            return 2
        phase = argv[idx + 1]
    if phase not in ("declare", "complete"):
        print("RESULT FAIL unknown-phase %s" % phase)
        return 2
    for path in (B1, B2):
        if not os.path.isfile(path):
            print("RESULT FAIL boundary-declaration-missing %s" % path)
            return 2
    b1 = load(B1)
    b2 = load(B2)
    if not b1.get("statement") or not b2.get("statement"):
        print("RESULT FAIL boundary-without-statement")
        return 2

    results = []

    # B1-A2 - exactly one tier holds production credentials, and it is production.
    holders = []
    for path in sorted(glob.glob(os.path.join(TIERS, "*.yaml"))):
        doc = load(path)
        if doc.get("holds_production_credentials"):
            holders.append(doc.get("tier_id"))
    results.append(("B1-A2", holders == ["production"],
                    "tiers holding production credentials: %r" % holders))

    # B2-A2 - no private key block and no token prefix under access/ or infra/.
    leaks = []
    for root in ("access", "infra"):
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
            for filename in filenames:
                full = os.path.join(dirpath, filename)
                if os.path.abspath(full) == os.path.abspath(__file__):
                    continue          # this file names the markers it hunts for
                try:
                    with open(full, "r", encoding="utf-8", errors="ignore") as handle:
                        body = handle.read()
                except Exception:
                    continue
                for marker in LEAK_MARKERS:
                    if marker in body:
                        leaks.append("%s (%s)" % (full, marker))
    results.append(("B2-A2", not leaks, "leaks: %r" % leaks))

    if phase == "complete":
        # B1-A3 / B2-A1 - no fifth-tier credential is expected on a workstation.
        bad_hosts = []
        entries = sorted(glob.glob(os.path.join(FIFTH, "*.yaml")))
        if not entries:
            results.append(("B1-A3", False, "no fifth-tier entries found"))
            results.append(("B2-A1", False, "no fifth-tier entries found"))
        else:
            for path in entries:
                host = str(load(path).get("host") or "").lower()
                if not host:
                    bad_hosts.append("%s: empty host" % path)
                for marker in WORKSTATION_MARKERS:
                    if marker in host:
                        bad_hosts.append("%s: host %r looks like a workstation"
                                         % (path, host))
            results.append(("B1-A3", not bad_hosts, "bad hosts: %r" % bad_hosts))
            results.append(("B2-A1", not bad_hosts, "bad hosts: %r" % bad_hosts))

        # B2-A3 - the credential store does not passively yield to root.
        if not os.path.isfile(STORE):
            results.append(("B2-A3", False, "%s absent (built by L5-02-10)" % STORE))
        else:
            store = load(STORE)
            results.append(("B2-A3", store.get("passive_root_read") is False,
                            "passive_root_read=%r" % store.get("passive_root_read")))

        # B2-A4 - the shell gate requires a hardware-backed second factor.
        if not os.path.isfile(GATE):
            results.append(("B2-A4", False, "%s absent (built by L5-02-10)" % GATE))
        else:
            gate = load(GATE)
            second = gate.get("second_factor") or {}
            sshd = gate.get("sshd_required_settings") or {}
            ok = (bool(second.get("key_types_allowed"))
                  and all(str(k).startswith("sk-")
                          for k in second.get("key_types_allowed"))
                  and str(sshd.get("PasswordAuthentication")) == "no"
                  and gate.get("private_network_path_required") is True)
            results.append(("B2-A4", ok,
                            "key_types=%r PasswordAuthentication=%r private_path=%r"
                            % (second.get("key_types_allowed"),
                               sshd.get("PasswordAuthentication"),
                               gate.get("private_network_path_required"))))

        # B2-A5 - separation resolved, one way or the other.
        if not os.path.isfile(SEP):
            results.append(("B2-A5", False, "%s absent (built by L5-02-11)" % SEP))
        else:
            sep = load(SEP)
            state = str(sep.get("state") or "")
            if state == "separated":
                results.append(("B2-A5", True, "state=separated"))
            elif state == "accepted-risk":
                ok = bool(str(sep.get("holder") or "").strip()) \
                    and bool(str(sep.get("compensating_control") or "").strip()) \
                    and bool(str(sep.get("review_date") or "").strip())
                results.append(("B2-A5", ok, "state=accepted-risk holder=%r review=%r"
                                % (sep.get("holder"), sep.get("review_date"))))
            else:
                results.append(("B2-A5", False, "state=%r" % state))

    print("PHASE %s" % phase)
    failed = 0
    for name, ok, detail in results:
        print("ASSERTION %s %s %s" % (name, "OK" if ok else "FAIL", detail if not ok else ""))
        if not ok:
            failed += 1
    print("ASSERTIONS %d" % len(results))
    print("FAILED %d" % failed)
    if failed:
        print("RESULT FAIL")
        return 1
    print("RESULT PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
