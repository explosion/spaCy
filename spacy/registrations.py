"""Centralized registry population for spaCy components.

This module centralizes registry decorations to prevent circular import issues
with Cython annotation changes from __future__ import annotations. Functions
remain in their original locations, but decoration is moved here.
"""
from typing import Dict, Any

# Global flag to track if registry has been populated
REGISTRY_POPULATED = False

def populate_registry() -> None:
    """Populate the registry with all necessary components.
    
    This function should be called before accessing the registry, to ensure 
    it's populated. The function uses a global flag to prevent repopulation.
    """
    global REGISTRY_POPULATED
    if REGISTRY_POPULATED:
        return
    
    # Import all necessary modules
    from .util import registry, make_first_longest_spans_filter
    
    # Register miscellaneous components 
    registry.misc("spacy.first_longest_spans_filter.v1")(make_first_longest_spans_filter)
    
    # Import all pipeline components that were using registry decorators
    from .pipeline.tagger import make_tagger_scorer
    from .pipeline.ner import make_ner_scorer
    
    # Need to get references to the existing functions in registry by importing the function that is there
    # For the registry that was previously decorated
    
    # Import functions for use in registry
    from .scorer import get_ner_prf  # Used for entity_ruler_scorer
    
    # Import ML components that use registry
    from .ml.models.tok2vec import tok2vec_listener_v1, build_hash_embed_cnn_tok2vec
    
    # Register scorers
    registry.scorers("spacy.tagger_scorer.v1")(make_tagger_scorer)
    registry.scorers("spacy.ner_scorer.v1")(make_ner_scorer)
    # span_ruler_scorer removed as it's not in span_ruler.py
    registry.scorers("spacy.entity_ruler_scorer.v1")(make_entityruler_scorer)
    registry.scorers("spacy.sentencizer_scorer.v1")(make_sentencizer_scorer)
    registry.scorers("spacy.senter_scorer.v1")(make_senter_scorer)
    registry.scorers("spacy.textcat_scorer.v1")(make_textcat_scorer)
    registry.scorers("spacy.textcat_multilabel_scorer.v1")(make_textcat_multilabel_scorer)
    registry.scorers("spacy.span_finder_scorer.v1")(make_span_finder_scorer)
    registry.scorers("spacy.spancat_scorer.v1")(make_spancat_scorer)
    
    # Register tok2vec architectures we've modified
    registry.architectures("spacy.Tok2VecListener.v1")(tok2vec_listener_v1)
    registry.architectures("spacy.HashEmbedCNN.v2")(build_hash_embed_cnn_tok2vec)
    
    # Set the flag to indicate that the registry has been populated
    REGISTRY_POPULATED = True