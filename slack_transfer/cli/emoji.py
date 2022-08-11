import argparse
import os

from slack_transfer import DownloaderClient


def set_parser_emoji(parser: argparse.ArgumentParser) -> None:
    """See emoji section in :doc:`../../../user_guide/cli`"""
    parser.add_argument(
        "--data_dir",
        "-d",
        type=str,
        required=True,
        help="Data directory for saving download data or loading upload data. This is required.",
    )
    parser.add_argument(
        "--downloader_token",
        "-td",
        type=str,
        required=True,
        help="Download token obtained from slack (the original workspace). Starts with `xoxb-`",
    )


def main_emoji(args: argparse.Namespace) -> None:
    """See emoji section in :doc:`../../../user_guide/cli`"""

    local_data_dir = args.data_dir
    os.makedirs(local_data_dir, exist_ok=True)
    downloader = DownloaderClient(
        local_data_dir=local_data_dir, token=args.downloader_token
    )
    downloader.download_emoji()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    set_parser_emoji(parser=parser)
    args = parser.parse_args()
    main_emoji(args=args)
