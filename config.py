"""Configuration module"""

from collections import namedtuple
import json


Credentials = namedtuple('Credentials', ('api', 'secret', 'endpoint'))


class Conf:
    """Loads a sane configuration"""
    def __init__(self, filename="config.json"):
        try:
            with open(filename) as data_file:
                self.data = json.load(data_file)
        except:
            raise Exception(f"Could not source config file: {filename}")

    def get_api_credentials(self, apiname):
        """Returns a Credentials object for API access"""
        try:
            return Credentials(
                api=self.data["api"]["service"][apiname]["apiKey"],
                secret=self.data["api"]["service"][apiname]["apiSecret"],
                endpoint=self.data["api"]["service"][apiname]["endpoint"]
                )
        except:
            raise Exception(f"Couldn't find credentials for API: {apiname}")

    def get_api_calls(self):
        """Returns a list of calls to the api to generate the context object"""
        try:
            return self.data["api"]["calls"]
        except:
            raise Exception(f"Couldn't find call list for APIs")
