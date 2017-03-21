from __future__ import unicode_literals
import plac
import json
import random
import pathlib

from spacy.tokens import Doc
from spacy.syntax.nonproj import PseudoProjectivity
from spacy.language import Language
from spacy.gold import GoldParse
from spacy.tagger import Tagger
from spacy.pipeline import DependencyParser, BeamDependencyParser
from spacy.syntax.parser import get_templates
from spacy.syntax.arc_eager import ArcEager
from spacy.scorer import Scorer
from spacy.language_data.tag_map import TAG_MAP as DEFAULT_TAG_MAP
import spacy.attrs
import io


def read_conllx(loc, n=0):
    with io.open(loc, 'r', encoding='utf8') as file_:
        text = file_.read()
    i = 0
    for sent in text.strip().split('\n\n'):
        lines = sent.strip().split('\n')
        if lines:
            while lines[0].startswith('#'):
                lines.pop(0)
            tokens = []
            for line in lines:
                id_, word, lemma, pos, tag, morph, head, dep, _1, \
                _2 = line.split('\t')
                if '-' in id_ or '.' in id_:
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
            i += 1
            if n >= 1 and i >= n:
                break


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


def main(lang_name, train_loc, dev_loc, model_dir, clusters_loc=None):
    LangClass = spacy.util.get_lang_class(lang_name)
    train_sents = list(read_conllx(train_loc))
    train_sents = PseudoProjectivity.preprocess_training_data(train_sents)

    actions = ArcEager.get_actions(gold_parses=train_sents)
    features = get_templates('basic')

    model_dir = pathlib.Path(model_dir)
    if not model_dir.exists():
        model_dir.mkdir()
    if not (model_dir / 'deps').exists():
        (model_dir / 'deps').mkdir()
    if not (model_dir / 'pos').exists():
        (model_dir / 'pos').mkdir()
    with (model_dir / 'deps' / 'config.json').open('wb') as file_:
        file_.write(
            json.dumps(
                {'pseudoprojective': True, 'labels': actions, 'features': features}).encode('utf8'))

    vocab = LangClass.Defaults.create_vocab()
    if not (model_dir / 'vocab').exists():
        (model_dir / 'vocab').mkdir()
    else:
        if (model_dir / 'vocab' / 'strings.json').exists():
            with (model_dir / 'vocab' / 'strings.json').open() as file_:
                vocab.strings.load(file_)
            if (model_dir / 'vocab' / 'lexemes.bin').exists():
                vocab.load_lexemes(model_dir / 'vocab' / 'lexemes.bin')

    if clusters_loc is not None:
        clusters_loc = pathlib.Path(clusters_loc)
        with clusters_loc.open() as file_:
            for line in file_:
                try:
                    cluster, word, freq = line.split()
                except ValueError:
                    continue
                lex = vocab[word]
                lex.cluster = int(cluster[::-1], 2)
    # Populate vocab
    for _, doc_sents in train_sents:
        for (ids, words, tags, heads, deps, ner), _ in doc_sents:
            for word in words:
                _ = vocab[word]
            for dep in deps:
                _ = vocab[dep]
            for tag in tags:
                _ = vocab[tag]
            if vocab.morphology.tag_map:
                for tag in tags:
                    assert tag in vocab.morphology.tag_map, repr(tag)
    tagger = Tagger(vocab)
    parser = DependencyParser(vocab, actions=actions, features=features, L1=0.0)

    for itn in range(30):
        loss = 0.
        for _, doc_sents in train_sents:
            for (ids, words, tags, heads, deps, ner), _ in doc_sents:
                doc = Doc(vocab, words=words)
                gold = GoldParse(doc, tags=tags, heads=heads, deps=deps)
                tagger(doc)
                loss += parser.update(doc, gold, itn=itn)
                doc = Doc(vocab, words=words)
                tagger.update(doc, gold)
        random.shuffle(train_sents)
        scorer = score_model(vocab, tagger, parser, read_conllx(dev_loc))
        print('%d:\t%.3f\t%.3f\t%.3f' % (itn, loss, scorer.uas, scorer.tags_acc))
    nlp = LangClass(vocab=vocab, tagger=tagger, parser=parser)
    nlp.end_training(model_dir)
    scorer = score_model(vocab, tagger, parser, read_conllx(dev_loc))
    print('%d:\t%.3f\t%.3f\t%.3f' % (itn, scorer.uas, scorer.las, scorer.tags_acc))


if __name__ == '__main__':
    plac.call(main)
