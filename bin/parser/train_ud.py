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

from spacy.language import Language

from spacy.tagger import W_orth

TAGGER_TEMPLATES = (
    (W_orth,),
)

try:
    from codecs import open
except ImportError:
    pass


class TreebankParser(object):
    @staticmethod
    def setup_model_dir(model_dir, labels, templates, feat_set='basic', seed=0):
        dep_model_dir = path.join(model_dir, 'deps')
        pos_model_dir = path.join(model_dir, 'pos')
        if path.exists(dep_model_dir):
            shutil.rmtree(dep_model_dir)
        if path.exists(pos_model_dir):
            shutil.rmtree(pos_model_dir)
        os.mkdir(dep_model_dir)
        os.mkdir(pos_model_dir)

        Config.write(dep_model_dir, 'config', features=feat_set, seed=seed,
                     labels=labels)

    @classmethod
    def from_dir(cls, tag_map, model_dir):
        vocab = Vocab(tag_map=tag_map, get_lex_attr=Language.default_lex_attrs())
        vocab.get_lex_attr[spacy.attrs.LANG] = lambda _: 0
        tokenizer = Tokenizer(vocab, {}, None, None, None)
        tagger = Tagger.blank(vocab, TAGGER_TEMPLATES)

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
        self.tagger.train(tokens, tags)
        
        tokens = self.tokenizer.tokens_from_list(list(words))
        ids = range(len(words))
        ner = ['O'] * len(words)
        gold = GoldParse(tokens, ((ids, words, tags, heads, deps, ner)),
                         make_projective=False)
        self.tagger(tokens)
        if gold.is_projective:
            try:
                self.parser.train(tokens, gold)
            except:
                for id_, word, head, dep in zip(ids, words, heads, deps):
                    print(id_, word, head, dep)
                raise

    def __call__(self, words, tags=None):
        tokens = self.tokenizer.tokens_from_list(list(words))
        if tags is None:
            self.tagger(tokens)
        else:
            self.tagger.tag_from_strings(tokens, tags)
        self.parser(tokens)
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
                tokens.append((id_, word, tag, head, dep, 'O'))
            tuples = zip(*tokens)
            yield (None, [(tuples, [])])


def score_model(nlp, gold_docs, verbose=False):
    scorer = Scorer()
    for _, gold_doc in gold_docs:
        for annot_tuples, _ in gold_doc:
            tokens = nlp(list(annot_tuples[1]), tags=list(annot_tuples[2]))
            gold = GoldParse(tokens, annot_tuples)
            scorer.score(tokens, gold, verbose=verbose)
    return scorer


def main(train_loc, dev_loc, model_dir, tag_map_loc):
    with open(tag_map_loc) as file_:
        tag_map = json.loads(file_.read())
    train_sents = list(read_conllx(train_loc))
    labels = ArcEager.get_labels(train_sents)
    templates = get_templates('basic')

    TreebankParser.setup_model_dir(model_dir, labels, templates)
    
    nlp = TreebankParser.from_dir(tag_map, model_dir)

    for itn in range(15):
        for _, doc_sents in train_sents:
            for (ids, words, tags, heads, deps, ner), _ in doc_sents:
                nlp.train(words, tags, heads, deps)
        random.shuffle(train_sents)
        scorer = score_model(nlp, read_conllx(dev_loc))
        print('%d:\t%.3f\t%.3f' % (itn, scorer.uas, scorer.tags_acc))
    nlp.end_training(model_dir)
    scorer = score_model(nlp, read_conllx(dev_loc))
    print('%d:\t%.3f\t%.3f\t%.3f' % (itn, scorer.uas, scorer.las, scorer.tags_acc))
 

if __name__ == '__main__':
    plac.call(main)
