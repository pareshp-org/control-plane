# L1 Validator Contract
# FD-094 (PFD-001) — 2026-09-08
# Frozen interface. L2 CI must call exactly this. No other validator interface is valid.

## Entry point
`validators/registry/cli.py`

## Invocation grammar
```
python -m validators.registry.cli \
  --root <registry-root-path> \
  --as-of <YYYY-MM-DD> \
  --records-root <records-root-path> \
  --format json \
  --rule <rule-id>
```

## Exit codes
- 0: All rules pass
- 1: One or more rules fail
- 2: Input error (missing file, bad argument)

## Rule identifiers
R01 through R18 with sub-codes (e.g. R07.1).
Rules stored as flat Python files: `validators/registry/rules/r{nn}_{name}.py`

## Rule selection
Omit `--rule` to run all rules. Specify one `--rule Rnn` to run a single rule.

## Output format
`--format json` produces a JSON object with keys: `rule`, `status`, `violations[]`.
`--format text` (default) produces human-readable output.

## Baseline fixture
`make-fixture.sh` at the repo root generates a passing baseline registry for test harnesses.
Pattern: the must-fail recipe uses `INVALID: [` prefix to mark expected-failure fixtures.

## Cross-lane contract
L2 CI wires its workflow step to this grammar verbatim. Any change to this interface
requires a new FD entry and a lane-guard contract-version bump.
