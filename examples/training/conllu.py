'''Train for CONLL 2017 UD treebank evaluation. Takes .conllu files, writes
.conllu format for development data, allowing the official scorer to be used.
'''
from __future__ import unicode_literals
import plac
import tqdm
import re
import spacy
import spacy.util
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
    paragraphs = text.split('\n\n')
    paragraphs = [par.strip().replace('\n', ' ') for par in paragraphs]
    return paragraphs


def read_conllu(file_):
    docs = []
    doc = []
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
                doc.append(sent)
            sent = []
        else:
            sent.append(line.strip().split())
    if sent:
        doc.append(sent)
    if doc:
        docs.append(doc)
    return docs


def get_docs(nlp, text):
    paragraphs = split_text(text)
    docs = [nlp.make_doc(par) for par in paragraphs]
    return docs


def get_golds(docs, conllu):
    # sd is spacy doc; cd is conllu doc
    # cs is conllu sent, ct is conllu token
    golds = []
    for sd, cd in zip(docs, conllu):
        words = []
        tags = []
        heads = []
        deps = []
        for cs in cd:
            for id_, word, lemma, pos, tag, morph, head, dep, _1, _2 in cs:
                if '.' in id_:
                    continue
                i = len(words)
                id_ = int(id_)-1
                head = int(head)-1 if head != '0' else id_
                head_dist = head - id_
                words.append(word)
                tags.append(tag)
                heads.append(i+head_dist)
                deps.append('ROOT' if dep == 'root' else dep)
            heads, deps = projectivize(heads, deps)
        entities = ['-'] * len(words)
        gold = GoldParse(sd, words=words, tags=tags, heads=heads, deps=deps,
                         entities=entities)
        golds.append(gold)
    return golds

def parse_dev_data(nlp, text_loc, conllu_loc):
    with open(text_loc) as file_:
        docs = get_docs(nlp, file_.read())
    with open(conllu_loc) as file_:
        conllu_dev = read_conllu(file_)
    golds = list(get_golds(docs, conllu_dev))
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
                fields = [str(k+1), t.text, t.lemma_, t.pos_, t.tag_, '_', str(head), t.dep_, '_', '_']
                file_.write('\t'.join(fields) + '\n')
            file_.write('\n')


def main(spacy_model, conllu_train_loc, text_train_loc, conllu_dev_loc, text_dev_loc,
         output_loc):
    with open(conllu_train_loc) as file_:
        conllu_train = read_conllu(file_)
    nlp = load_model(spacy_model)
    print("Get docs")
    with open(text_train_loc) as file_:
        docs = get_docs(nlp, file_.read())
    golds = list(get_golds(docs, conllu_train))
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
    for i in range(10):
        with open(text_train_loc) as file_:
            docs = get_docs(nlp, file_.read())
        docs = docs[:len(golds)]
        with tqdm.tqdm(total=n_train_words, leave=False) as pbar:
            losses = {}
            for batch in minibatch(list(zip(docs, golds)), size=1):
                if not batch:
                    continue
                batch_docs, batch_gold = zip(*batch)

                nlp.update(batch_docs, batch_gold, sgd=optimizer,
                           drop=0.2, losses=losses)
                pbar.update(sum(len(doc) for doc in batch_docs))
        
        with nlp.use_params(optimizer.averages):
            dev_docs, scorer = parse_dev_data(nlp, text_dev_loc, conllu_dev_loc)
            print_progress(i, losses, scorer)
            with open(output_loc, 'w') as file_:
                print_conllu(dev_docs, file_)

if __name__ == '__main__':
    plac.call(main)
