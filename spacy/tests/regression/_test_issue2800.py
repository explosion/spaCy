# coding: utf-8
from __future__ import unicode_literals

import random
from spacy.lang.en import English


def test_train_with_many_entity_types():
    """Test issue that arises when too many labels are added to NER model.
    NB: currently causes segfault!
    """
    train_data = []
    train_data.extend([("One sentence", {"entities": []})])
    entity_types = [str(i) for i in range(1000)]
    nlp = English(pipeline=[])
    ner = nlp.create_pipe("ner")
    nlp.add_pipe(ner)
    for entity_type in list(entity_types):
        ner.add_label(entity_type)
    optimizer = nlp.begin_training()
    for i in range(20):
        losses = {}
        random.shuffle(train_data)
        for statement, entities in train_data:
            nlp.update([statement], [entities], sgd=optimizer, losses=losses, drop=0.5)
