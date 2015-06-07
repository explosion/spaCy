from __future__ import unicode_literals
import os
from os import path
import re


def split(text):
    """Split an annotation file by sentence. Each sentence's annotation should
    be a single string."""
    return text.strip().split('\n')[1:-1]
    

def parse(string, strip_bad_periods=False):
    """Given a sentence's annotation string, return a list of word strings,
    and a list of named entities, where each entity is a (start, end, label)
    triple."""
    tokens = []
    tags = []
    open_tag = None
    # Arbitrary corrections to promote alignment, and ensure that entities
    # begin at a space. This allows us to treat entities as tokens, making it
    # easier to return the list of entities.
    string = string.replace('... .', '...')
    string = string.replace('U.S.</ENAMEX> .', 'U.S.</ENAMEX>')
    string = string.replace('Co.</ENAMEX> .', 'Co.</ENAMEX>')
    string = string.replace('U.S. .', 'U.S.')
    string = string.replace('<ENAMEX ', '<ENAMEX')
    string = string.replace(' E_OFF="', 'E_OFF="')
    string = string.replace(' S_OFF="', 'S_OFF="')
    string = string.replace('units</ENAMEX>-<ENAMEX', 'units</ENAMEX> - <ENAMEX')
    string = string.replace('<ENAMEXTYPE="PERSON"E_OFF="1">Paula</ENAMEX> Zahn', 'Paula Zahn')
    string = string.replace('<ENAMEXTYPE="CARDINAL"><ENAMEXTYPE="CARDINAL">little</ENAMEX> drain</ENAMEX>', 'little drain')
    for substr in string.strip().split():
        substr = _fix_inner_entities(substr)
        tokens.append(_get_text(substr))
        try:
            tag, open_tag = _get_tag(substr, open_tag)
        except:
            raise
        tags.append(tag)
    return tokens, tags


tag_re = re.compile(r'<ENAMEXTYPE="[^"]+">')
def _fix_inner_entities(substr):
    tags = tag_re.findall(substr)
    if '</ENAMEX' in substr and not substr.endswith('</ENAMEX'):
            substr = substr.replace('</ENAMEX>', '') + '</ENAMEX>'
    if tags:
        substr = tag_re.sub('', substr)
        return tags[0] + substr
    else:
        return substr


def _get_tag(substr, tag):
    if substr.startswith('<'):
        tag = substr.split('"')[1]
        if substr.endswith('>'):
            return 'U-' + tag, None
        else:
            return 'B-%s' % tag, tag
    elif substr.endswith('>'):
        return 'L-' + tag, None
    elif tag is not None:
        return 'I-' + tag, tag
    else:
        return 'O', None


def _get_text(substr):
    if substr.startswith('<'):
        substr = substr.split('>', 1)[1]
    if substr.endswith('>'):
        substr = substr.split('<')[0]
    return reform_string(substr)


def tags_to_entities(tags):
    entities = []
    start = None
    for i, tag in enumerate(tags):
        if tag.startswith('O'):
            # TODO: We shouldn't be getting these malformed inputs. Fix this.
            if start is not None:
                start = None
            continue
        elif tag == '-':
            continue
        elif tag.startswith('I'):
            assert start is not None, tags[:i]
            continue
        if tag.startswith('U'):
            entities.append((tag[2:], i, i))
        elif tag.startswith('B'):
            start = i
        elif tag.startswith('L'):
            entities.append((tag[2:], start, i))
            start = None
        else:
            raise Exception(tag)
    return entities


def reform_string(tok):
    tok = tok.replace("``", '"')
    tok = tok.replace("`", "'")
    tok = tok.replace("''", '"')
    tok = tok.replace('\\', '')
    tok = tok.replace('-LCB-', '{')
    tok = tok.replace('-RCB-', '}')
    tok = tok.replace('-RRB-', ')')
    tok = tok.replace('-LRB-', '(')
    tok = tok.replace("'T-", "'T")
    tok = tok.replace('-AMP-', '&')
    return tok
