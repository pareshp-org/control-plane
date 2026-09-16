# CONTRACT.md — the deterministic output contract

Transcribed from `lanes/L4-06-tasks.md` §0.5, *"Deterministic output contract — used by every
acceptance command in this file."* This document does not amend that section; if the two ever
disagree, `L4-06-tasks.md` §0.5 is authoritative and this file is stale and must be re-transcribed.

## The contract

Every executable this lane ships prints its result as exactly one final line on stdout and sets
its exit code from the table below. Nothing else is printed to stdout on a pass.

```
<NAME> OK <counters>        exit 0    the assertion held
<NAME> FAIL <counters>      exit 1    the module executed and the assertion did not hold
<NAME> ERROR <reason>       exit 3    the module could not execute (missing input, unreachable store)
```

Exit `3` is never a pass and never a clean run. A check that cannot reach its input **fails
closed** (§40.1 line 3671: *"a check that cannot reach the records repository fails closed rather
than reporting zero"*). Any exit code other than 0, 1 or 3 is a crash and is a STOP.

## The dispatcher this contract binds

`tools/records/check.sh` is the one entry point every task's SELF-VERIFY calls
(`lanes/L4-06-tasks.md` §0.6). It runs `tools/records/checks/<TASK-ID>.sh` and reports:

- the check file is absent — `CHECK <TASK-ID> ERROR no-check-file`, exit 3;
- in `--audit` mode, the check file fails a minimum requirement (too short, no testable
  assertion, no negative fixture) — `CHECK <TASK-ID> ERROR audit-<reason>`, exit 3;
- the check file runs and exits zero — `CHECK <TASK-ID> PASS`, exit 0;
- the check file runs and exits non-zero — `CHECK <TASK-ID> FAIL`, exit 1.

Every check file under `tools/records/checks/` is itself bound by this same contract for its own
internal assertions, per `lanes/L4-06-tasks.md` §0.6's minimum check-file requirements.
