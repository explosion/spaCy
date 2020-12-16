import srsly
from ..gold_io import json_iterate, json_to_annotations
from ..example import annotations_to_doc
from ..example import _fix_legacy_dict_data, _parse_example_dict_data
from ...util import load_model
from ...lang.xx import MultiLanguage


def json_to_docs(input_data, model=None, **kwargs):
    nlp = load_model(model) if model is not None else MultiLanguage()
    if not isinstance(input_data, bytes):
        if not isinstance(input_data, str):
            input_data = srsly.json_dumps(input_data)
        input_data = input_data.encode("utf8")
    for json_doc in json_iterate(input_data):
        for json_para in json_to_annotations(json_doc):
            example_dict = _fix_legacy_dict_data(json_para)
            tok_dict, doc_dict = _parse_example_dict_data(example_dict)
            doc = annotations_to_doc(nlp.vocab, tok_dict, doc_dict)
            yield doc
