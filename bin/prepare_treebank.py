"""Convert OntoNotes into a json format.

doc: {
    id: string,
    paragraphs: [{
        raw: string,
        segmented: string,
        sents: [int],
        tokens: [{
            start: int,
            tag: string,
            head: int,
            dep: string}],
        brackets: [{
            start: int,
            end: int,
            label: string,
            flabel: int}]}]}

Consumes output of spacy/munge/align_raw.py
"""
import plac
import json
from os import path
import re

from spacy.munge import read_ptb
from spacy.munge import read_conll


def _iter_raw_files(raw_loc):
    files = json.load(open(raw_loc))
    for f in files:
        yield f


def _get_word_indices(raw_sent, word_idx, offset):
    indices = {}
    for piece in raw_sent.split('<SEP>'):
        for match in re.finditer(r'\S+', piece):
            indices[word_idx] = offset + match.start()
            word_idx += 1
        offset += len(piece)
    return indices, word_idx, offset + 1
            

def format_doc(section, filename, raw_paras, ptb_loc, dep_loc):
    ptb_sents = read_ptb.split(open(ptb_loc).read())
    dep_sents = read_conll.split(open(dep_loc).read())

    assert len(ptb_sents) == len(dep_sents)

    word_idx = 0
    i = 0
    doc = {'id': 'wsj_%s%s' % (section, filename), 'paragraphs': []}
    for raw_sents in raw_paras:
        para = {'raw': ' '.join(sent.replace('<SEP>', '') for sent in raw_sents),
                    'segmented': '<SENT>'.join(raw_sents),
                    'sents': [],
                    'tokens': [],
                    'brackets': []}
        offset = 0
        for raw_sent in raw_sents:
            words = raw_sent.replace('<SEP>', ' ').split()
            para['sents'].append(offset) 
            _, brackets = read_ptb.parse(ptb_sents[i], strip_bad_periods=True)
            _, annot = read_conll.parse(dep_sents[i], strip_bad_periods=True)
            indices, word_idx, offset = _get_word_indices(raw_sent, 0, offset)
            for j, token in enumerate(annot):
                head = indices[token['head']] if token['head'] != -1 else -1
                try:
                    para['tokens'].append({
                        'start': indices[token['id']],
                        'orth': words[j],
                        'tag': token['tag'],
                        'head': head,
                        'dep': token['dep']})
                except:
                    print sorted(indices.items())
                    print token
                    print raw_sent
                    raise
            for label, start, end in brackets:
                if start != end:
                    para['brackets'].append({'label': label,
                        'start': indices[start],
                        'end': indices[end-1]})
            i += 1
        doc['paragraphs'].append(para)
    return doc


def main(onto_dir, raw_dir, out_dir):
    for i in range(25):
        section = str(i) if i >= 10 else ('0' + str(i))
        raw_loc = path.join(raw_dir, 'wsj%s.json' % section)
        docs = []
        for j, raw_paras in enumerate(_iter_raw_files(raw_loc)):
            if section == '00':
                j += 1
            filename = str(j) if j >= 9 else ('0' + str(j))
            if section == '04' and filename == '55':
                continue
            ptb_loc = path.join(onto_dir, section, 'wsj_%s%s.mrg' % (section, filename))
            dep_loc = ptb_loc + '.3.pa.gs.tab'
            if path.exists(ptb_loc) and path.exists(dep_loc):
                print ptb_loc
                doc = format_doc(section, filename, raw_paras, ptb_loc, dep_loc)
                docs.append(doc)
        with open(path.join(out_dir, '%s.json' % section), 'w') as file_:
            json.dump(docs, file_)


if __name__ == '__main__':
    plac.call(main)

