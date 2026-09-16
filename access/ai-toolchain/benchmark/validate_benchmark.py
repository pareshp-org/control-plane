#!/usr/bin/env python3
"""Model-regression benchmark manifest validator (Spec Section 35.5).

Rules, all mechanical:
  B1 5 <= len(tasks) <= 10                  ("5-10 real tasks")
  B2 at least two distinct products         ("across at least two products")
  B3 at least two distinct stacks           ("and two stacks")
  B4 metrics is exactly the Section 35.5 five, no more and no fewer
  B5 candidate_model_checksum is sha256:<64 hex>
  B6 endpoint is lan-local-inference and driver is the Hermes batch runner
  B7 qa_subset is verification-authoring
  B8 no path under records/ appears anywhere in the manifest
     (Section 35.5: the nightly AI-eval runs are not this runner's work)
  B9 every task carries task_id, product, stack and source_record

Usage: validate_benchmark.py <manifest.yaml> [<manifest.yaml> ...]
"""
import os
import re
import sys

import yaml

METRICS = ["acceptance_rate", "review_time", "defect_rate",
           "plan_rejection_rate", "token_consumption"]

CHECKSUM_RE = re.compile(r"^sha256:[0-9a-f]{64}$")


def check(path):
    errors = []
    with open(path, "r", encoding="utf-8") as handle:
        raw = handle.read()
    doc = yaml.safe_load(raw)
    if not isinstance(doc, dict):
        return ["B9 file is not a YAML mapping"]
    tasks = doc.get("tasks")
    if not isinstance(tasks, list):
        errors.append("B1 tasks is not a list")
        tasks = []
    if not 5 <= len(tasks) <= 10:
        errors.append("B1 task count %d is outside the Section 35.5 range 5-10"
                      % len(tasks))
    products = set()
    stacks = set()
    for index, task in enumerate(tasks):
        if not isinstance(task, dict):
            errors.append("B9 task %d is not a mapping" % index)
            continue
        for field in ("task_id", "product", "stack", "source_record"):
            if not str(task.get(field, "")).strip():
                errors.append("B9 task %d missing %s" % (index, field))
        products.add(str(task.get("product", "")))
        stacks.add(str(task.get("stack", "")))
    products.discard("")
    stacks.discard("")
    if len(products) < 2:
        errors.append("B2 %d distinct products; Section 35.5 requires at "
                      "least two" % len(products))
    if len(stacks) < 2:
        errors.append("B3 %d distinct stacks; Section 35.5 requires at "
                      "least two" % len(stacks))
    metrics = doc.get("metrics")
    if not isinstance(metrics, list) or sorted(str(m) for m in metrics) != \
            sorted(METRICS):
        errors.append("B4 metrics is not exactly the Section 35.5 five: %s"
                      % ", ".join(METRICS))
    if not CHECKSUM_RE.match(str(doc.get("candidate_model_checksum", ""))):
        errors.append("B5 candidate_model_checksum is not sha256:<64 hex>")
    if str(doc.get("endpoint")) != "lan-local-inference":
        errors.append("B6 endpoint %r is not lan-local-inference"
                      % doc.get("endpoint"))
    if str(doc.get("driver")) != "hermes-agent-batch-runner":
        errors.append("B6 driver %r is not hermes-agent-batch-runner"
                      % doc.get("driver"))
    if str(doc.get("qa_subset")) != "verification-authoring":
        errors.append("B7 qa_subset %r is not verification-authoring"
                      % doc.get("qa_subset"))
    if "records/" in raw:
        errors.append("B8 manifest references records/ — the nightly AI-eval "
                      "runs of Section 38.3 are not this runner's work")
    return errors


def main():
    paths = sys.argv[1:]
    if not paths:
        print("BENCHMARK-VALIDATE: SKIPPED (no manifest given)")
        return 2
    total = 0
    for path in paths:
        if not os.path.exists(path):
            print("FAIL %s: file does not exist" % path)
            total += 1
            continue
        errors = check(path)
        if errors:
            total += len(errors)
            for err in errors:
                print("FAIL %s: %s" % (path, err))
        else:
            print("OK %s" % path)
    if total:
        print("BENCHMARK-VALIDATE: FAIL (%d errors)" % total)
        return 1
    print("BENCHMARK-VALIDATE: PASS (%d manifests)" % len(paths))
    return 0


if __name__ == "__main__":
    sys.exit(main())
