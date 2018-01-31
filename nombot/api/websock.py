"""A websocket library"""

from socketclusterclient import Socketcluster

from nombot.app.log import LoggerMixin


class SockMixin:
    """Wrap and manage a websocket interface"""
    def connect_ws(self, post_connect_callback, channels, reconnect=False):
        """
        Connect to a websocket
        :channels:  List of SockChannel instances
        """
        self.post_conn_cb = post_connect_callback
        self.channels = channels
        self.wsendpoint = self.context["conf"]["endpoints"].get("websocket")

        # Skip connecting if we don't have any channels to listen to
        if not channels:
            return

        # Create socket, connect, setting callbacks along the way
        self.sock = Socketcluster.socket(self.wsendpoint)
        self.sock.setBasicListener(self._on_connect, self._on_connect_close,
                                   self._on_connect_error)
        self.sock.setAuthenticationListener(self._on_set_auth, self._on_auth)
        self.sock.setreconnection(reconnect)
        self.sock.connect()

    def on_ws_connect(self):
        """
        Called after websock is established; override me to further init
        """
        pass

    def wscall(self, method, query=None, callback=None):
        """Submit a request on the websocket"""
        if callback is None:
            self.sock.emit(method, query)
        else:
            self.sock.emitack(method, query, callback)

    def connect_channels(self, channels):
        """Connect the provided channels"""
        self.log.info(f"Connecting to channels...")
        for chan in channels:
            chan.connect(self.sock)
            self.log.info(f"\t{chan.channel}")

    # Internal initialization callbacks...

    def _on_set_auth(self, sock, token):
        """Set Auth request received from websocket"""
        self.log.info(f"Token received: {token}")
        sock.setAuthtoken(token)

    def _on_auth(self, sock, authenticated):  # pylint: disable=unused-argument
        """Message received from websocket"""
        def ack(eventname, error, data):  # pylint: disable=unused-argument
            """Ack"""
            if error:
                self.log.error(f"""OnAuth: {error}""")
            else:
                self.connect_channels(self.channels)
                self.post_conn_cb()

        sock.emitack("auth", self.creds, ack)

    def _on_connect(self, sock):  # pylint: disable=unused-argument
        """Message received from websocket"""
        self.log.info(f"Connected to websocket {self.wsendpoint}")

    def _on_connect_error(self, sock, err):  # pylint: disable=unused-argument
        """Error received from websocket"""
        if isinstance(err, SystemExit):
            self.log.error(f"Shutting down websocket connection")
        else:
            self.log.error(f"Websocket error: {err}")

    def _on_connect_close(self, sock):  # pylint: disable=unused-argument
        """Close received from websocket"""
        self.log.info(f"Received close; shut down websocket \
                      {self.wsendpoint}")


class SockChannel(LoggerMixin):
    """Channel object"""
    name = 'channel'  # For logging

    def __init__(self, channel, response_type, callback):
        self.create_logger()
        self.sock = None
        self.channel = channel
        self.response_type = response_type
        self.callback = callback

        self.log.debug(f"Creating channel: {self.channel}")

    def connect(self, sock):
        """Attach a given socket to a channel"""
        def cbwrap(*args, **kwargs):
            """Callback wrapper; passes in response_type"""
            self.callback(self.response_type, *args, **kwargs)

        self.sock = sock
        self.sock.subscribe(self.channel)
        self.sock.onchannel(self.channel, cbwrap)
        self.log.debug(f"Listening on channel: {self.channel}")
