import logging
import os
from ssl import SSLContext
from typing import Dict
from typing import List
from typing import Optional
from typing import Union

from slack_sdk import WebClient
from slack_sdk.http_retry import RetryHandler

from .functions.common import get_channels_list
from .functions.common import get_file_volumes
from .functions.common import get_replies
from .functions.common import test_connection
from .functions.common import test_downloader
from .functions.common import test_uploader


class CommonDryRunClient(WebClient):
    """This class is generated to run dry-run operation.
    Inherit :code:`slack_sdk.WebClient`.

    .. seealso::
        - https://github.com/slackapi/python-slack-sdk

    Args:
        token (str; Optional): A string specifying an `xoxp-*` or `xoxb-*` token.
        base_url (str; Optional): A string representing the Slack API base URL.
            Default is `'https://www.slack.com/api/'`
        timeout (int; Optional): The maximum number of seconds the client will wait
            to connect and receive a response from Slack.
            Default is 30 seconds.
        ssl (SSLContext; Optional): An [`ssl.SSLContext`][1] instance, helpful for specifying
            your own custom certificate chain.
        proxy (str; Optional): String representing a fully-qualified URL to a proxy through
            which to route all requests to the Slack API. Even if this parameter
            is not specified, if any of the following environment variables are
            present, they will be loaded into this parameter: `HTTPS_PROXY`,
            `https_proxy`, `HTTP_PROXY` or `http_proxy`.
        headers (dict; Optional): Additional request headers to attach to all requests.

    .. seealso::
        - :code:`CommonDryRunClient.get_channels_list`: :func:`slack_transfer.functions.common.get_channels_list`
        - :code:`CommonDryRunClient.get_replies`: :func:`slack_transfer.functions.common.get_replies`
        - :code:`CommonDryRunClient.get_file_volumes`: :func:`slack_transfer.functions.common.get_file_volumes`
    """

    def get_channels_list(self) -> List[Dict]:
        """get channel list :func:`slack_transfer.functions.common.get_channels_list`"""
        return get_channels_list(client=self)

    def get_replies(self, channel_id: str, ts: str) -> List[Dict]:
        """get replies for a message :func:`slack_transfer.functions.common.get_replies`"""
        return get_replies(client=self, channel_id=channel_id, ts=ts)

    def get_file_volumes(
        self, channel_ids: Optional[Union[str, List[str]]] = None
    ) -> float:
        """calculate rough volume for files which will be downloaded (Dry-run mode) :func:`slack_transfer.functions.common.get_file_volumes`"""
        return get_file_volumes(client=self, channel_ids=channel_ids, auto_join=False)


class CommonNoLocalVolumeClient(CommonDryRunClient):
    """This class is generated to run without local volume. (Some small modification can be caused on WS.)
    Inherit :code:`slack_sdk.WebClient` via :func:`slack_transfer._base.CommonDryRunClient`

    .. seealso::
        - https://github.com/slackapi/python-slack-sdk

    Args:
        token (str; Optional): A string specifying an `xoxp-*` or `xoxb-*` token.
        base_url (str; Optional): A string representing the Slack API base URL.
            Default is `'https://www.slack.com/api/'`
        timeout (int; Optional): The maximum number of seconds the client will wait
            to connect and receive a response from Slack.
            Default is 30 seconds.
        ssl (SSLContext; Optional): An [`ssl.SSLContext`][1] instance, helpful for specifying
            your own custom certificate chain.
        proxy (str; Optional): String representing a fully-qualified URL to a proxy through
            which to route all requests to the Slack API. Even if this parameter
            is not specified, if any of the following environment variables are
            present, they will be loaded into this parameter: `HTTPS_PROXY`,
            `https_proxy`, `HTTP_PROXY` or `http_proxy`.
        headers (dict; Optional): Additional request headers to attach to all requests.

    .. seealso::
        - :code:`CommonNoLocalVolumeClient.get_channels_list`: :func:`slack_transfer.functions.common.get_channels_list`
        - :code:`CommonNoLocalVolumeClient.get_replies`: :func:`slack_transfer.functions.common.get_replies`
        - :code:`CommonNoLocalVolumeClient.get_file_volumes`: :func:`slack_transfer.functions.common.get_file_volumes`
        - :code:`CommonNoLocalVolumeClient.test_connection`: :func:`slack_transfer.functions.common.test_connection`
        - :code:`CommonNoLocalVolumeClient.test_downloader`: :func:`slack_transfer.functions.common.test_downloader`
        - :code:`CommonNoLocalVolumeClient.test_uploader`: :func:`slack_transfer.functions.common.test_uploader`
    """

    def get_file_volumes(
        self,
        channel_ids: Optional[Union[str, List[str]]] = None,
        auto_join: bool = False,
    ) -> float:
        """calculate rough volume for files which will be downloaded :func:`slack_transfer.functions.common.get_file_volumes`"""
        return get_file_volumes(
            client=self, channel_ids=channel_ids, auto_join=auto_join
        )

    def test_connection(self) -> None:
        """test general connection to slack using token :func:`slack_transfer.functions.common.test_connection`"""
        return test_connection(client=self)

    def test_downloader(self) -> None:
        """test the token as downloader mode :func:`slack_transfer.functions.common.test_downloader`"""
        return test_downloader(client=self)

    def test_uploader(self) -> None:
        """test the token as uploader mode :func:`slack_transfer.functions.common.test_uploader`"""
        return test_uploader(client=self)


class CommonClient(CommonNoLocalVolumeClient):
    """Common class among normal clients.
    Inherit :code:`slack_sdk.WebClient` via some classes.

    .. seealso::
        - https://github.com/slackapi/python-slack-sdk

    Args:
        local_data_dir (str): A directory you want to save and load your slack data.
        token (str; Optional): A string specifying an `xoxp-*` or `xoxb-*` token.
        base_url (str; Optional): A string representing the Slack API base URL.
            Default is `'https://www.slack.com/api/'`
        timeout (int; Optional): The maximum number of seconds the client will wait
            to connect and receive a response from Slack.
            Default is 30 seconds.
        ssl (SSLContext; Optional): An [`ssl.SSLContext`][1] instance, helpful for specifying
            your own custom certificate chain.
        proxy (str; Optional): String representing a fully-qualified URL to a proxy through
            which to route all requests to the Slack API. Even if this parameter
            is not specified, if any of the following environment variables are
            present, they will be loaded into this parameter: `HTTPS_PROXY`,
            `https_proxy`, `HTTP_PROXY` or `http_proxy`.
        headers (dict; Optional): Additional request headers to attach to all requests.

    .. seealso::
        - :code:`CommonClient.get_channels_list`: :func:`slack_transfer.functions.common.get_channels_list`
        - :code:`CommonClient.get_replies`: :func:`slack_transfer.functions.common.get_replies`
        - :code:`CommonClient.get_file_volumes`: :func:`slack_transfer.functions.common.get_file_volumes`
        - :code:`CommonClient.test_connection`: :func:`slack_transfer.functions.common.test_connection`
        - :code:`CommonClient.test_downloader`: :func:`slack_transfer.functions.common.test_downloader`
        - :code:`CommonClient.test_uploader`: :func:`slack_transfer.functions.common.test_uploader`
    """

    BASE_URL = "https://www.slack.com/api/"
    TYPE = "bot"

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
        if token is not None and self.TYPE == "bot" and not token.startswith("xoxb-"):
            raise ValueError("token have to be start with xoxb-")
        if token is not None and self.TYPE == "user" and not token.startswith("xoxp-"):
            raise ValueError("token have to be start with xoxp-")
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
        os.makedirs(os.path.join(self.local_data_dir, "bookmarks"), exist_ok=True)
        os.makedirs(os.path.join(self.local_data_dir, "emojis"), exist_ok=True)


class UploaderClientABC(CommonClient):
    """Abstract class for Uploader Clients. This is the same as :class:`slack_transfer._base.CommonClient`.
    But, this is introduced for easily identify the client is uploader."""

    pass


class DownloaderClientABC(CommonClient):
    """Abstract class for Downloader Clients. This is the same as :class:`slack_transfer._base.CommonClient`.
    But, this is introduced for easily identify the client is downloader."""

    pass
