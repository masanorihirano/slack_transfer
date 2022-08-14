import argparse

from .._base import CommonNoLocalVolumeClient


def set_parser_token_test(parser: argparse.ArgumentParser) -> None:
    """See token_test section in :doc:`../../../user_guide/cli`"""
    parser.add_argument(
        "--token",
        type=str,
        required=True,
        help="Token obtained from slack. Starts with `xoxb-`",
    )
    parser.add_argument(
        "--as_downloader", action="store_true", help="for checking as downloader"
    )
    parser.add_argument(
        "--as_uploader", action="store_true", help="for checking as uploader"
    )


def main_token_test(args: argparse.Namespace) -> None:
    """See token_test section in :doc:`../../../user_guide/cli`"""
    client = CommonNoLocalVolumeClient(token=args.token)
    client.test_connection()

    if args.as_downloader:
        client.test_downloader()

    if args.as_uploader:
        client.test_uploader()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    set_parser_token_test(parser=parser)
    args = parser.parse_args()
    main_token_test(args=args)
