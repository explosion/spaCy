# cython: profile=True
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from os import path
import os
import shutil
import random
import json
import cython

from .pos_feats cimport fill_context as pos_fill_context
from .pos_feats cimport CONTEXT_SIZE as POS_CONTEXT_SIZE

from thinc.features cimport ConjFeat


NULL_TAG = 0


def setup_model_dir(tag_type, tag_names, templates, model_dir):
    if path.exists(model_dir):
        shutil.rmtree(model_dir)
    os.mkdir(model_dir)
    config = {
        'tag_type': tag_type,
        'templates': templates,
        'tag_names': tag_names,
    }
    with open(path.join(model_dir, 'config.json'), 'w') as file_:
        json.dump(config, file_)


def train(train_sents, model_dir, nr_iter=5):
    tagger = Tagger(model_dir)
    for _ in range(nr_iter):
        n_corr = 0
        total = 0
        for tokens, golds in train_sents:
            assert len(tokens) == len(golds), [t.string for t in tokens]
            for i, gold in enumerate(golds):
                guess = tagger.predict(i, tokens)
                tokens.set_tag(i, tagger.tag_type, guess)
                tagger.tell_answer(gold)
                if gold != NULL_TAG:
                    total += 1
                    n_corr += guess == gold
        print('%.4f' % ((n_corr / total) * 100))
        random.shuffle(train_sents)
    tagger.model.end_training()
    tagger.model.dump(path.join(model_dir, 'model'), freq_thresh=10)


def evaluate(tagger, sents):
    n_corr = 0
    total = 0
    for tokens, golds in sents:
        for i, gold in enumerate(golds):
            guess = tagger.predict(i, tokens)
            tokens.set_tag(i, tagger.tag_type, guess)
            if gold != NULL_TAG:
                total += 1
                n_corr += guess == gold
    return n_corr / total


cdef class Tagger:
    """Assign part-of-speech, named entity or supersense tags, using greedy
    decoding.  The tagger reads its model and configuration from disk.
    """
    def __init__(self, model_dir):
        self.mem = Pool()
        cfg = json.load(open(path.join(model_dir, 'config.json')))
        templates = cfg['templates']
        self.tag_names = cfg['tag_names']
        self.tag_type = cfg['tag_type']
        self.extractor = Extractor(templates, [ConjFeat] * len(templates))
        self.model = LinearModel(len(self.tag_names), self.extractor.n)
        print("Load tagger model")
        if path.exists(path.join(model_dir, 'model')):
            self.model.load(path.join(model_dir, 'model'))
        print("Done")

        if self.tag_type == POS:
            n_context = POS_CONTEXT_SIZE
        self._context = <atom_t*>self.mem.alloc(n_context, sizeof(atom_t))
        self._feats = <feat_t*>self.mem.alloc(self.extractor.n+1, sizeof(feat_t))
        self._values = <weight_t*>self.mem.alloc(self.extractor.n+1, sizeof(weight_t))
        self._scores = <weight_t*>self.mem.alloc(self.model.nr_class, sizeof(weight_t))
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
        if self.tag_type == POS:
            pos_fill_context(self._context, i, tokens)
        else:
            raise StandardError
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
