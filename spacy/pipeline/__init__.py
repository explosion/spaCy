# coding: utf8
from __future__ import unicode_literals

from .pipes import Tagger, DependencyParser, EntityRecognizer, EntityLinker
from .pipes import TextCategorizer, Tensorizer, Pipe, Sentencizer
from .morphologizer import Morphologizer
from .entityruler import EntityRuler
from .hooks import SentenceSegmenter, SimilarityHook
from .functions import merge_entities, merge_noun_chunks, merge_subtokens

__all__ = [
    "Tagger",
    "DependencyParser",
    "EntityRecognizer",
    "EntityLinker",
    "TextCategorizer",
    "Tensorizer",
    "Pipe",
    "Morphologizer",
    "EntityRuler",
    "Sentencizer",
    "SentenceSegmenter",
    "SimilarityHook",
    "merge_entities",
    "merge_noun_chunks",
    "merge_subtokens",
]
