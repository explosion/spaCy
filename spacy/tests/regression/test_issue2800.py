'''Test issue that arises when too many labels are added to NER model.'''
from __future__ import unicode_literals

import random
from ...lang.en import English

def train_model(train_data, entity_types):
    nlp = English(pipeline=[])

    ner = nlp.create_pipe("ner")
    nlp.add_pipe(ner)

    for entity_type in list(entity_types):
        ner.add_label(entity_type)

    optimizer = nlp.begin_training()

    # Start training
    for i in range(20):
        losses = {}
        index = 0
        random.shuffle(train_data)

        for statement, entities in train_data:
            nlp.update([statement], [entities], sgd=optimizer, losses=losses, drop=0.5)
    return nlp


def test_train_with_many_entity_types():
    train_data = []
    train_data.extend([("One sentence", {"entities": []})])
    entity_types = [str(i) for i in range(1000)]

    model = train_model(train_data, entity_types)

    
