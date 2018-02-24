'''Train for CONLL 2017 UD treebank evaluation. Takes .conllu files, writes
.conllu format for development data, allowing the official scorer to be used.
'''
from __future__ import unicode_literals
import plac
import tqdm
import re
import sys
import spacy
import spacy.util
from spacy.tokens import Doc
from spacy.gold import GoldParse, minibatch
from spacy.syntax.nonproj import projectivize
from collections import defaultdict, Counter
from timeit import default_timer as timer
from spacy.matcher import Matcher

import random
import numpy.random

from spacy._align import align

random.seed(0)
numpy.random.seed(0)


def get_token_acc(docs, golds):
    '''Quick function to evaluate tokenization accuracy.'''
    miss = 0
    hit = 0
    for doc, gold in zip(docs, golds):
        for i in range(len(doc)):
            token = doc[i]
            align = gold.words[i]
            if align == None:
                miss += 1
            else:
                hit += 1
    return miss, hit


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
    #for annot in gold.orig_annot:
    #    print(annot)
    #for i in range(len(doc)):
    #    print(doc[i].text, gold.words[i], gold.labels[i], gold.heads[i])
    return doc, gold


def refresh_docs(docs):
    vocab = docs[0].vocab
    return [Doc(vocab, words=[t.text for t in doc],
                       spaces=[t.whitespace_ for t in doc])
            for doc in docs]


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
        #print([t.text for t in doc])
        file_.write("# newdoc id = {i}\n".format(i=i))
        for j, sent in enumerate(doc.sents):
            file_.write("# sent_id = {i}.{j}\n".format(i=i, j=j))
            file_.write("# text = {text}\n".format(text=sent.text))
            for k, t in enumerate(sent):
                if t.head.i == t.i:
                    head = 0
                else:
                    head = k + (t.head.i - t.i) + 1
                fields = [str(k+1), t.text, t.lemma_, t.pos_, t.tag_, '_',
                          str(head), t.dep_.lower(), '_', '_']
                file_.write('\t'.join(fields) + '\n')
            file_.write('\n')


def main(lang, conllu_train_loc, text_train_loc, conllu_dev_loc, text_dev_loc,
         output_loc):
    nlp = spacy.blank(lang)
    if lang == 'en':
        vec_nlp = spacy.util.load_model('spacy/data/en_core_web_lg/en_core_web_lg-2.0.0')
        nlp.vocab.vectors = vec_nlp.vocab.vectors
        for lex in vec_nlp.vocab:
            _ = nlp.vocab[lex.orth_]
        vec_nlp = None
    with open(conllu_train_loc) as conllu_file:
        with open(text_train_loc) as text_file:
            docs, golds = read_data(nlp, conllu_file, text_file,
                                    oracle_segments=False, raw_text=True,
                                    max_doc_length=10, limit=None)
    print("Create parser")
    nlp.add_pipe(nlp.create_pipe('parser'))
    nlp.parser.add_multitask_objective('tag')
    nlp.parser.add_multitask_objective('sent_start')
    nlp.parser.moves.add_action(2, 'subtok')
    nlp.add_pipe(nlp.create_pipe('tagger'))
    for gold in golds:
        for tag in gold.tags:
            if tag is not None:
                nlp.tagger.add_label(tag)
    optimizer = nlp.begin_training(lambda: golds_to_gold_tuples(docs, golds))
    # Replace labels that didn't make the frequency cutoff
    actions = set(nlp.parser.labels)
    label_set = set([act.split('-')[1] for act in actions if '-' in act])
    for gold in golds:
        for i, label in enumerate(gold.labels):
            if label is not None and label not in label_set:
                gold.labels[i] = label.split('||')[0]
    n_train_words = sum(len(doc) for doc in docs)
    print(n_train_words)
    print("Begin training")
    # Batch size starts at 1 and grows, so that we make updates quickly
    # at the beginning of training.
    batch_sizes = spacy.util.compounding(spacy.util.env_opt('batch_from', 1),
                                   spacy.util.env_opt('batch_to', 8),
                                   spacy.util.env_opt('batch_compound', 1.001))
    for i in range(30):
        docs = refresh_docs(docs)
        batches = minibatch(list(zip(docs, golds)), size=batch_sizes)
        with tqdm.tqdm(total=n_train_words, leave=False) as pbar:
            losses = {}
            for batch in batches:
                if not batch:
                    continue
                batch_docs, batch_gold = zip(*batch)

                nlp.update(batch_docs, batch_gold, sgd=optimizer,
                           drop=0.2, losses=losses)
                pbar.update(sum(len(doc) for doc in batch_docs))
        
        with nlp.use_params(optimizer.averages):
            dev_docs, scorer = parse_dev_data(nlp, text_dev_loc, conllu_dev_loc,
                                              oracle_segments=False, joint_sbd=True,
                                              limit=5)
            print_progress(i, losses, scorer)
            with open(output_loc, 'w') as file_:
                print_conllu(dev_docs, file_)
            with open('/tmp/train.conllu', 'w') as file_:
                print_conllu(list(nlp.pipe([d.text for d in batch_docs])), file_)




if __name__ == '__main__':
    plac.call(main)
