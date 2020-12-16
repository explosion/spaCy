# coding: utf8
from __future__ import unicode_literals

from spacy.lang.en import English
from spacy.tokens import Span, Doc


class CustomPipe:
    name = "my_pipe"

    def __init__(self):
        Span.set_extension("my_ext", getter=self._get_my_ext)
        Doc.set_extension("my_ext", default=None)

    def __call__(self, doc):
        gathered_ext = []
        for sent in doc.sents:
            sent_ext = self._get_my_ext(sent)
            sent._.set("my_ext", sent_ext)
            gathered_ext.append(sent_ext)

        doc._.set("my_ext", "\n".join(gathered_ext))

        return doc

    @staticmethod
    def _get_my_ext(span):
        return str(span.end)


def test_issue4903():
    # ensures that this runs correctly and doesn't hang or crash on Windows / macOS

    nlp = English()
    custom_component = CustomPipe()
    nlp.add_pipe(nlp.create_pipe("sentencizer"))
    nlp.add_pipe(custom_component, after="sentencizer")

    text = ["I like bananas.", "Do you like them?", "No, I prefer wasabi."]
    docs = list(nlp.pipe(text, n_process=2))
    assert docs[0].text == "I like bananas."
    assert docs[1].text == "Do you like them?"
    assert docs[2].text == "No, I prefer wasabi."
