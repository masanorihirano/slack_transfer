import datetime
import json
import os.path
import time
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple

from dateutil import tz
from slack_sdk.errors import SlackApiError
from slack_sdk.models.attachments import Attachment
from slack_sdk.web import SlackResponse

from slack_transfer.commons.client import UploaderClient
from slack_transfer.uploader.checker import get_channels_list


def create_all_channels(
    client: UploaderClient, name_mappings: Optional[Dict[str, str]] = None
) -> None:
    downloaded_channels = json.load(
        open(
            os.path.join(client.local_data_dir, "channels.json"),
            mode="r",
            encoding="utf-8",
        )
    )
    channels_list: List[Dict] = get_channels_list(client=client)
    for old_channel_info in downloaded_channels:
        new_channel_name = (
            name_mappings[old_channel_info["name"]]
            if name_mappings and old_channel_info["name"] in name_mappings
            else old_channel_info["name"]
        )
        new_channel_if_exists = list(
            filter(lambda x: x["name"] == new_channel_name, channels_list)
        )
        if len(new_channel_if_exists) != 0:
            if len(new_channel_if_exists) > 1:
                raise AssertionError(
                    f"Error: multiple channels exists ({new_channel_name})"
                )
            continue
        response = client.conversations_create(name=new_channel_name)
        if not response["ok"]:
            raise IOError(f"Error in making channel {new_channel_name}")
        new_channel_info = response["channel"]
        new_channel_id = new_channel_info["id"]
        client.conversations_setTopic(
            channel=new_channel_id, topic=old_channel_info["topic"]["value"]
        )
        client.conversations_setPurpose(
            channel=new_channel_id, purpose=old_channel_info["purpose"]["value"]
        )


def upload_file(
    client: UploaderClient,
    old_file_id: str,
    file_name: str,
    channel_id: Optional[str] = None,
    title: Optional[str] = None,
    filetype: Optional[str] = None,
) -> Tuple[str, str]:
    file_path = os.path.join(
        client.local_data_dir, "files", f"{old_file_id}--{file_name}"
    )
    response: SlackResponse = client.files_upload(
        file=file_path,
        filename=file_name,
        filetype=filetype,
        title=title,
        channels=channel_id,
    )
    if not response["ok"]:
        raise IOError(f"Error in uploading file {file_path}")
    return response["file"]["id"], response["file"]["permalink"]


def data_insert(
    client: UploaderClient,
    channel_name: str,
    old_members_dict: Dict[str, str],
    old_channel_name: Optional[str] = None,
    time_zone: str = "Asia/Tokyo",
):
    tz_delta = tz.gettz(time_zone)
    channels_list: List[Dict] = get_channels_list(client=client)
    new_channel_info = list(filter(lambda x: x["name"] == channel_name, channels_list))[
        0
    ]
    new_channel_id = new_channel_info["id"]

    data_file_name = (
        f"{old_channel_name}.json" if old_channel_name else f"{channel_name}.json"
    )
    data_file_path = os.path.join(client.local_data_dir, "channels", data_file_name)
    messages: List[Dict] = json.load(open(data_file_path, mode="r", encoding="utf-8"))
    messages.sort(key=lambda x: x["ts"], reverse=False)
    ts_mapper: Dict[str, str] = {}
    for message in messages:
        file_ids = []
        file_permalinks = []
        file_titles = []
        if "files" in message:
            for file in message["files"]:
                old_file_id = file["id"]
                file_name = file["name"]
                title = file["title"]
                file_type = file["filetype"]
                new_file_id, new_file_permalink = upload_file(
                    client=client,
                    old_file_id=old_file_id,
                    file_name=file_name,
                    channel_id=None,
                    title=title,
                    filetype=file_type,
                )
                file_ids.append(new_file_id)
                file_permalinks.append(new_file_permalink)
                file_titles.append(title)

        new_thread_ts = None
        if "thread_ts" in message.keys() and message["thread_ts"] != "":
            if message["thread_ts"] in ts_mapper:
                new_thread_ts = ts_mapper[message["thread_ts"]]

        i_count = 0
        while True:
            try:
                date_time = datetime.datetime.fromtimestamp(
                    float(message["ts"]), tz=tz_delta
                ).strftime("%Y/%m/%d %H:%M %Z")
                response: SlackResponse = client.chat_postMessage(
                    channel=new_channel_id,
                    text=message["text"],
                    attachments=(
                        message["attachments"] if "attachments" in message else []
                    ),
                    blocks=(
                        list(
                            filter(
                                lambda x: x["type"] not in ["rich_text"],
                                message["blocks"],
                            )
                        )
                        if "blocks" in message
                        else []
                    )
                    + [
                        {"type": "file", "source": "remote", "file_id": file_id}
                        for file_id in file_ids
                    ],
                    thread_ts=new_thread_ts,
                    reply_broadcast=(
                        message["subtype"] == "thread_broadcast"
                        if "subtype" in message
                        else False
                    ),
                    username=old_members_dict[message["user"]] + " [" + date_time + "]",
                )
                break
            except SlackApiError as e:
                if e.response["error"] == "ratelimited":
                    i_count += 1
                    if i_count < 10:
                        time.sleep(2)
                        continue
                raise e

        if not response["ok"]:
            raise IOError(f"Error in posting message {message['text']}")

        if "thread_ts" in message.keys() and message["thread_ts"] != "":
            if message["thread_ts"] in ts_mapper:
                pass
            else:
                ts_mapper[message["thread_ts"]] = response["message"]["ts"]
        else:
            ts_mapper[message["ts"]] = response["message"]["ts"]
