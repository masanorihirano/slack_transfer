import warnings
from typing import Dict
from typing import List
from typing import Optional
from typing import Union

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from slack_sdk.web import SlackResponse


def get_channels_list(client: WebClient) -> List[Dict]:
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


def get_replies(client: WebClient, channel_id: str, ts: str) -> List[Dict]:
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
        client (WebClient): client including DownloaderClient and UploaderClient
        channel_ids (Optional; str or List[str]; default=None): channel id list for calculation. If not set, calculate all accessible channels.
        auto_join (bool; default=False): when bot is not in channel, automatically join if possible (public channel).

    Yields:
        float: total file volumes (bytes)
    """
    if channel_ids is None:
        channels = get_channels_list(client=client)
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
                    warnings.warn(f"slack bot is not in `{channel_id}`. Skip this.")
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
