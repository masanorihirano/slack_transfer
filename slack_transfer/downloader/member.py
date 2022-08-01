import json
import os
from typing import Dict
from typing import List
from typing import Optional

from slack_sdk.web import SlackResponse

from slack_transfer.commons.client import DownloaderClient


def download_members_list(client: DownloaderClient) -> List[Dict]:
    members: List[Dict] = []
    next_cursor: Optional[str] = None

    while True:
        response: SlackResponse = client.users_list(cursor=next_cursor)
        if not response["ok"]:
            raise IOError("user list cannot be fetched in downloading WS data.")
        members.extend(response["members"])

        if "response_metadata" in response:
            next_cursor = response["response_metadata"]["next_cursor"]
            if next_cursor == "":
                break
        else:
            break

    json.dump(
        members,
        open(
            os.path.join(client.local_data_dir, "members.json"),
            mode="w",
            encoding="utf-8",
        ),
        indent=4,
    )
    return members
