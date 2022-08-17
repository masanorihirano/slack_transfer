import datetime
import json
import os.path
import time
import warnings
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple
from typing import Union

import tqdm
from dateutil import tz
from markdownify import markdownify
from slack_sdk.errors import SlackApiError
from slack_sdk.web import SlackResponse

from .._base import UploaderClientABC
from .common import get_channels_list


def create_all_channels(
    client: UploaderClientABC,
    channel_names: Optional[List[str]] = None,
    name_mappings: Optional[Dict[str, str]] = None,
) -> None:
    """create all channels or specified channels. In this process, channel purpose and description are also set.

    Args:
        client (UploaderClientABC): uploader client. If use this via any UploaderClient Class, self is automatically set.
            Thus, ignore this.
        channel_names (List[str]; Optional; default=None): list of channels to be made.
        name_mappings (Dict[str, str]; Optional; default=None): You can set name mappings between the channel names of the
            original and destination workspaces. For example, :code:`{"old_name1": "new_name1", "old_name2": "new_name2"}`.
    """
    downloaded_channels = json.load(
        open(
            os.path.join(client.local_data_dir, "channels.json"),
            mode="r",
            encoding="utf-8",
        )
    )
    if channel_names:
        downloaded_channels = list(
            filter(lambda x: (x["name"] in channel_names), downloaded_channels)  # type: ignore
        )
    else:
        downloaded_channels = list(
            filter(
                lambda x: os.path.exists(
                    os.path.join(client.local_data_dir, "channels", f"{x['name']}.json")
                ),
                downloaded_channels,
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
    client: UploaderClientABC,
    old_file_id: str,
    file_name: str,
    channel_id: Optional[str] = None,
    title: Optional[str] = None,
    filetype: Optional[str] = None,
    is_slack_post: bool = False,
) -> Optional[Tuple[str, str]]:
    """upload a file. This is usually preprocess for posting message attaching files.
    **So, this method is not usually directly used by users.**

    Args:
        client (UploaderClientABC): uploader client. If use this via any UploaderClient Class, self is automatically set.
            Thus, ignore this.
        old_file_id (str): old file id. This is required to find the file in local data dir.
        file_name (str): file name. It have to be the original old file name.
            This is also required to find the file in local data dir. The uploaded file is also named as the same.
        channel_id (str; Optional; default=None): channel id (usually 9-digits string)
        title (str; Optional; default=None): title for appending to the file when uploading.
        filetype (str; Optional; default=None): file type. It is not mimetype. See: https://api.slack.com/types/file#types
        is_slack_post (bool; Optional; default=False): set True if this file is slack post.
    """
    file_path: Optional[str] = os.path.join(
        client.local_data_dir, "files", f"{old_file_id}--{file_name}"
    )
    content = None
    if is_slack_post:
        filetype = "post"
        if file_path is None:
            raise AssertionError
        # ToDo: better support of slack post
        content = (
            markdownify(
                json.load(open(file_path, mode="r"))["full"]
                .replace("<pre>", "```")
                .replace("</pre>", "```")
                .replace("<p>", "")
                .replace("</p>", "")
            )
            .replace("\n\n\n", "\n")
            .replace("\n\n", "\n")
        )
        file_path = None
    try:
        response: SlackResponse = client.files_upload(
            file=file_path,
            content=content,
            filename=file_name,
            filetype=filetype,
            title=title,
            channels=channel_id,
        )
        if channel_id:
            for ts in list(
                map(lambda x: x[0]["ts"], response["file"]["shares"]["public"].values())
            ):
                client.chat_delete(channel=channel_id, ts=ts)
    except FileNotFoundError as e:
        warnings.warn(
            f"file is missing (possibly duu to original slack limitations): {file_path}"
        )
        return None
    if not response["ok"]:
        raise IOError(f"Error in uploading file {file_path}")
    return response["file"]["id"], response["file"]["permalink"]


def check_channel_exists(client: UploaderClientABC, channel_name: str) -> bool:
    """check if a channel already exists or not

    Args:
        client (UploaderClientABC): uploader client. If use this via any UploaderClient Class, self is automatically set.
            Thus, ignore this.
        channel_name (str): channel name wanted to be checked.

    Yield:
         bool: return True if exists. Otherwise, return False.
    """
    channels_list: List[Dict] = get_channels_list(client=client)
    new_channel_infos = list(filter(lambda x: x["name"] == channel_name, channels_list))
    if len(new_channel_infos) > 1:
        raise AssertionError
    return len(new_channel_infos) == 1


def check_insert_finished(
    client: UploaderClientABC,
    channel_name: str,
    old_members_dict: Dict[str, str],
    old_channel_name: Optional[str] = None,
    time_zone: str = "Asia/Tokyo",
) -> bool:
    """check if the uploading for a channel already finished or not. This check is rough. Just checking some latest messages.
    Note that it raise error if the channel doesn't exist.

    Args:
        client (UploaderClientABC): uploader client. If use this via any UploaderClient Class, self is automatically set.
            Thus, ignore this.
        channel_name (str): channel name wanted to be checked.
        old_members_dict (Dict[str, str]): a dictionary between old user id and old user preview name.
            (Old means the original WS) key is 9-digit string if and value is the preview user name.
        old_channel_name (str; Optional; default=None): old channel name. It required to find the stored data.
        time_zone (str; Optional; default=Asia/Tokyo): time zone to preview the original post data on the destination WS.
            See: https://dateutil.readthedocs.io/en/stable/tz.html

    Yield:
         bool: return True if finished. Otherwise, return False.
    """
    # return error when channel not exists
    tz_delta = tz.gettz(time_zone)
    channels_list: List[Dict] = get_channels_list(client=client)
    new_channel_infos = list(filter(lambda x: x["name"] == channel_name, channels_list))
    if len(new_channel_infos) != 1:
        raise AssertionError("channel possibly does not exists")
    new_channel_info = new_channel_infos[0]
    new_channel_id = new_channel_info["id"]
    data_file_name = (
        f"{old_channel_name}.json" if old_channel_name else f"{channel_name}.json"
    )
    data_file_path = os.path.join(client.local_data_dir, "channels", data_file_name)
    old_messages: List[Dict] = json.load(
        open(data_file_path, mode="r", encoding="utf-8")
    )
    old_messages = list(
        filter(
            lambda x: "thread_ts" not in x
            or ("subtype" in x and x["subtype"] == "thread_broadcast"),
            old_messages,
        )
    )
    old_messages.sort(key=lambda x: x["ts"], reverse=False)

    response = client.conversations_history(channel=new_channel_id)
    new_messages = response["messages"]
    new_messages.sort(key=lambda x: x["ts"], reverse=False)

    expected_username_dict: Dict[str, int] = {}
    for i in range(1, min(len(old_messages) + 1, 10)):
        expected_date_time = datetime.datetime.fromtimestamp(
            float(old_messages[-i]["ts"]), tz=tz_delta
        ).strftime("%Y/%m/%d %H:%M %Z")
        expected: str = (
            (
                old_members_dict[old_messages[-i]["user"]]
                if "user" in old_messages[-i]
                and old_messages[-i]["user"] in old_members_dict
                else "Unknown member"
            )
            + " ["
            + expected_date_time
            + "]"
        )

        if expected in expected_username_dict:
            expected_username_dict[expected] += 1
        else:
            expected_username_dict[expected] = 1
    for key, value in expected_username_dict.items():
        if (
            len(
                list(
                    filter(
                        lambda x: "username" in x and x["username"] == key, new_messages
                    )
                )
            )
            < value
        ):
            return False
    return True


def data_insert(
    client: UploaderClientABC,
    channel_name: str,
    old_members_dict: Dict[str, str],
    old_members_icon_url_dict: Optional[Dict[str, str]] = None,
    old_channel_name: Optional[str] = None,
    time_zone: str = "Asia/Tokyo",
    progress: Union[bool, tqdm.tqdm] = True,
) -> str:
    """upload messages, files, reactions, and pins.

    Args:
        client (UploaderClientABC): uploader client. If use this via any UploaderClient Class, self is automatically set.
            Thus, ignore this.
        channel_name (str): channel name wanted to be checked.
        old_members_dict (Dict[str, str]): a dictionary between old user id and old user preview name.
            (Old means the original WS) key is 9-digit string if and value is the preview user name.
        old_members_icon_url_dict (Dict[str, str]]; Optional; default=None): a dictionary between old user id and old user
            icon url. key is 9-digit string if and value is url.
        old_channel_name (str; Optional; default=None): old channel name. It required to find the stored data.
        time_zone (str; Optional; default=Asia/Tokyo): time zone to preview the original post data on the destination WS.
            See: https://dateutil.readthedocs.io/en/stable/tz.html
        progress (Union[bool, tqdm.tqdm]; Optional; default=True): set progress bar. progress bar will be updated each time one
            message is processed. You can set progress bar from outside this method if you want to make the whole progress bar
            beyond each progress of each channel. If you set it to boolean, it is understood as if you want to show a progress
            bar only for this processing.

    Yield:
         str: channel id (9-digit string)
    """
    if old_members_icon_url_dict is None:
        old_members_icon_url_dict = {}
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
    progress_bar: tqdm.tqdm
    if isinstance(progress, bool):
        progress_bar = tqdm.tqdm(total=len(messages), disable=not progress)
    else:
        progress_bar = progress
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
                upload_start_st = int(time.time())
                try:
                    upload_results = upload_file(
                        client=client,
                        old_file_id=old_file_id,
                        file_name=file_name,
                        channel_id=new_channel_id,
                        title=title,
                        filetype=file_type,
                        is_slack_post=(
                            file["mimetype"] == "application/vnd.slack-docs"
                        ),
                    )
                except SlackApiError as e:
                    # ToDo: workaround for #11
                    for i_try in range(5):
                        try:
                            time.sleep(30 * i_try)
                            _response = client.files_list(
                                channel=None, ts_from=str(upload_start_st)
                            )
                            # ToDo: paging: たぶんほとんどの場合不要
                            if not _response["ok"] or len(_response["files"]) == 0:
                                raise IOError(f"Error in uploading file {file_name}")
                            file_candidates = list(
                                filter(
                                    lambda x: x["name"] == file_name
                                    and x["title"] == title,
                                    _response["files"],
                                )
                            )
                            if len(file_candidates) == 0:
                                raise IOError(f"Error in uploading file {file_name}")
                            upload_results = (
                                file_candidates[-1]["id"],
                                file_candidates[-1]["permalink"],
                            )
                            break
                        except Exception as e2:
                            if i_try == 4:
                                raise e2

                if upload_results:
                    new_file_id, new_file_permalink = upload_results
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
                blocks: List[Dict] = (
                    list(
                        filter(
                            lambda x: x["type"] not in ["rich_text", "call"],
                            message["blocks"],
                        )
                    )
                    if "blocks" in message
                    else []
                ) + [
                    {"type": "file", "source": "remote", "file_id": file_id}
                    for file_id in file_ids
                ]

                if len(blocks) != 0:
                    blocks = (
                        [
                            {
                                "type": "section",
                                "text": {
                                    "type": "mrkdwn",
                                    "text": message["text"][
                                        i
                                        * 3000 : min(
                                            len(message["text"]), (i + 1) * 3000
                                        )
                                    ],
                                },
                            }
                            for i in range((len(message["text"]) - 1) // 3000 + 1)
                        ]
                        if message["text"]
                        else []
                    ) + blocks

                if (
                    len(blocks) == 0
                    and message["text"] == ""
                    and "attachments" not in message
                ):
                    message[
                        "text"
                    ] = "[Migration Error] this thread is missing (possibly due to original slack limitation)"
                attachments: List[Dict] = (
                    message["attachments"] if "attachments" in message else []
                )
                for i_attachment in range(len(attachments)):
                    if "blocks" in attachments[i_attachment]:
                        attachments[i_attachment]["blocks"] = list(
                            filter(
                                lambda x: x["type"] not in ["call"],
                                attachments[i_attachment]["blocks"],
                            )
                        )
                response: SlackResponse = client.chat_postMessage(
                    channel=new_channel_id,
                    text=message["text"],
                    attachments=attachments,
                    blocks=blocks,
                    thread_ts=new_thread_ts,
                    reply_broadcast=(
                        message["subtype"] == "thread_broadcast"
                        if "subtype" in message
                        else False
                    ),
                    username=(
                        old_members_dict[message["user"]]
                        if "user" in message and message["user"] in old_members_dict
                        else "Unknown member"
                    )
                    + " ["
                    + date_time
                    + "]",
                    icon_url=old_members_icon_url_dict[message["user"]]
                    if "user" in message
                    and message["user"] in old_members_icon_url_dict
                    else None,
                )
                break
            except SlackApiError as e:
                if e.response["error"] in ["ratelimited", "fatal_error"]:
                    i_count += 1
                    if i_count < 10:
                        time.sleep(2)
                        continue
                raise e

        if not response["ok"]:
            raise IOError(f"Error in posting message {message['text']}")

        if "reactions" in message:
            for reaction in message["reactions"]:
                try:
                    client.reactions_add(
                        channel=new_channel_id,
                        name=reaction["name"],
                        timestamp=response["ts"],
                    )
                except SlackApiError as e:
                    if e.response["error"] == "invalid_name":
                        warnings.warn(
                            f"reaction `{reaction['name']}` doesn't exist. Skip adding this reaction."
                        )
                    else:
                        raise e

        if "pinned_to" in message:
            channels_ids_pined = message["pinned_to"]
            if len(channels_ids_pined) > 1:
                # ToDo: "pined to multiple channels is not supported"
                raise NotImplemented
            client.pins_add(channel=new_channel_id, timestamp=response["ts"])

        if "thread_ts" in message.keys() and message["thread_ts"] != "":
            if message["thread_ts"] in ts_mapper:
                pass
            else:
                ts_mapper[message["thread_ts"]] = response["message"]["ts"]
        else:
            ts_mapper[message["ts"]] = response["message"]["ts"]
        progress_bar.update(n=1)
    return new_channel_id


def check_upload_conflict(
    client: UploaderClientABC, name_mappings: Optional[Dict[str, str]] = None
) -> List[str]:
    """check upload conflict in terms of channel name.

    This is not considered if the channel is already finished processing. Just checking name conflict.

    Args:
        client (UploaderClientABC): uploader client. If use this via any UploaderClient Class, self is automatically set.
            Thus, ignore this.
        name_mappings (Dict[str, str]; Optional; default=None): You can set name mappings between the channel names of the
            original and destination workspaces. For example, :code:`{"old_name1": "new_name1", "old_name2": "new_name2"}`.

    Yield:
        List[str]: name conflicting channels' names.
    """
    existing_channels = get_channels_list(client=client)
    downloaded_channels = json.load(
        open(
            os.path.join(client.local_data_dir, "channels.json"),
            mode="r",
            encoding="utf-8",
        )
    )
    downloaded_channels = list(
        filter(
            lambda x: os.path.exists(
                os.path.join(client.local_data_dir, "channels", f"{x['name']}.json")
            ),
            downloaded_channels,
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


def insert_bookmarks(
    client: UploaderClientABC, channel_id: str, old_channel_name: str = None
) -> None:
    """insert a series of bookmarks to a channel.

    This method is not checking if the bookmarks are already inserted or not.

    Args:
        client (UploaderClientABC): uploader client. If use this via any UploaderClient Class, self is automatically set.
            Thus, ignore this.
        channel_id (str; Optional; default=None): channel id (usually 9-digits string)
        old_channel_name (str; Optional; default=None): old channel name. It required to find the stored data.
    """
    data_file_path = os.path.join(
        client.local_data_dir, "bookmarks", f"{old_channel_name}.json"
    )
    if not os.path.exists(data_file_path):
        return
    bookmarks: List[Dict] = json.load(open(data_file_path, mode="r", encoding="utf-8"))
    for bookmark in bookmarks:
        del bookmark["channel_id"]
        client.bookmarks_add(channel_id=channel_id, **bookmark)
