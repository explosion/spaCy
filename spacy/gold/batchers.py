from typing import Union, Iterator, Iterable, Sequence, TypeVar, List, Callable
from functools import partial

from .example import Example
from ..util import registry


Sizing = Union[Iterator[int], int]
ItemT = TypeVar("ItemT")
Batcher = Callable[[Iterable[ItemT]], Iterable[List[ItemT]]]


@registry.batchers("batch_by_padded.v1")
def configure_minibatch_by_padded_size(
    *,
    size: Sizing,
    buffer: int,
    discard_oversize: bool,
    get_length: Optional[Callable[[ItemT], int]]=None
) -> Batcher:
    return partial(
        minibatch_by_padded_size,
        size=size,
        buffer=buffer,
        discard_oversize=discard_oversize,
        get_length=get_length
    )


@registry.batchers("batch_by_words.v1")
def configure_minibatch_by_words(
    *,
    size: Sizing,
    tolerance: float,
    discard_oversize: bool,
    get_length: Optional[Callable[[ItemT], int]]=None
) -> Batcher:
    return partial(
        minibatch_by_words,
        size=size,
        buffer=buffer,
        discard_oversize=discard_oversize,
        get_length=get_length
    )


@registry.batchers("batch_by_sequence.v1")
def configure_minibatch(size: Sizing, get_length=None) -> Batcher:
    return partial(minibatch(size=size, get_length=get_length)


def minibatch_by_padded_size(
    docs: Iterator["Doc"],
    size: Union[Iterator[int], int],
    buffer: int = 256,
    discard_oversize: bool = False,
    get_length: Optional[Callable]=len
) -> Iterator[Iterator["Doc"]]:
    if isinstance(size, int):
        size_ = itertools.repeat(size)
    else:
        size_ = size
    for outer_batch in minibatch(docs, size=buffer):
        outer_batch = list(outer_batch)
        target_size = next(size_)
        for indices in _batch_by_length(outer_batch, target_size, get_length):
            subbatch = [outer_batch[i] for i in indices]
            padded_size = max(len(seq) for seq in subbatch) * len(subbatch)
            if discard_oversize and padded_size >= target_size:
                pass
            else:
                yield subbatch


def minibatch_by_words(docs, size, tolerance=0.2, discard_oversize=False, get_length=len):
    """Create minibatches of roughly a given number of words. If any examples
    are longer than the specified batch length, they will appear in a batch by
    themselves, or be discarded if discard_oversize=True.
    The argument 'docs' can be a list of strings, Doc's or Example's. """
    if isinstance(size, int):
        size_ = itertools.repeat(size)
    elif isinstance(size, List):
        size_ = iter(size)
    else:
        size_ = size
    target_size = next(size_)
    tol_size = target_size * tolerance
    batch = []
    overflow = []
    batch_size = 0
    overflow_size = 0
    for doc in docs:
        n_words = get_length(doc)
        # if the current example exceeds the maximum batch size, it is returned separately
        # but only if discard_oversize=False.
        if n_words > target_size + tol_size:
            if not discard_oversize:
                yield [doc]
        # add the example to the current batch if there's no overflow yet and it still fits
        elif overflow_size == 0 and (batch_size + n_words) <= target_size:
            batch.append(doc)
            batch_size += n_words
        # add the example to the overflow buffer if it fits in the tolerance margin
        elif (batch_size + overflow_size + n_words) <= (target_size + tol_size):
            overflow.append(doc)
            overflow_size += n_words
        # yield the previous batch and start a new one. The new one gets the overflow examples.
        else:
            if batch:
                yield batch
            target_size = next(size_)
            tol_size = target_size * tolerance
            batch = overflow
            batch_size = overflow_size
            overflow = []
            overflow_size = 0
            # this example still fits
            if (batch_size + n_words) <= target_size:
                batch.append(doc)
                batch_size += n_words
            # this example fits in overflow
            elif (batch_size + n_words) <= (target_size + tol_size):
                overflow.append(doc)
                overflow_size += n_words
            # this example does not fit with the previous overflow: start another new batch
            else:
                if batch:
                    yield batch
                target_size = next(size_)
                tol_size = target_size * tolerance
                batch = [doc]
                batch_size = n_words
    batch.extend(overflow)
    if batch:
        yield batch


def minibatch(
    items: Iterable[Any], size: Sizing
) -> Iterator[Any]:
    """Iterate over batches of items. `size` may be an iterator,
    so that batch-size can vary on each step.
    """
    if isinstance(size, int):
        size_ = itertools.repeat(size)
    else:
        size_ = size
    items = iter(items)
    while True:
        batch_size = next(size_)
        batch = list(itertools.islice(items, int(batch_size)))
        if len(batch) == 0:
            break
        yield list(batch)


def _batch_by_length(seqs: Sequence[Any], max_words: int, get_length=len) -> List[List[Any]]:
    """Given a list of sequences, return a batched list of indices into the
    list, where the batches are grouped by length, in descending order.

    Batches may be at most max_words in size, defined as max sequence length * size.
    """
    # Use negative index so we can get sort by position ascending.
    lengths_indices = [(get_length(seq), i) for i, seq in enumerate(seqs)]
    lengths_indices.sort()
    batches = []
    batch = []
    for length, i in lengths_indices:
        if not batch:
            batch.append(i)
        elif length * (len(batch) + 1) <= max_words:
            batch.append(i)
        else:
            batches.append(batch)
            batch = [i]
    if batch:
        batches.append(batch)
    # Check lengths match
    assert sum(len(b) for b in batches) == len(seqs)
    batches = [list(sorted(batch)) for batch in batches]
    batches.reverse()
    return batches
