# Per-product workflow caller templates — spec Sections 19.1, 33.2

`create-product` (Subsystem D, lane L3) copies these files into a new product
repository under `.github/workflows/`, substituting the `__UPPER_SNAKE__`
placeholders from `product.yaml`. The templates contain no logic: each is a
thin caller that consumes a reusable workflow from the control plane BY
PINNED TAG (Section 33.2, Section 33.3).

Required per repository (Section 33.2): ci.yml, build.yml, deploy-staging.yml,
deploy-production.yml, migrate.yml, restore-test.yml, restore-production.yml
wherever the product declares a `recovery:` block (Section 44.5), and
conditionally background-queue.yml.
