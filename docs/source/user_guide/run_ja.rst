slack_transfer.run の使い方
============================
:doc:`environment_ja` のステップが完了している前提で説明します．

0. 全体像と用語定義
---------------------
:mod:`slack_transfer.run` を用いることで，移行元のSlack workspaceから移行先のSlack workspaceにデータを移行することができます．

まず，ここでは以下のように用語を定義します．
 - WS: slack workspaceのことを意味します．
 - OrG: Slack OrGのことを意味します．Enterprise gridの契約をしている場合のみに適用され，多くの場合，意識する必要はありませんが，このレポジトリの特記事項などにおいてEnter prise grid配下のWSの場合の注意事項がある場合があります．
 - download側: ここでは，移行元のWSを指します．データをこのWSからdownloadすることからdownload側と呼びます．
 - upload側：ここでは，移行先のWSを指します．データをこのWSにuploadすることからupload側と呼びます．
 - 端末: :doc:`environment_ja` で環境構築

このレポジトリでは，同じWSでもdownload側とupload側を間違えてしまうと，大事故の原因なので，明示的に分離を行っており，tokenの権限なども役割に合わせて，read/writeを使い分けるなどして，事故が起きないようにします．

:mod:`slack_transfer.run` は基本的に移行作業をall-in-oneで実施します．
さまざまな対策はしているとはいえ，slackサーバーの挙動や，子のレポジトリに存在する潜在的なバグにより，一発で成功しない場合もあることは，あらかじめご承知おきください．
:mod:`slack_transfer.run` が実施する作業は以下です．

.. code-block:: none

    ┌────────────┐                ┌────────────┐              ┌────────────┐
    │download側WS│  --download->  │    端末    │  --upload->  │ Upload側WS │
    └────────────┘                └────────────┘              └────────────┘

そのため，端末に，download側WSのデータを保存するのに充分なディスク容量が必要です．
一般的に，大きい容量を必要とするものではありませんが，download側WSの添付ファイルなども端末にダウンロードするため，添付ファイルのサイズと量次第では，大きな容量を必要とする場合があります．
フリープランを使用していれば，5GBを超える場合にアップロード時に警告が出ていると思われます．
他にも，事前に容量を確認できる機能を実装する予定はあります．

1. 注意事項
---------------------
 - 移植といっても，完全な移植はできません．できる限り多くを移植できるようには努めていますが，一部Slack APIの仕様上できないものがあります．
 - メッセージの移植はAPIによる代理投稿として行われるので，タイムスタンプは移植時の物に変わります．代わりに，投稿者名の末尾にオリジナルのタイムスタンプを付与しています．
 - MITライセンスで提供されており，なんら保証はありません．
 - Channelしか移植できません．DMは移植できません．

2. slackトークンの取得(download側)
---------------------

Download側に必要になるScopeは以下です．

【Downloader/Uploader共通で必要】
 - channels:history
 - channels:join
 - channels:read
 - files:read
 - groups:history
 - groups:read

【Downloaderに必要】
 - bookmarks:read
 - users:read

3. slackトークンの取得(upload側)
---------------------

Upload側に必要になるScopeは以下です．

【Downloader/Uploader共通で必要】
 - channels:history
 - channels:join
 - channels:read
 - files:read
 - groups:history
 - groups:read

【Uploaderに必要】
 - channels:manage
 - files:write
 - chat:write
 - pins:write
 - bookmarks:write


4. チャンネル名のマッピングの検討
---------------------
generalチャンネル(あるいはそれを改称した場合も)は，特別な取扱いをされ，privateへの変更ができないだけでなく，Slack connectができません．
そのため，Upload側WSのgeneralチャンネルにデータを流し込むことには慎重になるべきです．

一般に，download側WSのgeneralチャンネルをupload側WSのgeneralチャンネルにデータ移行することはお勧めしません．

それ以外にも，すでにupload側WSにチャンネル名の重複が存在する場合には，以下の3つの選択肢があります．
 - そのままこれまでの投稿の末尾に追加する → 特に追加の作業不要
 - 一旦まっさらにして，新規で作りたい → 先にチャンネルを削除(アーカイブとして残したい場合はチャンネル名を変更してからアーカイブ)
 - 別チャンネルとして新しく作りたい → チャンネルマッピングを設定します．後述の引数で設定します．

これらの基準に基づき，マッピングを行うチャンネルを選定して，旧チャンネルに対応する新チャンネルのマッピングを決めてください．

5. Upload側WSのPrivateチャンネルにAPI botの追加
---------------------

6. :mod:`slack_transfer.run` の実行
---------------------
ここまで準備したら，いよいよデータの移行を開始します．

大体の時間の目安としては，メッセージ数をMとすると，
 - ダウンロードが 3M/100 秒 + ファイルのダウンロード時間
 - アップロードが M 秒 + ファイルのアップロード時間

くらいのオーダーで，アップロード時には特に時間がかかるとと思った方が良いです．
これは，Slack APIのlimitもありますので，CLIを使用して並列化をすることなどはあまりお勧めしません．

Mが充分に大きい場合には，作業を行う端末が長時間にわたって稼働できるときに作業をおこなうことをお勧めします．
なお，CLIを使った個別の移行も可能にする予定ですので，そちらもご検討ください．

では，実際に移行の作業に入ります．

まず，venvを使用する場合にはvenvに入ります．

Mac/Linux/WSLの場合

.. code-block:: bash

    $ . .venv/bin/activate

Windowsの場合

.. code-block:: bash

    $ . .venv\Scripts\activate

そのうえで，

.. code-block:: bash

    $ poetry run python -m slack_transfer.run --data_dir=<local_data_dir> --downloader_token=<downloader_token> --uploader_token=<uploader_token> --channel_names=<channel_names> --name_mappings=<name_mappings> [--override]

などと実行します．
それぞれのパラメータは以下の通りです．
 - :mod:`<local_data_dir>`: ダウンロードしたデータを端末内に一時保存するディレクトリです．相対ディレクトリ，絶対ディレクトリのどちらでも設定できます．存在しない場合は自動生成されます．わからなければ， :mod:`local_data_dir` などと設定してください．
 - :mod:`<downloader_token>`: 2で取得したdownload側WSのAPI tokenです． xoxb-から始まります．
 - :mod:`<uploader_token>`: 3で取得したupload側WSのAPI tokenです． xoxb-から始まります．
 - :mod:`<channel_names>`: 処理の対象にしたいチャンネル名を指定します．カンマ区切りで，Download側WSの名前で指定します．指定せず，すべてを対象にする場合は，:mod:`--channel_names=<channel_names>`を丸ごと削除します．
 - :mod:`<name_mappings>`: 4で決めたチャンネル名のマッピングを設定します．不要な場合は :mod:`\-\-name_mappings=<name_mappings>` を丸っと削除してください．なお，設定方法は :mod:`old_name1:new_name1,old_name2:new_name2` などと設定します．old_nameがdownload側，new_nameがupload側のチャンネル名で，マッピングが必要なものだけを記載すれば充分です．(そのままの名前でよい場合は設定不用意)
 - :mod:`--override`: 4で「そのままこれまでの投稿の末尾に追加する」を選択した場合には，これを付与してください．不要な場合は削除します．

それ以外の詳細な引数に関しては，
:doc:`../reference/generated/other/slack_transfer.run.run` を参照してください．

これらを総合すると，実行すべきコマンド例は以下のような形になります．

.. code-block:: bash

    $ poetry run python -m slack_transfer.run --data_dir=local_data_dir --downloader_token=xoxb-00000000000-0000000000000-xxxxxxxxxxxxxxxxxxxxxxxx --uploader_token=xoxb-0000000000000-0000000000000-xxxxxxxxxxxxxxxxxxxxxxxx --override --name_mappings=general:_general,random:_random

