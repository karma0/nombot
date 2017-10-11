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

    def get_credentials(self):
        """Returns a Credentials object for API access"""
        Credentials(
            api=self.data["api"]["apiKey"],
            secret=self.data["api"]["apiSecret"],
            endpoint=self.data["api"]["endpoint"]
            )
