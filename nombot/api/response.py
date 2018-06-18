"""
Generic API Interface, mixin, and response maps/types
"""

from bors.common.dotobj import DotObj
from nombot.generics import exchange as X


RESPONSE_MAP = {
    # commented, as they are not implemented
    "fetchBalance": X.BalanceSchema(many=True),
    "fetchMarkets": X.MarketSchema(),
    # "fetchOHLCV": X.OHLCVSchema(many=True),
    "fetchOrderBook": X.OrderBookSchema(many=True),
    "fetchOrders": X.OrderSchema(many=True),
    "fetchOpenOrders": X.OrderSchema(many=True),
    "fetchClosedOrders": X.OrderSchema(many=True),
    "fetchTicker": X.TickerSchema(),
    "fetchTickers": X.TickerSchema(many=True),
    "fetchTrades": X.TradeSchema(many=True),
    "fetchMyTrades": X.MyTradeSchema(many=True),
}


class Result(DotObj):
    """A bare result object"""
    def __init__(self, **kwargs):
        self.callname = kwargs.get('callname', None)
        self.channel = kwargs.get('channel', None)
        self.response_type = kwargs.get('response_type', None)
        self.result = kwargs.get('results', None)
        self.errors = kwargs.get('errors', None)
