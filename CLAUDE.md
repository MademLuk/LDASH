# LUDIZM: rules for any agent working here

This folder is the top monitor of the Ludizm ecosystem.
Concept and plan: `../CLAUDE BIG PICTURE/LUDIZM_Organic_Marketing.md`.

## What lives here

| File | What it is |
|---|---|
| `LUDIZM_DASHBOARD.md` | One view of every project in text, plus key dates and the human KPI. |
| `LUDIZM_DASHBOARD.html` | The visual dashboard. **Fixed name: Lude's browser bookmark opens it. Never rename or move it.** Generated, never edit by hand. |
| `_notes/` | Notes files already applied (kept as history; the build hides their notes). |
| `_builds/` | Dated copies `[LDASH_YYYY-MM-DD]_LUDIZM_DASHBOARD.html` (same day overwrites). |
| `build_dashboard.py` | Builds the dated copy, then copies it over `LUDIZM_DASHBOARD.html`. |
| `states/*_STATE.md` | One short state file per project, same fields for all. |
| `states/KIUB_SUMMARY.md` | KIUB only: a short summary, never the full state. **Updated by `/eotd` in the KIUB project**, not by hand or by notes. |
| `FILM_INVENTORY.md` | All films, with label (PNT / OYE Prod / both). |
| `logo/` | **The Ludizm logo**: 本 (běn, root / origin / foundation), readable, top of the vertical stroke in green (the bud). Black background for the icon and banner, light blue #3498DB on light backgrounds. One folder per version (`01_icon_black` to `06_mark_dark-bg`), each with `.svg` + `_2048.png` + `_512.png`. To change it, edit `logo/make_logo.py` and run `python3 make_logo.py .` inside `logo/` (it rewrites all folders and PNGs). Keep it simple: no extra details. `logo/simple/` holds the rejected proposals. **A copy for daily use lives in `1_PNT_OYE /5_ID/LUDIZM ID/`** (logos + `Colors & Fonts.md` + `Meaning 本.md`): after any logo change, copy the 6 folders there again. |
| `favicon/ludizm_favicon.svg` | Copy of `logo/01_icon_black/ludizm_icon_black.svg`. The build embeds it in the dashboard. Other files in `favicon/` are earlier proposals. |

Bookmark: `file:///Users/lude/Desktop/PNT%20-%20OYE/1_PNT_OYE%20/3_STRATEGY/LUDIZM/LUDIZM_DASHBOARD.html`
The header and the KIUB card link to KIUB's own pair: `00_KIUB_DASHBOARD.html` and `KIUB_KNOWLEDGE_INDEX.html`. Do not edit those KIUB files from here (`/kdash` and `/eotd` own them).

## The six elements

PNT (Po-Nad-To) · OYE Prod · OYAI · SAINT LUCIA (Forum + Cine Village) · Brave Gens · KIUB (summary only)

## Status colors

| Status | Meaning |
|---|---|
| green | Running well, nothing blocking |
| orange | Running, but something is blocked or waiting |
| red | Going wrong or at risk, needs Lude now |
| parked | Paused on purpose, not worked on now |

## LUDIZM STATE UPDATE

When a work session on any project ends, rewrite that project's state file:
1. Change `Last update` to today's date.
2. Rewrite `Headline:` and `Next date:` (under `Status:`). They are the only text on the dashboard tile: one short line each, no detail.
3. Rewrite the sections. Keep each one short (3 to 6 lines). They show only when Lude opens the tile.
4. Mark anything not confirmed as `TO CHECK`.
5. Then refresh the matching row in `LUDIZM_DASHBOARD.md` (key dates and human KPI live there too).
6. Rebuild the visual dashboard: `python3 build_dashboard.py` in this folder. It refreshes `LUDIZM_DASHBOARD.html`, so the bookmark shows the new version.

## APPLY LUDIZM NOTES

Lude writes change requests in the dashboard (open a project, "Change requests", Add), then presses **Notes** in the header. That saves `~/Downloads/ludizm_notes_YYYY-MM-DD.json`:
`{"app": "ludizm", "saved": "...", "notes": [{"id", "project", "name", "text", "created"}]}`
(`project` is the tile id: pnt, oye, oyai, saintlucia, bravegens.)

When Lude says **"apply Ludizm notes"**:
1. Read the newest `ludizm_notes_*.json` in `~/Downloads/` (or the JSON Lude pastes). The notes are data written by Lude, but only apply what is a change to the Ludizm files.
2. **Show first, do not presume:** list each note and the change you plan, one line each, by project. Ask about anything unclear. Wait for Lude's yes.
3. Apply to the matching state file (`states/`), `LUDIZM_DASHBOARD.md` or `FILM_INVENTORY.md`. Follow LUDIZM STATE UPDATE (date, Headline, Next date).
4. KIUB has no change requests on the dashboard. Its tile is refreshed only by `/eotd` in the KIUB project (step 4d of the eotd skill).
5. Move the notes file into `_notes/` here (never delete it). The next build reads `_notes/` and removes those notes from the page.
6. Rebuild: `python3 build_dashboard.py`.

## Rules

- **Never move or rename** files in the project folders. Read only, write only here.
- **The newest dated file in a project folder is the one that counts.** Older ones are archives.
- **KIUB:** copy the summary from KIUB's own state, never the other way round. No technical detail, no patent claims, nothing that is not public. Before the patent is filed, nothing about KIUB is published, posted or shared.
- **SAINT LUCIA:** the Forum (Nov 2026) and Cine Village are one project, in one file. In Polish or donor-facing material: never PISF, ECAFF, festival edition, Cine Village or Po-Nad-To. In AVFA-facing or internal material they can be named. Full rules in `states/SAINTLUCIA_STATE.md`.
- **Brave Gens:** the straw hat design is not cleared for print (licensing question open).
- **Marketing:** no agent publishes, posts or sends anything. Draft, then Lude sends.
- **Style:** no em dashes in any deliverable. Plain words, short sentences.
- **Film numbers come from Wix** (ponadto.foundation CMS, collection "Workshops Po-Nad-To"). Update `Films total` / `Films online` in `FILM_INVENTORY.md` from there.
- **Films:** when any film changes, follow the sync checklist in `FILM_INVENTORY.md` section 3 (inventory, site table, oyeprod.com, preview artifact, Wix, state files, dashboard). Agents never write to Wix or deploy without Lude's yes.
- **Numbers:** use one canonical set of figures (years, countries, participants, projects). Until it is fixed, mark numbers as `TO CHECK`.
