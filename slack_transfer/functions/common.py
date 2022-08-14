import warnings
from typing import Dict
from typing import List
from typing import Optional
from typing import Union

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from slack_sdk.web import SlackResponse


def get_channels_list(client: WebClient) -> List[Dict]:
    """get channel list.

    Args:
        client (WebClient): client. If use this via any Client Class, self is automatically set. Thus, ignore this.

    Yields:
        List[Dict]: List of channel info. The details of channel info is listed: https://api.slack.com/types/channel
        (see the dictionary corresponding to channel key.)
    """
    channels: List[Dict] = []
    next_cursor: Optional[str] = None

    while True:
        response: SlackResponse = client.conversations_list(
            cursor=next_cursor, types="public_channel,private_channel"
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


def get_replies(client: WebClient, channel_id: str, ts: str) -> List[Dict]:
    """get replies to the specific message.

    Args:
        client (WebClient): client. If use this via any Client Class, self is automatically set. Thus, ignore this.
        channel_id (str): channel id (usually 9-digits string)
        ts (str): ts of the specific message. ts is a unix timestamp in the format of float. But, here, string for it is accepted.


    Yields:
        List[Dict]: List of the reply messages. The details of message is listed: https://api.slack.com/reference/messaging/payload
    """
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


def get_file_volumes(
    client: WebClient,
    channel_ids: Optional[Union[str, List[str]]] = None,
    auto_join: bool = False,
) -> float:
    """Calculate the total file volumes (bytes)

    Args:
        client (WebClient): client. If use this via any Client Class, self is automatically set. Thus, ignore this.
        channel_ids (Optional; str or List[str]; default=None): channel id list for calculation.
            If not set, calculate all accessible channels.
        auto_join (bool; default=False): when bot is not in channel, automatically join if possible (public channel).
            This feature is disabled for :class:`slack_transfer._base.CommonDryRunClient`

    Yields:
        float: total file volumes (bytes)
    """
    channels = get_channels_list(client=client)
    channel_id_name_dict = dict([(x["id"], x["name"]) for x in channels])
    if channel_ids is None:
        channel_ids = list(map(lambda x: x["id"], channels))
    elif isinstance(channel_ids, str):
        channel_ids = [channel_ids]
    else:
        channel_ids = channel_ids

    volume_dict: Dict[str, int] = {}

    for channel_id in channel_ids:
        next_cursor: Optional[str] = None
        while True:
            try:
                response: SlackResponse = client.files_list(
                    channel=channel_id, cursor=next_cursor
                )
            except SlackApiError as e:
                if e.response["error"] == "not_in_channel":
                    if auto_join:
                        try:
                            client.conversations_join(channel=channel_id)
                            continue
                        except:
                            pass
                    warnings.warn(
                        f"slack bot is not in `{channel_id_name_dict[channel_id] if channel_id in channel_id_name_dict else channel_id}`. Skip this."
                    )
                    break
                else:
                    raise e
            if not response["ok"]:
                raise IOError("channel list cannot be fetched.")
            volume_dict.update(
                dict(map(lambda x: (x["id"], x["size"]), response["files"]))
            )

            if "response_metadata" in response:
                next_cursor = response["response_metadata"]["next_cursor"]
                if next_cursor == "":
                    break
            else:
                break
    return sum(volume_dict.values())


def test_connection(client: WebClient) -> None:
    """test connections to slack.

    This test including common scope among all client.
    The token set to the client use this method requires the following scope:
     - channels:history
     - channels:join
     - channels:read
     - files:read
     - groups:history
     - groups:read

     If one of the scope is missing, this method rise an error.
     Those tests are performed step by step. It means that missing scope appears not at once.

    Args:
        client (WebClient): client. If use this via any Client Class, self is automatically set. Thus, ignore this.
    """
    response = client.auth_test()
    if not response["ok"]:
        raise IOError("slack token is invalid.")
    print(f"Successfully access to `{response['team']}`")

    # channels:read,groups:read
    try:
        response = client.conversations_list(types="public_channel,private_channel")
    except SlackApiError as e:
        if e.response["error"] == "missing_scope":
            raise AttributeError("missing scope: channels:read,groups:read")
        else:
            raise e

    channel_cand_public = list(filter(lambda x: x["is_general"], response.data["channels"]))  # type: ignore
    if len(channel_cand_public) == 0:
        raise ValueError("general type channel doesn't exist.")
    if len(channel_cand_public) != 1:
        raise AssertionError

    # channels:join
    try:
        client.conversations_join(channel=channel_cand_public[0]["id"])
    except SlackApiError as e:
        if e.response["error"] != "method_not_supported_for_channel_type":
            raise e
    # channels:history for public
    try:
        client.conversations_history(channel=channel_cand_public[0]["id"], ts="1")
    except SlackApiError as e:
        if e.response["error"] == "missing_scope":
            raise AttributeError("missing scope: channels:history")
        else:
            raise e
    # files:read
    client.files_list()

    channel_cand_private = list(filter(lambda x: x["is_private"], response.data["channels"]))  # type: ignore
    if len(channel_cand_private) == 0:
        warnings.warn("No private channel is tested")
        return
    # groups:history for private
    try:
        client.conversations_history(channel=channel_cand_private[0]["id"], ts="1")
    except SlackApiError as e:
        if e.response["error"] == "missing_scope":
            raise AttributeError("missing scope: groups:history")
        else:
            raise e


def test_downloader(client: WebClient) -> None:
    """test connections to slack as downloader.

    This test including common scope for DownloaderClient.
    The token set to the client use this method requires the following scope:
     - bookmarks:read
     - emoji:read
     - users:read

     If one of the scope is missing, this method rise an error.
     Those tests are performed step by step. It means that missing scope appears not at once.

    Args:
        client (WebClient): client. If use this via any Client Class, self is automatically set. Thus, ignore this.
    """
    client.users_list()

    # channels:read,groups:read
    response = client.conversations_list(types="public_channel,private_channel")
    channel_cand_public = list(filter(lambda x: x["is_general"], response.data["channels"]))  # type: ignore
    if len(channel_cand_public) == 0:
        raise ValueError("general type channel doesn't exist.")
    if len(channel_cand_public) != 1:
        raise AssertionError
    # bookmarks:read
    client.bookmarks_list(channel_id=channel_cand_public[0]["id"])
    # emoji:read
    client.emoji_list()
    print("test for downloader is finished!")


def test_uploader(client: WebClient) -> None:
    """test connections to slack as uploader.

    This test including common scope for UploaderClient.
    The token set to the client use this method requires the following scope:
     - channels:manage
     - files:write
     - chat:write
     - pins:write
     - bookmarks:write
     - reaction:write

     If one of the scope is missing, this method rise an error.
     Those tests are performed step by step. It means that missing scope appears not at once.

    Args:
        client (WebClient): client. If use this via any Client Class, self is automatically set. Thus, ignore this.
    """
    # channels:manage
    # conversations_setTopic and conversations_setPurpose is also the same scope
    try:
        client.conversations_create(name=":::", is_private=False)
    except SlackApiError as e:
        if e.response["error"] == "missing_scope":
            raise AttributeError("missing scope: channels:manage")
        elif e.response["error"] == "invalid_name_specials":
            pass
        else:
            raise e
    # try:
    #     client.conversations_create(name=":::", is_private=True)
    # except SlackApiError as e:
    #     if e.response["error"] == "missing_scope":
    #         raise AttributeError(f"missing scope: groups:write")
    #     elif e.response["error"] == "invalid_name_specials":
    #         pass
    #     else:
    #         raise e

    # files:write
    try:
        client.files_upload(content="aaa", channels=":::::")
    except SlackApiError as e:
        if e.response["error"] == "missing_scope":
            raise e

    # files_list is tested in test_connection

    # chat:write
    try:
        client.chat_postMessage(channel=":::::", text="test")
    except SlackApiError as e:
        if e.response["error"] == "missing_scope":
            raise AttributeError("missing scope: chat:write")

    # pins:write
    try:
        client.pins_add(channel=":::::", timestamp="1")
    except SlackApiError as e:
        if e.response["error"] == "missing_scope":
            raise e

    # bookmarks:write
    try:
        client.bookmarks_add(channel_id=":::::", title="test", type="link")
    except SlackApiError as e:
        if e.response["error"] == "missing_scope":
            raise e

    # reaction:write
    try:
        client.reactions_add(channel=":::::", name="test", timestamp="1")
    except SlackApiError as e:
        if e.response["error"] == "missing_scope":
            raise e

    print("test for uploader is finished!")
