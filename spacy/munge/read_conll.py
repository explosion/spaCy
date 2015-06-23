from __future__ import unicode_literals


def split(text):
    return [sent.strip() for sent in text.split('\n\n') if sent.strip()]


def parse(sent_text, strip_bad_periods=False):
    sent_text = sent_text.strip()
    assert sent_text
    annot = []
    words = []
    id_map = {-1: -1}
    for i, line in enumerate(sent_text.split('\n')):
        word, tag, head, dep = _parse_line(line)
        if strip_bad_periods and words and _is_bad_period(words[-1], word):
            continue
        id_map[i] = len(words)
  
        annot.append({
            'id': len(words),
            'word': word,
            'tag': tag,
            'head': int(head) - 1,
            'dep': dep})
        words.append(word)
    for entry in annot:
        entry['head'] = id_map[entry['head']]
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


def _parse_line(line):
    pieces = line.split()
    if len(pieces) == 4:
        return pieces
    else:
        return pieces[1], pieces[3], pieces[5], pieces[6]

