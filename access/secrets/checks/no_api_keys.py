#!/usr/bin/env python3
"""The API-key-free check.

Section 40.2 line 3691: "No API keys in developer environments. env | grep -i
api_key must return empty. Shell profiles and repository .env files are checked
during onboarding and re-checked quarterly."
Section 36.6 line 3235 restates it for the AI toolchain: some tools silently
prefer an API key over subscription authentication when one is present,
producing metered billing with no warning.
Section 98.2 Phase 1 line 9015 makes it a Foundation-week verification.
Invariant 84: API keys remain absent from developer environments.

Probes:
  P1 the live process environment
  P2 every shell profile path given with --profiles
  P3 every .env, .env.* and *.env file under --scan-root

Findings name the VARIABLE and the FILE. They never print the value.

Fail-closed (invariant 80): a named profile that exists but cannot be read is
exit 2. Skipping it would report clean.

Usage:
  no_api_keys.py [--profiles a,b,c] [--scan-root DIR] [--skip-env]

--skip-env exists only so the fixtures are deterministic on any machine. The
scheduled run never passes it; no-api-keys.schedule.yaml says so.

Exit 0 clean, 1 one or more findings, 2 input fault.
"""
import os
import sys

NEEDLE = "api_key"
SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv", "venv"}


def option(argv, name, default=None):
    if name in argv:
        idx = argv.index(name)
        if idx + 1 < len(argv):
            return argv[idx + 1]
    return default


def names_in_text(body):
    hits = []
    for raw in body.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[len("export "):].strip()
        if "=" not in line:
            continue
        name = line.split("=", 1)[0].strip()
        if NEEDLE in name.lower():
            hits.append(name)
    return hits


def env_files(root):
    found = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for filename in filenames:
            if filename == ".env" or filename.startswith(".env.") \
               or filename.endswith(".env"):
                found.append(os.path.join(dirpath, filename))
    return sorted(found)


def main(argv):
    profiles = [p for p in (option(argv, "--profiles", "") or "").split(",") if p]
    scan_root = option(argv, "--scan-root", ".")
    skip_env = "--skip-env" in argv

    findings = []
    p1 = 0
    if not skip_env:
        for name in sorted(os.environ):
            if NEEDLE in name.lower():
                findings.append("FINDING P1 %s present in the process environment" % name)
                p1 += 1

    p2 = 0
    for path in profiles:
        if not os.path.exists(path):
            print("PROFILE-ABSENT %s" % path)
            continue
        try:
            with open(path, "r", encoding="utf-8", errors="replace") as handle:
                body = handle.read()
        except Exception as exc:                                # fail closed
            print("RESULT FAIL profile-unreadable %s (%s)" % (path, exc))
            return 2
        for name in names_in_text(body):
            findings.append("FINDING P2 %s assigned in %s" % (name, path))
            p2 += 1

    p3 = 0
    for path in env_files(scan_root):
        try:
            with open(path, "r", encoding="utf-8", errors="replace") as handle:
                body = handle.read()
        except Exception as exc:                                # fail closed
            print("RESULT FAIL env-file-unreadable %s (%s)" % (path, exc))
            return 2
        for name in names_in_text(body):
            findings.append("FINDING P3 %s assigned in %s" % (name, path))
            p3 += 1

    for line in findings:
        print(line)
    print("PROBE P1 %d" % p1)
    print("PROBE P2 %d" % p2)
    print("PROBE P3 %d" % p3)
    print("FINDINGS %d" % len(findings))
    if findings:
        print("INVARIANT 84 BREACHED")
        print("RESULT FAIL")
        return 1
    print("RESULT PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
