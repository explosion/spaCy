import plac
from ..download import download


@plac.annotations(
    force=("Force overwrite", "flag", "f", bool),
)
def main(data_size='all', force=False):
    if data_size in ('all', 'parser'):
        print("Downloading parsing model")
        download('en', force)
    if data_size in ('all', 'glove'):
        print("Downloading GloVe vectors")
        download('en_glove_cc_300_1m_vectors', force)


if __name__ == '__main__':
    plac.call(main)
