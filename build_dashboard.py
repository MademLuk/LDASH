#!/usr/bin/env python3
"""Build LUDIZM_DASHBOARD.html from the state files.

Run from anywhere:  python3 build_dashboard.py
Reads:  states/*.md, LUDIZM_DASHBOARD.md (key dates + human KPI), FILM_INVENTORY.md
Writes: LUDIZM_DASHBOARD.html  (fixed name: the browser bookmark opens this one, never rename it)
        _builds/[LDASH_YYYY-MM-DD]_LUDIZM_DASHBOARD.html  (dated copy, same day overwrites)

Layout: calm overview first (six tiles: name, status, headline, next date).
Click a tile to open that project's full detail in a side panel.
Each state file gives its tile text with two lines under Status:
    Headline: <one short line>
    Next date: <one short line>
"""
import html
import json
import re
import shutil
from datetime import datetime
from pathlib import Path
from urllib.parse import quote

HERE = Path(__file__).resolve().parent
STATES = HERE / "states"
OUT = HERE / "LUDIZM_DASHBOARD.html"
BUILDS = HERE / "_builds"
# Notes files already applied by Claude (their note ids disappear from the page)
NOTES_DONE = HERE / "_notes"
# Favicon: 本 (ben, root / origin / foundation), embedded so the page works on its own
FAVICON = HERE / "favicon" / "ludizm_favicon.svg"
# Header logo: white 本 + LUDIZM, transparent (sits on the black header band)
LOGO = HERE / "logo" / "04_horizontal_dark-bg" / "ludizm_horizontal_dark-bg.svg"

# KIUB's own pair (Dashboard + Knowledge index), opened from the header and the KIUB panel
KIUB_DIR = Path("/Users/lude/Desktop/PNT - OYE/2_KIUB /KIUB 2026 Taff/MEGA_DOC_2026_Taff Claude")
KIUB_DASHBOARD = "file://" + quote(str(KIUB_DIR / "00_KIUB_DASHBOARD.html"))
KIUB_INDEX = "file://" + quote(str(KIUB_DIR / "KIUB_KNOWLEDGE_INDEX.html"))

# id, state file, display name, tagline, brand color
ELEMENTS = [
    ("pnt", "PNT_STATE.md", "PNT", "Po-Nad-To Foundation", "#0D7A72"),
    ("oye", "OYE_STATE.md", "OYE Prod", "Film studio + DIY tools", "#E74C3C"),
    ("oyai", "OYAI_STATE.md", "OYAI", "AI literacy trainings", "#3498DB"),
    ("saintlucia", "SAINTLUCIA_STATE.md", "Saint Lucia", "Forum 2026 + Cine Village", "#1ABC9C"),
    ("bravegens", "BRAVEGENS_STATE.md", "Brave Gens", "Merch + movement", "#FF6B2C"),
    ("kiub", "KIUB_SUMMARY.md", "KIUB", "Summary only", "#9B59E5"),
]

MAIN_SECTIONS = ["To do", "Now (this week)", "Blocked / waiting"]
NOW_VISIBLE = 3  # longer "Now" lists fold the rest away
MORE_SECTIONS = ["Content ready to show", "Leads and recruits", "Numbers (KPIs)"]
FOOTER_PREFIXES = ("Sources:", "Source:", "Folder:", "Folders:", "Red lines:", "Rule:")
FIELDS = ("Last update", "Status", "Headline", "Next date", "Next milestone", "Blocked by", "Full detail")
STATUSES = ("green", "orange", "red", "parked")
MEANING = {
    "green": "Running well, nothing blocking",
    "orange": "Running, but something is blocked or waiting",
    "red": "Going wrong or at risk, needs Lude now",
    "parked": "Paused on purpose, not worked on now",
}


def inline(text):
    """Tiny Markdown: bold, code, links, TO CHECK badge."""
    t = html.escape(text)
    t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"`(.+?)`", r"<code>\1</code>", t)
    t = re.sub(r"(https?://[^\s)<]+)", r'<a href="\1" target="_blank" rel="noopener">\1</a>', t)
    t = re.sub(r"\b(?<![\w/@.])([a-z0-9-]+\.(?:org|com|space))\b(?![^<]*</a>)",
               r'<a href="https://\1" target="_blank" rel="noopener">\1</a>', t)
    t = t.replace("TO CHECK", '<span class="tc">to check</span>')
    return t


def plain(text):
    return html.escape(re.sub(r"[*`]", "", text))


def parse_state(path):
    data = {"intro": [], "fields": {}, "sections": {}, "footer": [], "to_check": 0}
    current = None
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line:
            continue
        data["to_check"] += line.count("TO CHECK")
        if line.startswith("# "):
            continue
        if line.startswith("## "):
            current = line[3:].strip()
            data["sections"][current] = []
            continue
        if line.startswith(FOOTER_PREFIXES):
            data["footer"].append(line)
            continue
        m = re.match(r"^(" + "|".join(FIELDS) + r"):\s*(.*)$", line)
        if m and current is None:
            data["fields"][m.group(1)] = m.group(2)
            continue
        item = line[2:] if line.startswith("- ") else line
        if current is None:
            data["intro"].append(item)
        else:
            data["sections"][current].append(item)
    status = data["fields"].get("Status", "").split()
    data["status"] = status[0].lower() if status and status[0].lower() in STATUSES else "unknown"
    return data


def parse_dashboard_md():
    """Key dates and the human KPI live in LUDIZM_DASHBOARD.md."""
    path = HERE / "LUDIZM_DASHBOARD.md"
    dates, kpi, section = [], [], None
    if not path.exists():
        return dates, kpi
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if line.startswith("## "):
            section = line[3:]
            continue
        if not line:
            continue
        if section == "This month at a glance" and line.startswith("- "):
            m = re.match(r"^- \*\*(.+?):\*\*\s*(.*)$", line)
            if m:
                dates.append((m.group(1), m.group(2)))
        elif section == "Human KPI":
            kpi.append(line)
    return dates, kpi


def count_films():
    """'Films total' and 'Films online' lines in FILM_INVENTORY.md (PNT site, Wix CMS)."""
    path = HERE / "FILM_INVENTORY.md"
    if not path.exists():
        return "films TO CHECK"
    text = path.read_text(encoding="utf-8")
    total = re.search(r"^Films total:\s*(\d+)", text, flags=re.M)
    online = re.search(r"^Films online:\s*(\d+)", text, flags=re.M)
    if not total:
        return "films TO CHECK"
    return f"{total.group(1)} films" + (f" ({online.group(1)} online)" if online else "")


def list_html(items):
    if not items:
        return '<p class="empty">Nothing noted</p>'
    return "<ul>" + "".join(f"<li>{inline(i)}</li>" for i in items) + "</ul>"


def intro_html(d):
    intro = "".join(f"<p>{inline(i)}</p>" for i in d["intro"])
    return f'<div class="intro">{intro}</div>' if intro else ""


def todo_items(d):
    """'- [ ] task · owner · when' lines from the To do section."""
    out = []
    for raw in d["sections"].get("To do", []):
        done = raw.lower().startswith("[x]")
        text = raw[3:].strip() if raw[:3].lower() in ("[ ]", "[x]") else raw
        parts = [x.strip() for x in text.split(" · ")]
        out.append({"done": done, "task": parts[0], "meta": " · ".join(parts[1:]),
                    "who": parts[1] if len(parts) > 1 else "", "when": parts[2] if len(parts) > 2 else ""})
    return out


def todo_html(eid, items):
    """Open tasks first (draggable, in priority order), then a folded green 'Done' list."""
    def li(i, t):
        tid = f"{eid}-{i}"
        checked = " checked disabled" if t["done"] else ""
        meta = f'<small>{inline(t["meta"])}</small>' if t["meta"] else ""
        drag = "" if t["done"] else ' draggable="true"'
        grip = "" if t["done"] else '<span class="grip" aria-hidden="true" title="Drag to change the priority">⋮⋮</span>'
        tools = "" if t["done"] else (
            '<span class="move"><button type="button" data-move="-1" aria-label="Move up">▲</button>'
            '<button type="button" data-move="1" aria-label="Move down">▼</button></span>'
            '<button type="button" class="edit" data-edit aria-label="Edit this task" title="Edit: text, who, when">✎</button>')
        return (f'<li class="todo{" done" if t["done"] else ""}"{drag} data-text="{html.escape(t["task"])}" data-who="{html.escape(t["who"])}" data-when="{html.escape(t["when"])}">'
                f'{grip}<label>'
                f'<input type="checkbox" data-task="{tid}" data-project="{eid}" data-text="{html.escape(t["task"])}"{checked}>'
                f'<span>{inline(t["task"])}{meta}</span></label>{tools}'
                f'<button type="button" class="edit remove" data-remove aria-label="Remove this task" title="Remove this task">🗑</button></li>')
    open_li = "".join(li(i, t) for i, t in enumerate(items) if not t["done"])
    done_li = "".join(li(i, t) for i, t in enumerate(items) if t["done"])
    n_done = sum(1 for t in items if t["done"])
    empty = '' if open_li else '<p class="empty">No open tasks</p>'
    return (f'{empty}<ul class="todos" data-project="{eid}">{open_li}</ul>'
            f'<details class="done-wrap" data-project="{eid}"{"" if n_done else " hidden"}>'
            f'<summary>Done (<span class="done-n">{n_done}</span>)</summary>'
            f'<ul class="done-todos" data-project="{eid}">{done_li}</ul></details>')


def tile(idx, eid, name, color, d):
    f = d["fields"]
    headline = f.get("Headline") or (d["sections"].get("Now (this week)") or [""])[0]
    nxt = f.get("Next date") or f.get("Next milestone", "")
    open_n = sum(1 for t in todo_items(d) if not t["done"])
    todo_badge = f'<span class="todo-n">{open_n} to do</span>' if open_n else ""
    return f"""
<button class="tile glass" type="button" data-open="{eid}" style="--brand:{color}" aria-label="{name}: open details">
  <span class="bar"></span><span class="sweep"></span>
  <span class="tile-top"><span class="idx">{idx:02d}</span><span class="status s-{d['status']}" title="{MEANING.get(d['status'], '')}">{d['status']}</span></span>
  <span class="tile-top"><span class="name">{name}</span><span class="nbadge" data-badge="{eid}" hidden></span></span>
  <span class="headline">{plain(headline)}</span>
  <span class="next">{plain(nxt)}</span>
  {todo_badge}
</button>"""


def detail(eid, name, tagline, color, d):
    f = d["fields"]
    tc = d["to_check"]
    meta = f'Updated {html.escape(f.get("Last update", "?"))}' + (f' · {tc} to check' if tc else "")
    intro = intro_html(d) if eid == "kiub" else ""
    if eid == "kiub":
        body = (
            f'<section><h3>Next milestone</h3><p>{inline(f.get("Next milestone", ""))}</p></section>'
            f'<section class="blocked"><h3>Blocked by</h3><p>{inline(f.get("Blocked by", ""))}</p></section>'
            f'<section><h3>Full detail</h3><p class="links">'
            f'<a class="pillbtn" href="{KIUB_DASHBOARD}">KIUB Dashboard</a>'
            f'<a class="pillbtn" href="{KIUB_INDEX}">Knowledge index</a></p></section>'
        )
        more = ""
    else:
        body = f'<section class="todo-sec"><h3>To do</h3>{todo_html(eid, todo_items(d))}</section>'
        now = d["sections"].get("Now (this week)", [])
        rest = ""
        if len(now) > NOW_VISIBLE:
            rest = f'<details class="inline"><summary>{len(now) - NOW_VISIBLE} more</summary>{list_html(now[NOW_VISIBLE:])}</details>'
        if now:
            body += f'<section><h3>Now</h3>{list_html(now[:NOW_VISIBLE])}{rest}</section>'
        blocked = d["sections"].get("Blocked / waiting", [])
        if blocked:
            body += f'<section class="blocked"><h3>Waiting</h3>{list_html(blocked)}</section>'
        extra = [s for s in d["sections"] if s not in MAIN_SECTIONS]
        ordered = [s for s in MORE_SECTIONS if s in extra] + [s for s in extra if s not in MORE_SECTIONS]
        inner = intro_html(d) + "".join(f'<section><h3>{s}</h3>{list_html(d["sections"][s])}</section>' for s in ordered)
        more = f'<details class="more"><summary>More: background, content, leads, numbers</summary>{inner}</details>' if inner else ""
    # KIUB has no change requests: its summary is refreshed by /eotd in the KIUB project
    waiting = [n for n in inbox_notes() if n.get("project") == eid]
    inbox = ""
    if waiting:
        inbox = '<ul class="inbox">' + "".join(
            f'<li>{html.escape(n.get("text", ""))}<small>{html.escape(str(n.get("created", ""))[:16].replace("T", " "))} · waiting for Claude (6:00, /eotd or on request)</small></li>'
            for n in waiting) + "</ul>"
    notes = "" if eid == "kiub" else NOTES_BLOCK.format(eid=eid, name=name, inbox=inbox)
    footer = "".join(f'<p>{inline(x)}</p>' for x in d["footer"])
    footer = f'<details class="src"><summary>Sources</summary>{footer}</details>' if footer else ""
    return f"""
<article class="detail" id="d-{eid}" style="--brand:{color}" hidden>
  <header>
    <p class="label">{tagline}</p>
    <h2>{name}</h2>
    <p class="meta"><span class="status s-{d['status']}">{d['status']}</span> {meta}</p>
  </header>
  {intro}{body}{more}
  {notes}
  {footer}
</article>"""


NOTES_BLOCK = """<section class="notes">
    <h3>Change requests</h3>
    {inbox}
    <ul class="note-list" data-for="{eid}"></ul>
    <form class="note-form" data-for="{eid}" data-name="{name}">
      <textarea rows="3" placeholder="What should change in the {name} file?" aria-label="Change request for {name}"></textarea>
      <button type="submit">Add</button>
    </form>
  </section>"""


def inbox_notes():
    path = HERE / "_inbox" / "notes.json"
    try:
        return json.loads(path.read_text(encoding="utf-8")).get("notes", [])
    except (OSError, ValueError):
        return []


def applied_note_ids():
    ids = []
    for f in sorted(NOTES_DONE.glob("*.json")) if NOTES_DONE.exists() else []:
        try:
            ids += [n.get("id") for n in json.loads(f.read_text(encoding="utf-8")).get("notes", []) if n.get("id")]
        except (ValueError, AttributeError):
            pass
    return ids


def build():
    rows = []
    for eid, fname, name, tagline, color in ELEMENTS:
        path = STATES / fname
        if path.exists():
            rows.append((eid, name, tagline, color, parse_state(path)))
    counts = {s: sum(1 for *_, d in rows if d["status"] == s) for s in STATUSES}
    total_tc = sum(d["to_check"] for *_, d in rows)
    dates, kpi = parse_dashboard_md()
    films = count_films()
    built = datetime.now().strftime("%d %B %Y, %H:%M")
    today = datetime.now().strftime("%d %b %Y").upper()
    applied = json.dumps(applied_note_ids())

    icon = ""
    if FAVICON.exists():
        svg = " ".join(FAVICON.read_text(encoding="utf-8").split())
        icon = f'<link rel="icon" type="image/svg+xml" href="data:image/svg+xml,{quote(svg)}">'
    logo = '<span class="wordmark">LUDIZM</span>'
    if LOGO.exists():
        logo = re.sub(r"<title>.*?</title>", "", LOGO.read_text(encoding="utf-8"), flags=re.S)

    tiles = "".join(tile(i, eid, name, color, d) for i, (eid, name, _, color, d) in enumerate(rows, 1))
    details = "".join(detail(eid, name, tagline, color, d) for eid, name, tagline, color, d in rows)
    summary = " · ".join(f'<span class="sum" title="{MEANING[s]}"><span class="dot s-{s}"></span>{counts[s]} {s}</span>'
                         for s in STATUSES if counts[s])
    dates_html = "".join(f"<li><b>{plain(w)}</b>{plain(t)}</li>" for w, t in dates)
    quote_line = plain(kpi[0].strip('"')) if kpi else ""

    page = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Ludizm Dashboard</title>
{icon}
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Rajdhani:wght@500;600;700&family=Space+Grotesk:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
/* HUD theme: dark cockpit by default, "daylight" when switched to light */
:root {{
  --bg: #04070B; --bg2: #0A1420; --glass: rgba(140, 190, 230, .06); --glass-strong: rgba(9, 15, 22, .97);
  --line: rgba(160, 205, 240, .16); --line-strong: rgba(160, 205, 240, .32);
  --ink: #E6F1FA; --muted: #7F96AA; --hud: #FF6A13; --hud-soft: rgba(255, 106, 19, .14);
  --grid: rgba(120, 180, 230, .05); --shade: rgba(0, 4, 8, .78); --blocked-bg: rgba(255, 106, 19, .08);
  --s-green: #39F5A0; --s-orange: #FFB020; --s-red: #FF4D4D; --s-parked: #7C8794; --s-unknown: #7C8794;
  --glow: 0 0 10px;
}}
:root[data-theme="light"] {{
  --bg: #DCE6EE; --bg2: #F2F6F9; --glass: rgba(255, 255, 255, .55); --glass-strong: rgba(250, 252, 254, .98);
  --line: rgba(20, 50, 80, .14); --line-strong: rgba(20, 50, 80, .3);
  --ink: #0E1B26; --muted: #4F6576; --hud: #E05500; --hud-soft: rgba(224, 85, 0, .1);
  --grid: rgba(20, 60, 100, .06); --shade: rgba(20, 35, 50, .5); --blocked-bg: rgba(224, 85, 0, .07);
  --s-green: #129A5C; --s-orange: #D98200; --s-red: #D23030; --s-parked: #8794A0; --glow: 0 0 0;
}}
* {{ box-sizing: border-box; }}
html, body {{ margin: 0; }}
body {{ color: var(--ink); font: 16px/1.6 "Space Grotesk", system-ui, sans-serif; min-height: 100vh;
  background:
    radial-gradient(1200px 600px at 80% -10%, rgba(52, 152, 219, .16), transparent 60%),
    radial-gradient(900px 500px at -10% 110%, rgba(255, 106, 19, .08), transparent 60%),
    linear-gradient(var(--grid) 1px, transparent 1px) 0 0 / 48px 48px,
    linear-gradient(90deg, var(--grid) 1px, transparent 1px) 0 0 / 48px 48px,
    linear-gradient(180deg, var(--bg2), var(--bg));
  background-attachment: fixed; }}
body::after {{ content: ""; position: fixed; inset: 0; pointer-events: none;
  background: repeating-linear-gradient(0deg, rgba(255,255,255,.018) 0 1px, transparent 1px 3px); }}
:root[data-theme="light"] body::after {{ display: none; }}
body.locked {{ overflow: hidden; }}
.wrap {{ max-width: 1140px; margin: 0 auto; padding: 22px 24px 48px; position: relative; z-index: 1; }}
.mono {{ font-family: "JetBrains Mono", monospace; }}
.label {{ font: 500 11px "JetBrains Mono", monospace; text-transform: uppercase; letter-spacing: .16em; color: var(--muted); }}

/* Glass panel with HUD corner brackets */
.glass {{ position: relative; background: var(--glass); border: 1px solid var(--line);
  -webkit-backdrop-filter: blur(12px); backdrop-filter: blur(12px);
  clip-path: polygon(0 0, calc(100% - 14px) 0, 100% 14px, 100% 100%, 14px 100%, 0 calc(100% - 14px)); }}
.glass::before, .glass::after {{ content: ""; position: absolute; width: 12px; height: 12px; pointer-events: none; }}
.glass::before {{ top: 6px; left: 6px; border-top: 2px solid var(--hud); border-left: 2px solid var(--hud); }}
.glass::after {{ bottom: 6px; right: 6px; border-bottom: 2px solid var(--hud); border-right: 2px solid var(--hud); }}

/* Header bar */
.top {{ display: grid; grid-template-columns: auto 1fr auto; align-items: center; gap: 18px; padding: 14px 20px; }}
.brand svg {{ display: block; height: clamp(28px, 5vw, 38px); width: auto; }}
:root[data-theme="light"] .brand svg [stroke="#FFFFFF"] {{ stroke: #0E1B26; }}
.wordmark {{ font: 700 26px "Rajdhani", sans-serif; }}
.readout {{ display: flex; gap: 22px; justify-content: center; flex-wrap: wrap; }}
.readout div {{ display: flex; flex-direction: column; align-items: center; }}
.readout b {{ font: 600 18px "Rajdhani", sans-serif; letter-spacing: .06em; color: var(--ink); }}
.tools {{ display: flex; gap: 8px; align-items: center; }}
.tools a, .tools button {{ font: 500 11px "JetBrains Mono", monospace; letter-spacing: .12em; text-transform: uppercase;
  color: var(--ink); text-decoration: none; background: transparent; border: 1px solid var(--line-strong);
  padding: 6px 10px; cursor: pointer; }}
.tools a:hover, .tools button:hover {{ border-color: var(--hud); color: var(--hud); }}

/* Status readout */
.summary {{ margin: 18px 2px 12px; display: flex; flex-wrap: wrap; gap: 6px 18px; align-items: center; }}
.summary .label:first-child {{ color: var(--hud); }}
.sum {{ cursor: help; font: 500 12px "JetBrains Mono", monospace; text-transform: uppercase; letter-spacing: .1em; }}
.dot {{ display: inline-block; width: 8px; height: 8px; border-radius: 50%; margin-right: 8px; background: var(--s-unknown); }}
.s-green.dot, .status.s-green::before {{ background: var(--s-green); box-shadow: var(--glow) var(--s-green); }}
.s-orange.dot, .status.s-orange::before {{ background: var(--s-orange); box-shadow: var(--glow) var(--s-orange); }}
.s-red.dot, .status.s-red::before {{ background: var(--s-red); box-shadow: var(--glow) var(--s-red); animation: pulse 1.4s infinite; }}
.s-parked.dot, .status.s-parked::before {{ background: var(--s-parked); }}
@keyframes pulse {{ 50% {{ opacity: .35; }} }}

/* Tiles */
.grid {{ display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 14px; }}
.tile {{ appearance: none; -webkit-appearance: none; font: inherit; color: inherit; text-align: left; margin: 0; cursor: pointer; display: flex; flex-direction: column; gap: 8px;
  padding: 18px 20px 16px 22px; min-height: 142px; transition: border-color .2s ease, background .2s ease; }}
.tile .bar {{ position: absolute; left: 0; top: 18px; bottom: 18px; width: 3px; background: var(--brand); box-shadow: var(--glow) var(--brand); }}
.tile:hover, .tile:focus-visible {{ border-color: var(--hud); background: var(--hud-soft); outline: none; }}
.tile .sweep {{ position: absolute; inset: 0; pointer-events: none; opacity: 0;
  background: linear-gradient(100deg, transparent 30%, rgba(255,255,255,.08) 50%, transparent 70%); transform: translateX(-100%); }}
.tile:hover .sweep {{ opacity: 1; transform: translateX(100%); transition: transform .7s ease; }}
.tile-top {{ display: flex; justify-content: space-between; align-items: center; gap: 10px; }}
.idx {{ font: 500 11px "JetBrains Mono", monospace; color: var(--hud); letter-spacing: .1em; }}
.name {{ font: 700 22px/1.1 "Rajdhani", sans-serif; letter-spacing: .04em; text-transform: uppercase; }}
.status {{ font: 500 10px "JetBrains Mono", monospace; text-transform: uppercase; letter-spacing: .14em; color: var(--muted);
  display: inline-flex; align-items: center; gap: 7px; white-space: nowrap; }}
.status::before {{ content: ""; width: 7px; height: 7px; border-radius: 50%; background: var(--s-unknown); }}
.headline {{ font-size: 16px; line-height: 1.45; }}
.todo-n {{ font: 500 12px "JetBrains Mono", monospace; letter-spacing: .06em; color: var(--ink);
  border: 1px solid var(--line-strong); padding: 1px 8px; align-self: flex-start; }}
.next {{ margin-top: auto; font: 400 13px "JetBrains Mono", monospace; color: var(--muted); }}
.next::before {{ content: "NEXT ▸ "; color: var(--hud); letter-spacing: .1em; }}

/* Upcoming track */
.track {{ margin-top: 22px; padding: 16px 20px; }}
.dates {{ list-style: none; padding: 0; margin: 10px 0 0; display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 12px 18px; border-top: 1px dashed var(--line-strong); }}
.dates li {{ position: relative; padding-top: 14px; font-size: 13px; color: var(--muted); }}
.dates li::before {{ content: ""; position: absolute; top: -4px; left: 0; width: 7px; height: 7px; background: var(--hud); transform: rotate(45deg); }}
.dates b {{ display: block; font: 600 14px "Rajdhani", sans-serif; letter-spacing: .08em; text-transform: uppercase; color: var(--ink); }}

.foot {{ margin-top: 22px; display: flex; flex-wrap: wrap; justify-content: space-between; gap: 8px 20px; }}
.foot q {{ font: italic 400 13px "Space Grotesk", sans-serif; color: var(--muted); }}

/* Detail panel */
.shade {{ position: fixed; inset: 0; z-index: 5; background: var(--shade); opacity: 0; pointer-events: none; transition: opacity .2s ease; }}
.panel {{ position: fixed; z-index: 6; top: 12px; right: 12px; bottom: 12px; width: min(680px, calc(100% - 24px));
  background: var(--glass-strong); transform: translateX(110%); transition: transform .28s ease; display: flex; flex-direction: column; }}
body.open .shade {{ opacity: 1; pointer-events: auto; }}
body.open .panel {{ transform: none; }}
.panel-bar {{ display: flex; justify-content: space-between; align-items: center; padding: 16px 20px 0 24px; }}
.close {{ all: unset; cursor: pointer; font: 500 11px "JetBrains Mono", monospace; letter-spacing: .14em; color: var(--muted);
  border: 1px solid var(--line-strong); padding: 6px 10px; }}
.close:hover, .close:focus-visible {{ color: var(--hud); border-color: var(--hud); }}
.panel-body {{ overflow-y: auto; padding: 8px 40px 40px; font-size: 17px; line-height: 1.65; }}
.detail header {{ border-left: 3px solid var(--brand); padding-left: 14px; margin: 10px 0 18px; }}
.detail h2 {{ font: 700 32px/1.05 "Rajdhani", sans-serif; letter-spacing: .05em; text-transform: uppercase; margin: 4px 0 8px; }}
.meta {{ margin: 0; font: 400 12px "JetBrains Mono", monospace; color: var(--muted); display: flex; gap: 12px; align-items: center; flex-wrap: wrap; }}
.intro p {{ margin: 0 0 8px; font-size: 15px; color: var(--muted); }}
.detail section {{ margin-top: 30px; }}
.detail h3 {{ display: flex; align-items: center; gap: 10px; font: 600 15px "Rajdhani", sans-serif; text-transform: uppercase;
  letter-spacing: .16em; color: var(--hud); margin: 0 0 8px; }}
.detail h3::after {{ content: ""; flex: 1; height: 1px; background: var(--line); }}
.detail section.blocked {{ background: var(--blocked-bg); border-left: 2px solid var(--s-orange); padding: 14px 18px; }}
.detail section.blocked h3 {{ color: var(--s-orange); }}
.detail p {{ margin: 0; }}
ul {{ margin: 0; padding-left: 0; list-style: none; }}
li {{ margin: 10px 0; padding-left: 18px; position: relative; }}
.detail li::before {{ content: "›"; position: absolute; left: 0; color: var(--hud); }}
.empty {{ color: var(--muted); font-style: italic; }}
details {{ margin-top: 22px; border-top: 1px solid var(--line); padding-top: 12px; }}
summary {{ cursor: pointer; font: 500 11px "JetBrains Mono", monospace; letter-spacing: .14em; text-transform: uppercase; color: var(--muted); }}
summary:hover {{ color: var(--hud); }}
.src {{ margin-top: 22px; font-size: 12px; color: var(--muted); overflow-wrap: anywhere; }}
.src p {{ margin: 0 0 4px; }}
code {{ font: 12px "JetBrains Mono", monospace; overflow-wrap: anywhere; color: var(--muted); }}
a {{ color: var(--hud); }}
.links {{ display: flex; gap: 8px; flex-wrap: wrap; }}
.pillbtn {{ font: 500 11px "JetBrains Mono", monospace; letter-spacing: .12em; text-transform: uppercase; text-decoration: none;
  color: var(--ink); border: 1px solid var(--hud); padding: 7px 12px; }}
.pillbtn:hover {{ background: var(--hud-soft); }}
.tc {{ font: 500 10px "JetBrains Mono", monospace; letter-spacing: .1em; text-transform: uppercase; color: var(--s-orange);
  border: 1px solid currentColor; padding: 0 4px; white-space: nowrap; }}

/* Change requests */
.notes {{ margin-top: 26px; }}
.note-list li {{ display: flex; gap: 10px; align-items: flex-start; justify-content: space-between;
  border: 1px solid var(--line); background: var(--glass); padding: 8px 10px; margin: 6px 0; }}
.note-list li::before {{ display: none; }}
.note-list small {{ display: block; font: 400 11px "JetBrains Mono", monospace; color: var(--muted); }}
.note-del {{ all: unset; cursor: pointer; color: var(--muted); font-size: 13px; padding: 0 4px; }}
.note-del:hover {{ color: var(--s-red); }}
.note-form {{ display: flex; flex-direction: column; gap: 8px; margin-top: 8px; }}
.note-form textarea {{ font: 14px/1.4 "Space Grotesk", sans-serif; color: var(--ink); background: var(--glass);
  border: 1px solid var(--line-strong); padding: 10px 12px; resize: vertical; }}
.note-form textarea:focus {{ outline: none; border-color: var(--hud); }}
.note-form button, #send-notes {{ align-self: flex-start; }}
.note-form button {{ font: 500 11px "JetBrains Mono", monospace; letter-spacing: .14em; text-transform: uppercase; cursor: pointer;
  color: var(--ink); background: var(--hud-soft); border: 1px solid var(--hud); padding: 7px 14px; }}
#ncount {{ color: var(--hud); }}
#send-notes[data-empty] {{ opacity: .55; }}
.nbadge {{ font: 500 10px "JetBrains Mono", monospace; letter-spacing: .1em; color: var(--hud); border: 1px solid var(--hud); padding: 1px 6px; }}
.toast {{ position: fixed; z-index: 9; left: 50%; bottom: 22px; transform: translateX(-50%); max-width: calc(100% - 32px);
  font: 500 12px "JetBrains Mono", monospace; color: var(--ink); background: var(--glass-strong); border: 1px solid var(--hud);
  padding: 10px 14px; -webkit-backdrop-filter: blur(12px); backdrop-filter: blur(12px); }}

/* To do checklist */
.todos li {{ padding-left: 0; margin: 4px 0; display: flex; align-items: stretch; gap: 0; }}
.todos li > label {{ flex: 1; }}
.todos li.dragging {{ opacity: .35; }}
.todos li.over-top {{ box-shadow: 0 -2px 0 var(--hud); }}
.todos li.over-bottom {{ box-shadow: 0 2px 0 var(--hud); }}
.grip {{ cursor: grab; display: grid; place-items: center; width: 26px; color: var(--muted); font-size: 16px; letter-spacing: -3px;
  border: 1px solid var(--line); border-right: 0; background: var(--glass); user-select: none; }}
.grip:hover {{ color: var(--hud); }}
.move {{ display: flex; flex-direction: column; border: 1px solid var(--line); border-left: 0; background: var(--glass); }}
.move button {{ all: unset; cursor: pointer; flex: 1; padding: 0 8px; font-size: 10px; color: var(--muted); display: grid; place-items: center; }}
.move button:hover, .move button:focus-visible {{ color: var(--hud); }}
.note-list .sent {{ color: var(--s-orange); margin-left: 8px; }}
.todos .edit {{ all: unset; cursor: pointer; display: grid; place-items: center; width: 30px; color: var(--muted);
  border: 1px solid var(--line); border-left: 0; background: var(--glass); }}
.todos .edit:hover, .todos .edit:focus-visible {{ color: var(--hud); }}
.todos .remove {{ font-size: 13px; }}
.todos .remove:hover, .todos .remove:focus-visible {{ color: var(--s-red); }}
.done-todos {{ margin-top: 8px; }}
.done-todos li {{ padding-left: 0; margin: 4px 0; display: flex; align-items: stretch; }}
.done-todos li::before {{ display: none; }}
.done-todos label {{ flex: 1; display: flex; gap: 14px; align-items: flex-start; padding: 8px 12px; border: 1px solid var(--line); background: var(--glass); }}
.done-todos input {{ appearance: none; -webkit-appearance: none; flex: none; width: 18px; height: 18px; margin: 3px 0 0;
  border: 2px solid var(--s-green); background: var(--s-green); display: grid; place-items: center; }}
.done-todos input::after {{ content: "✓"; color: #000; font-size: 12px; font-weight: 700; }}
.done-todos span {{ text-decoration: line-through; opacity: .6; }}
.done-todos small {{ display: block; font: 400 12px "JetBrains Mono", monospace; color: var(--muted); }}
.done-todos .remove {{ all: unset; cursor: pointer; display: grid; place-items: center; width: 30px; color: var(--muted);
  border: 1px solid var(--line); border-left: 0; background: var(--glass); font-size: 13px; }}
.done-todos .remove:hover {{ color: var(--s-red); }}
.done-wrap {{ margin-top: 12px; border: 0; padding: 0; }}
.done-wrap > summary {{ color: var(--s-green); font: 600 14px "Rajdhani", sans-serif; letter-spacing: .14em; text-transform: uppercase; }}
.done-wrap > summary:hover {{ color: var(--s-green); filter: brightness(1.2); }}
li.removed {{ display: none !important; }}
.todos li.edited span {{ color: var(--hud); }}
.edit-form {{ flex: 1; display: grid; grid-template-columns: 1fr 1fr; gap: 8px; padding: 10px 12px; border: 1px solid var(--hud); background: var(--glass); }}
.edit-form input {{ font: 15px "Space Grotesk", sans-serif; color: var(--ink); background: transparent; border: 1px solid var(--line-strong); padding: 6px 8px; }}
.edit-form input:first-child {{ grid-column: 1 / -1; }}
.edit-form .row {{ grid-column: 1 / -1; display: flex; gap: 8px; }}
.edit-form button {{ font: 500 11px "JetBrains Mono", monospace; letter-spacing: .12em; text-transform: uppercase; cursor: pointer;
  color: var(--ink); background: var(--hud-soft); border: 1px solid var(--hud); padding: 6px 12px; }}
.edit-form button.cancel {{ background: transparent; border-color: var(--line-strong); }}
.inbox li {{ padding-left: 0; border-left: 2px solid var(--s-orange); padding: 6px 10px; margin: 6px 0; }}
.inbox li::before {{ display: none; }}
.inbox small {{ display: block; font: 400 12px "JetBrains Mono", monospace; color: var(--muted); }}
.todos li::before {{ display: none; }}
.todos label {{ display: flex; gap: 14px; align-items: flex-start; cursor: pointer; padding: 10px 12px;
  border: 1px solid var(--line); background: var(--glass); }}
.todos label:hover {{ border-color: var(--hud); }}
.todos input {{ appearance: none; -webkit-appearance: none; flex: none; width: 20px; height: 20px; margin: 3px 0 0;
  border: 2px solid var(--hud); background: transparent; cursor: pointer; display: grid; place-items: center; }}
.todos input:checked {{ background: var(--hud); }}
.todos input:checked::after {{ content: "✓"; color: #000; font-size: 14px; font-weight: 700; }}
.todos small {{ display: block; font: 400 13px "JetBrains Mono", monospace; color: var(--muted); margin-top: 2px; }}
.todos li.done span, .todos li.ticked span {{ text-decoration: line-through; opacity: .55; }}
details.inline {{ margin: 4px 0 0; border: 0; padding: 0; }}
details.more {{ margin-top: 34px; }}
details.src {{ border: 0; padding: 0; margin-top: 18px; }}

@media (max-width: 900px) {{ .grid {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }} .readout {{ display: none; }}
  .top {{ grid-template-columns: auto auto; justify-content: space-between; }} }}
@media (max-width: 560px) {{
  .wrap {{ padding: 14px 16px 40px; }}
  .grid {{ grid-template-columns: 1fr; }}
  .tile {{ min-height: 0; }}
  .panel {{ top: 0; right: 0; bottom: 0; width: 100%; }}
  .panel-body {{ padding: 8px 18px 28px; }}
}}
@media (prefers-reduced-motion: reduce) {{ .tile, .tile .sweep, .panel, .shade {{ transition: none; }} .s-red {{ animation: none; }} }}
</style>
</head>
<body>
<div class="wrap">
  <header class="top glass">
    <div class="brand">{logo}</div>
    <div class="readout">
      <div><span class="label">System</span><b>Ecosystem</b></div>
      <div><span class="label">Local time</span><b id="clock">--:--</b></div>
      <div><span class="label">Date</span><b id="date">{today}</b></div>
    </div>
    <nav class="tools">
      <a href="{KIUB_DASHBOARD}">KIUB</a>
      <a href="{KIUB_INDEX}">Index</a>
      <button type="button" id="send-notes" title="Write your changes into the files">Update <span id="ncount">0</span></button>
      <button type="button" id="theme" aria-label="Switch cockpit or daylight">◐</button>
    </nav>
  </header>

  <p class="summary"><span class="label">// Status</span>{summary}</p>
  <main class="grid">{tiles}</main>

  <section class="track glass" aria-label="Upcoming">
    <span class="label">// Upcoming</span>
    <ul class="dates">{dates_html}</ul>
  </section>

  <footer class="foot">
    <q>{quote_line}</q>
    <span class="label">本 · {total_tc} to check · {films} · built {built}</span>
  </footer>
</div>

<div class="toast" id="toast" role="status" aria-live="polite" hidden></div>
<div class="shade" data-close></div>
<aside class="panel glass" role="dialog" aria-modal="true" aria-label="Project details" aria-hidden="true">
  <div class="panel-bar"><span class="label">// Detail</span><button class="close" type="button" data-close aria-label="Close">Close ✕</button></div>
  <div class="panel-body">{details}</div>
</aside>

<script>
(function () {{
  var root = document.documentElement, body = document.body, key = "ludizm-theme";
  var panel = document.querySelector(".panel"), lastTile = null;
  try {{ var saved = localStorage.getItem(key); if (saved) root.setAttribute("data-theme", saved); }} catch (e) {{}}
  document.getElementById("theme").addEventListener("click", function () {{
    var cur = root.getAttribute("data-theme") || "dark";
    var next = cur === "dark" ? "light" : "dark";
    root.setAttribute("data-theme", next);
    try {{ localStorage.setItem(key, next); }} catch (e) {{}}
  }});

  function show(id) {{
    var target = id && document.getElementById("d-" + id);
    document.querySelectorAll(".detail").forEach(function (d) {{ d.hidden = d !== target; }});
    if (target) {{
      body.classList.add("open", "locked");
      panel.setAttribute("aria-hidden", "false");
      panel.querySelector(".panel-body").scrollTop = 0;
      panel.querySelector(".close").focus();
    }} else {{
      body.classList.remove("open", "locked");
      panel.setAttribute("aria-hidden", "true");
      if (lastTile) lastTile.focus();
    }}
  }}
  function route() {{ show(location.hash.replace("#", "")); }}
  function closeIt() {{
    try {{ history.pushState("", "", location.pathname); }} catch (e) {{ location.hash = ""; }}
    show("");
  }}
  document.querySelectorAll("[data-open]").forEach(function (t) {{
    t.addEventListener("click", function () {{ lastTile = t; location.hash = t.getAttribute("data-open"); }});
  }});
  document.querySelectorAll("[data-close]").forEach(function (c) {{
    c.addEventListener("click", closeIt);
  }});
  document.addEventListener("keydown", function (e) {{
    if (e.key === "Escape" && body.classList.contains("open")) closeIt();
  }});
  // Change requests: kept in this browser until Claude applies them
  var NK = "ludizm-notes", APPLIED = {applied};
  function load() {{ try {{ return JSON.parse(localStorage.getItem(NK)) || []; }} catch (e) {{ return []; }} }}
  function store(list) {{ try {{ localStorage.setItem(NK, JSON.stringify(list)); }} catch (e) {{}} }}
  var notes = load().filter(function (n) {{ return APPLIED.indexOf(n.id) < 0; }});
  store(notes);
  function toast(msg) {{
    var t = document.getElementById("toast"); t.textContent = msg; t.hidden = false;
    clearTimeout(toast.t); toast.t = setTimeout(function () {{ t.hidden = true; }}, 6000);
  }}
  function render() {{
    document.querySelectorAll(".note-list").forEach(function (ul) {{
      var id = ul.getAttribute("data-for"); ul.textContent = "";
      notes.filter(function (n) {{ return n.project === id; }}).forEach(function (n) {{
        var li = document.createElement("li"), txt = document.createElement("span"), when = document.createElement("small"),
            del = document.createElement("button");
        txt.textContent = n.text;
        when.textContent = n.created.slice(0, 16).replace("T", " ") + (n.sent ? "  ·  sent, waiting to be applied" : "");
        txt.appendChild(when);
        del.className = "note-del"; del.type = "button"; del.textContent = "✕"; del.setAttribute("aria-label", "Delete this note");
        del.addEventListener("click", function () {{ notes = notes.filter(function (x) {{ return x.id !== n.id; }}); store(notes); render(); }});
        li.appendChild(txt); li.appendChild(del); ul.appendChild(li);
      }});
    }});
    document.querySelectorAll("[data-badge]").forEach(function (b) {{
      var c = notes.filter(function (n) {{ return n.project === b.getAttribute("data-badge"); }}).length;
      b.hidden = !c; b.textContent = c + (c > 1 ? " NOTES" : " NOTE");
    }});
    document.getElementById("ncount").textContent = notes.length;
    document.querySelectorAll("input[data-task]:not([disabled])").forEach(function (cb) {{
      var on = notes.some(function (n) {{ return n.task === cb.getAttribute("data-task"); }});
      cb.checked = on; cb.closest("li").classList.toggle("ticked", on);
    }});
    document.querySelectorAll("ul.todos").forEach(function (ul) {{
      var on = notes.filter(function (n) {{ return n.kind === "order" && n.project === ul.getAttribute("data-project"); }}).pop();
      if (!on) return;
      var items = Array.prototype.slice.call(ul.children);
      items.sort(function (a, b) {{
        var ia = on.order.indexOf(a.getAttribute("data-text")), ib = on.order.indexOf(b.getAttribute("data-text"));
        return (ia < 0 ? 999 : ia) - (ib < 0 ? 999 : ib);
      }}).forEach(function (li) {{ ul.appendChild(li); }});
    }});
    document.querySelectorAll("li.todo").forEach(function (li) {{
      var ul = li.parentNode, pid = ul.getAttribute("data-project");
      li.classList.toggle("removed", notes.some(function (n) {{
        return n.kind === "remove" && n.project === pid && n.taskText === li.getAttribute("data-text"); }}));
    }});
    document.querySelectorAll("input[data-task]:not([disabled])").forEach(function (cb) {{
      var li = cb.closest("li"), pid = cb.getAttribute("data-project");
      var openUl = document.querySelector('ul.todos[data-project="' + pid + '"]');
      var doneUl = document.querySelector('ul.done-todos[data-project="' + pid + '"]');
      if (cb.checked && li.parentNode !== doneUl) doneUl.appendChild(li);
      if (!cb.checked && li.parentNode === doneUl) openUl.appendChild(li);
    }});
    document.querySelectorAll("details.done-wrap").forEach(function (d) {{
      var n = d.querySelectorAll("li.todo:not(.removed)").length;
      d.querySelector(".done-n").textContent = n; d.hidden = !n;
    }});
    notes.filter(function (n) {{ return n.kind === "edit"; }}).forEach(function (n) {{
      document.querySelectorAll('ul.todos[data-project="' + n.project + '"] > li').forEach(function (li) {{
        if (li.getAttribute("data-text") !== n.old) return;
        var span = li.querySelector("label > span"); if (!span) return;
        span.textContent = n.task;
        var sm = document.createElement("small"); sm.textContent = [n.who, n.when].filter(Boolean).join(" · ");
        span.appendChild(sm); li.classList.add("edited");
      }});
    }});
    var sb = document.getElementById("send-notes");
    if (notes.length) sb.removeAttribute("data-empty"); else sb.setAttribute("data-empty", "");
  }}
  document.querySelectorAll("input[data-task]:not([disabled])").forEach(function (cb) {{
    cb.addEventListener("change", function () {{
      var tid = cb.getAttribute("data-task");
      notes = notes.filter(function (n) {{ return n.task !== tid; }});
      if (cb.checked) notes.push({{ id: Date.now().toString(36) + Math.random().toString(36).slice(2, 6), task: tid, kind: "done",
        taskText: cb.getAttribute("data-text"),
        project: cb.getAttribute("data-project"), name: cb.getAttribute("data-project"),
        text: "Done: " + cb.getAttribute("data-text"), created: new Date().toISOString() }});
      store(notes); render();
    }});
  }});
  function saveOrder(ul) {{
    var pid = ul.getAttribute("data-project");
    var order = Array.prototype.map.call(ul.children, function (li) {{ return li.getAttribute("data-text"); }});
    notes = notes.filter(function (n) {{ return !(n.kind === "order" && n.project === pid); }});
    notes.push({{ id: Date.now().toString(36) + Math.random().toString(36).slice(2, 6), kind: "order", project: pid, name: pid,
      order: order, text: "New priority order: " + order.join(" > "), created: new Date().toISOString() }});
    store(notes); render();
  }}
  document.addEventListener("click", function (e) {{
    var b = e.target.closest("button[data-remove]"); if (!b) return;
    var li = b.closest("li"), pid = li.parentNode.getAttribute("data-project"), t = li.getAttribute("data-text");
    notes = notes.filter(function (n) {{ return !(n.project === pid && (n.taskText === t || n.old === t)); }});
    notes.push({{ id: Date.now().toString(36) + Math.random().toString(36).slice(2, 6), kind: "remove", project: pid, name: pid,
      taskText: t, text: "Remove: " + t, created: new Date().toISOString() }});
    store(notes); render();
    toast("Removed. Press Update to write it into the file.");
  }});
  var dragged = null;
  document.querySelectorAll("ul.todos").forEach(function (ul) {{
    ul.addEventListener("dragstart", function (e) {{
      dragged = e.target.closest("li"); if (!dragged) return;
      dragged.classList.add("dragging"); e.dataTransfer.effectAllowed = "move";
      try {{ e.dataTransfer.setData("text/plain", dragged.getAttribute("data-text")); }} catch (x) {{}}
    }});
    ul.addEventListener("dragover", function (e) {{
      var li = e.target.closest("li"); if (!dragged || !li || li === dragged || li.parentNode !== ul) return;
      e.preventDefault();
      var r = li.getBoundingClientRect(), after = e.clientY > r.top + r.height / 2;
      ul.querySelectorAll("li").forEach(function (x) {{ x.classList.remove("over-top", "over-bottom"); }});
      li.classList.add(after ? "over-bottom" : "over-top");
    }});
    ul.addEventListener("drop", function (e) {{
      var li = e.target.closest("li"); if (!dragged || !li || li === dragged || li.parentNode !== ul) return;
      e.preventDefault();
      var r = li.getBoundingClientRect();
      ul.insertBefore(dragged, e.clientY > r.top + r.height / 2 ? li.nextSibling : li);
      saveOrder(ul);
    }});
    ul.addEventListener("dragend", function () {{
      if (dragged) dragged.classList.remove("dragging"); dragged = null;
      ul.querySelectorAll("li").forEach(function (x) {{ x.classList.remove("over-top", "over-bottom"); }});
    }});
    ul.addEventListener("click", function (e) {{
      var ed = e.target.closest("button[data-edit]");
      if (ed) {{
        var eli = ed.closest("li"), lab = eli.querySelector("label");
        if (eli.querySelector(".edit-form")) return;
        var prev = notes.filter(function (n) {{ return n.kind === "edit" && n.project === ul.getAttribute("data-project") && n.old === eli.getAttribute("data-text"); }}).pop();
        var f = document.createElement("form"); f.className = "edit-form";
        [["task", "Task"], ["who", "Who"], ["when", "When"]].forEach(function (k) {{
          var i = document.createElement("input"); i.name = k[0]; i.setAttribute("aria-label", k[1]); i.placeholder = k[1];
          i.value = prev ? prev[k[0]] : (k[0] === "task" ? eli.getAttribute("data-text") : eli.getAttribute("data-" + k[0])) || "";
          f.appendChild(i);
        }});
        var row = document.createElement("div"); row.className = "row";
        row.innerHTML = '<button type="submit">Save</button><button type="button" class="cancel">Cancel</button>';
        f.appendChild(row); lab.hidden = true; eli.insertBefore(f, lab.nextSibling); eli.draggable = false;
        f.querySelector("input").focus();
        function close() {{ f.remove(); lab.hidden = false; eli.draggable = true; }}
        row.querySelector(".cancel").addEventListener("click", close);
        f.addEventListener("submit", function (ev) {{
          ev.preventDefault();
          var pid = ul.getAttribute("data-project"), old = eli.getAttribute("data-text");
          notes = notes.filter(function (n) {{ return !(n.kind === "edit" && n.project === pid && n.old === old); }});
          var v = {{ task: f.task.value.trim() || old, who: f.who.value.trim(), when: f.when.value.trim() }};
          notes.push({{ id: Date.now().toString(36) + Math.random().toString(36).slice(2, 6), kind: "edit", project: pid, name: pid,
            old: old, task: v.task, who: v.who, when: v.when,
            text: "Edit: " + old + " → " + [v.task, v.who, v.when].filter(Boolean).join(" · "), created: new Date().toISOString() }});
          store(notes); close(); render();
        }});
        return;
      }}
      var b = e.target.closest("button[data-move]"); if (!b) return;
      var li = b.closest("li"), step = +b.getAttribute("data-move");
      var other = step < 0 ? li.previousElementSibling : li.nextElementSibling;
      if (!other) return;
      ul.insertBefore(li, step < 0 ? other : other.nextSibling);
      saveOrder(ul); b.focus();
    }});
  }});
  document.querySelectorAll(".note-form").forEach(function (f) {{
    f.addEventListener("submit", function (e) {{
      e.preventDefault();
      var ta = f.querySelector("textarea"), text = ta.value.trim();
      if (!text) return;
      notes.push({{ id: Date.now().toString(36) + Math.random().toString(36).slice(2, 6), project: f.getAttribute("data-for"),
        name: f.getAttribute("data-name"), text: text, created: new Date().toISOString() }});
      store(notes); ta.value = ""; render();
    }});
  }});
  var helper = false;
  if (location.protocol.indexOf("http") === 0) {{
    fetch("/api/ping").then(function (r) {{ return r.json(); }}).then(function (j) {{ helper = !!j.ok; }}).catch(function () {{}});
  }}
  document.getElementById("send-notes").addEventListener("click", function () {{
    if (!notes.length) {{ toast("Nothing to update yet."); return; }}
    if (helper) {{
      fetch("/api/update", {{ method: "POST", headers: {{ "Content-Type": "application/json", "X-Ludizm": "1" }},
        body: JSON.stringify({{ changes: notes }}) }})
        .then(function (r) {{ return r.json(); }})
        .then(function (j) {{
          if (!j.ok) throw new Error("refused");
          notes = []; store(notes);
          toast("Updated: " + j.applied.length + " change(s) written" + (j.notes_for_claude ? ", " + j.notes_for_claude + " note(s) kept for Claude" : "") + ".");
          setTimeout(function () {{ location.reload(); }}, 1200);
        }})
        .catch(function () {{ toast("The helper did not answer. Nothing was lost: try again in a moment."); }});
      return;
    }}
    var day = new Date().toISOString().slice(0, 10), name = "ludizm_notes_" + day + ".json";
    var blob = new Blob([JSON.stringify({{ app: "ludizm", saved: new Date().toISOString(), notes: notes }}, null, 2)], {{ type: "application/json" }});
    var a = document.createElement("a"); a.href = URL.createObjectURL(blob); a.download = name;
    document.body.appendChild(a); a.click(); a.remove();
    notes.forEach(function (n) {{ n.sent = true; }}); store(notes); render();
    toast("Sent (" + name + " in Downloads). Applied at 6:00, or now if you tell Claude: apply Ludizm notes.");
  }});
  render();

  function tick() {{
    var d = new Date(), c = document.getElementById("clock"), t = document.getElementById("date");
    if (c) c.textContent = d.toLocaleTimeString("en-GB", {{ hour: "2-digit", minute: "2-digit" }});
    if (t) t.textContent = d.toLocaleDateString("en-GB", {{ day: "2-digit", month: "short", year: "numeric" }}).toUpperCase();
  }}
  tick(); setInterval(tick, 15000);
  window.addEventListener("hashchange", route);
  route();
}})();
</script>
</body>
</html>
"""
    BUILDS.mkdir(exist_ok=True)
    dated = BUILDS / f"[LDASH_{datetime.now():%Y-%m-%d}]_LUDIZM_DASHBOARD.html"
    dated.write_text(page, encoding="utf-8")
    shutil.copyfile(dated, OUT)
    print(f"Dashboard written: {OUT}")
    print(f"Dated copy: {dated}")
    print(f"Bookmark: file://{quote(str(OUT))}")
    print(f"Statuses: {counts} · TO CHECK: {total_tc} · films: {films} · dates: {len(dates)}")


if __name__ == "__main__":
    build()
