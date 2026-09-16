"""L3-P1-08: environments and deployment branch/tag policy (spec 53.1 rows 7, 8).

Rule, exactly: for each repository and each environment named in the
committed template `declared/templates/environment.json`:

* A missing environment (not configured on the repository at all) is
  Amber, Level.WARN (row 7).
* On `staging` or `production` only, a missing, null, or widened
  deployment branch and tag policy is Blocking, Level.BLOCK (row 8) -
  §33.4 and §40.3 make this the control that makes an environment
  "accessible only to the production deployment workflow" true.
  "Widened" means more permissive than declared: `protected_branches`
  turned off, or `custom_branch_policies` turned on (either lets a ref
  outside the declared branch/tag policy deploy).

`compared` = repositories x declared environments (spec 53.1: "a
silently narrowed comparison is itself visible drift").
"""

from __future__ import annotations

from typing import Any

from reconciler.model import DriftClass, Finding, Level
from reconciler.registry import comparator

_GATED_ENVIRONMENTS = ("staging", "production")


def _policy_widened(declared_policy: dict[str, Any], actual_policy: dict[str, Any]) -> list[str]:
    widened: list[str] = []
    d_protected = bool(declared_policy.get("protected_branches"))
    a_protected = bool(actual_policy.get("protected_branches"))
    if d_protected and not a_protected:
        widened.append("protected_branches declared=True actual=False")
    d_custom = bool(declared_policy.get("custom_branch_policies"))
    a_custom = bool(actual_policy.get("custom_branch_policies"))
    if (not d_custom) and a_custom:
        widened.append("custom_branch_policies declared=False actual=True")
    return widened


@comparator("environments", fail_class=DriftClass.BLOCKING)
def compare(declared, actual, as_of):
    findings: list[Finding] = []
    first_seen = f"{as_of.isoformat()}T00:00:00Z"
    template = declared.templates.get("environment", {})
    declared_envs: list[str] = list(template.get("environments") or [])
    declared_policy: dict[str, Any] = template.get("deployment_branch_policy") or {}

    compared = 0
    for product_name in declared.products:
        actual_envs = actual.environments(product_name)
        for env_name in declared_envs:
            compared += 1
            if env_name not in actual_envs:
                findings.append(
                    Finding(
                        id=f"environments:{product_name}:{env_name}:missing_environment",
                        comparator="environments",
                        scope=f"{product_name}/{env_name}",
                        drift_class=DriftClass.AMBER,
                        level=Level.WARN,
                        evidence=(
                            f"{product_name}/{env_name} is declared in "
                            "declared/templates/environment.json but is not configured"
                        ),
                        first_seen=first_seen,
                    )
                )
                continue

            if env_name not in _GATED_ENVIRONMENTS:
                continue

            actual_policy = (actual_envs.get(env_name) or {}).get("deployment_branch_policy")
            if not actual_policy:
                findings.append(
                    Finding(
                        id=f"environments:{product_name}:{env_name}:deployment_branch_policy_missing",
                        comparator="environments",
                        scope=f"{product_name}/{env_name}",
                        drift_class=DriftClass.BLOCKING,
                        level=Level.BLOCK,
                        evidence=(
                            f"{product_name}/{env_name} has no deployment branch and tag policy - "
                            "declared/templates/environment.json requires one on staging and "
                            "production (§33.4, §40.3)"
                        ),
                        first_seen=first_seen,
                    )
                )
                continue

            widened = _policy_widened(declared_policy, actual_policy)
            if widened:
                findings.append(
                    Finding(
                        id=f"environments:{product_name}:{env_name}:deployment_branch_policy_widened",
                        comparator="environments",
                        scope=f"{product_name}/{env_name}",
                        drift_class=DriftClass.BLOCKING,
                        level=Level.BLOCK,
                        evidence=(
                            f"{product_name}/{env_name} deployment branch and tag policy "
                            f"widened vs declared/templates/environment.json: {'; '.join(widened)}"
                        ),
                        first_seen=first_seen,
                    )
                )

    return findings, compared
