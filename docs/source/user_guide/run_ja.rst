slack_transfer の使い方
============================
:doc:`environment_ja` のステップが完了している前提で説明します．

.. seealso::
    Google Colabで稼働可能なnotebookも例示しています:

    .. image:: https://colab.research.google.com/assets/colab-badge.svg
        :alt: Open In Colab
        :target: https://colab.research.google.com/github/masanorihirano/slack_transfer/blob/main/examples/slack_transfer.ipynb


0. 全体像と用語定義
---------------------
:code:`slack_transfer` を用いることで，移行元のSlack workspaceから移行先のSlack workspaceにデータを移行することができます．

なお，Slack trialがまだ使える状態で残っていれば，一時的に有効にすることで，過去のデータをすべて回収できます．

まず，ここでは以下のように用語を定義します．
 - WS: slack workspaceのことを意味します．
 - OrG: Slack OrGのことを意味します．Enterprise gridの契約をしている場合のみに適用され，多くの場合，意識する必要はありませんが，このレポジトリの特記事項などにおいてEnter prise grid配下のWSの場合の注意事項がある場合があります．
 - download側: ここでは，移行元のWSを指します．データをこのWSからdownloadすることからdownload側と呼びます．
 - upload側：ここでは，移行先のWSを指します．データをこのWSにuploadすることからupload側と呼びます．
 - 端末: :doc:`environment_ja` で環境構築

このレポジトリでは，同じWSでもdownload側とupload側を間違えてしまうと，大事故の原因なので，明示的に分離を行っており，tokenの権限なども役割に合わせて，read/writeを使い分けるなどして，事故が起きないようにします．

:code:`slack_transfer` は基本的に移行作業をall-in-oneで実施します．
さまざまな対策はしているとはいえ，slackサーバーの挙動や，子のレポジトリに存在する潜在的なバグにより，一発で成功しない場合もあることは，あらかじめご承知おきください．
:code:`slack_transfer` が実施する作業は以下です．

.. code-block:: none

    ┌────────────┐                ┌────────────┐              ┌────────────┐
    │download側WS│  --download->  │    端末    │  --upload->  │ Upload側WS │
    └────────────┘                └────────────┘              └────────────┘

そのため，端末に，download側WSのデータを保存するのに充分なディスク容量が必要です．
一般的に，大きい容量を必要とするものではありませんが，download側WSの添付ファイルなども端末にダウンロードするため，添付ファイルのサイズと量次第では，大きな容量を必要とする場合があります．
フリープランを使用していれば，5GBを超える場合にアップロード時に警告が出ていると思われます．
どうしても必要な容量を確認したい場合は，:doc:`./cli` のfile_volumeのCLIを使用して，概算してください．

なお，このユーザーガイドでは，download側WSとUpload側WSの双方で管理者に相当する権限があるという前提を想定していますが，そうでない場合でも使用できる場合はあると思われます．

1. 注意事項
---------------------
 - 移植といっても，完全な移植はできません．できる限り多くを移植できるようには努めていますが，一部Slack APIの仕様上できないものがあります．現時点で対応していないものは以下です．
    - Slack connectの移植 (Slack connectは，connect元につなぎなおしを依頼してください)
    - Bookmarkの移植におけるフォルダー分けの維持 (Slack APIの設計上不可能)
    - Slack postを移植した場合に，フォーマット崩れする可能性があることと，readonlyで移植される (Slack　APIの設計上不可能)
    - reactionはAPIによるリアクションとして，各1種類につき1回分までしか移植されません (APIではbotがreactionのemojiを押すことしかできないので，)
    - 3000文字を越える投稿におけるフォーマット崩れの可能性 (APIの制限のため，分割投稿となるから．)
    - emojiのアップロード (APIの制限のため，ダウンロードはできますが，アップロードはできません．)
    - markdownを含めた複数のメディアやパネル等のテキスト以外の物が含まれている場合に，横幅が50%に抑えられてしまう (APIの制限によるものです)
    - 添付ファイルは，1ファイルごとの個別の投稿として投稿されたのちに，元の投稿と同じフォーマッティングの投稿が行われます．つまり，Nファイル添付していた場合には，N個の個別のファイル共有と，1個のもとの投稿のコピーとなります．(Slack APIの実装にないためです．)
    - 数MB以上のファイルについては，Slack APIのバグにより，アップロードできない可能性があります．特にOrG配下のWSではその閾値が10MB以上であることが多く，一般のWSでは，200MB程度でも機能する場合があります．また，そのリトライや，回避策を自動的に試す関係で，ファイルのアップロード処理にきわめて時間がかかる場合があります．
 - mentionなどのユーザーネームは移植しません．これは，ユーザーの対応を指定する作業が煩雑であるだけではなく，Slack connectで一度Download側とUploader側WS間をconnectすると，ユーザー情報が自動的に取り込まれ，反映されるためです．
 - メッセージの移植はAPIによる代理投稿として行われるので，タイムスタンプは移植時の物に変わります．代わりに，投稿者名の末尾にオリジナルのタイムスタンプを付与しています．
 - MITライセンスで提供されており，なんら保証はありません． (ビルドされたバイナリ版だけはGPL3.0ライセンスです．)
 - Channelしか移植できません．DMは移植できません．

なお，このツールは，できる限り，破壊的操作を行わないように設計されています．

Download側WSで実施されうる変更：
 - このツールで使用するSlack botがすべてのPublic channelに意図せず自ら自動参加をする
    - token_test時には，general相当のデフォルトチャンネルに自動で自ら参加します．

Download側でユーザーが行わなければいけない作業:
 - このツールを用いて移植したいprivate channelにたいして，このツールで使用するbotを追加する

Upload側WSで実施される変更：
 - チャンネルの作成を含む，ファイルアップロード，bookmarkの追加，メッセージの投稿，ピンの作成などの新規追加作業
 - :code:`--override` フラグを使用した場合に，既存のチャンネルに対して，ファイルやbookmark，メッセージの追加，チャンネルの説明と目的の変更，pinの追加など．

Upload側でユーザーが行わなければいけない作業(=このツールが実施しないこと):
 - 不要チャンネルの削除
 - データ移行に失敗した場合に，再度実施する際のチャンネルを削除する操作 (:code:`--override` フラグを使う選択肢もありますが，二重にデータが入り得ります)
 - 移行完了後に，public channelから希望に応じてprivate channelに変える操作
 - 希望に応じて他人をチャンネルに追加する操作

なお，本番環境への移行の前に，一旦テスト用のWSを作成し，正常に移行できることを確認してから，本番環境への移行をおこなうことをお勧めします．
不具合等があれば，githubのissue ( https://github.com/masanorihirano/slack_transfer/issues )を立てることもできますが，サポートやbug fixは保証していません．
なお，記入の際にはトークン情報など，confidentialな情報を書き込まないように注意してください．

.. _downloader_token_ja:

2. slackトークンの取得(download側)
---------------------
まず， https://api.slack.com/apps/ に進みます．

.. image:: assets/create-app-dl-01.png

「Create New App」をクリックします．

.. image:: assets/create-app-dl-02.png
    :scale: 70%

ここで，どちらを選択してもかまわないのですが，「From an app manifest」を選択すると，一気に設定を負えることができるので，お勧めです．

選択肢A: 「From an app manifest」を選んだ場合
~~~~~~~~~~~~~~~~~~~~~

.. image:: assets/create-app-dl-a-03.png
    :scale: 70%

Select a workspaceからDownload側のワークスペースを選択します．

.. image:: assets/create-app-dl-a-04.png
    :scale: 70%

次に進みます．

.. image:: assets/create-app-dl-a-05.png
    :scale: 70%

このような画面がでてくるので，タブはYAMLのままで，中のコードを削除します．
そのうえで， `こちらのリンク <../_static/downloader.yml>`_ の内容をコピペします．

.. image:: assets/create-app-dl-a-06.png
    :scale: 70%

これで次へ進みます．

.. image:: assets/create-app-dl-a-07.png
    :scale: 70%

レビューを要求されるので， :ref:`scope_dl_ja` も参考にしながら確認をします．

.. image:: assets/create-app-dl-a-08.png

「Install to Workspace」をクリックします．

.. image:: assets/create-app-dl-a-09.png
    :scale: 70%

許可を要求されるので許可します．(Allow)

.. image:: assets/create-app-dl-a-10.png

画面が戻るので，「OAuth & Permissions」をクリックします．

.. image:: assets/create-app-dl-a-11.png

「Bot User OAuth Token」が今回欲しいTokenです．「xoxb-」からはじまることを確認してください．

選択肢B: 「From scratch」を選択した場合
~~~~~~~~~~~~~~~~~~~~~

.. image:: assets/create-app-dl-a-03.png
    :scale: 70%

APIの名前と，ワークスペースの選択を求められますので，入力します．

.. image:: assets/create-app-dl-a-04.png
    :scale: 70%

入力後，次に進みます．

.. image:: assets/create-app-dl-a-10.png

画面が戻るので，「OAuth & Permissions」をクリックします．

.. image:: assets/create-app-dl-b-06.png

「Bot Token Scopes」まで下に進み，:ref:`scope_dl_ja` のリストにあるスコープを「Add permission by Scope or API method...」のところで選択し，「Add an OAuth Scope」を押して，追加していきます．
全部完了したら，上の方にある，「Install to Workspace」のボタンが押せるようになるので，クリックします．

.. image:: assets/create-app-dl-a-08.png

「Install to Workspace」をクリックします．

.. image:: assets/create-app-dl-a-09.png
    :scale: 70%

許可を要求されるので許可します．(Allow)

.. image:: assets/create-app-dl-a-10.png

画面が戻るので，「OAuth & Permissions」をクリックします．

.. image:: assets/create-app-dl-a-11.png

「Bot User OAuth Token」が今回欲しいTokenです．「xoxb-」からはじまることを確認してください．


.. _scope_dl_ja:

Download側に必要なScope
~~~~~~~~~~~~~~~~~~~~~
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
 - emoji:read
 - users:read

.. _uploader_token_ja:

3. slackトークンの取得(upload側)
---------------------
基本的に前項と同じ操作をUpload側WSでも行います．

API名はUploader APIなどとわかりやすいようにしましょう．また，インストール先のWSを間違えないように気を付けてください．

manifestファイルを用いて作成する場合は `uploader用のyml <../_static/uploader.yml>`_ の内容をコピペします．

なお，Upload側に必要になるScopeは以下です．

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
 - chat:write.customize
 - pins:write
 - bookmarks:write
 - reaction:write

.. _invite_private_ja:

4. Download側WSのPrivateチャンネルにAPI botの追加
---------------------
デフォルトでは，APIはprivate channelを読み込むことができないので，ユーザーのinviteに相当する作業を行います．
Public channelに関しては，招待なくとも自分で参加することができるのが一般なので，操作は不要です．

.. image:: assets/add-api-to-private-01.png
    :scale: 100%

Slackの左側のパネルから，Add Appsを選択します．(出てこない場合は，2のステップに失敗しています．)

.. image:: assets/add-api-to-private-02.png
    :scale: 70%

続いて，出てくるアプリのリストの中からDownloader API(2で作成)を選びます．

.. image:: assets/add-api-to-private-03.png
    :scale: 70%

すると，チャットのような画面が出てくるので，ユーザー名の下矢印を開いて，メニューを開きます．

.. image:: assets/add-api-to-private-04.png
    :scale: 70%

メニューになかに，「Add this app to a channel」を選択します．

.. image:: assets/add-api-to-private-05.png
    :scale: 70%

すると，チャンネルリストを選べる画面が出てくるので，目的のチャンネルを選択します．
ここでは，Public channelしか出ていませんが，自分が参加しているprivate channelであれば，選択することができます．
Public channelは特に作業せずとも，APIが自動的にjoinして作業を行うことはできるので，わざわざ追加する必要はありません．

.. _channel_mappings_ja:

5. チャンネル名のマッピングの検討
---------------------
generalチャンネル(あるいはそれを改称した場合も)は，特別な取扱いをされ，privateへの変更ができないだけでなく，Slack connectができません．
そのため，Upload側WSのgeneralチャンネルにデータを流し込むことには慎重になるべきです．

一般に，download側WSのgeneralチャンネルをupload側WSのgeneralチャンネルにデータ移行することはお勧めしません．

それ以外にも，すでにupload側WSにチャンネル名の重複が存在する場合には，以下の3つの選択肢があります．
 - そのままこれまでの投稿の末尾に追加する → 特に追加の作業不要 (:code:`--override` フラグを使用します)
 - 一旦まっさらにして，新規で作りたい → 先にチャンネルを削除(アーカイブとして残したい場合はチャンネル名を変更してからアーカイブ)
 - 別チャンネルとして新しく作りたい → チャンネルマッピングを設定します．後述の引数で設定します．

これらの基準に基づき，マッピングを行うチャンネルを選定して，旧チャンネルに対応する新チャンネルのマッピングを決めてください．

.. _migrate_emojis_ja:

6. emojiの移行
---------------------
emojiの移行を実施します．
emojiを先に移行しないと，後述の手順で，reactionの一部移設ができません．

管理者画面またはスタンプを押す場所でadd emojiから手動で登録することになりますが，画像の元データがない場合は，先にツールを使ってダウンロードできます．

7-2で後述するinteractive modeの場合は，自動で案内が出るので，スキップ可能です．

emojiは指定したディレクトリのemojisフォルダー内にダウンロードされます．必要に応じて，Uploader側の管理画面からアップロードして追加してください．

7-1で述べるCLIで絵文字をダウンロードする方法は以下です．

まずはpython環境に入ります．
Mac/Linux/WSLの場合

.. code-block:: bash

    $ . .venv/bin/activate

Windowsの場合

.. code-block:: bash

    $ . .venv\Scripts\activate


そのうえで，

.. code-block:: bash

    $ slack_transfer emoji --data_dir <local_data_dir> --downloader_token <downloader_token>

として実施します．
ここで，各パラメータは以下の通りです．
 - :code:`<local_data_dir>`: ダウンロードしたデータを端末内に一時保存するディレクトリです．相対ディレクトリ，絶対ディレクトリのどちらでも設定できます．存在しない場合は自動生成されます．わからなければ， :code:`local_data_dir` などと設定してください．
 - :code:`<downloader_token>`: 2で取得したdownload側WSのAPI tokenです． xoxb-から始まります．

:code:`<local_data_dir>/emojis`のフォルダーに絵文字が保存されるので，これを移行します．基本的には，そのままインポートすればemojiの名前も元の通りインポートできます．

絵文字を移行するツールが存在します( https://github.com/smashwilson/slack-emojinator )が，適切に移行できる保証がないうえ，非公開APIを使用しているため，ここでは推奨しません．

また，OrG配下のWSにおいては，絵文字がOrG内全WS共通であることから，emojiがコンフリクトする場合があったり，アップロードが不適切な場合もありますので，ご注意ください．

7. データ移行の実行
---------------------
ここまで準備したら，いよいよデータの移行を開始します．

大体の時間の目安としては，メッセージ数をMとすると，
 - ダウンロードが 3M/100 秒 + ファイルのダウンロード時間
 - アップロードが M 秒 + ファイルのアップロード時間

くらいのオーダーで，アップロード時には特に時間がかかるとと思った方が良いです．
これは，Slack APIのlimitもありますので，CLIを使用して並列化をすることなどはあまりお勧めしません．

Mが充分に大きい場合には，作業を行う端末が長時間にわたって稼働できるときに作業をおこなうことをお勧めします．
なお，CLIを使った個別の移行も可能ですので，そちらもご検討ください．

では，実際に移行の作業に入ります．

まず，venvを使用する場合にはvenvに入ります．

Mac/Linux/WSLの場合

.. code-block:: bash

    $ . .venv/bin/activate

Windowsの場合

.. code-block:: bash

    $ . .venv\Scripts\activate

なお以降の操作は2パターンあります．
 1. runコマンドを使用して，すべての設定をCLIから流し込む方法
 2. interactiveコマンドを使用して，すべて画面操作で設定を進める方法

どちらでも構いませんが2は環境によってはまれに動かない場合があるので，その場合は，1を選んでください．

7-1. runコマンドを使用して，すべての設定をCLIから流し込む方法
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    $ slack_transfer　run --data_dir=<local_data_dir> --downloader_token=<downloader_token> --uploader_token=<uploader_token> --channel_names=<channel_names> --name_mappings=<name_mappings> [--override] [--skip_bookmarks]

などと実行します．
:code:`slack_transfer` が実行できない場合には，代わりに :code:`python -m slack_transfer.run` を使用することもできます．

それぞれのパラメータは以下の通りです．
 - :code:`<local_data_dir>`: ダウンロードしたデータを端末内に一時保存するディレクトリです．相対ディレクトリ，絶対ディレクトリのどちらでも設定できます．存在しない場合は自動生成されます．わからなければ， :code:`local_data_dir` などと設定してください．
 - :code:`<downloader_token>`: 2で取得したdownload側WSのAPI tokenです． xoxb-から始まります．
 - :code:`<uploader_token>`: 3で取得したupload側WSのAPI tokenです． xoxb-から始まります．
 - :code:`<channel_names>`: 処理の対象にしたいチャンネル名を指定します．カンマ区切りで，Download側WSの名前で指定します．指定せず，すべてを対象にする場合は，:code:`--channel_names=<channel_names>`を丸ごと削除します．
 - :code:`<name_mappings>`: 4で決めたチャンネル名のマッピングを設定します．不要な場合は :code:`\-\-name_mappings=<name_mappings>` を丸っと削除してください．なお，設定方法は :code:`old_name1:new_name1,old_name2:new_name2` などと設定します．old_nameがdownload側，new_nameがupload側のチャンネル名で，マッピングが必要なものだけを記載すれば充分です．(そのままの名前でよい場合は設定不用意)
 - :code:`--override`: 4で「そのままこれまでの投稿の末尾に追加する」を選択した場合には，これを付与してください．不要な場合は削除します．
 - :code:`--skip_bookmarks`: bookmarkの移植を行わない場合に使用するフラグです．bookmarkも移植する場合は削除します．

それ以外の詳細な引数に関しては，
:doc:`../reference/generated/other/slack_transfer.run.run` を参照してください．

これらを総合すると，実行すべきコマンド例は以下のような形になります．

.. code-block:: bash

    $ slack_transfer　run --data_dir=local_data_dir --downloader_token=xoxb-00000000000-0000000000000-xxxxxxxxxxxxxxxxxxxxxxxx --uploader_token=xoxb-0000000000000-0000000000000-xxxxxxxxxxxxxxxxxxxxxxxx --override --name_mappings=general:_general,random:_random

7-2. interactiveコマンドを使用して，すべて画面操作で設定を進める方法
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    $ slack_transfer　interactive

でプログラムを開始できます．あとは，指示に従って進めるだけです．

