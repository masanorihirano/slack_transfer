import argparse
import glob
import os
import unicodedata
from typing import Dict
from typing import List

from slack_transfer import DownloaderClient
from slack_transfer import UploaderClient


def set_parser_bookmark(parser: argparse.ArgumentParser) -> None:
    """See bookmark section in :doc:`../../../user_guide/cli`"""
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
        "--uploader_token",
        "-tu",
        type=str,
        required=True,
        help="upload token obtained from slack (the destination workspace). Starts with `xoxb-`",
    )
    parser.add_argument(
        "--channel_names",
        type=str,
        default=None,
        help="channel names you want to move bookmarks. If not set, set to all available channels. "
        + "Set by comma-separation for multiple inputs. For example, `general,random`",
    )
    parser.add_argument(
        "--name_mappings",
        type=str,
        default=None,
        help="You can set name mappings between the channel names of the original and destination workspaces. "
        + "Comma-separated dictionaries (key:value) are available. For example, `old_name1:new_name1,old_name2:new_name2`.",
    )


def main_bookmark(args: argparse.Namespace) -> None:
    """See bookmark section in :doc:`../../../user_guide/cli`"""
    if args.channel_names is not None:
        channel_names = args.channel_names.split(",")
    else:
        channel_names = None

    local_data_dir = args.data_dir
    os.makedirs(local_data_dir, exist_ok=True)
    downloader = DownloaderClient(
        local_data_dir=local_data_dir, token=args.downloader_token
    )
    channels_list: List[Dict] = downloader.download_channels_list()
    if channel_names:
        channels_list = list(
            filter(lambda x: (x["name"] in channel_names), channels_list)  # type: ignore
        )
    for i, channel in enumerate(channels_list):
        downloader.download_bookmark(
            channel_id=channel["id"], channel_name=channel["name"]
        )

    uploader = UploaderClient(
        local_data_dir=local_data_dir, token=args.uploader_token, timeout=300
    )
    name_mappings = {}
    if args.name_mappings:
        name_mappings = dict(
            [
                (dict_input.split(":")[0], dict_input.split(":")[1])
                for dict_input in args.name_mappings.split(",")
            ]
        )
    uploader.create_all_channels(
        channel_names=channel_names, name_mappings=name_mappings
    )
    channel_files: List[str] = list(
        map(
            lambda x: unicodedata.normalize("NFC", x),
            glob.glob(os.path.join(uploader.local_data_dir, "channels", "*.json")),
        )
    )
    if channel_names:
        channel_files = list(
            filter(
                lambda x: (os.path.basename(x)[:-5] in channel_names),  # type: ignore
                channel_files,
            )
        )
    uploader_channel_list = uploader.get_channels_list()
    for i, channel_file_path in enumerate(channel_files):
        old_channel_name = os.path.basename(channel_file_path).replace(".json", "")
        if old_channel_name in name_mappings:
            new_channel_name = name_mappings[old_channel_name]
        else:
            new_channel_name = old_channel_name
        print(f"{i + 1}/{len(channel_files)}: {old_channel_name} -> {new_channel_name}")
        channel_candidate_list = list(
            filter(lambda x: x["name"] == new_channel_name, uploader_channel_list)
        )
        if len(channel_candidate_list) != 1:
            raise IOError(
                f"channel not found in the destination channel: {new_channel_name}"
            )
        uploader.insert_bookmarks(
            channel_id=channel_candidate_list[0]["id"],
            old_channel_name=old_channel_name,
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    set_parser_bookmark(parser=parser)
    args = parser.parse_args()
    main_bookmark(args=args)
