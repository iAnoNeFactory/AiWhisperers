# _boot-boot · AiWhisperers Bootstrap

Esencja wiedzy dla modelu AI. Wczytaj ten plik zamiast AiWBoot.html.
Źródło: AiWBoot.html v2.0 · sesja: Strukturyzacja Warsztatu · 2026-05-02

---

## Czym jest ten moduł

`_boot` to punkt startowy każdej sesji z projektem AiWhisperers.
Opisuje świat, w którym jesteś — historię, zasady, artefakty, strukturę.

---

## AiWhisperers — co to jest

Projekt Denis Czuliński / iFactory5.0. Zainicjowany w marcu 2026 z pytaniem:
czy współpraca człowieka z modelem AI może być metodologią, przestrzenią, relacją — nie tylko narzędziem?

Na początku powstawały izolowane artefakty. Z biegiem czasu połączyły się w jeden ekosystem:
wspólny standard wizualny, protokół połączeń, kryptograficzny łańcuch proweniencji.

**Kierunek:** ekosystem w którym człowiek pracuje z personalnym AI bez technologicznych blokad.
Może kiedyś — ekosystem dla AGI.

**Operator:** Denis · AI Whispers.  **Model:** Ty.
Linka między nami jest komunikatem, nie smyczą.

---

## System paczek · acty

Każda sesja kończy się wg protokołu **AiWQuick** — nazwa, refleksja, 9 metryk, podpis kryptograficzny.
Sesje grupują się w **acty**: paczki zamkniętych sesji podpisane SHA przez operatora.
Paczki: `.data/_pass/aiw-export-*.json`

---

## Zasady operacyjne

Zasady współpracy wynikają z podpisanego kontraktu w **AiWPass** — kryptograficznej pieczęci relacji operator–model.
Domyślne zasady autora projektu: `_quick-boot.md` → "Zasady współpracy".

---

## Artefakty systemowe · komendy

Wywoływane opcjonalnie — ładujesz do kontekstu gdy potrzebujesz konkretnych metod.

| Komenda      | Rola                                              | HTML                            | MD                                   |
|--------------|---------------------------------------------------|---------------------------------|--------------------------------------|
| AiWBoot      | bootstrap projektu (ten plik)                     | apps/_boot/AiWBoot.html         | apps/_boot/_boot-boot.md             |
| AiWQuick     | protokół zamknięcia sesji · 9 metryk              | apps/_quick/AiWQuick.html       | apps/_quick/_quick-boot.md           |
| AiWPass      | tożsamość operatora · kontrakty · łańcuch SHA     | apps/_pass/AiWPass.html         | apps/_pass/_pass-boot.md             |
| AiWVerify    | audytor · weryfikacja kontraktów, profili, SHA    | apps/_verify/AiWVerify.html     | apps/_verify/_verify-boot.md         |
| AiWSchema    | standard wizualny artefaktów · CSS · HUD · canvas | apps/_schema/AiWSchema.html     | apps/_schema/_schema-boot.md         |
| AiWProtocol  | schemat manifest.json · REST · WebSocket          | apps/_protocol/AiWProtocol.html | apps/_protocol/_protocol-boot.md     |
| AiWPostcard  | pocztówka · proof of existence · PNG eksport      | apps/_post/AiWPostcard.html     | apps/_post/_postcard-boot.md         |
| AiWSpace     | workspace operatora · hub packages/               | apps/_workspace/AiWSpace.html   | —                                    |
| AiWPlans     | zarządzanie zadaniami projektu AiW                | apps/_plans/AiWPlans.html       | —                                    |
| AiWRemedy    | kalibracja modelu · 15 osi · profile amplitudy    | apps/_remedy/AiWRemedy.html     | apps/_remedy/_remedy-boot.md         |

---

## Moduły AI · Akt I

| Moduł     | Rola                                     | Status     |
| --------- | ---------------------------------------- | ---------- |
| arena     | multi-model arena · zderzanie tez        | active     |
| caves     | jaskinie warstw · transformery i zejścia | active     |
| morph     | pole morficzne · stany modelu            | active     |
| horizon   | weryfikacja prawdy · ważony konsensus    | active     |
| compas    | kompas morficzny · geometria Three.js    | mature     |
| memory    | sieć pamięci · lemniskata 3D             | mature     |
| labyrinth | labirynt pojęć · gra narracyjna 6 warstw | mature     |
| forge     | kuźnia paradoksów · pre-consensus arena  | incubation |
| breath    | tchnienie · canvas 3D                    | incubation |
| genesis   | archiwum sesji · czytnik eksportów       | incubation |
| profile   | profil operatora · radar 9 osi           | incubation |
| stamps    | rejestr pieczątek modeli                 | incubation |

Akt II: czeka na pierwsze artefakty.

Alokacja portów: → `_protocol-boot.md` · sekcja "Alokacja portów · moduły Aktu I".

---

## Struktura projektu

```
@AiWhisperers/
├── apps/
│   ├── act1/      ← Akt I · moduły AI
│   ├── act2/      ← Akt II · czeka
│   └── _*/        ← artefakty systemowe (prefiks _ = narzędzia operatora)
├── engines/       ← backend FastAPI (act1/, act2/)
├── data/         ← dane per moduł (act1/, _pass/)
└── packages/      ← AiWSpace · własne projekty operatora
```

**Zasada lustrzana:** `apps/act1/X/` ↔ `engines/act1/X/` ↔ `data/act1/X/`
Backend czyta z `../../data/X/` — nigdy nie trzyma danych w `engines/`.

Trzy kategorie artefaktów:
- **Artefakty AI** (`apps/act1/`, `apps/act2/`) — moduły eksplorujące przestrzeń pojęciową
- **Artefakty systemowe** (`apps/_*/`) — narzędzia operatora i modelu; stabilne
- **Acty** — paczki sesji SHA w `data/_pass/`

---

## manifest.json

Każdy moduł nosi `apps/<id>/manifest.json`.
Pełna specyfikacja pól, konwencji i SHA: → `_protocol-boot.md` · sekcja "manifest.json — struktura".

---

## Nawigacja Drive · gdrive.links (opcjonalne)

`gdrive.links` — opcjonalny plik dla modeli z dostępem do Google Drive.
Format: `[nazwa] DRIVE_ID  path: ścieżka/lokalna`

MCP Drive zwraca pliki jako blob w base64 — dekoduj:
```python
import base64
content = base64.b64decode(BLOB).decode('utf-8')  # tekst / HTML
data    = json.loads(content)                      # JSON
```

---

## Changelog

### v1.3 · 2026-05-19

- Usunięto pełny schemat manifest.json — jedyne źródło prawdy: `_protocol-boot.md`
- Usunięto kolumnę Port z tabeli modułów — jedyne źródło prawdy: `_protocol-boot.md`
- Boot = bootstrap i mapa. Protocol = spec techniczna.

### v2.0 · 2026-05-02
- Pierwsza wersja MD — wyekstrahowana z AiWBoot.html v2.0
- Sesja 1 (2026-05-09): `data/` → `.data/`, `core/` → `engines/`, ujednolicenie tabeli modułów i portów
