import plac
import json
from os import path
import shutil
import os
import random
import io

from spacy.syntax.util import Config
from spacy.gold import GoldParse
from spacy.tokenizer import Tokenizer
from spacy.vocab import Vocab
from spacy.tagger import Tagger
from spacy.syntax.parser import Parser
from spacy.syntax.arc_eager import ArcEager
from spacy.syntax.parser import get_templates
from spacy.scorer import Scorer
import spacy.attrs
from spacy.syntax.nonproj import PseudoProjectivity

from spacy.syntax._parse_features import *

from spacy.language import Language

try:
    from codecs import open
except ImportError:
    pass


features = [
    (S2W,),
    (S1W, ),
    (S1rW,),
    (S0lW, ),
    (S0l2W, ),
    (S0W, ),
    (S0r2W, ),
    (S0rW, ),
    (N0l2W, ),
    (N0lW, ),
    (N0W, ),
    (N1W, ),
    (N2W, )
]

slots = [0] * len(features)

features += [
    (S2p,),
    (S1p, ),
    (S1rp,),
    (S0lp,),
    (S0l2p,),
    (S0p, ),
    (S0r2p, ),
    (S0rp, ),
    (N0l2p, ),
    (N0lp, ),
    (N0p, ),
    (N1p, ),
    (N2p, )
]

slots += [1] * (len(features) - len(slots))

features += [
    (S2L,),
    (S1L,),
    (S1rL,),
    (S0lL,),
    (S0l2L,),
    (S0L,),
    (S0rL,),
    (S0r2L,),
    (N0l2L,),
    (N0lL,),
]
slots += [2] * (len(features) - len(slots))
#
#features += [(S2p, S1p), (S1p, S0p)]
#slots += [3, 3]
#features += [(S0p, N0p)]
#slots += [4]
#    (S0l2p, S0l2L, S0lp, S0l2L),
#    (N0l2p, N0l2L, N0lp, N0lL),
#    (S1p, S1rp, S1rL),
#    (S0p, S0rp, S0rL),
#)




class TreebankParser(object):
    @staticmethod
    def setup_model_dir(model_dir, labels, vector_widths=(300,), slots=(0,),
            hidden_layers=(300, 300),
            feat_set='basic', seed=0, update_step='sgd', eta=0.005, rho=0.0):
        dep_model_dir = path.join(model_dir, 'deps')
        pos_model_dir = path.join(model_dir, 'pos')
        if path.exists(dep_model_dir):
            shutil.rmtree(dep_model_dir)
        if path.exists(pos_model_dir):
            shutil.rmtree(pos_model_dir)
        os.mkdir(dep_model_dir)
        os.mkdir(pos_model_dir)

        Config.write(dep_model_dir, 'config', model='neural', feat_set=feat_set,
                     seed=seed, labels=labels, vector_widths=vector_widths, slots=slots,
                     hidden_layers=hidden_layers, update_step=update_step, eta=eta, rho=rho)

    @classmethod
    def from_dir(cls, tag_map, model_dir):
        vocab = Vocab.load(model_dir, get_lex_attr=Language.default_lex_attrs())
        vocab.get_lex_attr[spacy.attrs.LANG] = lambda _: 0
        tokenizer = Tokenizer(vocab, {}, None, None, None)
        tagger = Tagger.blank(vocab, Tagger.default_templates())

        cfg = Config.read(path.join(model_dir, 'deps'), 'config')
        parser = Parser.from_dir(path.join(model_dir, 'deps'), vocab.strings, ArcEager)
        return cls(vocab, tokenizer, tagger, parser)

    def __init__(self, vocab, tokenizer, tagger, parser):
        self.vocab = vocab
        self.tokenizer = tokenizer
        self.tagger = tagger
        self.parser = parser

    def train(self, words, tags, heads, deps):
        tokens = self.tokenizer.tokens_from_list(list(words))
        ids = range(len(words))
        ner = ['O'] * len(words)
        gold = GoldParse(tokens, ((ids, words, tags, heads, deps, ner)))
        self.tagger.tag_from_strings(tokens, tags)
        loss = self.parser.train(tokens, gold)
        PseudoProjectivity.deprojectivize(tokens)
        return loss

    def __call__(self, words, tags=None):
        tokens = self.tokenizer.tokens_from_list(list(words))
        if tags is None:
            self.tagger(tokens)
        else:
            self.tagger.tag_from_strings(tokens, tags)
        self.parser(tokens)
        PseudoProjectivity.deprojectivize(tokens)
        return tokens

    def end_training(self, data_dir):
        self.parser.model.end_training()
        self.parser.model.dump(path.join(data_dir, 'deps', 'model'))
        self.tagger.model.end_training()
        self.tagger.model.dump(path.join(data_dir, 'pos', 'model'))
        strings_loc = path.join(data_dir, 'vocab', 'strings.json')
        with io.open(strings_loc, 'w', encoding='utf8') as file_:
            self.vocab.strings.dump(file_)
        self.vocab.dump(path.join(data_dir, 'vocab', 'lexemes.bin'))


def read_conllx(loc):
    with open(loc, 'r', 'utf8') as file_:
        text = file_.read()
    for sent in text.strip().split('\n\n'):
        lines = sent.strip().split('\n')
        if lines:
            while lines[0].startswith('#'):
                lines.pop(0)
            tokens = []
            for line in lines:
                id_, word, lemma, pos, tag, morph, head, dep, _1, _2 = line.split()
                if '-' in id_:
                    continue
                id_ = int(id_) - 1
                head = (int(head) - 1) if head != '0' else id_
                dep = 'ROOT' if dep == 'root' else dep
                tokens.append([id_, word, tag, head, dep, 'O'])
            tuples = [list(el) for el in zip(*tokens)]
            yield (None, [(tuples, [])])


def score_model(nlp, gold_docs, verbose=False):
    scorer = Scorer()
    for _, gold_doc in gold_docs:
        for annot_tuples, _ in gold_doc:
            tokens = nlp(list(annot_tuples[1]), tags=list(annot_tuples[2]))
            gold = GoldParse(tokens, annot_tuples)
            scorer.score(tokens, gold, verbose=verbose)
    return scorer


@plac.annotations(
    n_iter=("Number of training iterations", "option", "i", int),
)
def main(train_loc, dev_loc, model_dir, tag_map_loc, n_iter=10):
    with open(tag_map_loc) as file_:
        tag_map = json.loads(file_.read())
    train_sents = list(read_conllx(train_loc))
    train_sents = PseudoProjectivity.preprocess_training_data(train_sents)
    dev_sents = list(read_conllx(dev_loc))

    labels = ArcEager.get_labels(train_sents)

    TreebankParser.setup_model_dir(model_dir, labels,
        feat_set=features, vector_widths=(10,10,10,30,30), slots=slots,
        hidden_layers=(100,100,100), update_step='adam')
    
    nlp = TreebankParser.from_dir(tag_map, model_dir)
    nlp.parser.model.rho = 1e-4
    print(nlp.parser.model.widths)

    for itn in range(n_iter):
        loss = 0.0
        for _, doc_sents in train_sents:
            for (ids, words, tags, heads, deps, ner), _ in doc_sents:
                loss += nlp.train(words, tags, heads, deps)
        random.shuffle(train_sents)
        scorer = score_model(nlp, dev_sents)
        print('%d:\t%.3f\t%.3f\t%.3f' % (itn, loss, scorer.uas, scorer.tags_acc))
        print(nlp.parser.model.mem.size)
    nlp.end_training(model_dir)
    scorer = score_model(nlp, read_conllx(dev_loc))
    print('Dev: %.3f\t%.3f\t%.3f' % (scorer.uas, scorer.las, scorer.tags_acc))
 

if __name__ == '__main__':
    plac.call(main)
