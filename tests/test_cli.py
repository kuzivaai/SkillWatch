"""Tests for the CLI interface."""

import tempfile
from pathlib import Path

from skillwatch.cli import main


class TestCLI:
    def _run(self, *args, db_path=None):
        """Run CLI with a temp database."""
        if db_path is None:
            db_path = tempfile.mktemp(suffix=".db")
        argv = ["--db", db_path] + list(args)
        return main(argv), db_path

    def test_version(self, capsys):
        import pytest
        with pytest.raises(SystemExit, match="0"):
            main(["--version"])
        captured = capsys.readouterr()
        assert "0.1.0" in captured.out

    def test_list_empty(self, capsys):
        code, _ = self._run("list")
        assert code == 0
        captured = capsys.readouterr()
        assert "0 URLs" in captured.out

    def test_add_url_and_list(self, capsys):
        db = tempfile.mktemp(suffix=".db")
        code, _ = self._run("add-url", "https://example.com/docs", db_path=db)
        assert code == 0

        code, _ = self._run("list", db_path=db)
        captured = capsys.readouterr()
        assert "example.com/docs" in captured.out
        assert "1 URLs" in captured.out

    def test_add_from_file(self, capsys):
        content = "# Skill\nSee [docs](https://example.com/setup).\n"
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write(content)
            f.flush()

            db = tempfile.mktemp(suffix=".db")
            code, _ = self._run("add", f.name, db_path=db)
            assert code == 0
            captured = capsys.readouterr()
            assert "example.com/setup" in captured.out

        Path(f.name).unlink()

    def test_add_ssrf_blocked(self, capsys):
        code, _ = self._run("add-url", "http://169.254.169.254/latest")
        assert code == 1
        captured = capsys.readouterr()
        assert "Blocked" in captured.err

    def test_remove_url(self, capsys):
        db = tempfile.mktemp(suffix=".db")
        self._run("add-url", "https://example.com/docs", db_path=db)
        code, _ = self._run("remove", "https://example.com/docs", db_path=db)
        assert code == 0

        code, _ = self._run("list", db_path=db)
        captured = capsys.readouterr()
        assert "0 URLs" in captured.out

    def test_remove_nonexistent(self, capsys):
        code, _ = self._run("remove", "https://nonexistent.com")
        assert code == 0
        captured = capsys.readouterr()
        assert "not found" in captured.out

    def test_alerts_empty(self, capsys):
        code, _ = self._run("alerts")
        assert code == 0
        captured = capsys.readouterr()
        assert "No open alerts" in captured.out

    def test_no_command_shows_help(self, capsys):
        code, _ = self._run()
        assert code == 0
