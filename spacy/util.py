import os
from os import path
import codecs
import json
import re

DATA_DIR = path.join(path.dirname(__file__), '..', 'data')


def utf8open(loc, mode='r'):
    return codecs.open(loc, mode, 'utf8')


def read_lang_data(name):
    data_dir = path.join(DATA_DIR, name)
    tokenization = read_tokenization(data_dir)
    prefix = read_prefix(data_dir)
    suffix = read_suffix(data_dir)
    words = load_resource(data_dir, 'words')
    probs = load_resource(data_dir, 'probs')
    clusters = load_resource(data_dir, 'clusters')
    case_stats = load_resource(data_dir, 'case_stats')
    tag_stats = load_resource(data_dir, 'tag_stats')
    return tokenization, prefix, suffix, words, probs, clusters, case_stats, tag_stats


def load_resource(data_dir, name):
    loc = path.join(data_dir, name + '.json')
    return json.load(loc) if path.exists(loc) else {}

def read_prefix(data_dir):
    with  utf8open(path.join(data_dir, 'prefix')) as file_:
        entries = file_.read().split('\n')
        expression = '|'.join(['^' + re.escape(piece) for piece in entries])
    return expression

def read_suffix(data_dir):
    with  utf8open(path.join(data_dir, 'suffix')) as file_:
        entries = file_.read().split('\n')
        expression = '|'.join([re.escape(piece) + '$' for piece in entries])
    return expression

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
