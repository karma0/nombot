#!/usr/bin/env python3

"""
Trading bot
"""

try:
    import coloredlogs
    coloredlogs.install()
except ImportError:
    print("Use Python coloredlogs module for colored output")

from bors.app.builder import AppBuilder
from bors.app.strategy import Strategy
from bors.strategies.print import PrintResult

from nombot.app.config import AppConf
from nombot.strategies.middleware.coinigy import CoinigyStrategy
from nombot.strategies.middleware.trading import OHLCVStrategy
from nombot.api.services.coinigy import Coinigy


def main(strategies=None, apiclasses=None, config=None):
    """Main routine"""
    # instantiate this first to avoid weird errors
    conf = AppConf(config)
    if strategies is None:
        strategies = [
            CoinigyStrategy(),
            OHLCVStrategy(),
            PrintResult(),
        ]
    if apiclasses is None:
        apiclasses = [Coinigy]

    # Roll out pipeline
    strat = Strategy(*strategies)
    impl = AppBuilder(apiclasses, strat, conf)

    # Run
    impl.run()


if __name__ == "__main__":
    main()
