from __future__ import unicode_literals
import os
import random
import contextlib
import shutil
import pytest
import tempfile
from pathlib import Path


import pathlib
from ...gold import GoldParse
from ...pipeline import EntityRecognizer
from ...language import Language

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
    ]


@contextlib.contextmanager
def temp_save_model(model):
    model_dir = Path(tempfile.mkdtemp())
    model.save_to_directory(model_dir)
    yield model_dir
    shutil.rmtree(model_dir.as_posix())


# TODO: Fix when saving/loading is fixed.
@pytest.mark.xfail
def test_issue999(train_data):
    '''Test that adding entities and resuming training works passably OK.
    There are two issues here:

    1) We have to readd labels. This isn't very nice.
    2) There's no way to set the learning rate for the weight update, so we
        end up out-of-scale, causing it to learn too fast.
    '''
    nlp = Language(pipeline=[])
    nlp.entity = EntityRecognizer(nlp.vocab, features=Language.Defaults.entity_features)
    nlp.pipeline.append(nlp.entity)
    for _, offsets in train_data:
        for start, end, ent_type in offsets:
            nlp.entity.add_label(ent_type)
    nlp.entity.model.learn_rate = 0.001
    for itn in range(100):
        random.shuffle(train_data)
        for raw_text, entity_offsets in train_data:
            doc = nlp.make_doc(raw_text)
            gold = GoldParse(doc, entities=entity_offsets)
            loss = nlp.entity.update(doc, gold)

    with temp_save_model(nlp) as model_dir:
        nlp2 = Language(path=model_dir)

    for raw_text, entity_offsets in train_data:
        doc = nlp2(raw_text)
        ents = {(ent.start_char, ent.end_char): ent.label_ for ent in doc.ents}
        for start, end, label in entity_offsets:
            if (start, end) in ents:
                assert ents[(start, end)] == label
                break
        else:
            if entity_offsets:
                raise Exception(ents)
