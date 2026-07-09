"""Data assembly for demo-prep briefs.

Phase 1: all data comes from a local fixture JSON file (the example demo
payload). No live API calls happen anywhere in this module.

Phase 2+ will add live sources behind the same `assemble()` interface:
Attio first, Apollo/Clay on miss, live web search for recent news only.
The fixture schema in fixtures/example_demo.json IS the contract those
live sources must produce.
"""

import json
from pathlib import Path


class AssemblyError(Exception):
    """Raised when a payload can't be turned into a brief at all."""


def load_fixture(path):
    """Load and lightly validate a demo payload from a JSON file."""
    p = Path(path)
    if not p.exists():
        raise AssemblyError(f"Fixture file not found: {p}")
    with open(p) as f:
        data = json.load(f)

    company = data.get("company") or {}
    if not company.get("name"):
        raise AssemblyError(
            "Payload has no company.name — cannot build a brief without it."
        )

    # Normalize the sections the renderer expects so it never KeyErrors.
    data.setdefault("event", {})
    data.setdefault("attendees", [])
    data.setdefault("news", [])
    data.setdefault("history", {})
    return data


def resolve_company_domain(attendee_emails, org_domains, deal_domain=None):
    """Pick the prospect's domain from invite attendee emails.

    Mirrors the production resolution rules:
      1. Exclude internal attendees (org_domains).
      2. If a linked Deal already names a domain, prefer the external
         domain that matches it.
      3. Otherwise the most-represented external domain wins.
      4. Ties / leftovers are returned so the page can show the ambiguity.

    Returns (chosen_domain_or_None, all_external_domains_sorted_by_count).
    """
    org = {d.lower().strip() for d in org_domains}
    counts = {}
    for email in attendee_emails:
        if "@" not in email:
            continue
        domain = email.split("@", 1)[1].lower().strip()
        if domain in org:
            continue
        counts[domain] = counts.get(domain, 0) + 1

    if not counts:
        return None, []

    ranked = sorted(counts, key=lambda d: (-counts[d], d))
    if deal_domain and deal_domain.lower() in counts:
        return deal_domain.lower(), ranked
    return ranked[0], ranked


def assemble(args, config):
    """Produce the brief payload for the requested demo.

    Phase 1 only supports --fixture. The --event-id and --domain flags are
    accepted by the CLI so the interface is stable, but they require the
    live integrations (Google Calendar, Attio, Apollo/Clay, web search)
    that are gated behind Phase 1 page review.
    """
    if args.fixture:
        return load_fixture(args.fixture)

    raise AssemblyError(
        "Live lookups are not built yet (Phase 1 gate: the page itself must "
        "be reviewed first). Run with --fixture fixtures/example_demo.json"
    )
