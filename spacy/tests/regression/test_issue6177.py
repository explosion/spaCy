# coding: utf8
from __future__ import unicode_literals

from spacy.lang.en import English
from spacy.util import fix_random_seed


def test_issue6177():
    """Test that after fixing the random seed, the results of the pipeline are truly identical"""

    # NOTE: no need to transform this code to v3 when 'master' is merged into 'develop'.
    # A similar test exists already for v3: test_issue5551
    # This is just a backport
    results = []
    for i in range(3):
        fix_random_seed(0)
        nlp = English()
        example = (
            "Once hot, form ping-pong-ball-sized balls of the mixture, each weighing roughly 25 g.",
            {"cats": {"Labe1": 1.0, "Label2": 0.0, "Label3": 0.0}},
        )
        textcat = nlp.create_pipe("textcat")
        nlp.add_pipe(textcat)
        for label in set(example[1]["cats"]):
            textcat.add_label(label)
        # Train
        optimizer = nlp.begin_training()
        text, annots = example
        nlp.update([text], [annots], sgd=optimizer)
        # Store the result of each iteration
        result = textcat.model.predict([nlp.make_doc(text)])
        results.append(list(result[0]))

    # All results should be the same because of the fixed seed
    assert len(results) == 3
    assert results[0] == results[1]
    assert results[0] == results[2]
