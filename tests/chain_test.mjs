// tests/chain_test.mjs
// Uruchamianie: node tests/chain_test.mjs
// Weryfikuje deterministyczność SHA payloadów proweniencji.
// Brak zewnętrznych zależności — tylko node:crypto.

import { webcrypto } from 'node:crypto';
import { strict as assert } from 'node:assert';

const { subtle } = webcrypto;

async function sha256hex(str) {
  const buf = await subtle.digest('SHA-256', new TextEncoder().encode(str));
  return Array.from(new Uint8Array(buf)).map(b => b.toString(16).padStart(2, '0')).join('');
}

// ── Test 1: payload kontraktu — deterministyczność ────────────────────────────

async function testContractPayloadDeterministic() {
  const payload = {
    operator:        "Denis · AI Whispers",
    model:           "Claude",
    version:         "claude-sonnet-4-6",
    date:            "9 maja 2026",
    pubkey:          "AAABBBCCC==",
    sha_declaration: "deadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeef",
    sha_warunki:     "cafef00dcafef00dcafef00dcafef00dcafef00dcafef00dcafef00dcafef00d",
    timestamp:       "2026-05-09T10:00:00Z"
  };

  const sha1 = await sha256hex(JSON.stringify(payload));
  const sha2 = await sha256hex(JSON.stringify(payload));
  assert.equal(sha1, sha2, "Payload kontraktu powinien być deterministyczny");

  // Inna kolejność kluczy = inny SHA — to jest oczekiwane i POŻĄDANE
  // (dlatego kolejność w anchorPayload musi być stała)
  const reordered = {
    timestamp:       payload.timestamp,
    operator:        payload.operator,
    model:           payload.model,
    version:         payload.version,
    date:            payload.date,
    pubkey:          payload.pubkey,
    sha_declaration: payload.sha_declaration,
    sha_warunki:     payload.sha_warunki
  };
  const shaReordered = await sha256hex(JSON.stringify(reordered));
  assert.notEqual(sha1, shaReordered, "Inna kolejność pól powinna dać inny SHA");

  console.log(`✓ contract payload deterministyczny: ${sha1.slice(0,16)}…`);
}

// ── Test 2: SHA sesji — kanoniczny payload ────────────────────────────────────

async function testSessionShaCanonical() {
  const session = {
    nazwa:          "Test Session ✨",
    chat_id:        "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    parent_sid:     "",
    data:           "9 maja 2026",
    typ:            "techniczna",
    operator_state: "focused",
    refleksja:      "Testowa refleksja z polskimi znakami: ąęśćźżóń.",
    metryki: {
      lustro:       "0.85",
      klej:         "0.90",
      zakorzeniony: "0.88",
      tarcie:       "0.40",
      rezonans:     "0.92",
      cisza:        "0.70",
      gestosc:      "0.80",
      iskra:        "0.95",
      tryb:         "Build"
    },
    komentarze: {
      lustro:       "test lustro",
      klej:         "test klej",
      zakorzeniony: "test zakorzeniony",
      tarcie:       "test tarcie",
      rezonans:     "test rezonans",
      cisza:        "test cisza",
      gestosc:      "test gestosc",
      iskra:        "test iskra",
      tryb:         "Build z rekonesansem."
    },
    projekt: {
      powstal:   false,
      nazwa:     "",
      komentarz: "",
      artefakty: []
    },
    contract_sha: "5f558a5ee8862fde54a47952fca52f23a9ad82ce1bb84024e733f01d7d15d586",
    timestamp:    "2026-05-09T12:00:00Z"
  };

  const sha = await sha256hex(JSON.stringify(session));

  // Wartość referencyjna — wygenerowana przy pierwszym uruchomieniu.
  // Jeśli specyfikacja session_payload się zmieni, ten assert złamie się celowo.
  const EXPECTED = "c7c0015f5ceac630e193d5b5e1aceec7df15fa9614e2ab9a48244056a4f516bb";
  assert.equal(sha, EXPECTED,
    `SHA sesji nie zgadza się ze wzorcem.\n  expected: ${EXPECTED}\n  actual:   ${sha}\n` +
    `  Jeśli zmiana była celowa — zaktualizuj EXPECTED w tym teście.`
  );

  // Weryfikacja: null w parent_sid psuje hash (model musi dawać "")
  const withNull = { ...session, parent_sid: null };
  const shaNullParent = await sha256hex(JSON.stringify(withNull));
  assert.notEqual(sha, shaNullParent, "null w parent_sid powinien dać inny SHA niż ''");

  console.log(`✓ session SHA kanoniczny: ${sha.slice(0,16)}…`);
}

// ── Test 3: wartości metryk jako string, nie liczba ───────────────────────────

async function testMetricValuesAsStrings() {
  const base = { lustro: "0.85", klej: "0.90" };
  const asNumbers = { lustro: 0.85, klej: 0.90 };

  const shaString = await sha256hex(JSON.stringify(base));
  const shaNumber = await sha256hex(JSON.stringify(asNumbers));
  assert.notEqual(shaString, shaNumber,
    "Metryki jako string i jako liczba powinny dać różne SHA"
  );

  console.log(`✓ metryki string vs number — poprawnie różne SHA`);
}

// ── Runner ────────────────────────────────────────────────────────────────────

async function run() {
  console.log("── chain_test ──────────────────────────────────");
  try {
    await testContractPayloadDeterministic();
    await testSessionShaCanonical();
    await testMetricValuesAsStrings();
    console.log("────────────────────────────────────────────────");
    console.log("All tests passed.");
  } catch (err) {
    console.error("\nFAIL:", err.message);
    process.exit(1);
  }
}

run();
