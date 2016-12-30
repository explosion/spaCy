import plac
import sputnik

from ..download import download
from .. import about


@plac.annotations(
    force=("Force overwrite", "flag", "f", bool),
    data_path=("Path to download model", "option", "d", str)
)
def main(data_size='all', force=False, data_path=None):
    if force:
        sputnik.purge(about.__title__, about.__version__)

    if data_size in ('all', 'parser'):
        print("Downloading parsing model")
        download('en', force=False, data_path=data_path)
    if data_size in ('all', 'glove'):
        print("Downloading GloVe vectors")
        download('en_glove_cc_300_1m_vectors', force=False, data_path=data_path)


if __name__ == '__main__':
    plac.call(main)
