# coding: utf8
from __future__ import unicode_literals

from .pipeline import Tagger, DependencyParser, EntityRecognizer  # noqa
from .pipeline import TextCategorizer  # noqa
from .tensorizer import Tensorizer  # noqa
from .entityruler import EntityRuler  # noqa
from .hooks import SentenceSegmenter, SimilarityHook  # noqa
from .functions import merge_entities, merge_noun_chunks, merge_subtokens  # noqa
from .pipe import Pipe  # noqa
