from spacy.lang.en import English
from spacy.util import fix_random_seed


def test_issue5551():
    """Test that after fixing the random seed, the results of the pipeline are truly identical"""
    component = "textcat"
    pipe_cfg = {"exclusive_classes": False}

    results = []
    for i in range(3):
        fix_random_seed(0)
        nlp = English()
        example = (
            "Once hot, form ping-pong-ball-sized balls of the mixture, each weighing roughly 25 g.",
            {"cats": {"Labe1": 1.0, "Label2": 0.0, "Label3": 0.0}},
        )
        nlp.add_pipe(nlp.create_pipe(component, config=pipe_cfg), last=True)
        pipe = nlp.get_pipe(component)
        for label in set(example[1]["cats"]):
            pipe.add_label(label)
        nlp.begin_training(component_cfg={component: pipe_cfg})

        # Store the result of each iteration
        result = pipe.model.predict([nlp.make_doc(example[0])])
        results.append(list(result[0]))

    # All results should be the same because of the fixed seed
    assert len(results) == 3
    assert results[0] == results[1]
    assert results[0] == results[2]
