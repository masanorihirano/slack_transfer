環境構築
==========
※ jupyter notebookなどのpythonが使用できる環境があれば充分です．jupyter notebookの場合は，2の「マシーンの環境に直接インストールする場合」から始めてください． `!`をつけて実行することで，コマンドを実行することができます．ただし，jupyter notebookの場合は，インタラクティブモードは使用できません．

Google Colabで稼働可能なnotebookも例示しています:

.. image:: https://colab.research.google.com/assets/colab-badge.svg
    :alt: Open In Colab
    :target: https://colab.research.google.com/github/masanorihirano/slack_transfer/blob/main/examples/slack_transfer.ipynb


1. Python環境の構築
-------------------
※binary版(exe版)を使用する場合は不要です．3に進んでください．

Windows
~~~~~~~~~~~~~~~
Windowsの場合は，WSLの仕様をお勧めします．
WSLはlinuxと同じです．

WSLを使用しない場合は，以下のリンクからPythonを取得します．

https://www.microsoft.com/store/productId/9P7QFQMJRFP7

なお，移行の作業はシェルを必要とします．
pwshなり，cmdなりで操作をしてください．


Mac
~~~~~~~~~~~~~~~
たぶん，初期設定は不要です．

Linux
~~~~~~~~~~~~~~~
たぶん，初期設定は不要ですが，python3が見つからなければ，:code:`sudo apt install python3` などでインストールしてください．


2. slack-transfer のインストール
-------------------
※binary版(exe版)を使用する場合は不要です．3に進んでください．

マシーンの環境に直接インストールする場合
~~~~~~~~~~~~~~~
.. code-block:: bash

    pip3 install slack-transfer


venvを利用する場合
~~~~~~~~~~~~~~~
WSL/linux/macos:

.. code-block:: bash
    $ python3 -m venv .venv
    $ source .venv/bin/activate
    (.venv)$ pip3 install slack-transfer


Windows:

.. code-block:: bash
    $ python3 -m venv .venv
    $ source .venv\Scripts\activate
    (.venv)$ pip3 install slack-transfer


3. もし万が一，どうしても環境構築が困難な場合
-------------------
下記のリリースページの各バージョンの場所に，ビルド済みの実行ファイルが環境ごとにzipファイルでおかれています．

https://github.com/masanorihirano/slack_transfer/releases

セキュリティー上のリスクがあるため，推奨はしていませんが，どうしても環境構築が困難である場合には，OSに合わせたファイルをダウンロードし，実行することで，インタラクティブモードで作業をすることができます．
ZIPを解凍すると，中に実行ファイルが入っています．Mac OSの場合は，設定のセキュリティー&プライバシーから実行許可をする必要があります．Windowsの場合は，ダブルクリック後，詳細から実行するを選ぶ必要があります．
Linuxの場合は，Ubuntu版が挙動すると思われます．ただし，すべての環境での挙動をサポートしているわけではないので，動かない可能性があることを予めご了承ください．

※インタラクティブモード以外のCLIを使用することはできません．
