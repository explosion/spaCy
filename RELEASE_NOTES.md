Bug fix for model downloading in environments without pip on PATH

## Fixes

- Fix `spacy download` failing in environments where `pip` is not on PATH but is available as a Python module (e.g., some virtual environments and containers)
