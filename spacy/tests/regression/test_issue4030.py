import spacy
from spacy.gold import Example
from spacy.util import minibatch, compounding


def test_issue4030():
    """ Test whether textcat works fine with empty doc """
    unique_classes = ["offensive", "inoffensive"]
    x_train = [
        "This is an offensive text",
        "This is the second offensive text",
        "inoff",
    ]
    y_train = ["offensive", "offensive", "inoffensive"]

    nlp = spacy.blank("en")

    # preparing the data
    train_data = []
    for text, train_instance in zip(x_train, y_train):
        cat_dict = {label: label == train_instance for label in unique_classes}
        train_data.append(Example.from_dict(nlp.make_doc(text), {"cats": cat_dict}))

    # add a text categorizer component
    textcat = nlp.create_pipe(
        "textcat",
        config={"exclusive_classes": True, "architecture": "bow", "ngram_size": 2},
    )

    for label in unique_classes:
        textcat.add_label(label)
    nlp.add_pipe(textcat, last=True)

    # training the network
    with nlp.select_pipes(enable="textcat"):
        optimizer = nlp.begin_training()
        for i in range(3):
            losses = {}
            batches = minibatch(train_data, size=compounding(4.0, 32.0, 1.001))

            for batch in batches:
                nlp.update(
                    examples=batch, sgd=optimizer, drop=0.1, losses=losses,
                )

    # processing of an empty doc should result in 0.0 for all categories
    doc = nlp("")
    assert doc.cats["offensive"] == 0.0
    assert doc.cats["inoffensive"] == 0.0
