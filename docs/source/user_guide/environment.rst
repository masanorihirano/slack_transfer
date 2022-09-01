Environmental Settings
==========
\* A python environment such as jupyter notebook is sufficient. For jupyter notebook, start with 2, "Installing directly into the machine's environment". :code:`!` can be used to execute the command. However, interactive mode is not available for jupyter notebook.

A notebook that can run on Google Colab is also provided:

.. image:: https://colab.research.google.com/assets/colab-badge.svg
    :alt: Open In Colab
    :target: https://colab.research.google.com/github/masanorihirano/slack_transfer/blob/main/examples/slack_transfer.ipynb


1. Building a Python Environment
-------------------
\* If you are using the binary version (exe version), this is not necessary.

Windows
~~~~~~~~~~~~~~~
For Windows, the use of  WSL is highly recommended.
WSL is the same as Linux.

If you do not use WSL, you can obtain Python from the following link.

https://www.microsoft.com/store/productId/9P7QFQMJRFP7

The migration process requires a shell.
Please use pwsh or cmd.


Mac
~~~~~~~~~~~~~~~
Probably no initial setup is required.

Linux
~~~~~~~~~~~~~~~
Probably no initial setup is required, but if python3 is not found, install it with :code:`sudo apt install python3` or similar.


2. Installing slack-transfer
-------------------
\* If you are using the binary version (exe version), this is not necessary.

Installing directly into the machine's environment
~~~~~~~~~~~~~~~
.. code-block:: bash

    pip3 install slack-transfer


Using venv
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


3. When it is impossible to build your environment
-------------------
The built executable files are available as zip files for each environment on the release page at the following link.

https://github.com/masanorihirano/slack_transfer/releases

Although we don't recommend it due to security risks, you can use it if you have difficulty in setting up the environment.
You can download and un-archive the files which is compatible to your OS.
Then, run the program in interactive mode.
If you are using Mac OS, you will need to set the execute permission in the "Security & Privacy" tab of the "Configuration" menu.
For Linux, the Ubuntu version should work. However, please note that this version does not support all environments, so it may not work in all cases.

\*The CLI cannot be used.
