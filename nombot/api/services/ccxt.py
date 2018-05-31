"""CCXT API Facade"""

import asyncio
from itertools import product
from dataclasses import dataclass

import ccxt.async as ccxt
from ccxt.base.errors import ExchangeNotAvailable, ExchangeError

from bors.app.log import LoggerMixin

from nombot.generics.request import RequestSchema
from nombot.generics.response import ResponseSchema


@dataclass
class CCXTExchange:
    """Exchange data object"""
    name: str
    symbols: list
    rate_limit: int = None

    _ex = None
    markets = {}  # type: dict
    queue = asyncio.Queue()

    def __post_init__(self):
        # instantiate exchange object
        self._ex = getattr(ccxt, self.name)()

        if self.rate_limit is not None:
            self._ex.rate_limit = self.rate_limit
        self._ex.enable_rate_limit = True

        asyncio.get_event_loop().run_until_complete(self.load())

        if not self.symbols:
            self.symbols = getattr(self._ex, "symbols", [])
        print(f"""SYMS: {self.symbols}""")

    async def load(self, *args, **kwargs):
        """Load the markets; initializing the exchange object with data"""
        markets = await self._ex.load_markets(*args, **kwargs)
        self.markets = {
            "/".join(pair): markets["/".join(pair)]
            for pair in product(self.symbols, self.symbols)
            if pair in markets
        }

    async def call(self, callname, *args, **kwargs):
        """Generalized async `call` method, pass callname and parameters"""
        try:
            await getattr(self._ex, callname)(*args, **kwargs)
        except TypeError:
            raise AttributeError(f"Failed to execute call {callname} on "
                                 f"exchange {self._ex.name}")

    def close(self):
        self._ex.close()


class CCXT:
    """CCXTExchange wrapper"""
    _ex = {}  # type: dict

    def __init__(self, exchanges=None, symbols=None, rate_limit=None):
        if exchanges is None or not exchanges:
            exchanges = ccxt.exchanges

        for exch in exchanges:
            self._ex[exch] = CCXTExchange(exch, symbols, rate_limit)

    async def call_on_exchanges(self, callname, *args, **kwargs):
        """Cycle through all configured exchanges to make a call"""
        for exchange, ex in self._ex.items():
            try:
                await ex.call(callname, *args, **kwargs)
            except (ExchangeNotAvailable, ExchangeError):
                pass

    async def call_over_syms(self, callname, *args, **kwargs):
        """Cycle through configured exchanges and symbols and make a call"""
        print(f"""Calling call_all_on_syms: {callname}""")
        for exchange, ex in self._ex.items():
            for sym, mkt in ex.markets.items():
                print(f"""Exchange: {exchange}; Symbol: {sym}""")
                try:
                    await ex.call(callname, sym, *args, **kwargs)
                except (ExchangeNotAvailable, ExchangeError):
                    pass

    def shutdown(self):
        """Shutdown / cleanup"""
        for exch, ex in self._ex.items():
            ex.close()


class CCXTApi(LoggerMixin):  # pylint: disable=R0902
    """
        This class implements ccxt's REST api as documented in the
        documentation available at:
        https://github.com/ccxt/ccxt/wiki/Manual
    """
    name = "ccxt"

    local_overrides = {
        "fetch_order_book": "call_over_syms",
        "default": "call_on_exchanges",  # required
    }

    def __init__(self, context):
        """Launched by Api when we're ready to connect"""
        self.request_schema = RequestSchema
        self.result_schema = ResponseSchema

        self.context = context
        self.conf = context.get("conf")

        # Websocket credentials object
        self.creds = self.context.get("credentials")

        self.create_logger()
        self.log.debug(f"Starting API Facade {self.name}")

        self.ccxt = CCXT(self.conf["exchanges"], self.context["currencies"])

    def call(self, callname, *args, **kwargs):
        """Substitute for REST api as defined in bors.api.requestor.Req"""
        method = self.local_overrides.get(
                callname, self.local_overrides["default"])
        loop = asyncio.get_event_loop()
        results = []
        loop.run_until_complete(
                getattr(self.ccxt, method)(callname, *args, **kwargs))
        loop.close()

    def shutdown(self):
        """Perform last-minute stuff"""
        self.log.info(f"Shutting down API interface instance for {self.name}")
        self.ccxt.shutdown()
