# tools/evidence — subsystem F, the production evidence chain

Owner: Lane 2 (PARTITION.md line 18). Spec: Section 32 (lines 2803-2828),
Section 99.2 row F (line 9193), named tool `verify-digest-chain` (line 9215).

Contents:
  eleven-questions.yaml         the Section 32 question-to-store table, as data
  evidence-query                answers all eleven questions for one deployment
  verify-digest-chain           the digest-vs-approval sweep (Section 46.1 gate)
  collect-version.sh            GET /version observation collector
  build-deployment-record.sh    record + event payload builder for the deploy workflows
  deploy-gate.sh                fails closed while the chain is not confirmed closed
  lib/common.sh                 shared helpers
  lib/                          digest-invariant libraries (identity.sh, record-read.sh)
  fixtures/                     synthetic estates: one closed chain, four broken

Hard rule: no file in this tree contains a hardcoded path into the records
schema tree, the registries tree, the metrics tree or the reconciler tree
(each owned by another lane). Foreign surfaces are reached only through
contracts/ (PARTITION.md rule 4).
