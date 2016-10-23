import plac
import sputnik

from ..download import download
from .. import about


@plac.annotations(
    force=("Force overwrite", "flag", "f", bool),
)
def main(data_size='all', force=False):
    if force:
        sputnik.purge(about.__title__, about.__version__)

    if data_size in ('all', 'parser'):
        print("Downloading parsing model")
        download('en', False)
    if data_size in ('all', 'glove'):
        print("Downloading GloVe vectors")
        download('en_glove_cc_300_1m_vectors', False)


if __name__ == '__main__':
    plac.call(main)
