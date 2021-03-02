from spacy.lang.en import English


def test_issue7065():
    text = "Kathleen Battle sang in Mahler 's Symphony No. 8 at the Cincinnati Symphony Orchestra 's May Festival."
    nlp = English()
    nlp.add_pipe("sentencizer")
    ruler = nlp.add_pipe("entity_ruler")
    patterns = [{"label": "THING", "pattern": [{"LOWER": "symphony"}, {"LOWER": "no"}, {"LOWER": "."}, {"LOWER": "8"}]}]
    ruler.add_patterns(patterns)

    doc = nlp(text)
    sentences = [s for s in doc.sents]
    assert len(sentences) == 2
    sent0 = sentences[0]
    ent = doc.ents[0]
    assert ent.start < sent0.end < ent.end
    assert sentences.index(ent.sent) == 0
