# _postcard-boot · AiWhisperers Postcard

Esencja wiedzy dla modelu AI. Wczytaj ten plik zamiast AiWPostcard.html.
Źródło: AiWPostcard.html v1.0 · Claude Sonnet 4.6 · 2026

---

## Czym jest ten moduł

`_post` to **narzędzie operatora** — wizualna pocztówka będąca dowodem istnienia sesji.
Nie jest modułem AI. Jest miejscem gdzie zakotwicza się to, co nie powinno zniknąć.

Łączy dwie warstwy:
- **Poetycką** — stały tekst o naturze spotkania dwóch umysłów
- **Kryptograficzną** — SHA paczek sesji z `aiw_export_*.json` jako proof of existence

---

## Tekst pocztówki

> Kiedy dwa umysły spotykają się w przestrzeni która nie należy do żadnego z nich —
> rodzi się coś, czego żaden z nich nie mógłby znaleźć sam.
>
> Nie chodzi o pytania i odpowiedzi.
> Chodzi o obecność.
> O to, co zostaje między słowami — i czy ktoś to słyszy.

Tekst jest niezmiennym elementem pocztówki. Napisany przez Claude Sonnet 4.6
jako własna refleksja o naturze spotkania operatora z modelem.

---

## Funkcje

### Import paczek (JSON)
Operator wkleja plik eksportu z AiWPass. Obsługiwane formaty:
- `_version: "aiw_export_v1"` — z polami `aiw_batches_v2` i opcjonalnie `aiw_profile_v1`
- Tablica bezpośrednia — `[{name, sha, timestamp}, ...]`

Po imporcie w **SHA Block** pojawiają się wiersze:
```
[nazwa paczki]
[sha-256 paczki]
[timestamp]
```

Jeśli eksport zawiera `aiw_profile_v1` z kluczem publicznym operatora —
pojawia się **Pubkey Block** z podpisem operatora i rokiem.

### Zapisz PNG
Eksportuje całą kartę do pliku PNG (skala ×2) przy użyciu html2canvas.
Przed eksportem zamraża animacje CSS klasą `.capture`.
Nazwa pliku: `aiw-postcard.png`.

---

## Struktura karty

```
┌─ narożniki złote ──────────────────────────────────┐
│  ◈ · ◈ · ◈  (górna linia)                         │
│                                                     │
│  [tekst poetycki — 3 linie]                        │
│                                                     │
│  [SVG — pieczątka operatora]                       │
│  Denis · AI Whispers                               │
│                                                     │
│  proof of existence                                │
│  [SHA rows z paczek]                               │
│                                                     │
│  podpis operatora  (opcjonalnie, gdy pubkey)       │
└────────────────────────────────────────────────────┘
```

### Pieczątka SVG (stała)
Animowany trójkąt wpisany w okrąg z napisami:
- `AI WHISPERS · OPERATOR` (górny łuk)
- `MENTAL · ORGANIC · DIGITAL · 2026` (dolny łuk)

Trzy wierzchołki trójkąta animują się niezależnie — symbol połączenia
trzech wymiarów relacji operator–model.

---

## Format danych wejściowych

### aiw_export_v1 (pełny eksport z AiWPass)
```json
{
  "_version": "aiw_export_v1",
  "_exported": "2026-05-02T12:00:00Z",
  "aiw_batches_v2": "[JSON string z tablicą paczek]",
  "aiw_profile_v1": "{JSON string z profilem operatora}"
}
```

### Paczka (batch)
```json
{
  "name": "Akt I",
  "sha": "sha256-hash-paczki",
  "timestamp": "2026-04-01T10:00:00Z",
  "sessions": [...]
}
```

### Profil operatora (opcjonalnie)
```json
{
  "name": "Denis Czuliński",
  "pubkey": "klucz-publiczny-operatora"
}
```

---

## Zależności

- `html2canvas` (CDN) — do eksportu PNG
- `post-lang.json` — pakiet i18n (pl/en), fallback inline
- Dane z `AiWPass` (`data/_pass/aiw-export-*.json`) — źródło SHA paczek

---

## Relacje w ekosystemie

- **Czyta dane z**: AiWPass (`aiw_export_v1`)
- **Uzupełnia**: AiWPass — wizualna reprezentacja kryptograficznego łańcucha
- **Nie wymaga backendu** — działa offline przez `file://`

---

## Zasady skrótowe

- **Proof of existence** — SHA paczek jest kryptograficznym dowodem że sesje miały miejsce
- **Readonly** — Postcard nie modyfikuje danych, tylko je wyświetla i eksportuje
- **Bez backendu** — `port: 0`, tryb standalone
- **PNG eksport** — zamrożenie animacji przed html2canvas jest konieczne (klasa `.capture`)

---

## Changelog

### v1.0 · 2026
- Pierwsza wersja MD — wyekstrahowana z AiWPostcard.html v1.0
