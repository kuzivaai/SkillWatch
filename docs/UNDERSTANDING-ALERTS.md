# Understanding your alerts

When SkillWatch flags a change, it shows a plain-language line for each thing it
noticed, the raw code in brackets (useful for searching or scripting), and one
piece of advice: **what to do**. This guide explains each flag in ordinary words
and how to decide whether a change is a real problem.

> **The honest limit.** SkillWatch cannot tell you for certain that a change is an
> attack. In testing, roughly **1 in 5 alerts is a false alarm**. It points you at
> what changed and why it might matter; the judgement is still yours. If you are not
> sure, treat the change as suspicious until you have checked it.

## How to read an alert

```
skillwatch alerts        # the list: what changed, in plain language
skillwatch alert 1       # one alert in full, including the diff
```

Each alert has a **severity**:

- **CRITICAL:** the change could let someone run code or hijack an AI assistant.
  Stop using the skill or tool that points at this page until you have checked it.
- **WARNING:** the change is worth a look. It may be innocent (for example, a page
  that legitimately added install instructions), or it may be a disguise.
- **INFO:** a minor change, shown for completeness.

## What each flag means, and what to do

### Critical

| Flag | What it means | What to do |
|---|---|---|
| `new_exec_command` | The page added a command that could download or run software (for example `curl … \| bash`). | Do not run anything from the page. Check who changed it and why. |
| `prompt_injection` | The page added wording that could tell an AI assistant to ignore its instructions. | Stop pointing an AI agent at this page until you have read the change. |
| `suspicious_script` | The page added a script that can read cookies, send data, or run code. | Treat the page as untrusted; inspect the script in the diff. |
| `data_uri_embed` | The page embedded hidden content (a `data:` frame) that can run in a browser. | Treat as untrusted; the payload is in the diff. |

### Warning

| Flag | What it means | What to do |
|---|---|---|
| `new_base64` | The page added a long encoded string that could hide instructions or code. | Decode it if you can; a legitimate page rarely needs one. |
| `credential_reference` | The page now mentions passwords, API keys, or tokens. | Check the context: is it asking for secrets it should not need? |
| `new_domains` | The page now links to web addresses it did not reference before. | Check whether the new destinations are expected. |
| `unicode_homoglyph` | The page uses look-alike letters, for example Cyrillic that mimics English (a common disguise trick). | Look closely at the flagged text; letters may not be what they seem. |
| `data_uri_payload` | The page contains a `data:` URL with runnable content. | Inspect it in the diff before trusting the page. |
| `meta_refresh_redirect` | The page added an automatic redirect to another address. | Check where it now sends people. |
| `major_deletion` | More than half the page's content was removed. | A large deletion can hide a swap; compare old and new. |
| `iframe_detected` | The page added an embedded frame from another source. | Check what the frame loads. |

### Info

| Flag | What it means | What to do |
|---|---|---|
| `hidden_content` | The page added text hidden with an inline `style="display:none"` or `style="visibility:hidden"`. | Read the hidden text in the diff; hiding it is itself a signal. **Absence of this flag does not mean nothing is hidden** — the check only reads inline lower-case styles, so text hidden via a stylesheet, an upper-case declaration, off-screen positioning, `opacity:0` or the HTML `hidden` attribute will not raise it. |

## If you are still unsure

- Compare the old and new content in the diff (`skillwatch alert <id>`).
- If you did not expect the change and cannot explain it, treat the source as
  compromised: stop using the skill or tool that points at it, and tell whoever
  maintains that skill.
- A change with no flags at all is shown as "content changed, no suspicious
  patterns". That is not a guarantee of safety, only that none of the 13 checks
  matched.
