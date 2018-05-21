"""Configuration module"""

from collections import namedtuple

from nombot.generics.config import NomConfSchema
from bors.app.config import AppConf


Credentials = namedtuple('Credentials', ('api', 'secret'))


class NomAppConf(AppConf):
    """NomBot configuration Object"""
    def __init__(self, config=None):
        super().__init__(config)
        self.conf = NomConfSchema().load(self.raw_conf).data

    def get_api_credentials(self, apiname):
        """Returns a Credentials object for API access"""
        print(f"""self.data: {self.conf}""")
        for svc in self.conf.get("api").get("services"):
            if svc["name"] == apiname:
                try:
                    return Credentials(
                        api=svc
                        .get("credentials")
                        .get("apikey"),

                        secret=svc
                        .get("credentials")
                        .get("secret"),
                    )
                except AttributeError:
                    raise Exception(
                        f"Couldn't find credentials for API: {apiname}")

    def get_currencies(self):
        """Returns the currencies that we'll be working with"""
        try:
            return self.conf.get("currencies").copy()
        except AttributeError:
            raise Exception(f"Couldn't find the currencies in the \
                            configuration")
