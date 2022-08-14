import argparse

from slack_transfer.run import run


def set_parser_upload(parser: argparse.ArgumentParser) -> None:
    """See upload section in :doc:`../../../user_guide/cli`"""
    parser.add_argument(
        "--data_dir",
        "-d",
        type=str,
        required=True,
        help="Data directory for saving upload data or loading upload data. This is required.",
    )
    parser.add_argument(
        "--uploader_token",
        "-tu",
        type=str,
        required=True,
        help="upload token obtained from slack (the destination workspace). Starts with `xoxb-`",
    )
    parser.add_argument(
        "--old_channel_names",
        type=str,
        default=None,
        help="channel names you want to upload. Name is selected among downloaded WS. "
        + "If not set, set to all available channels. "
        + "Set by comma-separation for multiple inputs. For example, `general,random`",
    )
    parser.add_argument(
        "--override",
        action="store_true",
        help="This flag enables message migration to the destination workspace even when a channel already exists."
        + " This means that additional messages are inserted after the message already sent to the channel."
        + " If you want not to do so, please delete the channel on the destination workspace first.",
    )
    parser.add_argument(
        "--name_mappings",
        type=str,
        default=None,
        help="You can set name mappings between the channel names of the original and destination workspaces. "
        + "Comma-separated dictionaries (key:value) are available. For example, `old_name1:new_name1,old_name2:new_name2`.",
    )
    parser.add_argument(
        "--skip_bookmarks", action="store_true", help="Skip process bookmarks."
    )


def main_upload(args: argparse.Namespace) -> None:
    """See upload section in :doc:`../../../user_guide/cli`"""
    if args.name_mappings:
        name_mappings = dict(
            [
                (dict_input.split(":")[0], dict_input.split(":")[1])
                for dict_input in args.name_mappings.split(",")
            ]
        )
    else:
        name_mappings = None

    if args.old_channel_names is not None:
        channel_names = args.old_channel_names.split(",")
    else:
        channel_names = None

    run(
        local_data_dir=args.data_dir,
        uploader_token=args.uploader_token,
        override=args.override,
        skip_download=True,
        name_mappings=name_mappings,
        channel_names=channel_names,
        skip_bookmarks=args.skip_bookmarks,
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    set_parser_upload(parser=parser)
    args = parser.parse_args()
    main_upload(args=args)
