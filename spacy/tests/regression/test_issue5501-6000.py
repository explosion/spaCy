import pytest
from numpy.testing import assert_almost_equal
from thinc.api import Config, fix_random_seed, get_current_ops

from spacy.lang.en import English
from spacy.pipeline.textcat import single_label_default_config, single_label_bow_config
from spacy.pipeline.textcat import single_label_cnn_config
from spacy.pipeline.textcat_multilabel import multi_label_default_config
from spacy.pipeline.textcat_multilabel import multi_label_bow_config
from spacy.pipeline.textcat_multilabel import multi_label_cnn_config
from spacy.tokens import Span
from spacy import displacy
from spacy.pipeline import merge_entities
from spacy.training import Example


@pytest.mark.parametrize(
    "textcat_config",
    [
        single_label_default_config,
        single_label_bow_config,
        single_label_cnn_config,
        multi_label_default_config,
        multi_label_bow_config,
        multi_label_cnn_config,
    ],
)
def test_issue5551(textcat_config):
    """Test that after fixing the random seed, the results of the pipeline are truly identical"""
    component = "textcat"

    pipe_cfg = Config().from_str(textcat_config)
    results = []
    for i in range(3):
        fix_random_seed(0)
        nlp = English()
        text = "Once hot, form ping-pong-ball-sized balls of the mixture, each weighing roughly 25 g."
        annots = {"cats": {"Labe1": 1.0, "Label2": 0.0, "Label3": 0.0}}
        pipe = nlp.add_pipe(component, config=pipe_cfg, last=True)
        for label in set(annots["cats"]):
            pipe.add_label(label)
        # Train
        nlp.initialize()
        doc = nlp.make_doc(text)
        nlp.update([Example.from_dict(doc, annots)])
        # Store the result of each iteration
        result = pipe.model.predict([doc])
        results.append(result[0])
    # All results should be the same because of the fixed seed
    assert len(results) == 3
    ops = get_current_ops()
    assert_almost_equal(ops.to_numpy(results[0]), ops.to_numpy(results[1]))
    assert_almost_equal(ops.to_numpy(results[0]), ops.to_numpy(results[2]))


def test_issue5838():
    # Displacy's EntityRenderer break line
    # not working after last entity
    sample_text = "First line\nSecond line, with ent\nThird line\nFourth line\n"
    nlp = English()
    doc = nlp(sample_text)
    doc.ents = [Span(doc, 7, 8, label="test")]
    html = displacy.render(doc, style="ent")
    found = html.count("</br>")
    assert found == 4


def test_issue5918():
    # Test edge case when merging entities.
    nlp = English()
    ruler = nlp.add_pipe("entity_ruler")
    patterns = [
        {"label": "ORG", "pattern": "Digicon Inc"},
        {"label": "ORG", "pattern": "Rotan Mosle Inc's"},
        {"label": "ORG", "pattern": "Rotan Mosle Technology Partners Ltd"},
    ]
    ruler.add_patterns(patterns)

    text = """
        Digicon Inc said it has completed the previously-announced disposition
        of its computer systems division to an investment group led by
        Rotan Mosle Inc's Rotan Mosle Technology Partners Ltd affiliate.
        """
    doc = nlp(text)
    assert len(doc.ents) == 3
    # make it so that the third span's head is within the entity (ent_iob=I)
    # bug #5918 would wrongly transfer that I to the full entity, resulting in 2 instead of 3 final ents.
    # TODO: test for logging here
    # with pytest.warns(UserWarning):
    #     doc[29].head = doc[33]
    doc = merge_entities(doc)
    assert len(doc.ents) == 3
