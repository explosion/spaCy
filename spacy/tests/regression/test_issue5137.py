import spacy
from spacy.language import Language
from spacy.lang.en import English
from spacy.tests.util import make_tempdir


def test_issue5137():
    class MyComponent(object):
        name = "my_component"

        def __init__(self, nlp, **cfg):
            self.nlp = nlp
            self.categories = cfg.get("categories", "all_categories")

        def __call__(self, doc):
            pass

        def to_disk(self, path, **kwargs):
            pass

        def from_disk(self, path, **cfg):
            pass

    Language.factories["my_component"] = lambda nlp, **cfg: MyComponent(nlp, **cfg)

    nlp = English()
    nlp.add_pipe(nlp.create_pipe("my_component"))
    assert nlp.get_pipe("my_component").categories == "all_categories"

    with make_tempdir() as tmpdir:
        nlp.to_disk(tmpdir)
        nlp2 = spacy.load(tmpdir, categories="my_categories")
        assert nlp2.get_pipe("my_component").categories == "my_categories"
