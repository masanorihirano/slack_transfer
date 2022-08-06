import argparse

from ..run import main_run
from ..run import set_parser_run
from ..version import __version__
from .file_volume import main_file_volume
from .file_volume import set_parser_file_volume


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

    parser_file_volume = subparsers.add_parser(
        "file_volume", help="see `file_volume -h`"
    )
    set_parser_file_volume(parser=parser_file_volume)
    parser_file_volume.set_defaults(handler=main_file_volume)

    args = parser.parse_args()
    if hasattr(args, "handler"):
        args.handler(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
