# _index-boot · AiWhisperers · Mapa Poznania

Esencja wiedzy dla modelu AI. Wczytaj ten plik zamiast przeglądania index.html.
Źródło: index.html v2.2 · sesja: Genesis → AiWSessions · 2026-07-22

Pełna dokumentacja projektu: `readme.html` — SHA weryfikowany przez `manifest.json` → `docs_sha`.

---

## Czym jest ten artefakt

`index.html` to **główna mapa poznania** ekosystemu AiWhisperers (~4400 linii, czyste JS + Canvas, bez frameworka).
Wczytując ten plik operator widzi cały ekosystem jako animowaną konstelację — moduły jako węzły orbity, narzędzia systemowe w dolnym barze.

Nie jest routerem ani shellą — jest przestrzenią orientacji: gdzie jesteś, co istnieje, dokąd można przejść.

---

## Struktura wizualna

### Konstelacja modułów · Akt I

Każdy moduł AI to węzeł `<div class="node">` z animowanym `<canvas data-glyph="...">`.
Węzły są pozycjonowane absolutnie (top/left w %) na tle `.akt-stage`.
Kliknięcie otwiera moduł w nowej zakładce.

Aktywne moduły (Akt I):
- `arena` · `caves` · `morph` · `horizon` (active)
- `compas` · `memory` · `labyrinth` · `wall` (mature)
- `breath` · `forge` · `profile` · `stamps` (incubation)

Akt II: osobna sekcja `.akt-stage` z komunikatem "czeka".

### Dolny bar · narzędzia operatora

`<footer class="hud hud-bottom"><nav class="narzedzia">` — 9 narzędzi:

| Glyph | Artefakt | Link |
|-------|----------|------|
| boot | AiWBoot | `apps/_boot/AiWBoot.html` |
| quick | AiWQuick | `apps/_quick/AiWQuick.html` |
| pass | AiWPass | `apps/_pass/AiWPass.html` |
| sessions | AiWSessions | `apps/_sessions/AiWSessions.html` |
| verify | AiWVerify | `apps/_verify/AiWVerify.html` |
| schema | AiWSchema | `apps/_schema/AiWSchema.html` |
| protocol | AiWProtocol | `apps/_protocol/AiWProtocol.html` |
| workspace | AiWSpace | `apps/_workspace/AiWSpace.html` |
| plany | AiWPlans | `apps/_plans/AiWPlans.html` |

### Górny bar

Lewo: linki `⟵` (map = bieżąca strona), README, POSTCARD, REMEDY
Prawo: GitHub (`iAnoNeFactory/AiWhisperers`), live indicator

---

## System GLYPHS

```javascript
const GLYPHS = {
  sun(c, t) { /* tchnienie — kula 3D */ },
  arena(c, t) { /* ... */ },
  // ... wszystkie moduły + narzędzia
};
```

Każdy `<canvas data-glyph="X">` jest rejestrowany w `glyphCanvases[]`.
Render loop: `requestAnimationFrame(loop)` wywołuje `GLYPHS[kind](c, nowMs)` dla każdego canvasu.

Konwencja parametrów:
- `c` — element `<canvas>`
- `t` — timestamp w ms (od startu animacji)
- `S = c.width` — rozmiar (56px dla narzędzi, 160px dla węzłów, 320px dla sun)

### Dodawanie nowego glypha

1. Dodaj funkcję do `GLYPHS` w `index.html`
2. Dodaj `<canvas data-glyph="nazwa">` w HTML
3. Glyph zostanie automatycznie zarejestrowany w render loop

---

## Atmosfera

```javascript
function drawAtmosphere(t) { /* gwiazdy, pył, odbicia w wodzie */ }
```

Trzy warstwy: gwiazdy, cząstki pyłu, odbicia wodne (fale sinusoidalne na dole).
Inicjalizowane przez `seedDust()`, animowane w głównym `loop()`.

---

## TCHNIENIE — live indicator

Połączenie z backendem modułu breath (port 8005):

```javascript
const TCHNIENIE_API = 'http://localhost:8005/api/breath/state';
```

Fallback offline: symulacja aktywności z biasem pory dnia (pool faz: czyta/myśli/pisze/śpi/...).
Wskaźnik: `#tchnienie-live` (data-state: active/idle) + `#tchnienie-action` (tekst fazy).

---

## Pliki powiązane

| Plik | Rola |
|------|------|
| `readme.html` | pełna dokumentacja projektu (manifesto, struktura, metryki, profile) |
| `_index-boot.md` | ten plik — wiedza dla AI |
| `manifest.json` | metadane artefaktu |

---

## Changelog

### v2.2 · 2026-07-22
- Genesis (dawniej `apps/act1/genesis/genesis.html`, incubation) przeniesiony i przemianowany na artefakt systemowy `apps/_sessions/AiWSessions.html` (status active)
- Dodano ikonę AiWSessions w dolnym barze między Pass a Verify
- Glyph `sessions` — zaadaptowany dawny glyph `genesis` (manuskrypt + słoje + pieczęć), S-relatywny więc działa też w 56px
- Węzeł Genesis w konstelacji Aktu I zastąpiony węzłem `wall` — tablica projektu na artykuły i notatki, `apps/act1/wall/wall.html` (status mature)
- Dodano glyph `wall` — kartki przypięte do ściany, stonowana paleta
- Wall czyta `data/act1/wall/<kategoria>/<wpis>/<lang>.md` przez wygenerowany `data/act1/wall/index.json` (`tools/build_wall_index.py`, wpięty w pre-commit hook obok `build_sitemap.py`) — statyczne, działa na GitHub Pages bez backendu. Auto-detekcja języka przeglądarki (PL/EN) z ręcznym przełącznikiem.
- `window.GenesisAPI` → `window.SessionsAPI`, event `genesis:updated` → `sessions:updated`

### v2.1 · 2026-05-09
- Dodano ikonę AiWVerify w dolnym barze między Pass a Schema
- Glyph `verify` — purpurowy checkmark z obracającym pierścieniem
- Stworzono `_index-boot.md` i `manifest.json` dla artefaktu root

### v2.0 · pre-changelog
- Konstelacja modułów Aktu I z animowanymi glyphami
- Dolny bar narzędzi operatora
- Atmosfera (gwiazdy, pył, odbicia)
- Połączenie z TCHNIENIE_API
