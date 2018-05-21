"""Configuration module"""

from collections import namedtuple

from bors.app.config import AppConf as BorsAppConf
from bors.common.singleton import Singleton
from nombot.generics.config import ConfSchema


Credentials = namedtuple('Credentials', ('api', 'secret'))


DEFAULT_CONFIG_FILE = "config.json"


class AppConf(metaclass=Singleton):
    """NomBot configuration Object"""
    conf = None
    services_by_name = {}  # type: dict

    def __init__(self, config=None, schema=None):
        # Bail if we've been loaded before
        if self.conf is not None:
            return

        schema = ConfSchema() if schema is None else schema

        self.config = DEFAULT_CONFIG_FILE if config is None else config
        try:
            self.conf = ConfSchema().loads(self.config).data
        except:  # NOQA  # pylint: disable=bare-except
            with open(self.config) as json_data:
                data = json_data.read()
                self.conf = ConfSchema().loads(data).data

        print(f"""NOMAD CONF: {self.conf}""")
        BorsAppConf(config=self.conf, schema=schema)

    def get_api_services_by_name(self):
        """Return a dict of services by name"""
        if not self.services_by_name:
            self.services_by_name = {s.get('name'): s for s in self.conf
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
            return self.conf.get("currencies").copy()
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
            return self.conf.get("api").get("calls").copy()
        except:  # NOQA
            raise Exception(f"Couldn't find call list for APIs")

    def get_api(self, name=None):
        """Returns the API configuration"""
        if name is None:
            try:
                return self.conf.get("api").copy()
            except:  # NOQA
                raise Exception(f"Couldn't find the API configuration")
        try:
            return self.services_by_name.get(name).copy()
        except:  # NOQA
            raise Exception(f"Couldn't find the API configuration")

    def get_logger(self, name=None):
        """Return a logger configuration object"""
        logconf = self.conf.get("logger").copy()
        upd = logconf.pop('modules', None)
        try:
            logconf.update(upd[name])
        except KeyError:
            pass
        return logconf
