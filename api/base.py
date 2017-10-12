"""
Generic API Adapter
"""

from collections import namedtuple
import abc

from api.result_types import RESULT_TYPES


class ApiAdapter:
    """Adapter for all IApi implementations"""

    return_types = {
        "alerts": namedtuple('alerts', ('open_alerts', 'alert_history')),
    }

    def __init__(self, conf, Api):
        self.Api = Api
        self.name = Api.name
        self.creds = conf.get_api_credentials(self.name)
        self.calls = conf.get_api_calls()
        self.api = None

    def run(self, callback):
        """Executed on startup of application"""
        self.api = self.Api(self.creds)
        callback({call: self.call(call) for call in self.calls})

    def shutdown(self):
        """Executed on startup of application"""
        self.api.shutdown()

    def call(self, call):
        """Executed on startup of application"""
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
    def call(self, call, query=None, **args):
        """
        Generic interface to REST api
        :param method:  query name
        :param query:   dictionary of inputs
        :param json:    if True return the raw results in json format
        :param args:    keyword arguments added to the payload
        :return:
        """
        pass

    @abc.abstractmethod
    def data(self, exchange, market, data_type):
        """
        Common wrapper for data related queries
        :param exchange:
        :param market:
        :param data_type:
            currently supported are 'history', 'bids', 'asks', 'orders'
        :return:
        """
        pass
