# Model-regression benchmark — manifest field table

Spec Section 35.5. One file per benchmark under
`access/ai-toolchain/benchmark/manifests/<benchmark-id>.yaml`
(PARTITION.md rule 3: directory-per-item).

Validated by `access/ai-toolchain/benchmark/validate_benchmark.py`.
Dispatched by `access/ai-toolchain/benchmark/run_benchmark.sh`.

## Required fields

| Field | Rule |
|---|---|
| `benchmark_id` | lower-case identifier |
| `candidate_model` | the model under evaluation |
| `candidate_model_checksum` | `sha256:` followed by 64 lower-case hex characters |
| `endpoint` | the literal `lan-local-inference` |
| `driver` | the literal `hermes-agent-batch-runner` |
| `qa_subset` | the literal `verification-authoring` |
| `tasks` | 5 to 10 entries; each carries `task_id`, `product`, `stack`, `source_record`; at least two distinct products and two distinct stacks |
| `metrics` | exactly: `acceptance_rate`, `review_time`, `defect_rate`, `plan_rejection_rate`, `token_consumption` |
| `spec_reference` | `35.5` |

## The SIG-42 boundary — binding

Section 35.5: "The nightly product AI-eval runs of Section 38.3 are not this
runner's work: they remain CI machinery holding the product's
environment-scoped provider keys, which never reside on any Hermes Agent
host."

Consequences, enforced mechanically:

* A manifest referencing any path under `records/` fails rule **B8**.
* `run_benchmark.sh` writes nothing under `records/`. **SIG-42** — AI-eval
  regression, Red, routed to the Primary Owner — is raised by the AI-eval
  scheduled runner of Section 38.3, which is not this file's tool.
* `run_benchmark.sh` refuses to run at all when any `*API_KEY*` variable is
  present in the environment (Section 36.6, invariant 84).

## What a manifest never contains

An invented task. Section 35.5 says "**real** tasks"; the task set is drawn
from real product work records by the person running the benchmark, and each
task names its `source_record`. A benchmark over fabricated tasks measures
nothing and its result cannot inform an adoption decision.

An invented model checksum. The value comes from the mirrored artefact at its
pin (Section 36.3).

An adoption decision. Section 35.5: "The runner executes; humans record the
results and make the adoption decision." The newest model is not assumed
better; nobody is forced to switch; results are recorded so the same
evaluation is not repeated from memory.
