import logging
import os
from ssl import SSLContext
from typing import Dict
from typing import List
from typing import Optional

from slack_sdk import WebClient
from slack_sdk.http_retry import RetryHandler

from .functions.common import get_channels_list
from .functions.common import get_replies


class CommonClient(WebClient):
    BASE_URL = "https://www.slack.com/api/"

    def __init__(
        self,
        local_data_dir: str,
        token: Optional[str] = None,
        base_url: str = BASE_URL,
        timeout: int = 30,
        ssl: Optional[SSLContext] = None,
        proxy: Optional[str] = None,
        headers: Optional[dict] = None,
        user_agent_prefix: Optional[str] = None,
        user_agent_suffix: Optional[str] = None,
        team_id: Optional[str] = None,
        logger: Optional[logging.Logger] = None,
        retry_handlers: Optional[List[RetryHandler]] = None,
    ):
        super().__init__(
            token=token,
            base_url=base_url,
            timeout=timeout,
            ssl=ssl,
            proxy=proxy,
            headers=headers,
            user_agent_prefix=user_agent_prefix,
            user_agent_suffix=user_agent_suffix,
            team_id=team_id,
            logger=logger,
            retry_handlers=retry_handlers,
        )
        self.local_data_dir: str = local_data_dir
        os.makedirs(os.path.join(self.local_data_dir, "files"), exist_ok=True)
        os.makedirs(os.path.join(self.local_data_dir, "channels"), exist_ok=True)

    def get_channels_list(self) -> List[Dict]:
        return get_channels_list(client=self)

    def get_replies(self, channel_id: str, ts: str) -> List[Dict]:
        return get_replies(client=self, channel_id=channel_id, ts=ts)


class UploaderClientABC(CommonClient):
    pass


class DownloaderClientABC(CommonClient):
    pass
