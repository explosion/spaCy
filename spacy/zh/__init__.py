import jieba
from ..language import Language

from ..tokenizer import Tokenizer
from ..tokens.doc import Doc


class JiebaTokenizer(Tokenizer):
    def __call__(self, text):
        orths = []
        spaces = []
        for orth, start, end in jieba.tokenize(text):
            # TODO: This is wrong if multiple spaces in a row.
            if orth == u' ':
                spaces[-1] = True
            else:
                orths.append(orth)
                spaces.append(False)
        return Doc(self.vocab, orths_and_spaces=zip(orths, spaces))


class CharacterTokenizer(Tokenizer):
    def __call__(self, text):
        return self.tokens_from_list(list(text))


class Chinese(Language):
    lang = u'zh'

    @classmethod
    def default_tokenizer(cls, package, vocab):
        '''Return Jieba-wrapper tokenizer.'''
        return JiebaTokenizer.from_package(package, vocab)
