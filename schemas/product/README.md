# schemas/product — OWNED BY LANE 1 (Registries & Contracts)

Per-product contract schemas:
- Product Operating Contract      -> spec Section 15  (lines 1284-1606)
- Verification Contract           -> spec Section 31  (lines 2741-2802)
- Shared Service Contract         -> spec Section 20  (lines 2027-2112)

RULES
- Version fields per spec Section 60.2 (lines 5152-5214):
  product.yaml -> contract_version; verification/contract.yaml -> contract_version;
  service.yaml -> service_version.
- Additive only. No lane other than L1 writes here.
