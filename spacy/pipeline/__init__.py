# coding: utf8
from __future__ import unicode_literals

from .pipes import Tagger, DependencyParser, EntityRecognizer  # noqa
from .pipes import TextCategorizer, Tensorizer, Pipe  # noqa
from .entityruler import EntityRuler  # noqa
from .hooks import SentenceSegmenter, SimilarityHook  # noqa
from .functions import merge_entities, merge_noun_chunks, merge_subtokens  # noqa
