"""Read a vector file, and prepare it as binary data, for easy consumption"""

import plac

from spacy.vocab import write_binary_vectors


def main(in_loc, out_loc):
    write_binary_vectors(in_loc, out_loc)


if __name__ == '__main__':
    plac.call(main)
