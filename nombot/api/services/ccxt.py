"""CCXT API Facade"""

from marshmallow import fields, pre_load

from bors.app.log import LoggerMixin

from nombot.generics.request import RequestSchema
from nombot.generics.response import ResponseSchema


class CCXTResponseSchema(ResponseSchema):
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


class CCXTApi:
    exchanges = {}

    def __init__(self, exchanges):
        for exch in exchanges:
            exchange = getattr(ccxt, exch)
            try:
                self.exchanges[exch] = exchange()
                self.exchanges[exch].load_markets()
            except:
                del self.exchanges[exch]
                self.log.error(f"Failed to attach exchange `{exch}`")

    def call_all(self, method, data=None):
        pass


class CCXT(LoggerMixin):  # pylint: disable=R0902
    """
        This class implements ccxt's REST api as documented in the
        documentation available at:
        https://github.com/ccxt/ccxt/wiki/Manual
    """
    name = "ccxt"

    def __init__(self, context):
        """Launched by Api when we're ready to connect"""
        self.request_schema = RequestSchema
        self.result_schema = CCXTResponseSchema

        self.context = context

        # Websocket credentials object
        self.creds = self.context.get("credentials")

        self.create_logger()
        self.log.debug(f"Starting API Facade {self.name}")

        self.ccxt = CCXTApi(self.conf["exchanges"])

    def call(self, callname, data=None, **args):
        """Substitute for REST api as defined in bors.api.requestor.Req"""
        self.ccxt.call_all(callname, data, **args)

    def shutdown(self):
        """Perform last-minute stuff"""
        self.log.info(f"Shutting down API interface instance for {self.name}")
