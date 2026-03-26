# _verify-boot · AiWVerify · Knowledge Bootstrap

Esencja wiedzy dla modelu AI. Wczytaj ten plik zamiast AiWVerify.html.
Źródło: AiWVerify.html v2.1 · sesja: Wyrównanie Ekosystemu · 2026-05-09

---

## Czym jest ten moduł

`_verify` to audytor kryptograficzny ekosystemu AiWhisperers.
Działa wyłącznie lokalnie — Web Crypto API przeglądarki, bez serwera, bez telemetrii.
Każdy SHA, każdy podpis Ed25519 obliczany jest in-browser. Plik wgrany tutaj nie trafia nigdzie.

**Zasada:** weryfikacja to czysty dowód matematyczny — dane albo zgadzają się z kluczem, albo nie.

---

## Sześć kart weryfikacji

### Kontrakt
Wczytuje plik `aiw_contracts_v1` (eksport z AiWPass).
Sprawdza SHA-256 każdego kontraktu z archiwum i zgodność pubkey z profilem.
Format wejściowy: `contract_<operator>_<date>.json`.

### Profil
Wczytuje plik `aiw_profile_export_v2`.
Weryfikuje:
- **Profile SHA** — SHA-256 z pól: `operator · domain · node · inception · country · pubkey`
- **Podpis certyfikacji** — Ed25519 właściciela (`certificationSig`) nad SHA profilu
- **Kontrakty** powiązane z profilem
- **Self-cert** (root) vs cert zewnętrzny

### Łańcuch
Wczytuje wiele plików naraz: profil + children (`aiw_children_v1`) + certyfikaty.
Buduje drzewo zaufania (`extractNodes → buildForest`).
Każdy węzeł: zielony ✓ (podpis Ed25519 zweryfikowany), czerwony ✗ (niezgodność), szary ◦ (stub bez pełnego profilu).

### Sesja *(w rozwoju)*
Weryfikacja danych sesji — `session_sha`, kanoniczny payload proweniencji,
zgodność z kontraktem operatora, ciągłość łańcucha `parent_sid`.

### Artefakty
Wczytuje pary: `manifest.json` + plik HTML (`files.entry`) + opcjonalnie `*-boot.md` (`files.bootstrap`).
Weryfikuje trzy SHA:
- **`entry_sha`** — SHA-256 pliku HTML artefaktu (`files.entry`)
- **`bootstrap_sha`** — SHA-256 pliku `*-boot.md` (`files.bootstrap`)
- **`docs_sha`** — SHA-256 pliku dokumentacji (`files.docs`: readme.html, *-api-spec.md itp.)

Wynik dla każdego modułu: ✓ / ✗ / ◦ (brak SHA w manifeście) / ? (brak pliku w wczytanych)

### Akty *(w rozwoju)*
Weryfikacja paczek sesji — `aiw-export-*.json`, łańcuch aktów, SHA zbiorowy,
anchor na blockchain. Operuje na eksportach z AiWPass.

---

## Kryptografia — prymitywy (identyczne jak AiWPass)

### SHA-256

```javascript
async function sha256hex(str) {
  const buf = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(str));
  return Array.from(new Uint8Array(buf)).map(b => b.toString(16).padStart(2,'0')).join('');
}
```

### Weryfikacja Ed25519

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

P-256 obsługiwany przy imporcie dla wstecznej kompatybilności (prefiks `P256:`). Generowanie tylko Ed25519.

---

## Relacja z AiWPass

`AiWVerify` jest lustrem `AiWPass` — każda zmiana w Pass (nowe pola, nowy format payloadu) musi znaleźć odzwierciedlenie tutaj.

Typowy przepływ:
```
AiWPass → eksport kontraktów     → AiWVerify / karta Kontrakt
AiWPass → eksport profilu        → AiWVerify / karta Profil
AiWPass → eksport children       → AiWVerify / karta Łańcuch
manifest.json + HTML + boot.md   → AiWVerify / karta Artefakty
```

---

## Karta Artefakty — jak używać

1. Wrzuć dowolną liczbę plików naraz: `manifest.json`, pliki HTML, pliki `*-boot.md`
2. Verifier automatycznie paruje manifesty z plikami po nazwie z `files.entry` i `files.bootstrap`
3. Oblicza SHA-256 w przeglądarce i porównuje z `entry_sha` / `bootstrap_sha` w manifeście

Symbole wyników:
- `✓` — SHA zgodny z manifestem
- `✗` — NIEZGODNOŚĆ — plik zmieniony bez aktualizacji manifestu
- `◦` — brak SHA w manifeście (pole puste)
- `?` — plik nie został wczytany

---

## Changelog

### v2.1 · 2026-05-09
- Przeniesiony z `apps/_pass/` do własnego modułu `apps/_verify/`
- Dodano kartę **Artefakty** — weryfikacja `entry_sha` + `bootstrap_sha` (dwie kolumny)
- Dodano karty **Sesja** i **Akty** (w rozwoju)
- Top bar: `⟵ mapa` (lewo), `PASS` (prawo)
- Stworzono `_verify-boot.md` (ten plik)

### v2.0 · pre-changelog
- Trzy karty: Kontrakt · Profil · Łańcuch
- Auto-chain: `extractNodes → buildForest`, drzewo zaufania
- Wsteczna kompatybilność P-256
