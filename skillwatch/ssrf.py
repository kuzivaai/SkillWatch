"""SSRF protection — validate URLs and pin DNS resolution."""

from __future__ import annotations

import ipaddress
import re
import socket
from dataclasses import dataclass
from typing import Any
from urllib.parse import urlparse, urlunparse

import requests
from requests.adapters import HTTPAdapter


# Explicit supplemental blocklist. The primary gate is the stdlib classification
# in _check_ip (is_private/is_reserved/...), which is comprehensive and tracks
# the IANA special-purpose registries across Python versions. This list is
# belt-and-braces for cases a given Python version's flags may miss (e.g. CGNAT
# on older 3.10), ranges that embed private IPv4 (6to4/NAT64), and reserved /
# benchmark / documentation ranges. Blocking here can only refuse a non-public
# address; it can never block a globally-routable one.
_BLOCKED_NETWORKS = [
    # IPv4
    ipaddress.ip_network("0.0.0.0/8"),
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("100.64.0.0/10"),   # CGNAT (not is_private on all versions)
    ipaddress.ip_network("127.0.0.0/8"),
    ipaddress.ip_network("169.254.0.0/16"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.0.0.0/24"),    # IETF protocol assignments
    ipaddress.ip_network("192.0.2.0/24"),    # TEST-NET-1 (documentation)
    ipaddress.ip_network("192.168.0.0/16"),
    ipaddress.ip_network("198.18.0.0/15"),   # benchmarking (RFC 2544)
    ipaddress.ip_network("198.51.100.0/24"), # TEST-NET-2 (documentation)
    ipaddress.ip_network("203.0.113.0/24"),  # TEST-NET-3 (documentation)
    ipaddress.ip_network("224.0.0.0/4"),     # multicast
    ipaddress.ip_network("240.0.0.0/4"),     # reserved (Class E), incl. 255.255.255.255
    # IPv6
    ipaddress.ip_network("::/128"),        # unspecified
    ipaddress.ip_network("::1/128"),       # loopback
    ipaddress.ip_network("64:ff9b::/96"),  # NAT64
    ipaddress.ip_network("100::/64"),      # discard-only
    ipaddress.ip_network("2001:db8::/32"), # documentation
    ipaddress.ip_network("2002::/16"),     # 6to4 (can wrap private IPv4)
    ipaddress.ip_network("fc00::/7"),      # unique local
    ipaddress.ip_network("fe80::/10"),     # link-local unicast
    ipaddress.ip_network("ff00::/8"),      # multicast
]

_ALLOWED_SCHEMES = {"http", "https"}

# Reject hostnames that look like non-standard numeric IP notation
# (decimal, octal, hex) which getaddrinfo may resolve on some systems
_NUMERIC_HOST_RE = re.compile(r"^(\d+|0[xX][0-9a-fA-F]+)$")


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

    # Reject credentials in URLs (prevents userinfo-based SSRF confusion)
    if parsed.username or parsed.password:
        raise SSRFError(f"Credentials in URL not permitted: {url}")

    hostname = parsed.hostname
    port = parsed.port or (443 if parsed.scheme == "https" else 80)

    # Reject non-standard numeric IP notation (decimal, hex, octal)
    # that getaddrinfo may resolve to private IPs on some systems
    if _NUMERIC_HOST_RE.match(hostname):
        raise SSRFError(f"Non-standard numeric hostname not permitted: {hostname}")

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
    except (socket.gaierror, UnicodeError) as exc:
        raise SSRFError(f"Cannot resolve hostname: {hostname}") from exc

    if not infos:
        raise SSRFError(f"No DNS records for hostname: {hostname}")

    # Check ALL resolved IPs, use the first one for the connection
    resolved_ip: str | None = None
    for info in infos:
        ip = ipaddress.ip_address(info[4][0])
        _check_ip(ip, url)
        if resolved_ip is None:
            resolved_ip = str(ip)

    assert resolved_ip is not None  # infos is non-empty (checked above)
    return ValidatedURL(url=url, hostname=hostname, resolved_ip=resolved_ip, port=port)


def _check_ip(ip: ipaddress.IPv4Address | ipaddress.IPv6Address, url: str) -> None:
    # Unwrap IPv4-mapped IPv6 addresses (e.g. ::ffff:127.0.0.1)
    if isinstance(ip, ipaddress.IPv6Address) and ip.ipv4_mapped:
        _check_ip(ip.ipv4_mapped, url)
        return

    # Primary gate: refuse anything the stdlib does not consider globally
    # routable. This tracks the IANA special-purpose registries and covers
    # ranges the explicit list below might omit on newer allocations.
    if (
        ip.is_private
        or ip.is_loopback
        or ip.is_link_local
        or ip.is_multicast
        or ip.is_reserved
        or ip.is_unspecified
    ):
        raise SSRFError(f"Blocked private/reserved IP {ip} for URL: {url}")

    # Belt-and-braces: explicit supplemental ranges (see _BLOCKED_NETWORKS).
    for network in _BLOCKED_NETWORKS:
        if ip in network:
            raise SSRFError(f"Blocked private/reserved IP {ip} for URL: {url}")


class PinnedDNSAdapter(HTTPAdapter):
    """A requests HTTPAdapter that forces connections to a pre-resolved IP.

    This prevents DNS rebinding: the hostname is resolved once during
    validation, and the resolved IP is reused for the actual connection.

    The URL is rewritten to use the pinned IP for the TCP connection,
    while the original hostname is preserved via the Host header and
    urllib3's assert_hostname/server_hostname for TLS SNI and certificate
    verification. This approach is thread-safe — no global state is modified.
    """

    def __init__(self, pinned_ip: str, hostname: str, **kwargs: Any) -> None:
        self._pinned_ip = pinned_ip
        self._hostname = hostname
        super().__init__(**kwargs)

    def init_poolmanager(
        self, connections: int, maxsize: int, block: bool = False, **kwargs: Any
    ) -> None:
        kwargs["assert_hostname"] = self._hostname
        kwargs["server_hostname"] = self._hostname
        super().init_poolmanager(connections, maxsize, block=block, **kwargs)

    def send(
        self, request: requests.PreparedRequest, *args: Any, **kwargs: Any
    ) -> requests.Response:
        url = request.url or ""
        parsed = urlparse(url)

        # Always set Host header to the original hostname
        hostname = parsed.hostname or ""
        port_suffix = f":{parsed.port}" if parsed.port and parsed.port not in (80, 443) else ""
        request.headers["Host"] = f"{hostname}{port_suffix}"

        # Rewrite URL to use the pinned IP for the actual TCP connection
        ip = self._pinned_ip
        netloc = f"[{ip}]" if ":" in ip else ip
        if parsed.port:
            netloc = f"{netloc}:{parsed.port}"

        request.url = urlunparse((
            parsed.scheme, netloc, parsed.path or "",
            parsed.params or "", parsed.query or "", parsed.fragment or "",
        ))

        return super().send(request, *args, **kwargs)
