"""
Get a mapping of (lemma, sense_number)-->supersense, and a mapping
(lemma, ON group)-->(lemma, sense_number).

Then we can read the OntoNotes token-->(lemma, ON group) annotations, and resolve
them to the token-->supersense annotations we want to train from.

supersense: A WordNet lexical file number
sense_number: A WordNet sense key, found in e.g. wordnet/index.sense file
lex_filenum: A WordNet "super sense", or lexical file number.
onto_group: An OntoNotes sense grouping, which dominates zero or more WN senses.
"""
from __future__ import division

from os import path
import os
import re
import codecs


def get_sense_to_ssense(index_dot_sense_loc):
    mapping = {}
    pos_tags = [None, 'n', 'v', 'j', 'a', 's']
    for line in codecs.open(index_dot_sense_loc, 'r', 'utf8'):
        sense_key, synset_offset, sense_number, tag_cnt = line.split()
        lemma, lex_sense = sense_key.split('%')
        ss_type, lex_filenum, lex_id, head_word, head_id = lex_sense.split(':')
        pos = pos_tags[int(ss_type)]
        mapping[(lemma, pos, int(sense_number))] = int(lex_filenum)
    return mapping


sense_group_re = re.compile(r'<sense .*?</sense>', re.DOTALL)
wn_mapping_re = re.compile(r'version="3.0">([^<]+)<')
def get_og_to_sense(sense_inv_dir):
    mapping = {}
    for filename in os.listdir(sense_inv_dir):
        if not filename.endswith('.xml'):
            continue
        if '-' not in filename:
            continue
        lemma, pos = filename.split('-')[:2]
        pos = pos[0]
        # Word is these often don't validate, because of course. So, just parse
        # with regex...
        xml_str = open(path.join(sense_inv_dir, filename)).read()
        for sense_grouping in sense_group_re.findall(xml_str):
            group_num = sense_grouping.split('n="')[1].split('"')[0]
            if not group_num:
                continue

            group_num = int(float(group_num))
            key = (lemma, pos, int(group_num))
            mapping.setdefault(key, [])
            wn_elem = wn_mapping_re.search(sense_grouping)
            if wn_elem is not None:
                sense_num_str = wn_elem.groups()[0].replace('.', ',')
                sense_ids = [(lemma, pos, int(n)) for n in sense_num_str.strip().split(',')]
                mapping[key].extend(sense_ids)
    return mapping


def get_lexnames(loc):
    names = {}
    for line in open(loc):
        id_, name, syn_type = line.split()
        names[int(id_)] = name
    return names


def get_og_to_ssenses(wordnet_dir, onto_dir):
    sense_inv_dir = path.join(onto_dir, 'data', 'english', 'metadata', 'sense-inventories')
    og_to_sense = get_og_to_sense(sense_inv_dir)
    sense_to_ssense = get_sense_to_ssense(path.join(wordnet_dir, 'index.sense'))
    lexnames = get_lexnames(path.join(wordnet_dir, 'lexnames'))

    mapping = {}
    for key, senses in og_to_sense.items():
        if senses is not None:
            mapping[key] = set([lexnames[sense_to_ssense[s_key]]
                                for s_key in senses if s_key in sense_to_ssense])
    return mapping


def main(wordnet_dir, onto_dir):
    mapping = get_og_to_ssenses(wordnet_dir, onto_dir)
    print mapping[('dog', 'v', 1)]
    print mapping[('dog', 'n', 1)]
    print mapping[('abandon', 'v', 1)]
    print mapping[('abandon', 'n', 1)]


if __name__ == '__main__':
    import plac
    plac.call(main)
