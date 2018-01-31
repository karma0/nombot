"""
Simple context display strategy
"""

from nombot.app.strategy import IStrategy
from nombot.algorithms.echo import echo


class Print(IStrategy):
    """Print Strategy implementation"""
    def bind(self, context):
        """
        Bind the strategy to the middleware pipeline,
        returning the context
        """
        echo(f"""PrintStrategy: {context}""")

        # just a pass-through
        return context


class PrintResult(IStrategy):
    """Print Strategy implementation"""
    def bind(self, context):
        """
        Bind the strategy to the middleware pipeline,
        returning the context
        """

        # just a pass-through
        return context
