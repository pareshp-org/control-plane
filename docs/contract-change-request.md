# Contract Change Request (CCR) Procedure

A lane needing a change to `contracts/**` files a CCR and stops. Guessing is not correct behaviour.

## Template

```yaml
ccr_id: CCR-YYYY-NNN
filed_by: <lane>
date: <YYYY-MM-DD>
contract_id: <C-XXX-YYY-N>
blocked_contract: <id or none>
blocked_lanes: [<L1>, ...]
change_summary: |
  <one paragraph>
urgency: BLOCKING | HIGH | NORMAL
```

## SLA

L0 responds within 1 business day. Blocking CCRs are the highest-priority L0 emergency.
