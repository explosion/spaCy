from __future__ import unicode_literals
import plac
import json
from os import path
import shutil
import os
import random
import io
import pathlib

from spacy.tokens import Doc
from spacy.syntax.nonproj import PseudoProjectivity
from spacy.language import Language
from spacy.gold import GoldParse
from spacy.vocab import Vocab
from spacy.tagger import Tagger
from spacy.pipeline import DependencyParser
from spacy.syntax.parser import get_templates
from spacy.syntax.arc_eager import ArcEager
from spacy.scorer import Scorer
from spacy.language_data.tag_map import TAG_MAP as DEFAULT_TAG_MAP
import spacy.attrs
import io



def read_conllx(loc):
    with io.open(loc, 'r', encoding='utf8') as file_:
        text = file_.read()
    for sent in text.strip().split('\n\n'):
        lines = sent.strip().split('\n')
        if lines:
            while lines[0].startswith('#'):
                lines.pop(0)
            tokens = []
            for line in lines:
                id_, word, lemma, tag, pos, morph, head, dep, _1, _2 = line.split()
                if '-' in id_:
                    continue
                try:
                    id_ = int(id_) - 1
                    head = (int(head) - 1) if head != '0' else id_
                    dep = 'ROOT' if dep == 'root' else dep
                    tokens.append((id_, word, tag, head, dep, 'O'))
                except:
                    print(line)
                    raise
            tuples = [list(t) for t in zip(*tokens)]
            yield (None, [[tuples, []]])


def score_model(vocab, tagger, parser, gold_docs, verbose=False):
    scorer = Scorer()
    for _, gold_doc in gold_docs:
        for (ids, words, tags, heads, deps, entities), _ in gold_doc:
            doc = Doc(vocab, words=words)
            tagger(doc)
            parser(doc)
            PseudoProjectivity.deprojectivize(doc)
            gold = GoldParse(doc, tags=tags, heads=heads, deps=deps)
            scorer.score(doc, gold, verbose=verbose)
    return scorer


def main(train_loc, dev_loc, model_dir, tag_map_loc=None):
    if tag_map_loc:
        with open(tag_map_loc) as file_:
            tag_map = json.loads(file_.read())
    else:
        tag_map = DEFAULT_TAG_MAP
    train_sents = list(read_conllx(train_loc))
    train_sents = PseudoProjectivity.preprocess_training_data(train_sents)

    actions = ArcEager.get_actions(gold_parses=train_sents)
    features = get_templates('basic')
    
    model_dir = pathlib.Path(model_dir)
    if not (model_dir / 'deps').exists():
        (model_dir / 'deps').mkdir()
    with (model_dir / 'deps' / 'config.json').open('wb') as file_:
        file_.write(
            json.dumps(
                {'pseudoprojective': True, 'labels': actions, 'features': features}).encode('utf8'))
    vocab = Vocab(lex_attr_getters=Language.Defaults.lex_attr_getters, tag_map=tag_map)
    # Populate vocab
    for _, doc_sents in train_sents:
        for (ids, words, tags, heads, deps, ner), _ in doc_sents:
            for word in words:
                _ = vocab[word]
            for dep in deps:
                _ = vocab[dep]
            for tag in tags:
                _ = vocab[tag]
            if tag_map:
                for tag in tags:
                    assert tag in tag_map, repr(tag)
    tagger = Tagger(vocab, tag_map=tag_map)
    parser = DependencyParser(vocab, actions=actions, features=features)
    
    for itn in range(15):
        for _, doc_sents in train_sents:
            for (ids, words, tags, heads, deps, ner), _ in doc_sents:
                doc = Doc(vocab, words=words)
                gold = GoldParse(doc, tags=tags, heads=heads, deps=deps)
                tagger(doc)
                parser.update(doc, gold)
                doc = Doc(vocab, words=words)
                tagger.update(doc, gold)
        random.shuffle(train_sents)
        scorer = score_model(vocab, tagger, parser, read_conllx(dev_loc))
        print('%d:\t%.3f\t%.3f' % (itn, scorer.uas, scorer.tags_acc))
    nlp = Language(vocab=vocab, tagger=tagger, parser=parser)
    nlp.end_training(model_dir)
    scorer = score_model(vocab, tagger, parser, read_conllx(dev_loc))
    print('%d:\t%.3f\t%.3f\t%.3f' % (itn, scorer.uas, scorer.las, scorer.tags_acc))
 

if __name__ == '__main__':
    plac.call(main)
