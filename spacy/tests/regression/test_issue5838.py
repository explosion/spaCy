from spacy.lang.en import English
from spacy.tokens import Span
from spacy import displacy


SAMPLE_TEXT = """First line
Second line, with ent
Third line
Fourth line
"""


def test_issue5838():
    # Displacy's EntityRenderer break line
    # not working after last entity

    nlp = English()
    doc = nlp(SAMPLE_TEXT)
    doc.ents = [Span(doc, 7, 8, label="test")]

    html = displacy.render(doc, style="ent")
    found = html.count("</br>")
    assert found == 4
