#!/usr/bin/env python3
"""Evaluate fifth-tier credential runs against their behavioural envelopes.

Section 40.1 line 3685; D96 line 10189. A run outside the envelope is Blocking
drift on the single severity scale of Section 53.4.

Clauses, all Blocking:
  E1 unmatched-trigger        the run names a trigger with no trigger record
  E2 run-count-ceiling        more runs in one day than 2 x scheduled runs
  E3 unexpected-source-host   source_host is not the expected source host
  E4 missing-api-call-count   the run publishes no per-run API-call count
  E5 unsigned-run-record      signature or signer is empty

Fail-closed (invariant 80): an unreadable envelope, run record or trigger
record is exit 2. A directory that exists and is empty of runs is NOT a pass by
default - see --allow-empty-runs, which the scheduled caller never passes.

Usage:
  evaluate_envelope.py <envelope-dir> <runs-dir> <triggers-dir> [--allow-empty-runs]

Exit 0 clean, 1 one or more Blocking findings, 2 input fault.
"""
import glob
import os
import sys

import yaml


def load_dir(path, label, errors):
    docs = []
    if not os.path.isdir(path):
        errors.append("%s-dir-missing %s" % (label, path))
        return docs
    for name in sorted(os.listdir(path)):
        if not (name.endswith(".yaml") or name.endswith(".yml")):
            continue
        full = os.path.join(path, name)
        try:
            with open(full, "r", encoding="utf-8") as handle:
                doc = yaml.safe_load(handle)
        except Exception as exc:                                # fail closed
            errors.append("%s-unparseable %s (%s)" % (label, full, exc))
            continue
        if not isinstance(doc, dict):
            errors.append("%s-not-a-mapping %s" % (label, full))
            continue
        doc["__path"] = full
        docs.append(doc)
    return docs


def day_of(value):
    return str(value)[:10]


def main(argv):
    args = [a for a in argv[1:] if not a.startswith("--")]
    flags = set(a for a in argv[1:] if a.startswith("--"))
    if len(args) != 3:
        print("RESULT FAIL usage evaluate_envelope.py <envelope-dir> <runs-dir> <triggers-dir>")
        return 2
    env_dir, runs_dir, trig_dir = args
    errors = []
    envelopes = load_dir(env_dir, "envelope", errors)
    runs = load_dir(runs_dir, "run", errors)
    triggers = load_dir(trig_dir, "trigger", errors)
    if errors:
        for line in errors:
            print("INPUT-FAULT %s" % line)
        print("RESULT FAIL input-fault")
        return 2
    if not envelopes:
        print("RESULT FAIL no-envelopes %s" % env_dir)
        return 2
    if not runs and "--allow-empty-runs" not in flags:
        print("RESULT FAIL no-run-records %s" % runs_dir)
        return 2

    by_cred = {}
    for env in envelopes:
        cred = env.get("credential_id")
        if not cred:
            print("RESULT FAIL envelope-without-credential_id %s" % env["__path"])
            return 2
        by_cred[cred] = env
    trigger_ids = set()
    for trig in triggers:
        tid = trig.get("trigger_id")
        cred = trig.get("credential_id")
        if tid and cred:
            trigger_ids.add((str(cred), str(tid)))

    findings = []
    counts = {}
    for run in sorted(runs, key=lambda r: str(r.get("run_id"))):
        cred = str(run.get("credential_id") or "")
        run_id = str(run.get("run_id") or os.path.basename(run["__path"]))
        env = by_cred.get(cred)
        if env is None:
            findings.append(("E0", cred, run_id, "no envelope declared for this credential"))
            continue
        trigger = str(run.get("scheduled_trigger") or "")
        if not trigger or (cred, trigger) not in trigger_ids:
            findings.append(("E1", cred, run_id,
                             "scheduled_trigger %r matches no trigger record" % trigger))
        host = str(run.get("source_host") or "")
        expected = str(env["expected_source_host"]["value"])
        if host != expected:
            findings.append(("E3", cred, run_id,
                             "source_host %r is not the expected source host %r"
                             % (host, expected)))
        if run.get("api_call_count") is None:
            findings.append(("E4", cred, run_id,
                             "no api_call_count published for this run"))
        if not str(run.get("signature") or "").strip() \
           or not str(run.get("signer") or "").strip():
            findings.append(("E5", cred, run_id, "run record is not signed"))
        counts.setdefault((cred, day_of(run.get("started_at"))), []).append(run_id)

    for (cred, day), run_ids in sorted(counts.items()):
        ceiling = int(by_cred[cred]["run_count_ceiling_per_day"]["value"])
        if len(run_ids) > ceiling:
            findings.append(("E2", cred, day,
                             "%d runs on %s exceeds the ceiling of %d"
                             % (len(run_ids), day, ceiling)))

    for clause, cred, subject, detail in sorted(findings):
        print("DRIFT Blocking %s %s %s - %s" % (clause, cred, subject, detail))
    print("FINDINGS %d" % len(findings))
    if findings:
        print("CLASS Blocking")
        print("SCALE Section 53.4")
        print("RESULT FAIL")
        return 1
    print("RESULT PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
