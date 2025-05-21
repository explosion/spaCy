import json
import os
from pathlib import Path

import pytest

from spacy.util import registry

# Path to the reference registry contents, relative to this file
REFERENCE_FILE = Path(__file__).parent / "registry_contents.json"


@pytest.fixture
def reference_registry():
    """Load reference registry contents from JSON file"""
    if not REFERENCE_FILE.exists():
        pytest.fail(f"Reference file {REFERENCE_FILE} not found.")

    with REFERENCE_FILE.open("r") as f:
        return json.load(f)


def test_registry_types(reference_registry):
    """Test that all registry types match the reference"""
    # Get current registry types
    current_registry_types = set(registry.get_registry_names())
    expected_registry_types = set(reference_registry.keys())

    # Check for missing registry types
    missing_types = expected_registry_types - current_registry_types
    assert not missing_types, f"Missing registry types: {', '.join(missing_types)}"


def test_registry_entries(reference_registry):
    """Test that all registry entries are present"""
    # Check each registry's entries
    for registry_name, expected_entries in reference_registry.items():
        # Skip if this registry type doesn't exist
        if not hasattr(registry, registry_name):
            pytest.fail(f"Registry '{registry_name}' does not exist.")

        # Get current entries
        reg = getattr(registry, registry_name)
        current_entries = sorted(list(reg.get_all().keys()))

        # Compare entries
        expected_set = set(expected_entries)
        current_set = set(current_entries)

        # Check for missing entries - these would indicate our new registry population
        # mechanism is missing something
        missing_entries = expected_set - current_set
        assert (
            not missing_entries
        ), f"Registry '{registry_name}' missing entries: {', '.join(missing_entries)}"
