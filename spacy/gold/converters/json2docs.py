import tempfile
import contextlib
import shutil
from pathlib import Path
from ..gold_io import json_to_annotations
from ..example import annotations2doc
from ..example import _fix_legacy_dict_data, _parse_example_dict_data
from ...util import load_model
from ...lang.xx import MultiLanguage


@contextlib.contextmanager
def make_tempdir():
    d = Path(tempfile.mkdtemp())
    yield d
    shutil.rmtree(str(d))


def json2docs(input_data, model=None, **kwargs):
    nlp = load_model(model) if model is not None else MultiLanguage()
    docs = []
    for json_annot in json_to_annotations(input_data):
        example_dict = _fix_legacy_dict_data(json_annot)
        tok_dict, doc_dict = _parse_example_dict_data(example_dict)
        doc = annotations2doc(nlp.vocab, tok_dict, doc_dict)
        docs.append(doc)
    return docs
