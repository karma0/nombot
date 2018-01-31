"""
Generic API Interface, mixin, and response maps/types
"""

from nombot.common.dotobj import DotObj
from nombot.generics import exchange as X


RESPONSE_MAP = {
    "accounts": X.AccountSchema(many=True),
    "balances": X.BalanceSchema(many=True),
    "alerts": X.AllAlertsSchema(),
    "newsFeed": X.NewsItemSchema(many=True),
    "orderTypes": X.OrderTypesCallSchema(),
    "refreshBalance": X.BalanceSchema(),
    "addOrder": X.OrderReferenceSchema(),
    "exchanges": X.ExchangeSchema(many=True),
    "markets": X.MarketSchema(many=True),
    "data": X.AllMarketDataSchema(),
    "ticker": X.TickSchema(),
    "trade": X.WsTradeChannel(),
    "orders": X.WsOrderChannel(many=True),
    "Favorite": X.FavoriteTickSchema(many=True),
    "all": X.AllMarketDataSchema(),
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
