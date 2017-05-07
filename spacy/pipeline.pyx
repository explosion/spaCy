# coding: utf8
from __future__ import unicode_literals

from thinc.api import chain, layerize, with_getitem
from thinc.neural import Model, Softmax
import numpy

from .syntax.parser cimport Parser
#from .syntax.beam_parser cimport BeamParser
from .syntax.ner cimport BiluoPushDown
from .syntax.arc_eager cimport ArcEager
from .tagger import Tagger
from ._ml import build_tok2vec, flatten

# TODO: The disorganization here is pretty embarrassing. At least it's only
# internals.
from .syntax.parser import get_templates as get_feature_templates
from .attrs import DEP, ENT_TYPE


class TokenVectorEncoder(object):
    '''Assign position-sensitive vectors to tokens, using a CNN or RNN.'''
    def __init__(self, vocab, **cfg):
        self.vocab = vocab
        self.model = build_tok2vec(vocab.lang, 64, **cfg)
        self.tagger = chain(
                        self.model,
                        flatten,
                        Softmax(self.vocab.morphology.n_tags, 64))

    def __call__(self, doc):
        doc.tensor = self.model([doc])[0]

    def begin_update(self, docs, drop=0.):
        tensors, bp_tensors = self.model.begin_update(docs, drop=drop)
        for i, doc in enumerate(docs):
            doc.tensor = tensors[i]
        return tensors, bp_tensors

    def update(self, docs, golds, drop=0., sgd=None):
        scores, finish_update = self.tagger.begin_update(docs, drop=drop)
        losses = scores.copy()
        idx = 0
        for i, gold in enumerate(golds):
            ids = numpy.zeros((len(gold),), dtype='i')
            start = idx
            for j, tag in enumerate(gold.tags):
                ids[j] = docs[0].vocab.morphology.tag_names.index(tag)
                idx += 1
            self.tagger.ops.xp.scatter_add(losses[start:idx], ids, -1.0)
        finish_update(losses, sgd)


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
        # Set label into serializer. Super hacky :(
        for attr, freqs in self.vocab.serializer_freqs:
            if attr == ENT_TYPE and label not in freqs:
                freqs.append([label, 1])
        self.vocab._serializer = None

#
#cdef class BeamEntityRecognizer(BeamParser):
#    """
#    Annotate named entities on Doc objects.
#    """
#    TransitionSystem = BiluoPushDown
#
#    feature_templates = get_feature_templates('ner')
#
#    def add_label(self, label):
#        Parser.add_label(self, label)
#        if isinstance(label, basestring):
#            label = self.vocab.strings[label]
#        # Set label into serializer. Super hacky :(
#        for attr, freqs in self.vocab.serializer_freqs:
#            if attr == ENT_TYPE and label not in freqs:
#                freqs.append([label, 1])
#        self.vocab._serializer = None
#

cdef class DependencyParser(Parser):
    TransitionSystem = ArcEager

    feature_templates = get_feature_templates('basic')

    def add_label(self, label):
        Parser.add_label(self, label)
        if isinstance(label, basestring):
            label = self.vocab.strings[label]
        for attr, freqs in self.vocab.serializer_freqs:
            if attr == DEP and label not in freqs:
                freqs.append([label, 1])
        # Super hacky :(
        self.vocab._serializer = None

#
#cdef class BeamDependencyParser(BeamParser):
#    TransitionSystem = ArcEager
#
#    feature_templates = get_feature_templates('basic')
#
#    def add_label(self, label):
#        Parser.add_label(self, label)
#        if isinstance(label, basestring):
#            label = self.vocab.strings[label]
#        for attr, freqs in self.vocab.serializer_freqs:
#            if attr == DEP and label not in freqs:
#                freqs.append([label, 1])
#        # Super hacky :(
#        self.vocab._serializer = None
#

#__all__ = [Tagger, DependencyParser, EntityRecognizer, BeamDependencyParser, BeamEntityRecognizer]
__all__ = [Tagger, DependencyParser, EntityRecognizer]
