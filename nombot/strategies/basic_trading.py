"""
Supplementary trading strategy
"""

from nombot.app.strategy import IStrategy


class StockSupplement(IStrategy):
    """Print Strategy implementation"""
    history = StockDataFrame()

    def bind(self, context):
        """
        Bind the strategy to the middleware pipeline,
        returning the context
        """
        self.supplement(context)

        # just pass-through
        return context

    def supplement(self, context):
        """Supplement the context with stockstats"""
        self.history.append(self.parse(context.get('result')))

    def parse(self, result):
        """Parse the results to generate stock data as exchange->src->dest"""
        return result
