# coding: utf-8

from spacy.compat import intern, queue
from spacy.strings import hash_string
from operator import itemgetter
import re
import json

from .pattern import DependencyPattern

TOKEN_INITIAL = intern('initial')


class PatternParser(object):
    """Compile a Pattern query into a :class:`Pattern`, that can be used to
    match :class:`DependencyTree`s."""
    whitespace_re = re.compile(r'\s+', re.U)
    newline_re = re.compile(r'(\r\n|\r|\n)')
    name_re = re.compile(r'\w+', re.U)

    TOKEN_BLOCK_BEGIN = '['
    TOKEN_BLOCK_END = ']'
    EDGE_BLOCK_BEGIN = '>'
    WHITESPACE = ' '

    @classmethod
    def parse(cls, query):
        """Parse the given `query`, and compile it into a :class:`Pattern`."""
        pattern = DependencyPattern()

        for lineno, token_stream in enumerate(cls.tokenize(query)):
            try:
                cls._parse_line(token_stream, pattern, lineno+1)
            except StopIteration:
                raise SyntaxError("A token is missing, please check your "
                                  "query.")

        if not pattern.nodes:
            return

        cls.check_pattern(pattern)
        return pattern

    @staticmethod
    def check_pattern(pattern):
        if not pattern.is_connected():
            raise ValueError("The pattern tree must be a fully connected "
                             "graph.")

        if pattern.root_node is None:
            raise ValueError("The root node of the tree could not be found.")

    @classmethod
    def _parse_line(cls, stream, pattern, lineno):
        while not stream.closed:
            token = stream.current

            if token.type == 'name':
                next_token = stream.look()

                if next_token.type == 'node':
                    cls.parse_node_def(stream, pattern)

                elif next_token.type == 'edge':
                    cls.parse_edge_def(stream, pattern)

                else:
                    raise SyntaxError("line %d: A 'node' or 'edge' token must "
                                      "follow a 'name' token." % lineno)

            elif token.type == 'node':
                next_token = stream.look()

                if next_token.type == 'edge':
                    cls.parse_edge_def(stream, pattern)
                else:
                    raise SyntaxError("line %d: an 'edge' token is "
                                      "expected." % lineno)

            if not stream.closed:
                next(stream)

    @classmethod
    def parse_node_def(cls, stream, pattern):
        name_token = stream.current
        next(stream)
        node_token = stream.current
        cls.add_node(node_token, pattern, name_token)

    @classmethod
    def add_node(cls, node_token, pattern, name_token=None):
        token_name = None
        if name_token is not None:
            token_id = name_token.value
            token_name = name_token.value
        else:
            token_id = node_token.hash()

        if token_id in pattern.nodes:
            raise SyntaxError("Token with ID '{}' already registered.".format(
                token_id))

        token_attr = cls.parse_node_attributes(node_token.value)
        token_attr['_name'] = token_name
        pattern.add_node(token_id, token_attr)

    @classmethod
    def parse_edge_def(cls, stream, pattern):
        token = stream.current

        if token.type == 'name':
            token_id = token.value
            if token_id not in pattern.nodes:
                raise SyntaxError("Token '{}' with ID '{}' is not "
                                  "defined.".format(token, token_id))

        elif token.type == 'node':
            token_id = token.hash()
            cls.add_node(token, pattern)

        next(stream)
        edge_attr = cls.parse_edge_attributes(stream.current.value)
        next(stream)

        head_token = stream.current
        if head_token.type == 'name':
            head_token_id = head_token.value
            if head_token_id not in pattern.nodes:
                raise SyntaxError("Token '{}' with ID '{}' is not "
                                  "defined.".format(head_token, head_token_id))
        elif head_token.type == 'node':
            head_token_id = head_token.hash()
            cls.add_node(head_token, pattern)
        else:
            raise SyntaxError("A 'node' or 'name' token was expected.")

        # inverse the dependency to have an actual tree
        pattern.add_edge(head_token_id, token_id, edge_attr)

    @classmethod
    def parse_node_attributes(cls, string):
        string = string[1:]  # remove the trailing '['
        end_delimiter_idx = string.find(']')

        attr_str = string[:end_delimiter_idx]
        attr = {}

        try:
            attr = json.loads(attr_str)
        except json.JSONDecodeError:
            for pair in attr_str.split(","):
                key, value = pair.split(':')
                attr[key] = value

        for key, value in attr.items():
            attr[key] = cls.compile_expression(value)

        alias = string[end_delimiter_idx+2:]

        if alias:
            attr['_alias'] = alias

        return attr

    @classmethod
    def parse_edge_attributes(cls, string):
        string = string[1:]  # remove the trailing '>'

        if not string:
            return None

        return cls.compile_expression(string)

    @staticmethod
    def compile_expression(expr):
        if expr.startswith('/') and expr.endswith('/'):
            string = expr[1:-1]
            return re.compile(string, re.U)

        return expr

    @classmethod
    def tokenize(cls, text):
        lines = text.splitlines()

        for lineno, line in enumerate(lines):
            yield TokenStream(cls._tokenize_line(line, lineno+1))

    @classmethod
    def _tokenize_line(cls, line, lineno):
        reader = Reader(line)

        while reader.remaining():
            char = reader.next()

            if char == cls.TOKEN_BLOCK_BEGIN:
                token = 'node'
                idx = reader.find(cls.TOKEN_BLOCK_END)

                if idx == -1:
                    raise SyntaxError("A token block end ']' was expected.")

                idx += 1
                if len(reader) > idx and reader[idx] == '=':
                    # The node has a name
                    idx = reader.find(cls.WHITESPACE, start=idx)

                    if idx == -1:
                        idx = reader.remaining()

            elif char == cls.EDGE_BLOCK_BEGIN:
                token = 'edge'
                idx = reader.find(cls.WHITESPACE)

            elif cls.name_re.match(char):
                token = 'name'
                idx = reader.find(cls.WHITESPACE)

                if idx == -1:
                    whole_name_match = cls.name_re.match(str(reader))
                    idx = whole_name_match.end()

            elif cls.newline_re.match(char) or cls.whitespace_re.match(char):
                # skip the whitespace
                reader.consume()
                continue

            else:
                raise SyntaxError("Unrecognized token BEGIN char: '{"
                                  "}'".format(char))

            if idx == -1:
                raise SyntaxError("Ending character of token '{}' not "
                                  "found.".format(token))
            value = reader.consume(idx)

            yield Token(lineno, token, value)


class Reader(object):
    """A class used by the :class:`PatternParser` to tokenize the `text`."""
    __slots__ = ('text', 'pos')

    def __init__(self, text):
        self.text = text
        self.pos = 0

    def find(self, needle, start=0, end=None):
        pos = self.pos
        start += pos
        if end is None:
            index = self.text.find(needle, start)
        else:
            end += pos
            index = self.text.find(needle, start, end)
        if index != -1:
            index -= pos
        return index

    def consume(self, count=1):
        new_pos = self.pos + count
        s = self.text[self.pos:new_pos]
        self.pos = new_pos
        return s

    def next(self):
        return self.text[self.pos:self.pos + 1]

    def remaining(self):
        return len(self.text) - self.pos

    def __len__(self):
        return self.remaining()

    def __getitem__(self, key):
        if key < 0:
            return self.text[key]
        else:
            return self.text[self.pos + key]

    def __str__(self):
        return self.text[self.pos:]


# The following classes were copied from Jinja2, a BSD-licensed project,
# and slightly modified: Token, TokenStreamIterator, TokenStream.

class Token(tuple):
    """Token class."""
    __slots__ = ()
    lineno, type, value = (property(itemgetter(x)) for x in range(3))

    def __new__(cls, lineno, type, value):
        return tuple.__new__(cls, (lineno, intern(str(type)), value))

    def hash(self):
        string = self.value
        return hash_string(string)

    def __repr__(self):
        return 'Token(%r, %r, %r)' % (
            self.lineno,
            self.type,
            self.value)


class TokenStreamIterator(object):
    """The iterator for tokenstreams. Iterate over the stream until the
    stream is empty.
    """

    def __init__(self, stream):
        self.stream = stream

    def __iter__(self):
        return self

    def __next__(self):
        token = self.stream.current
        try:
            next(self.stream)
        except StopIteration:
            self.stream.close()
            raise StopIteration()

        return token


class TokenStream(object):
    """A token stream is an iterable that yields :class:`Token`s. The
    current active token is stored as :attr:`current`.
    """

    def __init__(self, generator):
        self._iter = iter(generator)
        self._pushed = queue.deque()
        self.closed = False
        self.current = Token(1, TOKEN_INITIAL, '')
        next(self)

    def __iter__(self):
        return TokenStreamIterator(self)

    def __bool__(self):
        return bool(self._pushed)
    __nonzero__ = __bool__  # py2

    def push(self, token):
        """Push a token back to the stream."""
        self._pushed.append(token)

    def look(self):
        """Look at the next token."""
        old_token = next(self)
        result = self.current
        self.push(result)
        self.current = old_token
        return result

    def __next__(self):
        """Go one token ahead and return the old one."""
        rv = self.current
        if self._pushed:
            self.current = self._pushed.popleft()
        else:
            if self.closed:
                raise StopIteration("No token left.")
            try:
                self.current = next(self._iter)
            except StopIteration:
                self.close()
        return rv

    def close(self):
        """Close the stream."""
        self._iter = None
        self.closed = True
