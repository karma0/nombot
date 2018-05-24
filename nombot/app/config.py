"""Configuration module"""

from nombot.generics.config import NomConfSchema
from bors.app.config import AppConf


class NomAppConf(AppConf):
    """NomBot configuration Object"""
    schema = NomConfSchema

    def get_api_credentials(self, apiname):
        """Returns a Credentials object for API access"""
        try:
            creds = self.get_api_service(apiname).get("credentials")
            return {  # simultaneous assign/remove
                "apikey": creds.pop("apikey", None),
                "secret": creds.pop("secret", None),
            }
        except AttributeError:
            raise Exception(f"Couldn't find credentials for API: {apiname}")

    def get_currencies(self):
        """Returns the currencies that we'll be working with"""
        try:
            return self.conf.get("currencies").copy()
        except AttributeError:
            raise Exception(f"Couldn't find the currencies in the \
                            configuration")
