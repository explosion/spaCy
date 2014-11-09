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


from .context cimport fill_context
from .context cimport N_FIELDS

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


def train(train_sents, model_dir, nr_iter=10):
    cdef Tokens tokens
    tagger = Tagger(model_dir)
    for _ in range(nr_iter):
        n_corr = 0
        total = 0
        for tokens, golds in train_sents:
            assert len(tokens) == len(golds), [t.string for t in tokens]
            for i in range(tokens.length):
                if tagger.tag_type == POS:
                    gold = _get_gold_pos(i, golds, tokens.pos)
                elif tagger.tag_type == ENTITY:
                    gold = _get_gold_ner(i, golds, tokens.ner)
                guess = tagger.predict(i, tokens)
                tokens.set_tag(i, tagger.tag_type, guess)
                if gold is not None:
                    tagger.tell_answer(gold)
                    total += 1
                    n_corr += guess in gold
                #print('%s\t%d\t%d' % (tokens[i].string, guess, gold))
        print('%.4f' % ((n_corr / total) * 100))
        random.shuffle(train_sents)
    tagger.model.end_training()
    tagger.model.dump(path.join(model_dir, 'model'))


cdef object _get_gold_pos(i, golds, int* pred):
    if golds[i] == 0:
        return None
    else:
        return [golds[i]]


cdef object _get_gold_ner(i, golds, int* ner):
    if golds[i] == 0:
        return None
    else:
        return [golds[i]]


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
        self.model = LinearModel(len(self.tag_names))
        if path.exists(path.join(model_dir, 'model')):
            self.model.load(path.join(model_dir, 'model'))

        self._context = <atom_t*>self.mem.alloc(N_FIELDS, sizeof(atom_t))
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
        fill_context(self._context, i, tokens)
        self.extractor.extract(self._feats, self._values, self._context, NULL)
        self._guess = self.model.score(self._scores, self._feats, self._values)
        return self._guess

    cpdef int tell_answer(self, list golds) except -1:
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
        if guess in golds:
            self.model.update({})
            return 0
        best_gold = golds[0]
        best_score = self._scores[best_gold-1]
        for gold in golds[1:]:
            if self._scores[gold-1] > best_gold:
                best_score = self._scores[best_gold-1]
                best_gold = gold
        counts = {guess: {}, best_gold: {}}
        self.extractor.count(counts[best_gold], self._feats, 1)
        self.extractor.count(counts[guess], self._feats, -1)
        self.model.update(counts)

    def tag_id(self, object tag_name):
        """Encode tag_name into a tag ID integer."""
        tag_id = self.tag_names.index(tag_name)
        if tag_id == -1:
            tag_id = len(self.tag_names)
            self.tag_names.append(tag_name)
        return tag_id
