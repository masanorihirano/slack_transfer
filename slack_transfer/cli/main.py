import argparse

from slack_transfer.run import main_run
from slack_transfer.run import set_parser_run
from slack_transfer.version import __version__

from .bookmark import main_bookmark
from .bookmark import set_parser_bookmark
from .download import main_download
from .download import set_parser_download
from .emoji import main_emoji
from .emoji import set_parser_emoji
from .file_volume import main_file_volume
from .file_volume import set_parser_file_volume
from .token_test import main_token_test
from .token_test import set_parser_token_test
from .upload import main_upload
from .upload import set_parser_upload


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

    parser_download = subparsers.add_parser("download", help="see `download -h`")
    set_parser_download(parser=parser_download)
    parser_download.set_defaults(handler=main_download)

    parser_upload = subparsers.add_parser("upload", help="see `upload -h`")
    set_parser_upload(parser=parser_upload)
    parser_upload.set_defaults(handler=main_upload)

    parser_bookmark = subparsers.add_parser("bookmark", help="see `bookmark -h`")
    set_parser_bookmark(parser=parser_bookmark)
    parser_bookmark.set_defaults(handler=main_bookmark)

    parser_emoji = subparsers.add_parser("emoji", help="see `emoji -h`")
    set_parser_emoji(parser=parser_emoji)
    parser_emoji.set_defaults(handler=main_emoji)

    parser_token_test = subparsers.add_parser("token_test", help="see `token_test -h`")
    set_parser_token_test(parser=parser_token_test)
    parser_token_test.set_defaults(handler=main_token_test)

    try:
        import tkinter

        from slack_transfer.interactive import interactive

        interactive_wrap = lambda _: interactive()
        parser_interactive = subparsers.add_parser(
            "interactive", help="interactive mode."
        )
        parser_interactive.set_defaults(handler=interactive_wrap)
    except:
        pass

    args = parser.parse_args()
    if hasattr(args, "handler"):
        args.handler(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
