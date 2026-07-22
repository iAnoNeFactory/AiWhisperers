#!/usr/bin/env python3
"""Buduje sitemap.xml z manifestów projektu.
Uruchamiany automatycznie przez pre-commit hook.
"""

import json
from datetime import date
from pathlib import Path
from xml.sax.saxutils import escape as xml_escape

BASE_URL  = "https://aiwhisperers.pl"
ROOT      = Path(__file__).parent.parent
OUT       = ROOT / "sitemap.xml"
TODAY     = date.today().isoformat()

def load_manifest(path: Path) -> dict | None:
    try:
        return json.loads(path.read_text())
    except Exception:
        return None

def entry_url(manifest_path: Path, manifest: dict) -> str | None:
    entry = manifest.get("files", {}).get("entry")
    if not entry:
        return None
    rel_dir = manifest_path.parent.relative_to(ROOT)
    return f"{BASE_URL}/{rel_dir}/{entry}"

def entry_date(manifest: dict) -> str:
    return manifest.get("date") or TODAY

urls: list[tuple[str, str, str]] = []  # (loc, lastmod, priority)

# --- Root ---
urls.append((f"{BASE_URL}/",            TODAY, "1.0"))
urls.append((f"{BASE_URL}/readme.html", TODAY, "0.8"))

# --- Narzędzia operatora: apps/_*/ ---
for mpath in sorted((ROOT / "apps").glob("_*/manifest.json")):
    m = load_manifest(mpath)
    if not m:
        continue
    url = entry_url(mpath, m)
    if url:
        urls.append((url, entry_date(m), "0.9"))

# --- Moduły Aktu I: apps/act1/*/ ---
for mpath in sorted((ROOT / "apps" / "act1").glob("*/manifest.json")):
    m = load_manifest(mpath)
    if not m:
        continue
    url = entry_url(mpath, m)
    if url:
        urls.append((url, entry_date(m), "0.8"))

# --- Wall: wpisy per kategoria/język, żeby boty trafiały wprost na artykuły ---
# Deep link: wall.html?a=<slug>&lang=<xx> (obsługiwane przez apps/act1/wall/wall.html).
WALL_INDEX = ROOT / "data" / "act1" / "wall" / "index.json"
wall_data = load_manifest(WALL_INDEX)
if wall_data:
    WALL_URL = f"{BASE_URL}/apps/act1/wall/wall.html"
    for cat, entries in wall_data.get("categories", {}).items():
        priority = "1.0" if cat in ("articles", "guidelines") else "0.7"
        for e in entries:
            lastmod = e.get("date") or TODAY
            for lang in e.get("langs", {}):
                loc = f"{WALL_URL}?a={e['slug']}&lang={lang}"
                urls.append((loc, lastmod, priority))

# --- Zapis ---
lines = ['<?xml version="1.0" encoding="UTF-8"?>',
         '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
for loc, lastmod, priority in urls:
    lines.append(f'  <url><loc>{xml_escape(loc)}</loc><lastmod>{lastmod}</lastmod><priority>{priority}</priority></url>')
lines.append('</urlset>')

OUT.write_text("\n".join(lines) + "\n")
print(f"✓ sitemap.xml — {len(urls)} URL-i")
