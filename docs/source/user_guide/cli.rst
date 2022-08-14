CLI
==========
After pip installation, you can use :code:`slack_transfer` CLI command instead of :code:`python -m slack_transfer.cli.*`

.. code-block:: bash

   pip install slack-transfer
   slack-transfer --help


run
----------------
Run message migration. No intaractive mode. All settings are given through CLI args.

usage:
    :code:`slack_transfer run [-h] --data_dir DATA_DIR [--downloader_token DOWNLOADER_TOKEN] [--uploader_token UPLOADER_TOKEN] [--override] [--skip_download] [--skip_upload] [--name_mappings NAME_MAPPINGS] [--skip_bookmarks]`

optional arguments:
    :code:`-h, --help`
        show this help message and exit
    :code:`--data_dir DATA_DIR, -d DATA_DIR`
        Data directory for saving download data or loading upload data. This is required.
    :code:`--downloader_token DOWNLOADER_TOKEN, -td DOWNLOADER_TOKEN`
        Download token obtained from slack (the original workspace). Starts with `xoxb-`
    :code:`--uploader_token UPLOADER_TOKEN, -tu UPLOADER_TOKEN`
        Upload token obtained from slack (the destination workspace). Starts with `xoxb-`
    :code:`--override`
        This flag enables message migration to the destination workspace even when a channel already exists. This means that additional messages are inserted after the message already sent to the channel. If you want not to do so, please delete the channel on the destination workspace first.
    :code:`--skip_download`
        Skip download. This is usually used when the download is already finished.
    :code:`--skip_upload`
        Skip upload. This is usually used when only the download is necessary.
    :code:`--channel_names CHANNEL_NAMES`
        channel names you want to process. If not set, set to all available channels. Set by comma-separation for multiple inputs. For example, `general,random`
    :code:`--name_mappings NAME_MAPPINGS`
        You can set name mappings between the channel names of the original and destination workspaces. Comma-separated dictionaries (key:value) are available. For example, `old_name1:new_name1,old_name2:new_name2`.
    :code:`--skip_bookmarks`
        Skip process bookmarks.

file_volume
----------------
Check file volumes before downloading.
Return the total file size of given channels.

usage:
    :code:`slack_transfer file_volume [-h] --token TOKEN [--channel_ids CHANNEL_IDS] [--auto_join]`

optional arguments:
    :code:`-h, --help`
        show this help message and exit
    :code:`--token TOKEN`
        Token obtained from slack. Starts with `xoxb-`
    :code:`--channel_ids CHANNEL_IDS`
        channel ids you want to check the total volume of files. If not set, set to all available channels. Set by comma-separation for multiple inputs
    :code:`--auto_join`
        if bot is not in channel automatically join when this flag is used.


download
----------------
Download the specific channels or all channels as you want.

usage:
    :code:`slack_transfer download [-h] --data_dir DATA_DIR --downloader_token DOWNLOADER_TOKEN [--channel_names CHANNEL_NAMES] [--skip_bookmarks]`

optional arguments:
    :code:`-h, --help`
        show this help message and exit
    :code:`--data_dir DATA_DIR, -d DATA_DIR`
        Data directory for saving download data or loading upload data. This is required.
    :code:`--downloader_token DOWNLOADER_TOKEN, -td DOWNLOADER_TOKEN`
        Download token obtained from slack (the original workspace). Starts with `xoxb-`
    :code:`--channel_names CHANNEL_NAMES`
        channel names you want to download. If not set, set to all available channels. Set by comma-separation for multiple inputs. For example, `general,random`
    :code:`--skip_bookmarks`
        Skip process bookmarks.

uploader
----------------
Upload the specific channels or all channels as you want.

usage:
    :code:`slack_transfer upload [-h] --data_dir DATA_DIR --uploader_token UPLOADER_TOKEN [--old_channel_names OLD_CHANNEL_NAMES] [--override] [--name_mappings NAME_MAPPINGS] [--skip_bookmarks]`

optional arguments:
    :code:`-h, --help`
        show this help message and exit
    :doce:`--data_dir DATA_DIR, -d DATA_DIR`
        Data directory for saving upload data or loading upload data. This is required.
    :code:`--uploader_token UPLOADER_TOKEN, -td UPLOADER_TOKEN`
        upload token obtained from slack (the original workspace). Starts with `xoxb-`
    :code:`--old_channel_names OLD_CHANNEL_NAMES`
        channel names you want to upload. Name is selected among downloaded WS. If not set, set to all available channels. Set by comma-separation for multiple inputs. For example, `general,random`
    :code:`--override`
        This flag enables message migration to the destination workspace even when a channel already exists. This means that additional messages are inserted after the message already sent to the channel. If you want not to do so, please delete the channel on the destination workspace first.
    :code:`--name_mappings NAME_MAPPINGS`
        You can set name mappings between the channel names of the original and destination workspaces. Comma-separated dictionaries (key:value) are available. For example, `old_name1:new_name1,old_name2:new_name2`.
    :code:`--skip_bookmarks`
        Skip process bookmarks.

bookmark
----------------
Move bookmarks of the specific channels from the original WS to the destination WS.

usage:
    :code:`slack_transfer bookmark [-h] --data_dir DATA_DIR --downloader_token DOWNLOADER_TOKEN --uploader_token UPLOADER_TOKEN [--channel_names CHANNEL_NAMES] [--name_mappings NAME_MAPPINGS]`

optional arguments:
    :code:`-h, --help`
        show this help message and exit
    :code:`--data_dir DATA_DIR, -d DATA_DIR`
        Data directory for saving download data or loading upload data. This is required.
    :code:`--downloader_token DOWNLOADER_TOKEN, -td DOWNLOADER_TOKEN`
        Download token obtained from slack (the original workspace). Starts with `xoxb-`
    :code:`--uploader_token UPLOADER_TOKEN, -tu UPLOADER_TOKEN`
        upload token obtained from slack (the destination workspace). Starts with `xoxb-`
    :code:`--channel_names CHANNEL_NAMES`
        channel names you want to move bookmarks. If not set, set to all available channels. Set by comma-separation for multiple inputs. For example, `general,random`
    :code:`--name_mappings NAME_MAPPINGS`
        You can set name mappings between the channel names of the original and destination workspaces. Comma-separated dictionaries (key:value) are available. For example, `old_name1:new_name1,old_name2:new_name2`.


emoji
----------------
Download emojis specific to the workspace. Only download is available.
Thus, after downloading, you have to add them to the destination WS.

usage:
    :code:`slack_transfer emoji [-h] --data_dir DATA_DIR --downloader_token DOWNLOADER_TOKEN`

optional arguments:
    :code:`-h, --help`
        show this help message and exit
    :code:`--data_dir DATA_DIR, -d DATA_DIR`
        Data directory for saving download data or loading upload data. This is required.
    :code:`--downloader_token DOWNLOADER_TOKEN, -td DOWNLOADER_TOKEN`
        Download token obtained from slack (the original workspace). Starts with `xoxb-`


token_test
----------------
Test your token by bootstrap. It means that if the token has not enough scope, it will be pointed out step by step of each tests.

usage:
    :code:`slack_transfer token_test [-h] --token TOKEN --test_channels TEST_CHANNELS [--as_downloader] [--as_uploader]`

optional arguments:
    :code:`-h, --help`
        show this help message and exit
    :code:`--token TOKEN`
        Token obtained from slack. Starts with `xoxb-`
    :code:`--test_channels TEST_CHANNELS`
        Test channel names. Multiple channels can be set by comma-separation like `general,private`
    :code:`--as_downloader`
        for checking as downloader
    :code:`--as_uploader`
        for checking as uploader

interactive
----------------
interactive mode.

.. code-block:: bash

    $ slack_transfer　interactive

