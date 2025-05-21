# coding: utf-8
"""Test factory import compatibility from original and new locations."""

import pytest
import importlib


@pytest.mark.parametrize(
    "factory_name,original_module,compat_module",
    [
        ("make_tagger", "spacy.registrations", "spacy.pipeline.tagger"),
        ("make_sentencizer", "spacy.registrations", "spacy.pipeline.sentencizer"),
        ("make_ner", "spacy.registrations", "spacy.pipeline.ner"),
        ("make_parser", "spacy.registrations", "spacy.pipeline.dep_parser"),
        ("make_tok2vec", "spacy.registrations", "spacy.pipeline.tok2vec"),
        ("make_spancat", "spacy.registrations", "spacy.pipeline.spancat"),
        ("make_spancat_singlelabel", "spacy.registrations", "spacy.pipeline.spancat"),
        ("make_lemmatizer", "spacy.registrations", "spacy.pipeline.lemmatizer"),
        ("make_entity_ruler", "spacy.registrations", "spacy.pipeline.entityruler"),
        ("make_span_ruler", "spacy.registrations", "spacy.pipeline.span_ruler"),
        (
            "make_edit_tree_lemmatizer",
            "spacy.registrations",
            "spacy.pipeline.edit_tree_lemmatizer",
        ),
        (
            "make_attribute_ruler",
            "spacy.registrations",
            "spacy.pipeline.attributeruler",
        ),
        ("make_entity_linker", "spacy.registrations", "spacy.pipeline.entity_linker"),
        ("make_textcat", "spacy.registrations", "spacy.pipeline.textcat"),
        ("make_token_splitter", "spacy.registrations", "spacy.pipeline.functions"),
        ("make_doc_cleaner", "spacy.registrations", "spacy.pipeline.functions"),
        ("make_morphologizer", "spacy.registrations", "spacy.pipeline.morphologizer"),
        ("make_senter", "spacy.registrations", "spacy.pipeline.senter"),
        ("make_span_finder", "spacy.registrations", "spacy.pipeline.span_finder"),
        (
            "make_multilabel_textcat",
            "spacy.registrations",
            "spacy.pipeline.textcat_multilabel",
        ),
        ("make_beam_ner", "spacy.registrations", "spacy.pipeline.ner"),
        ("make_beam_parser", "spacy.registrations", "spacy.pipeline.dep_parser"),
        ("make_nn_labeller", "spacy.registrations", "spacy.pipeline.multitask"),
        # This one's special because the function was named make_span_ruler, so
        # the name in the registrations.py doesn't match the name we make the import hook
        # point to. We could  make a test just for this but shrug
        # ("make_future_entity_ruler", "spacy.registrations", "spacy.pipeline.span_ruler"),
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

