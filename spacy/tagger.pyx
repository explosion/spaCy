# cython: profile=True
from os import path
import os
import shutil
import random
import codecs
import gzip
import json
import cython


from thinc.features cimport ConjFeat

NULL_TAG = 0


cdef class Tagger:
    """Assign part-of-speech, named entity or supersense tags, using greedy
    decoding.  The tagger reads its model and configuration from disk.
    """
    def __init__(self, model_dir):
        self.mem = Pool()
        cfg = json.load(path.join(model_dir, 'config.json'))
        templates = cfg['templates']
        self.tag_names = cfg['tag_names']
        self.tag_type = cfg['tag_type']
        self.model = LinearModel(len(self.tag_names))
        if path.exists(path.join(model_dir, 'model')):
            self.model.load(path.join(model_dir, 'model'))
        self.extractor = Extractor(templates, [ConjFeat] * len(templates))

        self._feats = <feat_t*>self.mem.alloc(self.extractor.n+1, sizeof(feat_t))
        self._values = <weight_t*>self.mem.alloc(self.extractor.n+1, sizeof(weight_t))
        self._scores = <weight_t*>self.mem.alloc(len(self.cfg.tags), sizeof(weight_t))
        self._guess = NULL_TAG

    cpdef int set_tags(self, Tokens tokens) except -1:
        """Assign tags to a Tokens object.

        >>> tokens = EN.tokenize(u'An example sentence.')
        >>> assert tokens[0].pos == 'NO_TAG'
        >>> EN.pos_tagger.set_tags(tokens)
        >>> assert tokens[0].pos == 'DT'
        """
        cdef int i
        for i in range(tokens.length):
            tokens.set_tag(i, self.tag_type, self.predict(i, tokens))

    cpdef class_t predict(self, int i, Tokens tokens) except 0:
        """Predict the tag of tokens[i].  The tagger remembers the features and
        prediction, in case you later call tell_answer.

        >>> tokens = EN.tokenize(u'An example sentence.')
        >>> tag = EN.pos_tagger.predict(0, tokens)
        >>> assert tag == EN.pos_tagger.tag_id('DT') == 5
        """
        #if self.tag_type == POS:
        #    _pos_feats.fill_context(self._context, i, tokens)
        self.extractor.extract(self._feats, self._values, self._context, NULL)
        self._guess = self.model.score(self._scores, self._feats, self._values)
        return self._guess

    cpdef int tell_answer(self, class_t gold) except -1:
        """Provide the correct tag for the word the tagger was last asked to predict.
        During Tagger.predict, the tagger remembers the features and prediction
        for the example. These are used to calculate a weight update given the
        correct label.

        >>> tokens = EN.tokenize('An example sentence.')
        >>> guess = EN.pos_tagger.predict(1, tokens)
        >>> JJ = EN.pos_tagger.tag_id('JJ')
        >>> JJ
        7
        >>> EN.pos_tagger.tell_answer(JJ)
        """
        cdef class_t guess = self._guess
        if gold == guess or gold == NULL_TAG:
            self.model.update({})
            return 0
        counts = {guess: {}, gold: {}}
        self.extractor.count(counts[gold], self._feats, 1)
        self.extractor.count(counts[guess], self._feats, -1)
        self.model.update(counts)

    def tag_id(self, object tag_name):
        """Encode tag_name into a tag ID integer."""
        tag_id = self.tag_names.index(tag_name)
        if tag_id == -1:
            tag_id = len(self.tag_names)
            self.tag_names.append(tag_name)
        return tag_id
