---
last_mapped_commit: c23a01076c25ff0b3f48404c5dbd702db1e8c9a1
last_mapped_at: 2026-09-16
---
# Technology Stack

**Analysis Date:** 2026-09-16

## Languages

**Primary:**

- Python 3.12+ - Core application logic, validators, tools, and scripts

## Runtime

**Environment:**

- Python 3.12+ (specified in `pyproject.toml`)

**Package Manager:**

- pip (PEP 517/518 via setuptools)
- Lockfile: Not detected (uses direct version constraints in `pyproject.toml`)

## Frameworks

**Core:**

- setuptools 67+ - Build backend and package discovery (`pyproject.toml`)
- wheel - Distribution format

**Testing:**

- pytest 7.0+ - Test runner and framework
- pytest-cov 4.0+ - Code coverage reporting (optional dependency)

**Build/Dev:**

- GitHub Actions - CI/CD orchestration (`.github/workflows/`)

## Key Dependencies

**Critical:**

- PyYAML 6.0+ - YAML parsing and serialization for configuration, registries, and fixtures (`pyproject.toml`)
- jsonschema 4.0+ - JSON Schema validation for registry and contract validation (`pyproject.toml`)
- referencing - JSON Schema reference resolution for complex schema validation (`validators/registry/tests/test_verification_schema.py`)

**Testing:**

- pytest (included in `dev` optional dependencies)
- pytest-cov (included in `dev` optional dependencies)

## Configuration

**Environment:**

- GITHUB_TOKEN - Personal access token for GitHub REST API calls (required for live reconciler operations)
- INVENTORY_DIR - Path to inventory directory (optional, used in `ops-vm/jobs/expiry_check.py`)
- DEADLINES_DIR - Path to deadlines directory (optional, used in `ops-vm/jobs/expiry_check.py`)
- PRODUCT_REGISTRY_FILE - Path to product registry file (optional, used in `ops-vm/jobs/restore_rotation.py`)
- COMMIT_FILE_PATH - Path to commit file (used in post-commit hooks)
- CP_ROOT - Control plane root directory path
- CPR_ROOT - Control plane records root directory path

**Build:**

- `pyproject.toml` - Project metadata, dependencies, setuptools configuration
- `pytest.ini` - Pytest configuration (test paths, naming patterns, output options)
- `Makefile` - Convenience targets for validation, testing, capacity planning
- `.github/dependabot.yml` - Automated dependency updates configuration

## Platform Requirements

**Development:**

- Python 3.12 or higher
- pip and setuptools installed
- Git (for pre-commit hooks)
- Make or Bash shell (for script execution)

**Production:**

- Python 3.12 runtime
- Deployment target: GitHub repository (uses GitHub REST API for read-only operations)
- No external databases or persistent storage backend required (uses local filesystem YAML files)

## Build System Details

**Package Layout:**

- Main package: `validators*` (includes validators.registry, validators.drift)
- Additional modules: `reconciler`, `access`, `assets`, `notify`, `tools`
- Test directory: `tests/`

**Build Command:**

```bash
python -m pip install -e .  # Install in editable mode
python -m pip install -e ".[dev]"  # With development dependencies
```

---

*Stack analysis: 2026-09-16*
