# cython: infer_types=True
# cython: profile=True
# coding: utf8
from __future__ import unicode_literals

from thinc.api import chain, layerize, with_getitem
from thinc.neural import Model, Softmax
import numpy
cimport numpy as np

from .tokens.doc cimport Doc
from .syntax.parser cimport Parser
from .syntax.parser import get_templates as get_feature_templates
from .syntax.beam_parser cimport BeamParser
from .syntax.ner cimport BiluoPushDown
from .syntax.arc_eager cimport ArcEager
from .tagger import Tagger
from .gold cimport GoldParse

from thinc.api import add, layerize, chain, clone, concatenate
from thinc.neural import Model, Maxout, Softmax, Affine
from thinc.neural._classes.hash_embed import HashEmbed
from thinc.neural.util import to_categorical

from thinc.neural._classes.convolution import ExtractWindow
from thinc.neural._classes.resnet import Residual
from thinc.neural._classes.batchnorm import BatchNorm as BN

from .attrs import ID, LOWER, PREFIX, SUFFIX, SHAPE, TAG, DEP
from ._ml import Tok2Vec, flatten, get_col, doc2feats



class TokenVectorEncoder(object):
    '''Assign position-sensitive vectors to tokens, using a CNN or RNN.'''

    @classmethod
    def Model(cls, width=128, embed_size=5000, **cfg):
        return Tok2Vec(width, embed_size, preprocess=False)

    def __init__(self, vocab, model=True, **cfg):
        self.vocab = vocab
        self.doc2feats = doc2feats()
        self.model = self.Model() if model is True else model
        if self.model not in (None, False):
            self.tagger = chain(
                            self.model,
                            Softmax(self.vocab.morphology.n_tags,
                                    self.model.nO))

    def pipe(self, docs):
        docs = list(docs)
        self.predict_tags(docs)
        for doc in docs:
            yield doc

    def __call__(self, doc):
        self.predict_tags([doc])

    def begin_update(self, feats, drop=0.):
        tokvecs, bp_tokvecs = self.model.begin_update(feats, drop=drop)
        return tokvecs, bp_tokvecs

    def predict_tags(self, docs, drop=0.):
        cdef Doc doc
        feats = self.doc2feats(docs)
        scores, finish_update = self.tagger.begin_update(feats, drop=drop)
        scores, _ = self.tagger.begin_update(feats, drop=drop)
        idx = 0
        guesses = scores.argmax(axis=1)
        if not isinstance(guesses, numpy.ndarray):
            guesses = guesses.get()
        for i, doc in enumerate(docs):
            tag_ids = guesses[idx:idx+len(doc)]
            for j, tag_id in enumerate(tag_ids):
                doc.vocab.morphology.assign_tag_id(&doc.c[j], tag_id)
                idx += 1

    def update(self, docs_feats, golds, drop=0., sgd=None):
        cdef int i, j, idx
        cdef GoldParse gold
        docs, feats = docs_feats
        scores, finish_update = self.tagger.begin_update(feats, drop=drop)

        tag_index = {tag: i for i, tag in enumerate(docs[0].vocab.morphology.tag_names)}

        idx = 0
        correct = numpy.zeros((scores.shape[0],), dtype='i')
        for gold in golds:
            for tag in gold.tags:
                correct[idx] = tag_index[tag]
                idx += 1
        correct = self.model.ops.xp.array(correct)
        d_scores = scores - to_categorical(correct, nb_classes=scores.shape[1])
        finish_update(d_scores, sgd)


cdef class EntityRecognizer(Parser):
    """
    Annotate named entities on Doc objects.
    """
    TransitionSystem = BiluoPushDown

    feature_templates = get_feature_templates('ner')

    def add_label(self, label):
        Parser.add_label(self, label)
        if isinstance(label, basestring):
            label = self.vocab.strings[label]


cdef class BeamEntityRecognizer(BeamParser):
    """
    Annotate named entities on Doc objects.
    """
    TransitionSystem = BiluoPushDown

    feature_templates = get_feature_templates('ner')

    def add_label(self, label):
        Parser.add_label(self, label)
        if isinstance(label, basestring):
            label = self.vocab.strings[label]


cdef class DependencyParser(Parser):
    TransitionSystem = ArcEager
    feature_templates = get_feature_templates('basic')

    def add_label(self, label):
        Parser.add_label(self, label)
        if isinstance(label, basestring):
            label = self.vocab.strings[label]


cdef class BeamDependencyParser(BeamParser):
    TransitionSystem = ArcEager

    feature_templates = get_feature_templates('basic')

    def add_label(self, label):
        Parser.add_label(self, label)
        if isinstance(label, basestring):
            label = self.vocab.strings[label]


__all__ = ['Tagger', 'DependencyParser', 'EntityRecognizer', 'BeamDependencyParser',
           'BeamEntityRecognizer', 'TokenVectorEnoder']
