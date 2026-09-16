# schemas/registry — OWNED BY LANE 1 (Registries & Contracts)

Subsystem A of spec Section 99.2 (lines 9184-9231).
JSON Schema documents for the control-plane registries listed in spec Section 52.6 (lines 4613-4648).

RULES
- Additive only. A `*.vN.schema.json` file is NEVER deleted or overwritten once merged
  (spec Section 60.2, lines 5152-5214: "Write the v2 schema alongside v1 - do not replace").
- No person identifier, product identifier or product count appears in any enum
  (spec Section 4.3, lines 243-257; invariants 51 and 52).
- No lane other than L1 writes here.
