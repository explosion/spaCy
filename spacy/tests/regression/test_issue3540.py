import spacy


def test_issue3540():
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(u"I live in NewYork right now")

    gold_text = ["I", "live", "in", "NewYork", "right", "now"]
    assert [token.text for token in doc] == gold_text

    gold_lemma = ["-PRON-", "live", "in", "NewYork", "right", "now"]
    assert [token.lemma_ for token in doc] == gold_lemma

    vectors_1 = [token.vector for token in doc]
    assert len(vectors_1) == len(doc)

    with doc.retokenize() as retokenizer:
        heads = [(doc[3], 1), doc[2]]
        attrs = {"POS": ["PROPN", "PROPN"], "DEP": ["pobj", "compound"]}
        retokenizer.split(doc[3], [u"New", u"York"], heads=heads, attrs=attrs)

    gold_text = ["I", "live", "in", "New", "York", "right", "now"]
    assert [token.text for token in doc] == gold_text

    gold_lemma = ["-PRON-", "live", "in", "New", "York", "right", "now"]
    assert [token.lemma_ for token in doc] == gold_lemma

    vectors_2 = [token.vector for token in doc]
    assert len(vectors_2) == len(doc)

    assert vectors_1[0].tolist() == vectors_2[0].tolist()
    assert vectors_1[5].tolist() == vectors_2[6].tolist()
