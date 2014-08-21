import os
from os import path
import codecs
import json

DATA_DIR = path.join(path.dirname(__file__), '..', 'data')


def utf8open(loc, mode='r'):
    return codecs.open(loc, mode, 'utf8')


def load_case_stats(data_dir):
    case_loc = path.join(data_dir, 'case')
    case_stats = {}
    with utf8open(case_loc) as cases_file:
        for line in cases_file:
            word, upper, title = line.split()
            case_stats[word] = (float(upper), float(title))
    return case_stats


def read_dist_info(lang):
    dist_path = path.join(DATA_DIR, lang, 'distribution_info.json')
    if path.exists(dist_path):
        with open(dist_path) as file_:
            dist_info = json.load(file_)
    else:
        dist_info = {}
    return dist_info


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
            assert chunk not in seen, chunk
            seen.add(chunk)
            entries.append((chunk, list(pieces)))
            if chunk[0].isalpha() and chunk[0].islower():
                chunk = chunk[0].title() + chunk[1:]
                pieces[0] = pieces[0][0].title() + pieces[0][1:]
                seen.add(chunk)
                entries.append((chunk, pieces))
    return entries
