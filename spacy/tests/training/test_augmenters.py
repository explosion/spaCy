import pytest
from spacy.training import Corpus
from spacy.training.augment import create_orth_variants_augmenter
from spacy.training.augment import create_lower_casing_augmenter
from spacy.lang.en import English
from spacy.tokens import DocBin, Doc
from contextlib import contextmanager
import random

from ..util import make_tempdir


@contextmanager
def make_docbin(docs, name="roundtrip.spacy"):
    with make_tempdir() as tmpdir:
        output_file = tmpdir / name
        DocBin(docs=docs).to_disk(output_file)
        yield output_file


@pytest.fixture
def nlp():
    return English()


@pytest.fixture
def doc(nlp):
    # fmt: off
    words = ["Sarah", "'s", "sister", "flew", "to", "Silicon", "Valley", "via", "London", "."]
    tags = ["NNP", "POS", "NN", "VBD", "IN", "NNP", "NNP", "IN", "NNP", "."]
    pos = ["PROPN", "PART", "NOUN", "VERB", "ADP", "PROPN", "PROPN", "ADP", "PROPN", "PUNCT"]
    ents = ["B-PERSON", "I-PERSON", "O", "O", "O", "B-LOC", "I-LOC", "O", "B-GPE", "O"]
    cats = {"TRAVEL": 1.0, "BAKING": 0.0}
    # fmt: on
    doc = Doc(nlp.vocab, words=words, tags=tags, pos=pos, ents=ents)
    doc.cats = cats
    return doc


@pytest.mark.filterwarnings("ignore::UserWarning")
def test_make_orth_variants(nlp):
    single = [
        {"tags": ["NFP"], "variants": ["…", "..."]},
        {"tags": [":"], "variants": ["-", "—", "–", "--", "---", "——"]},
    ]
    # fmt: off
    words = ["\n\n", "A", "\t", "B", "a", "b", "…", "...", "-", "—", "–", "--", "---", "——"]
    tags = ["_SP", "NN", "\t", "NN", "NN", "NN", "NFP", "NFP", ":", ":", ":", ":", ":", ":"]
    # fmt: on
    spaces = [True] * len(words)
    spaces[0] = False
    spaces[2] = False
    doc = Doc(nlp.vocab, words=words, spaces=spaces, tags=tags)
    augmenter = create_orth_variants_augmenter(
        level=0.2, lower=0.5, orth_variants={"single": single}
    )
    with make_docbin([doc] * 10) as output_file:
        reader = Corpus(output_file, augmenter=augmenter)
        # Due to randomness, only test that it works without errors
        list(reader(nlp))

    # check that the following settings lowercase everything
    augmenter = create_orth_variants_augmenter(
        level=1.0, lower=1.0, orth_variants={"single": single}
    )
    with make_docbin([doc] * 10) as output_file:
        reader = Corpus(output_file, augmenter=augmenter)
        for example in reader(nlp):
            for token in example.reference:
                assert token.text == token.text.lower()

    # check that lowercasing is applied without tags
    doc = Doc(nlp.vocab, words=words, spaces=[True] * len(words))
    augmenter = create_orth_variants_augmenter(
        level=1.0, lower=1.0, orth_variants={"single": single}
    )
    with make_docbin([doc] * 10) as output_file:
        reader = Corpus(output_file, augmenter=augmenter)
        for example in reader(nlp):
            for ex_token, doc_token in zip(example.reference, doc):
                assert ex_token.text == doc_token.text.lower()

    # check that no lowercasing is applied with lower=0.0
    doc = Doc(nlp.vocab, words=words, spaces=[True] * len(words))
    augmenter = create_orth_variants_augmenter(
        level=1.0, lower=0.0, orth_variants={"single": single}
    )
    with make_docbin([doc] * 10) as output_file:
        reader = Corpus(output_file, augmenter=augmenter)
        for example in reader(nlp):
            for ex_token, doc_token in zip(example.reference, doc):
                assert ex_token.text == doc_token.text


def test_lowercase_augmenter(nlp, doc):
    augmenter = create_lower_casing_augmenter(level=1.0)
    with make_docbin([doc]) as output_file:
        reader = Corpus(output_file, augmenter=augmenter)
        corpus = list(reader(nlp))
    eg = corpus[0]
    assert eg.reference.text == doc.text.lower()
    assert eg.predicted.text == doc.text.lower()
    ents = [(e.start, e.end, e.label) for e in doc.ents]
    assert [(e.start, e.end, e.label) for e in eg.reference.ents] == ents
    for ref_ent, orig_ent in zip(eg.reference.ents, doc.ents):
        assert ref_ent.text == orig_ent.text.lower()
    assert [t.pos_ for t in eg.reference] == [t.pos_ for t in doc]

    # check that augmentation works when lowercasing leads to different
    # predicted tokenization
    words = ["A", "B", "CCC."]
    doc = Doc(nlp.vocab, words=words)
    with make_docbin([doc]) as output_file:
        reader = Corpus(output_file, augmenter=augmenter)
        corpus = list(reader(nlp))
    eg = corpus[0]
    assert eg.reference.text == doc.text.lower()
    assert eg.predicted.text == doc.text.lower()
    assert [t.text for t in eg.reference] == [t.lower() for t in words]
    assert [t.text for t in eg.predicted] == [
        t.text for t in nlp.make_doc(doc.text.lower())
    ]


@pytest.mark.filterwarnings("ignore::UserWarning")
def test_custom_data_augmentation(nlp, doc):
    def create_spongebob_augmenter(randomize: bool = False):
        def augment(nlp, example):
            text = example.text
            if randomize:
                ch = [c.lower() if random.random() < 0.5 else c.upper() for c in text]
            else:
                ch = [c.lower() if i % 2 else c.upper() for i, c in enumerate(text)]
            example_dict = example.to_dict()
            doc = nlp.make_doc("".join(ch))
            example_dict["token_annotation"]["ORTH"] = [t.text for t in doc]
            yield example
            yield example.from_dict(doc, example_dict)

        return augment

    with make_docbin([doc]) as output_file:
        reader = Corpus(output_file, augmenter=create_spongebob_augmenter())
        corpus = list(reader(nlp))
    orig_text = "Sarah 's sister flew to Silicon Valley via London . "
    augmented = "SaRaH 's sIsTeR FlEw tO SiLiCoN VaLlEy vIa lOnDoN . "
    assert corpus[0].text == orig_text
    assert corpus[0].reference.text == orig_text
    assert corpus[0].predicted.text == orig_text
    assert corpus[1].text == augmented
    assert corpus[1].reference.text == augmented
    assert corpus[1].predicted.text == augmented
    ents = [(e.start, e.end, e.label) for e in doc.ents]
    assert [(e.start, e.end, e.label) for e in corpus[0].reference.ents] == ents
    assert [(e.start, e.end, e.label) for e in corpus[1].reference.ents] == ents
