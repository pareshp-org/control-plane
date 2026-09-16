# Operations-VM buildout request (ASSISTED)

**Task:** L5-T23 -- VM provisioning, private path, object-locked backup bucket.
**Why this is ASSISTED, not LANE:** every step below needs a cloud-console
session, a payment method already on file, or an SSH session to a host that
does not exist until this request is executed. No agent may create an
account, enter payment details, or provision billed cloud infrastructure
(see the platform's own credential/purchase rules) -- a human with console
and billing access must run this checklist and record the evidence below.

**What is already built and does not need re-doing here:**
- `ops-vm/stack/compose.shared.yml`, `ops-vm/stack/versions.env.example`,
  `ops-vm/provision/30-stack-up.sh` -- the stack that runs *once a host
  exists*.
- `infra/network/check-shell-gate.sh` -- the host-side SSH-hardening
  assertion this VM must satisfy once it is live (password auth off,
  keyboard-interactive off, root login off, pubkey-only).
- `infra/hosts/ops-vm.yaml`, `infra/hosts/layerb-host.yaml` -- the declared
  host shape this buildout must match.
- `infra/layer-b/provision-encrypted-volume.sh`, `check-separation.sh` --
  the Layer B store's own encrypted-volume and host-separation halves
  (Section 90.3, D95), already covered by L5-T51/L5-03-05/06.

**What this request is for -- the piece nothing above builds: the VM
itself, its private network path, and the object-locked backup bucket.**

## Checklist

1. **Cloud console access.** Confirm the human executing this holds console
   access to the account named in `infra/hosts/ops-vm.yaml`'s
   `provider`/`account` fields. Record the account id (not the credential)
   in the evidence file below.
2. **Payment method.** Confirm a payment method is already on file for that
   account (this request never enters one). Record only that a method
   exists (yes/no), never the instrument.
3. **VM provisioning.** Provision one host matching `infra/hosts/ops-vm.yaml`
   (CPU/RAM/disk floor, OS image, region). Record the instance id and
   region.
4. **Private network path (Section 51.4).** Place the host so that
   `infra/deadman/check-off-vm.sh` can truthfully assert it runs off the
   product infrastructure's own provider and off GitHub (D94) -- a separate
   VPC/network from every product's runtime, reachable only through the
   mesh/VPN this step also enrols. Record the network id and the VPN/mesh
   enrolment method.
5. **SSH enrolment.** SSH to the host once and run
   `infra/network/check-shell-gate.sh` over it (see the file's own header
   for the `ssh <host> 'bash -s' <` invocation). Record its PASS/FAIL
   output verbatim in the evidence file -- a FAIL here means the buildout
   is not done, not that the check needs relaxing.
6. **Object-locked backup bucket (Section 45.3, D54).** Create one bucket,
   in a **second credential domain** from the VM's own cloud account (never
   the same account holding the VM's compute credential -- Section 90.3's
   "the acceptance is stated in full or it is not an acceptance" applies
   here too: a backup target reachable by the same credential that can
   delete the VM is not a backup). Enable object lock / WORM at creation --
   it cannot be enabled retroactively on most providers. Record the bucket
   name, the credential-domain boundary (which account/role can write vs.
   which can delete), and the lock mode (governance/compliance) plus
   retention period.

## Evidence

Record the checklist results at `ops-vm/assisted/evidence/vm-buildout.md`
(template: `ops-vm/assisted/evidence/README.md`). Do not commit any
credential, access key, console password, or payment-instrument value --
account ids, instance ids, bucket names and check output only.
