# `access/runbooks/` — apply order

Executed by a human holding organisation-admin credentials. Every script is
**dry-run by default**; `--apply` is explicit, and in apply mode every script
requires `$ORG_LOGIN` and an authenticated `gh`. No build agent holds either.

The order below is the order declared in `access/arming/arming-order.yaml` and
checked by `access/tools/check_arming_order.py`. It is D101's order, and the
reason it is not negotiable is §98.2: *Teams granting Write exist before branch
protection is armed, so that no window opens in which no approval can satisfy the
gate.*

| Step | Command | Owner |
|---|---|---|
| AO-01 | `bash access/runbooks/apply-organisation.sh` | L5 |
| AO-02 | the owner-continuity check inside the same script | L5 |
| AO-03 | `bash access/runbooks/apply-teams.sh --input <registry-derived>.json` | L5 |
| AO-04 | `python access/codeowners/generate_codeowners.py --org "$ORG_LOGIN" --input <input>.json` | L5 |
| AO-05 | `bash access/runbooks/apply-branch-protection.sh --profile unarmed` | L5 |
| AO-06 | `bash access/runbooks/apply-environments.sh` | L5 |
| AO-07 | record the bootstrap exceptions — not an access path; routed to L0 | L0 |
| AO-08 | `bash access/runbooks/apply-branch-protection.sh --profile armed` | L5 |
| AO-09 | add each required status-check context, per phase, once a workflow emits it | L2 |

## Running order, verbatim

```bash
set -euo pipefail
export ORG_LOGIN=<the organisation login>
gh auth status

bash access/runbooks/apply-organisation.sh                       # dry run
bash access/runbooks/apply-organisation.sh --apply

bash access/runbooks/apply-teams.sh --input interim-teams.json          # dry run
bash access/runbooks/apply-teams.sh --input interim-teams.json --apply

bash access/runbooks/apply-branch-protection.sh --profile unarmed          # dry run
bash access/runbooks/apply-branch-protection.sh --profile unarmed --apply

bash access/runbooks/apply-environments.sh                       # dry run
bash access/runbooks/apply-environments.sh --apply

# The bootstrap exceptions are L0's. Do not arm until they are recorded.

bash access/runbooks/apply-branch-protection.sh --profile armed --apply
```

## The one refusal that must not be worked around

`apply-branch-protection.sh --profile armed --apply` refuses, per repository,
when no Team on that repository holds `push`, `maintain` or `admin`. That is not
a bug and it is not a permissions problem with the token. It means the Teams step
has not happened for that repository, and arming the gate would leave nobody
whose approval counts — the outcome §95.4 describes as a team that experiences
its merges mysteriously breaking. Run `apply-teams.sh` and try again.
