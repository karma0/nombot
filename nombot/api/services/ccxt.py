"""CCXT API Facade"""

import asyncio
from itertools import product
from dataclasses import dataclass

import ccxt.async as ccxt
from ccxt.base.errors import ExchangeNotAvailable, ExchangeError

from marshmallow import pre_load

from bors.app.log import LoggerMixin

from nombot.generics.request import RequestSchema
from nombot.generics.response import ResponseSchema


class CCXTResponseSchema(ResponseSchema):
    """Generic response class"""
    @pre_load
    def prep_response(self, in_data):
        """Set the response to the correct output"""
        in_data["result"] = in_data


@dataclass
class CCXTExchange:
    """Exchange data object"""
    name: str
    currencies: list
    rate_limit: int = None
    credentials: dict = None

    _ex = None
    loop = asyncio.get_event_loop()

    avail_currencies = None
    _currencies = None

    avail_markets = None
    markets = None

    avail_symbols = None
    symbols = None

    def __post_init__(self):
        # instantiate exchange object
        self._ex = getattr(ccxt, self.name)()

        if self.rate_limit is not None:
            self._ex.rate_limit = self.rate_limit
        self._ex.enable_rate_limit = True

        if self.credentials is not None:
            self._ex.apiKey = self.credentials.get("apiKey", None)
            self._ex.secret = self.credentials.get("secret", None)

        self.loop.run_until_complete(self.load())

    def has(self, callname):
        """Returns `has` value of exchange"""
        return self._ex.has.get(callname, False)

    async def load(self, reload=False, *args, **kwargs):
        """Load the markets; populating the exchange object with data"""
        if self.markets is not None and not reload:
            return

        self.avail_markets = await self._ex.load_markets(*args, **kwargs)

        self.avail_currencies = getattr(self._ex, "currencies", {})
        if not self.currencies:
            # copy all currencies
            self._currencies = self.avail_currencies
        else:
            # copy relevant currencies
            self._currencies = {
                curr: self.avail_currencies[curr]
                for curr in self.currencies
                if curr in self.avail_currencies
            }

        self.avail_symbols = getattr(self._ex, "symbols", [])
        currencies = self._currencies.keys()
        self.symbols = [
            "/".join(pair)
            for pair in product(currencies, currencies)
            if "/".join(pair) in self.avail_symbols
        ]

        self.markets = {
            sym: self.avail_markets[sym]
            for sym in self.symbols
        }

    async def call_over_syms(self, callname, *args, **kwargs):
        """Cycle through configured exchanges and symbols and make a call"""
        results = {}
        for sym in self.markets.keys():
            try:
                results[sym] = await self.call(callname, sym, *args, **kwargs)
            except (ExchangeNotAvailable, ExchangeError):
                pass
        return results

    async def call(self, callname, *args, **kwargs):
        """Generalized async `call` method, pass callname and parameters"""
        try:
            return await getattr(self._ex, callname)(*args, **kwargs)
        except TypeError:
            raise AttributeError(f"Failed to execute call {callname} on "
                                 f"exchange {self._ex.name}")

    async def close(self):
        """Close all exchange connections"""
        await self._ex.close()

    def shutdown(self):
        """Teardown the aio loop"""
        self.loop.run_until_complete(self.close())
        self.loop.close()


class CCXT:
    """CCXTExchange wrapper"""
    _ex = {}  # type: dict

    def __init__(self, log, conf, context):
        self.log = log
        self.conf = conf

        rate_limit = self.conf.get("rate_limit", None)
        currencies = self.conf.get("currencies", None)
        exchanges = self.conf.get("exchanges", None)
        credentials = context.get("credentials", None)

        if exchanges is None or not exchanges:
            exchanges = ccxt.exchanges

        # Instantiate exchange objects
        for exch in exchanges:

            # Extract credentials if they exist
            creds = None
            if credentials is not None:
                for cred in credentials:
                    if cred.get("name") == exch:
                        creds = cred.copy()

            # launch exchange
            self._ex[exch] = \
                CCXTExchange(exch, currencies=currencies,
                             rate_limit=rate_limit, credentials=creds)

    def call_capable(self, exch, callname):
        """Determine if the exchange supports the call"""
        if self._ex[exch].has(callname):
            return self._ex[exch].has(callname)
        self.log.warn(f"No method available -- "
                      f"exchange: {exch}; "
                      f"call: {callname}")
        return False

    def call_on_exchanges(self, calltype, callname, *args, **kwargs):
        """Cycle through all configured exchanges to make a call"""
        results = {}
        for ex in self._ex.values():
            if self.call_capable(ex.name, callname):
                try:
                    results[ex.name] = ex.loop.run_until_complete(
                        getattr(ex, calltype)(callname, *args, **kwargs))
                except (ExchangeNotAvailable, ExchangeError):
                    pass
        return results

    def shutdown(self):
        """Shutdown / cleanup"""
        for ex in self._ex.values():
            ex.shutdown()


class CCXTApi(LoggerMixin):  # pylint: disable=R0902
    """
        This class implements ccxt's REST api as documented in the
        documentation available at:
        https://github.com/ccxt/ccxt/wiki/Manual
    """
    name = "ccxt"

    local_overrides = {
        "fetchOHLCV": "call_over_syms",
        "fetchOrderBook": "call_over_syms",
        "fetchTicker": "call_over_syms",
        "fetchTrades": "call_over_syms",
    }

    def __init__(self, context):
        """Launched by Api when we're ready to connect"""
        self.request_schema = RequestSchema
        self.result_schema = CCXTResponseSchema

        self.context = context
        self.conf = context.get("conf")

        self.create_logger()
        self.log.debug(f"Starting API Facade {self.name}")

        self.ccxt = CCXT(self.log, self.conf, self.context)

    def call(self, callname, *args, **kwargs):
        """Substitute for REST api as defined in bors.api.requestor.Req"""
        return self.ccxt.call_on_exchanges(
            self.local_overrides.get(callname, "call"),
            callname, *args, **kwargs)

    def shutdown(self):
        """Perform last-minute stuff"""
        self.log.info(f"Shutting down API interface instance for {self.name}")

        # Take care of any currently running tasks in open loops
        for task in asyncio.Task.all_tasks():
            task.cancel()

        self.ccxt.shutdown()
