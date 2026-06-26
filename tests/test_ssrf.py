"""Tests for SSRF protection."""

import pytest

from skillwatch.ssrf import SSRFError, ValidatedURL, validate_url


class TestSSRFValidation:
    def test_allows_public_https(self):
        result = validate_url("https://docs.python.org/3/")
        assert isinstance(result, ValidatedURL)
        assert result.url == "https://docs.python.org/3/"
        assert result.resolved_ip  # non-empty

    def test_allows_public_http(self):
        result = validate_url("http://example.com")
        assert isinstance(result, ValidatedURL)
        assert result.url == "http://example.com"
        assert result.port == 80

    def test_blocks_private_10(self):
        with pytest.raises(SSRFError, match="private"):
            validate_url("http://10.0.0.1/admin")

    def test_blocks_private_172(self):
        with pytest.raises(SSRFError, match="private"):
            validate_url("http://172.16.0.1/admin")

    def test_blocks_private_192(self):
        with pytest.raises(SSRFError, match="private"):
            validate_url("http://192.168.1.1/admin")

    def test_blocks_loopback(self):
        with pytest.raises(SSRFError, match="private"):
            validate_url("http://127.0.0.1:8080/")

    def test_blocks_link_local(self):
        with pytest.raises(SSRFError, match="private"):
            validate_url("http://169.254.169.254/latest/meta-data/")

    def test_blocks_localhost(self):
        with pytest.raises(SSRFError, match="private"):
            validate_url("http://localhost/admin")

    def test_blocks_file_scheme(self):
        with pytest.raises(SSRFError, match="scheme"):
            validate_url("file:///etc/passwd")

    def test_blocks_ftp_scheme(self):
        with pytest.raises(SSRFError, match="scheme"):
            validate_url("ftp://files.example.com/data")

    def test_blocks_no_hostname(self):
        with pytest.raises(SSRFError):
            validate_url("https://")

    def test_blocks_zero_ip(self):
        with pytest.raises(SSRFError, match="private"):
            validate_url("http://0.0.0.0/")

    def test_blocks_ipv4_mapped_ipv6_loopback(self):
        with pytest.raises(SSRFError, match="private"):
            validate_url("http://[::ffff:127.0.0.1]/")
