# coding: utf8
from __future__ import print_function
# NB! This breaks in plac on Python 2!!
# from __future__ import unicode_literals

if __name__ == '__main__':
    import plac
    import sys
    from spacy.cli import download, link, info, package, train, convert
    from spacy.cli import vocab, init_model, profile, evaluate, validate
    from spacy.util import prints

    commands = {
        'download': download,
        'link': link,
        'info': info,
        'train': train,
        'evaluate': evaluate,
        'convert': convert,
        'package': package,
        'vocab': vocab,
        'init-model': init_model,
        'profile': profile,
        'validate': validate
    }
    if len(sys.argv) == 1:
        prints(', '.join(commands), title="Available commands", exits=1)
    command = sys.argv.pop(1)
    sys.argv[0] = 'spacy %s' % command
    if command in commands:
        plac.call(commands[command], sys.argv[1:])
    else:
        prints(
            "Available: %s" % ', '.join(commands),
            title="Unknown command: %s" % command,
            exits=1)
