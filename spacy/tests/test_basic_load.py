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
from spacy.tagger import Tagger
from spacy.syntax.parser import Parser, ParserModel
from spacy.matcher import Matcher
from spacy.syntax.parser import get_templates

from spacy.en import English


class TestLoadVocab(unittest.TestCase):
    def test_load(self):
        if path.exists(path.join(English.default_data_dir(), 'vocab')):
            vocab = Vocab.from_dir(path.join(English.default_data_dir(), 'vocab'))


class TestLoadTokenizer(unittest.TestCase):
    def test_load(self):
        data_dir = English.default_data_dir()
        if path.exists(path.join(data_dir, 'vocab')):
            vocab = Vocab.from_dir(path.join(data_dir, 'vocab'))
            tokenizer = Tokenizer.from_dir(vocab, path.join(data_dir, 'tokenizer'))


class TestLoadTagger(unittest.TestCase):
    def test_load(self):
        data_dir = English.default_data_dir()

        if path.exists(path.join(data_dir, 'vocab')):
            vocab = Vocab.from_dir(path.join(data_dir, 'vocab'))
            tagger = Tagger.from_dir(path.join(data_dir, 'tagger'), vocab)


class TestLoadParser(unittest.TestCase):
    def test_load(self):
        data_dir = English.default_data_dir()
        if path.exists(path.join(data_dir, 'vocab')):
            vocab = Vocab.from_dir(path.join(data_dir, 'vocab'))
        if path.exists(path.join(data_dir, 'deps')):
            parser = Parser.from_dir(path.join(data_dir, 'deps'), vocab.strings, ArcEager)

        config_data = {"labels": {"0": {"": True}, "1": {"": True}, "2": {"cc": True, "agent": True, "ccomp": True, "prt": True, "meta": True, "nsubjpass": True, "csubj": True, "conj": True, "dobj": True, "neg": True, "csubjpass": True, "mark": True, "auxpass": True, "advcl": True, "aux": True, "ROOT": True, "prep": True, "parataxis": True, "xcomp": True, "nsubj": True, "nummod": True, "advmod": True, "punct": True, "relcl": True, "quantmod": True, "acomp": True, "compound": True, "pcomp": True, "intj": True, "poss": True, "npadvmod": True, "case": True, "attr": True, "dep": True, "appos": True, "det": True, "nmod": True, "amod": True, "dative": True, "pobj": True, "expl": True, "predet": True, "preconj": True, "oprd": True, "acl": True}, "3": {"cc": True, "agent": True, "ccomp": True, "prt": True, "meta": True, "nsubjpass": True, "csubj": True, "conj": True, "acl": True, "poss": True, "neg": True, "mark": True, "auxpass": True, "advcl": True, "aux": True, "amod": True, "ROOT": True, "prep": True, "parataxis": True, "xcomp": True, "nsubj": True, "nummod": True, "advmod": True, "punct": True, "quantmod": True, "acomp": True, "pcomp": True, "intj": True, "relcl": True, "npadvmod": True, "case": True, "attr": True, "dep": True, "appos": True, "det": True, "nmod": True, "dobj": True, "dative": True, "pobj": True, "iobj": True, "expl": True, "predet": True, "preconj": True, "oprd": True}, "4": {"ROOT": True}}, "seed": 0, "features": "basic", "beam_width": 1}

        data_dir = English.default_data_dir()
        vocab = Vocab.from_dir(path.join(data_dir, 'vocab'))

        moves = ArcEager(vocab.strings, config_data['labels'])
        templates = get_templates(config_data['features'])

        model = ParserModel(moves.n_moves, templates)
        model.load(path.join(data_dir, 'deps', 'model'))

        parser = Parser(vocab.strings, moves, model)


if __name__ == '__main__':
    unittest.main()
