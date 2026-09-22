"""Unit tests for tools.provision.generate_prometheus_targets."""

import json
import tempfile
import unittest
from pathlib import Path

from tools.provision.generate_prometheus_targets import (
    discover_products,
    generate_targets,
    write_targets,
)


class TestGeneratePrometheusTargets(unittest.TestCase):
    def test_discover_products_fallback(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            empty_path = Path(tmpdir) / "nonexistent"
            products = discover_products(empty_path)
            self.assertEqual(len(products), 8)
            self.assertEqual(products[0]["product_id"], "Product-1")
            self.assertEqual(products[0]["port"], 8081)

    def test_generate_and_write_targets(self) -> None:
        sample_products = [
            {"product_id": "Product-1", "port": 8081, "profile": "service"},
            {"product_id": "Product-2", "port": 8082, "profile": "service"},
        ]
        targets = generate_targets(sample_products)
        self.assertEqual(len(targets), 2)
        self.assertEqual(targets[0]["labels"]["product"], "Product-1")
        self.assertIn("127.0.0.1:8081", targets[0]["targets"])

        with tempfile.TemporaryDirectory() as tmpdir:
            out_file = Path(tmpdir) / "targets" / "test_products.json"
            write_targets(out_file, targets)
            self.assertTrue(out_file.is_file())
            loaded = json.loads(out_file.read_text(encoding="utf-8"))
            self.assertEqual(len(loaded), 2)
            self.assertEqual(loaded[1]["labels"]["product"], "Product-2")


if __name__ == "__main__":
    unittest.main()
