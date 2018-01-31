"""
Simple echo strategy to output an "ECHO"
"""

from nombot.app.strategy import IStrategy
from nombot.algorithms.echo import echo


class Echo(IStrategy):
    """Echo Strategy implementation"""
    def bind(self, context):
        """
        Bind the strategy to the middleware pipeline,
        returning the context
        """
        echo("ECHO!")

        # just a pass-through
        return context
