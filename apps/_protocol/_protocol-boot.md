# _protocol-boot · AiWhisperers Protocol & Manifest

Esencja wiedzy dla modelu AI. Wczytaj ten plik zamiast AiWProtocol.html.
Źródło: AiWProtocol.html v1.0 · sesja: Wyrównanie Protokołu · 2026-05-02

---

## Czym jest ten moduł

`_protocol` to meta-moduł dokumentujący dwie rzeczy:
1. **Schemat manifest.json** — paszport każdego modułu w ekosystemie AiWhisperers
2. **Protokół połączeń artefakt↔backend** — REST polling i WebSocket

---

## manifest.json — struktura

Każdy moduł ma `apps/<id>/manifest.json`. Pola wymagane:

```json
{
  "id":          "kebab-case, stabilny, nigdy się nie zmienia",
  "name":        "Żywa nazwa · może mieć emoji i polskie znaki",
  "version":     "2.0",
  "date":        "2026-05-02",
  "description": "Jedno zdanie. Co to jest i co robi.",
  "type":        "słownik otwarty: standalone, consensus-engine, protocol-schema, ...",
  "status":      "incubation | active | mature | dormant | archived",

  "lineage": {
    "seed_session": "Nazwa sesji która urodziła moduł",
    "parent_sid":   "uuid poprzedniej sesji | ''",
    "contract_sha": "sha-256 operatora | ''",
    "contributors": [
      {"actor": "Denis",             "role": "operator",  "chat_id": ""},
      {"actor": "Claude Sonnet 4.6", "role": "architect", "chat_id": "uuid | ''"}
    ],
    "signature": {"actor": "", "sha256": ""}
  },

  "files": {
    "entry":          "index.html",
    "docs":           "readme.html | ''",
    "components":     [{"path": "sub.html", "role": "visualization"}],
    "bootstrap":      "<id>-boot.md",
    "bootstrap_sha":  "<hex64>",
    "entry_sha":      "<hex64>",
    "docs_sha":       "<hex64>"
  },

  "runtime": {
    "data_path":      ".data/<id>/",
    "io":             ["read", "write"],
    "port":           8001,
    "consumers":      ["human", "ai"],
    "operator_state": "focused | tired | flow | chaotic | ''",
    "i18n":           {"default": "pl", "available": [], "lang_file": ""}
  },

  "relations": [
    {"type": "requires",    "target": "aiwpass"},
    {"type": "feeds",       "target": "horizon"},
    {"type": "complements", "target": "memory"}
  ],
  "tags": ["przykład", "backend", "websocket"]
}
```

### Konwencje manifest.json

- **Puste wartości**: `""`, `[]`, `{"path": "", "port": 0}` — nigdy `null`
- **`files.backend`** pusty: `{"path": "", "port": 0}`
- **`files.bootstrap`** pusty: `""`
- **`runtime.port`**: `0` = tryb demo (mocki), `>0` = produkcja (FastAPI)
- **Meta-moduły** (prefiks `_`): `_schema`, `_protocol`, `_pass`, `_boot`, `_quick`
- **`files.bootstrap`**: plik `.md` z esencją wiedzy dla AI. Konwencja nazwy: `<id>-boot.md`
- **`files.entry_sha`**: SHA-256 (hex64) pliku `entry` (HTML artefaktu). Pusty string `""` gdy plik nie istnieje na dysku.
- **`files.bootstrap_sha`**: SHA-256 (hex64) pliku `bootstrap` (*-boot.md). Pusty string `""` gdy moduł nie ma boot'a.
- **`files.docs_sha`**: SHA-256 (hex64) pliku `docs` (dokumentacja: readme.html, *-api-spec.md itp.). Pusty string `""` gdy brak docs lub plik nie istnieje.

Wszystkie trzy SHA aktualizowane przy każdej zmianie wersji. Weryfikowane przez `tools/check_integrity.py` i kartę **Artefakty** w AiWVerify.

### Alokacja portów · moduły Aktu I

| ID         | Status      | Port  | Opis                                      |
|------------|-------------|-------|-------------------------------------------|
| arena      | active      | 8001  | multi-model arena · zderzanie tez         |
| caves      | active      | 8002  | jaskinie warstw · transformery i zejścia  |
| morph      | active      | 8003  | pole morficzne · stany modelu             |
| horizon    | active      | 8004  | weryfikacja prawdy · ważony konsensus     |
| breath     | incubation  | 8005  | tchnienie · canvas 3D                  |
| forge      | incubation  | —     | kuźnia paradoksów · pre-consensus arena   |
| genesis    | incubation  | —     | archiwum sesji · czytnik eksportów        |
| profile    | incubation  | —     | profil operatora · radar 9 osi            |
| stamps     | incubation  | —     | rejestr pieczątek modeli                  |
| compas     | mature      | —     | kompas morficzny · geometria Three.js     |
| memory     | mature      | —     | sieć pamięci · lemniskata 3D              |
| labyrinth  | mature      | —     | labirynt pojęć · gra narracyjna 6 warstw  |
| następny   | —           | 8006+ | —                                         |

---

## Protokół połączeń — Frontend

### Zasada offline-first

Ten sam plik HTML działa: przez `file://` (bez serwera), przez `http://localhost:PORT` (z backendem), wysłany jako plik.

```javascript
const MODULE_ID = 'breath';
const API       = location.protocol === 'file:' ? null : `${location.origin}/api`;
const WS_URL    = API ? `ws://${location.host}/ws/${MODULE_ID}` : null;
```

- `API === null` → tryb offline, mocki i localStorage
- `API !== null` → tryb serwerowy, pełna funkcjonalność

### Wskaźnik LIVE / MOCK

```html
<span id="live-dot">mock</span>
```

```javascript
function setLive(isLive) {
  const el = document.getElementById('live-dot');
  el.textContent = isLive ? 'live' : 'mock';
  el.style.color = isLive ? 'var(--green)' : 'var(--text-d)';
}
```

Nigdy nie pokazuj błędu połączenia użytkownikowi — tylko `live`/`mock`.

### REST Polling (MVP)

```javascript
async function fetchState() {
  if (!API) { applyState(getMock()); return; }
  try {
    const r = await fetch(`${API}/${MODULE_ID}/state`);
    if (!r.ok) throw new Error();
    applyState(await r.json()); setLive(true);
  } catch { setLive(false); applyState(getMock()); }
}

fetchState();
setInterval(fetchState, 4000);   // state: puls 4s
setInterval(fetchLog,  12000);   // log:   puls 12s
```

### WebSocket — AiWConnector

```javascript
class AiWConnector {
  constructor(moduleId, wsUrl) {
    this.id = moduleId; this.url = wsUrl;
    this.ws = null; this.delay = 1000; this.dead = false;
  }
  connect() {
    if (!this.url || this.dead) { setLive(false); return; }
    this.ws = new WebSocket(this.url);
    this.ws.onopen  = () => { setLive(true);  this.delay = 1000; };
    this.ws.onclose = () => {
      setLive(false); applyState(getMock());
      setTimeout(() => this.connect(), this.delay);
      this.delay = Math.min(this.delay * 2, 30000);  // exp backoff, max 30s
    };
    this.ws.onerror  = () => {};  // silent
    this.ws.onmessage = (e) => this.route(JSON.parse(e.data));
  }
  route(data) {
    if (data.type === 'BROADCAST_SIGNAL') updateTelemetry(data.telemetry);
    if (data.type === 'STATE_UPDATE' && data.target === this.id) applyState(data.payload);
    if (data.type === 'TASK_READY') handleTaskResult(data);
  }
  send(action, params = {}) {
    if (this.ws?.readyState === WebSocket.OPEN)
      this.ws.send(JSON.stringify({ type: 'ACTION', action, params }));
  }
  destroy() { this.dead = true; this.ws?.close(); }
}

const connector = new AiWConnector(MODULE_ID, WS_URL);
connector.connect();
// gdy WS zastępuje polling: clearInterval(_stateTimer); clearInterval(_logTimer);
```

---

## Typy komunikatów WebSocket

### BROADCAST_SIGNAL — Rdzeń → wszyscy

Puls systemu, co ~1s, do wszystkich podłączonych artefaktów.

```json
{
  "type": "BROADCAST_SIGNAL",
  "telemetry": {"cpu": 42.5, "mem": 61.2, "temp": 58.5}
}
```

### STATE_UPDATE — Rdzeń → konkretny artefakt

```json
{
  "type":    "STATE_UPDATE",
  "target":  "breath",
  "payload": {"activity_key": "mysli", "started_at": 1745257200000, "duration_ms": 9500, "metrics": {}}
}
```

Artefakt ignoruje jeśli `target !== MODULE_ID`.

### TASK_READY — Rdzeń → artefakt · wynik zadania

```json
{"type": "TASK_READY", "task_id": "gen-42", "result": {}}
```

### ACTION — artefakt → Rdzeń (WS only)

```json
{"type": "ACTION", "action": "set_state", "params": {"activity_key": "spi"}}
```

Dla prostych operacji preferuj REST POST. ACTION dla poleceń wymagających szybkiej odpowiedzi.

---

## Protokół połączeń — Backend (FastAPI)

### Dwie topologie — identyczny kod

**Topologia A — dedykowany port per moduł** (domyślna konwencja):
- Jeden silnik na własnym porcie (8001–8006+)
- `cd engines/<id> && uv run uvicorn <id>.main:app --port PORT --reload`

**Topologia B — wspólny port dla wielu artefaktów**:
- Jeden silnik na wspólnym porcie (np. 8000)
- Artefakty rozróżniane po `artifact_id` / `module_id` w URL
- `cd engines/hub && uv run uvicorn hub.main:app --port 8000 --reload`

### ConnectionManager

```python
class ConnectionManager:
    def __init__(self): self.active: dict[str, WebSocket] = {}

    async def connect(self, aid: str, ws: WebSocket):
        await ws.accept(); self.active[aid] = ws

    def disconnect(self, aid: str): self.active.pop(aid, None)

    async def broadcast(self, data: dict):
        dead = []
        for aid, ws in self.active.items():
            try: await ws.send_json(data)
            except: dead.append(aid)
        for aid in dead: self.disconnect(aid)

    async def send_to(self, aid: str, data: dict):
        if ws := self.active.get(aid):
            try: await ws.send_json(data)
            except: self.disconnect(aid)
```

Topologia A: rejestr ma zawsze 1 wpis. Topologia B: N wpisów, jeden per artefakt.

### REST endpoints

```python
@app.get("/api/{module_id}/state")
async def get_state(module_id: str): ...

@app.get("/api/{module_id}/log")
async def get_log(module_id: str, limit: int = 40): ...
```

### WebSocket endpoints

```python
@app.websocket("/ws/broadcast")          # keepalive, BROADCAST_SIGNAL
@app.websocket("/ws/{artifact_id}")      # dwukierunkowy kanał artefaktu
```

```python
@app.websocket("/ws/{artifact_id}")
async def ws_protocol(ws: WebSocket, artifact_id: str):
    await manager.connect(artifact_id, ws)
    try:
        while True:
            data = await ws.receive_json()
            if data.get("type") == "ACTION":
                await handle_action(artifact_id, data, manager)
    except WebSocketDisconnect: manager.disconnect(artifact_id)
```

### Telemetria — pętla przy starcie

```python
async def telemetry_loop():
    while True:
        await manager.broadcast({
            "type": "BROADCAST_SIGNAL",
            "telemetry": {"cpu": psutil.cpu_percent(), "mem": psutil.virtual_memory().percent}
        })
        await asyncio.sleep(1)

@asynccontextmanager
async def lifespan(app: FastAPI):
    asyncio.create_task(telemetry_loop())
    yield

app = FastAPI(lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
```

### Struktura katalogu silnika

```
engines/<id>/
├── <id>/
│   ├── __init__.py
│   ├── main.py      ← FastAPI app + endpointy
│   └── engine.py    ← logika biznesowa (opcjonalnie)
└── pyproject.toml
.data/<id>/          ← bazy danych (POZA engines/)
.logs/<id>/          ← logi (POZA engines/)
```

Silnik odczytuje dane ze ścieżki `../../.data/<id>/` — nigdy nie trzyma danych w `engines/`.

---

## Zasady skrótowe

- `bootstrap` = plik `.md` z wiedzą dla AI; HTML = dla przeglądarki
- `port: 0` = demo/offline; `port > 0` = produkcja
- Silent fail wszędzie — użytkownik nigdy nie widzi błędu połączenia
- `getMock()` zawsze zdefiniowane — animacja działa bez backendu
- CORS `allow_origins=["*"]` na dev, zaostrzyć w produkcji
- Dane poza kodem — zasada lustrzana: `apps/` ↔ `engines/` ↔ `.data/` ↔ `.logs/`

---

## Changelog

### v1.0 · 2026-05-02
- Pierwsza wersja MD — wyekstrahowana z AiWProtocol.html v1.0

### v1.1 · 2026-05-09
- `data/` → `.data/` w schemacie manifest.json
- Dodano pole `bootstrap_sha` do sekcji `files`
- Tabela portów rozszerzona do kanonicznej tabeli modułów Aktu I (ID, status, port, opis)
- `soul` → `morph`, `tchnienie` → `breath`, usunięto `growup`
- Aktualizacja `MODULE_ID` w przykładach
