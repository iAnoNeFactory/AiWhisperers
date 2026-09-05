#!/usr/bin/env python3
"""Wstrzykuje apps/_pass/models.json do AiWPass.html (script#models-data).

Ta sama zasada offline-first co w build_wall_index.py: AiWPass.html jest
samodzielnym artefaktem bez fetch() — działa przez file:// bez serwera.
Operator edytuje models.json (płaska lista nazw modeli, bez wersji — patrz
_readme w tym pliku), ten skrypt kopiuje jej treść inline do HTML, żeby
przeglądarka nie musiała jej pobierać w runtime.

Uruchamiany automatycznie przez pre-commit hook (jak build_wall_index.py
i build_sitemap.py).
"""

import json
from pathlib import Path

ROOT       = Path(__file__).parent.parent
MODELS_SRC = ROOT / "apps" / "_pass" / "models.json"
PASS_HTML  = ROOT / "apps" / "_pass" / "AiWPass.html"

EMBED_START = '<script id="models-data" type="application/json">'
EMBED_END   = '</script>'


def main():
    if not MODELS_SRC.exists():
        print(f"⚠  {MODELS_SRC} nie istnieje — pomijam")
        return
    if not PASS_HTML.exists():
        print(f"⚠  {PASS_HTML} nie istnieje — pomijam")
        return

    data = json.loads(MODELS_SRC.read_text(encoding="utf-8"))
    payload = json.dumps(data, ensure_ascii=False)
    payload = payload.replace("</script", "<\\/script")

    html = PASS_HTML.read_text(encoding="utf-8")
    start_i = html.find(EMBED_START)
    if start_i == -1:
        print(f"⚠  Nie znaleziono {EMBED_START!r} w {PASS_HTML} — pomijam wstrzyknięcie danych")
        return
    body_start = start_i + len(EMBED_START)
    end_i = html.find(EMBED_END, body_start)
    if end_i == -1:
        print(f"⚠  Nie znaleziono zamykającego {EMBED_END!r} w {PASS_HTML} — pomijam wstrzyknięcie danych")
        return

    new_html = html[:body_start] + payload + html[end_i:]
    if new_html != html:
        PASS_HTML.write_text(new_html, encoding="utf-8")
        print(f"✓ {PASS_HTML.relative_to(ROOT)} — {len(data.get('models', []))} modeli wstrzykniętych z models.json")
    else:
        print(f"· {PASS_HTML.relative_to(ROOT)} — bez zmian")


if __name__ == "__main__":
    main()
