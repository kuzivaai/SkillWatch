"""SSRF protection — validate URLs before fetching."""

import ipaddress
import socket
from urllib.parse import urlparse


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


def validate_url(url: str) -> str:
    """Validate a URL is safe to fetch. Returns the URL if safe, raises SSRFError if not."""
    parsed = urlparse(url)

    if parsed.scheme not in _ALLOWED_SCHEMES:
        raise SSRFError(f"Blocked scheme: {parsed.scheme}:// (only http/https allowed)")

    if not parsed.hostname:
        raise SSRFError(f"No hostname in URL: {url}")

    hostname = parsed.hostname

    # Try to parse as IP directly
    try:
        ip = ipaddress.ip_address(hostname)
        _check_ip(ip, url)
        return url
    except ValueError:
        pass

    # Resolve hostname to IP
    try:
        infos = socket.getaddrinfo(hostname, None, socket.AF_UNSPEC, socket.SOCK_STREAM)
    except socket.gaierror as exc:
        raise SSRFError(f"Cannot resolve hostname: {hostname}") from exc

    for info in infos:
        ip = ipaddress.ip_address(info[4][0])
        _check_ip(ip, url)

    return url


def _check_ip(ip: ipaddress.IPv4Address | ipaddress.IPv6Address, url: str) -> None:
    for network in _BLOCKED_NETWORKS:
        if ip in network:
            raise SSRFError(f"Blocked private/reserved IP {ip} for URL: {url}")
