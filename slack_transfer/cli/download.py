import argparse

from slack_transfer.run import run


def set_parser_download(parser: argparse.ArgumentParser) -> None:
    """See download section in :doc:`../../../user_guide/cli`"""
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
    parser.add_argument(
        "--channel_names",
        type=str,
        default=None,
        help="channel names you want to download. If not set, set to all available channels. "
        + "Set by comma-separation for multiple inputs. For example, `general,random`",
    )
    parser.add_argument(
        "--skip_bookmarks", action="store_true", help="Skip process bookmarks."
    )


def main_download(args: argparse.Namespace) -> None:
    """See download section in :doc:`../../../user_guide/cli`"""
    if args.channel_names is not None:
        channel_names = args.channel_names.split(",")
    else:
        channel_names = None

    run(
        local_data_dir=args.data_dir,
        downloader_token=args.downloader_token,
        skip_upload=True,
        channel_names=channel_names,
        skip_bookmarks=args.skip_bookmarks,
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    set_parser_download(parser=parser)
    args = parser.parse_args()
    main_download(args=args)
