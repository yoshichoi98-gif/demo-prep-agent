"""Render an assembled demo payload into the one-page Markdown brief.

Design rules (from the spec):
  - One screen. The rep reads it in under a minute.
  - Degrade gracefully: show what's known, mark what's missing — never
    crash or silently drop a section.
  - News capped at a few dated bullets with links.
"""

UNKNOWN = "_unknown_"


def _link(label, url):
    return f"[{label} ↗]({url})" if url else None


def _employees(value, approx=False):
    """Format an employee count that may be an exact int or a range string."""
    if value is None:
        return None
    if isinstance(value, int):
        return f"~{value} employees" if approx else f"{value} employees"
    return f"{value} employees"


def _header(data):
    company = data["company"]
    name = company["name"]
    attio = _link("Attio", company.get("attio_url"))
    title = f"# {name} — Demo Prep" + (f"   {attio}" if attio else "")

    facts = [
        company.get("facility_type"),
        _employees(company.get("employee_count"), approx=True),
        company.get("location"),
    ]
    subtitle = " · ".join(f for f in facts if f)

    lines = [title]
    if company.get("net_new"):
        lines.append("> ⚠️ **Net-new** — no Attio record; all data below is from live research.")
    if subtitle:
        lines.append(subtitle)
    return lines


def _career_step(step):
    """One timeline line: `years` **Role**, Company (tenure) — note."""
    line = f"  - `{step.get('when', UNKNOWN)}` "
    if step.get("role"):
        line += f"**{step['role']}**, {step['company']}" if step.get("company") else f"**{step['role']}**"
    else:
        line += f"**{step.get('company', UNKNOWN)}**"
    if step.get("tenure"):
        line += f" ({step['tenure']})"
    if step.get("note"):
        line += f" — {step['note']}"
    return line


def _attendees(data):
    lines = ["## Attendees"]
    attendees = data.get("attendees") or []
    if not attendees:
        lines.append(f"- {UNKNOWN} — no external attendees resolved from the invite")
        return lines
    for a in attendees:
        who = a.get("name") or a.get("email") or UNKNOWN
        title = a.get("title") or f"title {UNKNOWN}"
        li = _link("LinkedIn", a.get("linkedin"))
        line = f"- **{who}** — {title}"
        if li:
            line += f" {li}"
        if not a.get("name") and a.get("email"):
            line += " _(name not found)_"
        lines.append(line)
        for step in a.get("career") or []:
            lines.append(_career_step(step))
    return lines


def _locations_line(locations):
    parts = []
    for loc in locations:
        city, state = loc.get("city"), loc.get("state")
        label = ", ".join(p for p in (city, state) if p) or loc.get("name") or UNKNOWN
        if loc.get("hq"):
            label += " (HQ)"
        parts.append(label)
    return f"- **Locations ({len(locations)}):** " + " · ".join(parts)


def _company(data):
    company = data["company"]
    lines = ["## Company"]
    lines.append(company.get("summary") or f"Summary {UNKNOWN}.")
    if company.get("facility_type"):
        lines.append(f"- **Type:** {company['facility_type']}")
    if company.get("specialties"):
        lines.append(f"- **Specialties:** {', '.join(company['specialties'])}")
    if company.get("locations"):
        lines.append(_locations_line(company["locations"]))
    facts = [
        company.get("website") or company.get("domain"),
        _employees(company.get("employee_count")),
        _link("LinkedIn", company.get("linkedin")),
    ]
    fact_line = " · ".join(f for f in facts if f)
    if fact_line:
        lines.append(fact_line)
    return lines


def _news(data, max_bullets=5):
    lines = ["## Strategic initiatives (last 6 mo)"]
    news = (data.get("news") or [])[:max_bullets]
    if not news:
        lines.append("- _No recent news found._")
        return lines
    for item in news:
        date = item.get("date", UNKNOWN)
        headline = item.get("headline", UNKNOWN)
        li = _link("link", item.get("url"))
        lines.append(f"- **{date}** — {headline}" + (f" {li}" if li else ""))
    return lines


def _history(data):
    lines = ["## Our history with them"]
    history = data.get("history") or {}

    if data["company"].get("net_new") or not history:
        lines.append("- _No prior history — net-new company._")
        return lines

    touch = history.get("last_touch") or {}
    if touch:
        lines.append(f"- Last touch: **{touch.get('date', UNKNOWN)}** — {touch.get('summary', UNKNOWN)}")
    else:
        lines.append(f"- Last touch: {UNKNOWN}")

    deal = history.get("deal") or {}
    if deal:
        deal_line = f"- Open deal: **{deal.get('stage', UNKNOWN)}** / {deal.get('owner', UNKNOWN)}"
        li = _link("deal", deal.get("attio_url"))
        if li:
            deal_line += f" {li}"
        lines.append(deal_line)

    threads = history.get("email_threads") or {}
    if threads:
        people = threads.get("people") or []
        count = threads.get("count", UNKNOWN)
        noun = "email" if count == 1 else "emails"
        lines.append(
            f"- Notable threads: **{count} {noun}** across "
            f"{len(people)} people ({', '.join(people)}), org-wide"
        )
    return lines


def render_markdown(data, max_news_bullets=5):
    """Return the full one-pager as a Markdown string."""
    sections = [
        _header(data),
        _attendees(data),
        _company(data),
        _news(data, max_news_bullets),
        _history(data),
    ]
    return "\n\n".join("\n".join(s) for s in sections) + "\n"
