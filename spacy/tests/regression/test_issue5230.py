# coding: utf8
import warnings
from unittest import TestCase
import pytest
import srsly
from numpy import zeros
from spacy.kb import KnowledgeBase, Writer
from spacy.vectors import Vectors
from spacy.language import Language
from spacy.pipeline import Pipe
from spacy.compat import is_python2


from ..util import make_tempdir


def nlp():
    return Language()


def vectors():
    data = zeros((3, 1), dtype="f")
    keys = ["cat", "dog", "rat"]
    return Vectors(data=data, keys=keys)


def custom_pipe():
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

    return MyPipe(None)


def tagger():
    nlp = Language()
    nlp.add_pipe(nlp.create_pipe("tagger"))
    tagger = nlp.get_pipe("tagger")
    # need to add model for two reasons:
    # 1. no model leads to error in serialization,
    # 2. the affected line is the one for model serialization
    tagger.begin_training(pipeline=nlp.pipeline)
    return tagger


def entity_linker():
    nlp = Language()
    nlp.add_pipe(nlp.create_pipe("entity_linker"))
    entity_linker = nlp.get_pipe("entity_linker")
    # need to add model for two reasons:
    # 1. no model leads to error in serialization,
    # 2. the affected line is the one for model serialization
    kb = KnowledgeBase(nlp.vocab, entity_vector_length=1)
    entity_linker.set_kb(kb)
    entity_linker.begin_training(pipeline=nlp.pipeline)
    return entity_linker


objects_to_test = (
    [nlp(), vectors(), custom_pipe(), tagger(), entity_linker()],
    ["nlp", "vectors", "custom_pipe", "tagger", "entity_linker"],
)


def write_obj_and_catch_warnings(obj):
    with make_tempdir() as d:
        with warnings.catch_warnings(record=True) as warnings_list:
            warnings.filterwarnings("always", category=ResourceWarning)
            obj.to_disk(d)
            # in python3.5 it seems that deprecation warnings are not filtered by filterwarnings
            return list(filter(lambda x: isinstance(x, ResourceWarning), warnings_list))


@pytest.mark.skipif(is_python2, reason="ResourceWarning needs Python 3.x")
@pytest.mark.parametrize("obj", objects_to_test[0], ids=objects_to_test[1])
def test_to_disk_resource_warning(obj):
    warnings_list = write_obj_and_catch_warnings(obj)
    assert len(warnings_list) == 0


@pytest.mark.skipif(is_python2, reason="ResourceWarning needs Python 3.x")
def test_writer_with_path_py35():
    writer = None
    with make_tempdir() as d:
        path = d / "test"
        try:
            writer = Writer(path)
        except Exception as e:
            pytest.fail(str(e))
        finally:
            if writer:
                writer.close()


def test_save_and_load_knowledge_base():
    nlp = Language()
    kb = KnowledgeBase(nlp.vocab, entity_vector_length=1)
    with make_tempdir() as d:
        path = d / "kb"
        try:
            kb.dump(path)
        except Exception as e:
            pytest.fail(str(e))

        try:
            kb_loaded = KnowledgeBase(nlp.vocab, entity_vector_length=1)
            kb_loaded.load_bulk(path)
        except Exception as e:
            pytest.fail(str(e))


if not is_python2:

    class TestToDiskResourceWarningUnittest(TestCase):
        def test_resource_warning(self):
            scenarios = zip(*objects_to_test)

            for scenario in scenarios:
                with self.subTest(msg=scenario[1]):
                    warnings_list = write_obj_and_catch_warnings(scenario[0])
                    self.assertEqual(len(warnings_list), 0)
