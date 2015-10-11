"""Some quick tests that don't depend on data files or on pytest, for debugging the
MS windows build issues."""
from __future__ import print_function, unicode_literals

import unittest
import re
from os import path

from spacy.lemmatizer import Lemmatizer
from spacy.morphology import Morphology
from spacy.strings import StringStore
from spacy.vocab import Vocab
from spacy.tokenizer import Tokenizer
from spacy.syntax.arc_eager import ArcEager
from spacy._ml import Model
from spacy.tagger import Tagger
from spacy.syntax.parser import Parser
from spacy.matcher import Matcher

from spacy.en import English


class TestLoadVocab(unittest.TestCase):
    def test_load(self):
        vocab = Vocab.from_dir(path.join(English.default_data_dir(), 'vocab'))


class TestLoadTokenizer(unittest.TestCase):
    def test_load(self):
        data_dir = English.default_data_dir()
        vocab = Vocab.from_dir(path.join(data_dir, 'vocab'))
        tokenizer = Tokenizer.from_dir(vocab, path.join(data_dir, 'tokenizer'))


class TestLoadTagger(unittest.TestCase):
    def test_load(self):
        data_dir = English.default_data_dir()
        vocab = Vocab.from_dir(path.join(data_dir, 'vocab'))
        tagger = Tagger.from_dir(path.join(data_dir, 'tagger'), vocab)


class TestLoadParser(unittest.TestCase):
    def test_load(self):
        data_dir = English.default_data_dir()
        vocab = Vocab.from_dir(path.join(data_dir, 'vocab'))
        parser = Parser.from_dir(path.join(data_dir, 'deps'), vocab.strings, ArcEager)


if __name__ == '__main__':
    unittest.main()
