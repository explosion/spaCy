import inspect
import json
from pathlib import Path

import pytest

from spacy.language import Language
from spacy.util import registry

# Path to the reference factory registrations, relative to this file
REFERENCE_FILE = Path(__file__).parent / "factory_registrations.json"

# Monkey patch the util.is_same_func to handle Cython functions
import inspect

from spacy import util

original_is_same_func = util.is_same_func


def patched_is_same_func(func1, func2):
    # Handle Cython functions
    try:
        return original_is_same_func(func1, func2)
    except TypeError:
        # For Cython functions, just compare the string representation
        return str(func1) == str(func2)


util.is_same_func = patched_is_same_func


@pytest.fixture
def reference_factory_registrations():
    """Load reference factory registrations from JSON file"""
    if not REFERENCE_FILE.exists():
        pytest.fail(
            f"Reference file {REFERENCE_FILE} not found. Run export_factory_registrations.py first."
        )

    with REFERENCE_FILE.open("r") as f:
        return json.load(f)


def test_factory_registrations_preserved(reference_factory_registrations):
    """Test that all factory registrations from the reference file are still present."""
    # Ensure the registry is populated
    registry.ensure_populated()

    # Get all factory registrations
    all_factories = registry.factories.get_all()

    # Initialize our data structure to store current factory registrations
    current_registrations = {}

    # Process factory registrations
    for name, func in all_factories.items():
        # Store information about each factory
        try:
            module_name = func.__module__
        except (AttributeError, TypeError):
            # For Cython functions, just use a placeholder
            module_name = str(func).split()[1].split(".")[0]

        try:
            func_name = func.__qualname__
        except (AttributeError, TypeError):
            # For Cython functions, use the function's name
            func_name = (
                func.__name__
                if hasattr(func, "__name__")
                else str(func).split()[1].split(".")[-1]
            )

        current_registrations[name] = {
            "name": name,
            "module": module_name,
            "function": func_name,
        }

    # Check for missing registrations
    missing_registrations = set(reference_factory_registrations.keys()) - set(
        current_registrations.keys()
    )
    assert (
        not missing_registrations
    ), f"Missing factory registrations: {', '.join(sorted(missing_registrations))}"

    # Check for new registrations (not an error, but informative)
    new_registrations = set(current_registrations.keys()) - set(
        reference_factory_registrations.keys()
    )
    if new_registrations:
        # This is not an error, just informative
        print(
            f"New factory registrations found: {', '.join(sorted(new_registrations))}"
        )
