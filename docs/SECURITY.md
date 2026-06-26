# Security — SkillWatch Threat Model

A security tool must be secure. SkillWatch fetches arbitrary user-supplied URLs, which creates attack surface.

---

## Threats and Mitigations

### 1. SSRF (Server-Side Request Forgery)

**Attack:** User adds a URL like `http://169.254.169.254/latest/meta-data/` or `http://localhost:8080/admin`. SkillWatch fetches it, potentially leaking internal network data.

**Mitigation:**
- Before fetching, resolve the hostname to an IP address
- Reject private IPs: `10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`
- Reject link-local: `169.254.0.0/16`, `fe80::/10`
- Reject loopback: `127.0.0.0/8`, `::1`
- Reject `0.0.0.0`
- Only allow `http://` and `https://` schemes (reject `file://`, `ftp://`, `gopher://`)
- Follow redirects (max 3) but re-validate the IP at each hop

**Residual risk:** DNS rebinding (hostname resolves to public IP first, then to private IP on second lookup). Mitigated by resolving once and using the resolved IP for the actual fetch.

### 2. Denial of Storage

**Attack:** User monitors a URL that returns enormous responses (100 MB HTML page), filling disk.

**Mitigation:**
- Max response size: 5 MB. Abort fetch if Content-Length exceeds this or if streaming exceeds 5 MB.
- Max URLs per database: configurable, default 500. Warn at 400.
- Max content_text stored per snapshot: 500 KB after extraction.

**Residual risk:** Minimal — SQLite on local disk, user controls their own machine.

### 3. Content Injection in Diff Output

**Attack:** Monitored URL contains terminal escape sequences or ANSI codes that could manipulate the terminal when the diff is displayed.

**Mitigation:**
- Strip ANSI escape sequences from fetched content before storing or displaying.
- Use Python's `shlex.quote()` if content is ever passed to shell commands (it shouldn't be).

**Residual risk:** Low — terminal escape attacks are limited in impact.

### 4. Malicious SKILL.md / Config Parsing

**Attack:** User adds a crafted SKILL.md that exploits YAML parsing (billion laughs, arbitrary code execution via `!!python/object`).

**Mitigation:**
- Use `yaml.safe_load()` (never `yaml.load()`)
- Limit parsed file size to 1 MB
- Only extract URLs via regex — don't evaluate any code in parsed files

**Residual risk:** Negligible with safe_load.

### 5. Privacy — Fetched Content May Contain Secrets

**Attack:** A monitored URL is a private docs page that contains API keys, tokens, or internal information. SkillWatch stores this content in the local SQLite database.

**Mitigation:**
- Database stored locally (not sent anywhere)
- No telemetry, no analytics, no phone-home
- User controls what URLs they monitor
- README warns: "SkillWatch stores fetched content locally. Do not monitor URLs containing secrets you wouldn't store on disk."

**Residual risk:** User responsibility. The tool runs locally.

### 6. Timing Attacks / Fingerprinting

**Attack:** A malicious skill author detects SkillWatch's User-Agent and serves different content to it vs to the AI agent.

**Mitigation:**
- Configurable User-Agent (user can set it to match their browser)
- Default User-Agent identifies SkillWatch (transparent, not deceptive)
- v2 consideration: option to use a browser-like User-Agent for stealth monitoring

**Residual risk:** Sophisticated attackers can always detect automated fetching. This is a fundamental limitation of any monitoring approach.
