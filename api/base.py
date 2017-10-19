"""
Generic API Interface, mixin, and request/response maps/types
"""

import abc


class ApiErrorMixin:
    """Generic functions for performing validation and handling errors"""
    def check_missing_parameter(self, call, parameter):
        """Error on missing parameter to call"""
        if hasattr(self, parameter) and not getattr(self, parameter) is None:
            return

        raise Exception(f"Error: in order to retreive {call} from the API, \
                {self.name} requires {parameter} to be passed in.")


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
