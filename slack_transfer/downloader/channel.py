import json
import os
import time
import warnings
from typing import Dict
from typing import List
from typing import Optional

import requests
import tqdm.std
from slack_sdk.errors import SlackApiError
from slack_sdk.web import SlackResponse

from slack_transfer.commons.client import DownloaderClient


def download_channels_list(client: DownloaderClient) -> List[Dict]:
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

    json.dump(
        channels,
        open(
            os.path.join(client.local_data_dir, "channels.json"),
            mode="w",
            encoding="utf-8",
        ),
        indent=4,
    )
    return channels


def get_replies(client: DownloaderClient, channel_id: str, ts: str) -> List[Dict]:
    messages: List[Dict] = []
    next_cursor: Optional[str] = None
    while True:
        response = client.conversations_replies(
            channel=channel_id, ts=ts, cursor=next_cursor
        )
        if not response["ok"]:
            raise IOError(
                f"replies cannot be fetched in downloading WS data. (channel_id: {channel_id}, ts: {ts})"
            )
        messages.extend(response["messages"])

        if "response_metadata" in response:
            next_cursor = response["response_metadata"]["next_cursor"]
            if next_cursor == "":
                break
        else:
            break
    return messages


def download_file(
    client: DownloaderClient, file_id: str, file_name: str, url_private: str
) -> None:
    res = requests.get(
        url=url_private,
        allow_redirects=True,
        headers={"Authorization": f"Bearer {client.token}"},
        stream=True,
    )
    file_name = f"{file_id}--{file_name}"
    if res.status_code != 200:
        warnings.warn(f"failed to download: {url_private} as {file_name}")
        return None
    file_path = os.path.join(client.local_data_dir, "files", file_name)
    with open(file_path, mode="wb") as f:
        f.write(res.content)


def download_channel_history(
    client: DownloaderClient,
    channel_id: str,
    channel_name: str,
    latest: Optional[str] = None,
    ts_progress_bar: Optional[tqdm.std.tqdm] = None,
    ts_now: Optional[int] = None,
    auto_join: bool = True,
) -> None:
    # ToDo: 1 channel内でAPI limit来た場合の挙動
    if ts_progress_bar:
        if ts_now is None:
            ts_now = int(time.time())

    messages = []
    next_cursor: Optional[str] = None
    while True:
        try:
            response = client.conversations_history(
                channel=channel_id,
                latest=latest,
                cursor=next_cursor,
                include_all_metadata=True,
            )
        except SlackApiError as e:
            if e.response["error"] == "not_in_channel":
                if auto_join:
                    try:
                        client.conversations_join(channel=channel_id)
                        continue
                    except:
                        pass
                warnings.warn(f"slack bot is not in `{channel_name}`. Skip this.")
                return None
            else:
                raise e
        if not response["ok"]:
            raise IOError(
                f"channel history cannot be fetched in downloading WS data. (channel_id: {channel_id}, channel_name: {channel_name}, latest: {latest})"
            )
        for message in response["messages"]:
            if "files" in message:
                for file in message["files"]:
                    url_private: str = file["url_private"]
                    file_id: str = file["id"]
                    file_name: str = file["name"]
                    download_file(
                        client=client,
                        file_id=file_id,
                        file_name=file_name,
                        url_private=url_private,
                    )

            if "reply_count" in message and message["reply_count"] > 0:
                ts: str = message["ts"]
                replies = get_replies(client=client, channel_id=channel_id, ts=ts)
                messages.extend(replies)
            else:
                messages.append(message)

        if ts_progress_bar and len(messages) > 0:
            oldest_ts = messages[-1]["ts"]
            progress_ts = int(ts_now - float(oldest_ts))
            update_p = progress_ts - ts_progress_bar.n
            ts_progress_bar.update(update_p)

        if "response_metadata" in response:
            next_cursor = response["response_metadata"]["next_cursor"]
            latest = None
            if next_cursor == "":
                break
        else:
            break
    messages = list(
        {
            message["client_msg_id"]: message
            for message in [
                message for message in messages if "client_msg_id" in message
            ]
        }.values()
    ) + [message for message in messages if "client_msg_id" not in message]
    messages.sort(key=lambda x: x["ts"], reverse=False)
    json.dump(
        messages,
        open(
            os.path.join(client.local_data_dir, "channels", f"{channel_name}.json"),
            mode="w",
            encoding="utf-8",
        ),
        indent=4,
    )
