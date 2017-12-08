"""
Generic API Interface, mixin, and response maps/types
"""

from marshmallow import fields, Schema, post_load

from common.dotobj import DotObj
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
    "trade": X.WsTradeChannel(),
    "Favorite": X.FavoriteTickSchema(many=True),
    "all": X.AllMarketDataSchema(),
}


class Result(DotObj):
    """A bare result object"""
    def __init__(self, **kwargs):
        self.channel = kwargs.get('channel', None)
        self.callname = kwargs.get('callname', None)
        self.result = kwargs.get('result', None)
        self.errors = kwargs.get('errors', None)
        super().__init__(**kwargs)


class DefaultSchema(Schema):
    """Default schema parser"""
    MessageType = fields.Str(required=True)

    @post_load
    def generate_obj(self, data):  # pylint: disable=no-self-use
        """Generate new schema based on message type"""
        return RESPONSE_MAP[data["MessageType"]].dump(data["Data"])

    class Meta:
        """Data field is dyanamic type"""
        additional = ("Data",)


RESPONSE_MAP["default"] = DefaultSchema()


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
        print(f"""\n\nAPI RESP DATA!{self.context["callname"]}!{data}""")
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
        channel = self.context.get("channel")
        print(f"""\n\nRESP DATA!{channel}!{data}""")
        try:
            sch = RESPONSE_MAP[channel]
        except KeyError:
            sch = RESPONSE_MAP["default"]
        sch.dump(self.get_result(data))
        result = {
            "channel": channel,
            "result": sch.dump(self.get_result(data))  # NOQA
        }
        return Result(**result)
