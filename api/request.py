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
    def make_request(self, data):
        """Parse the outgoing schema"""
        callname = self.context.get("callname")
        try:
            payload = REQUEST_MAP[callname].dump(data)  # type: ignore
        except AttributeError:
            payload = None

        request = {
            "callname": callname,
            "payload": payload
        }
        return Request(**request)

    class Meta:
        """Stricty"""
        strict = True
