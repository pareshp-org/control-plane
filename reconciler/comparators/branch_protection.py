"""L3-P1-06: branch-protection template vs actual (spec 53.1 row 5).

Rule, exactly (§53.1 row 5, §11.3, §53.3, §53.4): deep-compare each
repository's actual branch protection against the committed template
`declared/templates/branch-protection.json`.

* A weakening difference - a `true` becoming `false`, a required count
  decreasing, a required status-check context disappearing, or a
  force-push/deletion allowance turning on - is Blocking, Level.BLOCK
  (§53.1 row 5: "Alert immediately; block deployment on the affected
  repository").
* A difference in the other direction - actual strictly stricter than
  declared - is Amber, Level.WARN, and is never a repair candidate:
  §53.3, "Where actual state is stricter than declared state,
  reconciliation raises Level 2 for human judgment rather than relaxing
  the control" (AT-033).

At most one finding per repository: whichever direction has a
difference (weakening takes priority - a repository cannot be both
weaker and stricter on the same run without one of the two lists being
empty by construction below). `compared` = number of repositories.

Security-floor note: this comparator emits the raw Amber for the
stricter-than-declared case, unfloored. §53.4's "security and
production drift are never classified below Red" is enforced centrally
by `reconciler.driftclass` (L3-P3-01) reading `os-health.yaml`, after
every comparator has run - not inside the comparator itself. Flooring
here would make the stricter-direction unit test below un-writable as
Amber, which the acceptance criteria require.
"""

from __future__ import annotations

from typing import Any

from reconciler.model import DriftClass, Finding, Level
from reconciler.registry import comparator

# Boolean fields where True is the stricter setting. `section` names
# the nested dict the field lives under in the template/actual JSON
# (None for a top-level field).
_STRICTER_WHEN_TRUE = (
    ("required_pull_request_reviews", "require_code_owner_reviews"),
    ("required_pull_request_reviews", "require_last_push_approval"),
    ("required_pull_request_reviews", "dismiss_stale_reviews"),
    ("required_status_checks", "strict"),
    (None, "enforce_admins"),
)

# Boolean fields where False is the stricter setting (allowing the
# action is the weaker state).
_STRICTER_WHEN_FALSE = (
    (None, "allow_force_pushes"),
    (None, "allow_deletions"),
)


def _get(d: dict[str, Any], section: str | None, key: str) -> Any:
    if section is None:
        return d.get(key)
    return (d.get(section) or {}).get(key)


def _diff(declared_tmpl: dict[str, Any], actual: dict[str, Any]) -> tuple[list[str], list[str]]:
    """Return (weakened, stricter) - each a list of human-readable field diffs."""

    weakened: list[str] = []
    stricter: list[str] = []

    for section, key in _STRICTER_WHEN_TRUE:
        d_val = _get(declared_tmpl, section, key)
        if d_val is None:
            continue
        a_val = bool(_get(actual, section, key))
        d_val = bool(d_val)
        label = f"{section}.{key}" if section else key
        if d_val and not a_val:
            weakened.append(f"{label} declared=True actual=False")
        elif a_val and not d_val:
            stricter.append(f"{label} declared=False actual=True")

    for section, key in _STRICTER_WHEN_FALSE:
        d_val = _get(declared_tmpl, section, key)
        if d_val is None:
            continue
        a_val = bool(_get(actual, section, key))
        d_val = bool(d_val)
        label = f"{section}.{key}" if section else key
        # Here False is stricter, so a_val True while d_val False is
        # weaker; a_val False while d_val True is stricter.
        if (not d_val) and a_val:
            weakened.append(f"{label} declared=False actual=True")
        elif d_val and not a_val:
            stricter.append(f"{label} declared=True actual=False")

    d_count = _get(declared_tmpl, "required_pull_request_reviews", "required_approving_review_count")
    if d_count is not None:
        a_count = _get(actual, "required_pull_request_reviews", "required_approving_review_count") or 0
        d_count = int(d_count)
        a_count = int(a_count)
        if a_count < d_count:
            weakened.append(f"required_approving_review_count declared={d_count} actual={a_count}")
        elif a_count > d_count:
            stricter.append(f"required_approving_review_count declared={d_count} actual={a_count}")

    d_contexts = set(_get(declared_tmpl, "required_status_checks", "contexts") or [])
    a_contexts = set(_get(actual, "required_status_checks", "contexts") or [])
    missing = sorted(d_contexts - a_contexts)
    extra = sorted(a_contexts - d_contexts)
    if missing:
        weakened.append(f"required_status_checks.contexts missing={missing}")
    if extra:
        stricter.append(f"required_status_checks.contexts extra={extra}")

    return weakened, stricter


@comparator("branch_protection", fail_class=DriftClass.BLOCKING)
def compare(declared, actual, as_of):
    findings: list[Finding] = []
    first_seen = f"{as_of.isoformat()}T00:00:00Z"
    template = declared.templates.get("branch-protection", {})

    for product_name in declared.products:
        actual_protection = actual.branch_protection(product_name)
        weakened, stricter = _diff(template, actual_protection)

        if weakened:
            findings.append(
                Finding(
                    id=f"branch_protection:{product_name}:weakened",
                    comparator="branch_protection",
                    scope=product_name,
                    drift_class=DriftClass.BLOCKING,
                    level=Level.BLOCK,
                    evidence=(
                        f"{product_name} branch protection weaker than "
                        f"declared/templates/branch-protection.json: {'; '.join(weakened)}"
                    ),
                    first_seen=first_seen,
                )
            )
        elif stricter:
            # AT-033 / §53.3: never relax a stricter-than-declared
            # control. Raised for human judgment, never repaired.
            findings.append(
                Finding(
                    id=f"branch_protection:{product_name}:stricter_than_declared",
                    comparator="branch_protection",
                    scope=product_name,
                    drift_class=DriftClass.AMBER,
                    level=Level.WARN,
                    evidence=(
                        f"{product_name} branch protection stricter than "
                        f"declared/templates/branch-protection.json: {'; '.join(stricter)}"
                    ),
                    first_seen=first_seen,
                )
            )

    return findings, len(declared.products)
