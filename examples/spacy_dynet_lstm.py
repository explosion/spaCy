from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

import pathlib
import plac
import random
from collections import Counter
import numpy as np
import os

from collections import defaultdict
from itertools import count

if os.environ.get('DYNET_GPU') == '1':
    import _gdynet as dynet
    from _gdynet import cg
else:
    import dynet
    from dynet import cg


class Vocab:
    def __init__(self, w2i=None):
        if w2i is None: w2i = defaultdict(count(0).next)
        self.w2i = dict(w2i)
        self.i2w = {i:w for w,i in w2i.iteritems()}
    @classmethod
    def from_corpus(cls, corpus):
        w2i = defaultdict(count(0).next)
        for sent in corpus:
            [w2i[word] for word in sent]
        return Vocab(w2i)

    def size(self):
        return len(self.w2i.keys())


def read_data(path):
    with path.open() as file_:
        sent = []
        for line in file_:
            line = line.strip().split()
            if not line:
                if sent:
                    yield sent
                sent = []
            else:
                pieces = line
                w = pieces[1]
                pos = pieces[3]
                sent.append((w, pos))


def get_vocab(train, test):
    words = []
    tags = []
    wc = Counter()
    for s in train:
        for w, p in s:
            words.append(w)
            tags.append(p)
            wc[w] += 1
    words.append("_UNK_")
    #words=[w if wc[w] > 1 else "_UNK_" for w in words]
    tags.append("_START_")

    for s in test:
        for w, p in s:
            words.append(w)
    vw = Vocab.from_corpus([words])
    vt = Vocab.from_corpus([tags])
    return words, tags, wc, vw, vt


class BiTagger(object):
    def __init__(self, vw, vt, nwords, ntags):
        self.vw = vw
        self.vt = vt
        self.nwords = nwords
        self.ntags = ntags

        self.UNK = self.vw.w2i["_UNK_"]

        self._model = dynet.Model()
        self._sgd = dynet.SimpleSGDTrainer(self._model)

        self._E = self._model.add_lookup_parameters((self.nwords, 128))
        self._p_t1 = self._model.add_lookup_parameters((self.ntags, 30))
        
        self._pH = self._model.add_parameters((32, 50*2))
        self._pO = self._model.add_parameters((self.ntags, 32))

        self._fwd_lstm = dynet.LSTMBuilder(1, 128, 50, self._model)
        self._bwd_lstm = dynet.LSTMBuilder(1, 128, 50, self._model)
        self._words_batch = []
        self._tags_batch = []
        self._minibatch_size = 32

    def __call__(self, words):
        dynet.renew_cg()
        word_ids = [self.vw.w2i.get(w, self.UNK) for w in words]
        wembs = [self._E[w] for w in word_ids]
        
        f_state = self._fwd_lstm.initial_state()
        b_state = self._bwd_lstm.initial_state()

        fw = [x.output() for x in f_state.add_inputs(wembs)]
        bw = [x.output() for x in b_state.add_inputs(reversed(wembs))]

        H = dynet.parameter(self._pH)
        O = dynet.parameter(self._pO)
        
        tags = []
        for i, (f, b) in enumerate(zip(fw, reversed(bw))):
            r_t = O * (dynet.tanh(H * dynet.concatenate([f, b])))
            out = dynet.softmax(r_t)
            tags.append(self.vt.i2w[np.argmax(out.npvalue())])
        return tags

    def predict_batch(self, words_batch):
        dynet.renew_cg()
        length = max(len(words) for words in words_batch)
        word_ids = np.zeros((length, len(words_batch)), dtype='int32')
        for j, words in enumerate(words_batch):
            for i, word in enumerate(words):
                word_ids[i, j] = self.vw.w2i.get(word, self.UNK)
        wembs = [dynet.lookup_batch(self._E, word_ids[i]) for i in range(length)]
        
        f_state = self._fwd_lstm.initial_state()
        b_state = self._bwd_lstm.initial_state()

        fw = [x.output() for x in f_state.add_inputs(wembs)]
        bw = [x.output() for x in b_state.add_inputs(reversed(wembs))]

        H = dynet.parameter(self._pH)
        O = dynet.parameter(self._pO)
        
        tags_batch = [[] for _ in range(len(words_batch))]
        for i, (f, b) in enumerate(zip(fw, reversed(bw))):
            r_t = O * (dynet.tanh(H * dynet.concatenate([f, b])))
            out = dynet.softmax(r_t).npvalue()
            for j in range(len(words_batch)):
                tags_batch[j].append(self.vt.i2w[np.argmax(out.T[j])])
        return tags_batch

    def pipe(self, sentences):
        batch = []
        for words in sentences:
            batch.append(words)
            if len(batch) == self._minibatch_size:
                tags_batch = self.predict_batch(batch)
                for words, tags in zip(batch, tags_batch):
                    yield tags
                batch = []

    def update(self, words, tags):
        self._words_batch.append(words)
        self._tags_batch.append(tags)
        if len(self._words_batch) == self._minibatch_size:
             loss = self.update_batch(self._words_batch, self._tags_batch)
             self._words_batch = []
             self._tags_batch = []
        else:
             loss = 0
        return loss
    
    def update_batch(self, words_batch, tags_batch):
        dynet.renew_cg()
        length = max(len(words) for words in words_batch)
        word_ids = np.zeros((length, len(words_batch)), dtype='int32')
        for j, words in enumerate(words_batch):
            for i, word in enumerate(words):
                word_ids[i, j] = self.vw.w2i.get(word, self.UNK)
        tag_ids = np.zeros((length, len(words_batch)), dtype='int32')
        for j, tags in enumerate(tags_batch):
            for i, tag in enumerate(tags):
                tag_ids[i, j] = self.vt.w2i.get(tag, self.UNK)
        wembs = [dynet.lookup_batch(self._E, word_ids[i]) for i in range(length)]
        wembs = [dynet.noise(we, 0.1) for we in wembs]
        
        f_state = self._fwd_lstm.initial_state()
        b_state = self._bwd_lstm.initial_state()

        fw = [x.output() for x in f_state.add_inputs(wembs)]
        bw = [x.output() for x in b_state.add_inputs(reversed(wembs))]

        H = dynet.parameter(self._pH)
        O = dynet.parameter(self._pO)
        
        errs = []
        for i, (f, b) in enumerate(zip(fw, reversed(bw))):
            f_b = dynet.concatenate([f,b])
            r_t = O * (dynet.tanh(H * f_b))
            err = dynet.pickneglogsoftmax_batch(r_t, tag_ids[i])
            errs.append(dynet.sum_batches(err))
        sum_errs = dynet.esum(errs)
        squared = -sum_errs # * sum_errs
        losses = sum_errs.scalar_value()
        sum_errs.backward()
        self._sgd.update()
        return losses


def main(train_loc, dev_loc, model_dir):
    train_loc = pathlib.Path(train_loc)
    dev_loc = pathlib.Path(dev_loc)

    train = list(read_data((train_loc)))
    test = list(read_data(dev_loc))

    words, tags, wc, vw, vt = get_vocab(train, test)

    UNK = vw.w2i["_UNK_"]
    nwords = vw.size()
    ntags  = vt.size()

    tagger = BiTagger(vw, vt, nwords, ntags)

    tagged = loss = 0
 
    for ITER in xrange(1):
        random.shuffle(train)
        for i, s in enumerate(train,1):
            if i % 5000 == 0:
                tagger._sgd.status()
                print(loss / tagged)
                loss = 0
                tagged = 0
            if i % 10000 == 0:
                good = bad = 0.0
                word_sents = [[w for w, t in sent] for sent in test]
                gold_sents = [[t for w, t in sent] for sent in test]
                for words, tags, golds in zip(words, tagger.pipe(words), gold_sents):
                    for go, gu in zip(golds, tags):
                        if go == gu:
                            good += 1 
                        else:
                            bad += 1
                print(good / (good+bad))
            loss += tagger.update([w for w, t in s], [t for w, t in s])
            tagged += len(s)


if __name__ == '__main__':
    plac.call(main)
