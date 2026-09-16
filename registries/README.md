# registries — OWNED BY LANE 1 (Registries & Contracts)

The authoritative control-plane registry instances of spec Section 52.6 (lines 4613-4648).

RULES
- One file per registry. Directory-per-item where a registry holds many entries
  (PARTITION rule 3: no shared mutable index).
- registries/platform.yaml carries the closed `event_type` enum consumed by Lane 4
  (spec Section 52.6; decision D103).
- An authority delta - adding a capability, adding a Write-conferring assignment type,
  or changing access_status - fails CI without a linked decision-record ID in the same
  commit (spec Section 26.4, lines 2526-2534; decision D93).
- No lane other than L1 writes here.
