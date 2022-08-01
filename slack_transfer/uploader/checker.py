import glob
import json
import os
from typing import Dict
from typing import List
from typing import Optional

from slack_sdk.web import SlackResponse

from slack_transfer.commons.client import UploaderClient


def get_channels_list(client: UploaderClient) -> List[Dict]:
    channels: List[Dict] = []
    next_cursor: Optional[str] = None

    while True:
        response: SlackResponse = client.conversations_list(
            cursor=next_cursor, types="public_channel, private_channel"
        )
        if not response["ok"]:
            raise IOError("channel list cannot be fetched in downloading WS data.")
        channels.extend(response["channels"])

        if "response_metadata" in response:
            next_cursor = response["response_metadata"]["next_cursor"]
            if next_cursor == "":
                break
        else:
            break

    return channels


def check_conflict(
    client: UploaderClient, name_mappings: Optional[Dict[str, str]] = None
) -> List[str]:
    existing_channels = get_channels_list(client=client)
    downloaded_channels = json.load(
        open(
            os.path.join(client.local_data_dir, "channels.json"),
            mode="r",
            encoding="utf-8",
        )
    )
    existing_channels_name = set(map(lambda x: x["name"], existing_channels))
    downloaded_channels_name = set(
        map(
            lambda x: name_mappings[x["name"]]
            if name_mappings is not None and x["name"] in name_mappings
            else x["name"],
            downloaded_channels,
        )
    )
    return list(existing_channels_name & downloaded_channels_name)
