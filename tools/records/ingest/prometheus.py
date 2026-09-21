#!/usr/bin/env python3
"""INGEST --prometheus limb. Master Spec 41.2 lines 3719-3728."""
import re
import sys
import yaml

PATH = "metrics/ingest/prometheus.yaml"
ENDPOINTS = [
    ("/health", "Liveness plus dependency health, distinguishing internal from external failure", 3723),
    ("/version", "Deployed artifact digest and build metadata", 3724),
    ("/metrics", "Prometheus format", 3725),
]
EXEMPT = ["batch", "client-app", "customer-hosted", "library", "static-site"]
CARRIES_NONE = ["deploy_key", "environment_access", "production_credential"]
FORBIDDEN = re.compile(r"https?://|:9090|:9100|hostname|ip_address|scrape_interval_seconds")


def fail(msg):
    print("INGEST FAIL prometheus %s" % msg)
    sys.exit(1)


def main():
    try:
        raw = open(PATH, encoding="utf-8").read()
        d = yaml.safe_load(raw)
        col = yaml.safe_load(open("metrics/ingest/collectors.yaml", encoding="utf-8"))
    except Exception as e:
        print("INGEST ERROR prometheus-unreadable:%s" % type(e).__name__)
        sys.exit(3)

    if FORBIDDEN.search(raw):
        fail("host-port-url-or-interval-declared-by-l4")
    if d.get("source_kind") != "collector":
        fail("prometheus-claimed-as-record-store")

    eps = d.get("endpoints") or []
    if [(e.get("path"), e.get("provides"), e.get("spec_line")) for e in eps] != ENDPOINTS:
        fail("endpoints-not-the-three-of-lines-3723-3725")

    if d.get("required_for_conformance_profiles") != ["service", "white-label"]:
        fail("required-profiles-not-service-and-white-label")
    if sorted(d.get("exempt_conformance_profiles") or []) != EXEMPT:
        fail("exempt-profiles-not-the-five-of-line-3719")
    if d.get("exempt_equivalent_evidence_section") != "15.7":
        fail("exempt-evidence-section-not-15-7")
    if d.get("never_failed_for_lacking_an_endpoint_its_shape_cannot_serve") is not True:
        fail("shape-exemption-not-declared")

    if d.get("telemetry_exposure_posture") != "private-authenticated":
        fail("posture-not-private-authenticated")
    if d.get("public_requires_recorded_founder_decision") is not True:
        fail("public-without-a-recorded-founder-decision")
    if d.get("public_is_a_framework_default") is not False:
        fail("public-declared-as-a-framework-default")
    if d.get("per_product_scrape_credential") is not True:
        fail("per-product-scrape-credential-not-declared")
    if sorted(d.get("private_path_carries_none_of") or []) != CARRIES_NONE:
        fail("private-path-scope-widened-beyond-line-3726")

    if d.get("version_digest_must_equal_approved_digest") is not True:
        fail("version-digest-equality-not-declared")
    if d.get("version_digest_mismatch_severity") != "P0":
        fail("digest-mismatch-not-p0")

    if d.get("ai_counters_exported_via") != "/metrics":
        fail("ai-counters-not-on-metrics-endpoint")
    if d.get("alert_fraction_key") != "cost.metrics_alert_fraction":
        fail("alert-fraction-key-renamed")
    if d.get("alert_fraction_initial_value_in_spec") != 0.8:
        fail("alert-fraction-initial-value-not-0-8")
    if d.get("l4_declares_alert_rule") is not False:
        fail("l4-declares-an-alert-rule-that-is-l5s")

    if d.get("scrape_interval_declared_by_l4") is not False:
        fail("l4-declares-a-scrape-interval-it-must-not-invent")
    p = col["collectors"]["prometheus"]
    if p.get("scrape_interval_declared_by_l4") is not False:
        fail("collectors-yaml-and-prometheus-yaml-disagree-on-the-interval-owner")
    if d.get("evidence_authored_by_lane_4") is not False:
        fail("lane-4-claims-authorship-of-assisted-evidence")

    print("INGEST OK prometheus endpoints=3 profiles=2 exempt=5 posture=private-authenticated")
    return 0


if __name__ == "__main__":
    sys.exit(main())
