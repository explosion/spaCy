import io
import plac

from spacy.en import English


def main(text_loc):
    with io.open(text_loc, 'r', encoding='utf8') as file_:
        text = file_.read()
    NLU = English()
    for paragraph in text.split('\n\n'):
        tokens = NLU(paragraph)

        ent_starts = {}
        ent_ends = {}
        for span in tokens.ents:
            ent_starts[span.start] = span.label_
            ent_ends[span.end] = span.label_

        output = []
        for token in tokens:
            if token.i in ent_starts:
                output.append('<%s>' % ent_starts[token.i])
            output.append(token.orth_)
            if (token.i+1) in ent_ends:
                output.append('</%s>' % ent_ends[token.i+1])
        output.append('\n\n')
    print ' '.join(output)


if __name__ == '__main__':
    plac.call(main)
