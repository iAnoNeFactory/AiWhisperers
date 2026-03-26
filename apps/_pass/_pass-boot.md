# _pass-boot · AiWPass + AiWVerify · Knowledge Bootstrap

Plik wiedzy dla modeli AI. Wczytaj zamiast przeglądania kodu HTML.
Źródło: `AiWPass.html` v4.1 · `AiWVerify.html` v2.0 · sesja maj 2026

---

## Czym jest ten moduł

`_pass` to para artefaktów stanowiących **kryptograficzną tożsamość operatora** w ekosystemie AiWhisperers:

| Plik | Rola |
|------|------|
| `AiWPass.html` | paszport operatora — tworzenie i zarządzanie tożsamością |
| `AiWVerify.html` | audytor — weryfikacja kontraktów, profili i łańcuchów · `apps/_verify/` |

Razem tworzą zamknięty system: Pass produkuje artefakty kryptograficzne, Verify je sprawdza — bez serwera, lokalnie w przeglądarce przez Web Crypto API.

---

## Filozofia

System oparty jest na **proweniencji, nie dostępie**. Kryptografia nie chroni tu przed nieautoryzowanym odczytem — zaświadcza, że konkretna osoba z konkretnym kluczem podjęła konkretną intencję w konkretnym momencie.

Trzy warstwy:
1. **Kontrakt** — pieczęć relacji operator–model. Co zostało powiedziane, kiedy, przez kogo.
2. **Profil** — tożsamość kryptograficzna operatora. Kto to jest, co go definiuje, kto go zna.
3. **Łańcuch** — drzewo zaufania. Kto certyfikował kogo; linia genealogiczna operatorów.

---

## Struktura AiWPass

### Karty główne

```
#main-tabs:
  · Kontrakt   → #view-kontrakt   (zapieczętuj, archiwum, eksport/import)
  · Profil     → #view-profil     (dane, klucze, certyfikacja, children)
```

### HUD i nawigacja

```
hud-l: ⟵ mapa         (link do ../../index.html)
hud-c: AI·WHISPERERS / Pass / paszport operatora · kontrakty
hud-r: VERIFY (→ AiWVerify.html) · HELP · ABOUT
```

Overlaye: `#help-overlay` (karta Kontrakt/Profil/Łańcuch) · `#about-overlay` (stemple) · `#overlay-pin` (PIN) · `#overlay-import-cert` · `#overlay-import-priv` · `#overlay-import-pub`

---

## Kryptografia — prymitywy

### Algorytm klucza

System używa wyłącznie **Ed25519** do generowania par kluczy. Stary format P-256 (ECDSA, prefiks `P256:`) jest obsługiwany przy imporcie i weryfikacji dla wstecznej kompatybilności — ale nie jest generowany.

```javascript
// Generowanie (AiWPass doGenerateKeys)
const kp = await crypto.subtle.generateKey({name: 'Ed25519'}, true, ['sign', 'verify']);
const pub  = btoa(String.fromCharCode(...new Uint8Array(await crypto.subtle.exportKey('raw',   kp.publicKey))));
const priv = btoa(String.fromCharCode(...new Uint8Array(await crypto.subtle.exportKey('pkcs8', kp.privateKey))));
```

- Klucz publiczny: format **raw**, base64, 32 bajty
- Klucz prywatny: format **pkcs8**, base64, ~48 bajtów

Klucz P-256 rozpoznawany po prefiksie `P256:` w zapisanej wartości.

### SHA-256

```javascript
// Hex (używany do SHA kontraktu, Profile SHA, PIN)
async function sha256hex(str) {
  const buf = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(str));
  return Array.from(new Uint8Array(buf)).map(b => b.toString(16).padStart(2,'0')).join('');
}

// Uint8Array (używany do payloadu podpisu certyfikatu)
async function sha256bytes(str) {
  const buf = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(str));
  return new Uint8Array(buf);
}
```

### Podpisywanie (sign)

```javascript
async function signBytes(hashBytes, privRaw) {
  const isP256 = privRaw.startsWith('P256:');
  const b64    = isP256 ? privRaw.slice(5) : privRaw;
  const privBytes = Uint8Array.from(atob(b64.replace(/\s/g,'')), c => c.charCodeAt(0));
  const alg    = isP256 ? {name:'ECDSA', namedCurve:'P-256'} : {name:'Ed25519'};
  const key    = await crypto.subtle.importKey('pkcs8', privBytes.buffer, alg, false, ['sign']);
  const sigAlg = isP256 ? {name:'ECDSA', hash:'SHA-256'} : {name:'Ed25519'};
  return btoa(String.fromCharCode(...new Uint8Array(await crypto.subtle.sign(sigAlg, key, hashBytes))));
}
```

### Weryfikacja (verify)

```javascript
async function verifyBytes(hashBytes, sigB64, pubB64) {
  const isP256 = pubB64.startsWith('P256:');
  const pubBytes = Uint8Array.from(atob((isP256 ? pubB64.slice(5) : pubB64).replace(/\s/g,'')), c => c.charCodeAt(0));
  const sigBytes = Uint8Array.from(atob(sigB64.replace(/\s/g,'')), c => c.charCodeAt(0));
  const alg    = isP256 ? {name:'ECDSA', namedCurve:'P-256'} : {name:'Ed25519'};
  const key    = await crypto.subtle.importKey('raw', pubBytes.buffer, alg, false, ['verify']);
  const verAlg = isP256 ? {name:'ECDSA', hash:'SHA-256'} : {name:'Ed25519'};
  return await crypto.subtle.verify(verAlg, key, sigBytes, hashBytes);
}
```

> **Uwaga krytyczna:** mapping function `c => c.charCodeAt(0)` musi być drugim argumentem `Uint8Array.from()`, nie `atob()`. Błąd nawiasowania daje tablicę samych zer i zawsze nieważny podpis.

---

## Kontrakty

### Idea

Kontrakt to kryptograficzna pieczęć momentu — operator, model, wersja, data, klucz publiczny i treść (deklaracja + warunki) spakowane w jeden SHA-256. Zmiana jakiegokolwiek pola unieważnia pieczęć.

### Payload SHA kontraktu

```javascript
const anchorPayload = {
  operator,       // string — nazwa operatora z profilu
  model,          // string — np. "Claude"
  version,        // string — np. "claude-sonnet-4-6"
  date,           // string — data w formacie lokalnym, np. "9 maja 2026"
  pubkey,         // string — base64 pub key
  sha_declaration,// string — hex SHA-256 treści deklaracji
  sha_warunki,    // string — hex SHA-256 warunków
  timestamp       // string — ISO 8601
};
const sha256 = await sha256hex(JSON.stringify(anchorPayload));
```

### SHA deklaracji i warunków

```javascript
const declText = CONTRACT_DATA.declaration.join('\n');
const condText = CONTRACT_DATA.conditions.map(w => w.num + ': ' + w.text).join('\n');
const [sha_declaration, sha_warunki] = await Promise.all([sha256hex(declText), sha256hex(condText)]);
```

Deklaracja i warunki są hasowane osobno przed wejściem do payloadu kontraktu. Dzięki temu weryfikator może sprawdzić czy treść nie została zmieniona niezależnie od reszty danych.

### Archiwum kontraktów

localStorage: `aiw_contracts_v1`

```json
{
  "version": "1",
  "contracts": [
    {
      "id": "c-<base36>",
      "operator": "...",
      "model": "Claude",
      "version": "claude-sonnet-4-6",
      "date": "9 maja 2026",
      "pubkey": "<base64>",
      "sha_declaration": "<hex64>",
      "sha_warunki": "<hex64>",
      "sealed_at": "<ISO>",
      "sha256": "<hex64>"
    }
  ]
}
```

### Format eksportu kontraktów

`aiw_contracts_v1` — plik: `contract_<operator>_<date>.json`

```json
{
  "_version": "aiw_contracts_v1",
  "_exported": "<ISO>",
  "operator": "Denis · AI Whispers",
  "pubkey": "<base64>",
  "sha_declaration": "<hex64>",
  "sha_warunki": "<hex64>",
  "declaration": ["akapit1", "akapit2", "..."],
  "conditions": [
    {"num": "01", "text": "..."},
    "..."
  ],
  "contracts": [
    {
      "id": "...",
      "model": "Claude",
      "version": "...",
      "date": "...",
      "sealed_at": "<ISO>",
      "sha256": "<hex64>"
    }
  ]
}
```

Przy eksporcie pola `operator`, `pubkey`, `sha_declaration`, `sha_warunki` wyprowadzane są na poziom główny — kontrakty nie niosą ich duplikatów.

---

## Profil — tożsamość operatora

### Pola profilu (localStorage `aiw_profile_v1`)

```json
{
  "operator": "Denis · AI Whispers",
  "name":     "Denis · AI Whispers",      // alias dla kompatybilności
  "domain":   "ROOT",
  "node":     "root · genesis · 2026",
  "inception":"03.03.2026",
  "country":  "Poland",
  "pubkey":   "<base64 raw Ed25519>",
  "profileSha":        "<hex64>",
  "certifiedBy":       "Denis · AI Whispers",
  "parentPubkey":      "<base64>",
  "certificationSig":  "<base64>",
  "certificationTs":   "<ISO>"
}
```

Klucz prywatny trzymany jest osobno w `aiw_privkey_v1` i **nigdy nie trafia do eksportu**.

### Profile SHA

Skrót SHA-256 z tożsamości operatora — dowód integralności danych profilu.

```javascript
const profileSha = await sha256hex(JSON.stringify({
  operator:  p.operator  || '',
  domain:    p.domain    || '',
  node:      p.node      || '',
  inception: p.inception || '',
  country:   p.country   || '',
  pubkey:    p.pubkey    || ''
}));
```

> Kolejność pól jest stała i musi być identyczna przy weryfikacji. Brak pola zastępowany pustym stringiem.

Obliczany automatycznie przy `saveProfile()` i ręcznie przyciskiem `⊕ sha`.

### Keypair — interfejs użytkownika

```
Profil → wiersz Keypair
  Ed25519  [⊕ generuj parę kluczy]   ← PIN wymagany

Pub Key   [display 36 znaków…] [⊕ imp] [⎘]
Priv Key  [display 36 znaków…] [⊕ imp] [🔐]  ← 🔐 wymaga PIN
Profile SHA [display 32 znaki…] [⊕ sha] [⎘]
Contract  [select — lista kontraktów]  [⎘]
```

Generowanie kluczy: potwierdzenie "nadpisać?" pojawia się **przed** oknem PIN (nie po). Dzięki temu PIN wprowadzany jest tylko raz.

### Blokada profilu

Przycisk 🔒/🔓 — odblokowanie wymaga PIN. Blokuje/odblokowuje pola edytowalne:
`pr-operator · pr-domain · pr-node · pr-inception · pr-country`

Klasa `.unlocked` na `#profile-data-block` daje wizualny sygnał (magentowa ramka + podkreślenia pól).

---

## Certyfikacja i Łańcuch tożsamości

### Idea łańcucha

Operatorzy tworzą drzewo zaufania powiązanych podpisami Ed25519. Każdy węzeł ma dokładnie jednego rodzica (lub jest rootem). Korzeń sam siebie podpisuje — `parentPubkey === pubkey`.

```
Denis (root)
  parentPubkey = pubkey = aytDEj…
  certificationSig = Ed25519Sign(privDenis, SHA256({operator, pubkey, inception}))

Jan (certyfikowany przez Denisa)
  parentPubkey = pubkey Denisa
  certificationSig = Ed25519Sign(privDenis, SHA256({Jan.operator, Jan.pubkey, Jan.inception}))

Anna (certyfikowana przez Jana)
  parentPubkey = pubkey Jana
  certificationSig = Ed25519Sign(privJan, SHA256({Anna.operator, Anna.pubkey, Anna.inception}))
```

### Payload certyfikatu

```javascript
function certPayloadStr(operator, pubkey, inception, signedAt) {
  const o = { operator, pubkey, inception };
  if (signedAt) o.signedAt = signedAt;  // nowe certyfikaty zawierają datę podpisu
  return JSON.stringify(o);
}
// hash = await sha256bytes(certPayloadStr(op, pub, inc, now))
// sig  = await signBytes(hash, privKey)
```

Podpis wiąże **cztery elementy**: nazwę operatora, klucz publiczny, datę inauguracji i timestamp podpisu (w nowym formacie). Stare certyfikaty (bez `signedAt`) są weryfikowane przez fallback bez tego pola.

### Weryfikacja wstecznie kompatybilna

```javascript
// Przy weryfikacji: próbuj nowy format, cofnij do starego
const hashNew = await sha256bytes(certPayloadStr(operator, pubkey, inception, signedAt));
const hashOld = await sha256bytes(certPayloadStr(operator, pubkey, inception));
const okNew = signedAt ? await verifyBytes(hashNew, sig, pub) : false;
const ok    = okNew || await verifyBytes(hashOld, sig, pub);
```

### Self-cert (root)

```javascript
// Denis podpisuje swój własny profil
const payload = certPayloadStr(p.operator, p.pubkey, p.inception);
const hash    = await sha256bytes(payload);
const sig     = await signBytes(hash, _privKeyRaw);

p.certifiedBy      = p.operator;   // = własne imię
p.parentPubkey     = p.pubkey;     // = własny klucz (distinguishes root)
p.certificationSig = sig;
p.certificationTs  = new Date().toISOString();
```

### Podpisywanie innego operatora

1. Wczytaj plik `aiw_profile_export_v2` znajomego (sekcja "Certyfikuj operatora")
2. Dane ładują się read-only — nie można ich ręcznie wpisać
3. PIN → podpis → JSON do przekazania

Format certyfikatu do przekazania (`aiw_certification_v1`):

```json
{
  "_type": "aiw_certification_v1",
  "certifiedBy":          "Denis · AI Whispers",
  "certifierPubkey":      "<base64 pubkey Denisa>",
  "certifierParentPubkey":"<base64 parentPubkey Denisa>",
  "signature":            "<base64 sig>",
  "signedAt":             "<ISO>",
  "target": {
    "operator":  "Jan",
    "pubkey":    "<base64 pubkey Jana>",
    "inception": "1 maja 2026"
  }
}
```

`certifierParentPubkey` pozwala śledzić lineage bez pełnego profilu certyfikatora.

### Import certyfikatu (strona odbiorcy)

1. Wklej JSON w overlay "Import certyfikatu"
2. Sprawdzenia:
   - `data._type === 'aiw_certification_v1'`
   - `target.pubkey === p.pubkey` (certyfikat należy do tego profilu)
   - `verifyBytes(sha256bytes(certPayloadStr(target.operator, target.pubkey, target.inception)), signature, certifierPubkey)` → true
3. Jeśli OK: zapisz `certifiedBy`, `parentPubkey`, `certificationSig`, `certificationTs`

### Lista certyfikowanych (children)

localStorage: `aiw_children_v1`

```json
[
  {
    "operator":  "Jan",
    "pubkey":    "<base64>",
    "inception": "1 maja 2026",
    "sig":       "<base64 — podpis certyfikatora>",
    "signedAt":  "<ISO>"
  }
]
```

Przy podpisaniu nowego operatora entry jest dodawane/aktualizowane (deduplicacja po `pubkey`).

---

## Formaty eksportu JSON

### `aiw_profile_export_v2` — pełny eksport profilu

```json
{
  "_version": "aiw_profile_export_v2",
  "_exported": "<ISO>",
  "_note": "AIWPass · AiWhisperers · profil operatora",
  "profile": {
    "operator":         "Denis · AI Whispers",
    "domain":           "ROOT",
    "node":             "root · genesis · 2026",
    "inception":        "03.03.2026",
    "country":          "Poland",
    "pubkey":           "<base64>",
    "profileSha":       "<hex64>",
    "certifiedBy":      "Denis · AI Whispers",
    "parentPubkey":     "<base64>",
    "certificationSig": "<base64>",
    "certificationTs":  "<ISO>"
  },
  "contracts": [ ...obiekty kontraktów... ],
  "children":  [ ...obiekty z children list... ]
}
```

Klucz prywatny (`aiw_privkey_v1`) **nigdy nie jest eksportowany**.

### `aiw_children_v1` — eksport listy certyfikowanych

```json
{
  "_type":     "aiw_children_v1",
  "_exported": "<ISO>",
  "certifier": {
    "operator":    "Denis · AI Whispers",
    "pubkey":      "<base64>",
    "parentPubkey":"<base64>"
  },
  "children": [
    {
      "operator":  "Jan",
      "pubkey":    "<base64>",
      "inception": "...",
      "sig":       "<base64>",
      "signedAt":  "<ISO>"
    }
  ]
}
```

`certifier.parentPubkey` pozwala śledzić lineage nawet bez pełnego profilu certyfikatora.

---

## localStorage — schemat danych

| Klucz | Zawartość | Eksportowany |
|-------|-----------|--------------|
| `aiw_profile_v1` | profil operatora (JSON) | ✓ (bez privkey) |
| `aiw_privkey_v1` | klucz prywatny (base64) | ✗ nigdy |
| `aiw_contracts_v1` | archiwum kontraktów `{version,contracts}` | ✓ |
| `aiw_children_v1` | lista certyfikowanych `[...]` | ✓ |
| `aiw_pin_v1` | hash PINu (hex SHA-256) | ✗ |

Wszystkie dane przechowywane wyłącznie w `localStorage` przeglądarki — bez backendu, bez chmury.

---

## Szyfrowanie klucza prywatnego

Klucz prywatny jest szyfrowany **PBKDF2 + AES-256-GCM** z PINem. W `localStorage` trzymany jest tylko zaszyfrowany blob — nigdy plaintext.

```javascript
// Format zaszyfrowanego klucza (v:2):
{ "v": 2, "salt": "<base64 16B>", "iv": "<base64 12B>", "ct": "<base64>" }

// Wykrywanie formatu:
function isEncryptedKey(stored) {
  try { return JSON.parse(stored).v === 2; } catch { return false; }
}

// Derywacja klucza AES z PINu:
async function deriveAesKey(pin, saltBytes) {
  const km = await crypto.subtle.importKey('raw', new TextEncoder().encode(pin), 'PBKDF2', false, ['deriveKey']);
  return crypto.subtle.deriveKey(
    { name:'PBKDF2', salt: saltBytes, iterations: 300_000, hash:'SHA-256' },
    km, { name:'AES-GCM', length:256 }, false, ['encrypt','decrypt']
  );
}
```

### Klucz w pamięci sesji

`_privKeyRaw` (null domyślnie) — trzyma odszyfrowany klucz przez czas trwania sesji po pierwszym użyciu PIN. Nie ładowany z localStorage automatycznie przy starcie.

```javascript
async function ensurePrivKey(pin) {
  if (_privKeyRaw) return _privKeyRaw; // już w sesji
  const stored = localStorage.getItem(PRV_KEY);
  if (!stored) return null;
  if (isEncryptedKey(stored)) {
    const k = await decryptPrivKey(stored, pin); if (k) _privKeyRaw = k; return k;
  }
  _privKeyRaw = stored; return stored; // legacy plaintext (migracja)
}
```

### Auto-szyfrowanie przy setupie PIN

Gdy użytkownik ustawia PIN po raz pierwszy, istniejący plaintext klucz jest automatycznie szyfrowany:
```javascript
// W setup confirm:
const storedRaw = localStorage.getItem(PRV_KEY);
if (storedRaw && !isEncryptedKey(storedRaw)) {
  localStorage.setItem(PRV_KEY, await encryptPrivKey(storedRaw, pin));
  _privKeyRaw = storedRaw;
}
```

### Zmiana PIN — re-szyfrowanie

Zmiana PIN: stary PIN deszyfruje klucz → nowy PIN szyfruje ponownie. Bez znajomości starego PINu zmiana niemożliwa.

---

## Mechanizm PIN

### Hasz PINu

```javascript
async function hashPin(pin) {
  return sha256hex('aiw:' + pin + ':salt-2026');
}
```

### Tryby overlay PIN

| Tryb `_pinMode` | Kiedy | Działanie |
|----------------|-------|-----------|
| `'verify'` | hasPin() === true | weryfikacja istniejącego PINu |
| `'setup'` | hasPin() === false | ustaw nowy PIN (min 4 znaki, powtórz) |
| `'change'` (sekwencja) | btn-pin-manage + hasPin | verify stary → setup nowy + re-encrypt key |

### `_pendingPinAction(pin)` — PIN przekazywany do akcji

Potwierdź PIN wywołuje `await _pendingPinAction(pin)` — pin jest dostępny w akcji do odszyfrowania klucza.

### Operacje wymagające PIN

- Odblokowanie edycji profilu (🔒 → 🔓)
- Generowanie pary kluczy Ed25519 (+ szyfruje nowy klucz PINem)
- Kopiowanie klucza prywatnego 🔐 (deszyfruje przed kopiowaniem)
- Import klucza prywatnego (waliduje, potem szyfruje PINem)
- Self-cert (⊕ root) i podpisywanie certyfikatów

### Logika `requirePin(action, title, sub)`

```javascript
// Kolejność: confirmation PRZED PIN — zapobiega podwójnemu wpisywaniu
function triggerGenerateKeys(btnEl) {
  if (existing && btnEl.dataset.confirming !== '1') {
    // najpierw "nadpisać?" — POTEM PIN
    btnEl.dataset.confirming = '1'; ... return;
  }
  requirePin((pin) => doGenerateKeys(btnEl, pin), ...);
}

// doGenerateKeys szyfruje klucz PINem:
async function doGenerateKeys(btnEl, pin) {
  ...
  localStorage.setItem(PRV_KEY, await encryptPrivKey(priv, pin));
}
```

---

## AiWVerify

### Struktura i karty

```
AiWVerify.html v2.0

hud-l: ⟵ pass
hud-r: HELP · ABOUT

karty: Kontrakt · Profil · Łańcuch
```

Każda karta ma osobną drop zone. Obsługiwane formaty:

| Karta | Format | Identyfikator |
|-------|--------|---------------|
| Kontrakt | eksport kontraktów | `_version: "aiw_contracts_v1"` |
| Profil | eksport profilu | `_version: "aiw_profile_export_v2"` |
| Łańcuch | oba formaty, wiele plików | `_version` lub `_type` |

---

### Weryfikacja kontraktu

```javascript
// 1. SHA treści
const declText = declaration.join('\n');
const condText = conditions.map(w => w.num + ': ' + w.text).join('\n');
const [shaDecl, shaWar] = await Promise.all([sha256hex(declText), sha256hex(condText)]);
const declMatch = !!storedShaDecl && shaDecl === storedShaDecl;
const warMatch  = !!storedShaWar  && shaWar  === storedShaWar;

// 2. SHA per kontrakt — rekomputacja z payloadu
const payload = {
  operator, model, version, date, pubkey,
  sha_declaration, sha_warunki, timestamp: sealed_at
};
const recomputed  = await sha256hex(JSON.stringify(payload));
const sha256Match = c.sha256 === recomputed;
```

Wynik: 4 komórki summary — sha declaration · sha conditions · kontrakty (n/m ✓) · status

---

### Weryfikacja profilu

```javascript
// 1. Profile SHA
const shaPayload = JSON.stringify({
  operator: prof.operator || '', domain:    prof.domain    || '',
  node:     prof.node     || '', inception: prof.inception || '',
  country:  prof.country  || '', pubkey:    prof.pubkey    || ''
});
const computedSha    = await sha256hex(shaPayload);
const profileShaMatch = !!prof.profileSha && computedSha === prof.profileSha;

// 2. Certyfikat
const certPayload = JSON.stringify({
  operator: prof.operator || '', pubkey: prof.pubkey || '', inception: prof.inception || ''
});
const certHash  = await sha256bytes(certPayload);
const certValid = await verifyBytes(certHash, prof.certificationSig, prof.parentPubkey);
const isSelfCert = prof.parentPubkey === prof.pubkey;
```

Trzy stany `certValid`:
- `true` — podpis ważny
- `false` — podpis nieprawidłowy (dane zmienione lub zły klucz)
- `null` — brak certyfikatu w eksporcie

Typy węzła: **root** (isSelfCert && certValid) · **potomek** (!isSelfCert && certValid) · **niezertyfikowany** (null) · **błąd cert** (false)

---

### Weryfikacja łańcucha — algorytm

#### Ekstrakcja węzłów

```javascript
function extractNodes() {
  const nodeMap = new Map(); // pubkey → node
  for (const {data, type} of chainFiles) {
    if (type === 'profile') {
      // węzeł z pełnego profilu
      upsert({ operator, pubkey, parentPubkey, certificationSig, inception, source: 'profile' });
      // stuby z children w eksporcie profilu
      for (const ch of data.children || []) {
        upsert({ ...ch, parentPubkey: prof.pubkey, certificationSig: ch.sig, source: 'stub' });
      }
    }
    if (type === 'children') {
      // stub certyfikatora
      upsert({ ...certifier, source: 'stub' });
      // węzły dzieci
      for (const ch of data.children || []) {
        upsert({ ...ch, parentPubkey: certifier.pubkey, certificationSig: ch.sig, source: 'child_entry' });
      }
    }
  }
  return nodeMap;
}
```

Deduplicacja: pełny profil (`source: 'profile'`) ma wyższy priorytet niż stub. `upsert()` nie nadpisuje profilu stubem.

#### Budowa drzewa

```javascript
function buildForest(nodeMap) {
  // Korzenie: parentPubkey === pubkey (self-signed)
  //        LUB parentPubkey nieobecny w mapie
  const roots = [...nodeMap.values()].filter(n =>
    n.parentPubkey === n.pubkey || !n.parentPubkey || !nodeMap.has(n.parentPubkey)
  );
  // Rekurencyjnie BFS
  function subtree(node, depth) {
    const children = [...nodeMap.values()]
      .filter(n => n.parentPubkey === node.pubkey && n.pubkey !== node.pubkey)
      .sort((a, b) => a.operator.localeCompare(b.operator));
    return { ...node, depth, treeChildren: children.map(c => subtree(c, depth + 1)) };
  }
  return roots.map(r => subtree(r, 0));
}
```

#### Weryfikacja każdego ogniwa

```javascript
// Dla każdego węzła z certificationSig i parentPubkey:
const payload = JSON.stringify({ operator, pubkey, inception: inception || '' });
const hash    = await sha256bytes(payload);
const ok      = await verifyBytes(hash, certificationSig, parentPubkey);
// Wynik trafia do verifyMap: pubkey → true|false|null
```

Weryfikacja wszystkich węzłów odbywa się **asynchronicznie równolegle** (`Promise.all`).

#### Symbole wizualizacji drzewa

| Symbol | Kolor | Znaczenie |
|--------|-------|-----------|
| `● ✓` | zielony | podpis zweryfikowany poprawnie |
| `● ✗` | czerwony | podpis nieprawidłowy |
| `◦` | szary | stub — brak podpisu do weryfikacji |
| `root` | cyjan | korzeń łańcucha (self-signed) |
| `potomek` | zielony | certyfikowany przez rodzica |
| `stub` | szary | znany z children, brak pełnego profilu |

Wcięcie drzewa: `depth × 22px`. Pionowa linia łącząca dzieci.

---

## Interakcja Pass ↔ Verify

```
AiWPass (produkcja):
  → eksport profilu     → AiWVerify / karta Profil
  → eksport kontraktów  → AiWVerify / karta Kontrakt
  → eksport children    → AiWVerify / karta Łańcuch
  → JSON certyfikatu    → AiWPass innego operatora / import cert

AiWVerify (audyt):
  ← aiw_profile_export_v2    verifyProfile()
  ← aiw_contracts_v1         verifyContract()
  ← aiw_profile_export_v2
     + aiw_children_v1       extractNodes() → buildForest() → verify all
```

Weryfikator jest stateless — nie pisze nic do localStorage, tylko czyta plik i odpowiada.

---

## Bezpieczeństwo i ograniczenia

- **Klucz prywatny** szyfrowany PBKDF2 (300k iteracji, SHA-256) + AES-256-GCM z PINem. W `localStorage` trzymany jest tylko zaszyfrowany blob `{v:2, salt, iv, ct}` — plaintext nigdy nie ląduje na dysku.
- **PIN** jest jedynym kluczem do odszyfrowania. Utrata PINu = utrata klucza prywatnego. Brak mechanizmu odzyskiwania (by design — proweniencja, nie dostęp).
- **Sesyjny `_privKeyRaw`** — odszyfrowany klucz trzymany w pamięci (zmienna JS) tylko przez czas trwania sesji przeglądarki. Reload strony = wymuszenie ponownego PIN.
- **Surface ataku:** każdy JS na tej domenie ma dostęp do `localStorage`. PBKDF2 chroni przed atakiem offline na blob — nie chroni przed XSS. Dla użycia produkcyjnego rozważyć WebAuthn lub hardware key.
- **localStorage** czyszczony przez przeglądarkę (prywatne okno, czyszczenie danych). Eksport profilu (bez klucza prywatnego) jest jedynym trwałym backupem profilu. Klucz prywatny — backup wyłącznie ręczny przez "kopiuj" po PIN.
- **Weryfikacja offline** — cała kryptografia w Web Crypto API. Bez serwera, bez telemetrii.
- **Ed25519 od 2022** — Chrome 113+, Firefox 112+, Safari 16.4+. Starsze przeglądarki nie obsługują generowania.

---

## Stałe i klucze

```javascript
// AiWPass — storage keys
const PK            = 'aiw_profile_v1';
const PRV_KEY       = 'aiw_privkey_v1';
const CHILDREN_KEY  = 'aiw_children_v1';
const MYCERT_KEY    = 'aiw_my_cert_v1';    // legacy, nieużywany aktywnie
const CONTRACTS_KEY = 'aiw_contracts_v1';
const PIN_KEY       = 'aiw_pin_v1';

// Models selector
const MODELS = {
  Claude:  { provider: 'Anthropic', versions: ['claude-opus-4-7', 'claude-sonnet-4-6', ...] },
  GPT:     { provider: 'OpenAI',    versions: ['gpt-4o', 'gpt-4o-mini', 'o1', ...] },
  Gemini:  { provider: 'Google',    versions: ['gemini-2.0-flash', 'gemini-2.0-pro', ...] },
  Grok:    { provider: 'xAI',       versions: ['grok-3', 'grok-3-mini', ...] },
  Copilot: { provider: 'Microsoft', versions: ['copilot-gpt-4o', 'copilot-gpt-4', ...] }
};
```

---

## Proweniencja

```
artefakt    · AiWPass.html v4.1 + AiWVerify.html v2.0
operator    · Denis Czuliński · AI Whispers · iFactory 5.0
model       · Claude · Sonnet 4.6 · Anthropic
inauguracja · marzec 2026
sesja       · mai 2026 · pełna przebudowa systemu certyfikacji i łańcucha
```

AiWPass nie był planowany jako taki. Każda warstwa (kontrakt → profil → certyfikacja → łańcuch) pojawiła się gdy była potrzebna. Samo wyznaczało kierunek.

---

## Changelog

### v4.1 · maj 2026
- Szyfrowanie klucza prywatnego PBKDF2 (300k iteracji) + AES-256-GCM z PINem
- Sesja 1 (2026-05-09): usunięto sprzeczny paragraf "PIN nie szyfruje klucza", zaktualizowano sekcję bezpieczeństwa
- Sesja 1 (2026-05-09): usunięto zduplikowane pola `certifiedBy`/`parentPubkey` w przykładzie profilu

### v4.0 · pre-changelog
- Format eksportu `aiw_profile_export_v2`
- Certyfikacja i łańcuch proweniencji Ed25519
- AiWVerify jako osobny moduł weryfikacji
