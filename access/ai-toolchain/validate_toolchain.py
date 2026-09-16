#!/usr/bin/env python3
"""Approved-runtime and pin validator (Spec Sections 35.2, 36.3; invariant 85).

Rules, all mechanical:
  T1 runtime_id equals the filename stem
  T2 runtime_id is in the closed Section 35.2 approved set, and every member
     of that set has exactly one file
  T3 approved_extensions and approved_mcp_servers keys are both present
     (an empty list is the Section 36.3 default, and is valid)
  T4 every extension and MCP-server entry pins its source by full 40-hex
     commit SHA or by sha256:<64 hex> content checksum -- never by tag,
     branch or "latest" (Section 36.3, invariant 85)
  T5 hermes-agent is pinned at the Section 36.3 commit, by full SHA
  T6 hermes-agent never uses the curl-pipe installer or the self-update
     command, and installs from the mirror
  T7 no runtime permits a vendor API key (Section 36.6, invariant 84)
  T8 kilo-code forbids credit-based billing (Section 35.2 caveat)
  T9 any model_artefact_checksum present is sha256:<64 hex>
"""
import os
import re
import sys

import yaml

APPROVED = {
    "claude-code", "codex", "antigravity",
    "cursor", "kilo-code", "hermes-agent",
}

HERMES_PIN = "8e9459c97f707047be5915a5c8b4c503756daa9b"

RUNTIMES = os.path.join("access", "ai-toolchain", "runtimes")
SHA_RE = re.compile(r"^[0-9a-f]{40}$")
CHECKSUM_RE = re.compile(r"^sha256:[0-9a-f]{64}$")


def pinned(source):
    text = str(source)
    return bool(SHA_RE.match(text) or CHECKSUM_RE.match(text))


def check(path, doc):
    errors = []
    stem = os.path.basename(path)[: -len(".yaml")]
    if doc.get("runtime_id") != stem:
        errors.append("T1 runtime_id %r != filename stem %r"
                      % (doc.get("runtime_id"), stem))
    if stem not in APPROVED:
        errors.append("T2 runtime_id %r is not on the Section 35.2 "
                      "approved list" % stem)
    for key in ("approved_extensions", "approved_mcp_servers"):
        if key not in doc:
            errors.append("T3 missing key: %s" % key)
            continue
        if not isinstance(doc[key], list):
            errors.append("T3 %s is not a list" % key)
            continue
        for entry in doc[key]:
            if not isinstance(entry, dict) or "source" not in entry:
                errors.append("T4 %s entry has no source pin" % key)
                continue
            if not pinned(entry["source"]):
                errors.append("T4 %s entry %r is not pinned by full commit "
                              "SHA or content checksum"
                              % (key, entry.get("name", entry["source"])))
    model = doc.get("model_configuration")
    if not isinstance(model, dict):
        errors.append("T7 model_configuration is missing")
    elif str(model.get("vendor_api_key")) != "forbidden":
        errors.append("T7 vendor_api_key %r is not forbidden"
                      % model.get("vendor_api_key"))
    if stem == "hermes-agent":
        if str(doc.get("source_pin")) != HERMES_PIN:
            errors.append("T5 source_pin %r is not the Section 36.3 commit"
                          % doc.get("source_pin"))
        if not SHA_RE.match(str(doc.get("source_pin", ""))):
            errors.append("T5 source_pin is not a full 40-hex commit SHA")
        if str(doc.get("curl_pipe_installer")) != "never":
            errors.append("T6 curl_pipe_installer is not never")
        if str(doc.get("self_update_command")) != "never":
            errors.append("T6 self_update_command is not never")
        if not str(doc.get("mirror", "")).strip():
            errors.append("T6 mirror is not declared")
    if stem == "kilo-code":
        if str(doc.get("credit_based_billing")) != "forbidden":
            errors.append("T8 credit_based_billing is not forbidden")
    if "model_artefact_checksum" in doc:
        if not CHECKSUM_RE.match(str(doc["model_artefact_checksum"])):
            errors.append("T9 model_artefact_checksum is not "
                          "sha256:<64 hex>")
    return errors


def main():
    if not os.path.isdir(RUNTIMES):
        print("TOOLCHAIN-VALIDATE: FAIL (%s absent)" % RUNTIMES)
        return 1
    names = sorted(n for n in os.listdir(RUNTIMES) if n.endswith(".yaml"))
    seen = set()
    total = 0
    for name in names:
        path = os.path.join(RUNTIMES, name)
        with open(path, "r", encoding="utf-8") as handle:
            doc = yaml.safe_load(handle) or {}
        if not isinstance(doc, dict):
            print("FAIL %s: T1 file is not a YAML mapping" % path)
            total += 1
            continue
        seen.add(name[: -len(".yaml")])
        errors = check(path, doc)
        if errors:
            total += len(errors)
            for err in errors:
                print("FAIL %s: %s" % (path, err))
        else:
            print("OK %s" % path)
    for missing in sorted(APPROVED - seen):
        print("FAIL %s: T2 approved runtime has no file" % missing)
        total += 1
    print("APPROVED-RUNTIMES: %d of %d" % (len(seen & APPROVED),
                                           len(APPROVED)))
    if total:
        print("TOOLCHAIN-VALIDATE: FAIL (%d errors)" % total)
        return 1
    print("TOOLCHAIN-VALIDATE: PASS (%d runtimes)" % len(names))
    return 0


if __name__ == "__main__":
    sys.exit(main())
