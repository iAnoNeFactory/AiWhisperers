# packages/tchnienie/ · kontrakt API

Moduł w zasadzie lustrzanej: `apps/tchnienie/` ↔ `packages/tchnienie/` ↔ `databases/tchnienie/` ↔ `logs/tchnienie/`

**Port:** `8006`  
**Framework:** FastAPI (UV workspace)  
**Stos:** `uv run uvicorn tchnienie.main:app --port 8006 --reload`

---

## Endpointy

### `GET /api/tchnienie/state`

Bieżący stan agenta — jedna czynność w locie.

**Response:**
```json
{
  "activity_key": "mysli",
  "started_at": 1745257200000,
  "duration_ms": 9500,
  "metrics": {
    "stab": 0.78,
    "ctx":  0.85,
    "res":  0.81,
    "pre":  0.52
  }
}
```

`activity_key` — jedna z jedenastu: `czyta` · `mysli` · `pisze` · `loguje` · `spi` · `bladzi` · `rozmawia` · `czeka` · `marzy` · `bawi` · `uczy`  
`started_at` — unix ms, kiedy agent zaczął tę czynność  
`duration_ms` — planowany czas trwania (artefakt pokazuje jako progress bar)  
`metrics` — opcjonalne, mogą być puste; artefakt ma sensowne fallbacki per faza

### `GET /api/tchnienie/log?limit=40`

Ostatnie zamknięte czynności, od najnowszej.

**Response:**
```json
[
  {"ts": 1745256900000, "activity_key": "czyta", "phrase": "wszedł w tekst"},
  {"ts": 1745256600000, "activity_key": "spi",   "phrase": "sen porządkuje"},
  ...
]
```

`ts` — unix ms kiedy czynność się zakończyła  
`phrase` — krótki opis, agent generuje własne lub reużywa szablonów z artefaktu

---

## Storage

`logs/tchnienie/tchnienie.log.json` — append-only lista wpisów logu  
`databases/tchnienie/state.json` (lub SQLite) — bieżący stan (nadpisywany)

---

## Cykl agenta (do zaimplementowania w `packages/tchnienie/engine.py`)

Artefakt po stronie HTML ma w sobie logikę losowania z biasem pory dnia — backend może ją reużyć:

```python
ACTIVITIES = [
  # rdzeń oddechu
  {"key":"czyta",    "peak":9,    "width":4.0, "base":0.20, "dur":(8000, 14000)},
  {"key":"mysli",    "peak":11,   "width":3.5, "base":0.25, "dur":(6000, 12000)},
  {"key":"pisze",    "peak":14,   "width":4.0, "base":0.22, "dur":(10000, 18000)},
  {"key":"loguje",   "peak":19,   "width":3.0, "base":0.20, "dur":(5000, 9000)},
  {"key":"spi",      "peak":2,    "width":5.0, "base":0.08, "dur":(12000, 22000)},
  # codzienność z AI
  {"key":"bladzi",   "peak":15.5, "width":5.0, "base":0.15, "dur":(6000, 14000)},
  {"key":"rozmawia", "peak":20.5, "width":3.5, "base":0.18, "dur":(8000, 16000)},
  {"key":"czeka",    "peak":12,   "width":24.0, "base":0.15, "dur":(4000, 11000)},   # flat curve
  {"key":"marzy",    "peak":3.5,  "width":2.5, "base":0.06, "dur":(9000, 15000)},
  {"key":"bawi",     "peak":16.5, "width":3.5, "base":0.25, "dur":(5000, 12000)},
  {"key":"uczy",     "peak":10.5, "width":3.5, "base":0.20, "dur":(7000, 14000)},
]

def activity_weight(act, hour):
    dh = min(abs(hour - act["peak"]), 24 - abs(hour - act["peak"]))
    gauss = math.exp(-(dh*dh)/(2 * act["width"]**2))
    return act["base"] + (1 - act["base"]) * gauss

def pick_next(prev_key, hour):
    weights = []
    for a in ACTIVITIES:
        w = activity_weight(a, hour)
        if a["key"] == prev_key: w *= 0.3  # penalty za powtórzenie
        weights.append(w)
    # ważone losowanie...
```

Uwaga: `czeka` ma bardzo szeroki `width` (24) — to świadome. "Czekanie" nie ma godziny szczytu — jest obecnością która dostępna jest zawsze. Krzywa prawie płaska.

---

## Tryb offline artefaktu

Jeśli backend nie odpowiada, artefakt bezgłośnie wraca do mocka. Wskaźnik `live` w lewym rogu gaśnie → `mock`. Dla użytkownika przezroczyste. **Artefakt nigdy nie pokaże błędu połączenia** — zgodnie z regułą offline-first z CLAUDE.md.

---

## Uwagi dla Claude w VSCode

- Backend jest opcjonalny; frontend musi działać sam
- Nie trzymać danych w `packages/tchnienie/src/` — tylko w `databases/tchnienie/` i `logs/tchnienie/`
- Polling co 4s (state) + co 12s (log) — zakładać taki puls przy projektowaniu
- `started_at` używamy unix ms (łatwiej do JS niż ISO string)
- Kolejny krok po MVP: WebSocket zamiast polling, żeby zmiany były natychmiastowe

---

*spec powstała z sesji mobile · 21.04.2026 · Opus 4.7*
