# validators/registry — OWNED BY LANE 1 (Registries & Contracts)

Subsystem B of spec Section 99.2 (lines 9184-9231): multi-version schema validators,
referential integrity, date rules, the 24x7-without-rota and commitments-conflict blockers,
exception-without-expiry rejection, unclassified-control rejection.

LAYOUT
  schema/            multi-version schema validation driver
  rules/             one file per non-schema rule; the rule list is spec Section 15.5 (lines 1564-1582)
  fixtures/valid/    golden fixtures that MUST pass
  fixtures/invalid/  golden fixtures that MUST fail - one per rule
  # canonical path (FD-036): tests/fixtures/invalid/<schema-id>/
  bin/               executable entrypoints, including check-commitment (spec Section 21.4, lines 2166-2184)
  _meta/             lane self-guard and spec-anchor files

EXIT CODES: 0 = pass, non-zero = fail. Never print a success string on failure.

NOT OWNED HERE: validators/drift/** belongs to Lane 3. Read the prefix.

ARCHITECTURE NOTE (FD-094, decided 2026-09-08): the live rule-dispatch
engine is `validators/registry/cli.py` + `validators/registry/rules/registry.py`
(flat R01-R18 modules, "Option B"), documented in `contracts/validator-contract.md`.
Invoke it as:

    python -m validators.registry.cli --root <p> --as-of <d> --records-root <p> --format json [--rule Rxx]

Do not resurrect the module-discovery/RULE_ID/APPLIES_TO harness described in
lanes/L1-05-tasks.md task L1-005 ("Option D") — FD-094 explicitly supersedes it.
