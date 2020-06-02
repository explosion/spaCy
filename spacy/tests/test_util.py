import pytest
from spacy.gold import Example

from .util import get_doc

from spacy.util import minibatch_by_words


@pytest.mark.parametrize(
    "doc_sizes, expected_batches",
    [
        ([400, 400, 199], [3]),
        ([400, 400, 199, 3], [4]),
        ([400, 400, 199, 3, 250], [3, 2]),
    ],
)
def test_util_minibatch(doc_sizes, expected_batches):
    docs = [get_doc(doc_size) for doc_size in doc_sizes]

    examples = [Example(doc=doc) for doc in docs]

    batches = list(minibatch_by_words(examples=examples, size=1000))
    assert [len(batch) for batch in batches] == expected_batches
