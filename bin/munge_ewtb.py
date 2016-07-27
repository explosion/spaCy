#!/usr/bin/env python
from __future__ import unicode_literals

from xml.etree import cElementTree as ElementTree
import json
import re

import plac
from pathlib import Path
from os import path


escaped_tokens = {
    '-LRB-': '(',
    '-RRB-': ')',
    '-LSB-': '[',
    '-RSB-': ']',
    '-LCB-': '{',
    '-RCB-': '}',
}

def read_parses(parse_loc):
    offset = 0
    doc = []
    for parse in open(str(parse_loc) + '.dep').read().strip().split('\n\n'):
        parse = _adjust_token_ids(parse, offset)
        offset += len(parse.split('\n'))
        doc.append(parse)
    return doc

def _adjust_token_ids(parse, offset):
    output = []
    for line in parse.split('\n'):
        pieces = line.split()
        pieces[0] = str(int(pieces[0]) + offset)
        pieces[5] = str(int(pieces[5]) + offset) if pieces[5] != '0' else '0'
        output.append('\t'.join(pieces))
    return '\n'.join(output)


def _fmt_doc(filename, paras):
    return {'id': filename, 'paragraphs': [_fmt_para(*para) for para in paras]}


def _fmt_para(raw, sents):
    return {'raw': raw, 'sentences': [_fmt_sent(sent) for sent in sents]}


def _fmt_sent(sent):
    return {
        'tokens': [_fmt_token(*t.split()) for t in sent.strip().split('\n')],
        'brackets': []}


def _fmt_token(id_, word, hyph, pos, ner, head, dep, blank1, blank2, blank3):
    head = int(head) - 1
    id_ = int(id_) - 1
    head = (head - id_) if head != -1 else 0
    return {'id': id_, 'orth': word, 'tag': pos, 'dep': dep, 'head': head}


tags_re = re.compile(r'<[\w\?/][^>]+>')
def main(out_dir, ewtb_dir='/usr/local/data/eng_web_tbk'):
    ewtb_dir = Path(ewtb_dir)
    out_dir = Path(out_dir)
    if not out_dir.exists():
        out_dir.mkdir()
    for genre_dir in ewtb_dir.joinpath('data').iterdir():
        #if 'answers' in str(genre_dir): continue
        parse_dir = genre_dir.joinpath('penntree')
        docs = []
        for source_loc in genre_dir.joinpath('source').joinpath('source_original').iterdir():
            filename = source_loc.parts[-1].replace('.sgm.sgm', '')
            filename = filename.replace('.xml', '')
            filename = filename.replace('.txt', '')
            parse_loc = parse_dir.joinpath(filename + '.xml.tree')
            parses = read_parses(parse_loc)
            source = source_loc.open().read().strip()
            if 'answers' in str(genre_dir):
                source = tags_re.sub('', source).strip()
            docs.append(_fmt_doc(filename, [[source, parses]]))

        out_loc = out_dir.joinpath(genre_dir.parts[-1] + '.json')
        with open(str(out_loc), 'w') as out_file:
            out_file.write(json.dumps(docs, indent=4))


if __name__ == '__main__':
    plac.call(main)
