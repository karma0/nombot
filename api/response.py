"""
Generic API Interface, mixin, and response maps/types
"""

from marshmallow import fields, Schema, post_load

from generics import exchange as X


RESPONSE_MAP = {
    "accounts": X.AccountSchema(many=True),
    "balances": X.BalanceSchema(many=True),
    "orders": X.AllOrdersSchema(),
    "alerts": X.AllAlertsSchema(),
    "newsFeed": X.NewsItemSchema(many=True),
    "orderTypes": X.OrderTypesCallSchema(),
    "refreshBalance": X.BalanceSchema(),
    "addOrder": X.OrderReferenceSchema(),
    "exchanges": X.ExchangeSchema(many=True),
    "markets": X.MarketSchema(many=True),
    "data": X.AllMarketDataSchema(),
    "ticker": X.TickSchema(),
    "ws_trade_ticker": X.WsTradeChannel(),
    "Favorite": X.FavoriteTickSchema(many=True),
}


class Result:
    """A bare result object"""
    def __init__(self, **kwargs):
        self.channel = kwargs.get('channel', None)
        self.callname = kwargs.get('callname', None)
        self.result = kwargs.get('result', None)
        self.errors = kwargs.get('errors', None)


class ResponseSchema(Schema):
    """Schema defining the data structure the API will respond with"""
    errors = fields.Dict()

    def get_result(self, data):  # pylint: disable=no-self-use
        """
        Retrieve the result from the parsed object
          ~~ Override this to match your API. ~~
        """
        return data.get("result", "")

    @post_load
    def populate_data(self, data):
        """Parse the incoming schema"""
        if "errors" in data:
            return Result(errors=data["errors"])
        callname = self.context.get("callname")
        result = {
            "callname": callname,
            "result": RESPONSE_MAP[callname]  # type: ignore
                      .dump(self.get_result(data))  # NOQA
        }
        return Result(**result)

    class Meta:
        """Stricty"""
        strict = True
        additional = ("result",)


class WSResponseSchema(ResponseSchema):
    """
    Schema defining the data structure from published messages on the websock
    """
    @post_load
    def populate_data(self, data):
        """Parse the incoming schema"""
        if "errors" in data:
            return Result(errors=data["errors"])
        # pylint: disable=E1101
        result = {
            "channel": self.context.get("channel"),
            "result": RESPONSE_MAP[self.MessageType]  # type: ignore
                      .dump(self.get_result(data))  # NOQA
        }
        return Result(**result)
