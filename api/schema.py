"""
Generic API Interface, mixin, and request/response maps/types
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
}

REQUEST_MAP = {
    "refreshBalance": X.RefreshBalanceSchema(),
    "addAlert": X.CreateAlertSchema(),
    "deleteAlert": X.AlertReferenceSchema(),
    "addOrder": X.CreateOrderSchema(),
    "cancelOrder": X.OrderReferenceSchema(),
    "markets": X.ExchangeReferenceSchema(),
    "data": X.MarketDataRequestSchema(),
    "ticker": X.TickerRequestSchema(),
}


class Result:
    """A bare result object"""
    def __init__(self, **kwargs):
        self.callname = kwargs.get('callname', None)
        self.result = kwargs.get('result', None)
        self.errors = kwargs.get('errors', None)


class ResponseSchema(Schema):
    """Schema defining the data structure the API will respond with"""
    errors = fields.Dict()

    def get_result(self, data):
        """Retrieve the result from the parsed object"""
        return data.get("result", "")

    @post_load
    def populate_data(self, data):
        """Parse the incoming schema"""
        if "errors" in data:
            return Result(errors=data["errors"])
        result = {
            "callname": self.context.get("callname"),
            "result": RESPONSE_MAP[self.context.get('callname')]\
                        .dump(self.get_result(data))
        }
        return Result(**result)

    class Meta:
        """Stricty"""
        strict = True
        additional = ("result",)
