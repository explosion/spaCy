# coding: utf8
from __future__ import unicode_literals

from .pipes import Tagger, DependencyParser, EntityRecognizer, EntityLinker
from .pipes import TextCategorizer, Tensorizer, Pipe, Sentencizer
from .morphologizer import Morphologizer
from .entityruler import EntityRuler
from .tok2vec import Tok2Vec
from .hooks import SentenceSegmenter, SimilarityHook
from .functions import merge_entities, merge_noun_chunks, merge_subtokens

__all__ = [
    "Tagger",
    "DependencyParser",
    "EntityRecognizer",
    "EntityLinker",
    "TextCategorizer",
    "Tensorizer",
    "Tok2Vec",
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
