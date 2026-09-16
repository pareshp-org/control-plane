# Shared Grafana instance - datasource rule

The people-performance datasource is **never** registered in this instance.

> "The people datasource is never registered in the shared instance; the Layer B
> boundary is instance separation, not folder membership. Folder ACLs in the
> shared instance remain defence in depth for Layer A views only."
> - Master Specification v4.0, Section 90.3 (D75)

Adding a people datasource entry here, or a dashboard in this instance that
references one, fails AT-097 and breaks invariant 109. The check that enforces
this is `access/layer-b/at-097-no-people-datasource-in-shared.sh` and it runs in
the People-tier gate (L5-03-12).
