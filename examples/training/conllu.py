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
from collections import Counter
from timeit import default_timer as timer

from spacy._align import align

def prevent_bad_sentences(doc):
    '''This is an example pipeline component for fixing sentence segmentation
    mistakes. The component sets is_sent_start to False, which means the
    parser will be prevented from making a sentence boundary there. The
    rules here aren't necessarily a good idea.'''
    for token in doc[1:]:
        if token.nbor(-1).text == ',':
            token.is_sent_start = False
        elif not token.nbor(-1).whitespace_:
            token.is_sent_start = False
        elif not token.nbor(-1).is_punct:
            token.is_sent_start = False
    return doc


def load_model(lang):
    '''This shows how to adjust the tokenization rules, to special-case
    for ways the CoNLLU tokenization differs. We need to get the tokenizer
    accuracy high on the various treebanks in order to do well. If we don't
    align on a content word, all dependencies to and from that word will
    be marked as incorrect.
    '''
    English = spacy.util.get_lang_class(lang)
    English.Defaults.infixes += ('(?<=[^-\d])[+\-\*^](?=[^-\d])',)
    English.Defaults.infixes += ('(?<=[^-])[+\-\*^](?=[^-\d])',)
    English.Defaults.infixes += ('(?<=[^-\d])[+\-\*^](?=[^-])',)
    English.Defaults.token_match = re.compile(r'=+').match
    nlp = English()
    nlp.tokenizer.add_special_case('***', [{'ORTH': '***'}])
    nlp.tokenizer.add_special_case("):", [{'ORTH': ")"}, {"ORTH": ":"}])
    nlp.tokenizer.add_special_case("and/or", [{'ORTH': "and"}, {"ORTH": "/"}, {"ORTH": "or"}])
    nlp.tokenizer.add_special_case("non-Microsoft", [{'ORTH': "non-Microsoft"}])
    nlp.tokenizer.add_special_case("mis-matches", [{'ORTH': "mis-matches"}])
    nlp.tokenizer.add_special_case("X.", [{'ORTH': "X"}, {"ORTH": "."}])
    nlp.tokenizer.add_special_case("b/c", [{'ORTH': "b/c"}])
    return nlp
    

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
              limit=None):
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
    for text, cd in zip(paragraphs, conllu):
        doc_words = []
        doc_tags = []
        doc_heads = []
        doc_deps = []
        doc_ents = []
        for cs in cd:
            sent_words = []
            sent_tags = []
            sent_heads = []
            sent_deps = []
            for id_, word, lemma, pos, tag, morph, head, dep, _1, _2 in cs:
                if '.' in id_:
                    continue
                if '-' in id_:
                    continue
                id_ = int(id_)-1
                head = int(head)-1 if head != '0' else id_
                sent_words.append(word)
                sent_tags.append(tag)
                sent_heads.append(head)
                sent_deps.append('ROOT' if dep == 'root' else dep)
            if oracle_segments:
                sent_heads, sent_deps = projectivize(sent_heads, sent_deps)
                docs.append(Doc(nlp.vocab, words=sent_words))
                golds.append(GoldParse(docs[-1], words=sent_words, heads=sent_heads,
                                       tags=sent_tags, deps=sent_deps,
                                       entities=['-']*len(sent_words)))
            for head in sent_heads:
                doc_heads.append(len(doc_words)+head)
            doc_words.extend(sent_words)
            doc_tags.extend(sent_tags)
            doc_deps.extend(sent_deps)
            doc_ents.extend(['-']*len(sent_words))
            # Create a GoldParse object for the sentence
        doc_heads, doc_deps = projectivize(doc_heads, doc_deps)
        if raw_text:
            docs.append(nlp.make_doc(text))
            golds.append(GoldParse(docs[-1], words=doc_words, tags=doc_tags,
                                   heads=doc_heads, deps=doc_deps,
                                   entities=doc_ents))
        if limit and len(docs) >= limit:
            break
    return docs, golds


def refresh_docs(docs):
    vocab = docs[0].vocab
    return [Doc(vocab, words=[t.text for t in doc],
                       spaces=[t.whitespace_ for t in doc])
            for doc in docs]


def read_conllu(file_):
    docs = []
    doc = None
    sent = []
    for line in file_:
        if line.startswith('# newdoc'):
            if doc:
                docs.append(doc)
            doc = []
        elif line.startswith('#'):
            continue
        elif not line.strip():
            if sent:
                if doc is None:
                    docs.append([sent])
                else:
                    doc.append(sent)
            sent = []
        else:
            sent.append(line.strip().split())
    if sent:
        if doc is None:
            docs.append([sent])
        else:
            doc.append(sent)
    if doc:
        docs.append(doc)
    return docs


def parse_dev_data(nlp, text_loc, conllu_loc, oracle_segments=False,
                   joint_sbd=True):
    with open(text_loc) as text_file:
        with open(conllu_loc) as conllu_file:
            docs, golds = read_data(nlp, conllu_file, text_file,
                                    oracle_segments=oracle_segments)
    if not joint_sbd:
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
    for i, doc in enumerate(docs):
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


def main(spacy_model, conllu_train_loc, text_train_loc, conllu_dev_loc, text_dev_loc,
         output_loc):
    nlp = load_model(spacy_model)
    with open(conllu_train_loc) as conllu_file:
        with open(text_train_loc) as text_file:
            docs, golds = read_data(nlp, conllu_file, text_file,
                                    oracle_segments=False, raw_text=True)
    print("Create parser")
    nlp.add_pipe(nlp.create_pipe('parser'))
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
                                   spacy.util.env_opt('batch_to', 2),
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
                                              oracle_segments=False, joint_sbd=True)
            print_progress(i, losses, scorer)
            with open(output_loc, 'w') as file_:
                print_conllu(dev_docs, file_)
            dev_docs, scorer = parse_dev_data(nlp, text_dev_loc, conllu_dev_loc,
                                              oracle_segments=False, joint_sbd=False)
            print_progress(i, losses, scorer)
            with open(output_loc, 'w') as file_:
                print_conllu(dev_docs, file_)



if __name__ == '__main__':
    plac.call(main)
