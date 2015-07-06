from __future__ import unicode_literals
import zlib
import gzip
import sqlite3
import os
from os import path
import sys


class DocsDB(object):
    def __init__(self, db_loc, batch_size=1000, limit=1000):
        limit = int(limit)
        batch_size = int(batch_size)
        self._conn = sqlite3.connect(db_loc)
        self._curr = self._conn.cursor()
        try:
            self._curr.execute('SELECT * FROM docs')
        except:
            print db_loc
            raise
        self._batch = self._curr.fetchmany(batch_size)
        self._batch_size = batch_size
        self._limit = limit

    def __iter__(self):
        while self._batch:
            for doc_id, compressed_doc in self._batch:
                if compressed_doc:
                    yield zlib.decompress(compressed_doc).decode('ascii')
                if doc_id >= self._limit:
                    self._batch = None
                    break
            else:
                self._batch = self._curr.fetchmany(size=self._batch_size)


class Gigaword(DocsDB):
    @classmethod
    def create(cls, giga_dir, db_loc):
        giga_dir = str(giga_dir)
        db_loc = str(db_loc)
        if path.exists(db_loc):
            os.unlink(db_loc)
        conn = sqlite3.connect(db_loc)
        c = conn.cursor()
        c.execute('''CREATE TABLE docs (id INTEGER PRIMARY KEY, body BLOB)''')
        doc_id = 0
        for file_loc in iter_files(giga_dir):
            print >> sys.stderr, file_loc
            for doc in iter_docs(file_loc):
                if doc.strip():
                    compressed = sqlite3.Binary(zlib.compress(doc))
                    c.execute('''INSERT INTO docs VALUES (?, ?)''', (doc_id, compressed))
                    doc_id += 1
            conn.commit()


def iter_files(giga_dir):
    for subdir in os.listdir(giga_dir):
        if not path.isdir(path.join(giga_dir, subdir)):
            continue
        for filename in os.listdir(path.join(giga_dir, subdir)):
            if filename.endswith('gz'):
                yield path.join(giga_dir, subdir, filename)
 

def iter_docs(zip_loc):
    doc = []
    para = []
    in_doc = False
    in_para = False
    try:
        lines = gzip.open(zip_loc, 'r').read().replace('&AMP;', '&').split('\n')
    except UnicodeDecodeError:
        lines = []
    for line in lines:
        line = line.strip()
        if not line:
            pass
        elif line[0] != '<':
            if in_para:
                para.append(line)
        elif line.startswith('<DOC'):
            in_doc = True
        elif line.startswith('<P>'):
            assert in_doc
            in_para = True
        elif line.startswith('</DOC'):
            assert not in_para
            in_doc = False
            yield '\n\n'.join(doc)
            doc = []
        elif line.startswith('</P>'):
            doc.append(' '.join(para))
            in_para = False
            para = []
        else:
            pass
    assert not in_doc
    assert not in_para
