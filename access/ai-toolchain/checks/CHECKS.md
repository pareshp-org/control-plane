# AI-toolchain checks — Spec Section 36.6, Section 96.6 S10

Three executable checks. Each fails closed. None of them ever prints a
credential value.

| Check | Obligation | Exit codes |
|---|---|---|
| `no_api_keys.sh` | Section 36.6: `env \| grep -i api_key` must return empty. Invariant 84: API keys remain absent from developer environments | `0` pass · `1` one or more variables present |
| `repomix_preflight.sh` | Section 36.6: Repomix runs as a pre-flight step before packaged code reaches a model; Secretlint coverage for each product's languages is confirmed before the fleet relies on it | `0` pass · `2` usage · `3` blocked |
| `s10_gate.sh` | Section 96.6 S10 and Section 36.6: no AI-assisted session opens a repository until that repository's committed-secrets check has passed — universal floor | `0` pass · `2` usage · `3` blocked |

## What these checks never do

* `no_api_keys.sh` prints **variable names only**. It never prints a value,
  never writes one to a file, and never appears in any log with a value
  attached.
* No check writes outside `access/`. None of them rotates, deletes or edits a
  credential; a found key is remediated by the person whose environment holds
  it.
* No check is weakened to make a run green. Section 36.6 gives two reasons the
  no-API-keys rule exists: the credential boundary, and the fixed-cost
  constraint — some AI tools silently prefer an API key over subscription auth
  when one is present, producing metered billing with no warning.
* `repomix_preflight.sh` never packages when repomix is absent or when
  Secretlint coverage is unrecorded. The guarantee covers only content that
  passes through Repomix packaging (Section 36.6); interactive runtimes read
  repository files directly, which is what `s10_gate.sh` covers.

## The Hermes estate leaves this rule unchanged

Section 36.6: every Hermes instance points at the estate's own local inference
endpoint and its `model.api_key` carries that instance's own endpoint
credential — a self-minted control-plane token, never a vendor API key. The
harness's optional tool keys are never configured on any seat or instance. **No
vendor API keys exist anywhere in the estate.** L5-05-09 records this on
`access/ai-toolchain/runtimes/hermes-agent.yaml`; this check is what proves it
on a live environment.
