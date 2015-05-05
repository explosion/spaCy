from __future__ import unicode_literals


def split(text):
    return [sent.strip() for sent in text.split('\n\n') if sent.strip()]


def parse(sent_text, strip_bad_periods=False):
    sent_text = sent_text.strip()
    assert sent_text
    annot = []
    words = []
    i = 0
    for line in sent_text.split('\n'):
        word, tag, head, dep = line.split()
        if strip_bad_periods and words and _is_bad_period(words[-1], word):
            continue
  
        annot.append({
            'id': i,
            'word': word,
            'tag': tag,
            'head': int(head) - 1 if int(head) != 0 else i,
            'dep': dep})
        words.append(word)
        i += 1
    return words, annot


def _is_bad_period(prev, period):
    if period != '.':
        return False
    elif prev == '.':
        return False
    elif not prev.endswith('.'):
        return False
    else:
        return True


