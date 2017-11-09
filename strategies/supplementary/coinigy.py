"""Coinigy strategy, subscribes to all favorited channels"""

from app.strategy import IStrategy


class CoinigyFacade:
    """Facade to engage with Coinigy API"""
    _call_lookup = {
        "accounts": "populate_accounts",
    }

    def __init__(self, context):
        self.context = context
        self.result = self.context.get("result")
        self.api_ctx = self.context.get("api_context")
        self.api_ctxs = self.context.get("api_contexts")

    def _lookup(self, callname):
        """Return a callable function based on the name"""
        return self._call_lookup.get(callname, lambda x: x)

    def parse_result(self):
        """Return an update to the context based on the result received"""
        return self._call_lookup.get(
                self.result.context["callname"],
                lambda x: x
            )()

    def populate_accounts(self):
        """Return an accounts object for supplementation"""
        return {self.result.context["callname"]: self.result}

    def connect_all_channels(self, eventname, error, data):  # pylint: disable=unused-argument
        """
        Dynamically generate the websocket channels based on exchange and
        currency configurations and what the server reports available.
        """
        for api_ctx in context.get("api_contexts").items():
            if api_ctx.get("coinigy", None) is not None:

        self.context["shared"]["all_channels"] = {}
        for chan in data[0]:
            self.context["shared"]["all_channels"][chan["channel"]] = False

        for exch in self.context["conf"]["exchanges"]:  # pylint: disable=too-many-nested-blocks
            for curr1 in self.context["currencies"]:
                for curr2 in self.context["currencies"]:
                    for ortra in ["order", "trade"]:
                        for chan in [
                                f"{ortra}-{exch}--{curr1}--{curr2}".upper(),
                                f"{ortra}-{exch}--{curr2}--{curr1}".upper()
                        ]:
                            if chan in self.context.all_channels:
                                self.context.all_channels[chan] = True
        self.subscribed_chans = \
            [k for k, v in self.context.all_channels.items() if v]

        for chan in self.subscribed_chans:
            if chan.startswith("ORDER"):
                restype = "order"
            elif chan.startswith("TRADE"):
                restype = "tradeMessage"
            self.channels.append(
                SockChannel(chan, restype, self.context.callback))

        # SockMixin
        self.connect_channels()


class CoinigyStrategy(IStrategy):
    """Strategy to supplement/act upon Coinigy API events"""
    _data = {
        ws_prepped: False,
        accounts: [],
    }

    def bind(self, context):
        """Bind actions to the strategy context"""
        cf = CoinigyFacade(result, api_ctx)

        # Find the websocket and connect_all_channels on it
        if not self.ws_prepped:
            for ctx in context.get("api_contexts").get("coinigy"):
                if ctx.inst.is_connected_ws:
                    cf.connect_all_channels(ctx.inst)
                    self.ws_prepped = True
                    break

        # Supplement
        context["coinigy"] = _data

        return context
