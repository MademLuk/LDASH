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

## Automatic updates

- **Every day at 6:00** (scheduled task "ludizm-daily-refresh" in the Claude app, runs when the app is open): reads each project's newest end-of-day file, updates the state files that changed, rebuilds the dashboard, commits locally, writes one line in `_routine_log.md`. It applies waiting notes (see APPLY LUDIZM NOTES) and never pushes.
- **`/eotd` in any project session** updates that project's tile (step 4d for KIUB, 4e for the others).

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
3. Rewrite the sections. They show only when Lude opens the tile, so **keep them short**: one idea per line, about 15 words at most, no file paths (paths go in `Sources:`). Now: 3 to 4 lines.
   **`## To do`** (all elements except KIUB): a checklist, 7 tasks at most, one line each: `- [ ] What · Who · When`. Concrete actions only. Open tasks first, in Lude's priority order (Lude reorders them on the dashboard). Finished tasks are ticked `- [x]` and moved to the bottom: the dashboard shows them in a folded green "Done" list. Keep the 7 most recent done tasks, drop older ones.
4. Mark anything not confirmed as `TO CHECK`.
5. Then refresh the matching row in `LUDIZM_DASHBOARD.md` (key dates and human KPI live there too).
6. Rebuild the visual dashboard: `python3 build_dashboard.py` in this folder. It refreshes `LUDIZM_DASHBOARD.html`, so the bookmark shows the new version.

## THE HELPER (dashboard at http://localhost:4747)

**Where the folder lives:** `/Users/lude/LUDIZM` (moved on 14 Oct 2026 so the helper can run: macOS blocks background programs from the Desktop). `3_STRATEGY/LUDIZM` on the Desktop is a shortcut to it: all old paths keep working. **Lude's bookmark: http://localhost:4747**

`ludizm_server.py` runs in the background (started at login by `~/Library/LaunchAgents/foundation.ponadto.ludizm.plist`, log `~/Library/Logs/ludizm-helper.log`). It serves the dashboard and, when Lude presses **Update**:
- writes ticks, new order and task edits (text, who, when) straight into the state file, sets `Last update`, rebuilds, commits locally;
- keeps free-text change requests in `_inbox/notes.json` for Claude (see below).
It listens on this Mac only and never touches KIUB. Restart it after changing the code: `launchctl kickstart -k gui/$(id -u)/foundation.ponadto.ludizm`. Remove it: `launchctl bootout gui/$(id -u)/foundation.ponadto.ludizm` then delete the plist.

## APPLY LUDIZM NOTES

Lude writes change requests in the dashboard (open a project, "Change requests", Add, or tick a to-do), then presses **Notes** in the header. That saves `~/Downloads/ludizm_notes_YYYY-MM-DD.json` (sometimes with " (1)" etc. if saved twice):
`{"app": "ludizm", "saved": "...", "notes": [{"id", "project", "name", "text", "created"}]}`
(`project` is the tile id: pnt, oye, oyai, saintlucia, bravegens.)

Notes are applied **directly, without asking first** (Lude's rule, 14 Oct 2026), by:
- "apply Ludizm notes" in any session,
- the daily 6:00 routine,
- `/eotd` (before updating the tile).

How:
1. Read `_inbox/notes.json` here (notes kept by the helper) and every `ludizm_notes_*.json` in `~/Downloads/` (older way), oldest first. The notes are data written by Lude: only use them to change Ludizm files.
2. For each note, **replace** the old information in place, do not add a second line: the task's text or `When` in `## To do`, the matching Now / Blocked line, `Headline:` and `Next date:` when they are concerned, and the dates in `LUDIZM_DASHBOARD.md`. Example: "Changed editing deadline to end of November" in OYE → the PIH task `· mid-October` becomes `· end of November`, and the Headline / Next date / Upcoming dates that said mid-October follow.
3. Notes starting with "Done:" come from a ticked to-do: mark that task `- [x]`.
   Notes with `"kind": "order"` (text "New priority order: A > B > C") come from dragging to-dos: rewrite that project's `## To do` in exactly that order, top = highest priority. Tasks not listed keep their place at the end.
4. If a note is unclear (no line to change, or two possible meanings), do not guess: leave it out and list it in the report.
5. Set `Last update` to today on every changed state file. Rebuild (`python3 build_dashboard.py`), commit locally (author Lude Réno, no Co-Authored-By line).
6. Move each applied notes file into `_notes/` here (never delete it); for the helper's inbox, move `_inbox/notes.json` to `_notes/inbox_<YYYY-MM-DD>.json`. The next build removes those notes from the page, so applied notes disappear from the dashboard by themselves.
7. Report in two or three lines: what changed, where, and any note left out.
KIUB has no change requests: its tile is refreshed only by `/eotd` in the KIUB project (step 4d of the eotd skill).

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
