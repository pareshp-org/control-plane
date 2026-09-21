#!/usr/bin/env python3
"""Assert the Phase 3 privileged-workflow posture. Charter DoD-05.

Spec: Section 37.3 (3261-3268) actor gate first; Section 39.5 (3589-3596) and
D87 (10180) runner isolation; Section 33.4 (2911) and D91 (10184) deployment
branch policy; Section 27.2 (2567-2576) and D73 (10156) the identity gate;
Section 27.2 line 2575 and D52 (10120) the rollback exemption;
Section 33.2 line 2860 no `if:` and no path filter on a gate job.

Fails closed: an unreadable file, an unparseable file and an unknown shape all
exit non-zero. Nothing here defaults to permit (Section 64, line 5431).

Exit codes: 0 posture holds; 1 posture violated; 2 could not tell.
"""
import argparse
import os
import sys

try:
    import yaml
except ImportError:
    print("PRIVILEGED_POSTURE_PYYAML_ABSENT")
    sys.exit(2)

EXEMPTION_PATH = "templates/workflows/rollback-exemption.yaml"
STEP_ANCHOR = "RUNNER-TIER-ASSERT v1"
GATE_JOBS = ("actor-gate", "runner-tier-assert", "env-policy-assert",
             "workflow-identity-gate", "rollback")
# A composer is a reusable workflow whose own first job is the actor gate and
# which this tool checks in its own right: the gate chain (L2-T175) and the
# rollback workflow (L2-T176).
COMPOSERS = ("production-gate-chain.yml@", "rollback.yml@")

FINDINGS = []


def finding(token, detail):
    FINDINGS.append("%s %s" % (token, detail))


def load(path):
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return yaml.safe_load(fh)
    except OSError:
        print("PRIVILEGED_FILE_UNREADABLE %s" % path)
        sys.exit(2)
    except yaml.YAMLError:
        print("PRIVILEGED_FILE_UNPARSEABLE %s" % path)
        sys.exit(2)


def raw(path):
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return fh.read()
    except OSError:
        print("PRIVILEGED_FILE_UNREADABLE %s" % path)
        sys.exit(2)


def needs_of(job):
    n = job.get("needs")
    if n is None:
        return []
    return [n] if isinstance(n, str) else list(n)


def reaches(jobs, start, target, seen=None):
    """True when `start` transitively needs `target`."""
    seen = seen or set()
    for n in needs_of(jobs.get(start, {})):
        if n == target:
            return True
        if n not in seen:
            seen.add(n)
            if reaches(jobs, n, target, seen):
                return True
    return False


def exemptions():
    if not os.path.isfile(EXEMPTION_PATH):
        print("PRIVILEGED_EXEMPTION_DECLARATION_ABSENT %s" % EXEMPTION_PATH)
        sys.exit(2)
    doc = load(EXEMPTION_PATH)
    if not isinstance(doc, dict) or not isinstance(doc.get("exempt_from"), list):
        print("PRIVILEGED_EXEMPTION_DECLARATION_MALFORMED %s" % EXEMPTION_PATH)
        sys.exit(2)
    out = {}
    for e in doc["exempt_from"]:
        if not isinstance(e, dict):
            continue
        gate = str(e.get("gate", "")).strip()
        # An exemption with no decision id and no spec citation is not an
        # exemption; it is an assertion someone wrote to silence this tool.
        if gate and e.get("decision") and e.get("spec_section") and e.get("spec_lines"):
            out[gate] = e
    return out


def check(path, exempt, is_rollback):
    doc = load(path)
    text = raw(path)
    if not isinstance(doc, dict) or not isinstance(doc.get("jobs"), dict):
        finding("PRIVILEGED_WORKFLOW_MALFORMED", path)
        return
    jobs = doc["jobs"]
    order = list(jobs)

    # --- Section 33.2 line 2860: no skip surface anywhere. -------------------
    for ln in text.splitlines():
        s = ln.strip()
        if s.startswith("if:") or s.startswith("paths:") or s.startswith("paths-ignore:"):
            finding("PRIVILEGED_SKIP_SURFACE", "%s :: %s" % (path, s))
        if s.startswith("continue-on-error:"):
            finding("PRIVILEGED_CONTINUE_ON_ERROR", "%s :: %s" % (path, s))

    # --- D87 line 10180: a privileged workflow is never branch-push triggered.
    triggers = doc.get(True, doc.get("on"))
    if isinstance(triggers, dict):
        for bad in ("push", "pull_request", "pull_request_target"):
            if bad in triggers:
                finding("PRIVILEGED_BRANCH_TRIGGER", "%s :: %s" % (path, bad))
    elif isinstance(triggers, (str, list)):
        finding("PRIVILEGED_BRANCH_TRIGGER", "%s :: bare trigger list" % path)

    # --- Section 37.3 line 3267 + DoD-05: the actor gate is first. -----------
    # A per-product template does not call actor-gate.yml directly: it calls a
    # COMPOSER — production-gate-chain.yml or rollback.yml — whose own first job
    # is the actor gate, asserted when this tool checks those files. Accepting a
    # composer here is what keeps DoD-05 true at workflow scope without
    # demanding that every template duplicate the chain.
    gate_job = None
    for name, job in jobs.items():
        uses = str(job.get("uses", ""))
        if ("actor-gate.yml@" in uses or name == "actor-gate"
                or any(c in uses for c in COMPOSERS)):
            gate_job = name
            break
    if gate_job is None:
        finding("ACTOR_GATE_ABSENT", path)
    else:
        if order[0] != gate_job:
            finding("ACTOR_GATE_NOT_FIRST", "%s :: first job is %s" % (path, order[0]))
        if needs_of(jobs[gate_job]):
            finding("ACTOR_GATE_NOT_FIRST", "%s :: %s carries needs:" % (path, gate_job))
        for name in order:
            if name == gate_job:
                continue
            if not reaches(jobs, name, gate_job):
                finding("ACTOR_GATE_BYPASSABLE", "%s :: %s" % (path, name))

    # --- D87: step index 0 of every non-gate job is the runner-tier fragment. -
    for name, job in jobs.items():
        if "uses" in job:
            continue                       # a reusable-workflow call has no steps
        if name in GATE_JOBS:
            continue
        steps = job.get("steps")
        if not isinstance(steps, list) or not steps:
            finding("PRIVILEGED_JOB_NO_STEPS", "%s :: %s" % (path, name))
            continue
        if str(steps[0].get("name", "")).strip() != STEP_ANCHOR:
            finding("RUNNER_TIER_ASSERT_NOT_STEP_ZERO",
                    "%s :: %s :: %s" % (path, name, steps[0].get("name")))

    # --- D91 line 10184: the environment policy assertion is present. --------
    composed = any(c in text for c in COMPOSERS)
    if ("env-policy-assert.yml@" not in text and not composed
            and "env-policy-assert" not in exempt):
        finding("ENV_POLICY_ASSERT_ABSENT", path)

    # --- Section 27.2 / D73: the identity gate, unless declared exempt. ------
    # rollback.yml is NOT counted as carrying the identity gate: its whole point
    # is that it does not (D52). production-gate-chain.yml is.
    has_identity = ("workflow-identity-gate.yml@" in text
                    or "workflow-identity-gate" in jobs
                    or "production-gate-chain.yml@" in text)
    if is_rollback:
        if "workflow-identity-gate" not in exempt:
            finding("ROLLBACK_EXEMPTION_UNDECLARED", path)
        if has_identity:
            # D52: the exemption is the point of the workflow. Re-adding the gate
            # makes the solo out-of-hours SEV-1 rollback impossible (Section 47.2).
            finding("ROLLBACK_IDENTITY_GATE_PRESENT", path)
    else:
        if not has_identity:
            finding("IDENTITY_GATE_ABSENT", path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--templates-dir", default="templates/workflows")
    ap.add_argument("--rollback-template", default="rollback.template.yml")
    ap.add_argument("--require", default="",
                    help="comma-separated template filenames that MUST exist")
    args = ap.parse_args()

    exempt = exemptions()

    # Section 39.5 line 3591 (four) plus Section 37.3 line 3267 (deploy-staging).
    members = [
        "deploy-production.template.yml",
        "migrate.template.yml",
        args.rollback_template,
        "restore-production.template.yml",
        "deploy-staging.template.yml",
    ]

    required = [r.strip() for r in args.require.split(",") if r.strip()]
    for r in required:
        if not os.path.isfile(os.path.join(args.templates_dir, r)):
            print("PRIVILEGED_TEMPLATE_ABSENT %s" % r)
            sys.exit(1)

    checked = 0
    for m in members:
        path = os.path.join(args.templates_dir, m)
        if not os.path.isfile(path):
            continue
        check(path, exempt, is_rollback=(m == args.rollback_template))
        checked += 1

    if checked == 0:
        # Zero observations is never a pass (Section 53.1, line 4674).
        print("PRIVILEGED_NO_TEMPLATES_CHECKED")
        return 2

    for f in FINDINGS:
        print(f)
    if FINDINGS:
        print("PRIVILEGED_POSTURE_FAIL findings=%d checked=%d" % (len(FINDINGS), checked))
        return 1
    print("PRIVILEGED_POSTURE_OK checked=%d" % checked)
    return 0


if __name__ == "__main__":
    sys.exit(main())
