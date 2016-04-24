from ..language import Language
from .jieba import JiebaTokenizer


class Chinese(Language):
    lang = u'zh'

    @classmethod
    def default_tokenizer(cls, package, vocab):
        '''Return Jieba-wrapper tokenizer.'''
        return JiebaTokenizer.from_package(package, vocab)


