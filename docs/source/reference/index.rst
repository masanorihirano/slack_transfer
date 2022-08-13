.. module:: slack_transfer

* :ref:`genindex`

API reference
==================
Client
~~~~~~~~~~~~~~~~~~
.. autosummary::
    :toctree: generated/client/
    :recursive:

    DownloaderClient
    UploaderClient

ClientABC
~~~~~~~~~~~~~~~~~~
.. autosummary::
    :toctree: generated/client_abc/
    :recursive:

    _base.CommonClient
    _base.DownloaderClientABC
    _base.UploaderClientABC

functions
~~~~~~~~~~~~~~~~~~
.. autosummary::
    :toctree: generated/functions/
    :recursive:

    functions.common
    functions.common.get_channels_list
    functions.common.get_file_volumes
    functions.common.get_replies
    functions.common.test_connection
    functions.common.test_downloader
    functions.common.test_uploader
    functions.download
    functions.download.download_bookmark
    functions.download.download_channel_history
    functions.download.download_channels_list
    functions.download.download_emoji
    functions.download.download_file
    functions.download.download_members_list
    functions.upload
    functions.upload.check_channel_exists
    functions.upload.check_insert_finished
    functions.upload.check_upload_conflict
    functions.upload.create_all_channels
    functions.upload.data_insert
    functions.upload.insert_bookmarks
    functions.upload.upload_file


CLI
~~~~~~~~~~~~~~~~~~
.. autosummary::
    :toctree: generated/cli/
    :recursive:

    cli.bookmark
    cli.download
    cli.emoji
    cli.file_volume
    cli.main
    cli.token_test
    cli.upload


Others
~~~~~~~~~~~~~~~~~~
.. autosummary::
    :toctree: generated/other/
    :recursive:

    __version__
    run.run
    interactive.interactive
