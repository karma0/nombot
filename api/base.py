"""
Generic API Adapter
"""

from collections import namedtuple
import abc
import pandas as pd


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
        callback([self.api.call(call) for call in self.calls])

    def shutdown(self):
        """Executed on startup of application"""
        self.api.shutdown()

    def call(self):
        """Executed on startup of application"""


class IApi:
    """Interface to an Api implementation"""
    # Use name to create a name for your api interface, and use the same
    #  name in your config
    name = "default"

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
