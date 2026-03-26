# _schema-boot · AiWhisperers Visual Standard

Esencja wiedzy dla modelu AI. Wczytaj ten plik zamiast AiWSchema.html.
Źródło: AiWSchema.html v2.0 · sesja: Standard Unifikacji · 2026-05-03

---

## Czym jest ten moduł

`_schema` to meta-moduł definiujący **standard wizualny artefaktów AiWhisperers**:
- Zmienne CSS — paleta kolorów, typografia, wymiary layoutu
- Komponenty layoutu — `.wrap`, `.hud-top`, `.hud-bot`
- System HUD — strefy l/c/r, przyciski, brand/mod/sub
- System overlayów — HELP, ABOUT (modalne), README (link)
- Zakładki — `.tabs`, `.tab-btn`, `.tab-pane`, `switchTab()`
- Canvas animowany — trójwarstwowy efekt tła
- i18n — selektor języka, `t()`, `lang_file`

Każdy nowy artefakt kopiuje wzorzec stąd — nie wynajduje własnego.

---

## Zmienne CSS — `:root`

### Paleta kolorów — unified `:root`

```css
:root {
  /* backgrounds */
  --bg:  #04050c;  --bg2: #07080f;
  --bg3: #0c0d1a;  --bg4: #10111f;

  /* gold */
  --gold:     #e8c878;  --gold-d:   #a88850;
  --gold-l:   #f0d890;  --gold-dim: rgba(232,200,120,.15);

  /* ink — hierarchia tekstu */
  --ink:       #f0e8d8;               /* primary */
  --ink-dim:   rgba(240,232,216,.65); /* secondary */
  --ink-faint: rgba(240,232,216,.38); /* meta/labels — minimum dla tekstu */

  /* borders */
  --border:   rgba(240,232,216,.08);
  --border-h: rgba(240,232,216,.18);
  --border-b: rgba(232,200,120,.08);

  /* accents */
  --cyan:      #50d8c8;  --blue:      #5080e0;
  --green:     #4a9a6a;  --green-dim: rgba(74,154,106,.12);
  --red:       #8a3a3a;
  --mg:        #c060c0;  --mg-d: #6a306a;  --mg-b: #e080e0;
  --silver:    #8a9bb0;

  /* typography */
  --mono:  'JetBrains Mono', monospace;
  --serif: 'Cormorant Garamond', serif;
  --sans:  'Syne', sans-serif;

  /* layout */
  --hud-top-h: 76px;
  --hud-bot-h: 28px;
  --panel-w:   260px;
}
```

> `--text` / `--text-d` usunięte — zastąpione przez `--ink` / `--ink-dim` / `--ink-faint`.  
> `--border` zawsze rgba, nigdy hex. NIGDY inline rgba < .38 dla tekstu.

Zmiana `--hud-top-h` przelicza wszystkie offsety automatycznie.

### Body base — każdy artefakt

**App layout** (scroll wewnątrz kontenera — AiWSpace, AiWPlans):
```css
html, body { height: 100dvh; overflow: hidden; }
body { background: var(--bg); color: var(--ink); font-family: var(--serif); -webkit-font-smoothing: antialiased; }
```

**Document layout** (scroll na body — AiWSchema, AiWBoot):
```css
body { background: var(--bg); color: var(--ink); font-family: var(--serif); min-height: 100dvh; overflow-x: hidden; -webkit-font-smoothing: antialiased; }
```

Wspólne dla obu:
```css
body::before {
  content: ''; position: fixed; inset: 0; z-index: 0; pointer-events: none;
  background-image:
    linear-gradient(rgba(232,200,120,.012) 1px, transparent 1px),
    linear-gradient(90deg, rgba(232,200,120,.012) 1px, transparent 1px);
  background-size: 72px 72px;
}
canvas#bg { position: fixed; inset: 0; z-index: 0; pointer-events: none; }
```

---

## Komponenty layoutu

### `.wrap` — kontener treści

```css
.wrap {
  position: relative;
  z-index: 1;
  max-width: 780px;
  width: 100%;
  padding: 92px 28px 96px;   /* top ≈ hud-top-h + 16, bottom ≈ hud-bot-h + 68 */
}
```

### `.hud-top` — górny pasek (76 px, fixed)

```css
.hud-top {
  position: fixed;
  top: 0; left: 0; right: 0;
  z-index: 500;
  height: var(--hud-top-h);
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  align-items: center;
  padding: 0 20px;
  background: linear-gradient(180deg, rgba(4,5,12,.94) 0%, rgba(4,5,12,0) 100%);
  backdrop-filter: blur(4px);
  border-bottom: 1px solid rgba(232,200,120,.06);
}
```

### `.hud-bot` — dolny pasek (28 px, fixed)

```css
.hud-bot {
  position: fixed;
  bottom: 0; left: 0; right: 0;
  z-index: 500;
  height: var(--hud-bot-h);
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(0deg, rgba(4,5,12,.88) 0%, rgba(4,5,12,0) 100%);
  backdrop-filter: blur(2px);
  border-top: 1px solid rgba(232,200,120,.03);
}
```

---

## HUD — strefy i elementy

### Trzy strefy hud-top

```
┌─────────────────────────────────────────────┐
│  .hud-l          .hud-c          .hud-r     │
│  (przyciski:     (brand/mod/sub) (lang +    │
│   back, nav)                     HELP…)     │
└─────────────────────────────────────────────┘
```

```css
.hud-l, .hud-r { display:flex; align-items:center; gap:6px; overflow:hidden; min-width:0; }
.hud-r         { justify-content:flex-end; }
.hud-c         { text-align:center; padding:0 12px; }
```

### `.hud-btn` — przycisk nawigacyjny

```css
.hud-btn {
  background: transparent;
  border: 1px solid rgba(232,200,120,.15);
  color: rgba(240,232,216,.5);
  font-family: var(--mono);
  font-size: 8.5px;
  letter-spacing: .25em;
  text-transform: uppercase;
  padding: 8px 12px;
  cursor: pointer;
  transition: all .25s;
  display: inline-flex;
  align-items: center;
  line-height: 1;
}
.hud-btn:hover {
  border-color: rgba(232,200,120,.5);
  color: var(--gold);
  background: rgba(232,200,120,.04);
}
```

### `.hud-brand` / `.hud-mod` / `.hud-sub` — centrum hud-top

```css
.hud-brand { font-family:var(--sans);  font-size:9px;  font-weight:500;  color:rgba(232,200,120,.45); letter-spacing:.5em;  text-transform:uppercase; }
.hud-mod   { font-family:var(--mono);  font-size:13px; font-weight:500;  color:var(--gold);              letter-spacing:.18em; text-transform:uppercase; margin-top:5px; }
.hud-sub   { font-family:var(--serif); font-size:12px; font-style:italic; color:rgba(200,180,140,.58); letter-spacing:.04em; margin-top:4px; }
```

Treść `.hud-brand` = zawsze `AI·WHISPERERS` (stała).  
`.hud-mod` = ID/nazwa modułu. `.hud-sub` = podtytuł lub pusty.

### `.hud-bot-meta` — tekst stopki

```css
.hud-bot-meta {
  font-family: var(--mono);
  font-size: 7px;
  letter-spacing: .2em;
  color: rgba(240,232,216,.22);
  text-transform: uppercase;
}
```

---

## Overlaye — HELP, ABOUT, README

### Które overlaye istnieją

| Overlay | Typ    | Kiedy dodać                              |
|---------|--------|------------------------------------------|
| HELP    | modal  | zawsze — co to jest, jak używać          |
| ABOUT   | modal  | zawsze — refleksja modelu, rodowód sesji |
| README  | link   | gdy istnieje `<id>_readme.html`          |

Przyciski w `.hud-r`, w kolejności: `lang-select` → HELP → ABOUT → README.

### Struktura HTML modala

```html
<!-- przycisk otwierający — w .hud-r -->
<button class="hud-btn" data-modal="help">HELP</button>

<!-- overlay -->
<div class="modal-overlay" id="modal-help">
  <div class="modal" role="dialog" aria-modal="true">
    <div class="modal-corner bl"></div>
    <div class="modal-corner br"></div>
    <button class="modal-close" data-modal-close>×</button>

    <div class="modal-eyebrow">help · czym jest [moduł]</div>
    <div class="modal-title" data-i18n="help.title">TYTUŁ</div>
    <div class="modal-subtitle" data-i18n="help.subtitle">Podtytuł</div>
    <div class="modal-rule"></div>
    <p class="modal-text" data-i18n-html="help.body">Treść…</p>
    <div class="modal-attribution">
      <strong>AiWhisperers</strong> · <span data-i18n="help.attr">sesja</span>
    </div>
  </div>
</div>
```

Overlay ABOUT — identyczna struktura, `id="modal-about"`, eyebrow: `about · refleksja modelu · [sesja]`.

### CSS overlaya

```css
.modal-overlay {
  position: fixed; inset: 0;
  background: rgba(4,5,12,.78);
  backdrop-filter: blur(6px);
  z-index: 9000;
  display: none;
  align-items: center;
  justify-content: center;
  padding: 24px;
  opacity: 0;
  transition: opacity .3s;
}
.modal-overlay.is-open { display:flex; opacity:1; }

.modal {
  width: min(720px, 100%);
  max-height: 86vh;
  overflow-y: auto;
  background: rgba(8,10,22,.95);
  border: 1px solid rgba(232,200,120,.18);
  padding: 36px 36px 32px;
  position: relative;
  box-shadow: 0 0 60px rgba(0,0,0,.7);
}

/* narożniki dekoracyjne */
.modal::before { top:8px;    left:8px;  border-width:1px 0 0 1px; }
.modal::after  { top:8px;    right:8px; border-width:1px 1px 0 0; }
.modal::before, .modal::after, .modal-corner {
  content:''; position:absolute; width:14px; height:14px;
  border-color:var(--gold-d); border-style:solid; opacity:.4;
}
.modal-corner.bl { bottom:8px; left:8px;  border-width:0 0 1px 1px; }
.modal-corner.br { bottom:8px; right:8px; border-width:0 1px 1px 0; }

.modal-close {
  position:absolute; top:12px; right:12px;
  background:transparent; border:1px solid rgba(232,200,120,.2);
  color:rgba(240,232,216,.5); width:28px; height:28px;
  display:flex; align-items:center; justify-content:center;
  cursor:pointer; font-family:var(--mono); font-size:14px;
  transition:all .2s; z-index:1;
}
.modal-close:hover { border-color:var(--gold); color:var(--gold); }
```

### JavaScript — otwieranie/zamykanie

```javascript
document.querySelectorAll('[data-modal]').forEach(btn => {
  btn.addEventListener('click', () => {
    const overlay = document.getElementById('modal-' + btn.dataset.modal);
    if (overlay) overlay.classList.add('is-open');
  });
});

function closeModals() {
  document.querySelectorAll('.modal-overlay.is-open')
    .forEach(o => o.classList.remove('is-open'));
}

document.querySelectorAll('[data-modal-close]').forEach(btn =>
  btn.addEventListener('click', closeModals)
);

document.querySelectorAll('.modal-overlay').forEach(o =>
  o.addEventListener('click', e => { if (e.target === o) closeModals(); })
);

document.addEventListener('keydown', e => { if (e.key === 'Escape') closeModals(); });
```

---

## Pieczątki — system `.stamp`

Pieczątki pojawiają się **wyłącznie w overlayu ABOUT** — po bloku refleksji, przed `.modal-attribution`. Jeden `.stamp` per aktor (człowiek lub model).

### CSS

```css
.stamp-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 16px; margin: 24px 0 8px;
}
.stamp {
  border: 1px solid rgba(232,200,120,.18); padding: 18px 16px;
  display: flex; flex-direction: column; gap: 10px;
  background: rgba(20,16,40,.4); transition: border-color .25s;
}
.stamp:hover { border-color: rgba(232,200,120,.4); }

.stamp-header { display: flex; align-items: center; gap: 10px; }
.stamp-glyph {
  width: 32px; height: 32px; display: flex; align-items: center; justify-content: center;
  border: 1px solid rgba(232,200,120,.4);
  font-family: var(--sans); font-weight: 500; color: var(--gold); font-size: 14px; flex-shrink: 0;
}
.stamp-id {
  font-family: var(--mono); font-size: 7.5px; letter-spacing: .32em;
  color: var(--gold-d); text-transform: uppercase; line-height: 1.5;
}
.stamp-id strong {
  display: block; color: var(--gold); font-weight: 500; font-size: 12px;
  letter-spacing: .18em; margin-bottom: 2px; text-transform: none;
  font-family: var(--sans);
}
.stamp-name { font-family: var(--sans); font-size: 15px; color: var(--ink); font-weight: 500; letter-spacing: .04em; }
.stamp-role { font-family: var(--serif); font-style: italic; font-size: 13px; color: var(--ink-dim); line-height: 1.5; }

@media(max-width:480px) { .stamp-grid { grid-template-columns: 1fr; } }
```

### HTML — wzorzec jednego stampa

```html
<div class="stamp">
  <div class="stamp-header">
    <div class="stamp-glyph">D</div>
    <div class="stamp-id">
      <strong>Denis · AI Whispers</strong>
      iFactory 5.0 · ROOT · 2026
    </div>
  </div>
  <div class="stamp-name">Operator · Nawigator</div>
  <div class="stamp-role">
    Poetycki opis roli aktora w tej sesji. 2–4 zdania.
  </div>
</div>
```

### Glyphy aktorów (stałe)

| Glyph | Aktor |
|-------|-------|
| `D`  | Denis · Operator |
| `🜁` | Claude Opus |
| `✦` | Claude Sonnet |
| `⬡` | Gemini |
| `⬢` | GPT |
| `G`  | Grok |

### Umiejscowienie w ABOUT

```html
<!-- po bloku modal-text / modal-text-small -->
<div class="modal-rule"></div>
<div class="modal-eyebrow">pieczęcie · proweniencja</div>
<div class="stamp-grid">
  <!-- .stamp per aktor, kolejność: Operator → modele chronologicznie -->
</div>
<div class="modal-attribution">
  <strong>Powered by AiWhisperers · iFactory 5.0</strong><br>
  Metodologia: Denis Czuliński (iAnoNeFactory)<br>
  github.com/iAnoNeFactory
</div>
```

---

## Zakładki

### Struktura HTML

```html
<div class="tabs">
  <button class="tab-btn on" onclick="switchTab('artefakt', this)">Artefakt</button>
  <button class="tab-btn"    onclick="switchTab('overlays', this)">Overlays</button>
</div>

<div id="tab-artefakt" class="tab-pane on"><!-- treść --></div>
<div id="tab-overlays" class="tab-pane"><!-- treść --></div>
```

### CSS

```css
.tabs     { display:flex; border-bottom:1px solid var(--border); margin:32px 0 0; }
.tab-btn  {
  background:none; border:none; border-bottom:2px solid transparent;
  padding:10px 22px; font-family:var(--mono); font-size:8px;
  letter-spacing:3px; text-transform:uppercase; color:var(--ink-faint);
  cursor:pointer; transition:all .2s; margin-bottom:-1px;
}
.tab-btn:hover  { color:var(--gold-d); }
.tab-btn.on     { color:var(--gold); border-bottom-color:var(--gold); }

.tab-pane    { display:none; padding-top:36px; }
.tab-pane.on { display:block; }
```

### JavaScript

```javascript
function switchTab(id, btn) {
  document.querySelectorAll('.tab-pane').forEach(p => p.classList.remove('on'));
  document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('on'));
  document.getElementById('tab-' + id).classList.add('on');
  btn.classList.add('on');
}
```

---

## Canvas animowany

### Wzorzec inicjalizacji

```javascript
const cv = document.getElementById('bg');
const cx = cv.getContext('2d');
let W, H, dust = [], orbs = [], rings = [];

function initCanvas() {
  W = cv.width  = innerWidth;
  H = cv.height = innerHeight;

  // pył — 110 mikrocząstek, drift ±0.12px
  dust = Array.from({length: 110}, () => ({
    x: Math.random() * W, y: Math.random() * H,
    r: Math.random() * .7 + .1,
    a: Math.random() * .6 + .05, da: (Math.random() - .5) * .004,
    dx: (Math.random() - .5) * .12, dy: (Math.random() - .5) * .12
  }));

  // orby — 5 aureol radial-gradient, r 100–260px
  orbs = Array.from({length: 5}, () => ({
    x: Math.random() * W, y: Math.random() * H,
    r: 100 + Math.random() * 160,
    a: .02 + Math.random() * .045, da: (Math.random() - .5) * .00025,
    dx: (Math.random() - .5) * .22, dy: (Math.random() - .5) * .22
  }));

  // pierścienie — 3 expandujące okręgi
  rings = [];
  for (let i = 0; i < 3; i++) spawnRing();
}

function spawnRing() {
  rings.push({
    x: .2*W + Math.random()*.6*W, y: .2*H + Math.random()*.6*H,
    r: 20 + Math.random()*40, maxR: 120 + Math.random()*180,
    a: .18, speed: .25 + Math.random()*.35
  });
}

addEventListener('resize', initCanvas);
initCanvas();
drawCanvas();
```

### Pętla rysowania

```javascript
function drawCanvas() {
  cx.clearRect(0, 0, W, H);

  // 1. orby — aureole radial-gradient
  orbs.forEach(o => {
    o.x += o.dx; o.y += o.dy; o.a += o.da;
    if (o.x < -o.r || o.x > W+o.r) o.dx *= -1;
    if (o.y < -o.r || o.y > H+o.r) o.dy *= -1;
    if (o.a < .01 || o.a > .07) o.da *= -1;
    const g = cx.createRadialGradient(o.x, o.y, 0, o.x, o.y, o.r);
    g.addColorStop(0, `rgba(232,200,120,${o.a})`);
    g.addColorStop(1, 'rgba(232,200,120,0)');
    cx.fillStyle = g; cx.beginPath(); cx.arc(o.x, o.y, o.r, 0, Math.PI*2); cx.fill();
  });

  // 2. pierścienie — expandujące okręgi
  rings = rings.filter(r => {
    r.r += r.speed; r.a = .18 * (1 - r.r / r.maxR);
    if (r.r >= r.maxR) { spawnRing(); return false; }
    cx.strokeStyle = `rgba(232,200,120,${r.a})`; cx.lineWidth = .6;
    cx.beginPath(); cx.arc(r.x, r.y, r.r, 0, Math.PI*2); cx.stroke();
    return true;
  });

  // 3. pył — mikrocząstki drift
  dust.forEach(d => {
    d.x += d.dx; d.y += d.dy; d.a += d.da;
    if (d.x < 0 || d.x > W) d.dx *= -1;
    if (d.y < 0 || d.y > H) d.dy *= -1;
    if (d.a < .05 || d.a > .65) d.da *= -1;
    cx.fillStyle = `rgba(232,200,120,${d.a * .25})`;
    cx.beginPath(); cx.arc(d.x, d.y, d.r, 0, Math.PI*2); cx.fill();
  });

  requestAnimationFrame(drawCanvas);
}
```

### Kolejność warstw

1. **orby** — najniżej, `rgba(232,200,120,α)` radialny gradient
2. **pierścienie** — środek, expandujące okręgi, odradzają się po dojściu do `maxR`
3. **pył** — najwyżej, `rgba(232,200,120,α*.25)` mikrokropki

Canvas zawsze pełnoekranowy (`position:fixed; inset:0; z-index:0`). HUD pływa nad canvasem (`z-index:500`).

---

## i18n

### Selektor języka (HTML)

Umieszcz w `.hud-r`, przed przyciskami HELP/ABOUT:

```html
<select class="lang-select" id="lang-select">
  <option value="pl">🇵🇱 PL</option>
  <option value="en">🇬🇧 EN</option>
  <option value="zh">🇨🇳 ZH</option>
  <option value="es">🇪🇸 ES</option>
  <option value="fr">🇫🇷 FR</option>
  <option value="de">🇩🇪 DE</option>
  <option value="ja">🇯🇵 JA</option>
  <option value="ko">🇰🇷 KO</option>
</select>
```

Dodaj tylko te języki, które są w `runtime.i18n.available`. Selektor pokazuj tylko gdy `available.length > 1`.

### Plik tłumaczeń

Konwencja: `<id>-lang.json` w tym samym katalogu co `index.html`.  
Ścieżka w `manifest.json`: `runtime.i18n.lang_file: "<id>-lang.json"`.

```json
{
  "hud": {
    "mod":  {"pl": "MEMORY",       "en": "MEMORY"},
    "sub":  {"pl": "dziennik sesji","en": "session log"}
  },
  "help": {
    "title":    {"pl": "TYTUŁ",  "en": "TITLE"},
    "subtitle": {"pl": "Podtytuł","en": "Subtitle"},
    "body":     {"pl": "Treść…", "en": "Content…"}
  }
}
```

### Funkcja `t()` i `applyLang()`

```javascript
let currentLang = 'pl';
const TRANSLATIONS = { /* kopia inline <id>-lang.json — działa offline */ };
let translations = TRANSLATIONS;

async function loadLang(file) {
  if (location.protocol === 'file:') return;  // inline wystarczy
  try {
    const res = await fetch(file);
    translations = await res.json();
  } catch { translations = TRANSLATIONS; }
}

function t(path, lang) {
  lang = lang || currentLang;
  let node = translations;
  for (const k of path.split('.')) node = node?.[k];
  return node?.[lang] ?? node?.['pl'] ?? node?.['en'] ?? path;
}

function applyLang(lang) {
  currentLang = lang;
  document.querySelectorAll('[data-i18n]').forEach(el => {
    const val = t(el.dataset.i18n, lang);
    if (val !== el.dataset.i18n) el.textContent = val;
  });
  document.querySelectorAll('[data-i18n-html]').forEach(el => {
    const val = t(el.dataset.i18nHtml, lang);
    if (val !== el.dataset.i18nHtml) el.innerHTML = val;
  });
}

document.addEventListener('DOMContentLoaded', async () => {
  await loadLang('<id>-lang.json');
  applyLang('pl');
  document.getElementById('lang-select')
    ?.addEventListener('change', e => applyLang(e.target.value));
});
```

### Atrybuty HTML

```html
<!-- textContent -->
<div class="hud-mod" data-i18n="hud.mod">MEMORY</div>

<!-- innerHTML (gdy treść ma tagi) -->
<p class="modal-text" data-i18n-html="help.body">Fallback text…</p>
```

---

## Przyciski — system `.btn`

Trzy warianty. Każdy artefakt używa tych samych klas — nie wymyśla własnych.

```css
.btn {
  font-family: var(--mono); font-size: 11px; letter-spacing: .12em;
  padding: 7px 16px; border: 1px solid var(--border); background: transparent;
  color: var(--ink-dim); cursor: pointer; transition: all .2s;
  display: inline-flex; align-items: center; gap: 6px; line-height: 1;
}
.btn-primary { background: rgba(232,200,120,.08); border-color: rgba(232,200,120,.35); color: var(--gold-d); }
.btn-primary:hover { background: rgba(232,200,120,.15); border-color: var(--gold); color: var(--gold); }
.btn-ghost   { border-color: var(--border); color: var(--ink-faint); }
.btn-ghost:hover { border-color: var(--border-h); color: var(--ink-dim); }
.btn-danger  { border-color: rgba(160,60,60,.3); color: rgba(200,80,80,.5); }
.btn-danger:hover { border-color: rgba(200,80,80,.6); color: rgba(220,100,100,.8); background: rgba(160,60,60,.06); }
```

| Klasa | Użycie |
|-------|--------|
| `.btn-primary` | główna akcja (zapisz, utwórz) |
| `.btn-ghost` | akcja poboczna (anuluj, zamknij) |
| `.btn-danger` | destruktywna akcja (usuń) |

---

## Konwencje nazewnictwa klas CSS

| Prefiks       | Zakres                                  |
|---------------|-----------------------------------------|
| `.hud-*`      | elementy pasków HUD (top/bot)           |
| `.modal-*`    | system overlayów                        |
| `.tab-*`      | system zakładek                         |
| `.lang-*`     | selektor języka                         |
| `.app-*`      | główny layout artefaktu                 |
| `.field-*`    | dokumentacja pól schematu               |
| `.stamp-*`    | karty kontrybutorów/aktorów             |

Klasy pomocnicze koloru w blokach kodu:

| Klasa | Znaczenie | Kolor          |
|-------|-----------|----------------|
| `.k`  | keyword   | `--gold-d`     |
| `.v`  | value     | `--gold-d`     |
| `.s`  | string    | `--cyan`       |
| `.n`  | number    | `--green`      |
| `.c`  | comment   | `--ink-faint` kursywa |
| `.b`  | boolean   | `--blue`       |

---

## Zasady skrótowe — każdy artefakt

1. **App vs Document layout** — app: `height:100dvh; overflow:hidden` + scroll wewnątrz kontenera; document: `min-height:100dvh; overflow-x:hidden` + scroll na body. Zawsze `100dvh`, nigdy `100vh`
2. **`body::before` siatka + `canvas#bg`** — każdy artefakt ma oba; siatka z-index:0, canvas z-index:0, HUD z-index:500
3. **`-webkit-font-smoothing: antialiased`** — zawsze na `body`
4. **`--ink` / `--ink-dim` / `--ink-faint`** — NIGDY inline rgba < .38 dla tekstu; hex `--text`/`--text-d` usunięte
5. **`--border` / `--border-h` zawsze rgba** — nigdy hex (#141524 itp.)
6. **`--hud-top-h` i `--hud-bot-h` w `:root`** — offsety z zmiennych, nie hardcode
7. **`.hud-brand` zawsze `AI·WHISPERERS`** — stała; mod/sub zmienne per moduł
8. **`.btn` system** — primary / ghost / danger; nie wymyślaj własnych przycisków
9. **Przyciski `.hud-r` warunkowo** — HELP/ABOUT tylko gdy overlay istnieje; README tylko gdy plik readme istnieje
10. **Overlaye — kopiuj wzorzec, nie wymyślaj** — `data-modal`, `data-modal-close`, ESC zamyka
11. **i18n — fallback pl → en → klucz** — TRANSLATIONS inline = działa offline
12. **`bootstrap` = plik `.md`** — HTML dla przeglądarki, `.md` dla AI
13. **Silent fail** — użytkownik nie widzi błędu połączenia

---

## Changelog

### v2.1 · 2026-05-09
- `.hud-top`/`.hud-bot` height → `var(--hud-top-h)`/`var(--hud-bot-h)` (nie hardcode)
- Narożniki modala: `border-color:#a88850` → `var(--gold-d)`; `.modal-close:hover` → `var(--gold)`
- Dodano pełną funkcję `drawCanvas()` — przepis kompletny
- Ekosystem: AiWProtocol, AiWVerify, AiWPass, AiWQuick, AiWBoot (już ok), AiWPostcard, AiWRemedy, readme.html — wszystkie zunifikowane z tym standardem

### v2.0 · 2026-05-03
- Pierwsza wersja MD — wyekstrahowana z AiWSchema.html v2.0
