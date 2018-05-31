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

    def get_currencies(self, service=None):
        """Returns the currencies that we'll be working with"""
        try:
            if service is not None:
                svc_conf = self.services_by_name[service]
                print(f"""svc_conf: {svc_conf}""")
                return svc_conf.get("currencies", []).copy() \
                    + self.conf.get("currencies", []).copy()
            print(f"""currencies: {self.conf.get("currencies")}""")
            return self.conf.get("currencies", []).copy()
        except AttributeError:
            return []
