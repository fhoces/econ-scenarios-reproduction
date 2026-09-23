#!/usr/bin/env python3
"""Render this project's tracker markdown files to styled HTML.

Handles understanding.md and coverage.md. Run with --if-stale to do nothing
unless a markdown file is newer than its html; that is the form the PostToolUse
hook in .claude/settings.json uses. Keep the filename: the hook points at it.
"""
import pathlib
import sys

import markdown

ROOT = pathlib.Path(__file__).resolve().parent
DOCS = ["understanding", "coverage"]

# The site's nav line, as on the report; relative links work for the published coverage.html.
NAV = ('<p style="font-size:14px;color:#5b6873;">'
       '<a href="explorer/">Open Output (the explorer)</a> &middot; Open Analysis: '
       '<a href="repro.html">Report</a> and <a href="slides/slides.html">Slides</a> &middot; '
       '<a href="https://github.com/fhoces/opa-ai-macro-econ-scenarios">Open Materials</a> '
       '&middot; <a href="index.html">Overview</a></p>\n')

TEMPLATE = """<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>__TITLE__</title>
<style>
  :root { --ink:#1f2933; --muted:#5b6873; --line:#d6dbe0; --bg:#ffffff;
          --solid:#1baf7a; --nearly:#eb6834; --partial:#c7a008; --none:#9aa6b2; }
  body { max-width: 900px; margin: 0 auto; padding: 2.2rem 16px 5rem;
         font: 16px/1.6 -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
         color: var(--ink); background: var(--bg); }
  h1 { font-size: 1.85rem; line-height: 1.25; margin: 0 0 .4rem; }
  h2 { font-size: 1.25rem; margin: 2.2rem 0 .6rem; padding-bottom: .3rem;
       border-bottom: 1px solid var(--line); }
  h1 + p { color: var(--muted); }
  table { border-collapse: collapse; width: 100%; margin: .8rem 0 1.2rem; font-size: 14.5px; }
  th, td { border: 1px solid var(--line); padding: 7px 10px; text-align: left; vertical-align: top; }
  th { background: #f4f6f8; font-weight: 600; }
  tbody tr:nth-child(even) { background: #fbfcfd; }
  td:nth-child(2) { white-space: nowrap; }
  td .tag { padding: 1px 8px; border-radius: 10px; color: #fff; font-size: 12.5px;
            font-weight: 650; display: inline-block; }
  hr { border: none; border-top: 1px solid var(--line); margin: 2.2rem 0; }
  code { background: #f4f6f8; padding: 1px 5px; border-radius: 3px; font-size: 90%; }
  li { margin: .3rem 0; }
  @media (max-width: 620px) { td:nth-child(2) { white-space: normal; } body { font-size: 15px; } }
</style></head><body>
__BODY__
<script>
  var tint = { "Solid": "var(--solid)", "Nearly": "var(--nearly)", "Partial": "var(--partial)",
               "Not yet": "var(--none)", "Skipping": "var(--none)" };
  document.querySelectorAll("td").forEach(function (td) {
    if (td.cellIndex !== 1) return;
    var label = td.textContent.trim(), c = tint[label];
    if (c) { td.innerHTML = '<span class="tag" style="background:' + c + '">' + label + '</span>'; }
  });
</script>
</body></html>"""


def stale(src: pathlib.Path, out: pathlib.Path) -> bool:
    if not out.exists():
        return True
    return src.stat().st_mtime > out.stat().st_mtime


def title_of(text: str, fallback: str) -> str:
    for line in text.split("\n"):
        if line.startswith("# "):
            return line[2:].split(":")[0].strip()
    return fallback


def render(stem: str, only_if_stale: bool) -> bool:
    src, out = ROOT / f"{stem}.md", ROOT / f"{stem}.html"
    if not src.exists():
        return False
    if only_if_stale and not stale(src, out):
        return False
    text = src.read_text()
    body = markdown.markdown(
        text,
        extensions=["tables", "fenced_code", "sane_lists", "attr_list"],
    )
    # Wide tables scroll inside their own box on a phone instead of widening the page.
    body = body.replace("<table>", '<div style="overflow-x:auto"><table>').replace(
        "</table>", "</table></div>")
    html = TEMPLATE.replace("__TITLE__", title_of(text, stem)).replace("__BODY__", NAV + body)
    out.write_text(html)
    print(f"rendered {out.name} ({out.stat().st_size} bytes)")
    return True


def main() -> int:
    only_if_stale = "--if-stale" in sys.argv
    for stem in DOCS:
        render(stem, only_if_stale)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
