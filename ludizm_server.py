#!/usr/bin/env python3
"""Ludizm helper: shows the dashboard at http://localhost:4747 and writes dashboard changes into the files.

- Ticks, new order and edits of a to-do are written into the state file at once, then the page is rebuilt.
- Free-text change requests are kept in _inbox/notes.json for Claude (6:00 routine, /eotd, "apply Ludizm notes").
- Listens on this Mac only (127.0.0.1). No internet, no other folder. KIUB is never changed here.

Started at login by ~/Library/LaunchAgents/foundation.ponadto.ludizm.plist
Run by hand:  python3 ludizm_server.py
"""
import json
import os
import re
import subprocess
import sys
from datetime import date, datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

HERE = Path(__file__).resolve().parent
PORT = int(os.environ.get("LUDIZM_PORT", "4747"))
STATES = HERE / "states"
INBOX = HERE / "_inbox" / "notes.json"
PAGE = HERE / "LUDIZM_DASHBOARD.html"
FILES = {
    "pnt": "PNT_STATE.md",
    "oye": "OYE_STATE.md",
    "oyai": "OYAI_STATE.md",
    "saintlucia": "SAINTLUCIA_STATE.md",
    "bravegens": "BRAVEGENS_STATE.md",
}  # KIUB is updated only by /eotd
TASK_LINE = re.compile(r"^- \[( |x|X)\] (.*)$")


def clean(value, limit=300):
    return " ".join(str(value or "").split())[:limit].replace(" · ", ", ")


def todo_block(text):
    """Return (start, end) line indexes of the '## To do' list."""
    lines = text.split("\n")
    try:
        start = lines.index("## To do") + 1
    except ValueError:
        return lines, None, None
    end = start
    while end < len(lines) and TASK_LINE.match(lines[end]):
        end += 1
    return lines, start, end


def task_of(line):
    m = TASK_LINE.match(line)
    return m.group(2).split(" · ")[0].strip() if m else None


def apply_structured(project, changes):
    """Order first, then ticks, then edits: all of them name tasks by their text as it is in the file."""
    path = STATES / FILES[project]
    lines, start, end = todo_block(path.read_text(encoding="utf-8"))
    if start is None:
        return []
    tasks = lines[start:end]
    done = []
    for c in changes:
        if c.get("kind") == "order":
            wanted = [str(t) for t in c.get("order", [])]
            tasks.sort(key=lambda l: wanted.index(task_of(l)) if task_of(l) in wanted else 999)
            done.append("new order")
    for c in changes:
        if c.get("kind") == "done":
            for i, l in enumerate(tasks):
                if task_of(l) == c.get("taskText"):
                    tasks[i] = l.replace("- [ ]", "- [x]", 1)
                    done.append("ticked: " + task_of(l))
    for c in changes:
        if c.get("kind") == "edit":
            for i, l in enumerate(tasks):
                if task_of(l) == c.get("old"):
                    box = "- [x]" if l.startswith("- [x]") else "- [ ]"
                    parts = [clean(c.get("task")) or c.get("old"), clean(c.get("who"), 60), clean(c.get("when"), 60)]
                    tasks[i] = box + " " + " · ".join(p for p in parts if p)
                    done.append("edited: " + parts[0])
    if done:
        lines[start:end] = tasks
        text = "\n".join(lines)
        text = re.sub(r"^Last update: .*$", "Last update: " + date.today().isoformat(), text, count=1, flags=re.M)
        path.write_text(text, encoding="utf-8")
    return done


def keep_for_claude(notes):
    INBOX.parent.mkdir(exist_ok=True)
    old = []
    if INBOX.exists():
        try:
            old = json.loads(INBOX.read_text(encoding="utf-8")).get("notes", [])
        except ValueError:
            old = []
    for n in notes:
        old.append({"id": clean(n.get("id"), 40), "project": n.get("project"), "text": clean(n.get("text"), 1000),
                    "created": clean(n.get("created"), 40)})
    INBOX.write_text(json.dumps({"app": "ludizm", "notes": old}, ensure_ascii=False, indent=2), encoding="utf-8")


def rebuild_and_commit(summary):
    subprocess.run([sys.executable, str(HERE / "build_dashboard.py")], cwd=HERE, capture_output=True)
    subprocess.run(["git", "add", "states", "LUDIZM_DASHBOARD.html", "LUDIZM_DASHBOARD.md"], cwd=HERE, capture_output=True)
    subprocess.run(["git", "commit", "-q", "-m", "Dashboard update: " + summary[:120]], cwd=HERE, capture_output=True)


class Handler(BaseHTTPRequestHandler):
    def _send(self, code, body, ctype="application/json"):
        data = body if isinstance(body, bytes) else json.dumps(body).encode()
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _local(self):
        host = (self.headers.get("Host") or "").split(":")[0]
        return host in ("localhost", "127.0.0.1")

    def do_GET(self):
        if not self._local():
            return self._send(403, {"ok": False})
        if self.path in ("/", "/index.html"):
            return self._send(200, PAGE.read_bytes(), "text/html; charset=utf-8")
        if self.path == "/api/ping":
            return self._send(200, {"ok": True, "app": "ludizm"})
        return self._send(404, {"ok": False})

    def do_POST(self):
        # The custom header blocks other websites: browsers cannot send it cross-site without a preflight we never answer.
        if not self._local() or self.path != "/api/update" or self.headers.get("X-Ludizm") != "1":
            return self._send(403, {"ok": False})
        try:
            size = min(int(self.headers.get("Content-Length", 0)), 200_000)
            changes = json.loads(self.rfile.read(size) or b"{}").get("changes", [])
        except ValueError:
            return self._send(400, {"ok": False, "error": "bad data"})
        applied, notes = [], []
        for project in FILES:
            mine = [c for c in changes if c.get("project") == project and c.get("kind") in ("order", "done", "edit")]
            if mine:
                applied += [project + ": " + x for x in apply_structured(project, mine)]
        notes = [c for c in changes if c.get("project") in FILES and c.get("kind") not in ("order", "done", "edit")]
        if notes:
            keep_for_claude(notes)
        if applied or notes:
            rebuild_and_commit("; ".join(applied) or "notes kept for Claude")
        with open(HERE / "_helper.log", "a", encoding="utf-8") as log:
            log.write(f"{datetime.now():%Y-%m-%d %H:%M} applied={len(applied)} notes_for_claude={len(notes)}\n")
        return self._send(200, {"ok": True, "applied": applied, "notes_for_claude": len(notes)})

    def log_message(self, *args):
        pass


if __name__ == "__main__":
    ThreadingHTTPServer(("127.0.0.1", PORT), Handler).serve_forever()
