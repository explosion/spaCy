import pytest
from spacy.language import Language
from spacy.training import Example
from spacy.lang.en import English


def test_set_annotations_on_update():
    # The custom component checks for sentence annotation
    @Language.factory("assert_sents", default_config={})
    def assert_sents(nlp, name):
        return AssertSents(name)

    class AssertSents:
        def __init__(self, name, **cfg):
            self.name = name
            pass

        def __call__(self, doc):
            if not doc.has_annotation("SENT_START"):
                raise ValueError("No sents")
            return doc

        def update(self, examples, *, drop=0.0, sgd=None, losses=None):
            for example in examples:
                if not example.predicted.has_annotation("SENT_START"):
                    raise ValueError("No sents")
            return {}

    nlp = English()
    nlp.add_pipe("sentencizer")
    nlp.add_pipe("assert_sents")

    # When the pipeline runs, annotations are set
    doc = nlp("This is a sentence.")

    examples = []
    for text in ["a a", "b b", "c c"]:
        examples.append(Example(nlp.make_doc(text), nlp(text)))

    for example in examples:
        assert not example.predicted.has_annotation("SENT_START")

    # If updating without setting annotations, assert_sents will raise an error
    with pytest.raises(ValueError):
        nlp.update(examples)

    # Updating while setting annotations for the sentencizer succeeds
    nlp.update(examples, set_annotations_on_update=["sentencizer"])
