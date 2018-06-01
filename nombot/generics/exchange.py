"""Generic exchange schemas"""

from marshmallow import fields as f

from bors.generics.common import ResultSchema


class LimitSchema(ResultSchema):
    """A Limit"""
    min = f.Float()
    max = f.Float()


class AmountPriceSchema(ResultSchema):
    """Limits"""
    amount = f.Nested(LimitSchema, required=True)
    price = f.Nested(LimitSchema, required=True)


class FeeSchema(ResultSchema):
    """A fee"""
    currency = f.Str(required=True)
    cost = f.Float(required=True)
    rate = f.Float(required=True)


class OrderSchema(ResultSchema):
    """Order"""
    id = f.Str(required=True)
    datetime = f.Str(required=True)
    timestamp = f.Int(required=True)
    lastTradeTimestamp = f.Int(required=True)
    status = f.Str(required=True)
    symbol = f.Str(required=True)
    type = f.Str(required=True)
    side = f.Str(required=True)
    price = f.Float(required=True)
    amount = f.Float(required=True)
    filled = f.Float(required=True)
    remaining = f.Float(required=True)
    cost = f.Float(required=True)
    trades = f.List(f.List(f.Float()))  # [  [ price, amount ], ... ]
    fee = f.Nested(FeeSchema, required=True)
    info = f.Dict(required=True)


class OrderBookSchema(ResultSchema):
    """Order Book"""
    bids = f.List(f.List(f.Float()))  # [  [ price, amount ], ... ]
    asks = f.List(f.List(f.Float()))  # [  [ price, amount ], ... ]
    timestamp = f.Int()
    datetime = f.Str()


class MarketSchema(ResultSchema):
    """Market"""
    active = f.Bool(required=True)
    symbol = f.Str(required=True)  # 'BTC/USD'
    base = f.Str(required=True)  # 'BTC'
    baseId = f.Str(required=True)
    quote = f.Str(required=True)  # 'USD'
    quoteId = f.Str(required=True)
    fee_loaded = f.Bool()
    id = f.Str(required=True)
    info = f.Dict(required=True)
    limits = f.Nested(AmountPriceSchema)
    maker = f.Float()
    taker = f.Float()
    percentage = f.Bool()
    precision = f.Nested(AmountPriceSchema)
    tierBased = f.Bool()


class TickerSchema(ResultSchema):
    """Ticker!"""
    symbol = f.Str(required=True)
    info = f.Dict(required=True)
    timestamp = f.Int()
    datetime = f.Str()
    high = f.Float()
    low = f.Float()
    bid = f.Float()
    bidVolume = f.Float()
    ask = f.Float()
    askVolume = f.Float()
    vwap = f.Float()
    open = f.Float()
    close = f.Float()
    last = f.Float()
    previousClose = f.Float()
    change = f.Float()
    percentage = f.Float()
    average = f.Float()
    baseVolume = f.Float()
    quoteVolume = f.Float()


class TradeSchema(ResultSchema):
    """A single trade"""
    info = f.Dict(required=True)
    id = f.Str(required=True)
    timestamp = f.Int(required=True)
    datetime = f.Str(required=True)
    symbol = f.Str(required=True)
    order = f.Str()
    type = f.Str(required=True)
    side = f.Str(required=True)
    price = f.Float(required=True)
    amount = f.Float(required=True)


class MyTradeSchema(ResultSchema):
    """A single trade on my account"""
    id = f.Str(required=True)
    timestamp = f.Int(required=True)
    datetime = f.Str(required=True)
    symbol = f.Str(required=True)
    order = f.Str()
    type = f.Str(required=True)
    side = f.Str(required=True)
    price = f.Float(required=True)
    amount = f.Float(required=True)
    cost = f.Float(required=True)
    fee = f.Nested(FeeSchema, required=True)
    info = f.Dict(required=True)
