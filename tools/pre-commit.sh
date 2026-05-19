#!/bin/bash
# Pre-commit hook — weryfikuje integralność projektu przed każdym commitem.
# Instalacja: ln -s ../../tools/pre-commit.sh .git/hooks/pre-commit
#             chmod +x tools/pre-commit.sh .git/hooks/pre-commit

set -e
cd "$(git rev-parse --show-toplevel)"

echo "→ Buduję sitemap.xml..."
python3 tools/build_sitemap.py
git add sitemap.xml

echo "→ Sprawdzam entry_sha + bootstrap_sha..."
python3 tools/check_integrity.py

echo "→ Waliduję manifesty..."
python3 tools/validate_manifests.py

echo "→ Test łańcucha SHA (Python)..."
python3 tests/chain_test.py

if command -v node &>/dev/null; then
  echo "→ Test łańcucha SHA (Node)..."
  node tests/chain_test.mjs
else
  echo "⚠  node nie znaleziony — pomijam chain_test.mjs"
fi

echo "✓ Wszystkie sprawdzenia przeszły"
