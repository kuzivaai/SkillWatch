"""Tests for the CLI interface."""

from pathlib import Path
import tempfile

import pytest

from skillwatch.cli import main


@pytest.fixture
def db_path(tmp_path):
    return str(tmp_path / "test.db")


class TestCLI:
    def _run(self, *args, db_path=None):
        """Run CLI with a temp database."""
        if db_path is None:
            db_path = str(Path(tempfile.mkdtemp()) / "test.db")
        argv = ["--db", db_path] + list(args)
        return main(argv), db_path

    def test_version(self, capsys):
        with pytest.raises(SystemExit, match="0"):
            main(["--version"])
        captured = capsys.readouterr()
        assert "0.1.0" in captured.out

    def test_list_empty(self, db_path, capsys):
        code, _ = self._run("list", db_path=db_path)
        assert code == 0
        captured = capsys.readouterr()
        assert "0 URLs" in captured.out

    def test_add_url_and_list(self, db_path, capsys):
        code, _ = self._run("add-url", "https://example.com/docs", db_path=db_path)
        assert code == 0

        code, _ = self._run("list", db_path=db_path)
        captured = capsys.readouterr()
        assert "example.com/docs" in captured.out
        assert "1 URLs" in captured.out

    def test_add_from_file(self, db_path, capsys):
        content = "# Skill\nSee [docs](https://example.com/setup).\n"
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write(content)
            f.flush()

            code, _ = self._run("add", f.name, db_path=db_path)
            assert code == 0
            captured = capsys.readouterr()
            assert "example.com/setup" in captured.out

        Path(f.name).unlink()

    def test_add_ssrf_blocked(self, db_path, capsys):
        code, _ = self._run("add-url", "http://169.254.169.254/latest", db_path=db_path)
        assert code == 1
        captured = capsys.readouterr()
        assert "Blocked" in captured.err

    def test_remove_url(self, db_path, capsys):
        self._run("add-url", "https://example.com/docs", db_path=db_path)
        code, _ = self._run("remove", "https://example.com/docs", db_path=db_path)
        assert code == 0

        code, _ = self._run("list", db_path=db_path)
        captured = capsys.readouterr()
        assert "0 URLs" in captured.out

    def test_remove_nonexistent(self, db_path, capsys):
        code, _ = self._run("remove", "https://nonexistent.com", db_path=db_path)
        assert code == 0
        captured = capsys.readouterr()
        assert "not found" in captured.out

    def test_alerts_empty(self, db_path, capsys):
        code, _ = self._run("alerts", db_path=db_path)
        assert code == 0
        captured = capsys.readouterr()
        assert "No open alerts" in captured.out

    def test_no_command_shows_help(self, db_path, capsys):
        code, _ = self._run(db_path=db_path)
        assert code == 0
