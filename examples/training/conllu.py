'''Train for CONLL 2017 UD treebank evaluation. Takes .conllu files, writes
.conllu format for development data, allowing the official scorer to be used.
'''
from __future__ import unicode_literals
import plac
import tqdm
import attr
from pathlib import Path
import re
import sys
import json

import spacy
import spacy.util
from spacy.tokens import Token, Doc
from spacy.gold import GoldParse, minibatch
from spacy.syntax.nonproj import projectivize
from collections import defaultdict, Counter
from timeit import default_timer as timer
from spacy.matcher import Matcher

import itertools
import random
import numpy.random
import cytoolz

from spacy._align import align

random.seed(0)
numpy.random.seed(0)

def minibatch_by_words(items, size=5000):
    random.shuffle(items)
    if isinstance(size, int):
        size_ = itertools.repeat(size)
    else:
        size_ = size
    items = iter(items)
    while True:
        batch_size = next(size_)
        batch = []
        while batch_size >= 0:
            try:
                doc, gold = next(items)
            except StopIteration:
                yield batch
                return
            batch_size -= len(doc)
            batch.append((doc, gold))
        if batch:
            yield batch
        else:
            break

################
# Data reading #
################

def split_text(text):
    return [par.strip().replace('\n', ' ')
            for par in text.split('\n\n')]
 

def read_data(nlp, conllu_file, text_file, raw_text=True, oracle_segments=False,
              max_doc_length=None, limit=None):
    '''Read the CONLLU format into (Doc, GoldParse) tuples. If raw_text=True,
    include Doc objects created using nlp.make_doc and then aligned against
    the gold-standard sequences. If oracle_segments=True, include Doc objects
    created from the gold-standard segments. At least one must be True.'''
    if not raw_text and not oracle_segments:
        raise ValueError("At least one of raw_text or oracle_segments must be True")
    paragraphs = split_text(text_file.read())
    conllu = read_conllu(conllu_file)
    # sd is spacy doc; cd is conllu doc
    # cs is conllu sent, ct is conllu token
    docs = []
    golds = []
    for doc_id, (text, cd) in enumerate(zip(paragraphs, conllu)):
        sent_annots = []
        for cs in cd:
            sent = defaultdict(list)
            for id_, word, lemma, pos, tag, morph, head, dep, _, space_after in cs:
                if '.' in id_:
                    continue
                if '-' in id_:
                    continue
                id_ = int(id_)-1
                head = int(head)-1 if head != '0' else id_
                sent['words'].append(word)
                sent['tags'].append(tag)
                sent['heads'].append(head)
                sent['deps'].append('ROOT' if dep == 'root' else dep)
                sent['spaces'].append(space_after == '_')
            sent['entities'] = ['-'] * len(sent['words'])
            sent['heads'], sent['deps'] = projectivize(sent['heads'],
                                                       sent['deps'])
            if oracle_segments:
                docs.append(Doc(nlp.vocab, words=sent['words'], spaces=sent['spaces']))
                golds.append(GoldParse(docs[-1], **sent))

            sent_annots.append(sent)
            if raw_text and max_doc_length and len(sent_annots) >= max_doc_length:
                doc, gold = _make_gold(nlp, None, sent_annots)
                sent_annots = []
                docs.append(doc)
                golds.append(gold)
                if limit and len(docs) >= limit:
                    return docs, golds

        if raw_text and sent_annots:
            doc, gold = _make_gold(nlp, None, sent_annots)
            docs.append(doc)
            golds.append(gold)
        if limit and len(docs) >= limit:
            return docs, golds
    return docs, golds


def read_conllu(file_):
    docs = []
    sent = []
    doc = []
    for line in file_:
        if line.startswith('# newdoc'):
            if doc:
                docs.append(doc)
            doc = []
        elif line.startswith('#'):
            continue
        elif not line.strip():
            if sent:
                doc.append(sent)
            sent = []
        else:
            sent.append(line.strip().split())
    if sent:
        doc.append(sent)
    if doc:
        docs.append(doc)
    return docs


def _make_gold(nlp, text, sent_annots):
    # Flatten the conll annotations, and adjust the head indices
    flat = defaultdict(list)
    for sent in sent_annots:
        flat['heads'].extend(len(flat['words'])+head for head in sent['heads'])
        for field in ['words', 'tags', 'deps', 'entities', 'spaces']:
            flat[field].extend(sent[field])
    # Construct text if necessary
    assert len(flat['words']) == len(flat['spaces'])
    if text is None:
        text = ''.join(word+' '*space for word, space in zip(flat['words'], flat['spaces'])) 
    doc = nlp.make_doc(text)
    flat.pop('spaces')
    gold = GoldParse(doc, **flat)
    return doc, gold

#############################
# Data transforms for spaCy #
#############################

def golds_to_gold_tuples(docs, golds):
    '''Get out the annoying 'tuples' format used by begin_training, given the
    GoldParse objects.'''
    tuples = []
    for doc, gold in zip(docs, golds):
        text = doc.text
        ids, words, tags, heads, labels, iob = zip(*gold.orig_annot)
        sents = [((ids, words, tags, heads, labels, iob), [])]
        tuples.append((text, sents))
    return tuples


##############
# Evaluation #
##############

def parse_dev_data(nlp, text_loc, conllu_loc, oracle_segments=False,
                   joint_sbd=True, limit=None):
    with open(text_loc) as text_file:
        with open(conllu_loc) as conllu_file:
            docs, golds = read_data(nlp, conllu_file, text_file,
                                    oracle_segments=oracle_segments, limit=limit)
    if joint_sbd:
        pass
    else:
        sbd = nlp.create_pipe('sentencizer')
        for doc in docs:
            doc = sbd(doc)
            for sent in doc.sents:
                sent[0].is_sent_start = True
                for word in sent[1:]:
                    word.is_sent_start = False
    scorer = nlp.evaluate(zip(docs, golds))
    return docs, scorer


def print_progress(itn, losses, scorer):
    scores = {}
    for col in ['dep_loss', 'tag_loss', 'uas', 'tags_acc', 'token_acc',
                'ents_p', 'ents_r', 'ents_f', 'cpu_wps', 'gpu_wps']:
        scores[col] = 0.0
    scores['dep_loss'] = losses.get('parser', 0.0)
    scores['ner_loss'] = losses.get('ner', 0.0)
    scores['tag_loss'] = losses.get('tagger', 0.0)
    scores.update(scorer.scores)
    tpl = '\t'.join((
        '{:d}',
        '{dep_loss:.3f}',
        '{ner_loss:.3f}',
        '{uas:.3f}',
        '{ents_p:.3f}',
        '{ents_r:.3f}',
        '{ents_f:.3f}',
        '{tags_acc:.3f}',
        '{token_acc:.3f}',
    ))
    print(tpl.format(itn, **scores))


def print_conllu(docs, file_):
    merger = Matcher(docs[0].vocab)
    merger.add('SUBTOK', None, [{'DEP': 'subtok', 'op': '+'}])
    for i, doc in enumerate(docs):
        matches = merger(doc)
        spans = [doc[start:end+1] for _, start, end in matches]
        offsets = [(span.start_char, span.end_char) for span in spans]
        for start_char, end_char in offsets:
            doc.merge(start_char, end_char)
        file_.write("# newdoc id = {i}\n".format(i=i))
        for j, sent in enumerate(doc.sents):
            file_.write("# sent_id = {i}.{j}\n".format(i=i, j=j))
            file_.write("# text = {text}\n".format(text=sent.text))
            for k, token in enumerate(sent):
                file_.write(token._.get_conllu_lines(k) + '\n')
            file_.write('\n')

#def get_sent_conllu(sent, sent_id):
#    lines = ["# sent_id = {sent_id}".format(sent_id=sent_id)]

def get_token_conllu(token, i):
    if token._.begins_fused:
        n = 1
        while token.nbor(n)._.inside_fused:
            n += 1
        id_ = '%d-%d' % (k, k+n)
        lines = [id_, token.text, '_', '_', '_', '_', '_', '_', '_', '_']
    else:
        lines = []
    if token.head.i == token.i:
        head = 0
    else:
        head = i + (token.head.i - token.i) + 1
    fields = [str(i+1), token.text, token.lemma_, token.pos_, token.tag_, '_',
              str(head), token.dep_.lower(), '_', '_']
    lines.append('\t'.join(fields))
    return '\n'.join(lines)

Token.set_extension('get_conllu_lines', method=get_token_conllu)
Token.set_extension('begins_fused', default=False)
Token.set_extension('inside_fused', default=False)


##################
# Initialization #
##################


def load_nlp(corpus, config):
    lang = corpus.split('_')[0]
    nlp = spacy.blank(lang)
    if config.vectors:
        nlp.vocab.from_disk(config.vectors / 'vocab')
    return nlp

def initialize_pipeline(nlp, docs, golds, config):
    print("Create parser")
    nlp.add_pipe(nlp.create_pipe('parser'))
    if config.multitask_tag:
        nlp.parser.add_multitask_objective('tag')
    if config.multitask_sent:
        nlp.parser.add_multitask_objective('sent_start')
    nlp.parser.moves.add_action(2, 'subtok')
    nlp.add_pipe(nlp.create_pipe('tagger'))
    for gold in golds:
        for tag in gold.tags:
            if tag is not None:
                nlp.tagger.add_label(tag)
    # Replace labels that didn't make the frequency cutoff
    actions = set(nlp.parser.labels)
    label_set = set([act.split('-')[1] for act in actions if '-' in act])
    for gold in golds:
        for i, label in enumerate(gold.labels):
            if label is not None and label not in label_set:
                gold.labels[i] = label.split('||')[0]
    return nlp.begin_training(lambda: golds_to_gold_tuples(docs, golds))


########################
# Command line helpers #
########################

@attr.s
class Config(object):
    vectors = attr.ib(default=None)
    max_doc_length = attr.ib(default=10)
    multitask_tag = attr.ib(default=True)
    multitask_sent = attr.ib(default=True)
    nr_epoch = attr.ib(default=30)
    batch_size = attr.ib(default=1000)
    dropout = attr.ib(default=0.2)

    @classmethod
    def load(cls, loc):
        with Path(loc).open('r', encoding='utf8') as file_:
            cfg = json.load(file_)
        return cls(**cfg)


class Dataset(object):
    def __init__(self, path, section):
        self.path = path
        self.section = section
        self.conllu = None
        self.text = None
        for file_path in self.path.iterdir():
            name = file_path.parts[-1]
            if section in name and name.endswith('conllu'):
                self.conllu = file_path
            elif section in name and name.endswith('txt'):
                self.text = file_path
        if self.conllu is None:
            msg = "Could not find .txt file in {path} for {section}"
            raise IOError(msg.format(section=section, path=path))
        if self.text is None:
            msg = "Could not find .txt file in {path} for {section}"
        self.lang = self.conllu.parts[-1].split('-')[0].split('_')[0]


class TreebankPaths(object):
    def __init__(self, ud_path, treebank, **cfg):
        self.train = Dataset(ud_path / treebank, 'train')
        self.dev = Dataset(ud_path / treebank, 'dev')
        self.lang = self.train.lang


@plac.annotations(
    ud_dir=("Path to Universal Dependencies corpus", "positional", None, Path),
    config=("Path to json formatted config file", "positional", None, Config.load),
    corpus=("UD corpus to train and evaluate on, e.g. en, es_ancora, etc",
            "positional", None, str),
    parses_loc=("Path to write the development parses", "positional", None, Path),
    limit=("Size limit", "option", "n", int)
)
def main(ud_dir, corpus, config, parses_loc='/tmp/dev.conllu', limit=10):
    paths = TreebankPaths(ud_dir, corpus)
    print("Train and evaluate", corpus, "using lang", paths.lang)
    nlp = load_nlp(paths.lang, config)

    docs, golds = read_data(nlp, paths.train.conllu.open(), paths.train.text.open(),
                            max_doc_length=config.max_doc_length, limit=limit)

    optimizer = initialize_pipeline(nlp, docs, golds, config)
    for i in range(config.nr_epoch):
        docs = [nlp.make_doc(doc.text) for doc in docs]
        batches = minibatch_by_words(list(zip(docs, golds)), size=config.batch_size)
        losses = {}
        n_train_words = sum(len(doc) for doc in docs)
        with tqdm.tqdm(total=n_train_words, leave=False) as pbar:
            for batch in batches:
                batch_docs, batch_gold = zip(*batch)
                pbar.update(sum(len(doc) for doc in batch_docs))
                nlp.update(batch_docs, batch_gold, sgd=optimizer,
                           drop=config.dropout, losses=losses)
        
        with nlp.use_params(optimizer.averages):
            dev_docs, scorer = parse_dev_data(nlp, paths.dev.text, paths.dev.conllu)
            print_progress(i, losses, scorer)
            with open(parses_loc, 'w') as file_:
                print_conllu(dev_docs, file_)


if __name__ == '__main__':
    plac.call(main)
