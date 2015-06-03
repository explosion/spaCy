import pytest
import os
from os import path

from spacy.munge.read_ontonotes import sgml_extract


text_data = open(path.join(path.dirname(__file__), 'web_sample1.sgm')).read()


def test_example_extract():
    article = sgml_extract(text_data)
    assert article['docid'] == 'blogspot.com_alaindewitt_20060924104100_ENG_20060924_104100'
    assert article['doctype'] == 'BLOG TEXT'
    assert article['datetime'] == '2006-09-24T10:41:00'
    assert article['headline'].strip() == 'Devastating Critique of the Arab World by One of Its Own'
    assert article['poster'] == 'Alain DeWitt'
    assert article['postdate'] == '2006-09-24T10:41:00'
    assert article['text'].startswith('Thanks again to my fri'), article['text'][:10]
    assert article['text'].endswith(' tide will turn."'), article['text'][-10:]
    assert '<' not in article['text'], article['text'][:10]


def test_directory():
    context_dir = '/usr/local/data/OntoNotes5/data/english/metadata/context/wb/sel'

    for fn in os.listdir(context_dir):
        with open(path.join(context_dir, fn)) as file_:
            text = file_.read()
        article = sgml_extract(text)

