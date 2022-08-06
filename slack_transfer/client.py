from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple
from typing import Union

import tqdm

from ._base import DownloaderClientABC
from ._base import UploaderClientABC
from .functions.download import download_channel_history
from .functions.download import download_channels_list
from .functions.download import download_file
from .functions.download import download_members_list
from .functions.upload import check_upload_conflict
from .functions.upload import create_all_channels
from .functions.upload import data_insert
from .functions.upload import upload_file


class DownloaderClient(DownloaderClientABC):
    """DownloaderClient"""

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


class UploaderClient(UploaderClientABC):
    """UploaderClient"""

    def create_all_channels(
        self, name_mappings: Optional[Dict[str, str]] = None
    ) -> None:
        return create_all_channels(client=self, name_mappings=name_mappings)

    def upload_file(
        self,
        old_file_id: str,
        file_name: str,
        channel_id: Optional[str] = None,
        title: Optional[str] = None,
        filetype: Optional[str] = None,
    ) -> Optional[Tuple[str, str]]:

        return upload_file(
            client=self,
            old_file_id=old_file_id,
            file_name=file_name,
            channel_id=channel_id,
            title=title,
            filetype=filetype,
        )

    def data_insert(
        self,
        channel_name: str,
        old_members_dict: Dict[str, str],
        old_channel_name: Optional[str] = None,
        time_zone: str = "Asia/Tokyo",
        progress: Union[bool, tqdm.tqdm] = True,
    ) -> None:
        return data_insert(
            client=self,
            channel_name=channel_name,
            old_members_dict=old_members_dict,
            old_channel_name=old_channel_name,
            time_zone=time_zone,
            progress=progress,
        )

    def check_upload_conflict(
        self, name_mappings: Optional[Dict[str, str]] = None
    ) -> List[str]:
        return check_upload_conflict(client=self, name_mappings=name_mappings)
