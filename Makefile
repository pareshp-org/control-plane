# Makefile — Multi-Product Engineering OS convenience targets
# Usage: make <target>
# FD-082: task IDs normalized to L<N>-<FF>-<NN> format

.PHONY: help check concordance handover canary validate test phase0-dry setup capacity schedule-check ready-queue lint metrics orphans

# Default target
help:
	@echo "Multi-Product Engineering OS — Make targets"
	@echo ""
	@echo "  check        Run concordance check (5-lane) + verify_handover"
	@echo "  concordance  Run concordance check only"
	@echo "  handover     Run verify_handover.sh only"
	@echo "  canary       Check registry canary sentinel"
	@echo "  validate     Run L1 validator CLI (Option B)"
	@echo "  phase0-dry   Dry-run Phase 0 (creates no resources)"
	@echo "  setup        Install git hooks"
	@echo "  capacity     L4 capacity model for current month (FD-089/FD-090)"
	@echo "  schedule-check L4 floor obligation check for current month (FD-031)"
	@echo "  ready-queue  L4 ready queue miss check (FD-091/PFD-017)"
	@echo ""

check: concordance handover
	@echo "=== All checks passed ==="

concordance:
	bash _concordance-check.sh lanes

handover:
	bash ../verify_handover.sh 2>/dev/null || bash ../../verify_handover.sh

canary:
	bash scripts/canary-check.sh registries/people/_canary.yaml

validate:
	python -m validators.registry.cli \
		--root . \
		--as-of $(shell date +%Y-%m-%d) \
		--records-root records/ \
		--format json

test:
	python -m pytest tests/ -v --tb=short

metrics:
	bash scripts/metrics/validate-metrics.sh

orphans:
	bash scripts/orphan-detect.sh .

phase0-dry:
	@echo "Setting GITHUB_TOKEN is required. Run:"
	@echo "  \$$env:GITHUB_TOKEN = 'your-pat'; bash run-phase-0.sh --dry-run"
	@echo ""
	@echo "Pre-flight check:"
	bash scripts/provision/check-prerequisites.sh

setup:
	@echo "Installing git hooks..."
	@mkdir -p .git/hooks
	@cp scripts/git-hooks/pre-commit .git/hooks/pre-commit 2>/dev/null && chmod +x .git/hooks/pre-commit || echo "No pre-commit hook found"
	@cp scripts/git-hooks/commit-msg .git/hooks/commit-msg 2>/dev/null && chmod +x .git/hooks/commit-msg || echo "No commit-msg hook found"
	@echo "Done."

lint:
	python -m py_compile validators/registry/cli.py && echo "Python lint: OK"
	python -m py_compile validators/registry/rules/registry.py && echo "Rule registry lint: OK"

capacity:
	python scripts/l4/capacity-model.py --period $(shell date +%Y-%m) --output text

schedule-check:
	python scripts/l4/scheduling.py --check --period $(shell date +%Y-%m)

ready-queue:
	bash scripts/l4/ready-queue.sh --check
