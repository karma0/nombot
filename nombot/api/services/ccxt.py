"""CCXT API Facade"""

import ccxt
import json
import asyncio

from ccxt.base.errors import ExchangeNotAvailable, ExchangeError

from marshmallow import fields, pre_load

from bors.app.log import LoggerMixin

from nombot.generics.request import RequestSchema
from nombot.generics.response import ResponseSchema


class CCXTResponseSchema(ResponseSchema):
    """Schema defining how the API will respond"""
    event = fields.Str()  # for WS response
    err_num = fields.Str()
    err_msg = fields.Str()

    @pre_load
    def combine_errors(self, in_data):  # pylint: disable=no-self-use
        """Convert the error to the expected output"""
        if "err_num" in in_data:
            in_data["errors"] = dict()
            in_data["errors"][in_data["err_num"]] = in_data["err_msg"]

    def get_result(self, data):
        """Return the actual result data"""
        return data.get("data", "")

    class Meta:
        """Add 'data' field"""
        strict = True
        additional = ("data",)


class CCXT:
    X = {}  # type: dict
    sym = {}  # type: dict

    def __init__(self, exchanges=None, symbols=None, rate_limit=None):
        if exchanges is None:
            exchanges = ccxt.exchanges

        for exch in exchanges:
            exchange = getattr(ccxt, exch)
            try:
                # instantiate exchange object
                self.X[exch] = exchange()
                if rate_limit is not None:
                    self.X[exch].rate_limit = rate_limit
                self.X[exch].enable_rate_limit = True

                # Add supported symbols for given exchange
                self.sym[exch] = []
                if symbols is None:
                    if self.X[exch].symbols is not None:
                        self.sym[exch] = self.X[exch].symbols
                else:
                    for sym1 in symbols:
                        for sym2 in symbols:
                            self.sym[exch] += [sym for sym in [
                                f"{sym1}/{sym2}",
                                f"{sym2}/{sym1}"
                            ] if sym in self.X[exchange].symbols]

            except:
                del self.X[exch]
                raise ValueError(f"Failed to attach exchange `{exch}`")

    async def call(self, ex, callname, *args, **kwargs):
        """Cycle through all configured exchanges and make a call"""
        return getattr(ex, callname)(*args, **kwargs)

    async def call_all(self, callname, *args, **kwargs):
        """Cycle through all configured exchanges and make a call"""
        results = []
        for exchange, ex in self.X.items():
            try:
                result = await self.call(ex, callname, *args, **kwargs)
                results.append(result)
            except (ExchangeNotAvailable, ExchangeError):
                pass
        return json.dumps(results)

    async def call_all_on_syms(self, callname, *args, **kwargs):
        """Cycle through all configured exchanges and symbols and make a call"""
        print(f"""Calling call_all_on_syms: {callname}""")
        results = []
        for exchange, ex in self.X.items():
            if self.sym[exchange] is None:
                continue
            for sym in self.sym[exchange]:
                print(f"""Exchange: {exchange}; Symbol: {sym}""")
                try:
                    result = self.call(ex, callname, sym, *args, **kwargs)
                    results.append(result)
                except (ExchangeNotAvailable, ExchangeError):
                    pass

        return json.dumps(results)


class CCXTApi(LoggerMixin):  # pylint: disable=R0902
    """
        This class implements ccxt's REST api as documented in the
        documentation available at:
        https://github.com/ccxt/ccxt/wiki/Manual
    """
    name = "ccxt"

    local_overrides = {
        "fetch_order_book": "call_all_on_syms",
        "default": "call_all",
    }

    def __init__(self, context):
        """Launched by Api when we're ready to connect"""
        self.request_schema = RequestSchema
        self.result_schema = CCXTResponseSchema

        self.context = context
        self.conf = context.get("conf")

        # Websocket credentials object
        self.creds = self.context.get("credentials")

        self.create_logger()
        self.log.debug(f"Starting API Facade {self.name}")

        #self.ccxt = CCXT(self.conf["exchanges"])
        self.ccxt = CCXT()

    def call(self, callname, data=None, **args):
        """Substitute for REST api as defined in bors.api.requestor.Req"""
        method = self.local_overrides.get(
                callname, self.local_overrides["default"])
        loop = asyncio.get_event_loop()
        results = []
        async def task():
            results = await getattr(self.ccxt, method)(callname, data, **args)
        loop.run_until_complete(task())
        loop.close()

    def shutdown(self):
        """Perform last-minute stuff"""
        self.log.info(f"Shutting down API interface instance for {self.name}")
