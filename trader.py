#!/usr/bin/env python3

"""
Trading bot
"""

from api.services.coinigy import Coinigy
from app.builder import AppBuilder
from app.config import Conf

from strategies.strategy import Strategy
from strategies.print import Print
from strategies.echo import Echo


def main(strategies=[Print(), Echo()], apiclasses=[Coinigy], configfile=None):
    """Main routine"""
    # Grab configuration
    conf = Conf(filename=configfile)

    # Roll out pipeline
    strat = Strategy(*strategies)
    impl = AppBuilder(apiclasses, strat)

    # Run
    impl.run()


if __name__ == "__main__":
    main()
