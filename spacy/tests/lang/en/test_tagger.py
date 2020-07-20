from spacy.symbols import POS, PRON, VERB, DET, NOUN, PUNCT
from ...util import get_doc


def test_en_tagger_load_morph_exc(en_tokenizer):
    text = "I like his style."
    tags = ["PRP", "VBP", "PRP$", "NN", "."]
    tag_map = {
        "PRP": {POS: PRON},
        "VBP": {POS: VERB},
        "PRP$": {POS: DET},
        "NN": {POS: NOUN},
        ".": {POS: PUNCT},
    }
    morph_exc = {"VBP": {"like": {"lemma": "luck"}}}
    en_tokenizer.vocab.morphology.load_tag_map(tag_map)
    en_tokenizer.vocab.morphology.load_morph_exceptions(morph_exc)
    tokens = en_tokenizer(text)
    doc = get_doc(tokens.vocab, words=[t.text for t in tokens], tags=tags)
    assert doc[1].tag_ == "VBP"
    assert doc[1].lemma_ == "luck"
