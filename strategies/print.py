"""
Simple context display strategy
"""

from strategies.strategy import IStrategy
from algorithms.echo import echo


class Print(IStrategy):
    """Print Strategy implementation"""
    def bind(self, context):
        """
        Bind the strategy to the middleware pipeline,
        returning the context
        """
        echo(context)

        # just a pass-through
        return context
