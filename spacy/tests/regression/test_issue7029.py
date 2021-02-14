from spacy.lang.en import English
from spacy.training import Example
from spacy.util import load_config_from_str


CONFIG = """
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


TRAIN_DATA = [
    ("I like green eggs", {"tags": ["N", "V", "J", "N"]}),
    ("Eat blue ham", {"tags": ["V", "J", "N"]}),
]


def test_issue7029():
    """Test that an empty document doesn't mess up an entire batch."""
    nlp = English.from_config(load_config_from_str(CONFIG))
    train_examples = []
    for t in TRAIN_DATA:
        train_examples.append(Example.from_dict(nlp.make_doc(t[0]), t[1]))
    optimizer = nlp.initialize(get_examples=lambda: train_examples)
    for i in range(50):
        losses = {}
        nlp.update(train_examples, sgd=optimizer, losses=losses)
    texts = ["first", "second", "third", "fourth", "and", "then", "some", ""]
    nlp.select_pipes(enable=["tok2vec", "tagger"])
    docs1 = list(nlp.pipe(texts, batch_size=1))
    docs2 = list(nlp.pipe(texts, batch_size=4))
    assert [doc[0].tag_ for doc in docs1[:-1]] == [doc[0].tag_ for doc in docs2[:-1]]
