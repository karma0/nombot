"""Configuration module"""

from collections import namedtuple

from common.singleton import Singleton
from generics.config import ConfSchema


Credentials = namedtuple('Credentials', ('api', 'secret'))


class Conf(metaclass=Singleton):
    """Loads a sane configuration"""
    sani_data = None

    def __init__(self, filename=None):
        if filename is None:
            filename = "config.json"

        try:
            with open(filename) as data_file:
                self.data = data_file.read()
        except:
            raise Exception(f"Could not source config file: {filename}")

        self.conf_schema = ConfSchema()
        self.sani_data = self.conf_schema.loads(self.data).errors
        if self.sani_data.errors:
            raise Exception(f"Could not parse config file \
                    ({filename}):\n{self.sani_data.errors}")

        self.services_by_name = {}  # type: dict

    def get_api_services_by_name(self):
        """Return a dict of services by name"""
        if not self.services_by_name:
            self.services_by_name = {s.get('name'): s for s in self.sani_data
                                     .get("api")
                                     .get("services")}
        return self.services_by_name

    def get_api_credentials(self, apiname):
        """Returns a Credentials object for API access"""
        try:
            return Credentials(
                api=self.data
                .get("api")
                .get("services")
                .get(apiname)
                .get("credentials")
                .get("apikey")
                .copy(),

                secret=self.data
                .get("api")
                .get("services")
                .get(apiname)
                .get("credentials")
                .get("secret")
                .copy(),
                )
        except AttributeError:
            raise Exception(f"Couldn't find credentials for API: {apiname}")

    def get_api_endpoints(self, apiname):
        """Returns the API endpoints"""
        try:
            return self.services_by_name\
                    .get(apiname)\
                    .get("endpoints")\
                    .copy()
        except AttributeError:
            raise Exception(f"Couldn't find the API endpoints")

    def get_currencies(self):
        """Returns the currencies that we'll be working with"""
        try:
            return self.sani_data.get("currencies").copy()
        except AttributeError:
            raise Exception(f"Couldn't find the currencies in the \
                            configuration")

    def get_ws_subscriptions(self, apiname):
        """Returns the websocket subscriptions"""
        try:
            return self.services_by_name\
                    .get(apiname)\
                    .get("subscriptions")\
                    .copy()
        except AttributeError:
            raise Exception(f"Couldn't find the websocket subscriptions")

    def get_api_calls(self):
        """Returns a list of calls to the api to generate the context object"""
        try:
            return self.sani_data.get("api").get("calls").copy()
        except:
            raise Exception(f"Couldn't find call list for APIs")

    def get_api(self, name=None):
        """Returns the API configuration"""
        if name is None:
            try:
                return self.sani_data.get("api").copy()
            except:
                raise Exception(f"Couldn't find the API configuration")
        try:
            return self.services_by_name.get(name).copy()
        except:
            raise Exception(f"Couldn't find the API configuration")

    def get_logger(self, name=None):
        """Return a logger configuration object"""
        logconf = self.sani_data.get("logger").copy()
        upd = logconf.pop('modules', None)
        try:
            logconf.update(upd[name])
        except KeyError:
            pass
        return logconf
