"""
Websock API adapter
"""

from multiprocessing import Process

from nombot.api.product import ApiProduct  # pylint: disable=E0611,E0401
from nombot.api.websock import SockChannel  # pylint: disable=E0611,E0401


class WsAdapter(ApiProduct):
    """Adapter for WebSockets"""
    is_connected_ws = None
    api = None
    thread = None

    def run(self):
        """
        Called by internal API subsystem to initialize websockets connections
        in the API interface
        """
        self.api = self.context.get("cls")(self.context)
        self.context["inst"].append(self)  # Adapters used by strategies

        def on_ws_connect(*args, **kwargs):
            """Callback on connect hook to set is_connected_ws"""
            self.is_connected_ws = True
            self.api.on_ws_connect(*args, **kwargs)

        # Initialize websocket in a thread with channels
        self.thread = Process(target=self.api.connect_ws, args=(
            on_ws_connect, [
                SockChannel(channel, res_type, self._generate_result)
                for channel, res_type in
                self
                .context
                .get("conf")
                .get("subscriptions")
                .items()
            ]))
        self.thread.start()

    def wscall(self, *args, **kwargs):
        """Passthrough method"""
        self.api.wscall(*args, **kwargs)

    def add_channels(self, channels):
        """
        Take a list of SockChannel objects and extend the websock listener
        """
        chans = [
            SockChannel(chan, res, self._generate_result)
            for chan, res in channels.items()
        ]
        self.api.channels.extend(chans)
        self.api.connect_channels(chans)

    def _generate_result(self, res_type, channel, result):
        """Generate the result object"""
        schema = self.api.ws_result_schema()
        schema.context['channel'] = channel
        schema.context['response_type'] = res_type
        self.callback(schema.load(result), self.context)
