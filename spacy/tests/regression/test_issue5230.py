# coding: utf8
import warnings

import numpy
import pytest
import srsly

from spacy.kb import KnowledgeBase
from spacy.vectors import Vectors
from spacy.language import Language
from spacy.pipeline import Pipe
from spacy.tests.util import make_tempdir


def test_language_to_disk_resource_warning():
    nlp = Language()
    with make_tempdir() as d:
        with warnings.catch_warnings(record=True) as w:
            # catch only warnings raised in spacy.language since there may be others from other components or pipelines
            warnings.filterwarnings(
                "always", module="spacy.language", category=ResourceWarning
            )
            nlp.to_disk(d)
            assert len(w) == 0


def test_vectors_to_disk_resource_warning():
    data = numpy.zeros((3, 300), dtype="f")
    keys = ["cat", "dog", "rat"]
    vectors = Vectors(data=data, keys=keys)
    with make_tempdir() as d:
        with warnings.catch_warnings(record=True) as w:
            warnings.filterwarnings("always", category=ResourceWarning)
            vectors.to_disk(d)
            assert len(w) == 0


def test_custom_pipes_to_disk_resource_warning():
    # create dummy pipe partially implementing interface -- only want to test to_disk
    class SerializableDummy(object):
        def __init__(self, **cfg):
            if cfg:
                self.cfg = cfg
            else:
                self.cfg = None
            super(SerializableDummy, self).__init__()

        def to_bytes(self, exclude=tuple(), disable=None, **kwargs):
            return srsly.msgpack_dumps({"dummy": srsly.json_dumps(None)})

        def from_bytes(self, bytes_data, exclude):
            return self

        def to_disk(self, path, exclude=tuple(), **kwargs):
            pass

        def from_disk(self, path, exclude=tuple(), **kwargs):
            return self

    class MyPipe(Pipe):
        def __init__(self, vocab, model=True, **cfg):
            if cfg:
                self.cfg = cfg
            else:
                self.cfg = None
            self.model = SerializableDummy()
            self.vocab = SerializableDummy()

    pipe = MyPipe(None)
    with make_tempdir() as d:
        with warnings.catch_warnings(record=True) as w:
            warnings.filterwarnings("always", category=ResourceWarning)
            pipe.to_disk(d)
            assert len(w) == 0


def test_tagger_to_disk_resource_warning():
    nlp = Language()
    nlp.add_pipe(nlp.create_pipe("tagger"))
    tagger = nlp.get_pipe("tagger")
    # need to add model for two reasons:
    # 1. no model leads to error in serialization,
    # 2. the affected line is the one for model serialization
    tagger.begin_training(pipeline=nlp.pipeline)

    with make_tempdir() as d:
        with warnings.catch_warnings(record=True) as w:
            warnings.filterwarnings("always", category=ResourceWarning)
            tagger.to_disk(d)
            assert len(w) == 0


def test_entity_linker_to_disk_resource_warning():
    nlp = Language()
    nlp.add_pipe(nlp.create_pipe("entity_linker"))
    entity_linker = nlp.get_pipe("entity_linker")
    # need to add model for two reasons:
    # 1. no model leads to error in serialization,
    # 2. the affected line is the one for model serialization
    kb = KnowledgeBase(nlp.vocab, entity_vector_length=1)
    entity_linker.set_kb(kb)
    entity_linker.begin_training(pipeline=nlp.pipeline)

    with make_tempdir() as d:
        with warnings.catch_warnings(record=True) as w:
            warnings.filterwarnings("always", category=ResourceWarning)
            entity_linker.to_disk(d)
            assert len(w) == 0
