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
import plac
import json
from os import path
import re

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
    ner_sents = read_ner.split(ner_text) if ner_text is not None else None

    assert len(ptb_sents) == len(dep_sents)

    i = 0
    doc = {'id': file_id, 'paragraphs': []}
    for raw_sents in raw_paras:
        para = {
            'raw': ' '.join(sent.replace('<SEP>', '') for sent in raw_sents),
            'sents': [],
            'tokens': [],
            'brackets': [],
            'entities': []}
        offset = 0
        for raw_sent in raw_sents:
            _, brackets = read_ptb.parse(ptb_sents[i], strip_bad_periods=True)
            _, annot = read_conll.parse(dep_sents[i], strip_bad_periods=True)
            if ner_sents is not None:
                _, ner = read_ner.parse(ner_sents[i], strip_bad_periods=True)
            else:
                ner = None
            for token_id, token in enumerate(annot):
                try:
                    head = (token['head'] + offset) if token['head'] != -1 else -1
                    para['tokens'].append({
                        'id': offset + token_id,
                        'orth': token['word'],
                        'tag': token['tag'],
                        'head': head,
                        'dep': token['dep']})
                except:
                    raise
            if ner is not None:
                for label, start, end in ner:
                    if start != end:
                        para['entities'].append({
                            'label': label,
                            'first': start + offset,
                            'last': (end-1) + offset})
            for label, start, end in brackets:
                if start != end:
                    para['brackets'].append({
                        'label': label,
                        'first': start + offset,
                        'last': (end-1) + offset})
            i += 1
            offset += len(annot)
            para['sents'].append(offset)
        doc['paragraphs'].append(para)
    return doc


def main(onto_dir, raw_dir, out_dir):
    for i in range(25):
        section = str(i) if i >= 10 else ('0' + str(i))
        raw_loc = path.join(raw_dir, 'wsj%s.json' % section)
        docs = []
        for j, (filename, raw_paras) in enumerate(_iter_raw_files(raw_loc)):
            if section == '00':
                j += 1
            if section == '04' and filename == '55':
                continue
            ptb_loc = path.join(onto_dir, section, '%s.parse' % filename)
            dep_loc = ptb_loc + '.dep'
            ner_loc = path.join(onto_dir, section, '%s.name' % filename)
            if path.exists(ptb_loc) and path.exists(dep_loc) and path.exists(ner_loc):
                docs.append(
                    format_doc(
                        filename,
                        raw_paras,
                        open(ptb_loc).read().strip(),
                        open(dep_loc).read().strip(),
                        open(ner_loc).read().strip() if path.exists(ner_loc) else None))
        with open(path.join(out_dir, '%s.json' % section), 'w') as file_:
            json.dump(docs, file_, indent=4)


if __name__ == '__main__':
    plac.call(main)

