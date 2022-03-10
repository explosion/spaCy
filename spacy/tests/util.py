import numpy
import tempfile
import contextlib
import srsly
from spacy.tokens import Doc
from spacy.vocab import Vocab
from spacy.util import make_tempdir  # noqa: F401
from thinc.api import get_current_ops


@contextlib.contextmanager
def make_tempfile(mode="r"):
    f = tempfile.TemporaryFile(mode=mode)
    yield f
    f.close()


def get_batch(batch_size):
    vocab = Vocab()
    docs = []
    start = 0
    for size in range(1, batch_size + 1):
        # Make the words numbers, so that they're distinct
        # across the batch, and easy to track.
        numbers = [str(i) for i in range(start, start + size)]
        docs.append(Doc(vocab, words=numbers))
        start += size
    return docs


def get_random_doc(n_words):
    vocab = Vocab()
    # Make the words numbers, so that they're easy to track.
    numbers = [str(i) for i in range(0, n_words)]
    return Doc(vocab, words=numbers)


def apply_transition_sequence(parser, doc, sequence):
    """Perform a series of pre-specified transitions, to put the parser in a
    desired state."""
    for action_name in sequence:
        if "-" in action_name:
            move, label = action_name.split("-")
            parser.add_label(label)
    with parser.step_through(doc) as stepwise:
        for transition in sequence:
            stepwise.transition(transition)


def add_vecs_to_vocab(vocab, vectors):
    """Add list of vector tuples to given vocab. All vectors need to have the
    same length. Format: [("text", [1, 2, 3])]"""
    length = len(vectors[0][1])
    vocab.reset_vectors(width=length)
    for word, vec in vectors:
        vocab.set_vector(word, vector=vec)
    return vocab


def get_cosine(vec1, vec2):
    """Get cosine for two given vectors"""
    OPS = get_current_ops()
    v1 = OPS.to_numpy(OPS.asarray(vec1))
    v2 = OPS.to_numpy(OPS.asarray(vec2))
    return numpy.dot(v1, v2) / (numpy.linalg.norm(v1) * numpy.linalg.norm(v2))


def assert_docs_equal(doc1, doc2):
    """Compare two Doc objects and assert that they're equal. Tests for tokens,
    tags, dependencies and entities."""
    assert [t.orth for t in doc1] == [t.orth for t in doc2]

    assert [t.pos for t in doc1] == [t.pos for t in doc2]
    assert [t.tag for t in doc1] == [t.tag for t in doc2]

    assert [t.head.i for t in doc1] == [t.head.i for t in doc2]
    assert [t.dep for t in doc1] == [t.dep for t in doc2]
    assert [t.is_sent_start for t in doc1] == [t.is_sent_start for t in doc2]

    assert [t.ent_type for t in doc1] == [t.ent_type for t in doc2]
    assert [t.ent_iob for t in doc1] == [t.ent_iob for t in doc2]
    for ent1, ent2 in zip(doc1.ents, doc2.ents):
        assert ent1.start == ent2.start
        assert ent1.end == ent2.end
        assert ent1.label == ent2.label
        assert ent1.kb_id == ent2.kb_id


def assert_packed_msg_equal(b1, b2):
    """Assert that two packed msgpack messages are equal."""
    msg1 = srsly.msgpack_loads(b1)
    msg2 = srsly.msgpack_loads(b2)
    assert sorted(msg1.keys()) == sorted(msg2.keys())
    for (k1, v1), (k2, v2) in zip(sorted(msg1.items()), sorted(msg2.items())):
        assert k1 == k2
        assert v1 == v2
