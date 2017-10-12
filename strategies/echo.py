"""
Simple Market Maker strategy
"""

from strategies.strategy import IStrategy
from algorithms.echo import echo


class Echo(IStrategy):
    """Echo Strategy imolementation"""
    def bind(self, context):
        """
        Bind the strategy to the middleware pipeline,
        returning the context
        """
        echo("ECHO!")

        # just a pass-through
        return context
