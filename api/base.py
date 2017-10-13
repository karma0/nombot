"""
Generic API Adapter
"""

import abc

from utils.factory import Creator
from api.context import AllApiContexts
from api.result_types import RESULT_TYPES
from common.config import Conf


class ApiAdapterFactory(Creator):  # pylint: disable=too-few-public-methods
    """Generator of ApiAdapters"""
    def _factory_method(self):
        return ApiAdapter()


class ApisAdapter:
    """Adapter of adapters for all API instantiations"""
    def __init__(self, api_classes):
        self.apis = []  # type: list

        # Extract configuration necessary to generate api adapters
        self.conf = Conf()
        api_conf = self.conf.get_api()
        exchanges = getattr(api_conf, "exchanges", [])
        currencies = getattr(api_conf, "currencies", [])

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

    def create_api_adapter(self, api_class, exchange=None, market=None):
        """Create and return an api adapter"""
        api = ApiAdapterFactory()
        api.product.interface(api_class, exchange, market)
        self.apis.append(api.product)

    def run(self, callback):
        """Executed on startup of application"""
        for api in self.apis:
            api.run(callback)

    def shutdown(self):
        """Executed on shutdown of application"""
        for api in self.apis:
            api.shutdown()


class ApiProduct:  # pylint: disable=too-few-public-methods
    """ApiAdapterFactory Product interface"""
    def __init__(self):
        self.api_class = None
        self.name = None
        self.exchange = None
        self.market = None
        self.calls = None
        self.api = None
        self.api_context = None
        self.conf = Conf()

    def interface(self, api_class, exchange=None, market=None):
        """Implement the interface for the adapter object"""
        self.api_class = api_class
        self.name = api_class.name
        self.exchange = exchange
        self.market = market
        self.calls = self.conf.get_api_calls()
        self.api = None
        self.api_context = AllApiContexts().get(self.name)
        self.api_context.creds = self.conf.get_api_credentials(self.name)


class ApiAdapter(ApiProduct):
    """Adapter for any IApi implementations"""
    def run(self, callback):
        """Executed on startup of application"""
        self.api = self.api_class(self.api_context)
        callback({call: self.call(call) for call in self.calls})

    def shutdown(self):
        """Executed on shutdown of application"""
        self.api.shutdown()

    def call(self, call):
        """Executed on startup of application"""
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
    def data(self, data_type):
        """
        Common wrapper for data related queries
        :param data_type:
            currently supported are 'history', 'bids', 'asks', 'orders'
        :return:
        """
        pass
