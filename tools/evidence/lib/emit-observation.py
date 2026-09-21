#!/usr/bin/env python3
"""Emit one JSONL observation line. Called once per target by collect-version.sh.

Argv: product digest_field conformance_profile observed_at collect_error url
Stdin: the raw /version body (empty when the fetch failed).

Spec: Section 41.2 (lines 3717-3730) names the endpoint and what it provides,
and never names a body key - so the key is read from the target declaration,
never assumed. Section 53.1 (line 4680): an unreachable target still emits a
line, because a silently narrowed comparison set is itself drift.
"""
import json, sys

product, field, profile, observed_at, err, url = sys.argv[1:7]
body = sys.stdin.read()
digest = None
if not err:
    try:
        doc = json.loads(body)
        digest = doc.get(field)
    except Exception:
        err = "unparseable /version body"
    if digest in (None, ""):
        digest = None
        if not err:
            err = "digest field %r absent from /version body" % field
print(json.dumps({
    "product": product,
    "observed_digest": digest,
    "observed_at": observed_at,
    "source": url,
    "conformance_profile": profile,
    "collect_error": err or None,
}, sort_keys=True))
