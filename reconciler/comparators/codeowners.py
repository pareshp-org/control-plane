"""L3-P1-05: assignments vs CODEOWNERS (spec 53.1 row 4).

Two reasons, at most one finding per (repo, reason):

* `machine_identity_present` - Blocking. A machine identity in
  CODEOWNERS is half the machine-authority wall (§37.3, §11.3):
  CODEOWNERS approval must come from a human, always. Detected as
  either a `[bot]`-suffixed login or a login absent from people.yaml
  entirely.
* `hand_edited` - Amber. The actual file differs from the content this
  comparator would generate from the product's assignments.

A repo with a machine-identity finding is not also checked for
hand-editing: the machine-identity condition already accounts for the
divergence and is the higher-priority concern (§11.3), so flagging both
would double-count the same underlying gap.
"""

from __future__ import annotations

from reconciler.model import DriftClass, Finding, Level
from reconciler.registry import comparator


def _parse_codeowners(text: str) -> list[tuple[str, list[str]]]:
    entries = []
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        path, owners = parts[0], [o.lstrip("@") for o in parts[1:]]
        entries.append((path, owners))
    return entries


def _generate_codeowners(product_yaml: dict) -> str:
    assignments = product_yaml.get("assignments") or {}
    lines = []
    top_level: list[str] = []
    for role in (
        "primary_owner",
        "cross_reviewer",
        "backup_owner",
        "incident_responder_primary",
        "incident_responder_backup",
    ):
        holder = assignments.get(role)
        if holder and holder not in top_level:
            top_level.append(holder)
    if top_level:
        lines.append("* " + " ".join(f"@{holder}" for holder in top_level))
    verifier = assignments.get("verification_responsibility")
    if verifier:
        lines.append(f"/verification/ @{verifier}")
    return "\n".join(lines) + ("\n" if lines else "")


@comparator("codeowners", fail_class=DriftClass.BLOCKING)
def compare(declared, actual, as_of):
    findings: list[Finding] = []
    first_seen = f"{as_of.isoformat()}T00:00:00Z"
    known_logins = {p.get("github_login") for p in declared.people}

    for product_name, product_yaml in declared.products.items():
        text = actual.codeowners(product_name)
        entries = _parse_codeowners(text)
        machine_owners = sorted(
            {
                owner
                for _, owners in entries
                for owner in owners
                if owner.endswith("[bot]") or owner not in known_logins
            }
        )
        if machine_owners:
            findings.append(
                Finding(
                    id=f"codeowners:{product_name}:machine_identity_present",
                    comparator="codeowners",
                    scope=product_name,
                    drift_class=DriftClass.BLOCKING,
                    level=Level.BLOCK,
                    evidence=(
                        f"{product_name} CODEOWNERS names machine identity/identities "
                        f"{machine_owners} - CODEOWNERS approval must be human-only (§11.3, §37.3)"
                    ),
                    first_seen=first_seen,
                )
            )
            continue

        generated = _generate_codeowners(product_yaml)
        if generated.strip() != text.strip():
            findings.append(
                Finding(
                    id=f"codeowners:{product_name}:hand_edited",
                    comparator="codeowners",
                    scope=product_name,
                    drift_class=DriftClass.AMBER,
                    level=Level.WARN,
                    evidence=(
                        f"{product_name} CODEOWNERS diverges from the content generated "
                        "from its assignments (hand-edited)"
                    ),
                    first_seen=first_seen,
                )
            )

    return findings, len(declared.products)
