"""Tests for URL extraction from SKILL.md and config files."""

import json
import tempfile
from pathlib import Path

import pytest

from skillwatch.parser import extract_urls_from_file, extract_urls_from_text


def test_extract_markdown_links():
    text = "See [docs](https://example.com/docs) for details."
    results = extract_urls_from_text(text)
    assert len(results) == 1
    assert results[0]["url"] == "https://example.com/docs"


def test_extract_raw_urls():
    text = "Visit https://example.com/setup to get started."
    results = extract_urls_from_text(text)
    assert len(results) == 1
    assert results[0]["url"] == "https://example.com/setup"


def test_extract_multiple_urls():
    text = """
    Check [link1](https://a.com/one) and https://b.com/two for info.
    Also see [link2](https://c.com/three).
    """
    results = extract_urls_from_text(text)
    urls = {r["url"] for r in results}
    assert urls == {"https://a.com/one", "https://b.com/two", "https://c.com/three"}


def test_deduplicates_urls():
    text = """
    See [docs](https://example.com/docs) and also https://example.com/docs for info.
    """
    results = extract_urls_from_text(text)
    assert len(results) == 1


def test_rejects_private_ips():
    text = """
    Internal: http://192.168.1.1/admin
    Cloud metadata: http://169.254.169.254/latest
    Loopback: http://127.0.0.1:8080/
    Public: https://example.com/docs
    """
    results = extract_urls_from_text(text)
    urls = {r["url"] for r in results}
    assert "https://example.com/docs" in urls
    assert not any("192.168" in u for u in urls)
    assert not any("169.254" in u for u in urls)
    assert not any("127.0.0" in u for u in urls)


def test_rejects_non_http_schemes():
    text = """
    ftp://files.example.com/data
    file:///etc/passwd
    https://example.com/docs
    """
    results = extract_urls_from_text(text)
    urls = {r["url"] for r in results}
    assert urls == {"https://example.com/docs"}


def test_strips_trailing_punctuation():
    text = "See https://example.com/docs."
    results = extract_urls_from_text(text)
    assert results[0]["url"] == "https://example.com/docs"


def test_extract_from_skill_md_file():
    content = """# My Skill

Setup at [docs](https://docs.example.com/setup).
API: https://api.example.com/v1
"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(content)
        f.flush()
        results = extract_urls_from_file(f.name)

    urls = {r["url"] for r in results}
    assert "https://docs.example.com/setup" in urls
    assert "https://api.example.com/v1" in urls
    assert all(r["source_type"] == "skill_md" for r in results)
    Path(f.name).unlink()


def test_extract_from_json_config():
    config = {
        "mcpServers": {
            "myTool": {
                "url": "https://mcp.example.com/v1",
                "docs": "https://docs.example.com/mcp-tool"
            }
        }
    }
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(config, f)
        f.flush()
        results = extract_urls_from_file(f.name)

    urls = {r["url"] for r in results}
    assert "https://mcp.example.com/v1" in urls
    assert "https://docs.example.com/mcp-tool" in urls
    assert all(r["source_type"] == "mcp_config" for r in results)
    Path(f.name).unlink()


def test_extract_from_url_list():
    content = """# URLs to monitor
https://example.com/docs
https://api.example.com/setup
# Comment line
not-a-url
"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write(content)
        f.flush()
        results = extract_urls_from_file(f.name)

    urls = {r["url"] for r in results}
    assert urls == {"https://example.com/docs", "https://api.example.com/setup"}
    Path(f.name).unlink()


def test_file_not_found():
    with pytest.raises(FileNotFoundError):
        extract_urls_from_file("/nonexistent/file.md")


def test_empty_file():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write("")
        f.flush()
        results = extract_urls_from_file(f.name)

    assert results == []
    Path(f.name).unlink()
