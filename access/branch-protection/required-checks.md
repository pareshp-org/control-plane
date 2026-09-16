# Required status checks — the list starts empty, per repository

Spec §98.2, Phase 1: *"The required-status-check list starts empty per repository
and is populated as each check comes into existence — CI checks at that product's
Phase 4, the verification contract at Phase 5, the pipeline checks at Phase 6. A
required check no workflow emits blocks every pull request indefinitely; a list
that silently stays empty is a gate that reads armed and is not. Each phase's
completion check names the contexts it adds."*

Both halves of that sentence are load-bearing, and they pull in opposite
directions. Adding a context early blocks every pull request on the repository
until the emitting workflow exists. Never adding one leaves a gate that reads
armed and is not. The resolution is the catalogue: the contexts are declared
here from Phase 1, and each is **added to a repository only at the phase that
brings its workflow into existence**.

| Context | Added at | Emitted by |
|---|---|---|
| `tests` | that product's Phase 4 | L2 reusable workflow |
| `build` | that product's Phase 4 | L2 reusable workflow |
| `security-scan` | that product's Phase 4 | L2 reusable workflow |
| `contract-validation` | that product's Phase 4 | L2 reusable workflow |
| `reviewer-matrix-validation` | that product's Phase 4 | L2 reusable workflow |
| `parity-check` | that product's Phase 4 | L2 reusable workflow |
| `verification-contract` | that product's Phase 5 | L2 reusable workflow |
| `control-plane/blocking-drift` | that product's Phase 6 | the reconciler (L3), surfaced as a check |

**This lane emits none of them.** `.github/workflows/**` is L2's path and
`reconciler/**` is L3's (§0.2). L5 declares the policy and renders the payload;
adding a context to a live repository is an apply-time step in
`access/runbooks/apply-branch-protection.sh`, and it is legitimate only once
`gh api /repos/$ORG_LOGIN/<repo>/commits/<sha>/check-runs` shows the context
actually reported by a run — which is exactly what the phase completion checks of
§98.2 Phases 4, 5 and 6 verify.
