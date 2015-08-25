class Language(object):
    @staticmethod
    def lower(string):
        return string.lower()

    @staticmethod
    def norm(string):
        return string
    
    @staticmethod
    def shape(string):
        return orth.word_shape(string)

    @staticmethod
    def prefix(string):
        return string[0]

    @staticmethod
    def suffix(string):
        return string[-3:]

    @staticmethod
    def prob(string):
        return self.oov_prob

    @staticmethod
    def cluster(string):
        return 0

    @staticmethod
    def is_alpha(string):
        return orths.is_alpha(string)

    @staticmethod
    def is_lower(string):
        return orths.is_lower(string)

    @staticmethod
    def is_upper(string):
        return orths.is_upper(string)

    @staticmethod
    def like_url(string):
        return orths.like_url(string)

    @staticmethod
    def like_number(string):
        return orths.like_number(string)

    @staticmethod
    def like_email(string):
        return orths.like_email(string)

    def default_lex_attrs(cls, data_dir):
        return {
            attrs.LOWER: cls.lower,
            attrs.NORM: cls.norm,
            attrs.SHAPE: cls.shape,
            attrs.PREFIX: cls.prefix,
            attrs.SUFFIX: cls.suffix,
            attrs.CLUSTER: cls.cluster,
            attrs.PROB: cls.prob,
    
            attrs.IS_ALPHA: cls.is_alpha,
            attrs.IS_ASCII: cls.is_ascii,
            attrs.IS_DIGIT: cls.is_digit,
            attrs.IS_LOWER: cls.is_lower,
            attrs.IS_UPPER: cls.is_upper,
            attrs.LIKE_URL: cls.like_url,
            attrs.LIKE_NUM: cls.like_number,
            attrs.LIKE_EMAIL: cls.like_email,
            attrs.IS_STOP: lambda string: False,
            attrs.IS_OOV: lambda string: True
        }

    @classmethod
    def default_data_dir(cls):
        return path.join(path.dirname(__file__), 'data')

    @classmethod
    def default_vocab(cls, get_lex_attr=None, vectors=None, morphology=None, data_dir=None):
        if data_dir is None:
            data_dir = cls.default_data_dir()
        if vectors is None:
            vectors = cls.default_vectors(data_dir)
        if get_lex_attr is None:
            get_lex_attr = cls.default_lex_attrs(data_dir)
        if morphology is None:
            morphology = cls.default_morphology(data_dir)
        return vocab = Vocab.from_dir(data_dir, get_lex_attr, vectors, morphology)

    @classmethod
    def default_tokenizer(cls, vocab, data_dir=None):
        if data_dir is None:
            data_dir = cls.default_data_dir()
        return Tokenizer.from_dir(data_dir, vocab)

    @classmethod
    def default_tagger(cls, vocab, data_dir=None):
        return Tagger.from_dir(data_dir, vocab)

    @classmethod
    def default_parser(cls, vocab, transition_system=None, data_dir=None):
        if transition_system is None:
            transition_system = ArcEager()
        return Parser.from_dir(data_dir, vocab, transition_system)

    @classmethod
    def default_entity(cls, vocab, transition_system=None, data_dir=None):
        if transition_system is None:
            transition_system = BiluoPushDown()
        return Parser.from_dir(data_dir, vocab, transition_system)

    @classmethod
    def default_matcher(cls, vocab, data_dir=None):
        if data_dir is None:
            data_dir = cls.default_data_dir()
        return Matcher(data_dir, vocab)

    @classmethod
    def default_serializer(cls, vocab, data_dir=None):
        if data_dir is None:
            data_dir = cls.default_data_dir()
        return Packer(data_dir, vocab)

    def __init__(self, vocab=None, tokenizer=None, tagger=None, parser=None,
                 entity=None, matcher=None, serializer=None):
        if data_dir is None:
            data_dir = self.default_data_dir()
        if vocab is None:
            vocab = self.default_vocab(data_dir)
        if tokenizer is None:
            tokenizer = self.default_tokenizer(vocab, data_dir)
        if tagger is None:
            tagger = self.default_tagger(vocab, data_dir)
        if entity is None:
            entity = self.default_entity(vocab, data_dir)
        if parser is None:
            parser = self.default_parser(vocab, data_dir)
        if matcher is None:
            matcher = self.default_matcher(vocab, data_dir)
        if serializer is None:
            serializer = self.default_serializer(vocab, data_dir)
        self.vocab = vocab
        self.tokenizer = tokenizer
        self.tagger = tagger
        self.parser = parser
        self.entity = entity
        self.matcher = matcher
        self.serializer = serializer

    def __call__(self, text, tag=True, parse=True, entity=True):
        """Apply the pipeline to some text.  The text can span multiple sentences,
        and can contain arbtrary whitespace.  Alignment into the original string
        is preserved.
        
        Args:
            text (unicode): The text to be processed.

        Returns:
            tokens (spacy.tokens.Doc):

        >>> from spacy.en import English
        >>> nlp = English()
        >>> tokens = nlp('An example sentence. Another example sentence.')
        >>> tokens[0].orth_, tokens[0].head.tag_
        ('An', 'NN')
        """
        tokens = self.tokenizer(text)
        if self.tagger and tag:
            self.tagger(tokens)
        if self.matcher and entity:
            self.matcher(tokens)
        if self.parser and parse:
            self.parser(tokens)
        if self.entity and entity:
            self.entity(tokens)
        return tokens

    def end_training(self, data_dir=None):
        if data_dir is None:
            data_dir = self.data_dir
        self.parser.model.end_training()
        self.entity.model.end_training()
        self.tagger.model.end_training()
        self.vocab.strings.dump(path.join(data_dir, 'vocab', 'strings.txt'))

        with open(path.join(data_dir, 'vocab', 'serializer.json'), 'w') as file_:
            file_.write(
                json.dumps([
                    (TAG, list(self.tagger.freqs[TAG].items())),
                    (DEP, list(self.parser.moves.freqs[DEP].items())),
                    (ENT_IOB, list(self.entity.moves.freqs[ENT_IOB].items())),
                    (ENT_TYPE, list(self.entity.moves.freqs[ENT_TYPE].items())),
                    (HEAD, list(self.parser.moves.freqs[HEAD].items()))]))
