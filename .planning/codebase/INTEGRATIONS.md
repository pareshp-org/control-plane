---
last_mapped_commit: c23a01076c25ff0b3f48404c5dbd702db1e8c9a1
last_mapped_at: 2026-09-16
---
# External Integrations

**Analysis Date:** 2026-09-16

## APIs & External Services

**GitHub REST API:**

- Service: GitHub organization and repository management
- What it's used for: Reading org members, team members, branch protection rules, environments, CODEOWNERS files, workflow files, tags, rulesets, bypass branches, and check runs
- SDK/Client: urllib.request (standard library) - custom implementation with Bearer token auth
- Auth: `GITHUB_TOKEN` environment variable (Personal Access Token required)
- API Version: 2022-11-28 (GitHub REST API v3)
- Endpoint: `https://api.github.com`
- Implementation: `reconciler/state/live_adapter.py` - LiveState class provides read-only GitHub API access
- Usage: 
  - `reconciler/state/live_adapter.py` - Phase 1 reconciler live mode (optional, not used in acceptance tests)
  - `validators/drift/credential_bounds.py` - Drift validator for credential verification
  - Other modules reference it for organization probing

**GitHub Actions:**

- Service: CI/CD pipeline orchestration
- What it's used for: Build, test, validation, and deployment workflows
- Implementation: `.github/workflows/` (16+ workflow files)
- Reusable workflows: `build.yml`, `concordance.yml`, `digest-gate.yml` 
- Triggers: Push events, pull requests, scheduled jobs, workflow dispatch
- Authentication: Uses GITHUB_TOKEN (provided by Actions runtime)

## Data Storage

**Local Filesystem (Primary):**

- Format: YAML files
- Registries: `registries/` directory (dir-per-item structure per FD-100)
- Records: `records/` directory (board, work metrics)
- Schemas: `schemas/registry/` (JSON Schema files)
- Fixtures: Test data in YAML format for reconciler testing
- No external database required

**Configuration Files (YAML):**

- `contracts/` - Contract definitions, event types, tag rulesets
- `infra/` - Infrastructure contracts and inputs
- `access/` - Access control definitions, environments, deployment policies
- `registries/` - Runtime registries (people, products, environments, economics, OS health)
- `records/` - Runtime metrics and records (board, work, restore records)

**JSON Storage:**

- `contracts/tag-ruleset.json` - GitHub tag ruleset configuration
- JSON Schema schemas in `schemas/registry/` for validation

## Authentication & Identity

**GitHub:**

- Auth Provider: GitHub (personal access token based)
- Implementation: Bearer token via `GITHUB_TOKEN` environment variable
- Scope Required: Read-only access to organization, teams, repositories, branch protection, environments, workflows
- Required Permissions (typical PAT scopes):
  - `repo` - Full control of private repositories
  - `admin:org_hook` - Hook administration
  - `admin:org` - Full control of organizations (may be restricted to read-only in practice)
- Token Format: `ghp_*` or `github_pat_*` patterns (detected in boundary checks)
- Usage Pattern:
  - Reconciler live adapter checks for GITHUB_TOKEN before making API calls
  - Raises `LiveAdapterDisabled` if token is not set
  - Optional: Can be passed directly to LiveState constructor (default uses environment variable)

**No identity provider integration detected:**

- No OAuth/OIDC integration
- No third-party authentication service
- Local GitHub org membership used for access control

## Monitoring & Observability

**Error Tracking:**

- Not detected - uses standard Python exception handling

**Logs:**

- Standard output logging via print statements and shell output
- Makefile targets include `validate`, `check`, and `metrics` with output to stdout
- GitHub Actions provides workflow logs
- No external logging service detected

**Audit:**

- Git commit history
- GitHub Actions workflow runs and logs
- Records stored in YAML files for audit trail

## CI/CD & Deployment

**Hosting:**

- GitHub (public repositories: `pareshp-org/control-plane`, `pareshp-org/control-plane-records`)

**CI Pipeline:**

- GitHub Actions (primary)
- Workflows:
  - `build.yml` - Reusable build workflow for artifact creation
  - `concordance.yml` - 5-lane concordance checks
  - `digest-gate.yml` - Digest verification gate
  - `lane-guard.yml` - Lane guard validation
  - `env-policy-assert.yml` - Environment policy assertions
  - Multiple phase-specific workflows (phase-0, phase-1, etc.)

**Deployment Commands:**

- `make phase0-dry` - Dry-run Phase 0 provisioning (requires GITHUB_TOKEN)
- `make check` - Run concordance + handover verification
- `make validate` - Run L1 validator CLI (Option B)

**Provisioning:**

- `scripts/provision/provision.sh` - Creates GitHub repositories and configuration
- `scripts/provision/check-prerequisites.sh` - Validates environment setup
- Phase 0: Provisions control plane, records repo, and base infrastructure

## Environment Configuration

**Required env vars for operations:**

- `GITHUB_TOKEN` - GitHub personal access token (required for live reconciler, provisioning, and CI operations)
- `CP_ROOT` - Control plane root directory (required by reconciler tests and tools)
- `CPR_ROOT` - Control plane records root directory (required by reconciler tests)

**Optional env vars:**

- `INVENTORY_DIR` - Path to inventory directory for expiry checks
- `DEADLINES_DIR` - Path to deadlines directory
- `INVENTORY_REPORT_DIR` - Output path for inventory reports
- `PRODUCT_REGISTRY_FILE` - Product registry file path
- `RESTORE_RECORD_DIR` - Restore record directory path
- `COMMIT_FILE_PATH` - Current commit file path (set by git hooks)

**Secrets location:**

- `GITHUB_TOKEN` - Must be set as environment variable or GitHub Actions secret
- No .env files detected (not committed; secrets separation via environment)
- No credential storage service integrated (GitHub Secrets, AWS Secrets Manager, etc.)

## Webhooks & Callbacks

**Incoming Webhooks:**

- Not detected - control plane is read-only to GitHub (only GET calls)

**Outgoing Webhooks:**

- GitHub Actions workflow dispatch - used to trigger dependent workflows
- No external webhook callbacks detected

**GitHub API Callbacks:**

- GitHub Actions provides automatic context/secrets injection
- No external callback handlers

## Rate Limiting & API Quotas

**GitHub API:**

- Uses unauthenticated API limits (60 req/hour) if GITHUB_TOKEN not set, raises error
- Authenticated requests: 5,000 req/hour per token
- Default timeout: 10 seconds per request (configurable in LiveState)
- No retry logic or exponential backoff detected (failures raise RuntimeError)

## Data Validation

**JSON Schema Validation:**

- Framework: jsonschema library
- Schema files: `schemas/registry/` (v1 schemas for each registry type)
- Validator: `validators/registry/rules/registry.py` implements rules R01-R18
- Validates:
  - Registry structure and content
  - Field types and constraints
  - Cross-registry references
  - Orphan detection (5 surfaces)

**YAML Validation:**

- PyYAML for parsing and serialization
- Schema-based validation in validators
- Contract validation in CI (lint_*.py scripts)

---

*Integration audit: 2026-09-16*
