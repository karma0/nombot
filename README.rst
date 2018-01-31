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
-  ``requests``
-  ``numpy``
-  ``pandas``
-  ``marshmallow`` for message passing, validation, and API message
   object definition.

Key Features
------------

Exchanges
~~~~~~~~~

-  Extensible for any exchange *(currently only supports coinigy)*.
-  Exchange helper facilities; \_connection pooling, websockets, shared
   contexts.
-  Mutiple exchange connectivity allowing for arbitrage.
-  Strive toward dynamic, forward-compatible interfaces.

Currencies
~~~~~~~~~~

*(coming soon)* \* All currencies possible (with some configuration). \*
Strive towards forward-compatible; *if the exchange supports it, it will
work*. \* Wallet support, allowing for automated coin transfers.
*(coming soon)*

Algorithms
~~~~~~~~~~

-  Implementation is independent of strategy, allowing for maximal
   reuse, flexibility, and enforcing DRY principles.
-  Can be developed to an interface using ``grpc`` and ``protobuf``, for
   example.
-  Integrated support for NumPy Arrays and Pandas DataFrames
   (implemented at the strategy level).

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

Configuration
~~~~~~~~~~~~~

-  Flexible modularized configuration using JSON.
-  C-style comment support.
-  Configuration objects are protected immutable, using ``namedtuple``
   containers.
-  Configuration object parameters exist as object attributes:
   ``conf.var1``.
-  Configuration is namespaced, allowing for hierarchical configuration
   passthrough.

Security
~~~~~~~~

-  Namespaced immutable configuration will greatly reduce your chance of
   information leakage and manipulation.
-  File system storage & security (requires careful consideration of
   file permissions; see install notes below).

Coming soon...
~~~~~~~~~~~~~~

-  GRPC strategy to allow parallel processing in microservices
   environments.
-  API expansion to World Coin Market's top-20 exchanges.
-  Backtesting and supporting documentation.
-  Database integration.
-  More documentation around creating exchanges, algorithms, and
   strategies.
-  Tests, tests, tests!

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
contain the latest development release and may break things.

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
