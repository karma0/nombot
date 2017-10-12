"""
Trading bot
"""

from api.coinigy import Coinigy
from builder import AppBuilder
from config import Conf

from strategies.strategy import Strategy
from strategies.print import Print


def main():
    """Main routine"""
    # Grab configuration
    conf = Conf()

    # Roll out pipeline
    strat = Strategy(Print())
    impl = AppBuilder(conf, Coinigy, strat)

    # Run
    impl.run()


if __name__ == "__main__":
    main()
