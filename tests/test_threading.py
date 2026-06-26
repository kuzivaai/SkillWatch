"""Test that PinnedDNSAdapter is thread-safe.

The adapter must not corrupt DNS resolution when used from multiple threads
simultaneously. No global state (socket.getaddrinfo) should be modified.
"""

import socket

import responses

from skillwatch.fetcher import fetch_url


class TestThreadSafety:
    @responses.activate
    def test_getaddrinfo_not_patched_after_fetch(self):
        """After a fetch completes, socket.getaddrinfo must be the original function."""
        original_getaddrinfo = socket.getaddrinfo

        responses.add(
            responses.GET, "https://example.com/docs",
            body="<html><body><p>Content here for testing.</p></body></html>", status=200,
        )

        fetch_url("https://example.com/docs")

        # getaddrinfo should be unchanged after fetch completes.
        # The old approach patched it globally; the new approach doesn't touch it.
        assert socket.getaddrinfo is original_getaddrinfo, \
            "socket.getaddrinfo was modified by fetch_url — DNS pinning is not thread-safe"

    @responses.activate
    def test_adapter_uses_url_rewriting_not_global_patch(self):
        """The adapter should rewrite the URL to use the pinned IP, not patch getaddrinfo."""
        responses.add(
            responses.GET, "https://example.com/page",
            body="<html><body><p>Page content for testing.</p></body></html>", status=200,
        )

        # Track whether getaddrinfo gets replaced during the fetch
        original = socket.getaddrinfo
        was_patched = []

        real_getaddrinfo = socket.getaddrinfo

        def monitoring_getaddrinfo(*args, **kwargs):
            if socket.getaddrinfo is not monitoring_getaddrinfo:
                was_patched.append(True)
            return real_getaddrinfo(*args, **kwargs)

        socket.getaddrinfo = monitoring_getaddrinfo
        try:
            fetch_url("https://example.com/page")
        finally:
            socket.getaddrinfo = original

        assert not was_patched, "socket.getaddrinfo was replaced during fetch — not thread-safe"
