import argparse

from ..run import main_run
from ..run import set_parser_run
from ..version import __version__


def main() -> None:
    print(
        f"""=========================
Welcome to slack_transfer
This is CLI v.{__version__}
========================="""
    )
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    parser_run = subparsers.add_parser("run", help="see `run -h`")
    set_parser_run(parser=parser_run)
    parser_run.set_defaults(handler=main_run)

    args = parser.parse_args()
    if hasattr(args, "handler"):
        args.handler(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
