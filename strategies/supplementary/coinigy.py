

class CoinigyStrategy(IStrategy):

    def get_accounts(self, eventname, error, data):  # pylint: disable=unused-argument
        """Get Accounts"""
        self.context["shared"]["accounts"] = data["data"]

    def get_channels(self, eventname, error, data):  # pylint: disable=unused-argument
        """
        Dynamically generate the websocket channels based on exchange and
        currency configurations and what the server reports available.
        """
        if error:
            raise Exception(error)

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
