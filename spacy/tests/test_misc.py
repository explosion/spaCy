# coding: utf-8
from __future__ import unicode_literals

from ..util import ensure_path
from .. import util
from ..displacy import parse_deps, parse_ents
from ..tokens import Span
from .util import get_doc

from pathlib import Path
import pytest
from thinc.neural import Maxout, Softmax
from thinc.api import chain


@pytest.mark.parametrize('text', ['hello/world', 'hello world'])
def test_util_ensure_path_succeeds(text):
    path = util.ensure_path(text)
    assert isinstance(path, Path)


@pytest.mark.parametrize('package', ['numpy'])
def test_util_is_package(package):
    """Test that an installed package via pip is recognised by util.is_package."""
    assert util.is_package(package)


@pytest.mark.parametrize('package', ['thinc'])
def test_util_get_package_path(package):
    """Test that a Path object is returned for a package name."""
    path = util.get_package_path(package)
    assert isinstance(path, Path)


def test_displacy_parse_ents(en_vocab):
    """Test that named entities on a Doc are converted into displaCy's format."""
    doc = get_doc(en_vocab, words=["But", "Google", "is", "starting", "from", "behind"])
    doc.ents = [Span(doc, 1, 2, label=doc.vocab.strings[u'ORG'])]
    ents = parse_ents(doc)
    assert isinstance(ents, dict)
    assert ents['text'] == 'But Google is starting from behind '
    assert ents['ents'] == [{'start': 4, 'end': 10, 'label': 'ORG'}]


def test_displacy_parse_deps(en_vocab):
    """Test that deps and tags on a Doc are converted into displaCy's format."""
    words = ["This", "is", "a", "sentence"]
    heads = [1, 0, 1, -2]
    tags = ['DT', 'VBZ', 'DT', 'NN']
    deps = ['nsubj', 'ROOT', 'det', 'attr']
    doc = get_doc(en_vocab, words=words, heads=heads, tags=tags, deps=deps)
    deps = parse_deps(doc)
    assert isinstance(deps, dict)
    assert deps['words'] == [{'text': 'This', 'tag': 'DT'},
                            {'text': 'is', 'tag': 'VBZ'},
                            {'text': 'a', 'tag': 'DT'},
                            {'text': 'sentence', 'tag': 'NN'}]
    assert deps['arcs'] == [{'start': 0, 'end': 1, 'label': 'nsubj', 'dir': 'left'},
                            {'start': 2, 'end': 3, 'label': 'det', 'dir': 'left'},
                            {'start': 1, 'end': 3, 'label': 'attr', 'dir': 'right'}]
