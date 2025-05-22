import itertools
from functools import partial
from typing import (
    Any,
    Callable,
    Iterable,
    Iterator,
    List,
    Optional,
    Sequence,
    TypeVar,
    Union,
)

from ..util import minibatch, registry

Sizing = Union[Sequence[int], int]
ItemT = TypeVar("ItemT")
BatcherT = Callable[[Iterable[ItemT]], Iterable[List[ItemT]]]


def configure_minibatch_by_padded_size(
    *,
    size: Sizing,
    buffer: int,
    discard_oversize: bool,
    get_length: Optional[Callable[[ItemT], int]] = None
) -> BatcherT:
    """Create a batcher that uses the `batch_by_padded_size` strategy.

    The padded size is defined as the maximum length of sequences within the
    batch multiplied by the number of sequences in the batch.

    size (int or Sequence[int]): The largest padded size to batch sequences into.
        Can be a single integer, or a sequence, allowing for variable batch sizes.
    buffer (int): The number of sequences to accumulate before sorting by length.
        A larger buffer will result in more even sizing, but if the buffer is
        very large, the iteration order will be less random, which can result
        in suboptimal training.
    discard_oversize (bool): Whether to discard sequences that are by themselves
        longer than the largest padded batch size.
    get_length (Callable or None): Function to get the length of a sequence item.
        The `len` function is used by default.
    """
    # Avoid displacing optional values from the underlying function.
    optionals = {"get_length": get_length} if get_length is not None else {}
    return partial(
        minibatch_by_padded_size,
        size=size,
        buffer=buffer,
        discard_oversize=discard_oversize,
        **optionals
    )


def configure_minibatch_by_words(
    *,
    size: Sizing,
    tolerance: float,
    discard_oversize: bool,
    get_length: Optional[Callable[[ItemT], int]] = None
) -> BatcherT:
    """Create a batcher that uses the "minibatch by words" strategy.

    size (int or Sequence[int]): The target number of words per batch.
        Can be a single integer, or a sequence, allowing for variable batch sizes.
    tolerance (float): What percentage of the size to allow batches to exceed.
    discard_oversize (bool): Whether to discard sequences that by themselves
        exceed the tolerated size.
    get_length (Callable or None): Function to get the length of a sequence
        item. The `len` function is used by default.
    """
    optionals = {"get_length": get_length} if get_length is not None else {}
    return partial(
        minibatch_by_words,
        size=size,
        tolerance=tolerance,
        discard_oversize=discard_oversize,
        **optionals
    )


def configure_minibatch(
    size: Sizing, get_length: Optional[Callable[[ItemT], int]] = None
) -> BatcherT:
    """Create a batcher that creates batches of the specified size.

    size (int or Sequence[int]): The target number of items per batch.
        Can be a single integer, or a sequence, allowing for variable batch sizes.
    """
    optionals = {"get_length": get_length} if get_length is not None else {}
    return partial(minibatch, size=size, **optionals)


def minibatch_by_padded_size(
    seqs: Iterable[ItemT],
    size: Sizing,
    buffer: int = 256,
    discard_oversize: bool = False,
    get_length: Callable = len,
) -> Iterable[List[ItemT]]:
    """Minibatch a sequence by the size of padded batches that would result,
    with sequences binned by length within a window.

    The padded size is defined as the maximum length of sequences within the
    batch multiplied by the number of sequences in the batch.

    size (int or Sequence[int]): The largest padded size to batch sequences into.
    buffer (int): The number of sequences to accumulate before sorting by length.
        A larger buffer will result in more even sizing, but if the buffer is
        very large, the iteration order will be less random, which can result
        in suboptimal training.
    discard_oversize (bool): Whether to discard sequences that are by themselves
        longer than the largest padded batch size.
    get_length (Callable or None): Function to get the length of a sequence item.
        The `len` function is used by default.
    """
    if isinstance(size, int):
        size_ = itertools.repeat(size)  # type: Iterator[int]
    else:
        size_ = iter(size)
    for outer_batch in minibatch(seqs, size=buffer):
        outer_batch = list(outer_batch)
        target_size = next(size_)
        for indices in _batch_by_length(outer_batch, target_size, get_length):
            subbatch = [outer_batch[i] for i in indices]
            padded_size = max(len(seq) for seq in subbatch) * len(subbatch)
            if discard_oversize and padded_size >= target_size:
                pass
            else:
                yield subbatch


def minibatch_by_words(
    seqs: Iterable[ItemT],
    size: Sizing,
    tolerance=0.2,
    discard_oversize=False,
    get_length=len,
) -> Iterable[List[ItemT]]:
    """Create minibatches of roughly a given number of words. If any examples
    are longer than the specified batch length, they will appear in a batch by
    themselves, or be discarded if discard_oversize=True.

    seqs (Iterable[Sequence]): The sequences to minibatch.
    size (int or Sequence[int]): The target number of words per batch.
        Can be a single integer, or a sequence, allowing for variable batch sizes.
    tolerance (float): What percentage of the size to allow batches to exceed.
    discard_oversize (bool): Whether to discard sequences that by themselves
        exceed the tolerated size.
    get_length (Callable or None): Function to get the length of a sequence
        item. The `len` function is used by default.
    """
    if isinstance(size, int):
        size_ = itertools.repeat(size)  # type: Iterator[int]
    else:
        size_ = iter(size)
    target_size = next(size_)
    tol_size = target_size * tolerance
    batch = []
    overflow = []
    batch_size = 0
    overflow_size = 0
    for seq in seqs:
        n_words = get_length(seq)
        # if the current example exceeds the maximum batch size, it is returned separately
        # but only if discard_oversize=False.
        if n_words > target_size + tol_size:
            if not discard_oversize:
                yield [seq]
        # add the example to the current batch if there's no overflow yet and it still fits
        elif overflow_size == 0 and (batch_size + n_words) <= target_size:
            batch.append(seq)
            batch_size += n_words
        # add the example to the overflow buffer if it fits in the tolerance margin
        elif (batch_size + overflow_size + n_words) <= (target_size + tol_size):
            overflow.append(seq)
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
                batch.append(seq)
                batch_size += n_words
            # this example fits in overflow
            elif (batch_size + n_words) <= (target_size + tol_size):
                overflow.append(seq)
                overflow_size += n_words
            # this example does not fit with the previous overflow: start another new batch
            else:
                if batch:
                    yield batch
                target_size = next(size_)
                tol_size = target_size * tolerance
                batch = [seq]
                batch_size = n_words
    batch.extend(overflow)
    if batch:
        yield batch


def _batch_by_length(
    seqs: Sequence[Any], max_words: int, get_length=len
) -> List[List[Any]]:
    """Given a list of sequences, return a batched list of indices into the
    list, where the batches are grouped by length, in descending order.

    Batches may be at most max_words in size, defined as max sequence length * size.
    """
    # Use negative index so we can get sort by position ascending.
    lengths_indices = [(get_length(seq), i) for i, seq in enumerate(seqs)]
    lengths_indices.sort()
    batches = []
    batch: List[int] = []
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
