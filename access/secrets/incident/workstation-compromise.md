# Containment: compromised engineering workstation

Section 43.4 lines 3928-3931, on the Section 43.1 flow. Malicious intent is not
assumed - the overwhelmingly likely cause is a phished credential or a
compromised device, and the mechanism is identical either way.

Order is not negotiable (Section 43.1):
DETECT -> CLASSIFY -> CONTAIN -> PRESERVE EVIDENCE -> ROTATE CREDENTIALS.

C-01 CONTAIN the person account: set access_status: suspended. One revocation
path, exercised for more than one reason.

C-02 CONTAIN the host reachability. Revoke EVERY cached session, SSH key and
private-path credential reaching the operations VM from that workstation.
Section 43.4 names the operations VM explicitly, because the second trust
boundary of Section 40.3 is what bounds this blast radius.

C-03 PRESERVE EVIDENCE before remediating: logs, audit records, artifact
digests, access history. Do not delete. Do not force-push.
Do not rotate before capturing. Rotation destroys the authentication trail you are about to need.

C-04 ROTATE EVERY FIFTH-TIER MACHINE CREDENTIAL - a named step, not an
inference. If the workstation held DevOps access, all five rotate:
reconciler, provisioning-cli, organisation-export-token, records-writer,
layer-b-backup. Each rotation runs the one-page runbook at
access/secrets/runbooks/rotate-fifth-tier-credential.md and is not done until
access/secrets/checks/rotation-complete.sh permits it - clean reconciliation,
AT-110 re-executed, re-escrow confirmed.

C-05 RE-REVIEW any change authored from that machine in the suspected window.

C-06 RE-RUN the API-key-free check on the rebuilt machine before it is used
again: bash access/secrets/checks/no-api-keys.sh

C-07 REVIEW the approved extension and MCP-server list of Section 36.3. It
exists precisely to keep this blast radius from silently growing; a compromise
is when it gets read, not when it gets written.

What this incident does NOT reach, and why that is a designed property rather
than luck: production (boundary 1, Section 40.3 line 3697) and - once C-02 and
C-04 complete - the control-plane machine-credential store (boundary 2, Section
40.3 line 3701, D95).
