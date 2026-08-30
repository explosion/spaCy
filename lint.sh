#!/usr/bin/env bash
# Local lint script matching the CI Validate job + mypy type checks.
# Fixes formatting and import sorting in-place, then re-verifies in
# check mode to catch any conflicts between the two, and runs mypy.
set -euo pipefail

err=0

echo "==> ruff format (auto-fixing)"
python -m ruff format spacy

echo "==> ruff isort (auto-fixing)"
python -m ruff check spacy --select I --fix

echo "==> ruff format (verify)"
if ! python -m ruff format spacy --check; then
    echo "FAIL: isort fix broke formatting"
    err=1
fi

echo "==> ruff isort (verify)"
if ! python -m ruff check spacy --select I; then
    echo "FAIL: format fix broke import sorting"
    err=1
fi

echo "==> mypy"
if ! python -m mypy spacy; then
    err=1
fi

if [ "$err" -ne 0 ]; then
    echo "FAIL: see errors above"
    exit 1
fi

echo "OK: all checks passed"
