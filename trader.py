#!/usr/bin/env python3

"""
Trading bot
"""

try:
    import coloredlogs
    coloredlogs.install()
except ImportError:
    print("Use Python coloredlogs module for colored output")

from nombot.api.services.coinigy import Coinigy
from nombot.app.builder import AppBuilder

from nombot.app.strategy import Strategy
from nombot.strategies.middleware.coinigy import CoinigyStrategy
from nombot.strategies.middleware.trading import OHLCVStrategy
from nombot.strategies.print import PrintResult


def main(strategies=None, apiclasses=None):
    """Main routine"""
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
    impl = AppBuilder(apiclasses, strat)

    # Run
    impl.run()


if __name__ == "__main__":
    main()
