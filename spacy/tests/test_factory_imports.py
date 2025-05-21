# coding: utf-8
"""Test factory import compatibility from original and new locations."""

import importlib

import pytest


@pytest.mark.parametrize(
    "factory_name,original_module,compat_module",
    [
        ("make_tagger", "spacy.pipeline.factories", "spacy.pipeline.tagger"),
        ("make_sentencizer", "spacy.pipeline.factories", "spacy.pipeline.sentencizer"),
        ("make_ner", "spacy.pipeline.factories", "spacy.pipeline.ner"),
        ("make_parser", "spacy.pipeline.factories", "spacy.pipeline.dep_parser"),
        ("make_tok2vec", "spacy.pipeline.factories", "spacy.pipeline.tok2vec"),
        ("make_spancat", "spacy.pipeline.factories", "spacy.pipeline.spancat"),
        (
            "make_spancat_singlelabel",
            "spacy.pipeline.factories",
            "spacy.pipeline.spancat",
        ),
        ("make_lemmatizer", "spacy.pipeline.factories", "spacy.pipeline.lemmatizer"),
        ("make_entity_ruler", "spacy.pipeline.factories", "spacy.pipeline.entityruler"),
        ("make_span_ruler", "spacy.pipeline.factories", "spacy.pipeline.span_ruler"),
        (
            "make_edit_tree_lemmatizer",
            "spacy.pipeline.factories",
            "spacy.pipeline.edit_tree_lemmatizer",
        ),
        (
            "make_attribute_ruler",
            "spacy.pipeline.factories",
            "spacy.pipeline.attributeruler",
        ),
        (
            "make_entity_linker",
            "spacy.pipeline.factories",
            "spacy.pipeline.entity_linker",
        ),
        ("make_textcat", "spacy.pipeline.factories", "spacy.pipeline.textcat"),
        ("make_token_splitter", "spacy.pipeline.factories", "spacy.pipeline.functions"),
        ("make_doc_cleaner", "spacy.pipeline.factories", "spacy.pipeline.functions"),
        (
            "make_morphologizer",
            "spacy.pipeline.factories",
            "spacy.pipeline.morphologizer",
        ),
        ("make_senter", "spacy.pipeline.factories", "spacy.pipeline.senter"),
        ("make_span_finder", "spacy.pipeline.factories", "spacy.pipeline.span_finder"),
        (
            "make_multilabel_textcat",
            "spacy.pipeline.factories",
            "spacy.pipeline.textcat_multilabel",
        ),
        ("make_beam_ner", "spacy.pipeline.factories", "spacy.pipeline.ner"),
        ("make_beam_parser", "spacy.pipeline.factories", "spacy.pipeline.dep_parser"),
        ("make_nn_labeller", "spacy.pipeline.factories", "spacy.pipeline.multitask"),
        # This one's special because the function was named make_span_ruler, so
        # the name in the registrations.py doesn't match the name we make the import hook
        # point to. We could  make a test just for this but shrug
        # ("make_future_entity_ruler", "spacy.pipeline.factories", "spacy.pipeline.span_ruler"),
    ],
)
def test_factory_import_compatibility(factory_name, original_module, compat_module):
    """Test that factory functions can be imported from both original and compatibility locations."""
    # Import from the original module (registrations.py)
    original_module_obj = importlib.import_module(original_module)
    original_factory = getattr(original_module_obj, factory_name)
    assert (
        original_factory is not None
    ), f"Could not import {factory_name} from {original_module}"

    # Import from the compatibility module (component file)
    compat_module_obj = importlib.import_module(compat_module)
    compat_factory = getattr(compat_module_obj, factory_name)
    assert (
        compat_factory is not None
    ), f"Could not import {factory_name} from {compat_module}"

    # Test that they're the same function (identity)
    assert original_factory is compat_factory, (
        f"Factory {factory_name} imported from {original_module} is not the same object "
        f"as the one imported from {compat_module}"
    )
