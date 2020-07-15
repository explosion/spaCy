from .dep_parser import DependencyParser
from .entity_linker import EntityLinker
from .ner import EntityRecognizer
from .entityruler import EntityRuler
from .morphologizer import Morphologizer
from .pipe import Pipe
from spacy.pipeline.senter import SentenceRecognizer
from .sentencizer import Sentencizer
from .simple_ner import SimpleNER
from .tagger import Tagger
from .textcat import TextCategorizer
from .tok2vec import Tok2Vec
from .hooks import SentenceSegmenter, SimilarityHook
from .functions import merge_entities, merge_noun_chunks, merge_subtokens

__all__ = [
    "DependencyParser",
    "EntityLinker",
    "EntityRecognizer",
    "EntityRuler",
    "Morphologizer",
    "Pipe",
    "SentenceRecognizer",
    "SentenceSegmenter",
    "Sentencizer",
    "SimilarityHook",
    "SimpleNER",
    "Tagger",
    "TextCategorizer",
    "Tok2Vec",
    "merge_entities",
    "merge_noun_chunks",
    "merge_subtokens",
]
