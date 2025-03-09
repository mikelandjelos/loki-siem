import argparse

from . import preprocessing
from .drain import drain
from .drain3 import drain3


def main():
    parser = argparse.ArgumentParser(description="Main CLI for log parsing.")
    subparsers = parser.add_subparsers(dest="parsing_utility", required=True)

    drain.get_parser(subparsers)
    drain3.get_parser(subparsers)
    preprocessing.get_parser(subparsers)

    args = parser.parse_args()

    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
