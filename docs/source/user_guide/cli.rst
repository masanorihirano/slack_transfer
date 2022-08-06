CLI
==========
After pip installation, you can use :mod:`slack_transfer` CLI command instead of :code:`python -m slack_transfer.cli.*`

.. code-block:: bash

   pip install slack-transfer
   slack-transfer --help


run
----------------
Run message migration. No intaractive mode. All settings are given through CLI args.

usage: slack_transfer run [-h] --data_dir DATA_DIR [--downloader_token DOWNLOADER_TOKEN] [--uploader_token UPLOADER_TOKEN] [--override] [--skip_download] [--skip_upload] [--name_mappings NAME_MAPPINGS]

optional arguments:
  -h, --help            show this help message and exit
  --data_dir DATA_DIR, -d DATA_DIR
                        Data directory for saving download data or loading upload data. This is required.
  --downloader_token DOWNLOADER_TOKEN, -td DOWNLOADER_TOKEN
                        Download token obtained from slack (the original workspace). Starts with `xoxb-`
  --uploader_token UPLOADER_TOKEN, -tu UPLOADER_TOKEN
                        Upload token obtained from slack (the destination workspace). Starts with `xoxb-`
  --override            This flag enables message migration to the destination workspace even when a channel already exists. This means that additional messages are inserted after the message already sent to the channel. If you
                        want not to do so, please delete the channel on the destination workspace first.
  --skip_download       Skip download. This is usually used when the download is already finished.
  --skip_upload         Skip upload. This is usually used when only the download is necessary.
  --name_mappings NAME_MAPPINGS
                        You can set name mappings between the channel names of the original and destination workspaces. Comma-separated dictionaries (key:value) are available. For example,
                        `old_name1:new_name1,old_name2:new_name2`.


file_volume
----------------
Check file volumes before downloading.
Return the total file size of given channels.

usage: slack_transfer file_volume [-h] --token TOKEN [--channel_ids CHANNEL_IDS] [--auto_join]

optional arguments:
  -h, --help            show this help message and exit
  --token TOKEN         Token obtained from slack. Starts with `xoxb-`
  --channel_ids CHANNEL_IDS
                        channel ids you want to check the total volume of files. If not set, set to all available channels. Set by comma-separation for multiple inputs
  --auto_join           if bot is not in channel automatically join when this flag is used.

