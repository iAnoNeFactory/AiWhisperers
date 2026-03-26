#!/usr/bin/env python3
"""
Weryfikuje deterministyczność SHA payloadów proweniencji po stronie Python.
SHA musi być identyczny jak w tests/chain_test.mjs.
Uruchamianie: python3 tests/chain_test.py
"""
import json, hashlib, sys


def sha256hex(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def json_compact(obj) -> str:
    return json.dumps(obj, ensure_ascii=False, separators=(",", ":"))


# ── Test 1: payload kontraktu — deterministyczność ────────────────────────────

def test_contract_payload_deterministic():
    payload = {
        "operator":        "Denis · AI Whispers",
        "model":           "Claude",
        "version":         "claude-sonnet-4-6",
        "date":            "9 maja 2026",
        "pubkey":          "AAABBBCCC==",
        "sha_declaration": "deadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeef",
        "sha_warunki":     "cafef00dcafef00dcafef00dcafef00dcafef00dcafef00dcafef00dcafef00d",
        "timestamp":       "2026-05-09T10:00:00Z"
    }
    sha1 = sha256hex(json_compact(payload))
    sha2 = sha256hex(json_compact(payload))
    assert sha1 == sha2, "Payload kontraktu powinien być deterministyczny"

    reordered = {k: payload[k] for k in reversed(list(payload))}
    sha_reordered = sha256hex(json_compact(reordered))
    assert sha1 != sha_reordered, "Inna kolejność pól powinna dać inny SHA"

    print(f"✓ contract payload deterministyczny: {sha1[:16]}…")


# ── Test 2: SHA sesji — wartość referencyjna zgodna z JS ─────────────────────

def test_session_sha_canonical():
    session = {
        "nazwa":          "Test Session ✨",
        "chat_id":        "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
        "parent_sid":     "",
        "data":           "9 maja 2026",
        "typ":            "techniczna",
        "operator_state": "focused",
        "refleksja":      "Testowa refleksja z polskimi znakami: ąęśćźżóń.",
        "metryki": {
            "lustro":       "0.85",
            "klej":         "0.90",
            "zakorzeniony": "0.88",
            "tarcie":       "0.40",
            "rezonans":     "0.92",
            "cisza":        "0.70",
            "gestosc":      "0.80",
            "iskra":        "0.95",
            "tryb":         "Build"
        },
        "komentarze": {
            "lustro":       "test lustro",
            "klej":         "test klej",
            "zakorzeniony": "test zakorzeniony",
            "tarcie":       "test tarcie",
            "rezonans":     "test rezonans",
            "cisza":        "test cisza",
            "gestosc":      "test gestosc",
            "iskra":        "test iskra",
            "tryb":         "Build z rekonesansem."
        },
        "projekt": {
            "powstal":   False,
            "nazwa":     "",
            "komentarz": "",
            "artefakty": []
        },
        "contract_sha": "5f558a5ee8862fde54a47952fca52f23a9ad82ce1bb84024e733f01d7d15d586",
        "timestamp":    "2026-05-09T12:00:00Z"
    }

    sha = sha256hex(json_compact(session))

    # Wartość referencyjna — identyczna jak EXPECTED w tests/chain_test.mjs
    EXPECTED = "c7c0015f5ceac630e193d5b5e1aceec7df15fa9614e2ab9a48244056a4f516bb"
    assert sha == EXPECTED, (
        f"SHA sesji nie zgadza się ze wzorcem.\n"
        f"  expected: {EXPECTED}\n"
        f"  actual:   {sha}\n"
        f"  Jeśli zmiana była celowa — zaktualizuj EXPECTED w obu testach."
    )

    # null w parent_sid psuje hash
    session_null = {**session, "parent_sid": None}
    sha_null = sha256hex(json_compact(session_null))
    assert sha != sha_null, "None w parent_sid powinien dać inny SHA niż ''"

    print(f"✓ session SHA kanoniczny (zgodny z JS): {sha[:16]}…")


# ── Test 3: wartości metryk jako string, nie liczba ───────────────────────────

def test_metric_values_as_strings():
    as_strings = {"lustro": "0.85", "klej": "0.90"}
    as_numbers = {"lustro": 0.85,   "klej": 0.90}

    sha_str = sha256hex(json_compact(as_strings))
    sha_num = sha256hex(json_compact(as_numbers))
    assert sha_str != sha_num, "Metryki string i liczba powinny dać różne SHA"

    print(f"✓ metryki string vs number — poprawnie różne SHA")


# ── Runner ────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("── chain_test (Python) ─────────────────────────")
    try:
        test_contract_payload_deterministic()
        test_session_sha_canonical()
        test_metric_values_as_strings()
        print("────────────────────────────────────────────────")
        print("All tests passed.")
    except AssertionError as e:
        print(f"\nFAIL: {e}")
        sys.exit(1)
