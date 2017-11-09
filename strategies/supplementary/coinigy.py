"""Coinigy strategy, subscribes to all favorited channels"""
from api.websock import SockChannel

from app.strategy import IStrategy
from common.factory import Creator, Product


class CoinigyFacade:
    """Encapsulates some API functionality"""
    def __init__(self, api_context):
        self.context = api_context
        self.conf = api_context.get("conf")
        self.api = api_context.get("inst")

    def connect_all_channels(self):
        """
        Dynamically generate the websocket channels based on exchange and
        currency configurations and what the server reports available.
        """
        channels = {}
        for chan in self.conf.get("subscriptions").keys():
            channels[chan] = False

        exch_currencies = []
        for exch in self.conf["exchanges"]:
            for curr1 in self.context["currencies"]:
                for curr2 in self.context["currencies"]:
                    if curr1 != curr2:
                        exch_currencies.append((exch, curr1, curr2))

        for exch, curr1, curr2 in exch_currencies:
            for ortra in ["order", "trade"]:
                for chan in [
                        f"{ortra}-{exch}--{curr1}--{curr2}".upper(),
                        f"{ortra}-{exch}--{curr2}--{curr1}".upper()
                ]:
                    if chan in channels:
                        channels[chan] = True
        self.context["shared"]["channels"] = \
            [k for k, v in self.context.all_channels.items() if v]

        sockchannels = []
        for chan in self.context["shared"]["channels"]:
            if chan.startswith("ORDER"):
                restype = "order"
            elif chan.startswith("TRADE"):
                restype = "tradeMessage"
            sockchannels.append(
                SockChannel(chan, restype, self.context["callback"]))

        # Connect SockMixins
        self.api.channels.extend(sockchannels)
        self.api.connect_channels(sockchannels)


class CoinigyResultParserFactory(Creator):
    """Generator of parser objects"""
    def _factory_method(self, *args, **kwargs):
        return CoinigyParser(*args, **kwargs)


class CoinigyParser(Product):
    """Result parsing class"""
    _call_lookup = {}  # type: dict

    def __init__(self, strategy_data, context):
        self.strategy_data = strategy_data
        self.context = context
        self.result = self.context.get("result")
        self.api_ctx = self.context.get("context")
        self.api_ctxs = self.context.get("api_contexts")

    def _lookup(self, callname):
        """Return a callable function based on the name"""
        return self._call_lookup.get(callname, self._default_parser)

    def _default_parser(self):
        """Return a result object for supplementation"""
        return self.strategy_data.update(
            {self.result.context["callname"]: self.result})

    def interface(self):
        """Return an update to the context based on the result received"""
        return self._call_lookup.get(self.result.context["callname"])()


class CoinigyStrategy(IStrategy):
    """Strategy to supplement/act upon Coinigy API events"""
    ws_prepped = False
    _strategy_data = {}  # type: dict

    def bind(self, context):
        """Bind actions to the strategy context"""
        parser = CoinigyResultParserFactory(self._strategy_data, context)
        parser.product.interface()

        # Find the websocket and connect_all_channels on it
        if not self.ws_prepped:
            api_facade = CoinigyFacade(context.api_context)
            for ctx in context.api_contexts.get("coinigy"):
                if ctx.inst.is_connected_ws:
                    api_facade.connect_all_channels()
                    self.ws_prepped = True
                    break

        # Supplement
        context["strategy"] = self._strategy_data

        return context
