# Design-partner participant runbook

This runbook executes the pilot defined in
[`../DESIGN-PARTNER-PILOT.md`](../DESIGN-PARTNER-PILOT.md). That protocol is the
only source for participant counts, timing, burden limits and routing decisions.

## Before starting

Use Python 3.10–3.13 and a clean virtual environment. The maintainer must name
the exact wheel and SHA-256 in the checklist. You need a public HTTPS page that
your workflow genuinely references and that you are permitted to fetch.
SkillWatch will reject private, local and reserved addresses. It is local-only;
apart from fetching URLs you add, it sends no data anywhere.

```bash
python3 -m venv .skillwatch-pilot-venv
. .skillwatch-pilot-venv/bin/activate
python -m pip install /path/to/the-supplied-skillwatch.whl
skillwatch --version
```

## Establish and repeat a baseline

Choose a disposable local database path and a real skill/configuration file:

```bash
export SKILLWATCH_DB="$PWD/skillwatch-pilot.db"
skillwatch --db "$SKILLWATCH_DB" add path/to/SKILL.md
skillwatch --db "$SKILLWATCH_DB" list
skillwatch --db "$SKILLWATCH_DB" scan
skillwatch --db "$SKILLWATCH_DB" status
skillwatch --db "$SKILLWATCH_DB" scan
skillwatch --db "$SKILLWATCH_DB" alerts
skillwatch --db "$SKILLWATCH_DB" verify
skillwatch --db "$SKILLWATCH_DB" ledger --export skillwatch-ledger.json
```

The first successful scan stores a baseline; it is not evidence that the page
is safe. An unchanged second scan means only that the fetched representation did
not change between those observations. `verify` checks the local evidence chain,
not publisher identity or the truth of the fetched content. Review an alert with
`skillwatch --db "$SKILLWATCH_DB" alert ID` when one exists.

## Failure and recovery

- If `add` reports no monitorable URLs, correct or remove blocked references and
  retry. Do not scan until `list` shows at least one URL.
- If a fetch fails, retain the output, check ordinary network/DNS access, and do
  not bypass private-address protection.
- If the input path is wrong or malformed, correct the file and rerun `add`.
- Ask the maintainer to record every intervention; an assisted run is not an
  unprompted-use result.

## Exit and removal

Export only evidence you agreed to share. Then remove monitored URLs with
`skillwatch --db "$SKILLWATCH_DB" remove URL`. After confirming the retention
choice with the maintainer, delete the disposable database, export and virtual
environment. SkillWatch performs no automatic upload or telemetry collection.
