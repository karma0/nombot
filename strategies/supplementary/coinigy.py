"""Coinigy strategy, subscribes to all favorited channels"""
from api.websock import SockChannel

from app.strategy import IStrategy

from common.factory import Creator, Product
from common.dotobj import DotObj


class CoinigyFacade:
    """Encapsulates some API functionality, initialized on result"""
    ws_prepped = False

    def __init__(self, api_context):
        self.context = api_context
        self.conf = api_context.get("conf")
        self.api = api_context.get("inst")

        # Find the websocket and connect_all_channels on it
        if not self.ws_prepped:
            for inst in self.context.get("inst"):
                try:
                    if inst.is_connected_ws:
                        self.ws_prepped = True
                        self._connect_all_channels(inst)
                        break
                except AttributeError:
                    pass

    # FIXME
    def _connect_all_channels(self, inst):
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
        self.api_ctx = self.context.get("conf")
        self.api_ctxs = self.context.get("api_contexts")

    def _lookup(self, callname):
        """Return a callable function based on the name"""
        return self._call_lookup.get(callname, self._default_parser)

    def _default_parser(self):
        """Return a result object for supplementation"""
        return self.strategy_data.coinigy.update(
            {self.result.callname: self.result})

    def interface(self):
        """Call the update to the context based on the result received"""
        if self.result.callname is not None:
            self._lookup(self.result.callname)()
        elif self.result.channel is not None:
            self._lookup(self.result.channel)()


class CoinigyStrategyData(DotObj):
    """Object to hold all strategy data"""
    coinigy = {}  # type: dict


class CoinigyStrategy(IStrategy):
    """Strategy to supplement/act upon Coinigy API events"""
    name = "coinigy_strategy"

    def __init__(self):
        self._strategy_data = CoinigyStrategyData()
        self.create_logger()
        self.api_facade = None  # initialized on result

    def bind(self, context):
        """Bind actions to the strategy context for a given result"""
        self.api_facade = CoinigyFacade(context.get("api_context"))

        parser = CoinigyResultParserFactory(self._strategy_data, context)
        parser.product.interface()

        # initialze supplemented data
        context["strategy"] = self._strategy_data

        return context
