#!/usr/bin/env python3
"""Per-product AI-restriction checker (Section 36.4).

Section 36.4: where a product contract's `ai_restrictions.ai_processing_permitted`
is false, the repository is excluded from five surfaces: AI runtime context,
Repomix packaging, GSD execution, the background layer's repository
whitelist, and any automated-review tooling. The exclusion is enforced at
onboarding, not remembered by individuals.

Product contracts are L1/product-owned, not Lane 5's; this checker reads
`products/*/product.yaml` (the live-repo convention named in
lanes/L1-03-validators.md:851) as data only, and never writes there. Until a
product with `ai_processing_permitted: false` is onboarded, the check has
nothing to enforce and reports PASS-VACUOUS with the count -- distinct from
a real PASS, so an empty read is never mistaken for a verified estate.

The five surfaces, as Lane 5 can observe them from its own owned trees:
  1. ai_runtime_context   access/ai-toolchain/runtimes/*.yaml repository
                           context/allowlist fields
  2. repomix_packaging    access/ai-toolchain/checks/repomix_preflight.sh's
                           configured scope
  3. gsd_execution        access/ai-toolchain/runtimes/*.yaml (GSD is a
                           runtime entry like any other)
  4. background_whitelist infra/runners/placement-rule.yaml /
                           infra/runners/hosts.list
  5. automated_review     out of Lane 5's owned trees (L2 CI); reported
                           INDETERMINATE-OUT-OF-SCOPE, never silently passed

Usage:  check_ai_restrictions.py [--products-dir <dir>] [--selftest]
Exit 0 PASS/PASS-VACUOUS, 1 FAIL (a restricted product's repo is present in
a surface this lane owns), 2 fail-closed (a restricted product's contract
is unreadable).
"""
import glob
import os
import re
import sys

import yaml

DEFAULT_PRODUCTS_DIR = "products"
RUNTIME_GLOB = os.path.join("access", "ai-toolchain", "runtimes", "*.yaml")
REPOMIX_SCRIPT = os.path.join("access", "ai-toolchain", "checks", "repomix_preflight.sh")
RUNNER_PLACEMENT = os.path.join("infra", "runners", "placement-rule.yaml")
RUNNER_HOSTS = os.path.join("infra", "runners", "hosts.list")

LANE5_OWNED_SURFACES = ["ai_runtime_context", "repomix_packaging", "gsd_execution",
                         "background_whitelist"]
OUT_OF_SCOPE_SURFACES = ["automated_review"]


def load_yaml(path):
    try:
        with open(path, "r", encoding="utf-8") as handle:
            return yaml.safe_load(handle)
    except (OSError, yaml.YAMLError):
        return None


def restricted_products(products_dir):
    """Return [(product_id, repo_names)] for every product whose contract
    declares ai_processing_permitted: false. A contract that exists but
    cannot be parsed is fail-closed -- treated as restricted with unknown
    repos, which surfaces as an inspection failure rather than a silent
    pass."""
    restricted = []
    unreadable = []
    for path in sorted(glob.glob(os.path.join(products_dir, "*", "product.yaml"))):
        product_id = os.path.basename(os.path.dirname(path))
        doc = load_yaml(path)
        if doc is None:
            unreadable.append(product_id)
            continue
        ai = (doc.get("ai_restrictions") or {})
        if ai.get("ai_processing_permitted") is False:
            repos = []
            for repo in ((doc.get("code") or {}).get("repositories") or []):
                name = repo.get("name") if isinstance(repo, dict) else None
                if name:
                    repos.append(name)
            restricted.append((product_id, repos))
    return restricted, unreadable


def _text_mentions_any(text, needles):
    lower = text.lower()
    return [n for n in needles if n.lower() in lower]


def check_surface_file(path, repo_names, surface_label):
    if not os.path.exists(path):
        return []  # nothing declared at all cannot name a restricted repo
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as handle:
            body = handle.read()
    except OSError:
        return ["%s (%s) unreadable" % (path, surface_label)]
    hits = _text_mentions_any(body, repo_names)
    return ["%s (%s) names restricted repo(s): %r" % (path, surface_label, hits)] if hits else []


def check_restricted_product(product_id, repo_names, runner_hosts_path=RUNNER_HOSTS):
    findings = []
    for runtime_path in glob.glob(RUNTIME_GLOB):
        findings += check_surface_file(runtime_path, repo_names, "ai_runtime_context/gsd_execution")
    findings += check_surface_file(REPOMIX_SCRIPT, repo_names, "repomix_packaging")
    findings += check_surface_file(RUNNER_PLACEMENT, repo_names, "background_whitelist")
    findings += check_surface_file(runner_hosts_path, repo_names, "background_whitelist")
    return findings


def run(products_dir, runner_hosts_path=RUNNER_HOSTS):
    restricted, unreadable = restricted_products(products_dir)
    findings = ["contract unreadable for restricted-candidate product %s" % p
                for p in unreadable]
    for product_id, repos in restricted:
        if not repos:
            findings.append(
                "product %s declares ai_processing_permitted: false but names "
                "no repositories to check -- cannot verify exclusion" % product_id)
            continue
        findings += ["product %s: %s" % (product_id, f)
                      for f in check_restricted_product(product_id, repos, runner_hosts_path)]
    return restricted, findings


def selftest():
    fixture_root = os.path.join("access", "tests", "fixtures", "at-ai-restrictions")
    clean_dir = os.path.join(fixture_root, "clean")
    breach_dir = os.path.join(fixture_root, "breach")
    os.makedirs(os.path.join(clean_dir, "restricted-co"), exist_ok=True)
    os.makedirs(os.path.join(breach_dir, "restricted-co"), exist_ok=True)

    contract = {
        "ai_restrictions": {"ai_processing_permitted": False, "basis": "Client MSA clause"},
        "code": {"repositories": [{"name": "restricted-co-api"}]},
    }
    for d in (clean_dir, breach_dir):
        with open(os.path.join(d, "restricted-co", "product.yaml"), "w", encoding="utf-8") as h:
            yaml.safe_dump(contract, h)

    try:
        restricted, findings = run(clean_dir)
        if not restricted:
            print("SELFTEST FAIL: the fixture's restricted product was not detected")
            return 1
        if findings:
            print("SELFTEST FAIL: a clean fixture (no surface names the restricted "
                  "repo) produced findings: %r" % findings)
            return 1

        # Breach fixture: plant the restricted repo name in a background
        # whitelist file this checker actually reads.
        breach_hosts = os.path.join(breach_dir, "hosts.list")
        with open(breach_hosts, "w", encoding="utf-8") as h:
            h.write("restricted-co-api\n")
        _, breach_findings = run(breach_dir, runner_hosts_path=breach_hosts)
        if not breach_findings:
            print("SELFTEST FAIL: a planted restricted-repo mention in a "
                  "background-whitelist file was not caught")
            return 1
    finally:
        import shutil
        shutil.rmtree(fixture_root, ignore_errors=True)

    # Vacuous-pass check against the real (currently empty) products/ tree.
    live_restricted, live_findings = run(DEFAULT_PRODUCTS_DIR)
    if live_findings:
        print("SELFTEST FAIL: the live products/ tree produced findings: %r" % live_findings)
        return 1

    print("L5-T29 SELF-VERIFY PASS")
    print("(live products/ tree: %d restricted products found)" % len(live_restricted))
    return 0


def main(argv):
    if "--selftest" in argv:
        return selftest()
    products_dir = DEFAULT_PRODUCTS_DIR
    if "--products-dir" in argv:
        products_dir = argv[argv.index("--products-dir") + 1]

    restricted, findings = run(products_dir)
    for f in findings:
        print("FINDING %s" % f)
    if findings:
        print("RESULT FAIL")
        return 1
    if not restricted:
        print("RESULT PASS-VACUOUS (0 products with ai_processing_permitted: false "
              "under %s)" % products_dir)
        return 0
    print("RESULT PASS (%d restricted product(s), 0 surface breaches)" % len(restricted))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
