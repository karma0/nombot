"""Coinigy strategy, subscribes to all favorited channels"""
from api.websock import SockChannel

from app.strategy import IStrategy
from app.log import LoggerMixin

from common.factory import Creator, Product
from common.dotobj import DotObj


class CoinigyFacade(LoggerMixin):
    """Encapsulates some API functionality, initialized on result"""
    possible_channels = []  # type: list

    def __init__(self, api_context):
        self.context = api_context
        self.conf = api_context.get("conf")
        self.wsapi = None
        self.api = None

        # Find the websocket and _connect_all_channels on it
        if self.wsapi is None or self.api is None:
            for inst in self.context.get("inst"):
                if inst.is_connected_ws:
                    self.wsapi = inst
                    # If we don't have a channel list, let's get one
                    if not self.possible_channels:
                        inst.wscall("channels", None,
                                    self._connect_all_channels)

                elif inst.is_connected_ws is not None:
                    self.api = inst

    def _connect_all_channels(self, eventname, error, data):
        """
        Dynamically generate the websocket channels based on exchange and
        currency configurations and what the server reports available.
        """
        if error or eventname != "channels":
            self.log.error(error)
            return

        # We've reached this point if we have a list of channels
        self.possible_channels = [item["channel"] for item in data[0]]

        # Assemble a list of configured channels
        channels = {chan: True for chan in
                    self.conf.get("subscriptions").keys()}

        # Assemble a list of
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
                    if chan in self.possible_channels:
                        if chan not in channels:
                            channels[chan] = False

        self.context["shared"]["channels"] = channels

        # Subscribe to channels that haven't been subscribed to yet
        sockchannels = []
        for chan in [k for k, v in channels.items() if not v]:
            if chan.startswith("ORDER"):
                restype = "order"
            elif chan.startswith("TRADE"):
                restype = "tradeMessage"
            sockchannels.append(
                SockChannel(chan, restype, self.context["callback"]))
            self.log.info(f"""CONNECTING CHANNEL!{chan}""")

        # Connect to channels
        self.wsapi.add_channels(sockchannels)


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
    coinigy = {
        "apiname": "coinigy"
    }


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
        context["strategy"].update({
            "coinigy": {
                "data": parser.product,
                "api": self.api_facade,
                }
            })

        return context
