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

    def test_blocks_credentials_in_url(self):
        with pytest.raises(SSRFError, match="Credentials"):
            validate_url("http://user:pass@example.com/")

    def test_blocks_ipv6_multicast(self):
        with pytest.raises(SSRFError, match="private"):
            validate_url("http://[ff02::1]/")

    def test_blocks_6to4(self):
        with pytest.raises(SSRFError, match="private"):
            validate_url("http://[2002:7f00:1::]/")

    def test_blocks_nat64(self):
        with pytest.raises(SSRFError, match="private"):
            validate_url("http://[64:ff9b::127.0.0.1]/")

    def test_blocks_decimal_ip(self):
        with pytest.raises(SSRFError, match="numeric"):
            validate_url("http://2130706433/")

    def test_blocks_hex_ip(self):
        with pytest.raises(SSRFError, match="numeric"):
            validate_url("http://0x7f000001/")

    def test_handles_unicode_hostname_error(self):
        with pytest.raises(SSRFError, match="Cannot resolve"):
            validate_url("http://.localhost/")


class TestSSRFReservedRanges:
    """Ranges that are not globally routable must be refused, via both the
    stdlib classification and the explicit supplemental list."""

    @pytest.mark.parametrize("url", [
        "http://240.0.0.1/",            # Class E / reserved
        "http://255.255.255.255/",      # limited broadcast (in 240/4)
        "http://192.0.0.1/",            # IETF protocol assignments
        "http://198.18.0.1/",           # benchmarking (RFC 2544)
        "http://192.0.2.5/",            # TEST-NET-1 (documentation)
        "http://203.0.113.9/",          # TEST-NET-3
        "http://[2001:db8::1]/",        # IPv6 documentation
    ])
    def test_blocks_additional_reserved(self, url):
        with pytest.raises(SSRFError):
            validate_url(url)

    def test_allows_global_ip_literal(self):
        # A globally-routable literal must still pass (no false block).
        result = validate_url("http://1.1.1.1/")
        assert result.resolved_ip == "1.1.1.1"
