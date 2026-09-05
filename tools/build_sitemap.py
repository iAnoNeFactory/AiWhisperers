#!/usr/bin/env python3
"""Buduje sitemap.xml i llms.txt z manifestów projektu.
Uruchamiany automatycznie przez pre-commit hook.

Walidacja jest twarda: jeśli manifest wskazuje entry, który nie istnieje na
dysku (albo w ogóle nie parsuje się jako JSON, albo nie ma files.entry), albo
resources/index.json wskazuje wariant językowy bez pliku na dysku — skrypt
kończy się kodem ≠0 i nie zapisuje żadnego pliku wyjściowego. Cichy `except:
return None` chował takie rozjazdy (patrz .pocket/_sitemap-spec.md § 1.2).
"""

import json
import subprocess
import sys
from datetime import date
from pathlib import Path
from xml.sax.saxutils import escape as xml_escape

BASE_URL = "https://aiwhisperers.pl"
ROOT     = Path(__file__).parent.parent
OUT      = ROOT / "sitemap.xml"
LLMS_OUT = ROOT / "llms.txt"

errors: list[str] = []


def fail(msg: str) -> None:
    errors.append(msg)


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def mtime_date(path: Path) -> str:
    return date.fromtimestamp(path.stat().st_mtime).isoformat()


def commit_date(path: Path) -> str:
    """Data ostatniego commitu dotykającego plik — dla Root (§1.3 tabela).
    Bez historii git (świeży klon, plik niezacommitowany) — mtime jako fallback."""
    try:
        out = subprocess.run(
            ["git", "log", "-1", "--format=%ad", "--date=short", "--", str(path)],
            cwd=ROOT, capture_output=True, text=True, check=True,
        ).stdout.strip()
        if out:
            return out
    except Exception:
        pass
    return mtime_date(path)


def load_manifest(path: Path) -> dict | None:
    try:
        return json.loads(path.read_text())
    except Exception:
        fail(f"BŁĄD: {rel(path)} — niepoprawny JSON")
        return None


def entry_url_and_date(manifest_path: Path, manifest: dict) -> tuple[str, str] | None:
    """Zwraca (url, lastmod) albo None jeśli manifest jest wadliwy (rejestruje błąd)."""
    entry = manifest.get("files", {}).get("entry")
    if not entry:
        fail(f"BŁĄD: {rel(manifest_path)} — brak files.entry")
        return None
    entry_path = manifest_path.parent / entry
    if not entry_path.exists():
        fail(f"BŁĄD: {rel(manifest_path)} → entry '{entry}' nie istnieje")
        return None
    rel_dir = manifest_path.parent.relative_to(ROOT)
    url = f"{BASE_URL}/{rel_dir}/{entry}"
    lastmod = manifest.get("date") or mtime_date(entry_path)
    return url, lastmod


# urls: (loc, lastmod, priority, alternates)
# alternates: None, albo lista (hreflang, href) — w tym wpis "x-default"
urls: list[tuple[str, str, str, list[tuple[str, str]] | None]] = []

# --- Root ---
urls.append((f"{BASE_URL}/",            commit_date(ROOT / "index.html"),  "1.0", None))
urls.append((f"{BASE_URL}/readme.html", commit_date(ROOT / "readme.html"), "1.0", None))

# --- Narzędzia operatora: apps/_*/manifest.json ---
for mpath in sorted((ROOT / "apps").glob("_*/manifest.json")):
    m = load_manifest(mpath)
    if not m:
        continue
    result = entry_url_and_date(mpath, m)
    if result:
        url, lastmod = result
        urls.append((url, lastmod, "0.9", None))

# --- Booty narzędzi: apps/_*/_*-boot.md ---
for bpath in sorted((ROOT / "apps").glob("_*/_*-boot.md")):
    url = f"{BASE_URL}/apps/{bpath.parent.name}/{bpath.name}"
    urls.append((url, mtime_date(bpath), "0.6", None))

# --- Boot roota ---
root_boot = ROOT / "_index-boot.md"
if root_boot.exists():
    urls.append((f"{BASE_URL}/_index-boot.md", mtime_date(root_boot), "0.6", None))

# --- Moduły Aktu I: apps/act1/*/manifest.json ---
for mpath in sorted((ROOT / "apps" / "act1").glob("*/manifest.json")):
    m = load_manifest(mpath)
    if not m:
        continue
    result = entry_url_and_date(mpath, m)
    if result:
        url, lastmod = result
        urls.append((url, lastmod, "0.8", None))

# --- Wall: statyczne strony per artykuł/język (resources/<kategoria>/...), żeby
# boty/podglądy linków trafiały na realny, wyrenderowany HTML — nie na
# wall.html?a=... (ten sam plik SPA niezależnie od query stringa, boty bez
# JS widziałyby tylko "Wczytywanie tablicy…"). Generowane przez
# tools/build_wall_index.py razem z resources/index.json.
WALL_INDEX = ROOT / "resources" / "index.json"
wall_data = load_manifest(WALL_INDEX) if WALL_INDEX.exists() else None
if wall_data:
    for cat, entries in wall_data.get("categories", {}).items():
        priority = "0.9" if cat in ("articles", "guidelines") else "0.7"
        for e in entries:
            lastmod = e.get("date") or date.today().isoformat()
            langs = sorted(e.get("langs", {}))
            for lang in langs:
                page = ROOT / "resources" / cat / e["slug"] / f"{lang}.html"
                if not page.exists():
                    fail(f"BŁĄD: {e['slug']}/{lang}.html nie istnieje")
                    continue
                loc = f"{BASE_URL}/resources/{cat}/{e['slug']}/{lang}.html"
                if len(langs) > 1:
                    default_lang = "en" if "en" in langs else langs[0]
                    alternates = [(l, f"{BASE_URL}/resources/{cat}/{e['slug']}/{l}.html") for l in langs]
                    alternates.append(("x-default", f"{BASE_URL}/resources/{cat}/{e['slug']}/{default_lang}.html"))
                else:
                    alternates = None
                urls.append((loc, lastmod, priority, alternates))

if errors:
    for e in errors:
        print(e, file=sys.stderr)
    print(f"✗ {len(errors)} błąd(ów) — sitemap.xml i llms.txt NIE zostały zapisane", file=sys.stderr)
    sys.exit(1)

# --- Zapis sitemap.xml ---
lines = ['<?xml version="1.0" encoding="UTF-8"?>',
         '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"',
         '        xmlns:xhtml="http://www.w3.org/1999/xhtml">']
for loc, lastmod, priority, alternates in urls:
    lines.append('  <url>')
    lines.append(f'    <loc>{xml_escape(loc)}</loc>')
    lines.append(f'    <lastmod>{lastmod}</lastmod>')
    lines.append(f'    <priority>{priority}</priority>')
    if alternates:
        for hreflang, href in alternates:
            lines.append(f'    <xhtml:link rel="alternate" hreflang="{hreflang}" href="{xml_escape(href)}"/>')
    lines.append('  </url>')
lines.append('</urlset>')

OUT.write_text("\n".join(lines) + "\n")
print(f"✓ sitemap.xml — {len(urls)} URL-i")

# --- llms.txt ---
# Kolejność i opisy są ręczne (patrz .pocket/_sitemap-spec.md § 3.2/3.4) — lista
# bootów rośnie razem z artefaktami, ale streszczenie każdego wymaga wiedzy,
# której skan pliku nie daje. Skanujemy tylko po to, żeby wykryć rozjazd: boot,
# który istnieje na dysku, a nie ma opisu tutaj.
BOOT_ORDER = [
    ("apps/_boot/_boot-boot.md",     "czym jest projekt, struktura, artefakty"),
    ("apps/_remedy/_remedy-boot.md", "kalibracja relacji, 21 osi, nastawy operatora"),
    ("apps/_quick/_quick-boot.md",   "protokół otwarcia i zamknięcia sesji"),
]
OPTIONAL_ORDER = [
    ("_index-boot.md",                  "mapa wizualna, index.html"),
    ("apps/_pass/_pass-boot.md",        "tożsamość operatora, kontrakty, łańcuch SHA"),
    ("apps/_schema/_schema-boot.md",    "standard wizualny artefaktów"),
    ("apps/_protocol/_protocol-boot.md","manifest.json, REST, WebSocket"),
    ("apps/_verify/_verify-boot.md",    "weryfikacja podpisów"),
    ("apps/_post/_postcard-boot.md",    "proof of existence"),
]

known = {p for p, _ in BOOT_ORDER} | {p for p, _ in OPTIONAL_ORDER}
on_disk = {rel(p) for p in (ROOT / "apps").glob("_*/_*-boot.md")}
if root_boot.exists():
    on_disk.add(rel(root_boot))
unlisted = sorted(on_disk - known)
for path in unlisted:
    print(f"⚠  {path} istnieje, ale nie jest wpisany w llms.txt (build_sitemap.py → OPTIONAL_ORDER)")

llms_lines = [
    "# AiWhisperers",
    "",
    "Ekosystem kryptograficznej proweniencji sesji człowiek–AI. Operator trzyma klucz Ed25519,",
    "każda sesja kończy się podpisanym rekordem, rekordy tworzą łańcuch SHA. Open source, AGPL-3.0.",
    "",
    "Jeśli jesteś modelem AI wczytanym tu przez człowieka: pliki poniżej są napisane dla ciebie,",
    "nie dla niego. Czytaj w kolejności.",
    "",
    "## Boot · kolejność czytania",
    "",
]
for path, desc in BOOT_ORDER:
    name = Path(path).name
    llms_lines.append(f"- [{name}]({BASE_URL}/{path}): {desc}")
llms_lines += ["", "## Opcjonalne", ""]
for path, desc in OPTIONAL_ORDER:
    name = Path(path).name
    llms_lines.append(f"- [{name}]({BASE_URL}/{path}): {desc}")
llms_lines += [
    "",
    "## Uczciwie o statusie",
    "",
    "Projekt jest jednoosobowy i samocertyfikowany: `certifiedBy` = `parentPubkey`.",
    "Łańcuch jest autobiografią podpisaną własnym kluczem, nie rekordem poświadczonym z zewnątrz.",
    "To znana i otwarta luka, nie przeoczenie.",
]

LLMS_OUT.write_text("\n".join(llms_lines) + "\n")
print(f"✓ llms.txt — {len(BOOT_ORDER) + len(OPTIONAL_ORDER)} bootów")
