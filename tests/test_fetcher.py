"""Tests for the URL fetcher with HTTP mocking."""

from unittest.mock import patch

import requests as req_lib
import responses

from skillwatch.fetcher import fetch_url, strip_escape_sequences, _normalise_whitespace
from .conftest import MOCK_IP, mock_validate_url

# All HTTP mock tests patch validate_url to skip real DNS and return MOCK_IP.
# responses library mocks must be registered against https://{MOCK_IP}/path.
_VALIDATE = "skillwatch.fetcher.validate_url"


class TestStripEscapeSequences:
    def test_strips_csi(self):
        text = "hello \x1b[31mred\x1b[0m world"
        assert strip_escape_sequences(text) == "hello red world"

    def test_strips_osc_bel_terminated(self):
        text = "before \x1b]52;c;SGVsbG8=\x07 after"
        assert strip_escape_sequences(text) == "before  after"

    def test_strips_osc_st_terminated(self):
        text = "before \x1b]8;;https://evil.com\x1b\\ after"
        assert strip_escape_sequences(text) == "before  after"

    def test_strips_dcs(self):
        text = "before \x1bPsome DCS data\x1b\\ after"
        assert strip_escape_sequences(text) == "before  after"

    def test_strips_c1_csi(self):
        text = "before \x9b31m after"
        assert strip_escape_sequences(text) == "before  after"

    def test_strips_c1_osc(self):
        text = "before \x9dsome data\x9c after"
        assert strip_escape_sequences(text) == "before  after"

    def test_strips_fe_sequences(self):
        text = "before \x1bM after"
        assert strip_escape_sequences(text) == "before  after"

    def test_preserves_normal_text(self):
        text = "Hello, this is normal text with [brackets] and numbers 123."
        assert strip_escape_sequences(text) == text

    def test_empty_string(self):
        assert strip_escape_sequences("") == ""


class TestNormaliseWhitespace:
    def test_collapses_spaces(self):
        assert _normalise_whitespace("hello   world") == "hello world"

    def test_strips_blank_lines(self):
        assert _normalise_whitespace("hello\n\nworld") == "hello\nworld"

    def test_strips_trailing_whitespace(self):
        assert _normalise_whitespace("hello   \nworld  ") == "hello\nworld"

    def test_empty_string(self):
        assert _normalise_whitespace("") == ""


class TestFetchUrlSSRF:
    def test_blocks_private_ip(self):
        result = fetch_url("http://192.168.1.1/admin")
        assert not result.ok
        assert "private" in result.error.lower() or "Blocked" in result.error

    def test_blocks_loopback(self):
        result = fetch_url("http://127.0.0.1:8080/")
        assert not result.ok
        assert "Blocked" in result.error

    def test_blocks_metadata_endpoint(self):
        result = fetch_url("http://169.254.169.254/latest/meta-data/")
        assert not result.ok

    def test_blocks_file_scheme(self):
        result = fetch_url("file:///etc/passwd")
        assert not result.ok
        assert "scheme" in result.error.lower()

    def test_blocks_ipv4_mapped_ipv6(self):
        result = fetch_url("http://[::ffff:127.0.0.1]/")
        assert not result.ok


class TestFetchUrlHTTP:
    @responses.activate
    def test_fetches_html_page(self):
        responses.add(
            responses.GET, f"https://{MOCK_IP}/docs",
            body="<html><body><p>Hello world documentation.</p></body></html>", status=200,
        )
        with patch(_VALIDATE, side_effect=mock_validate_url):
            result = fetch_url("https://example.com/docs")
        assert result.ok
        assert result.status_code == 200
        assert result.content_hash
        assert result.raw_html_hash

    @responses.activate
    def test_handles_http_404(self):
        responses.add(responses.GET, f"https://{MOCK_IP}/missing", status=404)
        with patch(_VALIDATE, side_effect=mock_validate_url):
            result = fetch_url("https://example.com/missing")
        assert not result.ok
        assert result.status_code == 404
        assert "404" in result.error

    @responses.activate
    def test_handles_http_500(self):
        responses.add(responses.GET, f"https://{MOCK_IP}/error", status=500)
        with patch(_VALIDATE, side_effect=mock_validate_url):
            result = fetch_url("https://example.com/error")
        assert not result.ok
        assert "500" in result.error

    @responses.activate
    def test_handles_connection_error(self):
        responses.add(
            responses.GET, f"https://{MOCK_IP}/slow",
            body=req_lib.exceptions.ConnectionError("Connection refused"),
        )
        with patch(_VALIDATE, side_effect=mock_validate_url):
            result = fetch_url("https://example.com/slow", timeout=1)
        assert not result.ok
        assert "error" in result.error.lower() or "connection" in result.error.lower()

    @responses.activate
    def test_enforces_size_limit(self):
        responses.add(
            responses.GET, f"https://{MOCK_IP}/large",
            body="x" * 2000, status=200,
        )
        with patch(_VALIDATE, side_effect=mock_validate_url):
            result = fetch_url("https://example.com/large", max_size=1000)
        assert not result.ok
        assert "exceeds" in result.error.lower()

    @responses.activate
    def test_follows_redirects_safely(self):
        responses.add(
            responses.GET, f"https://{MOCK_IP}/old",
            status=301, headers={"Location": "https://example.com/new"},
        )
        responses.add(
            responses.GET, f"https://{MOCK_IP}/new",
            body="<html><body><p>New page content here.</p></body></html>", status=200,
        )
        with patch(_VALIDATE, side_effect=mock_validate_url):
            result = fetch_url("https://example.com/old")
        assert result.ok

    @responses.activate
    def test_blocks_redirect_to_private_ip(self):
        responses.add(
            responses.GET, f"https://{MOCK_IP}/redirect",
            status=302, headers={"Location": "http://192.168.1.1/admin"},
        )
        with patch(_VALIDATE, side_effect=mock_validate_url):
            result = fetch_url("https://example.com/redirect")
        assert not result.ok
        # The redirect target (192.168.1.1) fails real validate_url SSRF check
        assert "Redirect blocked" in result.error or "private" in result.error.lower()

    @responses.activate
    def test_limits_redirect_count(self):
        for i in range(10):
            responses.add(
                responses.GET, f"https://{MOCK_IP}/r{i}",
                status=302, headers={"Location": f"https://example.com/r{i+1}"},
            )
        responses.add(
            responses.GET, f"https://{MOCK_IP}/r10",
            body="<html><body>Final</body></html>", status=200,
        )
        with patch(_VALIDATE, side_effect=mock_validate_url):
            result = fetch_url("https://example.com/r0")
        assert not result.ok
        assert "redirect" in result.error.lower()

    @responses.activate
    def test_content_hash_is_deterministic(self):
        for _ in range(2):
            responses.add(
                responses.GET, f"https://{MOCK_IP}/docs",
                body="<html><body><p>Same content every time.</p></body></html>", status=200,
            )
        with patch(_VALIDATE, side_effect=mock_validate_url):
            r1 = fetch_url("https://example.com/docs")
            r2 = fetch_url("https://example.com/docs")
        assert r1.content_hash == r2.content_hash

    @responses.activate
    def test_strips_escape_sequences_from_content(self):
        malicious_html = "<html><body><p>Normal text \x1b]52;c;PAYLOAD\x07 end</p></body></html>"
        responses.add(
            responses.GET, f"https://{MOCK_IP}/evil",
            body=malicious_html, status=200,
        )
        with patch(_VALIDATE, side_effect=mock_validate_url):
            result = fetch_url("https://example.com/evil")
        assert result.ok
        assert "\x1b" not in (result.content_text or "")
