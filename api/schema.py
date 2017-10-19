"""
Generic API Interface, mixin, and request/response maps/types
"""

import abc

from marshmallow import fields, Schema, pre_load

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


class ResponseSchema(Schema):
    """Schema defining the data structure the API will respond with"""
    call = fields.Str()
    errors = fields.Dict()

    #@pre_load
    #def find_schema(self, in_data):
    #    """Parse the incoming schema"""
    #    if "errors" in in_data:
    #        return in_data
    #    print(f"IN_DATA!{in_data}")
    #    in_data["data"] = RESPONSE_MAP[in_data["call"]]\
    #        .loads(in_data["data"], many=True)\
    #        .data
    #    return in_data

    class Meta:
        """Stricty"""
        strict = True
        additional = ("data",)
