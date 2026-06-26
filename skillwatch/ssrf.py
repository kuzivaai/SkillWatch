"""SSRF protection — validate URLs and pin DNS resolution."""

import ipaddress
import socket
from dataclasses import dataclass
from urllib.parse import urlparse

from requests.adapters import HTTPAdapter


_BLOCKED_NETWORKS = [
    ipaddress.ip_network("0.0.0.0/8"),
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("100.64.0.0/10"),
    ipaddress.ip_network("127.0.0.0/8"),
    ipaddress.ip_network("169.254.0.0/16"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.168.0.0/16"),
    ipaddress.ip_network("224.0.0.0/4"),
    ipaddress.ip_network("::1/128"),
    ipaddress.ip_network("fe80::/10"),
    ipaddress.ip_network("fc00::/7"),
]

_ALLOWED_SCHEMES = {"http", "https"}


class SSRFError(Exception):
    """Raised when a URL fails SSRF validation."""


@dataclass
class ValidatedURL:
    """A URL that has passed SSRF validation, with its resolved IP pinned."""
    url: str
    hostname: str
    resolved_ip: str
    port: int


def validate_url(url: str) -> ValidatedURL:
    """Validate a URL is safe to fetch. Returns a ValidatedURL with the pinned IP.

    Resolves DNS exactly once. The caller MUST use the resolved_ip for the
    actual connection to prevent DNS rebinding (TOCTOU).
    """
    parsed = urlparse(url)

    if parsed.scheme not in _ALLOWED_SCHEMES:
        raise SSRFError(f"Blocked scheme: {parsed.scheme}:// (only http/https allowed)")

    if not parsed.hostname:
        raise SSRFError(f"No hostname in URL: {url}")

    hostname = parsed.hostname
    port = parsed.port or (443 if parsed.scheme == "https" else 80)

    # Try to parse as IP literal first
    try:
        ip = ipaddress.ip_address(hostname)
        _check_ip(ip, url)
        return ValidatedURL(url=url, hostname=hostname, resolved_ip=str(ip), port=port)
    except ValueError:
        pass

    # Resolve hostname to IP — this is the ONLY DNS resolution that should happen
    try:
        infos = socket.getaddrinfo(hostname, port, socket.AF_UNSPEC, socket.SOCK_STREAM)
    except socket.gaierror as exc:
        raise SSRFError(f"Cannot resolve hostname: {hostname}") from exc

    if not infos:
        raise SSRFError(f"No DNS records for hostname: {hostname}")

    # Check ALL resolved IPs, use the first one for the connection
    resolved_ip = None
    for info in infos:
        ip = ipaddress.ip_address(info[4][0])
        _check_ip(ip, url)
        if resolved_ip is None:
            resolved_ip = str(ip)

    return ValidatedURL(url=url, hostname=hostname, resolved_ip=resolved_ip, port=port)


def _check_ip(ip: ipaddress.IPv4Address | ipaddress.IPv6Address, url: str) -> None:
    # Unwrap IPv4-mapped IPv6 addresses (e.g. ::ffff:127.0.0.1)
    if isinstance(ip, ipaddress.IPv6Address) and ip.ipv4_mapped:
        _check_ip(ip.ipv4_mapped, url)
        return

    for network in _BLOCKED_NETWORKS:
        if ip in network:
            raise SSRFError(f"Blocked private/reserved IP {ip} for URL: {url}")


class PinnedDNSAdapter(HTTPAdapter):
    """A requests HTTPAdapter that forces connections to a pre-resolved IP.

    This prevents DNS rebinding: the hostname is resolved once during
    validation, and the resolved IP is reused for the actual connection.

    The URL is NOT rewritten — the original hostname stays in place so
    TLS certificate verification and SNI work correctly. Instead, we
    temporarily override socket.getaddrinfo to return the pinned IP
    when the target hostname is resolved.

    This is single-threaded safe. SkillWatch does not use threads.
    """

    def __init__(self, pinned_ip: str, hostname: str, **kwargs):
        self._pinned_ip = pinned_ip
        self._hostname = hostname
        super().__init__(**kwargs)

    def send(self, request, *args, **kwargs):
        original_getaddrinfo = socket.getaddrinfo

        pinned_ip = self._pinned_ip
        target_hostname = self._hostname

        def _pinned_getaddrinfo(host, port, *a, **kw):
            if host == target_hostname:
                # Return the pre-validated IP instead of re-resolving
                return original_getaddrinfo(pinned_ip, port, *a, **kw)
            return original_getaddrinfo(host, port, *a, **kw)

        socket.getaddrinfo = _pinned_getaddrinfo
        try:
            return super().send(request, *args, **kwargs)
        finally:
            socket.getaddrinfo = original_getaddrinfo
