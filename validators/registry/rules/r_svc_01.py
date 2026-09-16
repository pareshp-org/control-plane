"""R-SVC-01 -- a service's consumers[] entry naming an id absent from the
loaded product documents.

Section 20.1: consumers is "authoritative; validated against products".

This module is a standalone, directly-tested rule function, not a
module wired into the FD-094 "Option B" dispatch engine
(validators/registry/rules/registry.py, RULES = R01..R18). FD-094
("Frozen interface... R01 through R18... Any change to this interface
requires a new FD entry", contracts/validator-contract.md) freezes that
rule catalogue; extending it to a new numbered slot for R-SVC-01 would
be exactly such a change, and is not this task's call to make. L1-404's
own ACCEPTANCE item 1 is the pytest file, which exercises this function
directly against the fixtures in validators/registry/fixtures/service/.
"""
from __future__ import annotations

RULE_ID = "R-SVC-01"
SPEC = "Section 20.1"
APPLIES_TO = ["service", "product"]


def check(service_doc: dict, known_product_ids) -> list[str]:
    """Return one finding per consumer id absent from ``known_product_ids``.

    ``known_product_ids`` is the set of ``identity.id`` values loaded from
    the product documents in context, or ``None`` when no product document
    is present at all -- in which case this rule is silent (returns no
    findings), exactly as R-PPL-04 is silent when its counterpart document
    is absent from ctx.docs.
    """
    if known_product_ids is None:
        return []
    known = set(known_product_ids)
    service_id = (service_doc.get("identity") or {}).get("id", "<unknown>")
    findings = []
    for consumer in service_doc.get("consumers") or []:
        if consumer not in known:
            findings.append(
                f"service '{service_id}' declares consumer '{consumer}', which is not "
                f"a known product; Section 20.1"
            )
    return findings
