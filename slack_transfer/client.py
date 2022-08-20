from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple
from typing import Union

import tqdm

from ._base import DownloaderClientABC
from ._base import UploaderClientABC
from .functions.download import download_bookmark
from .functions.download import download_channel_history
from .functions.download import download_channels_list
from .functions.download import download_emoji
from .functions.download import download_file
from .functions.download import download_members_list
from .functions.upload import check_channel_exists
from .functions.upload import check_insert_finished
from .functions.upload import check_upload_conflict
from .functions.upload import create_all_channels
from .functions.upload import data_insert
from .functions.upload import insert_bookmarks
from .functions.upload import upload_file


class DownloaderClient(DownloaderClientABC):
    """Downloader Client class.
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
        - :code:`DownloaderClient.get_channels_list`: :func:`slack_transfer.functions.common.get_channels_list`
        - :code:`DownloaderClient.get_replies`: :func:`slack_transfer.functions.common.get_replies`
        - :code:`DownloaderClient.get_file_volumes`: :func:`slack_transfer.functions.common.get_file_volumes`
        - :code:`DownloaderClient.test_connection`: :func:`slack_transfer.functions.common.test_connection`
        - :code:`DownloaderClient.test_downloader`: :func:`slack_transfer.functions.common.test_downloader`
        - :code:`DownloaderClient.test_uploader`: :func:`slack_transfer.functions.common.test_uploader`
        - :code:`DownloaderClient.download_channels_list`: :func:`slack_transfer.functions.download.download_channels_list`
        - :code:`DownloaderClient.download_file`: :func:`slack_transfer.functions.download.download_file`
        - :code:`DownloaderClient.download_channel_history`: :func:`slack_transfer.functions.download.download_channel_history`
        - :code:`DownloaderClient.download_members_list`: :func:`slack_transfer.functions.download.download_members_list`
        - :code:`DownloaderClient.download_bookmark`: :func:`slack_transfer.functions.download.download_bookmark`
        - :code:`DownloaderClient.download_emoji`: :func:`slack_transfer.functions.download.download_emoji`
    """

    def download_channels_list(self) -> List[Dict]:
        return download_channels_list(client=self)

    def download_file(self, file_id: str, file_name: str, url_private: str) -> None:
        return download_file(
            client=self, file_id=file_id, file_name=file_name, url_private=url_private
        )

    def download_channel_history(
        self,
        channel_id: str,
        channel_name: str,
        latest: Optional[str] = None,
        ts_progress_bar: Optional[tqdm.tqdm] = None,
        ts_now: Optional[int] = None,
        auto_join: bool = True,
    ) -> None:
        return download_channel_history(
            client=self,
            channel_id=channel_id,
            channel_name=channel_name,
            latest=latest,
            ts_progress_bar=ts_progress_bar,
            ts_now=ts_now,
            auto_join=auto_join,
        )

    def download_members_list(self) -> List[Dict]:
        return download_members_list(client=self)

    def download_bookmark(
        self, channel_id: str, channel_name: str, auto_join: bool = True
    ) -> None:
        return download_bookmark(
            client=self,
            channel_id=channel_id,
            channel_name=channel_name,
            auto_join=auto_join,
        )

    def download_emoji(self) -> None:
        return download_emoji(client=self)


class UploaderClient(UploaderClientABC):
    """Uploader Client class.
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
        - :code:`DownloaderClient.get_channels_list`: :func:`slack_transfer.functions.common.get_channels_list`
        - :code:`DownloaderClient.get_replies`: :func:`slack_transfer.functions.common.get_replies`
        - :code:`DownloaderClient.get_file_volumes`: :func:`slack_transfer.functions.common.get_file_volumes`
        - :code:`DownloaderClient.test_connection`: :func:`slack_transfer.functions.common.test_connection`
        - :code:`DownloaderClient.test_downloader`: :func:`slack_transfer.functions.common.test_downloader`
        - :code:`DownloaderClient.test_uploader`: :func:`slack_transfer.functions.common.test_uploader`
        - :code:`DownloaderClient.create_all_channels`: :func:`slack_transfer.functions.upload.create_all_channels`
        - :code:`DownloaderClient.upload_file`: :func:`slack_transfer.functions.upload.upload_file`
        - :code:`DownloaderClient.data_insert`: :func:`slack_transfer.functions.upload.data_insert`
        - :code:`DownloaderClient.check_upload_conflict`: :func:`slack_transfer.functions.upload.check_upload_conflict`
        - :code:`DownloaderClient.insert_bookmarks`: :func:`slack_transfer.functions.upload.insert_bookmarks`
        - :code:`DownloaderClient.check_insert_finished`: :func:`slack_transfer.functions.upload.check_insert_finished`
        - :code:`DownloaderClient.check_channel_exists`: :func:`slack_transfer.functions.upload.check_channel_exists`
    """

    def create_all_channels(
        self,
        channel_names: Optional[List[str]] = None,
        name_mappings: Optional[Dict[str, str]] = None,
    ) -> None:
        return create_all_channels(
            client=self, channel_names=channel_names, name_mappings=name_mappings
        )

    def upload_file(
        self,
        old_file_id: str,
        file_name: str,
        channel_id: Optional[str] = None,
        title: Optional[str] = None,
        filetype: Optional[str] = None,
        thread_ts: Optional[str] = None,
    ) -> Optional[Tuple[str, str]]:

        return upload_file(
            client=self,
            old_file_id=old_file_id,
            file_name=file_name,
            channel_id=channel_id,
            title=title,
            filetype=filetype,
            thread_ts=thread_ts,
        )

    def data_insert(
        self,
        channel_name: str,
        old_members_dict: Dict[str, str],
        old_members_icon_url_dict: Optional[Dict[str, str]] = None,
        old_channel_name: Optional[str] = None,
        time_zone: str = "Asia/Tokyo",
        progress: Union[bool, tqdm.tqdm] = True,
    ) -> str:
        return data_insert(
            client=self,
            channel_name=channel_name,
            old_members_dict=old_members_dict,
            old_members_icon_url_dict=old_members_icon_url_dict,
            old_channel_name=old_channel_name,
            time_zone=time_zone,
            progress=progress,
        )

    def check_upload_conflict(
        self, name_mappings: Optional[Dict[str, str]] = None
    ) -> List[str]:
        return check_upload_conflict(client=self, name_mappings=name_mappings)

    def insert_bookmarks(self, channel_id: str, old_channel_name: str = None) -> None:
        return insert_bookmarks(
            client=self, channel_id=channel_id, old_channel_name=old_channel_name
        )

    def check_insert_finished(
        self,
        channel_name: str,
        old_members_dict: Dict[str, str],
        old_channel_name: Optional[str] = None,
        time_zone: str = "Asia/Tokyo",
    ) -> bool:
        return check_insert_finished(
            client=self,
            channel_name=channel_name,
            old_members_dict=old_members_dict,
            old_channel_name=old_channel_name,
            time_zone=time_zone,
        )

    def check_channel_exists(self, channel_name: str) -> bool:
        return check_channel_exists(client=self, channel_name=channel_name)
