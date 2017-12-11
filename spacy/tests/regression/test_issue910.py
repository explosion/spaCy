# coding: utf8
from __future__ import unicode_literals

import json
import random
import contextlib
import shutil
import pytest
import tempfile
from pathlib import Path
from thinc.neural.optimizers import Adam

from ...gold import GoldParse
from ...pipeline import EntityRecognizer
from ...lang.en import English

try:
    unicode
except NameError:
    unicode = str


@pytest.fixture
def train_data():
    return [
            ["hey",[]],
            ["howdy",[]],
            ["hey there",[]],
            ["hello",[]],
            ["hi",[]],
            ["i'm looking for a place to eat",[]],
            ["i'm looking for a place in the north of town",[[31,36,"location"]]],
            ["show me chinese restaurants",[[8,15,"cuisine"]]],
            ["show me chines restaurants",[[8,14,"cuisine"]]],
            ["yes",[]],
            ["yep",[]],
            ["yeah",[]],
            ["show me a mexican place in the centre",[[31,37,"location"], [10,17,"cuisine"]]],
            ["bye",[]],["goodbye",[]],
            ["good bye",[]],
            ["stop",[]],
            ["end",[]],
            ["i am looking for an indian spot",[[20,26,"cuisine"]]],
            ["search for restaurants",[]],
            ["anywhere in the west",[[16,20,"location"]]],
            ["central indian restaurant",[[0,7,"location"],[8,14,"cuisine"]]],
            ["indeed",[]],
            ["that's right",[]],
            ["ok",[]],
            ["great",[]]
    ]

@pytest.fixture
def additional_entity_types():
    return ['cuisine', 'location']


@contextlib.contextmanager
def temp_save_model(model):
    model_dir = tempfile.mkdtemp()
    model.to_disk(model_dir)
    yield model_dir
    shutil.rmtree(model_dir.as_posix())


@pytest.mark.xfail
@pytest.mark.models('en')
def test_issue910(EN, train_data, additional_entity_types):
    '''Test that adding entities and resuming training works passably OK.
    There are two issues here:

    1) We have to readd labels. This isn't very nice.
    2) There's no way to set the learning rate for the weight update, so we
        end up out-of-scale, causing it to learn too fast.
    '''
    nlp = EN
    doc = nlp(u"I am looking for a restaurant in Berlin")
    ents_before_train = [(ent.label_, ent.text) for ent in doc.ents]
    # Fine tune the ner model
    for entity_type in additional_entity_types:
        nlp.entity.add_label(entity_type)

    sgd = Adam(nlp.entity.model[0].ops, 0.001)
    for itn in range(10):
        random.shuffle(train_data)
        for raw_text, entity_offsets in train_data:
            doc = nlp.make_doc(raw_text)
            nlp.tagger(doc)
            nlp.tensorizer(doc)
            gold = GoldParse(doc, entities=entity_offsets)
            loss = nlp.entity.update(doc, gold, sgd=sgd, drop=0.5)

    with temp_save_model(nlp.entity) as model_dir:
        # Load the fine tuned model
        loaded_ner = EntityRecognizer(nlp.vocab)
        loaded_ner.from_disk(model_dir)

    for raw_text, entity_offsets in train_data:
        doc = nlp.make_doc(raw_text)
        nlp.tagger(doc)
        loaded_ner(doc)
        ents = {(ent.start_char, ent.end_char): ent.label_ for ent in doc.ents}
        for start, end, label in entity_offsets:
            assert ents[(start, end)] == label
