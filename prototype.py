import glob
import json
import os.path
import time
from typing import Dict
from typing import List

import tqdm

from slack_transfer import DownloaderClient
from slack_transfer import UploaderClient


def main(
    downloader_token: str,
    uploader_token: str,
    override: bool = False,
    skip_download: bool = False,
    skip_upload: bool = False,
) -> None:
    local_data_dir = os.path.join(os.path.dirname(__file__), "local_data_dir")
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
        uploader = UploaderClient(
            local_data_dir=local_data_dir, token=uploader_token, timeout=300
        )
        name_mappings = {"general": "_general", "random": "_random"}
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
        for channel_file_path in channel_files:
            old_channel_name = os.path.basename(channel_file_path).replace(".json", "")
            if old_channel_name in name_mappings:
                new_channel_name = name_mappings[old_channel_name]
            else:
                new_channel_name = old_channel_name
            uploader.data_insert(
                channel_name=new_channel_name,
                old_members_dict=old_members_dict,
                old_channel_name=old_channel_name,
            )


if __name__ == "__main__":
    main(
        downloader_token="xoxb-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
        uploader_token="xoxb-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
        override=True,
    )
