import os
from os import path
import codecs

DATA_DIR = path.join(path.dirname(__file__), '..', 'data')


def utf8open(loc, mode='r'):
    return codecs.open(loc, mode, 'utf8')


def load_case_stats(data_dir):
    case_loc = path.join(data_dir, 'english.case')
    case_stats = {}
    with utf8open(case_loc) as cases_file:
        for line in cases_file:
            word, upper, title = line.split()
            case_stats[word] = (float(upper), float(title))
    return case_stats


def read_tokenization(lang):
    loc = path.join(DATA_DIR, lang, 'tokenization')
    entries = []
    seen = set()
    with utf8open(loc) as file_:
        for line in file_:
            line = line.strip()
            if line.startswith('#'):
                continue
            if not line:
                continue
            pieces = line.split()
            chunk = pieces.pop(0)
            lex = pieces.pop(0)
            assert chunk not in seen, chunk
            seen.add(chunk)
            entries.append((chunk, lex, pieces))
    return entries
 

"""
    def load_browns(self, data_dir):
        cdef Lexeme* w
        case_stats = load_case_stats(data_dir)
        brown_loc = path.join(data_dir, 'bllip-clusters')
        assert path.exists(brown_loc)
        cdef size_t start 
        cdef int end 
        with utf8open(brown_loc) as browns_file:
            for i, line in enumerate(browns_file):
                cluster_str, word, freq_str = line.split()
                # Decode as a little-endian string, so that we can do & 15 to get
                # the first 4 bits. See redshift._parse_features.pyx
                cluster = int(cluster_str[::-1], 2)
                upper_pc, title_pc = case_stats.get(word.lower(), (0.0, 0.0))
                start = 0
                end = -1
                find_slice(&start, &end, word)
                print "Load", repr(word), start, end
                w = <Lexeme*>init_word(word, start, end, cluster,
                                      upper_pc, title_pc, int(freq_str))
                self.words[_hash_str(word)] = <size_t>w
                self.strings[<size_t>w] = word

    def load_clitics(self, data_dir):
        cdef unicode orig_str
        cdef unicode clitic
        for orig_str, norm_form, clitic_strs in util.load_clitics(data_dir):
            w = init_clitic(orig_str, <Lexeme*>self.lookup_slice(norm_form, 0, -1))
            self.words[w.orig] = <size_t>w
            self.strings[<size_t>w] = orig_str
            assert len(clitic_strs) < MAX_CLITICS
            assert clitic_strs
            for i, clitic in enumerate(clitic_strs):
                # If we write punctuation here, assume we want to keep it,
                # so tell it the slice boundaries (the full string)
                w.clitics[i] = self.lookup_slice(clitic, 0, -1)
            # Ensure we null terminate
            w.clitics[i+1] = 0
"""

