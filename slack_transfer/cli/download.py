import argparse
import time
from typing import Dict
from typing import List

import tqdm

from slack_transfer import DownloaderClient


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
        help="channel names you want to check the total volume of files. If not set, set to all available channels. "
        + "Set by comma-separation for multiple inputs. For example, `general,random`",
    )


def main_download(args: argparse.Namespace) -> None:
    """See download section in :doc:`../../../user_guide/cli`"""
    downloader = DownloaderClient(
        local_data_dir=args.data_dir, token=args.downloader_token
    )
    channels_list: List[Dict] = downloader.download_channels_list()
    downloader.download_members_list()

    if args.channel_names is not None:
        channels = args.channel_names.split(",")
        channels_list = list(filter(lambda x: x["name"] in channels, channels_list))
    if len(channels_list):
        raise ValueError("channels not found.")

    ts_now = int(time.time())
    times_to_rest = list(map(lambda x: ts_now - x["created"], channels_list))
    for i, (channel, time_to_rest) in enumerate(zip(channels_list, times_to_rest)):
        print(f"{i + 1}/{len(channels_list)}: {channel['name']}")
        pbar = tqdm.tqdm(total=time_to_rest)
        downloader.download_channel_history(
            channel_id=channel["id"],
            channel_name=channel["name"],
            ts_progress_bar=pbar,
            ts_now=ts_now,
        )
        pbar.close()
        time.sleep(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    set_parser_download(parser=parser)
    args = parser.parse_args()
    main_download(args=args)
