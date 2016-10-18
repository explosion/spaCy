import plac
from ..download import download


@plac.annotations(
    force=("Force overwrite", "flag", "f", bool),
    ignore_glove=("Don't install the GloVe vectors", "flag", "g", bool),
)
def main(data_size='all', force=False, ignore_glove=False):
    download('en', force)
    download('en_glove_cc_300_1m_vectors', force)


if __name__ == '__main__':
    plac.call(main)
