#!/usr/bin/env python3
"""
Weryfikuje integralność artefaktów modułów:
  - entry_sha     : SHA-256 pliku files.entry (HTML artefaktu)
  - bootstrap_sha : SHA-256 pliku files.bootstrap (*-boot.md)
Uruchamianie: python3 tools/check_integrity.py
"""
import json, hashlib, sys
from pathlib import Path


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_field(manifest_path: Path, files: dict, field: str, file_key: str, errors: list) -> int:
    """Sprawdza parę (files[file_key], files[field]). Zwraca 1 jeśli sprawdzono."""
    file_name    = files.get(file_key, "")
    sha_expected = files.get(field, "")

    if not file_name:
        return 0  # brak nazwy pliku — pole opcjonalne

    file_path = manifest_path.parent / file_name
    if not file_path.exists():
        return 0  # plik jeszcze nie istnieje — moduł w inkubacji, pomijamy

    if not sha_expected:
        errors.append(f"{manifest_path}: {file_key}='{file_name}' istnieje ale {field} pusty")
        return 0

    sha_actual = sha256_file(file_path)
    if sha_actual != sha_expected:
        errors.append(
            f"{manifest_path}: SHA mismatch dla {file_name} ({field})\n"
            f"  expected: {sha_expected}\n"
            f"  actual:   {sha_actual}"
        )
        return 1

    return 1


def main():
    apps_dir = Path("apps")
    if not apps_dir.exists():
        print(f"FAIL: {apps_dir} nie istnieje (uruchom z katalogu @AiWhisperers/)")
        sys.exit(1)

    errors  = []
    checked = 0

    root_manifest = Path("manifest.json")
    all_manifests = ([root_manifest] if root_manifest.exists() else []) + sorted(apps_dir.rglob("manifest.json"))
    for manifest_path in all_manifests:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        files    = manifest.get("files", {})

        checked += check_field(manifest_path, files, "entry_sha",     "entry",     errors)
        checked += check_field(manifest_path, files, "bootstrap_sha", "bootstrap", errors)
        checked += check_field(manifest_path, files, "docs_sha",      "docs",      errors)

    if errors:
        print(f"FAIL: {len(errors)} problemów (sprawdzono {checked} par):")
        for e in errors:
            print(f"  {e}")
        sys.exit(1)
    print(f"OK: wszystkie {checked} par SHA zgodne")


if __name__ == "__main__":
    main()
