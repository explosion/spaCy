"""Convert OntoNotes into a json format.

doc: {
    id: string,
    paragraphs: [{
        raw: string,
        sents: [int],
        tokens: [{
            start: int,
            tag: string,
            head: int,
            dep: string}],
        ner: [{
            start: int,
            end: int,
            label: string}],
        brackets: [{
            start: int,
            end: int,
            label: string}]}]}

Consumes output of spacy/munge/align_raw.py
"""
from __future__ import unicode_literals
import plac
import json
from os import path
import os
import re
import io
from collections import defaultdict

from spacy.munge import read_ptb
from spacy.munge import read_conll
from spacy.munge import read_ner


def _iter_raw_files(raw_loc):
    files = json.load(open(raw_loc))
    for f in files:
        yield f


def format_doc(file_id, raw_paras, ptb_text, dep_text, ner_text):
    ptb_sents = read_ptb.split(ptb_text)
    dep_sents = read_conll.split(dep_text)
    if len(ptb_sents) != len(dep_sents):
        return None
    if ner_text is not None:
        ner_sents = read_ner.split(ner_text)
    else:
        ner_sents = [None] * len(ptb_sents)

    i = 0
    doc = {'id': file_id}
    if raw_paras is None:
        doc['paragraphs'] = [format_para(None, ptb_sents, dep_sents, ner_sents)]
        #for ptb_sent, dep_sent, ner_sent in zip(ptb_sents, dep_sents, ner_sents):
        #    doc['paragraphs'].append(format_para(None, [ptb_sent], [dep_sent], [ner_sent]))
    else:
        doc['paragraphs'] = []
        for raw_sents in raw_paras:
            para = format_para(
                        ' '.join(raw_sents).replace('<SEP>', ''),
                        ptb_sents[i:i+len(raw_sents)],
                        dep_sents[i:i+len(raw_sents)],
                        ner_sents[i:i+len(raw_sents)])
            if para['sentences']:
                doc['paragraphs'].append(para)
            i += len(raw_sents)
    return doc


def format_para(raw_text, ptb_sents, dep_sents, ner_sents):
    para = {'raw': raw_text, 'sentences': []}
    offset = 0
    assert len(ptb_sents) == len(dep_sents) == len(ner_sents)
    for ptb_text, dep_text, ner_text in zip(ptb_sents, dep_sents, ner_sents):
        _, deps = read_conll.parse(dep_text, strip_bad_periods=True)
        if deps and 'VERB' in [t['tag'] for t in deps]:
            continue
        if ner_text is not None:
            _, ner = read_ner.parse(ner_text, strip_bad_periods=True)
        else:
            ner = ['-' for _ in deps]
        _, brackets = read_ptb.parse(ptb_text, strip_bad_periods=True)
        # Necessary because the ClearNLP converter deletes EDITED words.
        if len(ner) != len(deps):
            ner = ['-' for _ in deps]
        para['sentences'].append(format_sentence(deps, ner, brackets))
    return para


def format_sentence(deps, ner, brackets):
    sent = {'tokens': [], 'brackets': []}
    for token_id, (token, token_ent) in enumerate(zip(deps, ner)):
        sent['tokens'].append(format_token(token_id, token, token_ent))

    for label, start, end in brackets:
        if start != end:
            sent['brackets'].append({
                'label': label,
                'first': start,
                'last': (end-1)})
    return sent


def format_token(token_id, token, ner):
    assert token_id == token['id']
    head = (token['head'] - token_id) if token['head'] != -1 else 0
    return {
        'id': token_id,
        'orth': token['word'],
        'tag': token['tag'],
        'head': head,
        'dep': token['dep'],
        'ner': ner}


def read_file(*pieces):
    loc = path.join(*pieces)
    if not path.exists(loc):
        return None
    else:
        return io.open(loc, 'r', encoding='utf8').read().strip()


def get_file_names(section_dir, subsection):
    filenames = []
    for fn in os.listdir(path.join(section_dir, subsection)):
        filenames.append(fn.rsplit('.', 1)[0])
    return list(sorted(set(filenames)))


def read_wsj_with_source(onto_dir, raw_dir):
    # Now do WSJ, with source alignment
    onto_dir = path.join(onto_dir, 'data', 'english', 'annotations', 'nw', 'wsj')
    docs = {}
    for i in range(25):
        section = str(i) if i >= 10 else ('0' + str(i))
        raw_loc = path.join(raw_dir, 'wsj%s.json' % section)
        for j, (filename, raw_paras) in enumerate(_iter_raw_files(raw_loc)):
            if section == '00':
                j += 1
            if section == '04' and filename == '55':
                continue
            ptb = read_file(onto_dir, section, '%s.parse' % filename)
            dep = read_file(onto_dir, section, '%s.parse.dep' % filename)
            ner = read_file(onto_dir, section, '%s.name' % filename)
            if ptb is not None and dep is not None:
                docs[filename] = format_doc(filename, raw_paras, ptb, dep, ner)
    return docs


def get_doc(onto_dir, file_path, wsj_docs):
    filename = file_path.rsplit('/', 1)[1]
    if filename in wsj_docs:
        return wsj_docs[filename]
    else:
        ptb = read_file(onto_dir, file_path + '.parse')
        dep = read_file(onto_dir, file_path + '.parse.dep')
        ner = read_file(onto_dir, file_path + '.name')
        if ptb is not None and dep is not None:
            return format_doc(filename, None, ptb, dep, ner)
        else:
            return None


def read_ids(loc):
    return open(loc).read().strip().split('\n')


def main(onto_dir, raw_dir, out_dir):
    wsj_docs = read_wsj_with_source(onto_dir, raw_dir)

    for partition in ('train', 'test', 'development'):
        ids = read_ids(path.join(onto_dir, '%s.id' % partition))
        docs_by_genre = defaultdict(list)
        for file_path in ids:
            doc = get_doc(onto_dir, file_path, wsj_docs)
            if doc is not None:
                genre = file_path.split('/')[3]
                docs_by_genre[genre].append(doc)
        part_dir = path.join(out_dir, partition)
        if not path.exists(part_dir):
            os.mkdir(part_dir)
        for genre, docs in sorted(docs_by_genre.items()):
            out_loc = path.join(part_dir, genre + '.json')
            with open(out_loc, 'w') as file_:
                json.dump(docs, file_, indent=4)


if __name__ == '__main__':
    plac.call(main)
