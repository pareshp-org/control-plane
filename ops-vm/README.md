# Operations VM

Subsystem M (spec Section 99.2). Runs: DevLake, Grafana, reconciliation, health
computation, Scorecard, Renovate, expiry checks, restore rotation, org export.

Binding rules, taken from the specification — none is negotiable here:

* Disposable. Everything on this host is provisioned from this repository. Its
  complete loss is a tested under-4-hour rebuild (Section 45.4), not a
  catastrophe (Section 51.5).
* Never in a product runtime path. Invariants 75 and 76; Section 51.3.
* No production credentials, no deploy keys, no environment access. It does hold
  the fifth-tier machine-credential store of Section 40.1 - the reconciler
  credential and the organisation-export token among them - which is why shell
  access to this host is not an infrastructure detail (Section 40.3).
* Not its own witness. Prometheus, alert evaluation and Grafana all die with the
  host, so machine detection carries an off-VM leg: the external per-product
  uptime check and the dead-man's-switch heartbeat of Section 51.5 and D94.
* No CI runner lives here (Section 49.1): Section 45.2's "CI keeps running when
  the VM is lost" depends on that placement.
* The background machine layer does not run here. It has its own dedicated host
  (Section 37) and the two hosts share no credentials (Section 51.5).
