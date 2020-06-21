import pytest

from .util import get_random_doc

from spacy.util import minibatch_by_words


@pytest.mark.parametrize(
    "doc_sizes, expected_batches",
    [
        ([400, 400, 199], [3]),
        ([400, 400, 199, 3], [4]),
        ([400, 400, 199, 3, 200], [3, 2]),
        ([400, 400, 199, 3, 1], [5]),
        ([400, 400, 199, 3, 1, 1500], [5]),  # 1500 will be discarded
        ([400, 400, 199, 3, 1, 200], [3, 3]),
        ([400, 400, 199, 3, 1, 999], [3, 3]),
        ([400, 400, 199, 3, 1, 999, 999], [3, 2, 1, 1]),
        ([1, 2, 999], [3]),
        ([1, 2, 999, 1], [4]),
        ([1, 200, 999, 1], [2, 2]),
        ([1, 999, 200, 1], [2, 2]),
    ],
)
def test_util_minibatch(doc_sizes, expected_batches):
    docs = [get_random_doc(doc_size) for doc_size in doc_sizes]
    tol = 0.2
    batch_size = 1000
    batches = list(
        minibatch_by_words(docs, size=batch_size, tolerance=tol, discard_oversize=True)
    )
    assert [len(batch) for batch in batches] == expected_batches

    max_size = batch_size + batch_size * tol
    for batch in batches:
        assert sum([len(doc) for doc in batch]) < max_size


@pytest.mark.parametrize(
    "doc_sizes, expected_batches",
    [
        ([400, 4000, 199], [1, 2]),
        ([400, 400, 199, 3000, 200], [1, 4]),
        ([400, 400, 199, 3, 1, 1500], [1, 5]),
        ([400, 400, 199, 3000, 2000, 200, 200], [1, 1, 3, 2]),
        ([1, 2, 9999], [1, 2]),
        ([2000, 1, 2000, 1, 1, 1, 2000], [1, 1, 1, 4]),
    ],
)
def test_util_minibatch_oversize(doc_sizes, expected_batches):
    """ Test that oversized documents are returned in their own batch"""
    docs = [get_random_doc(doc_size) for doc_size in doc_sizes]
    tol = 0.2
    batch_size = 1000
    batches = list(
        minibatch_by_words(docs, size=batch_size, tolerance=tol, discard_oversize=False)
    )
    assert [len(batch) for batch in batches] == expected_batches
