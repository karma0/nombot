"""Configuration module"""

from collections import namedtuple
import json

from common.singleton import Singleton


Credentials = namedtuple('Credentials', ('api', 'secret'))


class Conf(metaclass=Singleton):
    """Loads a sane configuration"""
    def __init__(self, filename=None):
        if filename is None:
            filename = "config.json"

        try:
            with open(filename) as data_file:
                self.data = json.load(data_file)
        except:
            raise Exception(f"Could not source config file: {filename}")

    def get_api_credentials(self, apiname):
        """Returns a Credentials object for API access"""
        try:
            return Credentials(
                api=self.data["api"]["services"][apiname]["credentials"]["apikey"],
                secret=self.data["api"]["services"][apiname]["credentials"]["secret"],
                )
        except:
            raise Exception(f"Couldn't find credentials for API: {apiname}")

    def get_api_endpoints(self, apiname):
        """Returns the API endpoints"""
        try:
            return self.data["api"]["services"][apiname]["endpoints"].copy()
        except KeyError:
            raise Exception(f"Couldn't find the API endpoints")

    def get_currencies(self):
        """Returns the currencies that we'll be working with"""
        try:
            return self.data["currencies"].copy()
        except KeyError:
            raise Exception(f"Couldn't find the currencies in the configuration")

    def get_ws_subscriptions(self, apiname):
        """Returns the websocket subscriptions"""
        try:
            return self.data["api"]["services"][apiname]["subscriptions"].copy()
        except KeyError:
            raise Exception(f"Couldn't find the websocket subscriptions")

    def get_api_calls(self):
        """Returns a list of calls to the api to generate the context object"""
        try:
            return self.data["api"]["calls"].copy()
        except:
            raise Exception(f"Couldn't find call list for APIs")

    def get_api(self, name=None):
        """Returns the API configuration"""
        if name is None:
            try:
                return self.data["api"].copy()
            except:
                raise Exception(f"Couldn't find the API configuration")
        try:
            return self.data["api"]["services"][name].copy()
        except:
            raise Exception(f"Couldn't find the API configuration")

    def get_logger(self, name=None):
        """Return a logger configuration object"""
        logconf = self.data["logger"].copy()
        upd = logconf.pop('modules', None)
        try:
            logconf.update(upd[name])
        except KeyError:
            pass
        return logconf
