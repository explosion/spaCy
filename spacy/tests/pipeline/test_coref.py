import pytest
import spacy
from spacy.matcher import PhraseMatcher
from spacy.training import Example
from spacy.lang.en import English
from spacy.tests.util import make_tempdir
from spacy.tokens import Doc
from spacy.pipeline.coref import DEFAULT_CLUSTERS_PREFIX
from spacy.pipeline.coref_er import DEFAULT_MENTIONS


# fmt: off
TRAIN_DATA = [
    (
        "John Smith told Laura that he was running late and asked her whether she could pick up their kids.",
        {
            "spans": {
                DEFAULT_MENTIONS: [
                    (0, 10, "MENTION"),
                    (16, 21, "MENTION"),
                    (27, 29, "MENTION"),
                    (57, 60, "MENTION"),
                    (69, 72, "MENTION"),
                    (87, 92, "MENTION"),
                    (87, 97, "MENTION"),
                ],
                f"{DEFAULT_CLUSTERS_PREFIX}_1": [
                    (0, 10, "MENTION"),     # John
                    (27, 29, "MENTION"),
                    (87, 92, "MENTION"),    # 'their' refers to John and Laur
                ],
                f"{DEFAULT_CLUSTERS_PREFIX}_2": [
                    (16, 21, "MENTION"),     # Laura
                    (57, 60, "MENTION"),
                    (69, 72, "MENTION"),
                    (87, 92, "MENTION"),     # 'their' refers to John and Laura
                ],
            }
        },
    ),
    (
        "Yes, I noticed that many friends around me received it. It seems that almost everyone received this SMS.",
        {
            "spans": {
                DEFAULT_MENTIONS: [
                    (5, 6, "MENTION"),
                    (40, 42, "MENTION"),
                    (52, 54, "MENTION"),
                    (95, 103, "MENTION"),
                ],
                f"{DEFAULT_CLUSTERS_PREFIX}_1": [
                    (5, 6, "MENTION"),      # I
                    (40, 42, "MENTION"),

                ],
                f"{DEFAULT_CLUSTERS_PREFIX}_2": [
                    (52, 54, "MENTION"),     # SMS
                    (95, 103, "MENTION"),
                ]
            }
        },
    ),
]
# fmt: on


@pytest.fixture
def nlp():
    return English()


@pytest.fixture
def examples(nlp):
    examples = []
    for text, annot in TRAIN_DATA:
        # eg = Example.from_dict(nlp.make_doc(text), annot)
        # if PR #7197 is merged, replace below with above line
        ref_doc = nlp.make_doc(text)
        for key, span_list in annot["spans"].items():
            spans = []
            for span_tuple in span_list:
                start_char = span_tuple[0]
                end_char = span_tuple[1]
                label = span_tuple[2]
                span = ref_doc.char_span(start_char, end_char, label=label)
                spans.append(span)
            ref_doc.spans[key] = spans
        eg = Example(nlp.make_doc(text), ref_doc)
        examples.append(eg)
    return examples


def test_coref_er_no_POS(nlp):
    doc = nlp("The police woman talked to him.")
    coref_er = nlp.add_pipe("coref_er", last=True)
    with pytest.raises(ValueError):
        coref_er(doc)


def test_coref_er_with_POS(nlp):
    words = ["The", "police", "woman", "talked", "to", "him", "."]
    pos = ["DET", "NOUN", "NOUN", "VERB", "ADP", "PRON", "PUNCT"]
    doc = Doc(nlp.vocab, words=words, pos=pos)
    coref_er = nlp.add_pipe("coref_er", last=True)
    coref_er(doc)
    assert len(doc.spans[coref_er.span_mentions]) == 1
    mention = doc.spans[coref_er.span_mentions][0]
    assert (mention.text, mention.start, mention.end) == ("him", 5, 6)


def test_coref_er_custom_POS(nlp):
    words = ["The", "police", "woman", "talked", "to", "him", "."]
    pos = ["DET", "NOUN", "NOUN", "VERB", "ADP", "PRON", "PUNCT"]
    doc = Doc(nlp.vocab, words=words, pos=pos)
    config = {"matcher_key": "POS", "matcher_values": ["NOUN"]}
    coref_er = nlp.add_pipe("coref_er", last=True, config=config)
    coref_er(doc)
    assert len(doc.spans[coref_er.span_mentions]) == 1
    mention = doc.spans[coref_er.span_mentions][0]
    assert (mention.text, mention.start, mention.end) == ("police woman", 1, 3)


def test_coref_clusters(nlp, examples):
    coref_er = nlp.add_pipe("coref_er", last=True)
    coref = nlp.add_pipe("coref", last=True)
    coref.initialize(lambda: examples)
    words = ["Laura", "walked", "her", "dog", "."]
    pos = ["PROPN", "VERB", "PRON", "NOUN", "PUNCT"]
    doc = Doc(nlp.vocab, words=words, pos=pos)
    coref_er(doc)
    coref(doc)
    assert len(doc.spans[coref_er.span_mentions]) > 0
    found_clusters = 0
    for name, spans in doc.spans.items():
        if name.startswith(coref.span_cluster_prefix):
            found_clusters += 1
    assert found_clusters > 0


def test_coref_er_score(nlp, examples):
    config = {"matcher_key": "POS", "matcher_values": []}
    coref_er = nlp.add_pipe("coref_er", last=True, config=config)
    coref = nlp.add_pipe("coref", last=True)
    coref.initialize(lambda: examples)
    mentions_key = coref_er.span_mentions
    cluster_prefix_key = coref.span_cluster_prefix
    matcher = PhraseMatcher(nlp.vocab)
    terms_1 = ["Laura", "her", "she"]
    terms_2 = ["it", "this SMS"]
    matcher.add("A", [nlp.make_doc(text) for text in terms_1])
    matcher.add("B", [nlp.make_doc(text) for text in terms_2])
    for eg in examples:
        pred = eg.predicted
        matches = matcher(pred, as_spans=True)
        pred.set_ents(matches)
        coref_er(pred)
        coref(pred)
        eg.predicted = pred
        # TODO: if #7209 is merged, experiment with 'include_label'
        scores = coref_er.score([eg])
        assert f"{mentions_key}_f" in scores
        scores = coref.score([eg])
        assert f"{cluster_prefix_key}_f" in scores


def test_coref_serialization(nlp):
    # Test that the coref component can be serialized
    config_er = {"matcher_key": "TAG", "matcher_values": ["NN"]}
    nlp.add_pipe("coref_er", last=True, config=config_er)
    nlp.add_pipe("coref", last=True)
    assert "coref_er" in nlp.pipe_names
    assert "coref" in nlp.pipe_names

    with make_tempdir() as tmp_dir:
        nlp.to_disk(tmp_dir)
        nlp2 = spacy.load(tmp_dir)
        assert "coref_er" in nlp2.pipe_names
        assert "coref" in nlp2.pipe_names
        coref_er_2 = nlp2.get_pipe("coref_er")
        assert coref_er_2.matcher_key == "TAG"
