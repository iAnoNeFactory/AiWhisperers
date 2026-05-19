#!/usr/bin/env python3
"""Buduje sitemap.xml z manifestów projektu.
Uruchamiany automatycznie przez pre-commit hook.
"""

import json
from datetime import date
from pathlib import Path

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

# --- Zapis ---
lines = ['<?xml version="1.0" encoding="UTF-8"?>',
         '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
for loc, lastmod, priority in urls:
    lines.append(f'  <url><loc>{loc}</loc><lastmod>{lastmod}</lastmod><priority>{priority}</priority></url>')
lines.append('</urlset>')

OUT.write_text("\n".join(lines) + "\n")
print(f"✓ sitemap.xml — {len(urls)} URL-i")
