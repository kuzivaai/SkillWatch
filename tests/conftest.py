"""Shared test fixtures for mocking DNS resolution in fetch tests."""

from urllib.parse import urlparse

from skillwatch.ssrf import ValidatedURL

# A predictable non-private IP for test mocks.
# When validate_url is mocked, it returns this IP, so responses
# library mocks can be registered against https://{MOCK_IP}/...
MOCK_IP = "93.184.216.34"


def mock_validate_url(url):
    """A test-only replacement for validate_url that skips real DNS.

    Returns a ValidatedURL with MOCK_IP so the PinnedDNSAdapter
    rewrites the URL to use this IP. The responses library mocks
    must be registered against https://{MOCK_IP}/... to match.

    Still performs SSRF checks on IP literals and private hostnames
    so redirect-to-private-IP tests work correctly.
    """
    import ipaddress

    from skillwatch.ssrf import SSRFError, _check_ip

    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        raise SSRFError(f"Blocked scheme: {parsed.scheme}:// (only http/https allowed)")
    if not parsed.hostname:
        raise SSRFError(f"No hostname in URL: {url}")

    hostname = parsed.hostname

    # Check IP literals (catches redirect-to-private-IP tests)
    try:
        ip = ipaddress.ip_address(hostname)
        _check_ip(ip, url)
    except ValueError:
        pass  # Not an IP literal — skip DNS, use MOCK_IP

    return ValidatedURL(
        url=url,
        hostname=hostname,
        resolved_ip=MOCK_IP,
        port=parsed.port or (443 if parsed.scheme == "https" else 80),
    )
