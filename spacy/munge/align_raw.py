"""Align the raw sentences from Read et al (2012) to the PTB tokenization,
outputing the format:

[{
    section: int,
    file: string,
    paragraphs: [{
        raw: string,
        segmented: string,
        tokens: [int]}]}]
"""
import plac
from pathlib import Path
import json
from os import path

from spacy.munge import read_ptb


def read_unsegmented(section_loc):
    # Arbitrary patches applied to the _raw_ text to promote alignment.
    patches = (
        ('. . . .', '...'),
        ('....', '...'),
        ('Co..', 'Co.'),
        ("`", "'"),
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
        with loc.open() as file_:
            text = file_.read()
        sents = []
        for parse_str in read_ptb.split(text):
            words, brackets = read_ptb.parse(parse_str, strip_bad_periods=True)
            words = [_reform_ptb_word(word) for word in words]
            string = ' '.join(words)
            sents.append(string)
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
    ptb_sents = _flatten(ptb_by_file)

    assert len(raw_sents) == len(ptb_sents)

    output = []
    for (p_id, p_sent_id, raw), (f_id, f_sent_id, ptb) in zip(raw_sents, ptb_sents):
        alignment = align_chars(raw, ptb)
        sepped = []
        for i, c in enumerate(ptb):
            if alignment[i] is False:
                sepped.append('<SEP>')
            else:
                sepped.append(c)
        output.append((f_id, p_id, f_sent_id, ''.join(sepped)))
    return output


def _flatten(nested):
    flat = []
    for id1, inner in enumerate(nested):
        flat.extend((id1, id2, item) for id2, item in enumerate(inner))
    return flat


def align_chars(raw, ptb):
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
    this = []
    output = []
    for f_id, p_id, s_id, sent in sents:
        if f_id != last_id:
            output.append(this)
            this = []
        this.append((f_id, p_id, s_id, sent))
        last_id = f_id
    if this:
        output.append(this)
    return output


def group_into_paras(sents):
    last_id = 0
    this = []
    output = []
    for f_id, p_id, s_id, sent in sents:
        if p_id != last_id and this:
            output.append(this)
            this = []
        this.append((sent))
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


def main(odc_dir, ptb_dir, out_dir):
    for odc_loc, ptb_sec_dir, out_loc in get_sections(odc_dir, ptb_dir, out_dir):
        raw_paragraphs = read_unsegmented(odc_loc)
        ptb_files = read_ptb_sec(ptb_sec_dir)
        aligned = get_alignment(raw_paragraphs, ptb_files)
        files = [group_into_paras(f) for f in group_into_files(aligned)]
        with open(out_loc, 'w') as file_:
            json.dump(files, file_)


if __name__ == '__main__':
    plac.call(main)
