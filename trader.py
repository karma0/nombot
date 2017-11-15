#!/usr/bin/env python3

"""
Trading bot
"""

from api.services.coinigy import Coinigy
from app.builder import AppBuilder

from app.strategy import Strategy
from strategies.supplementary.coinigy import CoinigyStrategy
from strategies.print import Print
from strategies.echo import Echo


def main(strategies=None, apiclasses=None):
    """Main routine"""
    if strategies is None:
        strategies = [
            CoinigyStrategy(),
            Print(),
            Echo()
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
