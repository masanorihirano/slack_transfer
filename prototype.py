import os

from slack_transfer import run

if __name__ == "__main__":
    local_data_dir = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "local_data_dir"
    )
    run(
        local_data_dir=local_data_dir,
        downloader_token="xoxb-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
        uploader_token="xoxb-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
        override=True,
    )
