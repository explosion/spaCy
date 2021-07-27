from spacy.cli.evaluate import print_textcats_auc_per_cat, print_prf_per_type
from spacy.lang.en import English
from spacy.training import Example
from spacy.tokens.doc import Doc
from spacy.vocab import Vocab
from spacy.kb import KnowledgeBase
from spacy.pipeline._parser_internals.arc_eager import ArcEager
from spacy.util import load_config_from_str, load_config
from spacy.cli.init_config import fill_config
from thinc.api import Config
from wasabi import msg

from ..util import make_tempdir


def test_issue7019():
    scores = {"LABEL_A": 0.39829102, "LABEL_B": 0.938298329382, "LABEL_C": None}
    print_textcats_auc_per_cat(msg, scores)
    scores = {
        "LABEL_A": {"p": 0.3420302, "r": 0.3929020, "f": 0.49823928932},
        "LABEL_B": {"p": None, "r": None, "f": None},
    }
    print_prf_per_type(msg, scores, name="foo", type="bar")


CONFIG_7029 = """
[nlp]
lang = "en"
pipeline = ["tok2vec", "tagger"]

[components]

[components.tok2vec]
factory = "tok2vec"

[components.tok2vec.model]
@architectures = "spacy.Tok2Vec.v1"

[components.tok2vec.model.embed]
@architectures = "spacy.MultiHashEmbed.v1"
width = ${components.tok2vec.model.encode:width}
attrs = ["NORM","PREFIX","SUFFIX","SHAPE"]
rows = [5000,2500,2500,2500]
include_static_vectors = false

[components.tok2vec.model.encode]
@architectures = "spacy.MaxoutWindowEncoder.v1"
width = 96
depth = 4
window_size = 1
maxout_pieces = 3

[components.tagger]
factory = "tagger"

[components.tagger.model]
@architectures = "spacy.Tagger.v1"
nO = null

[components.tagger.model.tok2vec]
@architectures = "spacy.Tok2VecListener.v1"
width = ${components.tok2vec.model.encode:width}
upstream = "*"
"""


def test_issue7029():
    """Test that an empty document doesn't mess up an entire batch."""
    TRAIN_DATA = [
        ("I like green eggs", {"tags": ["N", "V", "J", "N"]}),
        ("Eat blue ham", {"tags": ["V", "J", "N"]}),
    ]
    nlp = English.from_config(load_config_from_str(CONFIG_7029))
    train_examples = []
    for t in TRAIN_DATA:
        train_examples.append(Example.from_dict(nlp.make_doc(t[0]), t[1]))
    optimizer = nlp.initialize(get_examples=lambda: train_examples)
    for i in range(50):
        losses = {}
        nlp.update(train_examples, sgd=optimizer, losses=losses)
    texts = ["first", "second", "third", "fourth", "and", "then", "some", ""]
    docs1 = list(nlp.pipe(texts, batch_size=1))
    docs2 = list(nlp.pipe(texts, batch_size=4))
    assert [doc[0].tag_ for doc in docs1[:-1]] == [doc[0].tag_ for doc in docs2[:-1]]


def test_issue7055():
    """Test that fill-config doesn't turn sourced components into factories."""
    source_cfg = {
        "nlp": {"lang": "en", "pipeline": ["tok2vec", "tagger"]},
        "components": {
            "tok2vec": {"factory": "tok2vec"},
            "tagger": {"factory": "tagger"},
        },
    }
    source_nlp = English.from_config(source_cfg)
    with make_tempdir() as dir_path:
        # We need to create a loadable source pipeline
        source_path = dir_path / "test_model"
        source_nlp.to_disk(source_path)
        base_cfg = {
            "nlp": {"lang": "en", "pipeline": ["tok2vec", "tagger", "ner"]},
            "components": {
                "tok2vec": {"source": str(source_path)},
                "tagger": {"source": str(source_path)},
                "ner": {"factory": "ner"},
            },
        }
        base_cfg = Config(base_cfg)
        base_path = dir_path / "base.cfg"
        base_cfg.to_disk(base_path)
        output_path = dir_path / "config.cfg"
        fill_config(output_path, base_path, silent=True)
        filled_cfg = load_config(output_path)
    assert filled_cfg["components"]["tok2vec"]["source"] == str(source_path)
    assert filled_cfg["components"]["tagger"]["source"] == str(source_path)
    assert filled_cfg["components"]["ner"]["factory"] == "ner"
    assert "model" in filled_cfg["components"]["ner"]


def test_issue7056():
    """Test that the Unshift transition works properly, and doesn't cause
    sentence segmentation errors."""
    vocab = Vocab()
    ae = ArcEager(
        vocab.strings, ArcEager.get_actions(left_labels=["amod"], right_labels=["pobj"])
    )
    doc = Doc(vocab, words="Severe pain , after trauma".split())
    state = ae.init_batch([doc])[0]
    ae.apply_transition(state, "S")
    ae.apply_transition(state, "L-amod")
    ae.apply_transition(state, "S")
    ae.apply_transition(state, "S")
    ae.apply_transition(state, "S")
    ae.apply_transition(state, "R-pobj")
    ae.apply_transition(state, "D")
    ae.apply_transition(state, "D")
    ae.apply_transition(state, "D")
    assert not state.eol()


def test_partial_links():
    # Test that having some entities on the doc without gold links, doesn't crash
    TRAIN_DATA = [
        (
            "Russ Cochran his reprints include EC Comics.",
            {
                "links": {(0, 12): {"Q2146908": 1.0}},
                "entities": [(0, 12, "PERSON")],
                "sent_starts": [1, -1, 0, 0, 0, 0, 0, 0],
            },
        )
    ]
    nlp = English()
    vector_length = 3
    train_examples = []
    for text, annotation in TRAIN_DATA:
        doc = nlp(text)
        train_examples.append(Example.from_dict(doc, annotation))

    def create_kb(vocab):
        # create artificial KB
        mykb = KnowledgeBase(vocab, entity_vector_length=vector_length)
        mykb.add_entity(entity="Q2146908", freq=12, entity_vector=[6, -4, 3])
        mykb.add_alias("Russ Cochran", ["Q2146908"], [0.9])
        return mykb

    # Create and train the Entity Linker
    entity_linker = nlp.add_pipe("entity_linker", last=True)
    entity_linker.set_kb(create_kb)
    optimizer = nlp.initialize(get_examples=lambda: train_examples)
    for i in range(2):
        losses = {}
        nlp.update(train_examples, sgd=optimizer, losses=losses)

    # adding additional components that are required for the entity_linker
    nlp.add_pipe("sentencizer", first=True)
    patterns = [
        {"label": "PERSON", "pattern": [{"LOWER": "russ"}, {"LOWER": "cochran"}]},
        {"label": "ORG", "pattern": [{"LOWER": "ec"}, {"LOWER": "comics"}]},
    ]
    ruler = nlp.add_pipe("entity_ruler", before="entity_linker")
    ruler.add_patterns(patterns)

    # this will run the pipeline on the examples and shouldn't crash
    results = nlp.evaluate(train_examples)
    assert "PERSON" in results["ents_per_type"]
    assert "PERSON" in results["nel_f_per_type"]
    assert "ORG" in results["ents_per_type"]
    assert "ORG" not in results["nel_f_per_type"]


def test_issue7065():
    text = "Kathleen Battle sang in Mahler 's Symphony No. 8 at the Cincinnati Symphony Orchestra 's May Festival."
    nlp = English()
    nlp.add_pipe("sentencizer")
    ruler = nlp.add_pipe("entity_ruler")
    patterns = [
        {
            "label": "THING",
            "pattern": [
                {"LOWER": "symphony"},
                {"LOWER": "no"},
                {"LOWER": "."},
                {"LOWER": "8"},
            ],
        }
    ]
    ruler.add_patterns(patterns)

    doc = nlp(text)
    sentences = [s for s in doc.sents]
    assert len(sentences) == 2
    sent0 = sentences[0]
    ent = doc.ents[0]
    assert ent.start < sent0.end < ent.end
    assert sentences.index(ent.sent) == 0


def test_issue7065_b():
    # Test that the NEL doesn't crash when an entity crosses a sentence boundary
    nlp = English()
    vector_length = 3
    nlp.add_pipe("sentencizer")
    text = "Mahler 's Symphony No. 8 was beautiful."
    entities = [(0, 6, "PERSON"), (10, 24, "WORK")]
    links = {
        (0, 6): {"Q7304": 1.0, "Q270853": 0.0},
        (10, 24): {"Q7304": 0.0, "Q270853": 1.0},
    }
    sent_starts = [1, -1, 0, 0, 0, 0, 0, 0, 0]
    doc = nlp(text)
    example = Example.from_dict(
        doc, {"entities": entities, "links": links, "sent_starts": sent_starts}
    )
    train_examples = [example]

    def create_kb(vocab):
        # create artificial KB
        mykb = KnowledgeBase(vocab, entity_vector_length=vector_length)
        mykb.add_entity(entity="Q270853", freq=12, entity_vector=[9, 1, -7])
        mykb.add_alias(
            alias="No. 8",
            entities=["Q270853"],
            probabilities=[1.0],
        )
        mykb.add_entity(entity="Q7304", freq=12, entity_vector=[6, -4, 3])
        mykb.add_alias(
            alias="Mahler",
            entities=["Q7304"],
            probabilities=[1.0],
        )
        return mykb

    # Create the Entity Linker component and add it to the pipeline
    entity_linker = nlp.add_pipe("entity_linker", last=True)
    entity_linker.set_kb(create_kb)
    # train the NEL pipe
    optimizer = nlp.initialize(get_examples=lambda: train_examples)
    for i in range(2):
        losses = {}
        nlp.update(train_examples, sgd=optimizer, losses=losses)

    # Add a custom rule-based component to mimick NER
    patterns = [
        {"label": "PERSON", "pattern": [{"LOWER": "mahler"}]},
        {
            "label": "WORK",
            "pattern": [
                {"LOWER": "symphony"},
                {"LOWER": "no"},
                {"LOWER": "."},
                {"LOWER": "8"},
            ],
        },
    ]
    ruler = nlp.add_pipe("entity_ruler", before="entity_linker")
    ruler.add_patterns(patterns)
    # test the trained model - this should not throw E148
    doc = nlp(text)
    assert doc
