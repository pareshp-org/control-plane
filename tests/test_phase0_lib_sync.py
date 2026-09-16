"""
Sync check between scripts/phase0-lib/*.py and the heredocs embedded in
run-phase-0.sh that they mirror.

scripts/phase0-lib/append_register.py and verify_contracts.py are
manually-synced copies of the `cat > contracts/ci/<name>.py <<'PYEOF' ... PYEOF`
heredoc blocks inside run-phase-0.sh (added so those scripts can be unit
tested directly -- see tests/integration/test_phase0_register.py -- instead
of only via heredoc-extraction-to-scratch). Nothing enforces that the two
stay identical, and run-phase-0.sh has had many edits this session, so this
test extracts the CURRENT heredoc content straight out of run-phase-0.sh and
diffs it against the checked-in mirror, failing loudly on drift.

run-phase-0.sh is the source of truth. If this test fails, fix the mirror
file in scripts/phase0-lib/ to match -- never edit run-phase-0.sh to match
the mirror.
"""
from __future__ import annotations

import difflib
import re
from pathlib import Path

import pytest

IMPL_ROOT = Path(__file__).parent.parent
RUN_PHASE_0 = IMPL_ROOT / "run-phase-0.sh"
PHASE0_LIB = IMPL_ROOT / "scripts" / "phase0-lib"

# Each mirror file is checked in with its own header comment block (banner-
# delimited) explaining that it's a manual mirror -- that block doesn't exist
# in the heredoc and must be stripped before comparing. The block always
# starts on the line right after the shebang and is delimited top and bottom
# by a "# ----...----" banner line.
BANNER_RE = re.compile(r"^# -{10,}\s*$")

MIRRORS = [
    ("append_register.py", "contracts/ci/append_register.py"),
    ("verify_contracts.py", "contracts/ci/verify_contracts.py"),
]


def _heredoc_pattern(target_path: str) -> re.Pattern:
    # The opening line looks like (literally, in run-phase-0.sh):
    #   cat > contracts/ci/append_register.py <<'"'"'PYEOF'"'"'
    # -- the '"'"' dance embeds a literal quote so the heredoc delimiter is
    # quoted (no variable/command expansion inside) even though the whole
    # task body is itself already a single-quoted bash string.
    escaped = re.escape(target_path)
    opening = escaped + r" <<'\"'\"'PYEOF'\"'\"'"
    return re.compile(opening + r"\r?\n(.*?)\r?\nPYEOF\r?\n", re.DOTALL)


def _extract_heredoc(script_text: str, target_path: str) -> str:
    pattern = _heredoc_pattern(target_path)
    matches = pattern.findall(script_text)
    if not matches:
        raise AssertionError(
            f"could not find a `cat > {target_path} <<'PYEOF' ... PYEOF` heredoc "
            f"in {RUN_PHASE_0.name} -- extraction pattern may need updating "
            f"if the task's quoting style changed"
        )
    if len(matches) > 1:
        raise AssertionError(
            f"found {len(matches)} heredocs writing {target_path} in "
            f"{RUN_PHASE_0.name}, expected exactly 1 -- update this test to "
            f"say which one the mirror should track"
        )
    # The regex's trailing `\r?\n` (consumed as the newline that ends the
    # heredoc's last content line, right before the PYEOF delimiter line) is
    # not part of the captured group -- add it back so the extracted content
    # ends with a trailing newline like any normal text file.
    return matches[0] + "\n"


def _strip_mirror_header(mirror_text: str) -> str:
    """Remove the mirror file's own explanatory header comment block so what
    remains is exactly what the heredoc in run-phase-0.sh should produce.

    Expected shape:
        line 1:        shebang
        line 2:        banner ("# ---...")
        lines 3..N-1:  free-form comment lines
        line N:        banner ("# ---...")
        line N+1..:    real content (must match the heredoc byte-for-byte)
    """
    lines = mirror_text.splitlines(keepends=True)
    if len(lines) < 2 or not lines[0].startswith("#!"):
        raise AssertionError("mirror file must start with a shebang line")
    if not BANNER_RE.match(lines[1].rstrip("\n")):
        raise AssertionError(
            "mirror file must have a banner-delimited header comment "
            "starting on line 2 (see scripts/phase0-lib/append_register.py "
            "for the expected shape)"
        )
    close_idx = None
    for i in range(2, len(lines)):
        if BANNER_RE.match(lines[i].rstrip("\n")):
            close_idx = i
            break
    if close_idx is None:
        raise AssertionError(
            "mirror file's header comment block has no closing banner line"
        )
    return lines[0] + "".join(lines[close_idx + 1:])


def _diff(expected: str, actual: str, expected_label: str, actual_label: str) -> str:
    return "".join(
        difflib.unified_diff(
            expected.splitlines(keepends=True),
            actual.splitlines(keepends=True),
            fromfile=expected_label,
            tofile=actual_label,
        )
    )


def _check_sync(mirror_name: str, heredoc_target: str) -> str | None:
    """Return a failure message (including a unified diff) if the mirror has
    drifted from the run-phase-0.sh heredoc, or None if they match. Plain
    Python (no pytest dependency) so it can be reused by the __main__ block
    below for a pytest-free manual check."""
    script_text = RUN_PHASE_0.read_text(encoding="utf-8")
    heredoc_content = _extract_heredoc(script_text, heredoc_target)

    mirror_path = PHASE0_LIB / mirror_name
    if not mirror_path.exists():
        return f"mirror file missing: {mirror_path}"
    mirror_content = _strip_mirror_header(mirror_path.read_text(encoding="utf-8"))

    if heredoc_content == mirror_content:
        return None

    diff = _diff(
        heredoc_content, mirror_content,
        f"run-phase-0.sh:{heredoc_target} (source of truth)",
        f"scripts/phase0-lib/{mirror_name} (mirror, minus header)",
    )
    return (
        f"scripts/phase0-lib/{mirror_name} has drifted from the "
        f"run-phase-0.sh heredoc that writes {heredoc_target}.\n"
        f"run-phase-0.sh is the source of truth -- update the mirror "
        f"file to match it, do not edit run-phase-0.sh.\n\n{diff}"
    )


@pytest.mark.parametrize("mirror_name,heredoc_target", MIRRORS)
def test_mirror_is_in_sync_with_heredoc(mirror_name, heredoc_target):
    failure = _check_sync(mirror_name, heredoc_target)
    if failure is not None:
        pytest.fail(failure)


if __name__ == "__main__":
    # Allow `python tests/test_phase0_lib_sync.py` for a quick manual check
    # without pytest.
    failures = 0
    for mirror_name, heredoc_target in MIRRORS:
        try:
            failure = _check_sync(mirror_name, heredoc_target)
        except AssertionError as e:
            failure = str(e)
        if failure is None:
            print(f"IN SYNC: scripts/phase0-lib/{mirror_name}")
        else:
            failures += 1
            print(f"DRIFTED: scripts/phase0-lib/{mirror_name}\n{failure}")
    raise SystemExit(1 if failures else 0)
