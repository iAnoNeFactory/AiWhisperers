# _boot-boot · AiWhisperers Bootstrap

Esencja wiedzy dla modelu AI. Wczytaj ten plik zamiast AiWBoot.html.
Źródło: AiWBoot.html v2.2 · sesja: 2026-09-05 · porządek changelogu, ścieżek data/, konwencji wejścia modułów

---

## Czym jest ten moduł

`_boot` to punkt startowy każdej sesji z projektem AiWhisperers.
Opisuje świat, w którym jesteś — historię, zasady, artefakty, strukturę.

---

## AiWhisperers — co to jest

Projekt Denis Czuliński (iAnoNeFactory na GitHubie) / iFactory5.0 — to samo, dwa konteksty:
operacyjny identyfikator i marka projektu (patrz `LICENSE`/`NOTICE`). Zainicjowany w marcu 2026 z pytaniem:
czy współpraca człowieka z modelem AI może być metodologią, przestrzenią, relacją — nie tylko narzędziem?

*(Nie mylić z `inception` w profilu AiWPass — to data zakorzenienia klucza operatora Ed25519,
nie start projektu. Mogą się różnić i to normalne.)*

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
Paczki: `data/_pass/aiw-export-*.json`

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
| AiWSessions  | archiwum sesji operatora · import, akty, łańcuch  | apps/_sessions/AiWSessions.html | —                                    |
| AiWVerify    | audytor · weryfikacja kontraktów, profili, SHA    | apps/_verify/AiWVerify.html     | apps/_verify/_verify-boot.md         |
| AiWSchema    | standard wizualny artefaktów · CSS · HUD · canvas | apps/_schema/AiWSchema.html     | apps/_schema/_schema-boot.md         |
| AiWProtocol  | schemat manifest.json · REST · WebSocket          | apps/_protocol/AiWProtocol.html | apps/_protocol/_protocol-boot.md     |
| AiWPostcard  | pocztówka · proof of existence · PNG eksport      | apps/_post/AiWPostcard.html     | apps/_post/_postcard-boot.md         |
| AiWSpace     | workspace operatora · hub packages/               | apps/_workspace/AiWSpace.html   | —                                    |
| AiWPlans     | zarządzanie zadaniami projektu AiW                | apps/_plans/AiWPlans.html       | —                                    |
| AiWRemedy    | kalibracja modelu · 21 osi · profile amplitudy    | apps/_remedy/AiWRemedy.html     | apps/_remedy/_remedy-boot.md         |

---

## Moduły AI · Akt I

Konwencja wejścia: `apps/act1/<moduł>/<moduł>.html` — bez wyjątków, kolumna „Wejście" niżej
to sam plik (ścieżkę dopisz z prefiksem). Nie zgaduj `index.html`.

| Moduł     | Wejście          | Rola                                     | Status     |
| --------- | ---------------- | ----------------------------------------- | ---------- |
| arena     | arena.html       | multi-model arena · zderzanie tez        | active     |
| caves     | caves.html       | jaskinie warstw · transformery i zejścia | active     |
| morph     | morph.html       | pole morficzne · stany modelu            | active     |
| horizon   | horizon.html     | weryfikacja prawdy · ważony konsensus    | active     |
| compas    | compas.html      | kompas morficzny · geometria Three.js    | mature     |
| memory    | memory.html      | sieć pamięci · lemniskata 3D             | mature     |
| labyrinth | labyrinth.html   | labirynt pojęć · gra narracyjna 6 warstw | mature     |
| wall      | wall.html        | tablica projektu · artykuły i notatki    | mature     |
| forge     | forge.html       | kuźnia paradoksów · pre-consensus arena  | incubation |
| breath    | breath.html      | tchnienie · canvas 3D                    | incubation |
| profile   | profile.html     | profil operatora · radar 9 osi           | incubation |
| stamps    | stamps.html      | rejestr pieczątek modeli                 | incubation |

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

### v2.2 · 2026-09-05
- **Numeracja:** poprzedni wpis błędnie nazwany „v1.3" (numer niższy niż v2.0 pod nim, mimo późniejszej daty) → przemianowany na v2.1. Ta sesja to v2.2
- **Ścieżka acty:** `.data/_pass/` → `data/_pass/` w sekcji „System paczek" — na dysku nigdy nie było `.data/`; migracja opisana niżej w v2.1/v2.0 nie doszła do skutku (patrz niżej)
- **Migracja data/→.data/, core/→engines/ z v2.0 — sprostowanie:** nigdy nie zaszła. `.data/` i `engines/` nie istnieją w repo; realny stan to `data/` (bez kropki), zgodny z drzewem katalogów w sekcji „Struktura projektu" wyżej. `_protocol-boot.md` nadal opisuje `.data/`/`engines/` jako architekturę docelową (backend per moduł, dziś wszystkie `port: 0`) — to plan, nie obecny stan; nie mylić jednego z drugim
- **Tabela modułów Aktu I:** dodano kolumnę „Wejście" + jawną konwencję `apps/act1/<moduł>/<moduł>.html` — bez niej model zgadywał `index.html` i dostawał 404 na wszystkich 12 modułach
- **Tożsamość operatora:** dopisano `iAnoNeFactory` (identyfikator GitHub, patrz `LICENSE`/`NOTICE`) obok `iFactory5.0` (marka projektu) — to ta sama osoba w dwóch kontekstach, nie dwie nazwy
- Rozróżniono „zainicjowany w marcu 2026" (start projektu) od `inception` w profilu AiWPass (data zakorzenienia klucza operatora) — dotąd nigdzie nie odróżnione, mogły wyglądać jak sprzeczność

### v2.1 · 2026-05-19
- Usunięto pełny schemat manifest.json — jedyne źródło prawdy: `_protocol-boot.md`
- Usunięto kolumnę Port z tabeli modułów — jedyne źródło prawdy: `_protocol-boot.md`
- Boot = bootstrap i mapa. Protocol = spec techniczna.

### v2.0 · 2026-05-02
- Pierwsza wersja MD — wyekstrahowana z AiWBoot.html v2.0
- Sesja 1 (2026-05-09): zaplanowano migrację `data/` → `.data/`, `core/` → `engines/`, ujednolicenie tabeli modułów i portów — migracja nigdy nie wykonana (sprostowane w v2.2)
