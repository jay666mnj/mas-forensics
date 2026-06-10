from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from forensic_agent import run_demo


class DemoFlowTest(unittest.TestCase):
    def test_demo_flow_generates_traceable_report(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            result = run_demo(workspace=Path(tmpdir))
            report = result["report"]
            self.assertIn("取证分析报告草稿", report)
            self.assertIn("证据", report)
            self.assertIn("反向范围建议", report)
            self.assertGreaterEqual(len(result["findings"]), 1)
            self.assertIn("actors", result["reverse_scope"])
            self.assertEqual(result["review_issues"], [])
            self.assertTrue(Path(result["audit_path"]).exists())
            self.assertTrue(Path(result["report_path"]).exists())


if __name__ == "__main__":
    unittest.main()
