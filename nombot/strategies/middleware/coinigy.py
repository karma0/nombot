"""Coinigy strategy, subscribes to all favorited channels"""
from nombot.app.strategy import IStrategy
from nombot.app.log import LoggerMixin

from nombot.common.factory import Creator, Product
from nombot.common.dotobj import DotObj


class CoinigyFacade(LoggerMixin):
    """Encapsulates some API functionality, initialized on result"""
    name = "coinigy_facade"
    chan_callback = None

    def __init__(self, inst, api_context):
        self.context = api_context
        self.conf = api_context.get("conf")
        self.api = inst

        self.create_logger()

    def get_channels(self, callback):
        """Setup possible channels"""
        self.chan_callback = callback
        self.api.wscall("channels", None, self._connect_channels)

    def _connect_channels(self, ename, error, data):   # pylint: disable=W0613
        """
        Dynamically generate the websocket channels based on exchange and
        currency configurations and what the server reports available.
        """
        if error:
            self.log.error(f"Channel request error: {error}")
            return

        # We've reached this point if we have a list of channels
        possible_channels = [item["channel"] for item in data[0]]

        # Assemble a list of configured channels
        channels = {chan: True for chan in
                    self.conf.get("subscriptions").keys()}

        # Assemble a list of possibilities based on the config exch/currency
        ecc = []
        for exch in self.conf["exchanges"]:
            for curr1 in self.context["currencies"]:
                for curr2 in self.context["currencies"]:
                    if curr1 != curr2:
                        ecc.append((exch, curr1, curr2))

        for exch, curr1, curr2 in ecc:
            for ortra in ["order", "trade"]:
                for chan in [
                        f"{ortra}-{exch}--{curr1}--{curr2}".upper(),
                        f"{ortra}-{exch}--{curr2}--{curr1}".upper()
                ]:
                    if chan in possible_channels:
                        if chan not in channels:
                            channels[chan] = False

        self.context["shared"]["channels"] = channels

        # Subscribe to channels that haven't been subscribed to yet
        chan_resp = {}
        for chan in [k for k, v in channels.items() if not v]:
            restype = None
            if chan.startswith("ORDER"):
                restype = "orders"
            elif chan.startswith("TRADE"):
                restype = "trade"
            if restype is not None:
                chan_resp[chan] = restype
                self.log.info(f"""CONNECTING CHANNEL!{chan}""")

        # Connect to channels
        self.api.add_channels(chan_resp)
        self.chan_callback(possible_channels)


class CoinigyResultParserFactory(Creator):
    """Generator of parser objects"""
    def _factory_method(self, *args, **kwargs):
        return CoinigyParser(*args, **kwargs)


class CoinigyParser(Product, LoggerMixin):
    """Result parsing class"""
    name = "coinigy_parser"
    _call_lookup = {}  # type: dict

    def __init__(self, strategy_data, context):
        self.create_logger()
        self.strategy_data = strategy_data
        self.context = context
        self.result = self.context.get("result").data
        self.api_ctx = self.context.get("conf")
        self.api_ctxs = self.context.get("api_contexts")
        self.log.warning(f"""STRATEGY_DATA!{strategy_data}""")
        self.log.warning(f"""CONTEXT!{context}""")

    def _lookup(self, callname):
        """Return a callable function based on the name"""
        return self._call_lookup.get(callname, self._default_parser)

    def _default_parser(self):
        """Return a result object for supplementation"""
        update = {}
        if self.result.callname is not None:
            update[self.result.callname] = self.result
        elif self.result.response_type is not None:
            update[self.result.response_type] = self.result
        elif self.result.channel is not None:
            update[self.result.channel] = self.result

        return self.strategy_data.coinigy.update({"data": update})

    def interface(self):
        """Call the update to the context based on the result received"""
        if self.result.callname is not None:
            self._lookup(self.result.callname)()
        elif self.result.channel is not None:
            self._lookup(self.result.channel)()


class CoinigyStrategyData(DotObj):
    """Object to hold all strategy data"""
    coinigy = {
        "apiname": "coinigy",
        "data": {}
    }

    def __str__(self):
        return self.coinigy.__str__()


class CoinigyStrategy(IStrategy):
    """Strategy to supplement/act upon Coinigy API events"""
    name = "coinigy_strategy"
    possible_channels = {}  # type: dict
    api_facade = None
    ws_facade = None

    def __init__(self):
        self._strategy_data = CoinigyStrategyData()
        self.create_logger()

    def bind(self, context):
        """Bind actions to the strategy context for a given result"""
        if self.ws_facade is None or self.api_facade is None:
            api_context = context.get("api_context")
            for inst in api_context.get("inst"):
                if inst.is_connected_ws:

                    self.ws_facade = CoinigyFacade(inst, api_context)
                    if not self.possible_channels:

                        def pop_chans(chans):
                            """Populate the channels on success"""
                            self.possible_channels = chans

                        self.ws_facade.get_channels(pop_chans)

                elif inst.is_connected_ws is not None:
                    self.api_facade = \
                        CoinigyFacade(inst, api_context)

        parser = CoinigyResultParserFactory(self._strategy_data, context)
        parser.product.interface()

        # initialze supplemented data
        context["strategy"].update({
            "coinigy": {
                "data": parser.product.result,
                "api": self.api_facade,
                "ws": self.ws_facade,
                }
            })

        return context
