from typing import Iterable, List, Tuple
from contextlib import contextmanager
from pathlib import Path
import pytest
import tempfile

from spacy.lang.en import English
from spacy.training import Example, PlainTextCorpus

# Intentional newlines to check that they are skipped.
PLAIN_TEXT_DOC = """

This is a doc. It contains two sentences.
This is another doc.

A third doc.

"""

PLAIN_TEXT_DOC_TOKENIZED = [
    [
        "This",
        "is",
        "a",
        "doc",
        ".",
        "It",
        "contains",
        "two",
        "sentences",
        ".",
    ],
    ["This", "is", "another", "doc", "."],
    ["A", "third", "doc", "."],
]


@pytest.mark.parametrize("min_length, max_length", [(0, 0), (0, 5), (5, 0), (5, 5)])
def test_plain_text_reader(min_length, max_length):
    nlp = English()
    with _string_to_tmp_file(PLAIN_TEXT_DOC) as f:
        corpus = PlainTextCorpus(
            Path(f.name), min_length=min_length, max_length=max_length
        )

        check = [
            doc
            for doc in PLAIN_TEXT_DOC_TOKENIZED
            if len(doc) >= min_length and (max_length == 0 or len(doc) <= max_length)
        ]
        reference, predicted = _examples_to_tokens(corpus(nlp))

        assert reference == check
        assert predicted == check


@contextmanager
def _string_to_tmp_file(s: str):
    with tempfile.NamedTemporaryFile(suffix=".txt") as f:
        f.write(s.encode("utf-8"))
        f.seek(0)
        yield f


def _examples_to_tokens(
    examples: Iterable[Example],
) -> Tuple[List[List[str]], List[List[str]]]:
    reference = []
    predicted = []

    for eg in examples:
        reference.append([t.text for t in eg.reference])
        predicted.append([t.text for t in eg.predicted])

    return reference, predicted
