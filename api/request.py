"""
Generic API Interface, mixin, and request maps/types
"""

from marshmallow import fields, Schema, post_load

from generics import exchange as X


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


class Request:
    """A bare request object"""
    def __init__(self, **kwargs):
        self.callname = kwargs.get('callname', None)
        self.payload = kwargs.get('payload', None)


class RequestSchema(Schema):
    """Schema defining the data structure the API can be called with"""
    callname = fields.Str(required=True)
    payload = fields.Dict()

    @post_load
    def populate_data(self, data):
        """Parse the incoming schema"""
        if "errors" in data:
            return Request(errors=data["errors"])
        result = {
            "callname": self.context.get("callname"),
            "result":
                REQUEST_MAP[self.context.get('callname')].dump(data)
        }
        return Request(**result)

    class Meta:
        """Stricty"""
        strict = True
