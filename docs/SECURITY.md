# Security — SkillWatch Threat Model

A security tool must be secure. SkillWatch fetches arbitrary user-supplied URLs, which creates attack surface.

---

## Threats and Mitigations

### 1. SSRF (Server-Side Request Forgery)

**Attack:** User adds a URL like `http://169.254.169.254/latest/meta-data/` or `http://localhost:8080/admin`. SkillWatch fetches it, potentially leaking internal network data.

**Mitigation:**
- Before fetching, resolve the hostname to an IP address
- Reject private IPs: `10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`
- Reject loopback: `127.0.0.0/8`, `::1`
- Reject link-local: `169.254.0.0/16`, `fe80::/10`
- Reject IPv4-mapped IPv6: `::ffff:127.0.0.1` and similar (unwrapped and re-checked)
- Only allow `http://` and `https://` schemes (reject `file://`, `ftp://`, `gopher://`)
- Redirects followed manually (max 5 hops), each destination validated BEFORE the request is made

**Residual risk:** DNS rebinding. `validate_url` resolves the hostname to check the IP, but `requests.get` performs a second DNS resolution. Between the two lookups, an attacker controlling a domain could return a public IP first and a private IP second. Full mitigation requires a custom transport adapter that reuses the pre-resolved IP. Not implemented in v0.1.

### 2. Denial of Storage

**Attack:** User monitors a URL that returns enormous responses, filling disk.

**Mitigation:**
- Max response size: 5 MB. Fetch aborted mid-stream if exceeded.
- Text extraction via trafilatura typically reduces content to 2-10 KB.

**Not implemented:** URL count limits and per-snapshot content size caps. The tool runs locally and the user controls what they monitor, so unbounded growth is a user concern, not an attacker concern. Future versions may add configurable limits.

### 3. Content Injection in Terminal Output

**Attack:** Monitored URL contains terminal escape sequences (ANSI, OSC, DCS) that could manipulate the terminal when diffs are displayed. The most material risk is OSC 52 (clipboard write).

**Mitigation:**
- Escape sequences stripped at two points: once during content extraction (fetcher.py), once at display time (formatter.py)
- Regex covers CSI, OSC, DCS, Fe, and C1 control code families
- Raw HTML is never printed to terminal

**Residual risk:** Novel escape sequences not covered by the regex.

### 4. Malicious SKILL.md / Config Parsing

**Attack:** Crafted SKILL.md exploits YAML parsing (billion laughs, arbitrary code execution).

**Mitigation:**
- `yaml.safe_load()` used exclusively (never `yaml.load()`)
- Only URLs extracted via regex — no code is evaluated from parsed files

### 5. Privacy — Fetched Content May Contain Secrets

**Attack:** A monitored URL is a private docs page containing API keys or tokens. SkillWatch stores this content in the local SQLite database.

**Mitigation:**
- Database stored locally (not sent anywhere)
- No telemetry, no analytics, no phone-home
- User controls what URLs they monitor

### 6. Timing Attacks / Fingerprinting

**Attack:** A malicious skill author detects SkillWatch's User-Agent and serves different content to it vs to the AI agent.

**Mitigation:** Default User-Agent identifies SkillWatch (transparent, not deceptive). No built-in stealth mode.

**Residual risk:** Sophisticated attackers can always detect automated fetching.
