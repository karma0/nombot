"""
Simple result display strategy
"""

from bors.app.strategy import IStrategy
from bors.algorithms.echo import echo


class Print(IStrategy):
    """Print result from exchange"""
    def bind(self, context):
        """
        Bind the strategy to the middleware pipeline,
        returning the context
        """
        result = context["result"].data
        callname = result["channel"] if result["channel"] else result["callname"]
        echo(f"""Call: {callname}; PrintResult: {result["result"].data}""")
        return context
