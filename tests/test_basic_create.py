"""Some quick tests that don't depend on data files or on pytest, for debugging the
MS windows build issues."""
from __future__ import print_function, unicode_literals

import unittest
import re

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


class TestStringStore(unittest.TestCase):
    def test_encode_decode(self):
        strings = StringStore()
        hello_id = strings[u'Hello']
        world_id = strings[u'World']

        self.assertNotEqual(hello_id, world_id)
        
        self.assertEqual(strings[hello_id], u'Hello')
        self.assertEqual(strings[world_id], u'World')

        self.assertEqual(strings[u'Hello'], hello_id)
        self.assertEqual(strings[u'World'], world_id)


class TestMorphology(unittest.TestCase):
    def test_create(self):
        lemmatizer = Lemmatizer({}, {}, {})
        strings = StringStore()
        lemmatizer = Lemmatizer({}, {}, {})
        morphology = Morphology(strings, {}, lemmatizer)


class TestVocab(unittest.TestCase):
    def test_create(self):
        vocab = Vocab()

    def test_get_lexeme(self):
        vocab = Vocab()
        lexeme = vocab[u'Hello']
        assert lexeme.orth_ == u'Hello'


class TestTokenizer(unittest.TestCase):
    def test_create(self):
        vocab = Vocab()
        dummy_re = re.compile(r'sklfb;s')
        tokenizer = Tokenizer(vocab, {}, dummy_re, dummy_re, dummy_re)
        doc = tokenizer(u'I am a document.')
        
        self.assertEqual(len(doc), 4)


class TestTagger(unittest.TestCase):
    def test_create(self):
        vocab = Vocab()
        templates = ((1,),)
        model = Model(vocab.morphology.n_tags, templates, model_loc=None)
        tagger = Tagger(vocab, model)


class TestParser(unittest.TestCase):
    def test_create(self):
        vocab = Vocab()
        templates = ((1,),)
        labels_by_action = {0: ['One', 'Two'], 1: ['Two', 'Three']}
        transition_system = ArcEager(vocab.strings, labels_by_action)
        model = Model(vocab.morphology.n_tags, templates, model_loc=None)
        
        parser = Parser(vocab.strings, transition_system, model)


class TestMatcher(unittest.TestCase):
    def test_create(self):
        vocab = Vocab()
        matcher = Matcher(vocab, {})


if __name__ == '__main__':
    unittest.main()
