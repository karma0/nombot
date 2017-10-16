"""A websocket library"""

import json
from socketclusterclient import Socketcluster

from core.log import LoggerMixin
from core.config import Conf


class SockMixin:
    """Wrap and manage a websocket interface"""
    def connect_ws(self, post_connect_callback, channels):
        """
        Connect to a websocket
        :channels:  List of SockChannel instances
        """
        self.post_conn_cb = post_connect_callback
        self.channels = channels
        self.sock = Socketcluster.socket(self.wsendpoint)
        self.sock.setBasicListener(self.on_connect, self.on_connect_close,
                                   self.on_connect_error)
        self.sock.setAuthenticationListener(self.on_set_auth, self.on_auth)
        self.sock.setreconnection(False)
        self.sock.connect()
        self.log.info(f"Started websocket, listening on {self.wsendpoint}")

    def on_set_auth(self, sock, token):
        """Set Auth request received from websocket"""
        self.log.info(f"Token received: {token}")
        sock.setAuthtoken(token)

    def on_auth(self, sock, is_authenticated):
        """Message received from websocket"""
        self.log.info(f"Authenticated: {is_authenticated}")

        def ack(eventname, error, data):
            """Ack"""
            if error:
                self.log.error(error)
            self.log.info(f"Token is {json.dumps(data, sort_keys=True)}")
            self.post_conn_cb()

        sock.emitack("auth", self.creds, ack)

    def on_connect(self, sock):
        """Message received from websocket"""
        self.log.info("Connected to websocket {self.wsendpoint}")

    def on_connect_error(self, sock, err):
        """Error received from websocket"""
        self.log.error(err)

    def on_connect_close(self, sock):
        """Close received from websocket"""
        self.log.info(f"Received close; shutting down websocket {self.wsendpoint}")

    def connect_channels(self):
        for channel in self.channels:
            channel.connect(self.sock)


class SockChannel(LoggerMixin):
    """Handles Socketcluster alive connections"""
    name = 'channel' # For logging
    def __init__(self, channel, response_type, callback):
        self.create_logger()
        self.sock = None
        self.channel = channel
        self.response_type = response_type
        self.callback = callback

        self.log.debug(f"Creating channel: {self.channel}")

    def connect(self, sock):
        """We have liftoff!"""
        self.sock = sock
        self.sock.subscribe(self.channel)
        self.sock.onchannel(self.channel, self.callback)
        self.log.debug(f"Listening on channel: {self.channel}")
