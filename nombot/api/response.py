"""
Generic API Interface, mixin, and response maps/types
"""

from bors.common.dotobj import DotObj
from nombot.generics import exchange as X


RESPONSE_MAP = {
    "load_markets": X.MarketSchema(),
    "fetch_order_book": X.OrderBookSchema(),
    "fetch_ticker": X.TickerSchema(),
    "fetch_trades": X.TradeSchema(many=True),
}


class Result(DotObj):
    """A bare result object"""
    def __init__(self, **kwargs):
        self.callname = kwargs.get('callname', None)
        self.channel = kwargs.get('channel', None)
        self.response_type = kwargs.get('response_type', None)
        self.result = kwargs.get('result', None)
        self.errors = kwargs.get('errors', None)
        super().__init__(**kwargs)
