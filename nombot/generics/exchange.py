"""Generic exchange schemas"""

from marshmallow import Schema, post_load
from marshmallow import fields as f

from nombot.common.dotobj import DotObj


class GenericObject(DotObj):
    """Generic object with dot or hash style get/set"""
    pass

class GenericSchema(Schema):
    """Schema from which all other schemas should inherit"""
    @post_load
    def make_object(self, data):  # pylint: disable=no-self-use
        """Generate an object for passing to the exchange API"""
        return GenericObject(data)


class ApiFacadeSchema(GenericSchema):
    """Used to define an API integration (facade)"""
    name = f.Str(required=True)
    call = f.Method(required=True)


class RequestSchema(GenericSchema):
    """Generic API result (inherit to use a schema for result creation)"""
    class Meta:
        """All results should be strict"""
        strict = True


class ResultSchema(GenericSchema):
    """Generic API result (inherit to use a schema for result creation)"""
    class Meta:
        """All results should be strict"""
        strict = True


class NotificationSchema(ResultSchema):
    """Notification!"""
    notification_id = f.Str(required=True)
    notification_type_title = f.Str(required=True)
    notification_type_message = f.Str(required=True)
    notification_style = f.Str(required=True)
    notification_vars = f.Str()
    notification_title_vars = f.Str()
    notification_pinned = f.Str()
    notification_sound = f.Str()
    notification_sound_id = f.Str()


class AccountSchema(ResultSchema):
    """Account with an exchange"""
    auth_id = f.Str(required=True)
    auth_nickname = f.Str()
    exch_id = f.Str(required=True)
    exch_name = f.Str(required=True)
    auth_active = f.Str()
    auth_trade = f.Str()
    auth_updated = f.Str()



class RefreshBalanceSchema(GenericSchema):
    """Used to refresh a balance on an account"""
    auth_id = f.Str(required=True)


class BalanceSchema(ResultSchema):
    """A balance for a given currency or auth_id"""
    balance_curr_code = f.Str(required=True)
    balance_amount_avail = f.Float()
    balance_amount_held = f.Float()
    balance_amount_total = f.Float()
    btc_balance = f.Float()
    last_price = f.Float()


class OrderSchema(ResultSchema):
    """Order"""
    exch_name = f.Str(required=True)
    mkt_name = f.Str(required=True)
    limit_price = f.Float(required=True)
    operator = f.Str()
    order_id = f.Int(required=True)
    order_type = f.Str(required=True)
    order_price_type = f.Str(required=True)
    order_status = f.Str(required=True)
    quantity = f.Float(required=True)
    order_time = f.Str(required=True)
    foreign_order_id = f.Str()
    auth_id = f.Str(required=True)
    auth_nickname = f.Str()
    quantity_remaining = f.Float()
    stop_price = f.Float()
    price_type_id = f.Str()
    exch_code = f.Str(required=True)
    display_name = f.Str()


class AllOrdersSchema(ResultSchema):
    """Result containing open orders and history"""
    open_orders = f.List(f.Nested(OrderSchema()))
    order_history = f.List(f.Nested(OrderSchema()))


class AlertSchema(ResultSchema):
    """Alert"""
    exch_name = f.Str(required=True)
    mkt_name = f.Str(required=True)
    price = f.Float(required=True)
    operator = f.Str()  # <,>
    alert_history_id = f.Str()
    timestamp = f.Str(required=True)
    alert_price = f.Float(required=True)
    alert_note = f.Str()
    operator_text = f.Str()
    display_name = f.Str()


class AllAlertsSchema(ResultSchema):
    """Result containing active alerts and history"""
    open_alerts = f.List(f.Nested(AlertSchema()))
    alert_history = f.List(f.Nested(AlertSchema()))


class FavoriteTickSchema(ResultSchema):
    """Tick item from favorites"""
    exch_id = f.Int(required=True)
    exch_code = f.Str(required=True)
    exch_name = f.Str(required=True)
    mkt_id = f.Int(required=True)
    exchmkt_id = f.Int(required=True)
    display_name = f.Str(required=True)
    mkt_name = f.Str(required=True)
    primary_curr = f.Str(required=True)
    base_curr = f.Str(required=True)
    last_price = f.Int(required=True)
    btc_volume_24 = f.Float(required=True)
    volume_24 = f.Float(required=True)


class NewsItemSchema(ResultSchema):
    """News item"""
    id = f.Str(required=True)  # pylint: disable=invalid-name
    url = f.Str(required=True)
    title = f.Str(required=True)
    pubDate = f.Str(required=True)
    timestamp = f.Str(required=True)
    feed_id = f.Int(required=True)
    published_date = f.Str(required=True)
    feed_name = f.Str(required=True)
    feed_url = f.Str(required=True)
    feed_enabled = f.Int(required=True)
    feed_description = f.Str(required=True)
    url_field = f.Str(required=True)
    title_field = f.Str(required=True)
    date_field = f.Str(required=True)
    feed_image = f.Str(required=True)


class OrderTypeSchema(ResultSchema):
    """Order Type"""
    order_type_id = f.Int(required=True)
    name = f.Str(required=True)


class PriceTypeSchema(ResultSchema):
    """Price Type"""
    price_type_id = f.Int(required=True)
    name = f.Str(required=True)


class OrderTypesCallSchema(ResultSchema):
    """Response containing order_types and price_types"""
    order_types = f.List(f.Nested(OrderTypeSchema()))
    price_types = f.List(f.Nested(PriceTypeSchema()))


class CreateAlertSchema(GenericSchema):
    """Schema to generate a new alert"""
    exch_code = f.Str(required=True)  # BITF
    market_name = f.Str(required=True)  # BTC/USD
    alert_price = f.Float(required=True)
    alert_note = f.Str()


class AlertReferenceSchema(ResultSchema):
    """Schema to reference an alert during CRUD operations"""
    alert_id = f.Int(required=True)


class CreateOrderSchema(GenericSchema):
    """Schema to generate a new order"""
    auth_id = f.Int(required=True)
    exch_id = f.Int(required=True)
    mkt_id = f.Int(required=True)
    order_type_id = f.Int(required=True)
    price_type_id = f.Int(required=True)
    limit_price = f.Float(required=True)
    order_quantity = f.Float(required=True)


class OrderReferenceSchema(ResultSchema):
    """Schema to reference an order during CRUD operations"""
    internal_order_id = f.Int(required=True)


class ExchangeSchema(ResultSchema):
    """An exchange"""
    exch_id = f.Int(required=True)
    exch_name = f.Str(required=True)
    exch_code = f.Str(required=True)
    exch_fee = f.Float(required=True)
    exch_trade_enabled = f.Int(required=True)
    exch_balance_enabled = f.Int(required=True)
    exch_url = f.Str(required=True)


class ExchangeReferenceSchema(GenericSchema):
    """Used to request market data"""
    exchange_code = f.Str(required=True)


class MarketSchema(ResultSchema):
    """A currency trade pair"""
    exch_id = f.Int(required=True)
    exch_name = f.Str(required=True)
    exch_code = f.Str(required=True)
    mkt_id = f.Int(required=True)
    mkt_name = f.Str(required=True)
    exchmkt_id = f.Int(required=True)


class MarketDataRequestSchema(RequestSchema):
    """Request object for market data"""
    exchange_code = f.Str(required=True)
    exchange_market = f.Str(required=True)
    type = f.Str(required=True)


class MarketDataItemSchema(ResultSchema):
    """A single item of market data"""
    price = f.Float(required=True)
    quantity = f.Float(required=True)


class OrderItemSchema(MarketDataItemSchema):
    """A market data item that represents an ask or bid"""
    total = f.Float(required=True)


class HistoryItemSchema(MarketDataItemSchema):
    """A single order history item"""
    time_local = f.Str(required=True)
    type = f.Str(required=True)


class MarketDataSchema(ResultSchema):
    """A result encompassing some form of market data"""
    exch_code = f.Str(required=True)
    primary_curr_code = f.Str(required=True)
    secondary_curr_code = f.Str(required=True)
    type = f.Str(required=True)


class HistorySchema(MarketDataSchema):
    """A history of market data"""
    history = f.List(f.Nested(HistoryItemSchema()), required=True)


class AsksSchema(MarketDataSchema):
    """A list of open sell market orders"""
    asks = f.List(f.Nested(OrderItemSchema()), required=True)


class BidsSchema(MarketDataSchema):
    """A list of open buy market orders"""
    bids = f.List(f.Nested(OrderItemSchema()), required=True)


class OrdersSchema(MarketDataSchema):
    """A list of open buy AND sell market orders"""
    asks = f.List(f.Nested(OrderItemSchema()), required=True)
    bids = f.List(f.Nested(OrderItemSchema()), required=True)


class AllMarketDataSchema(MarketDataSchema):
    """A list of open buy and sell market orders, and the purchase history"""
    history = f.List(f.Nested(HistoryItemSchema()), required=True)
    asks = f.List(f.Nested(OrderItemSchema()), required=True)
    bids = f.List(f.Nested(OrderItemSchema()), required=True)


class TickerRequestSchema(RequestSchema):
    """Request object for ticker data"""
    exchange_code = f.Str(required=True)
    exchange_market = f.Str(required=True)


class TickSchema(ResultSchema):
    """An item from a ticker"""
    exchange = f.Str(required=True)
    market = f.Str(required=True)
    last_trade = f.Float(required=True)
    high_trade = f.Float(required=True)
    low_trade = f.Float(required=True)
    current_volume = f.Float(required=True)
    timestamp = f.Str(required=True)
    ask = f.Float(required=True)
    bid = f.Float(required=True)


class WsTradeChannel(ResultSchema):
    """An item from a websocket trade channel"""
    market_history_id = f.Int(required=True)
    channel = f.Str(required=True)
    exchange = f.Str(required=True)
    marketid = f.Int(required=True)
    label = f.Str(required=True)
    tradeid = f.Str(required=True)
    price = f.Float(required=True)
    quantity = f.Float(required=True)
    total = f.Float(required=True)
    type = f.Str(required=True)
    exchId = f.Int(required=True)
    time = f.Str(required=True)
    timestamp = f.Str(required=True)
    time_local = f.Str(required=True)

class WsOrderChannel(ResultSchema):
    """An item from a websocket order channel"""
    exchange = f.Str(required=True)
    label = f.Str(required=True)
    ordertype = f.Str(required=True)
    price = f.Float(required=True)
    quantity = f.Float(required=True)
    total = f.Float(required=True)
    timestamp = f.Str(required=True)
