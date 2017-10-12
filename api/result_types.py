"""Result type definitions"""

from collections import namedtuple as nt

RESULT_TYPES = {
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
        "exch_id",
    )),
}
