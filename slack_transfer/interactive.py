import json
import os.path
import ssl
import tkinter
from tkinter import filedialog
from typing import Dict
from typing import List
from typing import Tuple
from typing import TypeVar

import certifi
from prompt_toolkit import cursor_shapes
from prompt_toolkit.shortcuts import button_dialog
from prompt_toolkit.shortcuts import checkboxlist_dialog
from prompt_toolkit.shortcuts import input_dialog
from prompt_toolkit.shortcuts import message_dialog
from prompt_toolkit.shortcuts import radiolist_dialog
from prompt_toolkit.styles import Style

from slack_transfer import DownloaderClient
from slack_transfer._base import CommonNoLocalVolumeClient
from slack_transfer.run import run
from slack_transfer.version import __version__

T = TypeVar("T")
style = Style.from_dict({"dialog.body": "bg:#cccccc #000000"})


def radio_selection(
    title: str, text: str, choices_and_values: List[Tuple[str, T]]
) -> T:
    result: T = radiolist_dialog(
        title=title,
        text=text,
        values=[(y, x) for x, y in choices_and_values],
        style=style,
    ).run()
    if result is None:
        raise KeyboardInterrupt
    return result


def multiple_selection(
    title: str, text: str, choices_and_values: List[Tuple[str, T]]
) -> List[T]:

    dialog = checkboxlist_dialog(
        title=title,
        text=text,
        values=[(y, x) for x, y in choices_and_values],
        style=style,
    )
    dialog.cursor = cursor_shapes.SimpleCursorShapeConfig(
        cursor_shape=cursor_shapes.CursorShape.BLINKING_BLOCK
    )
    result: List[T] = dialog.run()
    if result is None:
        raise KeyboardInterrupt
    return result


def button_selection(
    title: str, text: str, choices_and_values: List[Tuple[str, T]]
) -> T:
    result: T = button_dialog(
        title=title, text=text, buttons=choices_and_values, style=style
    ).run()
    return result


def confirmation(title: str, text: str) -> None:
    message_dialog(title=title, text=text, style=style).run()
    return


def interactive() -> None:
    """See interactive section in :doc:`/user_guide/cli`"""
    try:
        ssl_context = ssl.create_default_context(
            ssl.Purpose.SERVER_AUTH, cafile=certifi.where(), capath=certifi.where()
        )
        confirmation(
            title="Start",
            text="In this system, all selection can be done using mouse pointer.\nこのシステムではすべての選択をマウスで行うことができます．",
        )

        language = button_selection(
            title="Select language",
            text="Please select language",
            choices_and_values=[("English", "en"), ("日本語", "ja")],
        )

        confirmation(
            title={"en": "Select folder", "ja": "フォルダー選択"}[language],
            text={
                "en": "Next, please select your folder to save and load the downloaded data. "
                + "We highly recommend making and selecting an empty folder when this is the first time.",
                "ja": "次に，このシステムで使用するフォルダーを選択してください．初めての使用であれば，空のフォルダーを作成し，選択することを強くお勧めします．",
            }[language],
        )

        tk = tkinter.Tk()
        local_data_dir = filedialog.askdirectory()
        tk.destroy()

        already_downloaded = os.path.exists(
            os.path.join(local_data_dir, "channels.json")
        ) and os.path.exists(os.path.join(local_data_dir, "members.json"))

        if already_downloaded:
            skip_download = button_selection(
                title="Download Selection",
                text={
                    "en": "Do you want to download slack data? Usually select yes. "
                    + "When you already downloaded data, you can select No.",
                    "ja": "Slackデータのダウンロードを行いますか？通常はYesを選択してください．すでにデータをダウンロード済みの場合はNoを選択しても構いません．",
                }[language],
                choices_and_values=[("Yes", False), ("No", True)],
            )
        else:
            skip_download = False

        downloader_token = None
        if not skip_download:
            downloader_token = input_dialog(
                title="Input download token",
                text={
                    "en": "Please inputs download token. How to get is: \n"
                    + "https://slack-transfer.readthedocs.io/en/stable/user_guide/run.html#downloader-token",
                    "ja": "ダウンロード用のAPI tokenを入力してください．\n詳細: "
                    + "https://slack-transfer.readthedocs.io/en/stable/user_guide/run_ja.html#downloader-token-ja",
                }[language],
            ).run()
            if downloader_token is None:
                raise KeyboardInterrupt
            client = CommonNoLocalVolumeClient(token=downloader_token, ssl=ssl_context)
            client.test_connection()
            client.test_downloader()

        if not skip_download:
            skip_upload = button_selection(
                title="Upload Selection",
                text={
                    "en": "Do you want to upload slack data? When you want to downloaded data only, you can select No.",
                    "ja": "Slackデータのアップロードを行いますか？データをダウンロードしたいだけであれば，Noを選択してください．",
                }[language],
                choices_and_values=[("Yes", False), ("No", True)],
            )
        else:
            skip_upload = False

        uploader_token = None
        if not skip_upload:
            uploader_token = input_dialog(
                title="Input upload token",
                text={
                    "en": "Please inputs upload token. How to get is: \n"
                    + "https://slack-transfer.readthedocs.io/en/stable/user_guide/run.html#uploader-token",
                    "ja": "アップロード用のAPI tokenを入力してください．\n詳細: "
                    + "https://slack-transfer.readthedocs.io/en/stable/user_guide/run_ja.html#uploader-token-ja",
                }[language],
            ).run()
            if uploader_token is None:
                raise KeyboardInterrupt
            client = CommonNoLocalVolumeClient(token=uploader_token, ssl=ssl_context)
            client.test_connection()
            client.test_uploader()

        if not skip_download:
            confirmation(
                title="Bot invitation",
                text={
                    "en": "Please invite bot to private channels if needed. After finishing, please select OK. How to do is: \n"
                    + "https://slack-transfer.readthedocs.io/en/stable/user_guide/run.html#invite-private",
                    "ja": "必要に応じて，Botをprivate channelに招待してください．完了したら，OKを押してください．\n詳細: "
                    + "https://slack-transfer.readthedocs.io/en/stable/user_guide/run_ja.html#invite-private-ja",
                }[language],
            )

        target_all_channels = button_selection(
            title="Channel Selection",
            text={
                "en": "Do you want to process all possible channels?",
                "ja": "可能な限りすべてのチャンネルを処理の対象にしますか？",
            }[language],
            choices_and_values=[("Yes", True), ("No", False)],
        )

        channel_names = None
        if not target_all_channels:
            channels: List[Dict]
            if not skip_download:
                client = CommonNoLocalVolumeClient(
                    token=downloader_token, ssl=ssl_context
                )
                channels = client.get_channels_list()
            else:
                channels = json.load(
                    open(os.path.join(local_data_dir, "channels.json"), mode="r")
                )
            channel_names = multiple_selection(
                title="Channel selection",
                text={
                    "en": "Please select targeting channels．(Private channels listed here but bot doesn't joined will be skiped.)",
                    "ja": "処理の対象にするチャンネルを選択してください．"
                    + "なお，ここに表示されているprivate channelでも，botを招待する作業を完了していないチャンネルはスキップされます．",
                }[language],
                choices_and_values=[
                    (channel["name"], channel["name"]) for channel in channels
                ],
            )

        name_mappings = None
        override = False
        if not skip_upload:
            needs_name_mappings = button_selection(
                title="Channel name mappings",
                text={
                    "en": "Do you need to name mappings of channels when uploading data to the destination WS? "
                    + "\nDetails: https://slack-transfer.readthedocs.io/en/stable/user_guide/run.html#channel-mappings",
                    "ja": "アップロード時にチャンネル名のマッピングが必要ですか？"
                    + "\n詳細: https://slack-transfer.readthedocs.io/en/stable/user_guide/run_ja.html#channel-mappings-ja",
                }[language],
                choices_and_values=[("Yes", True), ("No", False)],
            )
            if needs_name_mappings:
                _name_mappings = input_dialog(
                    title="Channel name mappings",
                    text={
                        "en": "Please inputs name mappings. Format is comma-separated colon-concatenate dictionary: "
                        + "old_channel_name1:new_channel_name1,old_channel_name2:new_channel_name2",
                        "ja": "チャンネル名のマッピングを入力してください．カンマ区切りで，コロンでマッピング前後のチャンネル名をつないでください．"
                        + "例) old_channel_name1:new_channel_name1,old_channel_name2:new_channel_name2",
                    }[language],
                ).run()
                name_mappings = dict(
                    [
                        (dict_input.split(":")[0], dict_input.split(":")[1])
                        for dict_input in _name_mappings.split(",")
                    ]
                )

            override = button_selection(
                title="Channel override",
                text={
                    "en": "Do you want to override (add more messages) in existing channels on uploading WS?",
                    "ja": "アップロード側のWSに同じ名前のチャンネルが存在する場合に，上書き(メッセージの追加)をしますか？",
                }[language],
                choices_and_values=[("Yes", True), ("No", False)],
            )

        skip_bookmarks = button_selection(
            title="Bookmark skip",
            text={
                "en": "Do you want to skip bookmark migration? Usually select No.",
                "ja": "Bookmarkのコピーをスキップしますか？通常はNoを選択してください．",
            }[language],
            choices_and_values=[("No", False), ("Yes", True)],
        )

        print_str = (
            f"All settings:\ndata directory: {local_data_dir}\nDownload: {not skip_download}\nUpload: {not skip_upload}\n"
            + f"Downloader token: {downloader_token}\nUploader token: {uploader_token}\n"
            + f"Channels: {channel_names if channel_names else 'Not specified'}\n"
            + f"Name mappings: {name_mappings}\nOverride: {override}\nSkip bookmark: {skip_bookmarks}"
        )

        final_confirmation = button_selection(
            title="Bot invitation",
            text={
                "en": f"Please check the setting: \n{print_str}",
                "ja": f"設定を確認してください: \n{print_str}",
            }[language],
            choices_and_values=[("Continue", True), ("Cancel", False)],
        )
        if not final_confirmation:
            raise KeyboardInterrupt

        if not skip_download and not skip_upload:
            downloader = DownloaderClient(
                local_data_dir=local_data_dir, token=downloader_token, ssl=ssl_context
            )
            downloader.download_emoji()
            confirmation(
                title="Emoji migration required",
                text={
                    "en": f"Emojis are downloaded in {local_data_dir}/emojis/ . \n"
                    + "If you need, please add those emojis to the destination WS **NOW**. Then, click OK.",
                    "ja": f"必要に応じて，{local_data_dir}/emojis/にダウンロードされた絵文字を移行先WSに登録してください．"
                    + "完了したら，OKを押してください．",
                }[language],
            )

        run(
            local_data_dir=local_data_dir,
            downloader_token=downloader_token,
            uploader_token=uploader_token,
            override=override,
            skip_download=skip_download,
            skip_upload=skip_upload,
            channel_names=channel_names,
            name_mappings=name_mappings,
            skip_bookmarks=skip_bookmarks,
            ssl=ssl_context,
        )
    except Exception as e:
        import traceback

        print(e)
        print(traceback.format_exc())

    print(
        "This is the end of this program. Type Enter to exit. プログラムはこれで終了です．エンターキーを押すと終了します．"
    )
    while True:
        key = input()
        if not key:
            break


if __name__ == "__main__":
    print(
        f"slack_transfer {__version__} Copyright (C) M.HIRANO\nThis program comes with ABSOLUTELY NO WARRANTY"
    )
    license_file = os.path.join(os.path.dirname(__file__), "license.json")
    if os.path.exists(license_file):
        print("\nThis program including following programs:")
        license_data = json.load(open(license_file, mode="r"))
        for porg_license in license_data:
            print(
                f"{porg_license['Name']} {porg_license['Version']} Copyright (C)  {porg_license['Author']}"
            )
    interactive()
