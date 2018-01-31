"""Coinigy API Facade"""

from marshmallow import fields, pre_load

from nombot.app.log import LoggerMixin
from nombot.api.requestor import Req
from nombot.api.websock import SockMixin

from nombot.generics.request import RequestSchema
from nombot.generics.response import WSResponseSchema, ResponseSchema
from nombot.generics.exchange import NotificationSchema


class CoinigyResponseSchema(ResponseSchema):
    """Schema defining how the API will respond"""
    event = fields.Str()  # for WS response
    notifications = fields.List(fields.Nested(NotificationSchema()))
    err_num = fields.Str()
    err_msg = fields.Str()

    @pre_load
    def combine_errors(self, in_data):  # pylint: disable=no-self-use
        """Convert the error to the expected output"""
        if "err_num" in in_data:
            in_data["errors"] = dict()
            in_data["errors"][in_data["err_num"]] = in_data["err_msg"]

    def get_result(self, data):
        """Return the actual result data"""
        return data.get("data", "")

    class Meta:
        """Add 'data' field"""
        strict = True
        additional = ("data",)


class CoinigyWSResponseSchema(WSResponseSchema):
    """Schema defining the message type from a websocket"""
    def get_result(self, data):
        """Return the actual result data"""
        return data


class Coinigy(LoggerMixin, SockMixin):  # pylint: disable=R0902
    """
        This class implements coinigy's REST api as documented in the
        documentation available at:
        https://github.com/coinigy/api
    """
    name = "coinigy"

    ENDPOINT_OVERRIDES = {
        "history": "data",
        "asks": "data",
        "bids": "data",
        "orders": "data",
        "all": "data"
    }

    def __init__(self, context):
        """Launched by Api when we're ready to connect"""
        self.request_schema = RequestSchema
        self.result_schema = CoinigyResponseSchema
        self.ws_result_schema = CoinigyWSResponseSchema

        # ApiContext
        self.context = context

        # Websocket credentials object
        self.creds = {
            'apiKey': self.context["conf"]["credentials"]["apikey"],
            'apiSecret': self.context["conf"]["credentials"]["secret"],
        }

        # API credetials object
        payload = {
            'X-API-KEY': self.context["conf"]["credentials"]["apikey"],
            'X-API-SECRET': self.context["conf"]["credentials"]["secret"],
        }

        self.create_logger()
        self.log.debug(f"Starting API Facade {self.name}")

        # Web request pool
        self.req = Req(self.context["conf"]["endpoints"]["rest"],
                       payload,
                       self.log)

        self.subscribed_chans = None

        # We don't need to deal directly with requests, so we pass them through
        self.call = self.req.call

    def shutdown(self):
        """Perform last-minute stuff"""
        self.log.info(f"Shutting down API interface instance for {self.name}")
