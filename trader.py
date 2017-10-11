"""
Trading bot
"""

from api.coinigy import Coinigy
from builder import Build
from config import Conf

from strategies.strategy import Strategy
from strategies.mm import MarketMaker


def main():
    """Main routine"""
    # Grab configuration
    conf = Conf()

    # Roll out pipeline
    strat = Strategy()
    strat.add_strategy(MarketMaker())
    impl = Pipeline(conf, Coinigy, strategy)

    # Run
    impl.run()


if __name__ == "__main__":
    main()
