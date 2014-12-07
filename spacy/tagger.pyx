# cython: profile=True
from __future__ import unicode_literals
from __future__ import division

from .context cimport fill_context
from .context cimport N_FIELDS

from os import path
import os
import shutil
import random
import json
import cython

from thinc.features cimport Feature, count_feats


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
    cdef Tagger tagger = Tagger(model_dir)
    cdef int i
    for _ in range(nr_iter):
        n_corr = 0
        total = 0
        for tokens, golds in train_sents:
            assert len(tokens) == len(golds), [t.string for t in tokens]
            for i in range(tokens.length):
                if tagger.tag_type == POS:
                    gold = _get_gold_pos(i, golds)
                else:
                    raise StandardError

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


cdef object _get_gold_pos(i, golds):
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
        self.extractor = Extractor(templates)
        self.model = LinearModel(len(self.tag_names))
        if path.exists(path.join(model_dir, 'model')):
            self.model.load(path.join(model_dir, 'model'))

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

    cpdef class_t predict(self, int i, Tokens tokens, object golds=None) except 0:
        """Predict the tag of tokens[i].  The tagger remembers the features and
        prediction, in case you later call tell_answer.

        >>> tokens = EN.tokenize(u'An example sentence.')
        >>> tag = EN.pos_tagger.predict(0, tokens)
        >>> assert tag == EN.pos_tagger.tag_id('DT') == 5
        """
        cdef int n_feats
        cdef atom_t[N_FIELDS] context
        print sizeof(context)
        fill_context(context, i, tokens.data)
        cdef Feature* feats = self.extractor.get_feats(context, &n_feats)
        cdef weight_t* scores = self.model.get_scores(feats, n_feats)
        cdef class_t guess = _arg_max(scores, self.nr_class)
        if golds is not None and guess not in golds:
            best = _arg_max_among(scores, golds)
            counts = {}
            count_feats(counts[guess], feats, n_feats, -1)
            count_feats(counts[best], feats, n_feats, 1)
            self.model.update(counts)
        return guess

    def tag_id(self, object tag_name):
        """Encode tag_name into a tag ID integer."""
        tag_id = self.tag_names.index(tag_name)
        if tag_id == -1:
            tag_id = len(self.tag_names)
            self.tag_names.append(tag_name)
        return tag_id


cdef class_t _arg_max(weight_t* scores, int n_classes):
    cdef int best = 0
    cdef weight_t score = scores[best]
    cdef int i
    for i in range(1, n_classes):
        if scores[i] > score:
            score = scores[i]
            best = i
    return best


cdef class_t _arg_max_among(weight_t* scores, list classes):
    cdef int best = classes[0]
    cdef weight_t score = scores[best]
    cdef class_t clas
    for clas in classes:
        if scores[clas] > score:
            score = scores[clas]
            best = clas
    return best
