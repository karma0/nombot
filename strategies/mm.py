"""
Simple Market Maker strategy
"""

from strategies.strategy import IStrategy


class MarketMaker(IStrategy):
    """Market Maker Strategy imolementation"""
    def bind(self, context):
        """
        Bind the strategy to the middleware pipeline,
        returning the context
        """
        print("ALGO!")
        return context

    def shutdown(self):
        pass
