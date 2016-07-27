"""Align the raw sentences from Read et al (2012) to the PTB tokenization,
outputting as a .json file. Used in bin/prepare_treebank.py
"""
from __future__ import unicode_literals

import plac
from pathlib import Path
import json
from os import path
import os

from spacy.munge import read_ptb
from spacy.munge.read_ontonotes import sgml_extract


def read_odc(section_loc):
    # Arbitrary patches applied to the _raw_ text to promote alignment.
    patches = (
        ('. . . .', '...'),
        ('....', '...'),
        ('Co..', 'Co.'),
        ("`", "'"),
        # OntoNotes specific
        (" S$", " US$"),
        ("Showtime or a sister service", "Showtime or a service"),
        ("The hotel and gaming company", "The hotel and Gaming company"),
        ("I'm-coming-down-your-throat", "I-'m coming-down-your-throat"),
    )
    
    paragraphs = []
    with open(section_loc) as file_:
        para = []
        for line in file_:
            if line.startswith('['):
                line = line.split('|', 1)[1].strip()
                for find, replace in patches:
                    line = line.replace(find, replace)
                para.append(line)
            else:
                paragraphs.append(para)
                para = []
        paragraphs.append(para)
    return paragraphs


def read_ptb_sec(ptb_sec_dir):
    ptb_sec_dir = Path(ptb_sec_dir)
    files = []
    for loc in ptb_sec_dir.iterdir():
        if not str(loc).endswith('parse') and not str(loc).endswith('mrg'):
            continue
        filename = loc.parts[-1].split('.')[0]
        with loc.open() as file_:
            text = file_.read()
        sents = []
        for parse_str in read_ptb.split(text):
            words, brackets = read_ptb.parse(parse_str, strip_bad_periods=True)
            words = [_reform_ptb_word(word) for word in words]
            string = ' '.join(words)
            sents.append((filename, string))
        files.append(sents)
    return files


def _reform_ptb_word(tok):
    tok = tok.replace("``", '"')
    tok = tok.replace("`", "'")
    tok = tok.replace("''", '"')
    tok = tok.replace('\\', '')
    tok = tok.replace('-LCB-', '{')
    tok = tok.replace('-RCB-', '}')
    tok = tok.replace('-RRB-', ')')
    tok = tok.replace('-LRB-', '(')
    tok = tok.replace("'T-", "'T")
    return tok
 

def get_alignment(raw_by_para, ptb_by_file):
    # These are list-of-lists, by paragraph and file respectively.
    # Flatten them into a list of (outer_id, inner_id, item) triples
    raw_sents = _flatten(raw_by_para)
    ptb_sents = list(_flatten(ptb_by_file))

    output = []
    ptb_idx = 0
    n_skipped = 0
    skips = []
    for (p_id, p_sent_id, raw) in raw_sents:
        if ptb_idx >= len(ptb_sents):
            n_skipped += 1
            continue
        f_id, f_sent_id, (ptb_id, ptb) = ptb_sents[ptb_idx]
        alignment = align_chars(raw, ptb)
        if not alignment:
            skips.append((ptb, raw))
            n_skipped += 1
            continue
        ptb_idx += 1
        sepped = []
        for i, c in enumerate(ptb):
            if alignment[i] is False:
                sepped.append('<SEP>')
            else:
                sepped.append(c)
        output.append((f_id, p_id, f_sent_id, (ptb_id, ''.join(sepped))))
    if n_skipped + len(ptb_sents) != len(raw_sents):
        for ptb, raw in skips:
            print(ptb)
            print(raw)
        raise Exception
    return output


def _flatten(nested):
    flat = []
    for id1, inner in enumerate(nested):
        flat.extend((id1, id2, item) for id2, item in enumerate(inner))
    return flat


def align_chars(raw, ptb):
    if raw.replace(' ', '') != ptb.replace(' ', ''):
        return None
    i = 0
    j = 0

    length = len(raw)
    alignment = [False for _ in range(len(ptb))]
    while i < length:
        if raw[i] == ' ' and ptb[j] == ' ':
            alignment[j] = True
            i += 1
            j += 1
        elif raw[i] == ' ':
            i += 1
        elif ptb[j] == ' ':
            j += 1
        assert raw[i].lower() == ptb[j].lower(), raw[i:1]
        alignment[j] = i
        i += 1; j += 1
    return alignment


def group_into_files(sents):
    last_id = 0
    last_fn = None
    this = []
    output = []
    for f_id, p_id, s_id, (filename, sent) in sents:
        if f_id != last_id:
            assert last_fn is not None
            output.append((last_fn, this))
            this = []
        last_fn = filename
        this.append((f_id, p_id, s_id, sent))
        last_id = f_id
    if this:
        assert last_fn is not None
        output.append((last_fn, this))
    return output


def group_into_paras(sents):
    last_id = 0
    this = []
    output = []
    for f_id, p_id, s_id, sent in sents:
        if p_id != last_id and this:
            output.append(this)
            this = []
        this.append(sent)
        last_id = p_id
    if this:
        output.append(this)
    return output


def get_sections(odc_dir, ptb_dir, out_dir):
    for i in range(25):
        section = str(i) if i >= 10 else ('0' + str(i))
        odc_loc = path.join(odc_dir, 'wsj%s.txt' % section)
        ptb_sec = path.join(ptb_dir, section)
        out_loc = path.join(out_dir, 'wsj%s.json' % section)
        yield odc_loc, ptb_sec, out_loc


def align_section(raw_paragraphs, ptb_files):
    aligned = get_alignment(raw_paragraphs, ptb_files)
    return [(fn, group_into_paras(sents))
            for fn, sents in group_into_files(aligned)]


def do_wsj(odc_dir, ptb_dir, out_dir):
    for odc_loc, ptb_sec_dir, out_loc in get_sections(odc_dir, ptb_dir, out_dir):
        files = align_section(read_odc(odc_loc), read_ptb_sec(ptb_sec_dir))
        with open(out_loc, 'w') as file_:
            json.dump(files, file_)


def do_web(src_dir, onto_dir, out_dir):
    mapping = dict(line.split() for line in open(path.join(onto_dir, 'map.txt'))
                   if len(line.split()) == 2)
    for annot_fn, src_fn in mapping.items():
        if not annot_fn.startswith('eng'):
            continue

        ptb_loc = path.join(onto_dir, annot_fn + '.parse') 
        src_loc = path.join(src_dir, src_fn + '.sgm')

        if path.exists(ptb_loc) and path.exists(src_loc):
            src_doc = sgml_extract(open(src_loc).read())
            ptb_doc = [read_ptb.parse(parse_str, strip_bad_periods=True)[0]
                       for parse_str in read_ptb.split(open(ptb_loc).read())]
            print('Found')
        else:
            print('Miss')


def may_mkdir(parent, *subdirs):
    if not path.exists(parent):
        os.mkdir(parent)
    for i in range(1, len(subdirs)):
        directories = (parent,) + subdirs[:i]
        subdir = path.join(*directories)
        if not path.exists(subdir):
            os.mkdir(subdir)


def main(odc_dir, onto_dir, out_dir):
    may_mkdir(out_dir, 'wsj', 'align')
    may_mkdir(out_dir, 'web', 'align')
    #do_wsj(odc_dir, path.join(ontonotes_dir, 'wsj', 'orig'),
    #       path.join(out_dir, 'wsj', 'align'))
    do_web(
        path.join(onto_dir, 'data', 'english', 'metadata', 'context', 'wb', 'sel'),
        path.join(onto_dir, 'data', 'english', 'annotations', 'wb'),
        path.join(out_dir, 'web', 'align'))



if __name__ == '__main__':
    plac.call(main)
