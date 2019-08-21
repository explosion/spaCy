# coding: utf8
from __future__ import unicode_literals

import srsly

from ...gold import docs_to_json
from ...util import get_lang_class, minibatch


def ner_jsonl2json(input_data, lang=None, n_sents=10, use_morphology=False):
    if lang is None:
        raise ValueError("No --lang specified, but tokenization required")
    json_docs = []
    input_examples = [srsly.json_loads(line) for line in input_data.strip().split("\n")]
    nlp = get_lang_class(lang)()
    sentencizer = nlp.create_pipe("sentencizer")
    for i, batch in enumerate(minibatch(input_examples, size=n_sents)):
        docs = []
        for record in batch:
            raw_text = record["text"]
            if "entities" in record:
                ents = record["entities"]
            else:
                ents = record["spans"]
            ents = [(e["start"], e["end"], e["label"]) for e in ents]
            doc = nlp.make_doc(raw_text)
            sentencizer(doc)
            spans = [doc.char_span(s, e, label=L) for s, e, L in ents]
            doc.ents = _cleanup_spans(spans)
            docs.append(doc)
        json_docs.append(docs_to_json(docs, id=i))
    return json_docs


def _cleanup_spans(spans):
    output = []
    seen = set()
    for span in spans:
        if span is not None:
            # Trim whitespace
            while len(span) and span[0].is_space:
                span = span[1:]
            while len(span) and span[-1].is_space:
                span = span[:-1]
            if not len(span):
                continue
            for i in range(span.start, span.end):
                if i in seen:
                    break
            else:
                output.append(span)
                seen.update(range(span.start, span.end))
    return output
