# Demo Prep Agent

Generates a one-page brief for each upcoming sales demo, so the rep can read
it in under a minute before the call. Eventually: posted to Slack + written
as an Attio note, fired daily at 5PM for next-day "Demo" calendar events.

## Current status: Phase 1 (page generator, fixture-driven)

**The Phase 1 gate:** the page itself must be reviewed by a human against a
real example demo before any automation (Slack, Attio, scheduler) gets built.
Nothing in this project calls a live API yet.

### Run it

```
python3 generate_brief.py --fixture fixtures/example_demo.json
```

Prints the brief to the terminal and writes a `.md` copy into `briefs/`.
Python 3 standard library only — nothing to install.

### Swap in the real example demo

`fixtures/example_demo.json` is **fictional placeholder data**. Replace its
contents with the real example demo (same field names — every field except
`company.name` is optional; missing fields render as "unknown" rather than
breaking). Then re-run the command above and review the page.

## Build phases (from the spec — do not reorder)

1. **Page generator (this phase).** CLI → terminal + local `.md`. Gate: human
   review of the actual page.
2. **Output targets.** Slack Block Kit post + Attio note via API.
3. **Scheduler.** GitHub Actions cron, daily 5PM: scan next-day GCal events
   titled "Demo", de-dupe processed event IDs, fail loudly to Slack on
   Google OAuth errors.

## Files

The one-pager's Attendees section shows, per attendee: name, role,
LinkedIn URL, current role(s) with tenure, past 3 companies with title +
tenure, and promotion history when their profile shows it.

- `generate_brief.py` — CLI entry point
- `assemble.py` — payload loading/validation + company-domain resolution
  (internal domains excluded; deal domain wins; else most-represented
  external domain). Phase 2 adds live sources behind the same interface:
  Attio first, Apollo/Clay only on miss, live web search for news only.
- `render.py` — Markdown one-pager renderer (graceful degradation,
  net-new banner, news capped at 5 bullets)
- `config.json` — org domains, title match string, Attio slugs (TODO),
  Slack webhook (TODO)
- `fixtures/example_demo.json` — the payload schema/contract

## Open discovery items (need answers before Phase 2/3)

- [ ] Attio attribute slugs: Company.domain, employee count, facility type,
      specialties, summary, LinkedIn; how the activity timeline is exposed.
- [ ] Google Calendar access scope (service account vs per-user OAuth)
      covering all rep calendars.
- [ ] Confirm org email domain(s) to exclude — config currently assumes
      only `alleviatehealth.care`.
- [ ] Slack target channel + webhook URL.

## Locked decisions (do not re-litigate)

Python · GitHub Actions cron · no Zapier · enrichment on-miss only ·
Attio + Gmail as primary internal sources.

**LinkedIn scraping — allowed with guard (decision updated 2026-06-09 by
Yoshi, supersedes the original ban).** The linkedin-mcp-server scraper
(stickerdaniel/linkedin-mcp-server, PyPI: linkedin-scraper-mcp) feeds the
attendee career-history section (Now / Past 3 companies / Promotions).
Because it can break silently, the automated job MUST treat it as
best-effort: if the scrape fails or times out, still generate and post the
page with the section marked "LinkedIn unavailable", and alert the failure
to Slack. Apollo/Clay remain the fallback for title + LinkedIn URL.

**Data sources added during Phase 1 testing:**
- Site Agent Data Google Sheet (live pull via gspread service account,
  sheet ID 13KzQocrzrmH6ifieZ2McanyURfNIqBb4UMEASAl8d-4): org_subcategory
  from `orgs`/`orgs_research`, site city/state/count from
  `locations_good_to_go`, matched on `domain`. Always pull live — never a
  cached CSV. Note: `orgs` has a duplicate `hq_address__snippet` header, so
  index columns by position, not name.
