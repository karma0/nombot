"""Configuration module"""

from collections import namedtuple
import json

from utils.singleton import Singleton


Credentials = namedtuple('Credentials', ('api', 'secret', 'endpoint'))


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
                api=self.data["api"]["services"][apiname]["apiKey"],
                secret=self.data["api"]["services"][apiname]["apiSecret"],
                endpoint=self.data["api"]["services"][apiname]["endpoint"]
                )
        except:
            raise Exception(f"Couldn't find credentials for API: {apiname}")

    def get_api_calls(self):
        """Returns a list of calls to the api to generate the context object"""
        try:
            return self.data["api"]["calls"].copy()
        except:
            raise Exception(f"Couldn't find call list for APIs")

    def get_api(self):
        """Returns the API configuration"""
        try:
            return self.data["api"].copy()
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
