import json, os, urllib.request
from pathlib import Path
from xml.sax.saxutils import escape

USER = "itstahakhann"
OUT = Path("assets/latest-repositories.svg")

req = urllib.request.Request(
    f"https://api.github.com/users/{USER}/repos?sort=created&direction=desc&per_page=3",
    headers={"Accept": "application/vnd.github+json",
             "User-Agent": "github-profile-action"}
)
with urllib.request.urlopen(req, timeout=20) as r:
    repos = json.load(r)

rows = []
for i, repo in enumerate(repos[:3], 1):
    name = escape(repo.get("name", "repository"))
    desc = escape((repo.get("description") or "No description").replace("\n", " ")[:75])
    lang = escape(repo.get("language") or "—")
    rows.append((i, name, desc, lang))

svg = [
'<svg width="1200" height="300" viewBox="0 0 1200 300" xmlns="http://www.w3.org/2000/svg">',
'<rect width="1200" height="300" rx="16" fill="#0b0b0b" stroke="#222"/>',
'<text x="35" y="38" fill="#777" font-family="monospace" font-size="13">LATEST_REPOSITORIES</text>'
]
for i, name, desc, lang in rows:
    y = 82 + (i-1)*68
    svg += [
        f'<text x="35" y="{y}" fill="#555" font-family="monospace" font-size="12">0{i}</text>',
        f'<text x="75" y="{y}" fill="#fff" font-family="monospace" font-size="14">{name}</text>',
        f'<text x="300" y="{y}" fill="#777" font-family="monospace" font-size="12">{desc}</text>',
        f'<text x="1030" y="{y}" fill="#aaa" font-family="monospace" font-size="12">{lang}</text>'
    ]
svg.append('</svg>')
OUT.write_text("\n".join(svg), encoding="utf-8")
