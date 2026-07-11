"""Tests for external anchoring (RFC 3161).

Crypto tests use a REAL timestamp token captured from freeTSA.org and freeTSA's
real CA certificate (tests/fixtures/rfc3161/), so verification exercises the
actual library and signature path, not a mock.
"""

import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

pytest.importorskip("rfc3161_client")  # skip if the [anchor] extra is absent

from skillwatch import anchoring  # noqa: E402
from skillwatch import ledger as _led  # noqa: E402
from skillwatch.cli import main  # noqa: E402
from skillwatch.store import Store  # noqa: E402

_FIX = Path(__file__).parent / "fixtures" / "rfc3161"
HEAD_A = "a" * 64  # the token below was issued over this exact message
TOKEN = (_FIX / "token_a64.tsr").read_bytes()
CACERT = (_FIX / "freetsa_cacert.pem").read_bytes()


@pytest.fixture
def store():
    with tempfile.TemporaryDirectory() as d:
        with Store(db_path=Path(d) / "t.db") as s:
            yield s


def _seed(store, n=3):
    url_id, _ = store.add_url("https://example.com/x", "manual")
    for i in range(n):
        store.add_snapshot(url_id, f"h{i}", f"v{i}", status_code=200)
    return store.verify_ledger().head


class TestRfc3161Crypto:
    def test_available(self):
        assert anchoring.anchoring_available() is True

    def test_verifies_real_token_for_correct_head(self):
        assert anchoring.verify_anchor(HEAD_A, "rfc3161", TOKEN, CACERT) is True

    def test_rejects_wrong_head(self):
        assert anchoring.verify_anchor("b" * 64, "rfc3161", TOKEN, CACERT) is False

    def test_rejects_empty_proof(self):
        assert anchoring.verify_anchor(HEAD_A, "rfc3161", b"", CACERT) is False

    def test_bundled_cacert_verifies(self):
        # cacert_pem=None uses the CA cert bundled in the package.
        assert anchoring.verify_anchor(HEAD_A, "rfc3161", TOKEN, None) is True

    def test_anchor_head_posts_and_parses(self):
        resp = Mock()
        resp.content = TOKEN
        resp.raise_for_status = Mock()
        # Public IP literal: passes SSRF validation without a DNS lookup.
        with patch("requests.post", return_value=resp) as post:
            result = anchoring.anchor_head(HEAD_A, tsa_url="http://1.1.1.1/tsr")
        assert post.called
        assert result.method == "rfc3161"
        assert result.proof == TOKEN
        assert result.timestamp  # gen_time parsed from the token

    def test_unknown_method_raises(self):
        with pytest.raises(anchoring.AnchorError):
            anchoring.anchor_head(HEAD_A, method="bogus")

    def test_verify_unknown_method_raises(self):
        with pytest.raises(anchoring.AnchorError):
            anchoring.verify_anchor(HEAD_A, "bogus", b"x")

    def test_refuses_private_tsa(self):
        # SSRF: must not POST to a link-local / metadata address.
        with pytest.raises(anchoring.AnchorError):
            anchoring.anchor_head(HEAD_A, tsa_url="http://169.254.169.254/tsr")

    def test_network_error_is_actionable(self):
        import requests as _rq
        with patch("requests.post", side_effect=_rq.RequestException("boom")):
            with pytest.raises(anchoring.AnchorError):
                anchoring.anchor_head(HEAD_A, tsa_url="http://1.1.1.1/tsr")


class TestAnchorStore:
    def test_record_get_latest(self, store):
        rid = store.record_anchor(3, HEAD_A, "rfc3161", "https://tsa", b"xx", "2026-07-11")
        assert rid > 0
        anchors = store.get_anchors()
        assert len(anchors) == 1
        assert anchors[0]["head"] == HEAD_A
        assert anchors[0]["proof"] == b"xx"
        assert store.anchor_count() == 1
        assert store.latest_anchor()["head"] == HEAD_A


class TestAnchorCommand:
    def test_records_and_writes_proof(self, store, tmp_path):
        _seed(store, 3)
        db = str(store.db_path)
        store.close()
        resp = Mock()
        resp.content = TOKEN
        resp.raise_for_status = Mock()
        out = tmp_path / "proof.tsr"
        with patch("requests.post", return_value=resp):
            code = main(["--db", db, "anchor", "--tsa", "http://1.1.1.1/tsr", "--out", str(out)])
        assert code == 0
        assert out.read_bytes() == TOKEN
        with Store(db_path=db) as s:
            assert s.anchor_count() == 1

    def test_empty_ledger_cannot_anchor(self, tmp_path):
        code = main(["--db", str(tmp_path / "e.db"), "anchor"])
        assert code == 1

    def test_unavailable_extra_is_actionable(self, store, monkeypatch, capsys):
        _seed(store, 2)
        db = str(store.db_path)
        store.close()
        monkeypatch.setattr(anchoring, "anchoring_available", lambda: False)
        code = main(["--db", db, "anchor"])
        assert code == 1
        assert "skillwatch[anchor]" in capsys.readouterr().err


class TestVerifyAutoChecksAnchors:
    def test_present_anchor_head_in_chain(self, store, capsys):
        head = _seed(store, 3)
        store.record_anchor(3, head, "manual", proof=b"")
        db = str(store.db_path)
        store.close()
        code = main(["--db", db, "verify"])
        out = capsys.readouterr().out
        assert code == 0
        assert "Anchor present" in out

    def test_diverged_anchor_detected(self, store, capsys):
        _seed(store, 3)
        store.record_anchor(3, "0" * 64, "manual", proof=b"")  # head not in chain
        db = str(store.db_path)
        store.close()
        code = main(["--db", db, "verify"])
        out = capsys.readouterr().out
        assert code == 1
        assert "DIVERGED" in out

    def test_crypto_anchor_verified_through_cli(self, store, capsys, monkeypatch):
        # Record a real rfc3161 anchor, then simulate its head being the current,
        # in-chain head so the REAL crypto verification runs via the CLI path.
        _seed(store, 2)
        store.record_anchor(2, HEAD_A, "rfc3161", "https://freetsa.org/tsr", TOKEN, "2026-07-11")
        db = str(store.db_path)
        store.close()
        monkeypatch.setattr(
            Store, "verify_ledger",
            lambda self: _led.LedgerVerification(ok=True, entries=2, head=HEAD_A),
        )
        monkeypatch.setattr(Store, "ledger_contains_hash", lambda self, h: h == HEAD_A)
        code = main(["--db", db, "verify"])
        out = capsys.readouterr().out
        assert code == 0
        assert "Anchor verified" in out


class TestGitAnchor:
    """The git backend commits the head to a repo — an independent, timestamped,
    pushable anchor that needs no timestamp authority and no extra dependencies."""

    @staticmethod
    def _init_repo(path):
        import subprocess
        subprocess.run(["git", "-C", str(path), "init", "-q"], check=True)
        subprocess.run(["git", "-C", str(path), "config", "user.email", "t@example.com"], check=True)
        subprocess.run(["git", "-C", str(path), "config", "user.name", "Test"], check=True)

    def test_module_commits_and_returns_sha(self, tmp_path):
        repo = tmp_path / "r"
        repo.mkdir()
        self._init_repo(repo)
        result = anchoring.anchor_head("c" * 64, method="git", repo_path=str(repo))
        assert result.method == "git"
        assert result.external_ref  # commit sha
        assert result.timestamp  # commit ISO time
        assert "c" * 64 in (repo / ".skillwatch-anchors.log").read_text()

    def test_cli_git_anchor_records(self, store, tmp_path):
        repo = tmp_path / "repo"
        repo.mkdir()
        self._init_repo(repo)
        head = _seed(store, 2)
        db = str(store.db_path)
        store.close()
        code = main(["--db", db, "anchor", "--method", "git", "--repo", str(repo)])
        assert code == 0
        assert head in (repo / ".skillwatch-anchors.log").read_text()
        with Store(db_path=db) as s:
            a = s.latest_anchor()
            assert a["method"] == "git" and a["head"] == head and a["external_ref"]

    def test_requires_a_git_repo(self, store, tmp_path):
        _seed(store, 1)
        db = str(store.db_path)
        store.close()
        code = main(["--db", db, "anchor", "--method", "git", "--repo", str(tmp_path / "nope")])
        assert code == 1

    def test_verify_shows_git_anchor(self, store, tmp_path, capsys):
        repo = tmp_path / "repo3"
        repo.mkdir()
        self._init_repo(repo)
        _seed(store, 2)
        db = str(store.db_path)
        store.close()
        main(["--db", db, "anchor", "--method", "git", "--repo", str(repo)])
        capsys.readouterr()
        code = main(["--db", db, "verify"])
        out = capsys.readouterr().out
        assert code == 0
        assert "Anchor present" in out and "git" in out
