"""
The code below aims to document how the lookup tables for the Italian POS-aware Lemmatizer
have been derived from the morphological lexicon morph-it, by Barone and Zanchetta, and from
the lookup file used by the previous, non-POS-aware, version of the lemmatizer ("legacy" table).
In fact, it was used to build both the individual lookup files (json) associated to different POS-tags
and the binary file obtained by merging them, following the procedure described at the end of this file.
The tag_map in the creator method of the ItalianLemmatizerLookupsBuilder class specifies a mapping
from the universal tag-set used by spaCy to the tag-set used by morph-it; it is a one-to-many mapping.
A catch-all entry with key "OTHER" is included in the mapping to make it complete.
Obviously, this mapping could be ameliored, based on further analysis and experimentation.
Entries of the single lookup file "it_lemma_lookup.json" (from the previous version of the lemmatizer)
whose word forms don't occur in morph-it have been kept in an additional table.
"""

from collections import OrderedDict
import os
import json
from spacy.lookups import Lookups

class ItalianLemmatizerLookupsBuilder():
    
    def __init__(self, in_path='.', out_path='.', in_name='morph-it.txt', tag_map={}):
        self.in_path = in_path
        self.out_path = out_path
        self.in_name = in_name
        self.tag_map = tag_map or {
           'ADJ': ['ADJ', 'DET', 'TALE',],
           'ADV': ['ADV',],
           'AUX': ['AUX', 'ASP', 'CAU', 'MOD',],
           'DET': ['ART', 'ARTPRE', 'DET',],
           'NOUN': ['NOUN', 'NPR',],
           'PRON': ['PRO',],
           'ADP': ['PRE', 'ARTPRE'],
           'VERB': ['VER', 'AUX', 'ASP', 'CAU', 'MOD',],
           'NUM': ['NUM',],
           'OTHER': ['ABL', 'SENT', 'SYM', 'PON', 'SI', 'INT', 'SMI', 'CON', 'WH', 'NE',],
        }

    def morphit_pos_set(self):
        """ This method just returns the tag-set used by the morph-it lexicon:
        >>> builder = lemmatizer_lookups_builder(in_path=path ...)
        >>> builder.morphit_pos_set()
        {'ABL', 'SENT', 'NUM', 'SYM', 'NPR', 'POSS', 'PON', 'ADV', 'VER', 'COM', 'SI', 'NOUN', 'MOD', 'AUX', 'TALE', 'PERS', 'INT', 'SMI', 'ASP', 'CARD', 'DEMO', 'CAU', 'ADJ', 'ARTPRE', 'CI', 'PRE', 'DET', 'ART', 'CON', 'INDEF', 'CE', 'CLI', 'PRO', 'CHE', 'WH', 'NE'}
        """
        morph_it_path = os.path.join(self.in_path, 'morph-it.txt')
        pos_set = set()
        with open(morph_it_path) as infile:
            line = infile.readline()
            while line:
                word, lemma, morph = line.replace('\n','').split('\t')
                pos_list = morph.split(':')[0].split('-')
                for pos in pos_list:
                    if pos.isupper() and len(pos)>1:
                        pos_set.add(pos)
                line = infile.readline()
        return pos_set

    def extract_pos_from_morphit(self, lookup_pos, lexicon_pos):
        """ Scans the entire morph-it lexicon and
            builds a lookup dict corresponding to an entry in the tag_map. """
        out_dict = OrderedDict()
        line = self.infile.readline()
        while line:
            try:
                word, lemma, morph = line.split('\t')
                for pos in lexicon_pos:
                    if pos in morph:
                        out_dict[word] = lemma
            except:
                print(len(line.split()), line.split())
            line = self.infile.readline()
        return out_dict

    def extract_lookup_tables(self, filename_pattern='it_lemma_lookup_{}.json'):
        """ Builds a lookup file (json) for each entry in the tag_map. """
        for lookup_pos, lexicon_pos in self.tag_map.items():
            self.infile = open(os.path.join(self.in_path, self.in_name), 'r')
            filename = filename_pattern.format(lookup_pos.lower())
            out_dict = self.extract_pos_from_morphit(lookup_pos, lexicon_pos)
            with open(os.path.join(self.out_path, filename), 'w') as outfile:
                outfile.write(json.dumps(out_dict, indent=2))
            self.infile.close()

    def make_lookups_bin(self, lookup_name_pattern='lemma_lookup_{}', filename_pattern='it_lemma_lookup_{}.json'):
        """ Merges the tables corresponding to the lookup files created by method "extract_lookup_tables"
            and an additional lookup table containing word forms found only in the "legacy" lookup file. """
        lookups = Lookups()
        lookup_keys = list(self.tag_map.keys())
        with open(os.path.join(self.out_path, 'it_lemma_lookup.json')) as json_legacy_file:
            legacy_dict = json.load(json_legacy_file)
            for lookup_pos in lookup_keys:
                lookup_name = lookup_name_pattern.format(lookup_pos.lower())
                filename = filename_pattern.format(lookup_pos.lower())
                with open(os.path.join(self.out_path, filename)) as json_file:
                    lookup_dict = json.load(json_file)
                lookups.add_table(lookup_name, lookup_dict)
                for word in lookup_dict.keys():
                    legacy_dict.pop(word, None)
            lookups.add_table('lemma_lookup_legacy', legacy_dict)
        lookups.to_disk(self.out_path, 'lookups.bin')

"""
In the sample code below, <path to morph-it.txt> refers to version 48 of the morph-it lexicon,
which can be downloaded from https://docs.sslmit.unibo.it/lib/exe/fetch.php?media=resources:morph-it.tgz ,
after expanding the compressed tar and converting to UTF-8 the text file morph-it_048.txt.
The same tar includes a copy of the lgpl licence and a readme file.
THE BINARY LOOKUPS FILE lookups.bin MUST BE MOVED/COPIED TO ALL ITALIAN LANGUAGE MODELS
AND THE [components.lemmatizer] SECTION OF THE config.cfg FILE MUST BE UPDATED (mode = "pos_lookup").

from spacy.lang.it.lemmatizer_lookups_builder import ItalianLemmatizerLookupsBuilder
in_name = 'morph-it.txt'
in_path = <path to morph-it.txt>
out_path = <local github directory for a fork of the spacy_lookups_data repository>
builder = ItalianLemmatizerLookupsBuilder(in_path=in_path, out_path=out_path, in_name=in_name)
builder.extract_lookup_tables()
builder.make_lookups_bin()
"""
