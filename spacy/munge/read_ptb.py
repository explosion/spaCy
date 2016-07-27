import re
import os
from os import path


def parse(sent_text, strip_bad_periods=False):
    sent_text = sent_text.strip()
    assert sent_text and sent_text.startswith('(')
    open_brackets = []
    brackets = []
    bracketsRE = re.compile(r'(\()([^\s\)\(]+)|([^\s\)\(]+)?(\))')
    word_i = 0
    words = []
    # Remove outermost bracket
    if sent_text.startswith('(('):
        sent_text = sent_text.replace('((', '( (', 1)
    for match in bracketsRE.finditer(sent_text[2:-1]):
        open_, label, text, close = match.groups()
        if open_:
            assert not close
            assert label.strip()
            open_brackets.append((label, word_i))
        else:
            assert close
            label, start = open_brackets.pop()
            assert label.strip()
            if strip_bad_periods and words and _is_bad_period(words[-1], text):
                continue
            # Traces leave 0-width bracket, but no token
            if text and label != '-NONE-':
                words.append(text)
                word_i += 1
            else:
                brackets.append((label, start, word_i))
    return words, brackets


def _is_bad_period(prev, period):
    if period != '.':
        return False
    elif prev == '.':
        return False
    elif not prev.endswith('.'):
        return False
    else:
        return True


def split(text):
    sentences = []
    current = []

    for line in text.strip().split('\n'):
        line = line.rstrip()
        if not line:
            continue
        # Detect the start of sentences by line starting with (
        # This is messy, but it keeps bracket parsing at the sentence level
        if line.startswith('(') and current:
            sentences.append('\n'.join(current))
            current = []
        current.append(line)
    if current:
        sentences.append('\n'.join(current))
    return sentences
