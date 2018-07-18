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
