import pytest

import spacy
from spacy import ty


@pytest.mark.issue(13246)
def test_issue13246(tmp_path):
    mypy = pytest.importorskip("mypy.api")
    # Apply silent import following to stubs too, so only consumer errors are reported.
    config = tmp_path / "mypy.ini"
    config.write_text("[mypy]\nfollow_imports_for_stubs = True\n", encoding="utf8")
    consumer = tmp_path / "consumer.py"
    consumer.write_text(
        "import spacy\n"
        "from spacy import Config, Language, explain, info, prefer_gpu, registry, require_cpu, require_gpu\n"
        "spacy.prefer_gpu()\n",
        encoding="utf8",
    )
    stdout, stderr, status = mypy.run(
        [
            "--strict",
            "--no-implicit-reexport",
            "--follow-imports=silent",
            "--ignore-missing-imports",
            "--config-file",
            str(config),
            "--cache-dir",
            str(tmp_path / ".mypy_cache"),
            str(consumer),
        ]
    )
    assert status == 0, stdout + stderr


def test_component_types():
    nlp = spacy.blank("en")
    tok2vec = nlp.create_pipe("tok2vec")
    tagger = nlp.create_pipe("tagger")
    entity_ruler = nlp.create_pipe("entity_ruler")
    assert isinstance(tok2vec, ty.TrainableComponent)
    assert isinstance(tagger, ty.TrainableComponent)
    assert not isinstance(entity_ruler, ty.TrainableComponent)
    assert isinstance(tok2vec, ty.InitializableComponent)
    assert isinstance(tagger, ty.InitializableComponent)
    assert isinstance(entity_ruler, ty.InitializableComponent)
    assert isinstance(tok2vec, ty.ListenedToComponent)
    assert not isinstance(tagger, ty.ListenedToComponent)
    assert not isinstance(entity_ruler, ty.ListenedToComponent)
