"""
Generic API Adapter
"""

from collections import namedtuple
import abc

from marshmallow import fields, Schema, pre_load

from common.factory import Creator
from api.websock import SockChannel
from core.config import Conf

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
        if in_data.errors:
            return in_data
        in_data["data"] = RESPONSE_MAP[in_data.call].loads(in_data["data"])
        return in_data

    class Meta:
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
    def __init__(self, api_classes):
        self.apis = []  # type: list
        self.wsocks = []  # type: list

        # Extract configuration necessary to generate api adapters
        self.conf = Conf()
        api_conf = self.conf.get_api()
        exchanges = getattr(api_conf, "exchanges", [])
        currencies = getattr(api_conf, "currencies", [])

        # Setup exchange/currency/call adapters
        exch_curr = []
        for exch in exchanges:
            for curr in currencies:
                exch_curr.append((exch, curr))

        if exch_curr:
            for val_pair in exch_curr:
                for api_class in api_classes:
                    self.create_api_adapter(api_class, *val_pair)
        else:
            for api_class in api_classes:
                self.create_api_adapter(api_class)

        for api_class in api_classes:
            self.create_ws_adapter(api_class)

    def create_ws_adapter(self, api_class):
        """Create and return an api adapter"""
        api = WsAdapterFactory()
        api.product.interface(api_class)
        self.wsocks.append(api.product)

    def create_api_adapter(self, api_class):
        """Create and return an api adapter"""
        api = ApiAdapterFactory()
        api.product.interface(api_class)
        self.apis.append(api.product)

    def run(self, callback):
        """Executed on startup of application"""
        for wsock in self.wsocks:
            wsock.run(callback)
        for api in self.apis:
            api.run(callback)

    def shutdown(self):
        """Executed on shutdown of application"""
        for wsock in self.wsocks:
            wsock.run()
        for api in self.apis:
            api.shutdown()


class ApiProduct:
    """ApiAdapterFactory Product interface"""
    def __init__(self):
        self.api_class = None
        self.name = None
        self.calls = None
        self.channels = None
        self.api = None
        self.api_context = None
        self.conf = Conf()
        self.rstypes = RESULT_TYPES.copy()

    def interface(self, api_class):
        """Implement the interface for the adapter object"""
        self.api_class = api_class
        self.name = api_class.name
        self.calls = self.conf.get_api_calls()
        self.channels = self.conf.get_ws_subscriptions(self.name)
        self.api = None
        self.api_context = AllApiContexts().get(self.name)
        self.api_context.creds = self.conf.get_api_credentials(self.name)

        try:
            self.rstypes.update(self.api.result_types)
        except AttributeError:
            pass

    def shutdown(self):
        """Executed on shutdown of application"""
        self.api.shutdown()


class WsAdapter(ApiProduct):
    """Adapter for WebSockets"""
    def run(self, callback):
        """
        Called by internal API subsystem to initialize websockets connections
        in the API interface
        """
        self.api_context.callback = callback
        self.api = self.api_class(self.api_context)

        # Default response type
        self.chanmsg = namedtuple(self.name, ("channel", "message"))

        # Initialize websocket with channels
        self.api.connect_ws(self.api.on_ws_connect,
            [SockChannel(channel, res_type, callback) \
                for channel, res_type in
             self.conf.get_ws_subscriptions(self.name).items()]
        )


class ApiAdapter(ApiProduct):
    """Adapter for any API implementations"""
    def run(self, result_callback):
        """Executed on startup of application"""
        self.api = self.api_class(self.api_context)

        # schedule loop
        result_callback({call: self.call(call) for call in self.calls})

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
            path = self.api.paths[callname]
        except:
            raise Exception(f"Could not retrieve path for {callname}")

        # Parse the path to the data
        idx = result
        count = 0
        try:
            for route in path.split('.'):
                idx = idx[route]
                count += 1
        except:
            raise Exception(f"Failed to find route ({path}) in part {count} \
                            for results:\n{result}")

        # Generate the result object from the result_type
        try:
            if isinstance(idx, dict):
                return [RESULT_TYPES[callname](**r) for r in idx]
            elif isinstance(idx, str):
                return [RESULT_TYPES[callname](idx)]
            return [RESULT_TYPES[callname](**r) for r in idx]
        except:
            raise Exception(f"Could not parse result(s) to object {callname} \
                            for results:\n{idx}")


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
    paths = None

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
