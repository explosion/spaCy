# coding: utf8
from __future__ import unicode_literals

import os
import warnings
import inspect


def add_codes(err_cls):
    """Add error codes to string messages via class attribute names."""
    class ErrorsWithCodes(object):
        def __getattribute__(self, code):
            msg = getattr(err_cls, code)
            return '[{code}] {msg}'.format(code=code, msg=msg)
    return ErrorsWithCodes()


@add_codes
class Warnings(object):
    W001 = ("As of spaCy v2.0, the keyword argument `path=` is deprecated. "
            "You can now call spacy.load with the path as its first argument, "
            "and the model's meta.json will be used to determine the language "
            "to load. For example:\nnlp = spacy.load('{path}')")
    W002 = ("Tokenizer.from_list is now deprecated. Create a new Doc object "
            "instead and pass in the strings as the `words` keyword argument, "
            "for example:\nfrom spacy.tokens import Doc\n"
            "doc = Doc(nlp.vocab, words=[...])")
    W003 = ("Positional arguments to Doc.merge are deprecated. Instead, use "
            "the keyword arguments, for example tag=, lemma= or ent_type=.")
    W004 = ("No text fixing enabled. Run `pip install ftfy` to enable fixing "
            "using ftfy.fix_text if necessary.")
    W005 = ("Doc object not parsed. This means displaCy won't be able to "
            "generate a dependency visualization for it. Make sure the Doc "
            "was processed with a model that supports dependency parsing, and "
            "not just a language class like `English()`. For more info, see "
            "the docs:\nhttps://spacy.io/usage/models")
    W006 = ("No entities to visualize found in Doc object. If this is "
            "surprising to you, make sure the Doc was processed using a model "
            "that supports named entity recognition, and check the `doc.ents` "
            "property manually if necessary.")


@add_codes
class Errors(object):
    E001 = ("No component '{name}' found in pipeline. Available names: {opts}")
    E002 = ("Can't find factory for '{name}'. This usually happens when spaCy "
            "calls `nlp.create_pipe` with a component name that's not built "
            "in - for example, when constructing the pipeline from a model's "
            "meta.json. If you're using a custom component, you can write to "
            "`Language.factories['{name}']` or remove it from the model meta "
            "and add it via `nlp.add_pipe` instead.")
    E003 = ("Not a valid pipeline component. Expected callable, but "
            "got {component} (name: '{name}').")
    E004 = ("If you meant to add a built-in component, use `create_pipe`: "
            "`nlp.add_pipe(nlp.create_pipe('{component}'))`")
    E005 = ("Pipeline component '{name}' returned None. If you're using a "
            "custom component, maybe you forgot to return the processed Doc?")
    E006 = ("Invalid constraints. You can only set one of the following: "
            "before, after, first, last.")
    E007 = ("'{name}' already exists in pipeline. Existing names: {opts}")
    E008 = ("Some current components would be lost when restoring previous "
            "pipeline state. If you added components after calling "
            "`nlp.disable_pipes()`, you should remove them explicitly with "
            "`nlp.remove_pipe()` before the pipeline is restored. Names of "
            "the new components: {names}")
    E009 = ("The `update` method expects same number of docs and golds, but "
            "got: {n_docs} docs, {n_golds} golds.")
    E010 = ("Word vectors set to length 0. This may be because you don't have "
            "a model installed or loaded, or because your model doesn't "
            "include word vectors. For more info, see the docs:\n"
            "https://spacy.io/usage/models")
    E011 = ("Unknown operator: '{op}'. Options: {opts}")
    E012 = ("Cannot add pattern for zero tokens to matcher.\nKey: {key}")
    E013 = ("Error selecting action in matcher")
    E014 = ("Uknown tag ID: {tag}")
    E015 = ("Conflicting morphology exception for ({tag}, {orth}). Use "
            "`force=True` to overwrite.")
    E016 = ("MultitaskObjective target should be function or one of: dep, "
            "tag, ent, dep_tag_offset, ent_tag.")
    E017 = ("Can only add unicode or bytes. Got type: {value_type}")
    E018 = ("Can't retrieve string for hash '{hash_value}'.")
    E019 = ("Can't create transition with unknown action ID: {action}. Action "
            "IDs are enumerated in spacy/syntax/{src}.pyx.")
    E020 = ("Could not find a gold-standard action to supervise the "
            "dependency parser. The tree is non-projective (i.e. it has "
            "crossing arcs - see spacy/syntax/nonproj.pyx for definitions). "
            "The ArcEager transition system only supports projective trees. "
            "To learn non-projective representations, transform the data "
            "before training and after parsing. Either pass "
            "`make_projective=True` to the GoldParse class, or use "
            "spacy.syntax.nonproj.preprocess_training_data.")
    E021 = ("Could not find a gold-standard action to supervise the "
            "dependency parser. The GoldParse was projective. The transition "
            "system has {n_actions} actions. State at failure: {state}")
    E022 = ("Could not find a transition with the name '{name}' in the NER "
            "model.")
    E023 = ("Error cleaning up beam: The same state occurred twice at "
            "memory address {addr} and position {i}.")
    E024 = ("Could not find an optimal move to supervise the parser. Usually, "
            "this means the GoldParse was not correct. For example, are all "
            "labels added to the model?")
    E025 = ("String is too long: {length} characters. Max is 2**30.")
    E026 = ("Error accessing token at position {i}: out of bounds in Doc of "
            "length {length}.")
    E027 = ("Arguments 'words' and 'spaces' should be sequences of the same "
            "length, or 'spaces' should be left default at None. spaces "
            "should be a sequence of booleans, with True meaning that the "
            "word owns a ' ' character following it.")
    E028 = ("orths_and_spaces expects either a list of unicode string or a "
            "list of (unicode, bool) tuples. Got bytes instance: {value}")
    E029 = ("noun_chunks requires the dependency parse, which requires a "
            "statistical model to be installed and loaded. For more info, see "
            "the documentation:\nhttps://spacy.io/usage/models")
    E030 = ("Sentence boundaries unset. You can add the 'sentencizer' "
            "component to the pipeline with: "
            "nlp.add_pipe(nlp.create_pipe('sentencizer')) "
            "Alternatively, add the dependency parser, or set sentence "
            "boundaries by setting doc[i].is_sent_start.")
    E031 = ("Invalid token: empty string ('') at position {i}.")
    E032 = ("Conflicting attributes specified in doc.from_array(): "
            "(HEAD, SENT_START). The HEAD attribute currently sets sentence "
            "boundaries implicitly, based on the tree structure. This means "
            "the HEAD attribute would potentially override the sentence "
            "boundaries set by SENT_START.")
    E033 = ("Cannot load into non-empty Doc of length {length}.")
    E034 = ("Doc.merge received {n_args} non-keyword arguments. Expected "
            "either 3 arguments (deprecated), or 0 (use keyword arguments).\n"
            "Arguments supplied:\n{args}\nKeyword arguments:{kwargs}")
    E035 = ("Error creating span with start {start} and end {end} for Doc of "
            "length {length}.")
    E036 = ("Error calculating span: Can't find a token starting at character "
            "offset {start}.")
    E037 = ("Error calculating span: Can't find a token ending at character "
            "offset {end}.")
    E038 = ("Error finding sentence for span. Infinite loop detected.")
    E039 = ("Array bounds exceeded while searching for root word. This likely "
            "means the parse tree is in an invalid state. Please report this "
            "issue here: http://github.com/explosion/spaCy/issues")
    E040 = ("Attempt to access token at {i}, max length {max_length}.")
    E041 = ("Invalid comparison operator: {op}. Likely a Cython bug?")
    E042 = ("Error accessing doc[{i}].nbor({j}), for doc of length {length}.")
    E043 = ("Refusing to write to token.sent_start if its document is parsed, "
            "because this may cause inconsistent state.")
    E044 = ("Invalid value for token.sent_start: {value}. Must be one of: "
            "None, True, False")
    E045 = ("Possibly infinite loop encountered while looking for {attr}.")
    E046 = ("Can't retrieve unregistered extension attribute '{name}'. Did "
            "you forget to call the `set_extension` method?")
    E047 = ("Can't assign a value to unregistered extension attribute "
            "'{name}'. Did you forget to call the `set_extension` method?")
    E048 = ("Can't import language {lang} from spacy.lang.")
    E049 = ("Can't find spaCy data directory: '{path}'. Check your "
            "installation and permissions, or use spacy.util.set_data_path "
            "to customise the location if necessary.")
    E050 = ("Can't find model '{name}'. It doesn't seem to be a shortcut "
            "link, a Python package or a valid path to a data directory.")
    E051 = ("Cant' load '{name}'. If you're using a shortcut link, make sure "
            "it points to a valid package (not just a data directory).")
    E052 = ("Can't find model directory: {path}")
    E053 = ("Could not read meta.json from {path}")
    E054 = ("No valid '{setting}' setting found in model meta.json.")
    E055 = ("Invalid ORTH value in exception:\nKey: {key}\nOrths: {orths}")
    E056 = ("Invalid tokenizer exception: ORTH values combined don't match "
            "original string.\nKey: {key}\nOrths: {orths}")
    E057 = ("Stepped slices not supported in Span objects. Try: "
            "list(tokens)[start:stop:step] instead.")
    E058 = ("Could not retrieve vector for key {key}.")
    E059 = ("One (and only one) keyword arg must be set. Got: {kwargs}")
    E060 = ("Cannot add new key to vectors: the table is full. Current shape: "
            "({rows}, {cols}).")
    E061 = ("Bad file name: {filename}. Example of a valid file name: "
            "'vectors.128.f.bin'")
    E062 = ("Cannot find empty bit for new lexical flag. All bits between 0 "
            "and 63 are occupied. You can replace one by specifying the "
            "`flag_id` explicitly, e.g. "
            "`nlp.vocab.add_flag(your_func, flag_id=IS_ALPHA`.")
    E063 = ("Invalid value for flag_id: {value}. Flag IDs must be between 1 "
            "and 63 (inclusive).")
    E064 = ("Error fetching a Lexeme from the Vocab. When looking up a "
            "string, the lexeme returned had an orth ID that did not match "
            "the query string. This means that the cached lexeme structs are "
            "mismatched to the string encoding table. The mismatched:\n"
            "Query string: {string}\nOrth cached: {orth}\nOrth ID: {orth_id}")
    E065 = ("Only one of the vector table's width and shape can be specified. "
            "Got width {width} and shape {shape}.")
    E066 = ("Error creating model helper for extracting columns. Can only "
            "extract columns by positive integer. Got: {value}.")
    E067 = ("Invalid BILUO tag sequence: Got a tag starting with 'I' (inside "
            "an entity) without a preceding 'B' (beginning of an entity). "
            "Tag sequence:\n{tags}")
    E068 = ("Invalid BILUO tag: '{tag}'.")
    E069 = ("Invalid gold-standard parse tree. Found cycle between word "
            "IDs: {cycle}")
    E070 = ("Invalid gold-standard data. Number of documents ({n_docs}) "
            "does not align with number of annotations ({n_annots}).")
    E071 = ("Error creating lexeme: specified orth ID ({orth}) does not "
            "match the one in the vocab ({vocab_orth}).")
    E072 = ("Error serializing lexeme: expected data length {length}, "
            "got {bad_length}.")
    E073 = ("Cannot assign vector of length {new_length}. Existing vectors "
            "are of length {length}. You can use `vocab.reset_vectors` to "
            "clear the existing vectors and resize the table.")
    E074 = ("Error interpreting compiled match pattern: patterns are expected "
            "to end with the attribute {attr}. Got: {bad_attr}.")
    E075 = ("Error accepting match: length ({length}) > maximum length "
            "({max_len}).")
    E076 = ("Error setting tensor on Doc: tensor has {rows} rows, while Doc "
            "has {words} words.")
    E077 = ("Error computing {value}: number of Docs ({n_docs}) does not "
            "equal number of GoldParse objects ({n_golds}) in batch.")
    E078 = ("Error computing score: number of words in Doc ({words_doc}) does "
            "not equal number of words in GoldParse ({words_gold}).")
    E079 = ("Error computing states in beam: number of predicted beams "
            "({pbeams}) does not equal number of gold beams ({gbeams}).")
    E080 = ("Duplicate state found in beam: {key}.")
    E081 = ("Error getting gradient in beam: number of histories ({n_hist}) "
            "does not equal number of losses ({losses}).")
    E082 = ("Error deprojectivizing parse: number of heads ({n_heads}), "
            "projective heads ({n_proj_heads}) and labels ({n_labels}) do not "
            "match.")
    E083 = ("Error setting extension: only one of `default`, `method`, or "
            "`getter` (plus optional `setter`) is allowed. Got: {nr_defined}")
    E084 = ("Error assigning label ID {label} to span: not in StringStore.")
    E085 = ("Can't create lexeme for string '{string}'.")
    E086 = ("Error deserializing lexeme '{string}': orth ID {orth_id} does "
            "not match hash {hash_id} in StringStore.")
    E087 = ("Unknown displaCy style: {style}.")
    E088 = ("Text of length {length} exceeds maximum of {max_length}. The "
            "v2.x parser and NER models require roughly 1GB of temporary "
            "memory per 100,000 characters in the input. This means long "
            "texts may cause memory allocation errors. If you're not using "
            "the parser or NER, it's probably safe to increase the "
            "`nlp.max_length` limit. The limit is in number of characters, so "
            "you can check whether your inputs are too long by checking "
            "`len(text)`.")
    E089 = ("Extensions can't have a setter argument without a getter "
            "argument. Check the keyword arguments on `set_extension`.")
    E090 = ("Extension '{name}' already exists on {obj}. To overwrite the "
            "existing extension, set `force=True` on `{obj}.set_extension`.")
    E091 = ("Invalid extension attribute {name}: expected callable or None, "
            "but got: {value}")
    E092 = ("Could not find or assign name for word vectors. Ususally, the "
            "name is read from the model's meta.json in vector.name. "
            "Alternatively, it is built from the 'lang' and 'name' keys in "
            "the meta.json. Vector names are required to avoid issue #1660.")
    E093 = ("token.ent_iob values make invalid sequence: I without B\n{seq}")
    E094 = ("Error reading line {line_num} in vectors file {loc}.")
    E095 = ("Can't write to frozen dictionary. This is likely an internal "
            "error. Are you writing to a default function argument?")
    E096 = ("Invalid object passed to displaCy: Can only visualize Doc or "
             "Span objects, or dicts if set to manual=True.")


@add_codes
class TempErrors(object):
    T001 = ("Max length currently 10 for phrase matching")
    T002 = ("Pattern length ({doc_len}) >= phrase_matcher.max_length "
            "({max_len}). Length can be set on initialization, up to 10.")
    T003 = ("Resizing pre-trained Tagger models is not currently supported.")
    T004 = ("Currently parser depth is hard-coded to 1. Received: {value}.")
    T005 = ("Currently history size is hard-coded to 0. Received: {value}.")
    T006 = ("Currently history width is hard-coded to 0. Received: {value}.")
    T007 = ("Can't yet set {attr} from Span. Vote for this feature on the "
            "issue tracker: http://github.com/explosion/spaCy/issues")
    T008 = ("Bad configuration of Tagger. This is probably a bug within "
            "spaCy. We changed the name of an internal attribute for loading "
            "pre-trained vectors, and the class has been passed the old name "
            "(pretrained_dims) but not the new name (pretrained_vectors).")


class ModelsWarning(UserWarning):
    pass


WARNINGS = {
    'user': UserWarning,
    'deprecation': DeprecationWarning,
    'models': ModelsWarning,
}


def _get_warn_types(arg):
    if arg == '':  # don't show any warnings
        return []
    if not arg or arg == 'all':  # show all available warnings
        return WARNINGS.keys()
    return [w_type.strip() for w_type in arg.split(',')
            if w_type.strip() in WARNINGS]


def _get_warn_excl(arg):
    if not arg:
        return []
    return [w_id.strip() for w_id in arg.split(',')]


SPACY_WARNING_FILTER = os.environ.get('SPACY_WARNING_FILTER')
SPACY_WARNING_TYPES = _get_warn_types(os.environ.get('SPACY_WARNING_TYPES'))
SPACY_WARNING_IGNORE = _get_warn_excl(os.environ.get('SPACY_WARNING_IGNORE'))


def user_warning(message):
    _warn(message, 'user')


def deprecation_warning(message):
    _warn(message, 'deprecation')


def models_warning(message):
    _warn(message, 'models')


def _warn(message, warn_type='user'):
    """
    message (unicode): The message to display.
    category (Warning): The Warning to show.
    """
    w_id = message.split('[', 1)[1].split(']', 1)[0]  # get ID from string
    if warn_type in SPACY_WARNING_TYPES and w_id not in SPACY_WARNING_IGNORE:
        category = WARNINGS[warn_type]
        stack = inspect.stack()[-1]
        with warnings.catch_warnings():
            if SPACY_WARNING_FILTER:
                warnings.simplefilter(SPACY_WARNING_FILTER, category)
            warnings.warn_explicit(message, category, stack[1], stack[2])
