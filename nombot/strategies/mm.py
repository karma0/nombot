"""
Simple Market Maker strategy
"""

from bors.app.strategy import IStrategy
from bors.algorithms.echo import echo


class MarketMaker(IStrategy):
    """Market Maker Strategy imolementation"""
    def bind(self, context):
        """
        Bind the strategy to the middleware pipeline,
        returning the context
        """
        echo("ALGO!")
        # currently, just a pass-through
        return context
