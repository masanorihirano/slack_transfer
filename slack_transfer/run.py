import argparse
import glob
import json
import os.path
import time
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
) -> None:
    os.makedirs(local_data_dir, exist_ok=True)
    if not skip_download:
        downloader = DownloaderClient(
            local_data_dir=local_data_dir, token=downloader_token
        )
        channels_list: List[Dict] = downloader.download_channels_list()
        downloader.download_members_list()

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

    if not skip_upload:
        if uploader_token is None:
            raise ValueError("uploader_token is required")
        uploader = UploaderClient(
            local_data_dir=local_data_dir, token=uploader_token, timeout=300
        )
        if name_mappings is None:
            name_mappings = {}

        conflicts = uploader.check_upload_conflict(name_mappings=name_mappings)
        if len(conflicts) > 0 and not override:
            raise ValueError(
                f"channels: {', '.join(conflicts)} are already exist. please set mapping or override=True"
            )
        uploader.create_all_channels(name_mappings=name_mappings)
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
        channel_files: List[str] = glob.glob(
            os.path.join(uploader.local_data_dir, "channels", "*.json")
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
            uploader.data_insert(
                channel_name=new_channel_name,
                old_members_dict=old_members_dict,
                old_channel_name=old_channel_name,
            )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
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
        "--name_mappings",
        type=str,
        default=None,
        help="You can set name mappings between the channel names of the original and destination workspaces. "
        + "Comma-separated dictionaries (key:value) are available. For example, `old_name1:new_name1,old_name2:new_name2`.",
    )
    args = parser.parse_args()
    name_mappings = None
    if args.name_mappings:
        name_mappings = dict(
            [
                (dict_input.split(":")[0], dict_input.split(":")[1])
                for dict_input in args.name_mappings.split(",")
            ]
        )
    if name_mappings:
        print(f"name mappings: {name_mappings}")
    run(
        local_data_dir=args.data_dir,
        downloader_token=args.downloader_token,
        uploader_token=args.uploader_token,
        override=args.override,
        skip_download=args.skip_download,
        skip_upload=args.skip_upload,
        name_mappings=name_mappings,
    )
