# coding: utf-8
from __future__ import unicode_literals

from ..util import ensure_path
from .. import util
from .. import displacy
from ..tokens import Span
from .util import get_doc
from .._ml import PrecomputableAffine

from pathlib import Path
import pytest
from thinc.neural._classes.maxout import Maxout
from thinc.neural._classes.softmax import Softmax
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
    ents = displacy.parse_ents(doc)
    assert isinstance(ents, dict)
    assert ents['text'] == 'But Google is starting from behind '
    assert ents['ents'] == [{'start': 4, 'end': 10, 'label': 'ORG'}]


def test_displacy_parse_deps(en_vocab):
    """Test that deps and tags on a Doc are converted into displaCy's format."""
    words = ["This", "is", "a", "sentence"]
    heads = [1, 0, 1, -2]
    pos = ['DET', 'VERB', 'DET', 'NOUN']
    tags = ['DT', 'VBZ', 'DT', 'NN']
    deps = ['nsubj', 'ROOT', 'det', 'attr']
    doc = get_doc(en_vocab, words=words, heads=heads, pos=pos, tags=tags,
                  deps=deps)
    deps = displacy.parse_deps(doc)
    assert isinstance(deps, dict)
    assert deps['words'] == [{'text': 'This', 'tag': 'DET'},
                            {'text': 'is', 'tag': 'VERB'},
                            {'text': 'a', 'tag': 'DET'},
                            {'text': 'sentence', 'tag': 'NOUN'}]
    assert deps['arcs'] == [{'start': 0, 'end': 1, 'label': 'nsubj', 'dir': 'left'},
                            {'start': 2, 'end': 3, 'label': 'det', 'dir': 'left'},
                            {'start': 1, 'end': 3, 'label': 'attr', 'dir': 'right'}]


def test_displacy_spans(en_vocab):
    """Test that displaCy can render Spans."""
    doc = get_doc(en_vocab, words=["But", "Google", "is", "starting", "from", "behind"])
    doc.ents = [Span(doc, 1, 2, label=doc.vocab.strings[u'ORG'])]
    html = displacy.render(doc[1:4], style='ent')
    assert html.startswith('<div')


def test_displacy_raises_for_wrong_type(en_vocab):
    with pytest.raises(ValueError):
        html = displacy.render('hello world')


def test_PrecomputableAffine(nO=4, nI=5, nF=3, nP=2):
    model = PrecomputableAffine(nO=nO, nI=nI, nF=nF, nP=nP)
    assert model.W.shape == (nF, nO, nP, nI)
    tensor = model.ops.allocate((10, nI))
    Y, get_dX = model.begin_update(tensor)
    assert Y.shape == (tensor.shape[0]+1, nF, nO, nP)
    assert model.d_pad.shape == (1, nF, nO, nP)
    dY = model.ops.allocate((15, nO, nP))
    ids = model.ops.allocate((15, nF))
    ids[1,2] = -1
    dY[1] = 1
    assert model.d_pad[0, 2, 0, 0] == 0.
    model._backprop_padding(dY, ids)
    assert model.d_pad[0, 2, 0, 0] == 1.
    model.d_pad.fill(0.)
    ids.fill(0.)
    dY.fill(0.)
    ids[1,2] = -1
    ids[1,1] = -1
    ids[1,0] = -1
    dY[1] = 1
    assert model.d_pad[0, 2, 0, 0] == 0.
    model._backprop_padding(dY, ids)
    assert model.d_pad[0, 2, 0, 0] == 3.
