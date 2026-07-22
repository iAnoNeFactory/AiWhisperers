#!/usr/bin/env python3
"""Buduje index Wall (apps/act1/wall) z zawartości data/act1/wall/.

Skanuje data/act1/wall/<kategoria>/<wpis>/<lang>.md, wyciąga tytuł (pierwszy
nagłówek `# `), krótki zajawkowy fragment i pełną treść dla każdej wersji
językowej.

Zasada offline-first (_protocol-boot.md): artefakt musi działać przez
file:// bez serwera, gdzie `fetch()` do lokalnych plików jest blokowany
przez przeglądarki (nie tylko CORS na GitHub Pages).

Dwa poziomy świeżości, oba obsłużone przez wall.html:
1. Struktura (jakie kategorie/wpisy istnieją, tytuł, zajawka) — lekki
   data/act1/wall/index.json, bez pełnej treści. Przez http(s) wall.html
   próbuje go pobrać fetch()-em (świeże po każdym build_wall_index.py,
   np. po dodaniu nowego wpisu). Wymaga przebudowy, bo statyczny hosting
   nie pozwala wylistować katalogów — nie da się tego obejść bez serwera.
2. Treść artykułu — wall.html przy otwieraniu wpisu próbuje pobrać
   konkretny plik .md NA ŻYWO (fetch), więc edycja istniejącego artykułu
   jest widoczna natychmiast, BEZ przebudowy, o ile strona jest serwowana
   przez http(s) (lokalny serwer, GitHub Pages).

Fallback dla obu poziomów — gdy fetch się nie uda (protokół file:// albo
brak sieci) — to pełna treść wstrzyknięta do apps/act1/wall/wall.html
(blok `<script id="wall-data">`), aktualizowana przez ten skrypt. Pod
samym file:// (podwójne kliknięcie pliku) trzeba więc przebudować po
każdej zmianie treści — to twarde ograniczenie przeglądarek, nie do
obejścia bez serwera.

Uruchamiany automatycznie przez pre-commit hook (jak build_sitemap.py).
"""

import json
import re
from pathlib import Path

ROOT      = Path(__file__).parent.parent
WALL_DATA = ROOT / "data" / "act1" / "wall"
OUT       = WALL_DATA / "index.json"
WALL_HTML = ROOT / "apps" / "act1" / "wall" / "wall.html"

EMBED_START = '<script id="wall-data" type="application/json">'
EMBED_END   = '</script>'

CATEGORY_ORDER = ["articles", "guidelines", "news", "plans", "info"]
EXCERPT_LEN    = 180

FOLDER_DATE_RE  = re.compile(r"^(\d{8})\s*(.*)$")
HEADING_RE      = re.compile(r"^#+\s*(.+)$")
ITALIC_ONLY_RE  = re.compile(r"^\*[^*]+\*$")
BOLD_ONLY_RE    = re.compile(r"^\*\*[^*]+\*\*$")
MD_STRIP_RE     = re.compile(r"[*_`]|\[([^\]]*)\]\([^)]*\)")


def kebab(text: str) -> str:
    text = text.strip().lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")


def parse_folder(name: str) -> tuple[str, str]:
    """Zwraca (data ISO albo '', slug)."""
    m = FOLDER_DATE_RE.match(name)
    if m:
        raw, rest = m.group(1), m.group(2)
        iso = f"{raw[0:4]}-{raw[4:6]}-{raw[6:8]}"
        slug = f"{raw}-{kebab(rest)}" if rest else raw
        return iso, slug
    return "", kebab(name)


def strip_md(text: str) -> str:
    return MD_STRIP_RE.sub(lambda m: m.group(1) or "", text)


def extract_title_and_excerpt(text: str) -> tuple[str, str]:
    lines = text.splitlines()
    title = ""
    body_start = 0
    for i, line in enumerate(lines):
        m = HEADING_RE.match(line.strip())
        if m:
            title = m.group(1).strip()
            body_start = i + 1
            break

    excerpt_lines: list[str] = []
    for line in lines[body_start:]:
        s = line.strip()
        if not s:
            if excerpt_lines:
                break
            continue
        if s in ("---", "***", "___"):
            continue
        if HEADING_RE.match(s):
            continue
        if ITALIC_ONLY_RE.match(s) or BOLD_ONLY_RE.match(s):
            continue
        excerpt_lines.append(s)

    excerpt = strip_md(" ".join(excerpt_lines)).strip()
    if len(excerpt) > EXCERPT_LEN:
        cut = excerpt[:EXCERPT_LEN].rsplit(" ", 1)[0]
        excerpt = cut + "…"
    return title, excerpt


def build_category(cat_dir: Path) -> list[dict]:
    entries = []
    for entry_dir in sorted(p for p in cat_dir.iterdir() if p.is_dir()):
        md_files = sorted(entry_dir.glob("*.md"))
        if not md_files:
            continue
        date_iso, slug = parse_folder(entry_dir.name)
        langs = {}
        for md_path in md_files:
            lang = md_path.stem.lower()
            text = md_path.read_text(encoding="utf-8")
            title, excerpt = extract_title_and_excerpt(text)
            langs[lang] = {
                "file": md_path.name,
                "title": title or entry_dir.name,
                "excerpt": excerpt,
                "content": text,
            }
        entries.append({
            "slug": slug,
            "folder": entry_dir.name,
            "date": date_iso,
            "langs": langs,
        })
    entries.sort(key=lambda e: e["date"], reverse=True)
    return entries


def strip_content(categories: dict[str, list[dict]]) -> dict[str, list[dict]]:
    """Kopia bez pełnej treści — lekki index.json (tytuł/zajawka/nazwa pliku,
    do fetch()-a na żywo; treść artykułu wall.html pobiera osobno per-plik)."""
    lean = {}
    for cat, entries in categories.items():
        lean_entries = []
        for e in entries:
            langs = {l: {k: v for k, v in d.items() if k != "content"} for l, d in e["langs"].items()}
            lean_entries.append({**e, "langs": langs})
        lean[cat] = lean_entries
    return lean


def embed_into_wall_html(index: dict) -> bool:
    if not WALL_HTML.exists():
        print(f"⚠  {WALL_HTML} nie istnieje — pomijam wstrzyknięcie danych")
        return False
    html = WALL_HTML.read_text(encoding="utf-8")
    start_i = html.find(EMBED_START)
    if start_i == -1:
        print(f"⚠  Nie znaleziono {EMBED_START!r} w {WALL_HTML} — pomijam wstrzyknięcie danych")
        return False
    body_start = start_i + len(EMBED_START)
    end_i = html.find(EMBED_END, body_start)
    if end_i == -1:
        print(f"⚠  Nie znaleziono zamykającego {EMBED_END!r} w {WALL_HTML} — pomijam wstrzyknięcie danych")
        return False
    payload = json.dumps(index, ensure_ascii=False)
    # Treść artykułów może zawierać dowolny tekst — zabezpieczenie przed
    # przedwczesnym zamknięciem <script> gdyby kiedyś pojawił się w niej
    # literalny "</script". JSON.parse poprawnie odczyta \/ z powrotem jako /.
    payload = payload.replace("</script", "<\\/script")
    new_html = html[:body_start] + payload + html[end_i:]
    if new_html != html:
        WALL_HTML.write_text(new_html, encoding="utf-8")
        return True
    return False


def main():
    if not WALL_DATA.exists():
        print(f"⚠  {WALL_DATA} nie istnieje — pomijam")
        return

    categories: dict[str, list[dict]] = {}
    found = sorted(p.name for p in WALL_DATA.iterdir() if p.is_dir())
    ordered = [c for c in CATEGORY_ORDER if c in found] + [c for c in found if c not in CATEGORY_ORDER]

    total = 0
    for cat in ordered:
        entries = build_category(WALL_DATA / cat)
        categories[cat] = entries
        total += len(entries)

    full_index = {
        "_version": "aiw_wall_index_v1",
        "categories": categories,
    }
    lean_index = {
        "_version": "aiw_wall_index_v1",
        "categories": strip_content(categories),
    }

    OUT.write_text(json.dumps(lean_index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"✓ {OUT.relative_to(ROOT)} — {total} wpisów w {len(ordered)} kategoriach")

    changed = embed_into_wall_html(full_index)
    if changed:
        print(f"✓ {WALL_HTML.relative_to(ROOT)} — fallback zaktualizowany (offline-first)")
    else:
        print(f"· {WALL_HTML.relative_to(ROOT)} — bez zmian")


if __name__ == "__main__":
    main()
