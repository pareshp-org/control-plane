# ASSISTED — per-person public-key registration and annual re-key

**L0 EXECUTES.** This document is the handoff; it is not the key exchange.

## Why this is not the executor's to do

Section 90.6 (quoted in full in `lanes/L5-03-layer-b.md`, task L5-03-10) fixes
the mechanism the self-view generator
(`ops-vm/layer-b/selfview/generate-selfview.sh`) and the registry
(`ops-vm/layer-b/selfview/pubkey-registry.yaml`) already implement: "the
person holds the private half ... and only the public half is registered at
onboarding." Registering a real person's public key means exchanging key
material with a real, named individual and confirming their identity —
exactly the kind of action this session's permission rules keep out of an
automated agent's hands, and exactly what L5-03-10's own escalation table
(`E-P3-02`) already routes to L0/L1: "the onboarding checklist item that
registers a person's public half ... is L0's onboarding track; the registry
is L1's."

## What to do, per person, at onboarding

1. Confirm the person's identity out of band (the same channel the rest of
   onboarding already uses).
2. Obtain the **public half only** of their existing hardware key or
   equivalent personal identity. The private half never leaves the person's
   possession and is never requested.
3. Register the public half in `ops-vm/layer-b/selfview/pubkey-registry.yaml`
   at the entry matching that person's login, following the shape the file
   already declares.
4. Confirm `ops-vm/layer-b/selfview/generate-selfview.sh` can encrypt to the
   newly registered key (`--dry-run` against a synthetic document is
   sufficient; it must never be run against real content as a registration
   test).

## Annual re-key, and the lost-device path

Section 90.6: "Registered material is re-keyed annually, and immediately on a
lost-device or compromised-workstation report under Section 43.4, each re-key
recorded as a decision."

- **Annual cadence** — repeat steps 1–4 for every registered person once a
  year; `ops-vm/layer-b/selfview/rekey-check.sh` reports which registrations
  are due.
- **Lost-device / compromised-workstation trigger** — re-key immediately,
  out of cycle, the moment
  `access/secrets/incident/workstation-compromise.md` names that person.
- **Recording the re-key as a decision** — decision records live in
  `records/decisions/`, owned by L4 (this is L5-03-10's escalation
  `E-P3-03`). This document does not write there; it is the trigger that
  tells whoever executes the re-key that a decision record is now due.

## Checklist for whoever executes this

- [ ] Person's identity confirmed out of band
- [ ] Public key half obtained (never the private half)
- [ ] Entry added or updated in
      `ops-vm/layer-b/selfview/pubkey-registry.yaml`
- [ ] `ops-vm/layer-b/selfview/rekey-check.sh` run and clean for this person
- [ ] Re-key recorded as a decision in `records/decisions/` (L4's write path)

## STOP rule

If asked to hold, transmit, or store a private key half on this person's
behalf — refuse. Section 90.6's entire design is that "the Founder session
therefore holds nothing that decrypts anyone's self-view." Holding a private
half anywhere in this pipeline defeats the property the section exists to
guarantee. File the blocker issue (escalation `E-P3-02`) instead.
