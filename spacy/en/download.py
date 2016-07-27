import plac
from ..download import download


@plac.annotations(
    force=("Force overwrite", "flag", "f", bool),
)
def main(data_size='all', force=False):
    download('en', force)


if __name__ == '__main__':
    plac.call(main)
