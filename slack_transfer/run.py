import argparse
import glob
import json
import os.path
import time
import unicodedata
from ssl import SSLContext
from typing import Dict
from typing import List
from typing import Optional

import tqdm

from .client import DownloaderClient
from .client import UploaderClient


def run(
    local_data_dir: str,
    downloader_token: Optional[str] = None,
    uploader_token: Optional[str] = None,
    override: bool = False,
    skip_download: bool = False,
    skip_upload: bool = False,
    name_mappings: Optional[Dict[str, str]] = None,
    channel_names: Optional[List[str]] = None,
    skip_bookmarks: bool = False,
    ssl: Optional[SSLContext] = None,
    time_zone: str = "Asia/Tokyo",
) -> None:
    """See run section in :doc:`/user_guide/cli`

    Args:
        local_data_dir (str): Data directory for saving download data or loading upload data. This is required.
        downloader_token (str; Optional; default=None): Download token obtained from slack (the original workspace).
            Starts with xoxb-. This is required when skip_download=False.
        uploader_token (str; Optional; default=None): Upload token obtained from slack (the destination workspace).
            Starts with xoxb-. This is required when skip_upload=False.
        override (bool; Optional; default=False): This flag enables message migration to the destination workspace
            even when a channel already exists. This means that additional messages are inserted after the message
            already sent to the channel. If you want not to do so, please delete the channel on the destination workspace first.
        skip_download (bool; Optional; default=False): Skip download. This is usually used when the download is already finished.
        skip_upload (bool; Optional; default=False): Skip upload. This is usually used when only the download is necessary.
        name_mappings (Dict[str, str]; Optional; default=None): You can set name mappings between the channel names of the
            original and destination workspaces. For example, :code:`{"old_name1": "new_name1", "old_name2": "new_name2"}`.
        channel_names (List[str]; Optional; default=None): channel names you want to process.
            If not set, set to all available channels.
        skip_bookmarks (bool; Optional; default=False): Skip process bookmarks.
        ssl: (SSLContext; Optional; default=None): : An [`ssl.SSLContext`][1] instance, helpful for specifying
            your own custom certificate chain.
        time_zone (str; Optional; default=Asia/Tokyo): time zone to preview the original post data on the destination WS.
            See: https://dateutil.readthedocs.io/en/stable/tz.html
    """
    os.makedirs(local_data_dir, exist_ok=True)
    if not skip_download:
        downloader = DownloaderClient(
            local_data_dir=local_data_dir, token=downloader_token, ssl=ssl
        )
        downloader.test_connection()
        downloader.test_downloader()
    if not skip_upload:
        if uploader_token is None:
            raise ValueError("uploader_token is required")
        uploader = UploaderClient(
            local_data_dir=local_data_dir, token=uploader_token, ssl=ssl
        )
        uploader.test_uploader()
    if not skip_download:
        channels_list: List[Dict] = downloader.download_channels_list()
        downloader.download_members_list()

        if channel_names:
            channels_list = list(
                filter(lambda x: (x["name"] in channel_names), channels_list)  # type: ignore
            )

        ts_now = int(time.time())
        times_to_rest = list(map(lambda x: ts_now - x["created"], channels_list))
        for i, (channel, time_to_rest) in enumerate(zip(channels_list, times_to_rest)):
            print(f"{i+1}/{len(channels_list)}: {channel['name']}")
            pbar = tqdm.tqdm(total=time_to_rest)
            downloader.download_channel_history(
                channel_id=channel["id"],
                channel_name=channel["name"],
                ts_progress_bar=pbar,
                ts_now=ts_now,
            )
            pbar.close()
            time.sleep(1)
            if not skip_bookmarks:
                downloader.download_bookmark(
                    channel_id=channel["id"], channel_name=channel["name"]
                )

    if not skip_upload:
        if name_mappings is None:
            name_mappings = {}

        old_members = json.load(
            open(
                os.path.join(uploader.local_data_dir, "members.json"),
                mode="r",
                encoding="utf-8",
            )
        )
        old_members_dict = dict(
            [(member["id"], member["profile"]["real_name"]) for member in old_members]
        )
        old_members_icon_url_dict = dict(
            [
                (
                    member["id"],
                    member["profile"]["image_original"]
                    if "image_original" in member["profile"]
                    else member["profile"]["image_512"],
                )
                for member in old_members
            ]
        )

        conflicts = uploader.check_upload_conflict(name_mappings=name_mappings)
        reverse_name_mappings = dict([(v, k) for k, v in name_mappings.items()])
        conflicts = list(
            filter(
                lambda x: (  # type: ignore
                    (
                        x
                        in [
                            name_mappings[y] if y in name_mappings else y
                            for y in channel_names
                        ]
                    )
                    if channel_names
                    else True
                    and uploader.check_channel_exists(channel_name=x)
                    and not uploader.check_insert_finished(
                        channel_name=x,
                        old_members_dict=old_members_dict,
                        old_channel_name=(
                            reverse_name_mappings[x]
                            if x in reverse_name_mappings
                            else x
                        ),
                        time_zone=time_zone,
                    )
                ),
                conflicts,
            )
        )
        if len(conflicts) > 0 and not override:
            raise ValueError(
                f"channels: {', '.join(conflicts)} are already exist. please set mapping or override=True"
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
        for i, channel_file_path in enumerate(channel_files):
            old_channel_name = os.path.basename(channel_file_path).replace(".json", "")
            if old_channel_name in name_mappings:
                new_channel_name = name_mappings[old_channel_name]
            else:
                new_channel_name = old_channel_name
            print(
                f"{i + 1}/{len(channel_files)}: {old_channel_name} -> {new_channel_name}"
            )
            if (
                uploader.check_channel_exists(channel_name=new_channel_name)
                and uploader.check_insert_finished(
                    channel_name=new_channel_name,
                    old_members_dict=old_members_dict,
                    old_channel_name=old_channel_name,
                    time_zone=time_zone,
                )
                and not override
            ):
                print("already finished. skip.")
                continue
            new_channel_id = uploader.data_insert(
                channel_name=new_channel_name,
                old_members_dict=old_members_dict,
                old_members_icon_url_dict=old_members_icon_url_dict,
                old_channel_name=old_channel_name,
                time_zone=time_zone,
            )
            if not skip_bookmarks:
                uploader.insert_bookmarks(
                    channel_id=new_channel_id, old_channel_name=old_channel_name
                )


def set_parser_run(parser: argparse.ArgumentParser) -> None:
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
        default=None,
        help="Download token obtained from slack (the original workspace). Starts with `xoxb-`",
    )
    parser.add_argument(
        "--uploader_token",
        "-tu",
        type=str,
        default=None,
        help="Upload token obtained from slack (the destination workspace). Starts with `xoxb-`",
    )
    parser.add_argument(
        "--override",
        action="store_true",
        help="This flag enables message migration to the destination workspace even when a channel already exists."
        + " This means that additional messages are inserted after the message already sent to the channel."
        + " If you want not to do so, please delete the channel on the destination workspace first.",
    )
    parser.add_argument(
        "--skip_download",
        action="store_true",
        help="Skip download. This is usually used when the download is already finished.",
    )
    parser.add_argument(
        "--skip_upload",
        action="store_true",
        help="Skip upload. This is usually used when only the download is necessary.",
    )
    parser.add_argument(
        "--channel_names",
        type=str,
        default=None,
        help="channel names you want to process. If not set, set to all available channels. "
        + "Set by comma-separation for multiple inputs. For example, `general,random`",
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


def main_run(args: argparse.Namespace) -> None:
    name_mappings = None
    if args.name_mappings:
        name_mappings = dict(
            [
                (dict_input.split(":")[0], dict_input.split(":")[1])
                for dict_input in args.name_mappings.split(",")
            ]
        )
    if args.channel_names is not None:
        channel_names = args.channel_names.split(",")
    else:
        channel_names = None
    if name_mappings:
        print(f"name mappings: {name_mappings}")
    run(
        local_data_dir=args.data_dir,
        downloader_token=args.downloader_token,
        uploader_token=args.uploader_token,
        override=args.override,
        skip_download=args.skip_download,
        skip_upload=args.skip_upload,
        channel_names=channel_names,
        name_mappings=name_mappings,
        skip_bookmarks=args.skip_bookmarks,
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    set_parser_run(parser=parser)
    args = parser.parse_args()
    main_run(args=args)
