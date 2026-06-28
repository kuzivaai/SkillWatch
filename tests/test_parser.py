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


def test_extract_from_yaml_config():
    content = """
mcpServers:
  myTool:
    url: https://mcp.example.com/v1
    docs: https://docs.example.com/yaml-tool
"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        f.write(content)
        f.flush()
        results = extract_urls_from_file(f.name)

    urls = {r["url"] for r in results}
    assert "https://mcp.example.com/v1" in urls
    assert "https://docs.example.com/yaml-tool" in urls
    assert all(r["source_type"] == "mcp_config" for r in results)
    Path(f.name).unlink()


def test_extract_from_yml_extension():
    content = """
servers:
  - url: https://api.example.com/yml-test
"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as f:
        f.write(content)
        f.flush()
        results = extract_urls_from_file(f.name)

    urls = {r["url"] for r in results}
    assert "https://api.example.com/yml-test" in urls
    Path(f.name).unlink()


def test_extract_yaml_with_list_values():
    content = """
tools:
  - name: tool1
    docs: https://docs.example.com/tool1
  - name: tool2
    docs: https://docs.example.com/tool2
"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        f.write(content)
        f.flush()
        results = extract_urls_from_file(f.name)

    urls = {r["url"] for r in results}
    assert "https://docs.example.com/tool1" in urls
    assert "https://docs.example.com/tool2" in urls
    Path(f.name).unlink()


def test_extract_yaml_with_invalid_yaml():
    content = "{{invalid yaml: [[[unterminated"
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        f.write(content)
        f.flush()
        results = extract_urls_from_file(f.name)

    # Should not crash — falls back to regex URL extraction
    assert results == []
    Path(f.name).unlink()


def test_extract_json_with_invalid_json():
    content = "{ invalid json }"
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        f.write(content)
        f.flush()
        results = extract_urls_from_file(f.name)

    # Should not crash — falls back to regex URL extraction
    assert results == []
    Path(f.name).unlink()


def test_extract_json_with_nested_lists():
    config = {
        "tools": [
            {"urls": ["https://a.example.com/1", "https://b.example.com/2"]},
            {"url": "https://c.example.com/3"},
        ]
    }
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(config, f)
        f.flush()
        results = extract_urls_from_file(f.name)

    urls = {r["url"] for r in results}
    assert "https://a.example.com/1" in urls
    assert "https://b.example.com/2" in urls
    assert "https://c.example.com/3" in urls
    Path(f.name).unlink()


def test_fallback_to_markdown_for_unknown_extension():
    content = "See [docs](https://example.com/unknown-ext) for info."
    with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
        f.write(content)
        f.flush()
        results = extract_urls_from_file(f.name)

    urls = {r["url"] for r in results}
    assert "https://example.com/unknown-ext" in urls
    Path(f.name).unlink()


def test_extract_url_with_balanced_parens():
    text = "[Wikipedia](https://en.wikipedia.org/wiki/URL_(disambiguation))"
    results = extract_urls_from_text(text)
    urls = [r["url"] for r in results]
    assert "https://en.wikipedia.org/wiki/URL_(disambiguation)" in urls


def test_extract_url_with_nested_parens():
    text = "[link](https://example.com/a(b)c)"
    results = extract_urls_from_text(text)
    urls = [r["url"] for r in results]
    assert "https://example.com/a(b)c" in urls


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
