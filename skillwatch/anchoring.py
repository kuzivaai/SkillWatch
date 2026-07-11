"""External anchoring of the ledger head.

The chain head (the last entry's ``chain_hash``) commits to the whole ledger
history. Anchoring obtains external, tamper-proof evidence that a given head
existed at a given time, so a later rewrite of history up to that head is
detectable even against a full-chain recompute that plain ``verify`` would
accept. Backends are pluggable.

The default ``rfc3161`` backend obtains a signed timestamp token from an
RFC 3161 Time-Stamp Authority (freeTSA.org by default), whose signature cannot
be forged. Only a hash leaves the machine — never page content or anything
identifying the user.

The cryptography for ``rfc3161`` lives in the optional ``[anchor]`` extra
(``rfc3161-client`` + ``cryptography``), so the core tool stays dependency-light
and fully offline. Every function degrades with a clear, actionable error if the
extra is not installed.
"""

from __future__ import annotations

import hashlib
import subprocess
from dataclasses import dataclass
from pathlib import Path

from .ssrf import SSRFError, validate_url

DEFAULT_TSA_URL = "https://freetsa.org/tsr"
DEFAULT_METHOD = "rfc3161"
GIT_ANCHOR_LOG = ".skillwatch-anchors.log"

INSTALL_HINT = (
    "RFC 3161 anchoring needs the optional extra. Install it with:\n"
    "    pip install 'skillwatch[anchor]'"
)


class AnchorError(Exception):
    """Raised when anchoring or anchor verification cannot be performed."""


@dataclass(frozen=True)
class AnchorResult:
    """The outcome of anchoring a head with a backend."""

    method: str
    external_ref: str  # e.g. the TSA URL the token came from
    proof: bytes  # the DER timestamp token (empty for non-cryptographic methods)
    timestamp: str  # ISO time the anchor asserts (from the token), or ""


def anchoring_available() -> bool:
    """True if the optional anchoring dependencies are importable."""
    try:
        import cryptography  # noqa: F401
        import rfc3161_client  # noqa: F401
    except ImportError:
        return False
    return True


def anchor_head(
    head: str,
    method: str = DEFAULT_METHOD,
    tsa_url: str = DEFAULT_TSA_URL,
    repo_path: str = ".",
) -> AnchorResult:
    """Obtain external anchor evidence for ``head``.

    - ``rfc3161``: a signed timestamp token from a Time-Stamp Authority
      (needs the ``[anchor]`` extra; depends on that authority being reachable).
    - ``git``: commit the head to a git repo you control, so pushing it to a
      remote (e.g. GitHub) gives an independent, timestamped record that does not
      depend on any timestamp authority. No extra dependencies.
    """
    if method == "rfc3161":
        return _rfc3161_anchor(head, tsa_url)
    if method == "git":
        return _git_anchor(head, repo_path)
    raise AnchorError(f"Unknown anchoring method: {method}")


def verify_anchor(
    head: str, method: str, proof: bytes, cacert_pem: bytes | None = None
) -> bool:
    """Verify that ``proof`` is a valid external anchor for ``head``.

    Returns True only if the proof cryptographically binds ``head`` to a trusted
    authority. Returns False on any verification failure. Raises AnchorError only
    when verification cannot be attempted (unknown method / missing extra).
    """
    if method == "rfc3161":
        return _rfc3161_verify(head, proof, cacert_pem)
    raise AnchorError(f"Unknown anchoring method: {method}")


# --- RFC 3161 backend (optional [anchor] extra) --------------------------


def _rfc3161_anchor(head: str, tsa_url: str) -> AnchorResult:
    try:
        import requests
        from rfc3161_client import (
            HashAlgorithm,
            TimestampRequestBuilder,
            decode_timestamp_response,
        )
    except ImportError as exc:
        raise AnchorError(INSTALL_HINT) from exc

    # Apply the same SSRF protection the rest of the tool uses: refuse to POST to
    # a private/reserved/metadata address even though the TSA URL is user-chosen.
    try:
        validate_url(tsa_url)
    except SSRFError as exc:
        raise AnchorError(
            f"Refusing to anchor to a non-public timestamp authority: {exc}"
        ) from exc

    message = head.encode("utf-8")
    request = (
        TimestampRequestBuilder()
        .data(message)
        .hash_algorithm(HashAlgorithm.SHA256)
        .nonce(nonce=False)
        .cert_request(cert_request=True)
        .build()
    )
    try:
        resp = requests.post(
            tsa_url,
            data=request.as_bytes(),
            headers={"Content-Type": "application/timestamp-query"},
            timeout=30,
        )
        resp.raise_for_status()
    except requests.RequestException as exc:
        raise AnchorError(f"Could not reach the timestamp authority {tsa_url}: {exc}") from exc

    token = resp.content
    tsr = decode_timestamp_response(token)
    if tsr.status != 0:
        raise AnchorError(
            f"The timestamp authority refused the request (status {tsr.status})"
        )
    timestamp = str(tsr.tst_info.gen_time)
    return AnchorResult(method="rfc3161", external_ref=tsa_url, proof=token, timestamp=timestamp)


def _rfc3161_verify(head: str, proof: bytes, cacert_pem: bytes | None) -> bool:
    try:
        from cryptography import x509
        from rfc3161_client import VerifierBuilder, decode_timestamp_response
    except ImportError as exc:
        raise AnchorError(INSTALL_HINT) from exc

    if not proof:
        return False
    if cacert_pem is None:
        cacert_pem = _bundled_freetsa_cacert()

    try:
        root = x509.load_pem_x509_certificate(cacert_pem)
        tsr = decode_timestamp_response(proof)
        hashed_message = hashlib.sha256(head.encode("utf-8")).digest()
        verifier = VerifierBuilder().add_root_certificate(root).build()
        return bool(verifier.verify(tsr, hashed_message))
    except Exception:
        # Any parse / signature / trust failure means the proof does not verify.
        return False


# --- git backend (no extra dependencies) ---------------------------------


def _git_anchor(head: str, repo_path: str) -> AnchorResult:
    repo = Path(repo_path)
    if not (repo / ".git").is_dir():
        raise AnchorError(
            f"{repo} is not a git repository. Point --repo at a git repo you can "
            "push (e.g. this project) so the anchor commit is preserved remotely."
        )

    log = repo / GIT_ANCHOR_LOG
    try:
        with open(log, "a", encoding="utf-8") as f:
            f.write(head + "\n")
    except OSError as exc:
        raise AnchorError(f"Could not write {log}: {exc}") from exc

    def _git(*args: str) -> str:
        try:
            proc = subprocess.run(
                ["git", "-C", str(repo), *args], capture_output=True, text=True
            )
        except FileNotFoundError as exc:
            raise AnchorError("git is not installed or not on PATH") from exc
        if proc.returncode != 0:
            raise AnchorError(f"git {args[0]} failed: {proc.stderr.strip()}")
        return proc.stdout.strip()

    _git("add", GIT_ANCHOR_LOG)
    _git("commit", "-m", f"skillwatch anchor {head}")
    sha = _git("rev-parse", "HEAD")
    when = _git("log", "-1", "--format=%cI")
    return AnchorResult(method="git", external_ref=sha, proof=b"", timestamp=when)


def _bundled_freetsa_cacert() -> bytes:
    """The freeTSA.org CA certificate shipped with the package, for offline
    verification of tokens from the default TSA."""
    from importlib import resources

    return (resources.files("skillwatch") / "data" / "freetsa_cacert.pem").read_bytes()
