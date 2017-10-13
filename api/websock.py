"""A websocket library"""

import json
from socketclusterclient import Socketcluster

from common.log import Logger
from common.config import Conf


class SockMixin:
    """Wrap and manage a websocket interface"""
    def setup(self, callbacks):
        """Setup a websocket;  callbacks is a hash of subscription:callback"""
        self.sock = None
        self.callbacks = callbacks
        self.handler = SockClusterHandler(self.name, self.callbacks)

    def connect(self):
        """Connect to a websocket"""
        self.sock = Socketcluster.socket(self.wsendpoint)
        self.sock.setBasicListener(self.on_connect, self.on_close, self.on_error)
        self.sock.setAuthenticationListener(self.on_set_auth, self.on_auth)
        self.sock.setreconnection(True)
        self.log.info(f"Started websocket, listening on {self.uri}")

    def on_set_auth(self, sock, token):
        """Set Auth request received from websocket"""
        self.log.info(f"Token received: {token}")
        sock.setAuthToken(token)

    def on_auth(self, sock, is_authenticated):
        """Message received from websocket"""
        self.log.info(f"Authenticated: {is_authenticated}")

        def ack(eventname, error, data):
            """Ack"""
            self.log.info(f"Token is {json.dumps(data, sort_keys=True)}")
            self.handler.connected(sock)

        sock.emitack("auth", self.conf.get_api_credentials(), ack)

    def on_connect(self, sock):
        """Message received from websocket"""
        self.log.info("Connected to websocket {self.uri}")

    def on_error(self, sock, err):
        """Error received from websocket"""
        self.log.error(err)

    def on_close(self, sock):
        """Close received from websocket"""
        self.log.info(f"Received close; shutting down websocket {self.uri}")


class SockClusterHandler:
    """Handles Socketcluster alive connections"""
    def __init__(self, name, callbacks):
        self.sock = None
        self.callbacks = callbacks
        self.conf = Conf()
        self.subscriptions = Conf().get_subscriptions()
        self.log = Logger().get(name)

    def connected(self, sock):
        """We have liftoff!"""
        self.sock = sock
        for channel in self.subscriptions:
            self.sock.subscribe(channel)
            self.sock.onchannel(channel, self.callbacks[channel])

    def chanmsg(self, method, msg, callback=lambda k, m:
                self.log.info(f"Received: {k}: {m}")):
        """Received message; process"""
        self.log.debug(f"Sending method {method}: {msg}")
        self.sock.emitack(method, msg, callback)
