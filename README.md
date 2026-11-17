# Demo Prep Agent (prototype)

Turns everything we know about an upcoming sales demo into a one-page brief a rep can read in under a minute before the call: who is attending and their career history, what the company does, recent news, and every past touchpoint with them.

**Status: working prototype.** This repo is the brief generator, built and tested against sample data. The planned automation around it (a daily calendar scan and posting to Slack and the CRM) was designed but not built here.

## Why I built it

Reps were walking into demos having spent 20 minutes clicking through the CRM, LinkedIn and Google, or having skipped it. I wanted the same high-quality prep for every demo, delivered automatically the evening before.

## What the brief covers

See [the sample brief](briefs/2026-06-10-crestview-post-acute-care.md). The company and people in it are fictional.

- **Attendees:** name, title, LinkedIn, current role and tenure, last three companies, promotions
- **Company:** what they do, size, specialties, location
- **Recent strategic news:** capped at five items so it stays skimmable
- **Our history with them:** last touch, open deal and stage, how many email threads and with whom
- A banner when the company is brand new to us

## Engineering decisions

- **Review the output before automating it.** The build was staged so a human had to approve a real brief before any scheduler or integration was built. It's cheaper to fix the page than to fix a pipeline that confidently posts the wrong page every day.
- **Missing data never breaks the page.** Every field except the company name is optional; anything unknown renders as "unknown" instead of crashing.
- **Works out who the customer is.** Company domain resolution ignores our own email domain, prefers the domain on the CRM deal, and otherwise takes the most common outside domain among attendees.
- **Fragile sources are best-effort.** LinkedIn scraping can break silently, so the design says to post the brief anyway with that section marked unavailable and raise an alert.
- **One data contract.** [`fixtures/example_demo.json`](fixtures/example_demo.json) defines the input shape, so live sources (CRM first, enrichment tools only on a miss) can be added behind it without touching the renderer.

## Run it

```bash
python3 generate_brief.py --fixture fixtures/example_demo.json
```

Prints the brief and saves a Markdown copy to `briefs/`. Standard library only, so there is nothing to install.

## Files

- `generate_brief.py`: command-line entry point
- `assemble.py`: loads and validates the input and resolves the company domain
- `render.py`: renders the one-page Markdown brief
- `config.json`: settings (internal domain, which calendar events count as demos)
- `fixtures/example_demo.json`: sample input (fictional)

---

Built at Alleviate Health.
