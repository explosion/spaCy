from __future__ import unicode_literals, print_function
import plac
import json
import random
import pathlib

from spacy.tokens import Doc
from spacy.syntax.nonproj import PseudoProjectivity
from spacy.language import Language
from spacy.gold import GoldParse
from spacy.tagger import Tagger
from spacy.pipeline import DependencyParser, TokenVectorEncoder
from spacy.syntax.parser import get_templates
from spacy.syntax.arc_eager import ArcEager
from spacy.scorer import Scorer
from spacy.language_data.tag_map import TAG_MAP as DEFAULT_TAG_MAP
import spacy.attrs
import io
from thinc.neural.ops import CupyOps
from thinc.neural import Model
from spacy.es import Spanish
from spacy.attrs import POS


from thinc.neural import Model


try:
    import cupy
    from thinc.neural.ops import CupyOps
except:
    cupy = None


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
                    dep = 'ROOT' if dep == 'root' else dep #'unlabelled'
                    tag = pos+'__'+dep+'__'+morph
                    Spanish.Defaults.tag_map[tag] = {POS: pos}
                    tokens.append((id_, word, tag, head, dep, 'O'))
                except:
                    raise
            tuples = [list(t) for t in zip(*tokens)]
            yield (None, [[tuples, []]])
            i += 1
            if n >= 1 and i >= n:
                break


def score_model(vocab, encoder, parser, Xs, ys, verbose=False):
    scorer = Scorer()
    correct = 0.
    total = 0.
    for doc, gold in zip(Xs, ys):
        doc = Doc(vocab, words=[w.text for w in doc])
        encoder(doc)
        parser(doc)
        PseudoProjectivity.deprojectivize(doc)
        scorer.score(doc, gold, verbose=verbose)
        for token, tag in zip(doc, gold.tags):
            if '_' in token.tag_:
                univ_guess, _ = token.tag_.split('_', 1)
            else:
                univ_guess = ''
            univ_truth, _ = tag.split('_', 1)
            correct += univ_guess == univ_truth
            total += 1
    return scorer


def organize_data(vocab, train_sents):
    Xs = []
    ys = []
    for _, doc_sents in train_sents:
        for (ids, words, tags, heads, deps, ner), _ in doc_sents:
            doc = Doc(vocab, words=words)
            gold = GoldParse(doc, tags=tags, heads=heads, deps=deps)
            Xs.append(doc)
            ys.append(gold)
    return Xs, ys


def main(lang_name, train_loc, dev_loc, model_dir, clusters_loc=None):
    LangClass = spacy.util.get_lang_class(lang_name)
    train_sents = list(read_conllx(train_loc))
    dev_sents = list(read_conllx(dev_loc))
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
                    vocab.morphology.tag_map[tag] = {POS: tag.split('__', 1)[0]}
    tagger = Tagger(vocab)
    encoder = TokenVectorEncoder(vocab, width=64)
    parser = DependencyParser(vocab, actions=actions, features=features, L1=0.0)

    Xs, ys = organize_data(vocab, train_sents)
    dev_Xs, dev_ys = organize_data(vocab, dev_sents)
    with encoder.model.begin_training(Xs[:100], ys[:100]) as (trainer, optimizer):
        docs = list(Xs)
        for doc in docs:
            encoder(doc)
        nn_loss = [0.]
        def track_progress():
            with encoder.tagger.use_params(optimizer.averages):
                with parser.model.use_params(optimizer.averages):
                    scorer = score_model(vocab, encoder, parser, dev_Xs, dev_ys)
            itn = len(nn_loss)
            print('%d:\t%.3f\t%.3f\t%.3f' % (itn, nn_loss[-1], scorer.uas, scorer.tags_acc))
            nn_loss.append(0.)
        track_progress()
        trainer.each_epoch.append(track_progress)
        trainer.batch_size = 24
        trainer.nb_epoch = 40
        for docs, golds in trainer.iterate(Xs, ys, progress_bar=True):
            docs = [Doc(vocab, words=[w.text for w in doc]) for doc in docs]
            tokvecs, upd_tokvecs = encoder.begin_update(docs)
            for doc, tokvec in zip(docs, tokvecs):
                doc.tensor = tokvec
            d_tokvecs = parser.update(docs, golds, sgd=optimizer)
            upd_tokvecs(d_tokvecs, sgd=optimizer)
            encoder.update(docs, golds, sgd=optimizer)
    nlp = LangClass(vocab=vocab, parser=parser)
    scorer = score_model(vocab, encoder, parser, read_conllx(dev_loc))
    print('%d:\t%.3f\t%.3f\t%.3f' % (itn, scorer.uas, scorer.las, scorer.tags_acc))
    #nlp.end_training(model_dir)
    #scorer = score_model(vocab, tagger, parser, read_conllx(dev_loc))
    #print('%d:\t%.3f\t%.3f\t%.3f' % (itn, scorer.uas, scorer.las, scorer.tags_acc))


if __name__ == '__main__':
    import cProfile
    import pstats
    if 1:
        plac.call(main)
    else:
        cProfile.runctx("plac.call(main)", globals(), locals(), "Profile.prof")
    s = pstats.Stats("Profile.prof")
    s.strip_dirs().sort_stats("time").print_stats()


    plac.call(main)
