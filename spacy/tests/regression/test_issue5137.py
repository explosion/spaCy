import spacy
from spacy.language import Language
from spacy.lang.en import English
from spacy.tests.util import make_tempdir


def test_issue5137():
    @Language.factory("my_component")
    class MyComponent:
        def __init__(self, nlp, name="my_component", categories="all_categories"):
            self.nlp = nlp
            self.categories = categories
            self.name = name

        def __call__(self, doc):
            pass

        def to_disk(self, path, **kwargs):
            pass

        def from_disk(self, path, **cfg):
            pass

    nlp = English()
    my_component = nlp.add_pipe("my_component")
    assert my_component.categories == "all_categories"

    with make_tempdir() as tmpdir:
        nlp.to_disk(tmpdir)
        overrides = {"components": {"my_component": {"categories": "my_categories"}}}
        nlp2 = spacy.load(tmpdir, config=overrides)
        assert nlp2.get_pipe("my_component").categories == "my_categories"
