# coding: utf8
from __future__ import unicode_literals

from .pipes import Tagger, DependencyParser, EntityRecognizer, Morphologizer
from .pipes import TextCategorizer, Tensorizer, Pipe
from .entityruler import EntityRuler
from .hooks import SentenceSegmenter, SimilarityHook
from .functions import merge_entities, merge_noun_chunks, merge_subtokens

__all__ = [
    "Tagger",
    "DependencyParser",
    "EntityRecognizer",
    "TextCategorizer",
    "Tensorizer",
    "Pipe",
    "Morphologizer",
    "EntityRuler",
    "SentenceSegmenter",
    "SimilarityHook",
    "merge_entities",
    "merge_noun_chunks",
    "merge_subtokens",
]
