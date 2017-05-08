# coding: utf8
from __future__ import unicode_literals

from thinc.api import chain, layerize, with_getitem
from thinc.neural import Model, Softmax

from .syntax.parser cimport Parser
#from .syntax.beam_parser cimport BeamParser
from .syntax.ner cimport BiluoPushDown
from .syntax.arc_eager cimport ArcEager
from .tagger import Tagger
from ._ml import build_tok2vec

# TODO: The disorganization here is pretty embarrassing. At least it's only
# internals.
from .syntax.parser import get_templates as get_feature_templates
from .attrs import DEP, ENT_TYPE


class TokenVectorEncoder(object):
    '''Assign position-sensitive vectors to tokens, using a CNN or RNN.'''
    def __init__(self, vocab, **cfg):
        self.vocab = vocab
        self.model = build_tok2vec(vocab.lang, **cfg)
        self.tagger = chain(
                        self.model,
                        Softmax(self.vocab.morphology.n_tags))

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
        loss = 0.0
        idx = 0
        for i, gold in enumerate(golds):
            for j, tag in enumerate(gold.tags):
                tag_id = docs[0].vocab.morphology.tag_names.index(tag)
                losses[idx, tag_id] -= 1.0
                loss += 1-scores[idx, tag_id]
                idx += 1
        finish_update(losses, sgd)
        return loss


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
