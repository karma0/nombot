#!/usr/bin/env python3

"""
Trading bot
"""

try:
    import coloredlogs
    coloredlogs.install()
except ImportError:
    print("Use Python coloredlogs module for colored output")

from api.services.coinigy import Coinigy
from app.builder import AppBuilder

from app.strategy import Strategy
from strategies.supplementary.coinigy import CoinigyStrategy
from strategies.supplementary.trading import OHLCVStrategy
from strategies.print import PrintResult


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
