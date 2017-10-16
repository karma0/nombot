"""Result type definitions"""

from collections import namedtuple as nt

RESULT_TYPES = {

    "channellist": nt("channellist", ("channel")),

    "tradeMessage": nt("tradeMessage", (
        "channel",
        "exchId",
        "exchange",
        "label",
        "market_history_id",
        "marketid",
        "price",
        "quantity",
        "time",
        "time_local",
        "timestamp",
        "total",
        "tradeid",
        "type"
    )),

    "accounts": nt("accounts", (
        "auth_id",
        "auth_key",
        "auth_optional1",
        "auth_nickname",
        "exch_name",
        "auth_secret",
        "auth_updated",
        "auth_active",
        "auth_trade",
        "exch_trade_enabled",
        "exch_id"
    )),

    "pushNotifications": nt("pushNotifications", (
        "notification_vars",
        "notification_title_vars",
        "notification_time_added",
        "notification_type_title",
        "notification_type_message",
        "notification_style"
    )),

    "alerts": nt("alerts", (
        "open_alerts",
        "alert_history"
    )),

    "userInfo": nt("userInfo", (
        "email",
        "active",
        "last_login",
        "chat_enabled",
        "chat_nick",
        "ticker_enabled",
        "ticker_indicator_time_type",
        "custom_ticker",
        "first_name",
        "last_name",
        "last_active",
        "pref_subscription_expires",
        "pref_alert_email",
        "pref_alert_sms",
        "pref_trade_email",
        "pref_trade_sms",
        "pref_alert_mobile",
        "pref_trade_mobile",
        "pref_balance_email",
        "pref_referral_code",
        "created_on",
        "company",
        "phone",
        "street1",
        "street2",
        "city",
        "state",
        "zip",
        "country",
        "newsletter",
        "two_factor",
        "subscription_status",
        "referral_balance",
        "pref_app_device_id"
    )),

    "activity": nt("activity", (
        "notification_vars",
        "notification_title_vars",
        "notification_time_added",
        "notification_type_title",
        "notification_type_message",
        "notification_style"
    )),

    "balances": nt("balances", (
        "balance_curr_code",
        "balance_amount_avail",
        "balance_amount_held",
        "balance_amount_total",
        "btc_balance",
        "last_price"
    )),

    "balanceHistory": nt("balanceHistory", (
        "auth_id",
        "balance_curr_code",
        "balance_date",
        "balance_amount_avail",
        "balance_amount_held",
        "balance_amount_total",
        "btc_value",
        "timestamp"
    )),

    "orders": nt("orders", (
        "open_orders",
        "order_history"
    )),

    "userWatchList": nt("userWatchList", (
        "exchmkt_id",
        "mkt_name",
        "exch_code",
        "exch_name",
        "primary_currency_name",
        "secondary_currency_name",
        "server_time",
        "last_price",
        "prev_price",
        "high_trade",
        "low_trade",
        "current_volume",
        "fiat_market",
        "btc_volume"
    )),

    "newsFeed": nt("newsFeed", (
        "id",
        "url",
        "title",
        "pubDate",
        "timestamp",
        "feed_id",
        "published_date",
        "feed_name",
        "feed_url",
        "feed_enabled",
        "feed_description",
        "url_field",
        "title_field",
        "date_field",
        "feed_image"
    )),

    "orderType": nt("orderType", (
        "order_type_id",
        "name",
        "order"
    )),

    "priceType": nt("priceType", (
        "price_type_id",
        "name",
        "order"
    )),

    "openorder": nt("openorder", (
        "auth_id",
        "exch_id",
        "mkt_id",
        "order_type_id",
        "price_type_id",
        "limit_price",
        "order_quantity"
    )),

    "exchange": nt("exchange", (
        "exch_id",
        "exch_name",
        "exch_code",
        "exch_fee",
        "exch_trade_enabled",
        "exch_balance_enabled",
        "exch_url"
    )),

    "market": nt("market", (
        "exch_id",
        "exch_name",
        "exch_code",
        "mkt_id",
        "mkt_name",
        "exchmkt_id"
    )),

    "data": nt("data", (
        "exch_code",
        "primary_curr_code",
        "secondary_curr_code",
        "type"
    )),

    "alldata": nt("alldata", (
        "exch_code",
        "primary_curr_code",
        "secondary_curr_code",
        "type",
        "history"
        "asks",
        "bids"
    )),

    "history": nt("history", (
        "price",
        "quantity",
        "time_local",
        "type"
    )),

    "ask": nt("ask", (
        "price",
        "quantity",
        "total"
    )),

    "bid": nt("bid", (
        "price",
        "quantity",
        "total"
    )),

    "order": nt("order", (
        "ordertype",
        "price",
        "quantity",
        "total"
    )),

    "ticker": nt("ticker", (
        "exchange",
        "market",
        "last_trade",
        "high_trade",
        "low_trade",
        "current_volume",
        "timestamp",
        "ask",
        "bid"
    )),

}
