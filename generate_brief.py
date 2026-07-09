#!/usr/bin/env python3
"""Generate a one-page demo-prep brief.

Phase 1 (current): fixture-driven only — develops and reviews the page
itself before any automation is built around it.

    python3 generate_brief.py --fixture fixtures/example_demo.json

The --event-id and --domain/--attendees flags exist so the CLI interface
is stable for Phases 2-3, but they error clearly until the page content
passes human review (the Phase 1 gate).
"""

import argparse
import json
import re
import sys
from pathlib import Path

from assemble import assemble, AssemblyError
from render import render_markdown

PROJECT_DIR = Path(__file__).resolve().parent


def load_config():
    with open(PROJECT_DIR / "config.json") as f:
        return json.load(f)


def slugify(name):
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-") or "brief"


def main():
    parser = argparse.ArgumentParser(description="Generate a demo-prep one-pager.")
    parser.add_argument("--fixture", help="Path to a demo payload JSON file (Phase 1 mode)")
    parser.add_argument("--event-id", help="Google Calendar event ID (Phase 3 — not yet wired)")
    parser.add_argument("--domain", help="Company domain (Phase 2 — not yet wired)")
    parser.add_argument("--attendees", help="Comma-separated attendee emails (Phase 2 — not yet wired)")
    parser.add_argument("--out-dir", help="Where to write the .md file (default: from config)")
    args = parser.parse_args()

    config = load_config()

    try:
        data = assemble(args, config)
    except AssemblyError as e:
        print(f"error: {e}", file=sys.stderr)
        sys.exit(1)

    page = render_markdown(data, max_news_bullets=config.get("news_max_bullets", 5))

    out_dir = Path(args.out_dir) if args.out_dir else PROJECT_DIR / config.get("output_dir", "briefs")
    out_dir.mkdir(parents=True, exist_ok=True)
    event_date = (data.get("event", {}).get("start") or "")[:10] or "undated"
    out_path = out_dir / f"{event_date}-{slugify(data['company']['name'])}.md"
    out_path.write_text(page)

    print(page)
    print(f"--- written to {out_path} ---", file=sys.stderr)


if __name__ == "__main__":
    main()
