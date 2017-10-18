"""
Generic API Adapter
"""

import abc

from marshmallow import fields, Schema, pre_load

from common.factory import Creator
from api.websock import SockChannel

from generics import exchange as X
from generics.context import ResultSchema


RESPONSE_MAP = {
    "accounts": X.AccountSchema(many=True),
    "balances": X.BalanceSchema(many=True),
    "orders": X.AllOrdersSchema(),
    "alerts": X.AllAlertsSchema(),
    "newsFeed": X.NewsItemSchema(many=True),
    "orderTypes": X.OrderTypesCallSchema(),
    "refreshBalance": X.BalanceSchema(),
    "addOrder": X.OrderReferenceSchema(),
    "exchanges": X.ExchangeSchema(many=True),
    "markets": X.MarketSchema(many=True),
    "data": X.AllMarketDataSchema(),
    "ticker": X.TickSchema(),
}

REQUEST_MAP = {
    "refreshBalance": X.RefreshBalanceSchema(),
    "addAlert": X.CreateAlertSchema(),
    "deleteAlert": X.AlertReferenceSchema(),
    "addOrder": X.CreateOrderSchema(),
    "cancelOrder": X.OrderReferenceSchema(),
    "markets": X.ExchangeReferenceSchema(),
    "data": X.MarketDataRequestSchema(),
    "ticker": X.TickerRequestSchema(),
}


class ResponseSchema(Schema):
    """Schema defining the data structure the API will respond with"""
    data = fields.List(fields.Nested(ResultSchema()), required=True)
    errors = fields.Dict()

    @pre_load
    def find_schema(self, in_data):
        """Parse the incoming schema"""
        if "errors" in in_data:
            return in_data
        in_data["data"] = RESPONSE_MAP[in_data.call]\
            .loads(in_data["data"])\
            .data
        return in_data

    class Meta:
        """Stricty"""
        strict = True


class WsAdapterFactory(Creator):  # pylint: disable=too-few-public-methods
    """Generator of WsAdapters"""
    def _factory_method(self):
        return WsAdapter()


class ApiAdapterFactory(Creator):  # pylint: disable=too-few-public-methods
    """Generator of ApiAdapters"""
    def _factory_method(self):
        return ApiAdapter()


class ApiMetaAdapter:
    """Adapter of adapters for all API instantiations"""
    def __init__(self, api_contexts):
        self.apis = []  # type: list
        self.wsocks = []  # type: list

        self.api_contexts = api_contexts

        for context in api_contexts:
            wsock = WsAdapterFactory()
            wsock.product.interface(context)
            self.wsocks.append(wsock.product)

            api = ApiAdapterFactory()
            api.product.interface(context)
            self.apis.append(api.product)

    def run(self):
        """Executed on startup of application"""
        for wsock in self.wsocks:
            wsock.run(wsock.api_context.get("callback"))
        for api in self.apis:
            api.run(api.api_context.get("callback"))

    def shutdown(self):
        """Executed on shutdown of application"""
        for wsock in self.wsocks:
            wsock.run()
        for api in self.apis:
            api.shutdown()


class ApiProduct:
    """ApiAdapterFactory Product interface"""
    def __init__(self):
        self.api = None
        self.api_context = None

    def interface(self, context):
        """Implement the interface for the adapter object"""
        self.api = None
        self.api_context = context

    def shutdown(self):
        """Executed on shutdown of application"""
        self.api.shutdown()


class WsAdapter(ApiProduct):
    """Adapter for WebSockets"""
    def run(self):
        """
        Called by internal API subsystem to initialize websockets connections
        in the API interface
        """
        self.api = self.api_context.get("cls")(self.api_context)

        # Initialize websocket with channels
        self.api.connect_ws(self.api.on_ws_connect, [
            SockChannel(channel, res_type, self.api_context.get("callback"))
            for channel, res_type in
            self
            .api_context
            .get("conf")
            .get("subscriptions")(self.api_context.get("name")).items()
        ])


class ApiAdapter(ApiProduct):
    """Adapter for any API implementations"""
    def run(self):
        """Executed on startup of application"""
        self.api = self.api_context.get("cls")(self.api_context)

        # TODO: schedule loop
        self.api_context.get("callback")(
            {call: self.call(call) for call in
             self.api_context.get("calls")}
            )

    def call(self, call):
        """Executed on each scheduled iteration"""
        method = getattr(self.api, call, None)
        if callable(method):
            return self.generate_result(method(), call)
        return self.generate_result(self.api.call(call), call)

    def generate_result(self, result, callname):
        """Generate a results object for delivery to the context object"""
        # Retrieve path from API class
        try:
            resp_sch = self.api.result_schema().load(result)
        except:
            raise Exception(f"""Could not parse response for {callname}\n \
                            Errors: {resp_sch["errors"]}""")
        try:
            loaded_sch = RESPONSE_MAP.get(callname).load(resp_sch.data)
            return loaded_sch.data
        except:
            raise Exception(f"""Could not parse response for {callname}\n \
                            Errors: {loaded_sch["errors"]}""")


class ApiErrorMixin:
    """Generic functions for performing validation and handling errors"""
    def check_missing_parameter(self, call, parameter):
        """Error on missing parameter to call"""
        if hasattr(self, parameter) and not getattr(self, parameter) is None:
            return

        raise Exception(f"Error: in order to retreive {call} from the API, \
                {self.name} requires {parameter} to be passed in.")

    def check_for_errors(self, response):
        """Validates that an error hasn't occurred"""
        pass


class IApi:
    """Interface to an Api implementation"""
    # Use name to create a name for your api interface, and use the same
    #  name in your config
    name = "default"

    def shutdown(self):
        """Override to perform any shutdown necessary"""
        pass

    @abc.abstractmethod
    def call(self, method, query=None, **args):
        """
        Generic interface to REST api
        :param method:  query name
        :param query:   dictionary of inputs
        :param args:    keyword arguments added to the payload
        :return:
        """
        pass

    @abc.abstractmethod
    def on_ws_connect(self):
        """
        Called by the websocket mixin
        """
        pass

    @abc.abstractmethod
    def data(self, data_type):
        """
        Common wrapper for data related queries
        :param data_type:
            currently supported are 'history', 'bids', 'asks', 'orders'
        :return:
        """
        pass
