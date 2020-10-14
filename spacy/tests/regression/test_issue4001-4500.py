import pytest
from spacy.pipeline import TrainablePipe
from spacy.matcher import PhraseMatcher, Matcher
from spacy.tokens import Doc, Span, DocBin
from spacy.training import Example, Corpus
from spacy.training.converters import json_to_docs
from spacy.vocab import Vocab
from spacy.lang.en import English
from spacy.util import minibatch, ensure_path, load_model
from spacy.util import compile_prefix_regex, compile_suffix_regex, compile_infix_regex
from spacy.tokenizer import Tokenizer
from spacy.lang.el import Greek
from spacy.language import Language
import spacy
from thinc.api import compounding
from collections import defaultdict

from ..util import make_tempdir


def test_issue4002(en_vocab):
    """Test that the PhraseMatcher can match on overwritten NORM attributes."""
    matcher = PhraseMatcher(en_vocab, attr="NORM")
    pattern1 = Doc(en_vocab, words=["c", "d"])
    assert [t.norm_ for t in pattern1] == ["c", "d"]
    matcher.add("TEST", [pattern1])
    doc = Doc(en_vocab, words=["a", "b", "c", "d"])
    assert [t.norm_ for t in doc] == ["a", "b", "c", "d"]
    matches = matcher(doc)
    assert len(matches) == 1
    matcher = PhraseMatcher(en_vocab, attr="NORM")
    pattern2 = Doc(en_vocab, words=["1", "2"])
    pattern2[0].norm_ = "c"
    pattern2[1].norm_ = "d"
    assert [t.norm_ for t in pattern2] == ["c", "d"]
    matcher.add("TEST", [pattern2])
    matches = matcher(doc)
    assert len(matches) == 1


def test_issue4030():
    """ Test whether textcat works fine with empty doc """
    unique_classes = ["offensive", "inoffensive"]
    x_train = [
        "This is an offensive text",
        "This is the second offensive text",
        "inoff",
    ]
    y_train = ["offensive", "offensive", "inoffensive"]
    nlp = spacy.blank("en")
    # preparing the data
    train_data = []
    for text, train_instance in zip(x_train, y_train):
        cat_dict = {label: label == train_instance for label in unique_classes}
        train_data.append(Example.from_dict(nlp.make_doc(text), {"cats": cat_dict}))
    # add a text categorizer component
    model = {
        "@architectures": "spacy.TextCatBOW.v1",
        "exclusive_classes": True,
        "ngram_size": 2,
        "no_output_layer": False,
    }
    textcat = nlp.add_pipe("textcat", config={"model": model}, last=True)
    for label in unique_classes:
        textcat.add_label(label)
    # training the network
    with nlp.select_pipes(enable="textcat"):
        optimizer = nlp.initialize()
        for i in range(3):
            losses = {}
            batches = minibatch(train_data, size=compounding(4.0, 32.0, 1.001))

            for batch in batches:
                nlp.update(examples=batch, sgd=optimizer, drop=0.1, losses=losses)
    # processing of an empty doc should result in 0.0 for all categories
    doc = nlp("")
    assert doc.cats["offensive"] == 0.0
    assert doc.cats["inoffensive"] == 0.0


def test_issue4042():
    """Test that serialization of an EntityRuler before NER works fine."""
    nlp = English()
    # add ner pipe
    ner = nlp.add_pipe("ner")
    ner.add_label("SOME_LABEL")
    nlp.initialize()
    # Add entity ruler
    patterns = [
        {"label": "MY_ORG", "pattern": "Apple"},
        {"label": "MY_GPE", "pattern": [{"lower": "san"}, {"lower": "francisco"}]},
    ]
    # works fine with "after"
    ruler = nlp.add_pipe("entity_ruler", before="ner")
    ruler.add_patterns(patterns)
    doc1 = nlp("What do you think about Apple ?")
    assert doc1.ents[0].label_ == "MY_ORG"

    with make_tempdir() as d:
        output_dir = ensure_path(d)
        if not output_dir.exists():
            output_dir.mkdir()
        nlp.to_disk(output_dir)
        nlp2 = load_model(output_dir)
        doc2 = nlp2("What do you think about Apple ?")
        assert doc2.ents[0].label_ == "MY_ORG"


def test_issue4042_bug2():
    """
    Test that serialization of an NER works fine when new labels were added.
    This is the second bug of two bugs underlying the issue 4042.
    """
    nlp1 = English()
    # add ner pipe
    ner1 = nlp1.add_pipe("ner")
    ner1.add_label("SOME_LABEL")
    nlp1.initialize()
    # add a new label to the doc
    doc1 = nlp1("What do you think about Apple ?")
    assert len(ner1.labels) == 1
    assert "SOME_LABEL" in ner1.labels
    apple_ent = Span(doc1, 5, 6, label="MY_ORG")
    doc1.ents = list(doc1.ents) + [apple_ent]
    # reapply the NER - at this point it should resize itself
    ner1(doc1)
    assert len(ner1.labels) == 2
    assert "SOME_LABEL" in ner1.labels
    assert "MY_ORG" in ner1.labels
    with make_tempdir() as d:
        # assert IO goes fine
        output_dir = ensure_path(d)
        if not output_dir.exists():
            output_dir.mkdir()
        ner1.to_disk(output_dir)
        config = {}
        ner2 = nlp1.create_pipe("ner", config=config)
        ner2.from_disk(output_dir)
        assert len(ner2.labels) == 2


def test_issue4054(en_vocab):
    """Test that a new blank model can be made with a vocab from file,
    and that serialization does not drop the language at any point."""
    nlp1 = English()
    vocab1 = nlp1.vocab
    with make_tempdir() as d:
        vocab_dir = ensure_path(d / "vocab")
        if not vocab_dir.exists():
            vocab_dir.mkdir()
        vocab1.to_disk(vocab_dir)
        vocab2 = Vocab().from_disk(vocab_dir)
        nlp2 = spacy.blank("en", vocab=vocab2)
        nlp_dir = ensure_path(d / "nlp")
        if not nlp_dir.exists():
            nlp_dir.mkdir()
        nlp2.to_disk(nlp_dir)
        nlp3 = load_model(nlp_dir)
        assert nlp3.lang == "en"


def test_issue4120(en_vocab):
    """Test that matches without a final {OP: ?} token are returned."""
    matcher = Matcher(en_vocab)
    matcher.add("TEST", [[{"ORTH": "a"}, {"OP": "?"}]])
    doc1 = Doc(en_vocab, words=["a"])
    assert len(matcher(doc1)) == 1  # works
    doc2 = Doc(en_vocab, words=["a", "b", "c"])
    assert len(matcher(doc2)) == 2  # fixed
    matcher = Matcher(en_vocab)
    matcher.add("TEST", [[{"ORTH": "a"}, {"OP": "?"}, {"ORTH": "b"}]])
    doc3 = Doc(en_vocab, words=["a", "b", "b", "c"])
    assert len(matcher(doc3)) == 2  # works
    matcher = Matcher(en_vocab)
    matcher.add("TEST", [[{"ORTH": "a"}, {"OP": "?"}, {"ORTH": "b", "OP": "?"}]])
    doc4 = Doc(en_vocab, words=["a", "b", "b", "c"])
    assert len(matcher(doc4)) == 3  # fixed


def test_issue4133(en_vocab):
    nlp = English()
    vocab_bytes = nlp.vocab.to_bytes()
    words = ["Apple", "is", "looking", "at", "buying", "a", "startup"]
    pos = ["NOUN", "VERB", "ADP", "VERB", "PROPN", "NOUN", "ADP"]
    doc = Doc(en_vocab, words=words)
    for i, token in enumerate(doc):
        token.pos_ = pos[i]
    # usually this is already True when starting from proper models instead of blank English
    doc_bytes = doc.to_bytes()
    vocab = Vocab()
    vocab = vocab.from_bytes(vocab_bytes)
    doc = Doc(vocab).from_bytes(doc_bytes)
    actual = []
    for token in doc:
        actual.append(token.pos_)
    assert actual == pos


def test_issue4190():
    def customize_tokenizer(nlp):
        prefix_re = compile_prefix_regex(nlp.Defaults.prefixes)
        suffix_re = compile_suffix_regex(nlp.Defaults.suffixes)
        infix_re = compile_infix_regex(nlp.Defaults.infixes)
        # Remove all exceptions where a single letter is followed by a period (e.g. 'h.')
        exceptions = {
            k: v
            for k, v in dict(nlp.Defaults.tokenizer_exceptions).items()
            if not (len(k) == 2 and k[1] == ".")
        }
        new_tokenizer = Tokenizer(
            nlp.vocab,
            exceptions,
            prefix_search=prefix_re.search,
            suffix_search=suffix_re.search,
            infix_finditer=infix_re.finditer,
            token_match=nlp.tokenizer.token_match,
        )
        nlp.tokenizer = new_tokenizer

    test_string = "Test c."
    # Load default language
    nlp_1 = English()
    doc_1a = nlp_1(test_string)
    result_1a = [token.text for token in doc_1a]  # noqa: F841
    # Modify tokenizer
    customize_tokenizer(nlp_1)
    doc_1b = nlp_1(test_string)
    result_1b = [token.text for token in doc_1b]
    # Save and Reload
    with make_tempdir() as model_dir:
        nlp_1.to_disk(model_dir)
        nlp_2 = load_model(model_dir)
    # This should be the modified tokenizer
    doc_2 = nlp_2(test_string)
    result_2 = [token.text for token in doc_2]
    assert result_1b == result_2


def test_issue4267():
    """ Test that running an entity_ruler after ner gives consistent results"""
    nlp = English()
    ner = nlp.add_pipe("ner")
    ner.add_label("PEOPLE")
    nlp.initialize()
    assert "ner" in nlp.pipe_names
    # assert that we have correct IOB annotations
    doc1 = nlp("hi")
    assert doc1.has_annotation("ENT_IOB")
    for token in doc1:
        assert token.ent_iob == 2
    # add entity ruler and run again
    patterns = [{"label": "SOFTWARE", "pattern": "spacy"}]
    ruler = nlp.add_pipe("entity_ruler")
    ruler.add_patterns(patterns)
    assert "entity_ruler" in nlp.pipe_names
    assert "ner" in nlp.pipe_names
    # assert that we still have correct IOB annotations
    doc2 = nlp("hi")
    assert doc2.has_annotation("ENT_IOB")
    for token in doc2:
        assert token.ent_iob == 2


@pytest.mark.skip(reason="lemmatizer lookups no longer in vocab")
def test_issue4272():
    """Test that lookup table can be accessed from Token.lemma if no POS tags
    are available."""
    nlp = Greek()
    doc = nlp("Χθες")
    assert doc[0].lemma_


def test_multiple_predictions():
    class DummyPipe(TrainablePipe):
        def __init__(self):
            self.model = "dummy_model"

        def predict(self, docs):
            return ([1, 2, 3], [4, 5, 6])

        def set_annotations(self, docs, scores):
            return docs

    nlp = Language()
    doc = nlp.make_doc("foo")
    dummy_pipe = DummyPipe()
    dummy_pipe(doc)


@pytest.mark.skip(reason="removed Beam stuff during the Example/GoldParse refactor")
def test_issue4313():
    """ This should not crash or exit with some strange error code """
    beam_width = 16
    beam_density = 0.0001
    nlp = English()
    config = {}
    ner = nlp.create_pipe("ner", config=config)
    ner.add_label("SOME_LABEL")
    ner.initialize(lambda: [])
    # add a new label to the doc
    doc = nlp("What do you think about Apple ?")
    assert len(ner.labels) == 1
    assert "SOME_LABEL" in ner.labels
    apple_ent = Span(doc, 5, 6, label="MY_ORG")
    doc.ents = list(doc.ents) + [apple_ent]

    # ensure the beam_parse still works with the new label
    docs = [doc]
    beams = nlp.entity.beam_parse(
        docs, beam_width=beam_width, beam_density=beam_density
    )

    for doc, beam in zip(docs, beams):
        entity_scores = defaultdict(float)
        for score, ents in nlp.entity.moves.get_beam_parses(beam):
            for start, end, label in ents:
                entity_scores[(start, end, label)] += score


def test_issue4348():
    """Test that training the tagger with empty data, doesn't throw errors"""
    nlp = English()
    example = Example.from_dict(nlp.make_doc(""), {"tags": []})
    TRAIN_DATA = [example, example]
    tagger = nlp.add_pipe("tagger")
    tagger.add_label("A")
    optimizer = nlp.initialize()
    for i in range(5):
        losses = {}
        batches = minibatch(TRAIN_DATA, size=compounding(4.0, 32.0, 1.001))
        for batch in batches:
            nlp.update(batch, sgd=optimizer, losses=losses)


def test_issue4367():
    """Test that docbin init goes well"""
    DocBin()
    DocBin(attrs=["LEMMA"])
    DocBin(attrs=["LEMMA", "ENT_IOB", "ENT_TYPE"])


def test_issue4373():
    """Test that PhraseMatcher.vocab can be accessed (like Matcher.vocab)."""
    matcher = Matcher(Vocab())
    assert isinstance(matcher.vocab, Vocab)
    matcher = PhraseMatcher(Vocab())
    assert isinstance(matcher.vocab, Vocab)


def test_issue4402():
    json_data = {
        "id": 0,
        "paragraphs": [
            {
                "raw": "How should I cook bacon in an oven?\nI've heard of people cooking bacon in an oven.",
                "sentences": [
                    {
                        "tokens": [
                            {"id": 0, "orth": "How", "ner": "O"},
                            {"id": 1, "orth": "should", "ner": "O"},
                            {"id": 2, "orth": "I", "ner": "O"},
                            {"id": 3, "orth": "cook", "ner": "O"},
                            {"id": 4, "orth": "bacon", "ner": "O"},
                            {"id": 5, "orth": "in", "ner": "O"},
                            {"id": 6, "orth": "an", "ner": "O"},
                            {"id": 7, "orth": "oven", "ner": "O"},
                            {"id": 8, "orth": "?", "ner": "O"},
                        ],
                        "brackets": [],
                    },
                    {
                        "tokens": [
                            {"id": 9, "orth": "\n", "ner": "O"},
                            {"id": 10, "orth": "I", "ner": "O"},
                            {"id": 11, "orth": "'ve", "ner": "O"},
                            {"id": 12, "orth": "heard", "ner": "O"},
                            {"id": 13, "orth": "of", "ner": "O"},
                            {"id": 14, "orth": "people", "ner": "O"},
                            {"id": 15, "orth": "cooking", "ner": "O"},
                            {"id": 16, "orth": "bacon", "ner": "O"},
                            {"id": 17, "orth": "in", "ner": "O"},
                            {"id": 18, "orth": "an", "ner": "O"},
                            {"id": 19, "orth": "oven", "ner": "O"},
                            {"id": 20, "orth": ".", "ner": "O"},
                        ],
                        "brackets": [],
                    },
                ],
                "cats": [
                    {"label": "baking", "value": 1.0},
                    {"label": "not_baking", "value": 0.0},
                ],
            },
            {
                "raw": "What is the difference between white and brown eggs?\n",
                "sentences": [
                    {
                        "tokens": [
                            {"id": 0, "orth": "What", "ner": "O"},
                            {"id": 1, "orth": "is", "ner": "O"},
                            {"id": 2, "orth": "the", "ner": "O"},
                            {"id": 3, "orth": "difference", "ner": "O"},
                            {"id": 4, "orth": "between", "ner": "O"},
                            {"id": 5, "orth": "white", "ner": "O"},
                            {"id": 6, "orth": "and", "ner": "O"},
                            {"id": 7, "orth": "brown", "ner": "O"},
                            {"id": 8, "orth": "eggs", "ner": "O"},
                            {"id": 9, "orth": "?", "ner": "O"},
                        ],
                        "brackets": [],
                    },
                    {"tokens": [{"id": 10, "orth": "\n", "ner": "O"}], "brackets": []},
                ],
                "cats": [
                    {"label": "baking", "value": 0.0},
                    {"label": "not_baking", "value": 1.0},
                ],
            },
        ],
    }
    nlp = English()
    attrs = ["ORTH", "SENT_START", "ENT_IOB", "ENT_TYPE"]
    with make_tempdir() as tmpdir:
        output_file = tmpdir / "test4402.spacy"
        docs = json_to_docs([json_data])
        data = DocBin(docs=docs, attrs=attrs).to_bytes()
        with output_file.open("wb") as file_:
            file_.write(data)
        reader = Corpus(output_file)
        train_data = list(reader(nlp))
        assert len(train_data) == 2

        split_train_data = []
        for eg in train_data:
            split_train_data.extend(eg.split_sents())
        assert len(split_train_data) == 4
