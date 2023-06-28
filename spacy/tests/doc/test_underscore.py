import pytest
from mock import Mock

from spacy.tokens import Doc, Span, Token
from spacy.tokens.underscore import Underscore


# Helper functions
def _get_tuple(s: Span):
    return "._.", "span_extension", s.start_char, s.end_char, s.label, s.kb_id, s.id


@pytest.fixture(scope="function", autouse=True)
def clean_underscore():
    # reset the Underscore object after the test, to avoid having state copied across tests
    yield
    Underscore.doc_extensions = {}
    Underscore.span_extensions = {}
    Underscore.token_extensions = {}


def test_create_doc_underscore():
    doc = Mock()
    doc.doc = doc
    uscore = Underscore(Underscore.doc_extensions, doc)
    assert uscore._doc is doc
    assert uscore._start is None
    assert uscore._end is None


def test_doc_underscore_getattr_setattr():
    doc = Mock()
    doc.doc = doc
    doc.user_data = {}
    Underscore.doc_extensions["hello"] = (False, None, None, None)
    doc._ = Underscore(Underscore.doc_extensions, doc)
    assert doc._.hello is False
    doc._.hello = True
    assert doc._.hello is True


def test_create_span_underscore():
    span = Mock(doc=Mock(), start=0, end=2)
    uscore = Underscore(
        Underscore.span_extensions, span, start=span.start, end=span.end
    )
    assert uscore._doc is span.doc
    assert uscore._start is span.start
    assert uscore._end is span.end


def test_span_underscore_getter_setter():
    span = Mock(doc=Mock(), start=0, end=2)
    Underscore.span_extensions["hello"] = (
        None,
        None,
        lambda s: (s.start, "hi"),
        lambda s, value: setattr(s, "start", value),
    )
    span._ = Underscore(
        Underscore.span_extensions, span, start=span.start, end=span.end
    )

    assert span._.hello == (0, "hi")
    span._.hello = 1
    assert span._.hello == (1, "hi")


def test_token_underscore_method():
    token = Mock(doc=Mock(), idx=7, say_cheese=lambda token: "cheese")
    Underscore.token_extensions["hello"] = (None, token.say_cheese, None, None)
    token._ = Underscore(Underscore.token_extensions, token, start=token.idx)
    assert token._.hello() == "cheese"


@pytest.mark.parametrize("obj", [Doc, Span, Token])
def test_doc_underscore_remove_extension(obj):
    ext_name = "to_be_removed"
    obj.set_extension(ext_name, default=False)
    assert obj.has_extension(ext_name)
    obj.remove_extension(ext_name)
    assert not obj.has_extension(ext_name)


@pytest.mark.parametrize("obj", [Doc, Span, Token])
def test_underscore_raises_for_dup(obj):
    obj.set_extension("test", default=None)
    with pytest.raises(ValueError):
        obj.set_extension("test", default=None)


@pytest.mark.parametrize(
    "invalid_kwargs",
    [
        {"getter": None, "setter": lambda: None},
        {"default": None, "method": lambda: None, "getter": lambda: None},
        {"setter": lambda: None},
        {"default": None, "method": lambda: None},
        {"getter": True},
    ],
)
def test_underscore_raises_for_invalid(invalid_kwargs):
    invalid_kwargs["force"] = True
    with pytest.raises(ValueError):
        Doc.set_extension("test", **invalid_kwargs)


@pytest.mark.parametrize(
    "valid_kwargs",
    [
        {"getter": lambda: None},
        {"getter": lambda: None, "setter": lambda: None},
        {"default": "hello"},
        {"default": None},
        {"method": lambda: None},
    ],
)
def test_underscore_accepts_valid(valid_kwargs):
    valid_kwargs["force"] = True
    Doc.set_extension("test", **valid_kwargs)


def test_underscore_mutable_defaults_list(en_vocab):
    """Test that mutable default arguments are handled correctly (see #2581)."""
    Doc.set_extension("mutable", default=[])
    doc1 = Doc(en_vocab, words=["one"])
    doc2 = Doc(en_vocab, words=["two"])
    doc1._.mutable.append("foo")
    assert len(doc1._.mutable) == 1
    assert doc1._.mutable[0] == "foo"
    assert len(doc2._.mutable) == 0
    doc1._.mutable = ["bar", "baz"]
    doc1._.mutable.append("foo")
    assert len(doc1._.mutable) == 3
    assert len(doc2._.mutable) == 0


def test_underscore_mutable_defaults_dict(en_vocab):
    """Test that mutable default arguments are handled correctly (see #2581)."""
    Token.set_extension("mutable", default={})
    token1 = Doc(en_vocab, words=["one"])[0]
    token2 = Doc(en_vocab, words=["two"])[0]
    token1._.mutable["foo"] = "bar"
    assert len(token1._.mutable) == 1
    assert token1._.mutable["foo"] == "bar"
    assert len(token2._.mutable) == 0
    token1._.mutable["foo"] = "baz"
    assert len(token1._.mutable) == 1
    assert token1._.mutable["foo"] == "baz"
    token1._.mutable["x"] = []
    token1._.mutable["x"].append("y")
    assert len(token1._.mutable) == 2
    assert token1._.mutable["x"] == ["y"]
    assert len(token2._.mutable) == 0


def test_underscore_dir(en_vocab):
    """Test that dir() correctly returns extension attributes. This enables
    things like tab-completion for the attributes in doc._."""
    Doc.set_extension("test_dir", default=None)
    doc = Doc(en_vocab, words=["hello", "world"])
    assert "_" in dir(doc)
    assert "test_dir" in dir(doc._)
    assert "test_dir" not in dir(doc[0]._)
    assert "test_dir" not in dir(doc[0:2]._)


def test_underscore_docstring(en_vocab):
    """Test that docstrings are available for extension methods, even though
    they're partials."""

    def test_method(doc, arg1=1, arg2=2):
        """I am a docstring"""
        return (arg1, arg2)

    Doc.set_extension("test_docstrings", method=test_method)
    doc = Doc(en_vocab, words=["hello", "world"])
    assert test_method.__doc__ == "I am a docstring"
    assert doc._.test_docstrings.__doc__.rsplit(". ")[-1] == "I am a docstring"


def test_underscore_for_unique_span(en_tokenizer):
    """Test that spans with the same boundaries but with different labels are uniquely identified (see #9706)."""
    Doc.set_extension(name="doc_extension", default=None)
    Span.set_extension(name="span_extension", default=None)
    Token.set_extension(name="token_extension", default=None)

    # Initialize doc
    text = "Hello, world!"
    doc = en_tokenizer(text)
    span_1 = Span(doc, 0, 2, "SPAN_1")
    span_2 = Span(doc, 0, 2, "SPAN_2")

    # Set custom extensions
    doc._.doc_extension = "doc extension"
    doc[0]._.token_extension = "token extension"
    span_1._.span_extension = "span_1 extension"
    span_2._.span_extension = "span_2 extension"

    # Assert extensions
    assert doc.user_data[_get_tuple(span_1)] == "span_1 extension"
    assert doc.user_data[_get_tuple(span_2)] == "span_2 extension"

    # Change label of span and assert extensions
    span_1.label_ = "NEW_LABEL"
    assert doc.user_data[_get_tuple(span_1)] == "span_1 extension"
    assert doc.user_data[_get_tuple(span_2)] == "span_2 extension"

    # Change KB_ID and assert extensions
    span_1.kb_id_ = "KB_ID"
    assert doc.user_data[_get_tuple(span_1)] == "span_1 extension"
    assert doc.user_data[_get_tuple(span_2)] == "span_2 extension"

    # Change extensions and assert
    span_2._.span_extension = "updated span_2 extension"
    assert doc.user_data[_get_tuple(span_1)] == "span_1 extension"
    assert doc.user_data[_get_tuple(span_2)] == "updated span_2 extension"

    # Change span ID and assert extensions
    span_2.id = 2
    assert doc.user_data[_get_tuple(span_1)] == "span_1 extension"
    assert doc.user_data[_get_tuple(span_2)] == "updated span_2 extension"

    # Assert extensions with original key
    assert doc.user_data[("._.", "doc_extension", None, None)] == "doc extension"
    assert doc.user_data[("._.", "token_extension", 0, None)] == "token extension"


def test_underscore_for_unique_span_from_docs(en_tokenizer):
    """Test that spans in the user_data keep the same data structure when using Doc.from_docs"""
    Span.set_extension(name="span_extension", default=None)
    Token.set_extension(name="token_extension", default=None)

    # Initialize doc
    text_1 = "Hello, world!"
    doc_1 = en_tokenizer(text_1)
    span_1a = Span(doc_1, 0, 2, "SPAN_1a")
    span_1b = Span(doc_1, 0, 2, "SPAN_1b")

    text_2 = "This is a test."
    doc_2 = en_tokenizer(text_2)
    span_2a = Span(doc_2, 0, 3, "SPAN_2a")

    # Set custom extensions
    doc_1[0]._.token_extension = "token_1"
    doc_2[1]._.token_extension = "token_2"
    span_1a._.span_extension = "span_1a extension"
    span_1b._.span_extension = "span_1b extension"
    span_2a._.span_extension = "span_2a extension"

    doc = Doc.from_docs([doc_1, doc_2])
    # Assert extensions
    assert doc_1.user_data[_get_tuple(span_1a)] == "span_1a extension"
    assert doc_1.user_data[_get_tuple(span_1b)] == "span_1b extension"
    assert doc_2.user_data[_get_tuple(span_2a)] == "span_2a extension"

    # Check extensions on merged doc
    assert doc.user_data[_get_tuple(span_1a)] == "span_1a extension"
    assert doc.user_data[_get_tuple(span_1b)] == "span_1b extension"
    assert (
        doc.user_data[
            (
                "._.",
                "span_extension",
                span_2a.start_char + len(doc_1.text) + 1,
                span_2a.end_char + len(doc_1.text) + 1,
                span_2a.label,
                span_2a.kb_id,
                span_2a.id,
            )
        ]
        == "span_2a extension"
    )


def test_underscore_for_unique_span_as_span(en_tokenizer):
    """Test that spans in the user_data keep the same data structure when using Span.as_doc"""
    Span.set_extension(name="span_extension", default=None)

    # Initialize doc
    text = "Hello, world!"
    doc = en_tokenizer(text)
    span_1 = Span(doc, 0, 2, "SPAN_1")
    span_2 = Span(doc, 0, 2, "SPAN_2")

    # Set custom extensions
    span_1._.span_extension = "span_1 extension"
    span_2._.span_extension = "span_2 extension"

    span_doc = span_1.as_doc(copy_user_data=True)

    # Assert extensions
    assert span_doc.user_data[_get_tuple(span_1)] == "span_1 extension"
    assert span_doc.user_data[_get_tuple(span_2)] == "span_2 extension"
