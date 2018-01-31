"""
Simple Market Maker strategy
"""

from nombot.app.strategy import IStrategy
from nombot.algorithms.echo import echo


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
