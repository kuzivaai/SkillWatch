"""Release gate controls checked using benign fixtures only."""

import importlib.util
import json
from datetime import date, timedelta
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
CHECK = ROOT / "scripts" / "readiness_consistency.py"
SPEC = importlib.util.spec_from_file_location("readiness_release_policy", CHECK)
assert SPEC and SPEC.loader
policy = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(policy)
DAY = date(2026, 11, 25)


class ReleaseGateTests(unittest.TestCase):
    def test_utc_date_and_verdict_boundaries(self):
        cases = [
            ("HOLD", 0, True, False),
            ("HOLD", 7, True, False),
            ("HOLD", 8, True, False),
            ("HOLD", 112, True, False),
            ("HOLD", -1, False, False),
            ("GO", 0, True, True),
            ("GO", 7, True, True),
            ("GO", 8, False, False),
            ("GO", -1, False, False),
            ("UNKNOWN", 8, False, False),
        ]
        for verdict, age, maintenance_passes, preflight_passes in cases:
            with self.subTest(verdict=verdict, age=age):
                status = {"verdict": verdict, "evaluated_at": (DAY - timedelta(days=age)).isoformat()}
                self.assertIs(not policy.readiness_date_errors(status, today=DAY), maintenance_passes)
                self.assertIs(not policy.publish_preflight_errors(status, today=DAY), preflight_passes)

    def test_bad_dates_block_both_paths(self):
        for value in [None, 20261125, "20261125", "2026-11-31", "2026-11-25T00:00:00Z"]:
            with self.subTest(value=value):
                status = {"verdict": "HOLD", "evaluated_at": value}
                self.assertTrue(policy.readiness_date_errors(status, today=DAY))
                self.assertTrue(policy.publish_preflight_errors(status, today=DAY))

    def test_cli_stops_at_hold_without_running_harness(self):
        with TemporaryDirectory() as tmp:
            script = Path(tmp) / "scripts" / CHECK.name
            script.parent.mkdir()
            script.write_bytes(CHECK.read_bytes())
            doc = Path(tmp) / "docs" / "readiness-status.json"
            doc.parent.mkdir()
            doc.write_text(
                json.dumps({"evaluated_at": policy.utc_today().isoformat(), "verdict": "HOLD"}),
                encoding="utf-8",
            )
            for arg in ["--publish-preflight", "--publish"]:
                with self.subTest(arg=arg):
                    # No harness exists: a traceback would not count as a correct rejection.
                    result = subprocess.run([sys.executable, str(script), arg], capture_output=True, text=True)
                    self.assertEqual(result.returncode, 1)
                    self.assertEqual(result.stdout, "FAIL: publishing requires a current GO verdict\n")
                    self.assertEqual(result.stderr, "")

    def test_fresh_go_does_not_bypass_evidence(self):
        with (
            patch.object(policy, "load_status", return_value={"evaluated_at": DAY.isoformat(), "verdict": "GO"}),
            patch.object(policy, "utc_today", return_value=DAY),
            patch.object(policy, "harness_metrics", side_effect=RuntimeError("evidence is unavailable")),
            patch("builtins.print"),
        ):
            self.assertEqual(policy.main(["--publish-preflight"]), 0)
            with self.assertRaisesRegex(RuntimeError, "evidence is unavailable"):
                policy.main(["--publish"])
