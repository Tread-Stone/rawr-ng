from argparse import ArgumentParser
from _schema import read_config


def _main():
    parser = ArgumentParser()
    parser.add_argument(
        "config_file",
        help="Path to yaml config file",
        type=read_config
    )
    args = vars(parser.parse_args())


if __name__ == "__main__":
    _main()
