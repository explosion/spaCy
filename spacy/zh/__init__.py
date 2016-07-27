from ..language import Language
from ..tokenizer import Tokenizer
from ..tagger import Tagger


class CharacterTokenizer(Tokenizer):
    def __call__(self, text):
        return self.tokens_from_list(list(text))


class Chinese(Language):
    lang = u'zh'

    def __call__(self, text):
        doc = self.tokenizer.tokens_from_list(list(text))
        self.tagger(doc)
        self.merge_characters(doc)
        return doc

    def merge_characters(self, doc):
        start = 0
        chunks = []
        for token in doc:
            if token.tag_ != 'CHAR':
                chunk = doc[start : token.i + 1]
                chunks.append(chunk)
                start = token.i + 1
        text = doc.text
        for chunk in chunks:
            chunk.merge(chunk[-1].tag_, chunk.text, u'')
