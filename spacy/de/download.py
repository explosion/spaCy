import plac
from ..download import download


@plac.annotations(
    force=("Force overwrite", "flag", "f", bool),
    data_path=("Path to download model", "option", "d", str)
)
def main(data_size='all', force=False, data_path=None):
    download('de', force=force, data_path=data_path)


if __name__ == '__main__':
    plac.call(main)
