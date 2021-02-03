import pytest
import spacy
from spacy.language import Language
from spacy.tokens import DocBin
from spacy import util
from spacy.schemas import ConfigSchemaInit

from spacy.training.initialize import init_nlp

from ..util import make_tempdir

TEXTCAT_WITH_LABELS_ARRAY_CONFIG = """
[paths]
train = "TRAIN_PLACEHOLDER"
raw = null
init_tok2vec = null
vectors = null

[system]
seed = 0
gpu_allocator = null

[nlp]
lang = "en"
pipeline = ["textcat"]
tokenizer = {"@tokenizers":"spacy.Tokenizer.v1"}
disabled = []
before_creation = null
after_creation = null
after_pipeline_creation = null
batch_size = 1000

[components]

[components.textcat]
factory = "TEXTCAT_PLACEHOLDER"

[corpora]

[corpora.train]
@readers = "spacy.Corpus.v1"
path = ${paths:train}

[corpora.dev]
@readers = "spacy.Corpus.v1"
path = ${paths:train}


[training]
train_corpus = "corpora.train"
dev_corpus = "corpora.dev"
seed = ${system.seed}
gpu_allocator = ${system.gpu_allocator}
frozen_components = []
before_to_disk = null

[pretraining]

[initialize]
vectors = ${paths.vectors}
init_tok2vec = ${paths.init_tok2vec}
vocab_data = null
lookups = null
before_init = null
after_init = null

[initialize.components]

[initialize.components.textcat]
labels = ['label1', 'label2']

[initialize.tokenizer]
"""


@pytest.mark.parametrize(
    "component_name",
    ["textcat", "textcat_multilabel"],
)
def test_textcat_initialize_labels_validation(component_name):
    """Test intializing textcat with labels in a list"""

    def create_data(out_file):
        nlp = spacy.blank("en")
        doc = nlp.make_doc("Some text")
        doc.cats = {"label1": 0, "label2": 1}

        out_data = DocBin(docs=[doc]).to_bytes()
        with out_file.open("wb") as file_:
            file_.write(out_data)

    with make_tempdir() as tmp_path:
        train_path = tmp_path / "train.spacy"
        create_data(train_path)

        config_str = TEXTCAT_WITH_LABELS_ARRAY_CONFIG.replace(
            "TEXTCAT_PLACEHOLDER", component_name
        )
        config_str = config_str.replace("TRAIN_PLACEHOLDER", train_path.as_posix())

        config = util.load_config_from_str(config_str)
        init_nlp(config)
