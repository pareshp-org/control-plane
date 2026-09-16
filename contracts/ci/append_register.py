#!/usr/bin/env python3
"""append_register.py CONTRACT_ID PATH VERSION OWNER PUB_LANE CONSUMERS STUB
Appends one row to contracts/register.yaml. Idempotent: skips if id already present.
"""
import sys, yaml, pathlib

REG = pathlib.Path("contracts/register.yaml")
args = sys.argv[1:]
if len(args) < 7:
    print("Usage: append_register.py ID PATH VER OWNER PUB_LANE CONSUMERS STUB", file=sys.stderr)
    sys.exit(1)

cid, path, ver, owner, pub_lane, consumers_raw, stub = args
consumers = [c.strip() for c in consumers_raw.split(",")]
data = yaml.safe_load(REG.read_text()) or {"contracts": []}
existing_ids = [r["id"] for r in data["contracts"]]
if cid in existing_ids:
    print(f"skip: {cid} already in register")
    sys.exit(0)
data["contracts"].append({
    "id": cid,
    "path": path,
    "version": int(ver),
    "owner": owner,
    "publishing_lane": pub_lane,
    "consuming_lanes": consumers,
    "stub": stub,
})
REG.write_text(yaml.dump(data, default_flow_style=False, sort_keys=False))
if stub:
    # verify_contracts.py resolves "stub" relative to the contracts/ dir
    # (ROOT = pathlib.Path(__file__).parent.parent from contracts/ci/), and
    # this script runs with cwd set to the repo root ($CP), same as REG
    # above, so the stub file must be created under contracts/, not
    # directly under cwd.
    stub_path = pathlib.Path("contracts") / stub
    stub_path.parent.mkdir(parents=True, exist_ok=True)
    if not stub_path.exists():
        stub_path.write_text(
            f"# STUB — placeholder for {cid}\n"
            "# Auto-created by contracts/ci/append_register.py at registration time.\n"
            "# Full content is authored progressively (see the \"path\" field in\n"
            "# contracts/register.yaml for where the real schema/content lives,\n"
            "# and the Phase 1 tasks for the owning lane for when it gets fully\n"
            "# authored).\n"
            "stub: true\n"
            f"contract_id: {cid}\n"
            f"registered_path: {path}\n"
        )
print(f"appended: {cid}")
