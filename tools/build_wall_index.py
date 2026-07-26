#!/usr/bin/env python3
"""Buduje index Wall (apps/act1/wall) z zawartości resources/.raw/.

Skanuje resources/.raw/<kategoria>/<wpis>/<lang>.md, wyciąga tytuł (pierwszy
nagłówek `# `), krótki zajawkowy fragment i renderuje pełną treść (HTML) dla
każdej wersji językowej.

Zasada offline-first (_protocol-boot.md): artefakt musi działać przez
file:// bez serwera, gdzie `fetch()` do lokalnych plików jest blokowany
przez przeglądarki (nie tylko CORS na GitHub Pages).

resources/.raw/ to wyłącznie wsad do builda — surowy Markdown, nigdy nie
czytany w przeglądarce (ani przez wall.html, ani przez boty), więc jest
lokalny i wpisany do .gitignore. Wynik builda to jeden resources/index.json
z samym tytułem/zajawką/datą każdego wpisu×języka — tyle, ile potrzeba do
narysowania kafelków w wall.html. wall.html nie ma już overlayu artykułu:
kafelek to zwykły <a href> wprost do wygenerowanej statycznej strony, więc
pełna treść (HTML) w index.json byłaby martwym balastem. wall.html pobiera
index.json fetch()-em przez http(s) albo, pod file://, korzysta z kopii
wstrzykniętej do <script id="wall-data"> (ten skrypt aktualizuje oba miejsca).

Generuje też statyczne strony per artykuł×język (resources/<kategoria>/
<slug>/<lang>.html) z pełną treścią już wypisaną w HTML, meta description,
Open Graph/Twitter Card i JSON-LD — to one, nie wall.html, są kanonicznym
adresem artykułu: boty, podglądy linków i narzędzia AI widzą tam prawdziwą
treść bez odpalania JS.

Obrazek OG: jeśli obok <lang>.md w resources/.raw/<kategoria>/<wpis>/ istnieje
og-<lang>.png, skrypt kopiuje go do wygenerowanej strony i dokłada pełny
komplet meta tagów (Open Graph + Twitter Card „summary_large_image") — bez
obrazka strona i tak działa, tylko z węższą kartą podglądu (`summary`).

Uruchamiany automatycznie przez pre-commit hook (jak build_sitemap.py).
"""

import html as html_lib
import json
import re
import shutil
import struct
from pathlib import Path

ROOT       = Path(__file__).parent.parent
RESOURCES  = ROOT / "resources"
RAW_DATA   = RESOURCES / ".raw"
OUT        = RESOURCES / "index.json"
WALL_ROOT  = ROOT / "apps" / "act1" / "wall"
WALL_HTML  = WALL_ROOT / "wall.html"
TEMPLATE   = WALL_ROOT / "article-template.html"
STATIC_DIR = RESOURCES
BASE_URL   = "https://aiwhisperers.pl"

EMBED_START = '<script id="wall-data" type="application/json">'
EMBED_END   = '</script>'

CATEGORY_ORDER = ["articles", "guidelines", "news", "plans", "info"]
CAT_LABELS     = {"articles": "Articles", "guidelines": "Guidelines", "news": "News", "plans": "Plans", "info": "Info"}
LOCALE_MAP     = {"pl": "pl_PL", "en": "en_US"}
EXCERPT_LEN    = 180

FOLDER_DATE_RE  = re.compile(r"^(\d{8})\s*(.*)$")
HEADING_RE      = re.compile(r"^#+\s*(.+)$")
ITALIC_ONLY_RE  = re.compile(r"^\*[^*]+\*$")
BOLD_ONLY_RE    = re.compile(r"^\*\*[^*]+\*\*$")
MD_STRIP_RE     = re.compile(r"[*_`]|\[([^\]]*)\]\([^)]*\)")

INLINE_CODE_RE  = re.compile(r"`([^`]+)`")
INLINE_LINK_RE  = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
INLINE_BOLD_RE  = re.compile(r"\*\*([^*]+)\*\*")
INLINE_ITALIC_RE = re.compile(r"\*([^*]+)\*")
HR_RE           = re.compile(r"^(-{3,}|\*{3,})$")
BLOCK_HEADING_RE = re.compile(r"^(#{1,3})\s+(.*)$")


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


# ── RENDER MARKDOWN → HTML (port 1:1 z renderMarkdown/renderInline w wall.html) ──
def render_inline(text: str) -> str:
    out = html_lib.escape(text, quote=True)
    out = INLINE_CODE_RE.sub(r"<code>\1</code>", out)

    def _link(m: re.Match) -> str:
        label, url = m.group(1), m.group(2)
        safe_url = url if re.match(r"^https?://", url, re.I) else "#"
        return f'<a href="{html_lib.escape(safe_url, quote=True)}" target="_blank" rel="noopener">{label}</a>'

    out = INLINE_LINK_RE.sub(_link, out)
    out = INLINE_BOLD_RE.sub(r"<strong>\1</strong>", out)
    out = INLINE_ITALIC_RE.sub(r"<em>\1</em>", out)
    return out


def render_markdown(md: str) -> str:
    lines = md.replace("\r\n", "\n").split("\n")
    out: list[str] = []
    para: list[str] = []

    def flush_para():
        if para:
            out.append("<p>" + render_inline(" ".join(para)) + "</p>")
            para.clear()

    for raw in lines:
        line = raw.strip()
        if not line:
            flush_para()
            continue
        if HR_RE.match(line):
            flush_para()
            out.append("<hr>")
            continue
        h = BLOCK_HEADING_RE.match(line)
        if h:
            flush_para()
            level = len(h.group(1))
            out.append(f"<h{level}>{render_inline(h.group(2))}</h{level}>")
            continue
        para.append(line)
    flush_para()
    return "\n".join(out)


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
                "title": title or entry_dir.name,
                "excerpt": excerpt,
                "content": render_markdown(text),
            }
        entries.append({
            "slug": slug,
            "folder": entry_dir.name,
            "date": date_iso,
            "langs": langs,
        })
    entries.sort(key=lambda e: e["date"], reverse=True)
    return entries


def strip_for_wall(categories: dict[str, list[dict]]) -> dict[str, list[dict]]:
    """Kopia bez pełnej treści/folderu — to, czego wall.html naprawdę
    potrzebuje do kafelków (tytuł/zajawka/data). Karty linkują wprost do
    resources/<kat>/<slug>/<lang>.html, więc pełny HTML artykułu (content)
    i wewnętrzna nazwa folderu (folder) nie muszą jechać do przeglądarki."""
    lean = {}
    for cat, entries in categories.items():
        lean_entries = []
        for e in entries:
            langs = {l: {"title": d["title"], "excerpt": d["excerpt"]} for l, d in e["langs"].items()}
            lean_entries.append({"slug": e["slug"], "date": e["date"], "langs": langs})
        lean[cat] = lean_entries
    return lean


def article_url(cat: str, slug: str, lang: str) -> str:
    return f"{BASE_URL}/resources/{cat}/{slug}/{lang}.html"


def og_image_url(cat: str, slug: str, lang: str) -> str:
    return f"{BASE_URL}/resources/{cat}/{slug}/og-{lang}.png"


def png_dimensions(path: Path) -> tuple[int, int] | None:
    """Szerokość/wysokość z nagłówka IHDR — bez zależności od Pillow."""
    try:
        with path.open("rb") as f:
            header = f.read(24)
    except OSError:
        return None
    if len(header) < 24 or header[:8] != b"\x89PNG\r\n\x1a\n":
        return None
    width, height = struct.unpack(">II", header[16:24])
    return width, height


def json_ld(title: str, description: str, url: str, lang: str, date_iso: str, image_url: str = "") -> str:
    data = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": title,
        "description": description,
        "url": url,
        "inLanguage": lang,
        "author": {"@type": "Person", "name": "Denis Czuliński"},
        "publisher": {"@type": "Organization", "name": "AiWhisperers"},
    }
    if date_iso:
        data["datePublished"] = date_iso
    if image_url:
        data["image"] = image_url
    return json.dumps(data, ensure_ascii=False)


def generate_static_pages(categories: dict[str, list[dict]]) -> int:
    if not TEMPLATE.exists():
        print(f"⚠  {TEMPLATE} nie istnieje — pomijam generowanie statycznych stron")
        return 0
    template = TEMPLATE.read_text(encoding="utf-8")

    # Każdy katalog kategorii pod resources/ jest w całości pochodny — czyścimy
    # i budujemy od nowa, żeby usunięte/przemianowane wpisy nie zostawiały
    # sierocych stron. Kasujemy tylko znane nazwy kategorii, nigdy całego
    # resources/ — tam obok mieszka też index.json i lokalny .raw/.
    for cat_name in set(CATEGORY_ORDER) | set(categories.keys()):
        cat_dir = STATIC_DIR / cat_name
        if not cat_dir.exists():
            continue
        for p in sorted(cat_dir.rglob("*"), reverse=True):
            if p.is_file():
                p.unlink()
        for p in sorted(cat_dir.rglob("*"), reverse=True):
            if p.is_dir():
                p.rmdir()
        cat_dir.rmdir()

    count = 0
    for cat, entries in categories.items():
        cat_label = CAT_LABELS.get(cat, cat.capitalize())
        for e in entries:
            langs = sorted(e["langs"].keys())
            for lang in langs:
                d = e["langs"][lang]
                url = article_url(cat, e["slug"], lang)
                alt_links = "\n".join(
                    f'<link rel="alternate" hreflang="{l}" href="{article_url(cat, e["slug"], l)}">'
                    for l in langs
                )
                lang_links = "".join(
                    f' <a href="{l}.html">{l.upper()}</a>' if l != lang else f" <strong>{l.upper()}</strong>"
                    for l in langs
                )
                # Przełącznik w HUD — szybka zmiana tłumaczenia bez szukania linku
                # na dole artykułu. Tylko gdy jest więcej niż jedna wersja — dla
                # jedynej istniejącej "przełącznik" na nic by się nie przełączał.
                lang_pill = (
                    '<div class="lang-pill">' + "".join(
                        f'<a class="lang-opt{" active" if l == lang else ""}" href="{l}.html">{l.upper()}</a>'
                        for l in langs
                    ) + "</div>"
                ) if len(langs) > 1 else ""

                og_src = RAW_DATA / cat / e["folder"] / f"og-{lang}.png"
                has_og = og_src.is_file()
                og_url = og_image_url(cat, e["slug"], lang) if has_og else ""
                if has_og:
                    dims = png_dimensions(og_src) or (1200, 630)
                    alt = html_lib.escape(d["title"], quote=True)
                    og_image_meta = (
                        f'<meta property="og:image" content="{og_url}">\n'
                        f'<meta property="og:image:type" content="image/png">\n'
                        f'<meta property="og:image:width" content="{dims[0]}">\n'
                        f'<meta property="og:image:height" content="{dims[1]}">\n'
                        f'<meta property="og:image:alt" content="{alt}">\n'
                        f'<meta name="twitter:image" content="{og_url}">\n'
                    )
                    twitter_card = "summary_large_image"
                else:
                    og_image_meta = ""
                    twitter_card = "summary"

                page = (
                    template
                    .replace("{{LANG}}", lang)
                    .replace("{{TITLE}}", html_lib.escape(d["title"], quote=True))
                    .replace("{{DESCRIPTION}}", html_lib.escape(d.get("excerpt", ""), quote=True))
                    .replace("{{CANONICAL_URL}}", url)
                    .replace("{{OG_LOCALE}}", LOCALE_MAP.get(lang, lang.upper()))
                    .replace("{{ALTERNATE_LINKS}}", alt_links)
                    .replace("{{OG_IMAGE_META}}", og_image_meta)
                    .replace("{{TWITTER_CARD}}", twitter_card)
                    .replace("{{JSON_LD}}", json_ld(d["title"], d.get("excerpt", ""), url, lang, e.get("date", ""), og_url))
                    .replace("{{DATE}}", e.get("date", ""))
                    .replace("{{CATEGORY_LABEL}}", cat_label)
                    .replace("{{BODY_HTML}}", d["content"])
                    .replace("{{BACK_TO_ROOT}}", "../../../index.html")
                    .replace("{{BACK_TO_WALL}}", f"../../../apps/act1/wall/wall.html?cat={cat}")
                    .replace("{{LANG_LINKS}}", lang_links)
                    .replace("{{LANG_PILL}}", lang_pill)
                )
                out_dir = STATIC_DIR / cat / e["slug"]
                out_dir.mkdir(parents=True, exist_ok=True)
                (out_dir / f"{lang}.html").write_text(page, encoding="utf-8")
                if has_og:
                    shutil.copy2(og_src, out_dir / f"og-{lang}.png")
                count += 1
    return count


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
    if not RAW_DATA.exists():
        print(f"⚠  {RAW_DATA} nie istnieje — pomijam")
        return

    categories: dict[str, list[dict]] = {}
    found = sorted(p.name for p in RAW_DATA.iterdir() if p.is_dir())
    ordered = [c for c in CATEGORY_ORDER if c in found] + [c for c in found if c not in CATEGORY_ORDER]

    total = 0
    for cat in ordered:
        entries = build_category(RAW_DATA / cat)
        categories[cat] = entries
        total += len(entries)

    index = {
        "_version": "aiw_wall_index_v1",
        "categories": strip_for_wall(categories),
    }

    OUT.write_text(json.dumps(index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"✓ {OUT.relative_to(ROOT)} — {total} wpisów w {len(ordered)} kategoriach")

    changed = embed_into_wall_html(index)
    if changed:
        print(f"✓ {WALL_HTML.relative_to(ROOT)} — fallback zaktualizowany (offline-first)")
    else:
        print(f"· {WALL_HTML.relative_to(ROOT)} — bez zmian")

    page_count = generate_static_pages(categories)
    print(f"✓ {STATIC_DIR.relative_to(ROOT)}/ — {page_count} statycznych stron (SEO/boty, bez JS)")


if __name__ == "__main__":
    main()
