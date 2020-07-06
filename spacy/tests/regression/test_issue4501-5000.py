import pytest
from mock import Mock
from spacy.pipeline import EntityRuler
from spacy.matcher import DependencyMatcher
from spacy.tokens import Doc, Span, DocBin
from spacy.gold import Example
from spacy.gold.converters.conllu2docs import conllu2docs
from spacy.lang.en import English
from spacy.kb import KnowledgeBase
from spacy.vocab import Vocab
from spacy.language import Language
from spacy.util import ensure_path, load_model_from_path
import numpy
import pickle

from ..util import get_doc, make_tempdir


def test_issue4528(en_vocab):
    """Test that user_data is correctly serialized in DocBin."""
    doc = Doc(en_vocab, words=["hello", "world"])
    doc.user_data["foo"] = "bar"
    # This is how extension attribute values are stored in the user data
    doc.user_data[("._.", "foo", None, None)] = "bar"
    doc_bin = DocBin(store_user_data=True)
    doc_bin.add(doc)
    doc_bin_bytes = doc_bin.to_bytes()
    new_doc_bin = DocBin(store_user_data=True).from_bytes(doc_bin_bytes)
    new_doc = list(new_doc_bin.get_docs(en_vocab))[0]
    assert new_doc.user_data["foo"] == "bar"
    assert new_doc.user_data[("._.", "foo", None, None)] == "bar"


@pytest.mark.parametrize(
    "text,words", [("A'B C", ["A", "'", "B", "C"]), ("A-B", ["A-B"])]
)
def test_gold_misaligned(en_tokenizer, text, words):
    doc = en_tokenizer(text)
    Example.from_dict(doc, {"words": words})


def test_issue4590(en_vocab):
    """Test that matches param in on_match method are the same as matches run with no on_match method"""
    pattern = [
        {"SPEC": {"NODE_NAME": "jumped"}, "PATTERN": {"ORTH": "jumped"}},
        {
            "SPEC": {"NODE_NAME": "fox", "NBOR_RELOP": ">", "NBOR_NAME": "jumped"},
            "PATTERN": {"ORTH": "fox"},
        },
        {
            "SPEC": {"NODE_NAME": "quick", "NBOR_RELOP": ".", "NBOR_NAME": "jumped"},
            "PATTERN": {"ORTH": "fox"},
        },
    ]

    on_match = Mock()
    matcher = DependencyMatcher(en_vocab)
    matcher.add("pattern", on_match, pattern)
    text = "The quick brown fox jumped over the lazy fox"
    heads = [3, 2, 1, 1, 0, -1, 2, 1, -3]
    deps = ["det", "amod", "amod", "nsubj", "ROOT", "prep", "det", "amod", "pobj"]
    doc = get_doc(en_vocab, text.split(), heads=heads, deps=deps)
    matches = matcher(doc)
    on_match_args = on_match.call_args
    assert on_match_args[0][3] == matches


def test_issue4651_with_phrase_matcher_attr():
    """Test that the EntityRuler PhraseMatcher is deserialize correctly using
    the method from_disk when the EntityRuler argument phrase_matcher_attr is
    specified.
    """
    text = "Spacy is a python library for nlp"
    nlp = English()
    ruler = EntityRuler(nlp, phrase_matcher_attr="LOWER")
    patterns = [{"label": "PYTHON_LIB", "pattern": "spacy", "id": "spaCy"}]
    ruler.add_patterns(patterns)
    nlp.add_pipe(ruler)
    doc = nlp(text)
    res = [(ent.text, ent.label_, ent.ent_id_) for ent in doc.ents]
    nlp_reloaded = English()
    with make_tempdir() as d:
        file_path = d / "entityruler"
        ruler.to_disk(file_path)
        ruler_reloaded = EntityRuler(nlp_reloaded).from_disk(file_path)
    nlp_reloaded.add_pipe(ruler_reloaded)
    doc_reloaded = nlp_reloaded(text)
    res_reloaded = [(ent.text, ent.label_, ent.ent_id_) for ent in doc_reloaded.ents]
    assert res == res_reloaded


def test_issue4651_without_phrase_matcher_attr():
    """Test that the EntityRuler PhraseMatcher is deserialize correctly using
    the method from_disk when the EntityRuler argument phrase_matcher_attr is
    not specified.
    """
    text = "Spacy is a python library for nlp"
    nlp = English()
    ruler = EntityRuler(nlp)
    patterns = [{"label": "PYTHON_LIB", "pattern": "spacy", "id": "spaCy"}]
    ruler.add_patterns(patterns)
    nlp.add_pipe(ruler)
    doc = nlp(text)
    res = [(ent.text, ent.label_, ent.ent_id_) for ent in doc.ents]
    nlp_reloaded = English()
    with make_tempdir() as d:
        file_path = d / "entityruler"
        ruler.to_disk(file_path)
        ruler_reloaded = EntityRuler(nlp_reloaded).from_disk(file_path)
    nlp_reloaded.add_pipe(ruler_reloaded)
    doc_reloaded = nlp_reloaded(text)
    res_reloaded = [(ent.text, ent.label_, ent.ent_id_) for ent in doc_reloaded.ents]
    assert res == res_reloaded


def test_issue4665():
    """
    conllu2json should not raise an exception if the HEAD column contains an
    underscore
    """
    input_data = """
1	[	_	PUNCT	-LRB-	_	_	punct	_	_
2	This	_	DET	DT	_	_	det	_	_
3	killing	_	NOUN	NN	_	_	nsubj	_	_
4	of	_	ADP	IN	_	_	case	_	_
5	a	_	DET	DT	_	_	det	_	_
6	respected	_	ADJ	JJ	_	_	amod	_	_
7	cleric	_	NOUN	NN	_	_	nmod	_	_
8	will	_	AUX	MD	_	_	aux	_	_
9	be	_	AUX	VB	_	_	aux	_	_
10	causing	_	VERB	VBG	_	_	root	_	_
11	us	_	PRON	PRP	_	_	iobj	_	_
12	trouble	_	NOUN	NN	_	_	dobj	_	_
13	for	_	ADP	IN	_	_	case	_	_
14	years	_	NOUN	NNS	_	_	nmod	_	_
15	to	_	PART	TO	_	_	mark	_	_
16	come	_	VERB	VB	_	_	acl	_	_
17	.	_	PUNCT	.	_	_	punct	_	_
18	]	_	PUNCT	-RRB-	_	_	punct	_	_
"""
    conllu2docs(input_data)


def test_issue4674():
    """Test that setting entities with overlapping identifiers does not mess up IO"""
    nlp = English()
    kb = KnowledgeBase(nlp.vocab, entity_vector_length=3)
    vector1 = [0.9, 1.1, 1.01]
    vector2 = [1.8, 2.25, 2.01]
    with pytest.warns(UserWarning):
        kb.set_entities(
            entity_list=["Q1", "Q1"],
            freq_list=[32, 111],
            vector_list=[vector1, vector2],
        )
    assert kb.get_size_entities() == 1
    # dumping to file & loading back in
    with make_tempdir() as d:
        dir_path = ensure_path(d)
        if not dir_path.exists():
            dir_path.mkdir()
        file_path = dir_path / "kb"
        kb.dump(str(file_path))
        kb2 = KnowledgeBase(vocab=nlp.vocab, entity_vector_length=3)
        kb2.load_bulk(str(file_path))
    assert kb2.get_size_entities() == 1


def test_issue4707():
    """Tests that disabled component names are also excluded from nlp.from_disk
    by default when loading a model.
    """
    nlp = English()
    nlp.add_pipe(nlp.create_pipe("sentencizer"))
    nlp.add_pipe(nlp.create_pipe("entity_ruler"))
    assert nlp.pipe_names == ["sentencizer", "entity_ruler"]
    exclude = ["tokenizer", "sentencizer"]
    with make_tempdir() as tmpdir:
        nlp.to_disk(tmpdir, exclude=exclude)
        new_nlp = load_model_from_path(tmpdir, disable=exclude)
    assert "sentencizer" not in new_nlp.pipe_names
    assert "entity_ruler" in new_nlp.pipe_names


@pytest.mark.filterwarnings("ignore::UserWarning")
def test_issue4725_1():
    """ Ensure the pickling of the NER goes well"""
    vocab = Vocab(vectors_name="test_vocab_add_vector")
    nlp = English(vocab=vocab)
    ner = nlp.create_pipe("ner", config={"min_action_freq": 342})
    with make_tempdir() as tmp_path:
        with (tmp_path / "ner.pkl").open("wb") as file_:
            pickle.dump(ner, file_)
            assert ner.cfg["min_action_freq"] == 342

        with (tmp_path / "ner.pkl").open("rb") as file_:
            ner2 = pickle.load(file_)
            assert ner2.cfg["min_action_freq"] == 342


@pytest.mark.filterwarnings("ignore::UserWarning")
def test_issue4725_2():
    # ensures that this runs correctly and doesn't hang or crash because of the global vectors
    # if it does crash, it's usually because of calling 'spawn' for multiprocessing (e.g. on Windows)
    vocab = Vocab(vectors_name="test_vocab_add_vector")
    data = numpy.ndarray((5, 3), dtype="f")
    data[0] = 1.0
    data[1] = 2.0
    vocab.set_vector("cat", data[0])
    vocab.set_vector("dog", data[1])
    nlp = English(vocab=vocab)
    ner = nlp.create_pipe("ner")
    nlp.add_pipe(ner)
    nlp.begin_training()
    docs = ["Kurt is in London."] * 10
    for _ in nlp.pipe(docs, batch_size=2, n_process=2):
        pass


def test_issue4849():
    nlp = English()
    ruler = EntityRuler(
        nlp,
        patterns=[
            {"label": "PERSON", "pattern": "joe biden", "id": "joe-biden"},
            {"label": "PERSON", "pattern": "bernie sanders", "id": "bernie-sanders"},
        ],
        phrase_matcher_attr="LOWER",
    )
    nlp.add_pipe(ruler)
    text = """
    The left is starting to take aim at Democratic front-runner Joe Biden.
    Sen. Bernie Sanders joined in her criticism: "There is no 'middle ground' when it comes to climate policy."
    """
    # USING 1 PROCESS
    count_ents = 0
    for doc in nlp.pipe([text], n_process=1):
        count_ents += len([ent for ent in doc.ents if ent.ent_id > 0])
    assert count_ents == 2
    # USING 2 PROCESSES
    count_ents = 0
    for doc in nlp.pipe([text], n_process=2):
        count_ents += len([ent for ent in doc.ents if ent.ent_id > 0])
    assert count_ents == 2


class CustomPipe:
    name = "my_pipe"

    def __init__(self):
        Span.set_extension("my_ext", getter=self._get_my_ext)
        Doc.set_extension("my_ext", default=None)

    def __call__(self, doc):
        gathered_ext = []
        for sent in doc.sents:
            sent_ext = self._get_my_ext(sent)
            sent._.set("my_ext", sent_ext)
            gathered_ext.append(sent_ext)

        doc._.set("my_ext", "\n".join(gathered_ext))

        return doc

    @staticmethod
    def _get_my_ext(span):
        return str(span.end)


def test_issue4903():
    """Ensure that this runs correctly and doesn't hang or crash on Windows /
    macOS."""
    nlp = English()
    custom_component = CustomPipe()
    nlp.add_pipe(nlp.create_pipe("sentencizer"))
    nlp.add_pipe(custom_component, after="sentencizer")

    text = ["I like bananas.", "Do you like them?", "No, I prefer wasabi."]
    docs = list(nlp.pipe(text, n_process=2))
    assert docs[0].text == "I like bananas."
    assert docs[1].text == "Do you like them?"
    assert docs[2].text == "No, I prefer wasabi."


def test_issue4924():
    nlp = Language()
    example = Example.from_dict(nlp.make_doc(""), {})
    nlp.evaluate([example])
