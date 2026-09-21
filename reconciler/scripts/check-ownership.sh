#!/usr/bin/env bash
# L3-P0-02: fails the branch if it touches a path outside this lane's three
# owned roots, or if THIS lane's own change set has added a namespace-package
# __init__.py under a shared parent it does not own (tools/, validators/).
#
# tools/__init__.py and validators/__init__.py are pre-existing, foreign-owned
# files whose *existence* on integration is not itself a violation (PARTITION.md
# already grants L3 the validators/drift/** and tools/provision/** subtrees
# beneath those shared parents) - the violation this check guards against is
# THIS lane creating either file, which would turn a shared implicit namespace
# package into a regular one and collide with the owning lane's package.
#
# Comparison base, in order of preference:
#   1. $BASE_REF if set and resolvable
#   2. origin/integration or integration, if this checkout has one (the real
#      multi-lane merge-train workflow)
#   3. the currently staged change set (git diff --cached), for a lane branch
#      that has not yet been rebased onto a shared integration ref
#   4. the working tree's unstaged change set, if nothing is staged
# If none of the above yields any changed path, there is nothing to check and
# the script reports OWNERSHIP OK.
set -euo pipefail

resolve_base_ref() {
    for candidate in "${BASE_REF:-}" origin/integration integration; do
        [ -n "$candidate" ] || continue
        if git rev-parse --verify "$candidate" >/dev/null 2>&1; then
            echo "$candidate"
            return 0
        fi
    done
    return 1
}

base_ref=""
if base_ref="$(resolve_base_ref)"; then
    changed_names="$(git diff --name-only "$base_ref"...HEAD)"
    added_names="$(git diff --name-status --diff-filter=A "$base_ref"...HEAD | awk '{print $2}')"
else
    staged="$(git diff --cached --name-only)"
    if [ -n "$staged" ]; then
        changed_names="$staged"
        added_names="$(git diff --cached --name-status --diff-filter=A | awk '{print $2}')"
    else
        changed_names="$(git diff --name-only)"
        added_names="$(git diff --name-status --diff-filter=A | awk '{print $2}')"
    fi
fi

foreign="$(printf '%s\n' "$changed_names" | grep -vE '^(reconciler/|tools/provision/|validators/drift/)' | sed '/^$/d' || true)"
if [ -n "$foreign" ]; then
    echo "FOREIGN PATHS:"
    echo "$foreign"
    exit 1
fi

added_namespace_files="$(printf '%s\n' "$added_names" | grep -E '^(tools/__init__\.py|validators/__init__\.py)$' || true)"
if [ -n "$added_namespace_files" ]; then
    echo "NAMESPACE VIOLATION"
    exit 1
fi

echo "OWNERSHIP OK"
