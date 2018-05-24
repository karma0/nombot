#!/usr/bin/env python3

"""
Trading bot
"""

try:
    import coloredlogs
    coloredlogs.install()
except ImportError:
    print("Use Python coloredlogs module for colored output")

from bors.app.strategy import Strategy
from bors.strategies.print import PrintResult

from nombot.app.builder import NomAppBuilder
from nombot.app.config import NomAppConf
from nombot.strategies.middleware.coinigy import CoinigyStrategy
from nombot.strategies.middleware.trading import OHLCVStrategy
from nombot.api.services.coinigy import Coinigy


def main(strategies=None, apiclasses=None, configfile=None):
    """Main routine"""
    # instantiate this first to avoid weird errors
    if strategies is None:
        strategies = [
            CoinigyStrategy(),
            OHLCVStrategy(),
            PrintResult(),
        ]
    if apiclasses is None:
        apiclasses = [Coinigy]

    # Roll out pipeline
    configfile = "config.json" if configfile is None else configfile
    with open(configfile) as json_data:
        config = json_data.read()
    app_conf = NomAppConf(config)
    strat = Strategy(*strategies)
    impl = NomAppBuilder(apiclasses, strat, app_conf)

    # Run
    impl.run()


if __name__ == "__main__":
    main()
