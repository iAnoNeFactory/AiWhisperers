#!/usr/bin/env python3
"""Waliduje wszystkie manifest.json w apps/ wg JSON Schema."""
import json, sys
from pathlib import Path

try:
    from jsonschema import validate, ValidationError
except ImportError:
    print("FAIL: pip install jsonschema")
    sys.exit(2)


def check_no_null(obj, path=""):
    errors = []
    if obj is None:
        errors.append(f"null at {path}")
    elif isinstance(obj, dict):
        for k, v in obj.items():
            errors.extend(check_no_null(v, f"{path}.{k}"))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            errors.extend(check_no_null(v, f"{path}[{i}]"))
    return errors


def main():
    schema_path = Path("tools/manifest.schema.json")
    if not schema_path.exists():
        print(f"FAIL: {schema_path} nie istnieje (uruchom z katalogu @AiWhisperers/)")
        sys.exit(1)

    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    errors = []
    checked = 0

    root_manifest = Path("manifest.json")
    all_manifests = ([root_manifest] if root_manifest.exists() else []) + sorted(Path("apps").rglob("manifest.json"))
    for manifest_path in all_manifests:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        null_errors = check_no_null(manifest)
        for e in null_errors:
            errors.append(f"{manifest_path}: {e}")
        try:
            validate(instance=manifest, schema=schema)
            checked += 1
        except ValidationError as e:
            errors.append(f"{manifest_path}: {e.message} (at {'.'.join(str(p) for p in e.path)})")

    if errors:
        print(f"FAIL: {len(errors)} problemów (sprawdzono {checked} manifestów):")
        for e in errors:
            print(f"  {e}")
        sys.exit(1)
    print(f"OK: wszystkie {checked} manifestów zgodne ze schematem")


if __name__ == "__main__":
    main()
