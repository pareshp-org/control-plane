"""Generate Prometheus file-SD scrape targets for MultiProduct services.

Spec: Section 41.2, Section 103.3; Invariant 52 (Targets are generated from the
product registry, never hand-listed).
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List

CONTROL_PLANE_ROOT = Path(__file__).resolve().parent.parent.parent
WORKSPACE_ROOT = CONTROL_PLANE_ROOT.parent.parent
DEFAULT_PRODUCTS_DIR = WORKSPACE_ROOT / "products"
DEFAULT_OUTPUT_PATH = CONTROL_PLANE_ROOT / "ops-vm" / "prometheus" / "targets" / "products.json"


def discover_products(products_dir: Path) -> List[Dict[str, Any]]:
    """Enumerate products dynamically from the workspace products directory."""
    products = []
    if not products_dir.is_dir():
        # Fallback to standard 8 products
        for i in range(1, 9):
            products.append({
                "product_id": f"Product-{i}",
                "port": 8080 + i,
                "profile": "service",
            })
        return products

    for pdir in sorted(products_dir.glob("Product-*")):
        if pdir.is_dir():
            product_id = pdir.name
            # Determine port from number or default
            try:
                num = int(product_id.split("-")[-1])
                port = 8080 + num
            except Exception:
                port = 8080
            products.append({
                "product_id": product_id,
                "port": port,
                "profile": "service",
                "path": str(pdir),
            })
    return products


def generate_targets(products: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Convert discovered products into Prometheus file-SD configuration."""
    target_groups = []
    for p in products:
        port = p["port"]
        pid = p["product_id"]
        group = {
            "targets": [
                f"127.0.0.1:{port}",
                f"host.docker.internal:{port}",
            ],
            "labels": {
                "job": "product-health",
                "product": pid,
                "profile": p.get("profile", "service"),
                "environment": "development",
            },
        }
        target_groups.append(group)
    return target_groups


def write_targets(output_path: Path, targets: List[Dict[str, Any]]) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    content = json.dumps(targets, indent=2) + "\n"
    output_path.write_text(content, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate Prometheus file-SD target configuration for products."
    )
    parser.add_argument(
        "--products-dir",
        type=Path,
        default=DEFAULT_PRODUCTS_DIR,
        help="Path to products directory",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT_PATH,
        help="Path to write Prometheus targets JSON",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print generated targets without writing to disk",
    )

    args = parser.parse_args()
    products = discover_products(args.products_dir)
    targets = generate_targets(products)

    if args.dry_run:
        print(json.dumps(targets, indent=2))
    else:
        write_targets(args.output, targets)
        print(f"Generated Prometheus targets for {len(targets)} products -> {args.output}")


if __name__ == "__main__":
    main()
