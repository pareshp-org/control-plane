"""L3-P4-01: the `provision` CLI skeleton (spec §12.6; §64.1; §101 invariant 79).

Four subcommands: `create-product`, `add-person`, `change-role`,
`remove-person`. Every one of them requires exactly one of `--fixture`
or `--live` (you must say which world you are planning against), and
every one of them is dry-run by default: nothing this CLI holds a
provisioning credential for is ever mutated unless the caller passes
the explicit `--apply` flag, and `--apply` is refused outright unless
`--live` is also given -- a fixture can never be "applied" to (§64.1:
"a configuration error must never grant excess authority").

This module is the skeleton only (L3-P4-01). The per-operation plan
builders that turn a fixture/org into a real, populated `Plan` --
`create-product` (L3-P4-07), `add-person` (L3-P4-09), `change-role`
(L3-P7-01), `remove-person` (L3-P7-02) -- land in later Phase-4/7 tasks
and are wired in at their own call sites. Until then every subcommand
plans zero steps and prints the Section 7 summary line honestly: an
empty plan is not a stub *result*, it is the correct result of a
skeleton that does not yet know how to enumerate a real operation's
steps, and it never claims a write it did not perform.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from tools.provision.plan import Plan

_COMMANDS = ("create-product", "add-person", "change-role", "remove-person")

# One line, appearing exactly once in top-level --help output, is the
# only mention of --apply outside each subcommand's own argument (the
# subcommands share identical --apply semantics, so it is documented
# once at the top rather than duplicated four times in --help text).
_EPILOG = (
    "Every subcommand is dry-run unless given --apply, which also requires --live: "
    "a fixture can never be applied to."
)


def _add_common_args(sub: argparse.ArgumentParser) -> None:
    source = sub.add_mutually_exclusive_group(required=True)
    source.add_argument("--fixture", default=None, help="plan against this fixture under reconciler/fixtures/")
    source.add_argument("--live", action="store_true", help="plan against the real organisation")
    sub.add_argument("--org", default=None, help="organisation name (only meaningful with --live)")
    sub.add_argument(
        "--apply",
        action="store_true",
        help="perform real writes instead of a dry run (requires --live)",
    )
    sub.add_argument("--dry-run", action="store_true", help="explicit no-op: this is already the default")
    sub.add_argument("--summary", action="store_true", help="print the PLAN summary line")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m tools.provision.cli",
        description="Lane 3 provisioning: create-product, add-person, change-role, remove-person.",
        epilog=_EPILOG,
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_create = sub.add_parser("create-product", help="scaffold a new product: repo, Team, CODEOWNERS, protection")
    _add_common_args(p_create)
    p_create.add_argument("--product", required=True, help="the product id to create")
    p_create.set_defaults(func=_cmd_create_product)

    p_add = sub.add_parser("add-person", help="onboard a person onto the organisation and any assignments")
    _add_common_args(p_add)
    p_add.add_argument("--login", required=True, help="the GitHub login being added")
    p_add.set_defaults(func=_cmd_add_person)

    p_change = sub.add_parser("change-role", help="move a person to a new role")
    _add_common_args(p_change)
    p_change.add_argument("--login", required=True, help="the GitHub login whose role is changing")
    p_change.add_argument("--to-role", required=True, help="the role the person is moving to")
    p_change.set_defaults(func=_cmd_change_role)

    p_remove = sub.add_parser("remove-person", help="offboard a person: revoke access and reassign ownership")
    _add_common_args(p_remove)
    p_remove.add_argument("--login", required=True, help="the GitHub login being removed")
    p_remove.set_defaults(func=_cmd_remove_person)

    return parser


class ApplyRequiresLive(RuntimeError):
    """--apply was given without --live: refused (§64.1)."""


def _check_apply_requires_live(args: argparse.Namespace) -> None:
    if args.apply and not args.live:
        raise ApplyRequiresLive(
            "--apply cannot be used with --fixture: a fixture is not something you can "
            "mutate. --apply requires --live."
        )


def _fixture_root(args: argparse.Namespace) -> Path | None:
    if args.fixture is None:
        return None
    root = Path(__file__).resolve().parent.parent.parent / "reconciler" / "fixtures" / args.fixture
    if not root.is_dir():
        raise FileNotFoundError(f"no such fixture: {args.fixture!r} (looked under {root})")
    return root


def _run_operation(args: argparse.Namespace, operation: str, plan: Plan) -> int:
    """Common dry-run/apply plumbing shared by every subcommand.

    Every subcommand's *steps* differ; the apply/dry-run contract does
    not. This is the one place that decides whether a write step is
    allowed to actually run, and it is the one place `applied` is ever
    set True.
    """
    _check_apply_requires_live(args)
    applied = bool(args.apply and args.live)

    if applied:
        # Skeleton only (L3-P4-01): no per-operation step executor
        # exists yet. An empty plan has nothing to apply, so this is
        # never reached with steps pending; a later task that wires a
        # non-empty plan in here must execute each write step for
        # real before this can honestly report writes > 0.
        pass

    print(plan.summary_line(operation, applied=applied))
    if not applied:
        print(f"NOTE: dry-run (default) for {operation} -- pass --apply and --live to perform writes")
    return 0


def _cmd_create_product(args: argparse.Namespace) -> int:
    _fixture_root(args)
    # L3-P4-07: the real thirteen-automated/two-manual plan (spec §19.1),
    # composing L3-P4-02 .. -06. It needs a registry to read the current
    # product roster from (steps 11-13) - only --fixture supplies one
    # today, so --live still plans zero steps rather than guess at a
    # live roster no accessor here can read; that stays honest with
    # _run_operation's own rule that --apply --live never claims a write
    # no step here actually performed.
    if args.fixture is not None:
        from tools.provision.create_product import build_create_product_plan

        plan = build_create_product_plan(args.product, args.fixture)
    else:
        plan = Plan()
    return _run_operation(args, "create-product", plan)


def _cmd_add_person(args: argparse.Namespace) -> int:
    _fixture_root(args)
    # L3-P4-09: the real seven-step plan (spec 12.6, 12.1).
    from tools.provision.add_person import build_add_person_plan

    return _run_operation(args, "add-person", build_add_person_plan(args.login))


def _cmd_change_role(args: argparse.Namespace) -> int:
    _fixture_root(args)
    # L3-P7-01: the real seven-step plan (spec 12.6).
    from tools.provision.change_role import build_change_role_plan

    return _run_operation(args, "change-role", build_change_role_plan(args.login, args.to_role))


def _cmd_remove_person(args: argparse.Namespace) -> int:
    _fixture_root(args)
    # L3-P7-02: the real eleven-step plan (spec 12.2, 12.6).
    from tools.provision.remove_person import build_remove_person_plan

    return _run_operation(args, "remove-person", build_remove_person_plan(args.login))


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except (ApplyRequiresLive, FileNotFoundError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
