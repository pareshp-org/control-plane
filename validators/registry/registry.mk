# registry.mk — Lane 1 (Registries & Contracts) make targets.
#
# Included by the ROOT Makefile, which is L0-owned under the frozen partition
# contract, with the single line:
#
#     -include validators/registry/registry.mk
#
# Lane 1 owns every target in this file. Phase L1-01 defines exactly four;
# phase L1-02 (subsystem B, Section 99.2) extends the same file and adds
# registry-schema-validate to the registry-verify chain.

REGISTRY_FILES := $(wildcard registries/*.yaml)
BASE_REF ?= origin/integration

.PHONY: registry-lint registry-append-only registry-inventory-check registry-verify

## registry-lint: every file in registries/ parses as YAML.
registry-lint:
	@test -n "$(REGISTRY_FILES)" || { echo "registry-lint: no registries/*.yaml found"; exit 1; }
	@python3 -c "import sys,yaml;[yaml.safe_load(open(f)) for f in sys.argv[1:]];print('REGISTRY_LINT_OK')" $(REGISTRY_FILES)

## registry-append-only: history was not destroyed (Sections 63.1, 97.2, invariant 47).
registry-append-only:
	@validators/registry/check-append-only.sh $(BASE_REF)

## registry-inventory-check: registries/INVENTORY.md still matches spec Section 52.6.
registry-inventory-check:
	@test -f registries/INVENTORY.md || { echo "registry-inventory-check: INVENTORY.md missing"; exit 1; }
	@rows=$$(awk '/^\| --- \| --- \| --- \|$$/{f=1;next} f&&/^\|/{c++} f&&!/^\|/{exit} END{print c+0}' registries/INVENTORY.md); \
	 test "$$rows" = "29" || { echo "registry-inventory-check: expected 29 rows, found $$rows (spec Section 52.6)"; exit 1; }; \
	 grep -q 'Table body sha256' registries/INVENTORY.md || { echo "registry-inventory-check: provenance stamp missing"; exit 1; }; \
	 echo "REGISTRY_INVENTORY_OK"

## registry-verify: the whole lane-1 gate. This is the target CI calls.
registry-verify: registry-lint registry-append-only registry-inventory-check
	@echo "REGISTRY_VERIFY_OK"
