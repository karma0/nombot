nombot
======

A flexible cryptocurrency trading bot written in Python.

Dependencies
------------

Some assumptions are made that you are familiar with Python and operate
in Linux. There is currently no way to test on Windows or Apple
operating systems, and while you may use the OTS strategies that come
with this repository, in order to expand on your strategy development
time is a likely requirement.

If you are able to use ``docker``, this will solve the first problem. If
you are able to pay for development services, that will solve the
second.

Python Dependencies
~~~~~~~~~~~~~~~~~~~

-  Python 3.6+ is assumed
-  ``bors``
-  ``ccxt``
-  ``dataclasses``

Key Features
------------

Exchanges
~~~~~~~~~

-  Extensible for any exchange using CCXT.
-  Exchange helper facilities; \_connection pooling, websockets, shared
   contexts.
-  Mutiple exchange connectivity allowing for arbitrage.
-  Strive toward dynamic, forward-compatible interfaces.

Currencies
~~~~~~~~~~

All currencies supported; *if the exchange supports it, it will
work*. \* Wallet support, allowing for automated coin transfers.
*(coming soon)*

Algorithms
~~~~~~~~~~

Implementation is independent of strategy, allowing for maximal
reuse, flexibility, and enforcing DRY principles.

Strategies
~~~~~~~~~~

-  "Plugable" *strategy* architecture using ``IStrategy`` inheritance.
-  "Stackable" architecture allows you to isolate grouped functionality
   for reuse.
-  Utilizes a middleware pipeline for processing.
-  Shared context objects allow for maximum versatility in complex
   scenarios.
-  Utilization of algorithms as backend functional libraries (strategy
   equates to "business logic").
-  Automatic configuration pass-through.
-  See ``bors`` for more information.

Configuration
~~~~~~~~~~~~~

Flexible modularized configuration using JSON.  See ``config.json.example``.

Security
~~~~~~~~

-  Namespaced immutable configuration will greatly reduce your chance of
   information leakage and manipulation.
-  File system storage & security (requires careful consideration of
   file permissions; see install notes below).

Coming soon...
~~~~~~~~~~~~~~

-  Backtesting and supporting documentation.
-  More documentation around creating exchanges, algorithms, and
   strategies.
-  Tests, tests, tests!
-  For a deployment example, see ``siphonexchange``.

Setup
-----

Installation
~~~~~~~~~~~~

.. code:: bash

    git clone https://github.com/karma0/nombot.git nombot && cd $_
    pip install requests numpy pandas

Upgrading to the latest
~~~~~~~~~~~~~~~~~~~~~~~

The ``master`` branch will contain the latest release. ``develop`` will
contain the latest developments and may break things.

.. code:: bash

    git pull

Configuration
~~~~~~~~~~~~~

1. Create your strategy class, using any available algorithms, or
   creating your own algorithms.
2. Copy ``config.json.example`` to ``config.json`` and execute
   ``chmod 600 config.json``.
3. Change the configuration required for your strategy, exchange(s), API
   calls, etc. based on the examples.

Execution
~~~~~~~~~

.. code:: bash

    ./trader.py

Contributing
------------

Options: 1. Follow the instructions here:
https://help.github.com/articles/fork-a-repo/ 2. Submit an issue or
feature request
`here <https://help.github.com/articles/fork-a-repo/>`__.
