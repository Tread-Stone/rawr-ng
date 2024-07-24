from argparse import ArgumentParser
from _schema import read_config, EnumerationOptions


def _main():
    parser = ArgumentParser()
    parser.add_argument(
        metavar="config_file",
        dest="cfg",
        help="Path to yaml config file",
        type=read_config
    )
    args = vars(parser.parse_args())
    cfg = args["cfg"]

    enumeration_options: EnumerationOptions = EnumerationOptions.from_dict(cfg["enumeration"])

    enumeration_options |= EnumerationOptions.no_rdp

    print({**enumeration_options})

def _run(**args):
    pass

def _dump():
    pass


if __name__ == "__main__":
    _main()


