from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

import pathlib
import plac
import random
from collections import Counter
import numpy as np

from collections import defaultdict
from itertools import count

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
    UNK = vw.w2i["_UNK_"]
    return words, tags, wc, vw, vt


class BiTagger(object):
    def __init__(self, nwords, ntags):
        self.nwords = nwords
        self.ntags = ntags

        self._model = dynet.Model()
        self._sgd = dynet.SimpleSGDTrainer(self._model)

        self._E = self._model.add_lookup_parameters((self.nwords, 128))
        self._p_t1 = self._model.add_lookup_parameters((self.ntags, 30))
        
        self._pH = self._model.add_parameters((32, 50*2))
        self._pO = self._model.add_parameters((self.ntags, 32))

        self._fwd_lstm = dynet.LSTMBuilder(1, 128, 50, self._model)
        self._bwd_lstm = dynet.LSTMBuilder(1, 128, 50, self._model)

    def __call__(self, doc):
        dynet.renew_cg()
        
        wembs = [self._E[word.rank] for word in doc]
        
        f_state = self._fwd_lstm.initial_state()
        b_state = self._bwd_lstm.initial_state()

        fw = [x.output() for x in f_state.add_inputs(wembs)]
        bw = [x.output() for x in b_state.add_inputs(reversed(wembs))]

        H = dynet.parameter(self._pH)
        O = dynet.parameter(self._pO)
        
        for i, (f, b) in enumerate(zip(fw, reversed(bw))):
            r_t = O * (dynet.tanh(H * dynet.concatenate([f, b])))
            out = dynet.softmax(r_t)
            doc[i].tag = np.argmax(out.npvalue())

    def update(self, doc, gold):
        dynet.renew_cg()
        wembs = [self._E[word.rank] for word in doc]
        wembs = [dynet.noise(we, 0.1) for we in wembs]
        
        f_state = self._fwd_lstm.initial_state()
        b_state = self._bwd_lstm.initial_state()

        fw = [x.output() for x in f_state.add_inputs(wembs)]
        bw = [x.output() for x in b_state.add_inputs(reversed(wembs))]

        H = dynet.parameter(self._pH)
        O = dynet.parameter(self._pO)
        
        errs = []
        for f, b, t in zip(fw, reversed(bw), tags):
            f_b = dynet.concatenate([f,b])
            r_t = O * (dynet.tanh(H * f_b))
            err = dynet.pickneglogsoftmax(r_t, t)
            errs.append(err)

        sum_errs = dynet.esum(errs)
        squared = -sum_errs # * sum_errs
        loss += sum_errs.scalar_value()
        sum_errs.backward()
        sgd.update()


def main(train_loc, dev_loc, model_dir):
    train_loc = pathlib.Path(train_loc)
    dev_loc = pathlib.Path(dev_loc)

    train = list(read_data((train_loc)))
    test = list(read_data(dev_loc))

    tagger = BiTagger(vocab)

    UNK = vw.w2i["_UNK_"]
    nwords = vw.size()
    ntags  = vt.size()

    model = dynet.Model()
    sgd = dynet.SimpleSGDTrainer(model)

    E = model.add_lookup_parameters((nwords, 128))
    p_t1  = model.add_lookup_parameters((ntags, 30))
    
    pH = model.add_parameters((32, 50*2))
    pO = model.add_parameters((ntags, 32))

    builders=[
        dynet.LSTMBuilder(1, 128, 50, model),
        dynet.LSTMBuilder(1, 128, 50, model),
    ]

    tagged = loss = 0
    for ITER in xrange(50):
        random.shuffle(train)
        for i, s in enumerate(train,1):
            if i % 5000 == 0:
                sgd.status()
                print(loss / tagged)
                loss = 0
                tagged = 0
            if i % 10000 == 0:
                good = bad = 0.0
                for sent in test:
                    word_ids = [vw.w2i.get(w, UNK) for w, t in sent]
                    tags = tagger.tag_sent(word_ids)
                    golds = [t for w, t in sent]
                    for go, gu in zip(golds, tags):
                        if go == gu:
                            good += 1 
                        else:
                            bad += 1
                print(good / (good+bad))
            ws = [vw.w2i.get(w, UNK) for w,p in s]
            ps = [vt.w2i[p] for w, p in s]
            model.update(ws, ps)


if __name__ == '__main__':
    plac.call(main)
