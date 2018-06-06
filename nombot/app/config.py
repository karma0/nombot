"""Configuration module"""

from nombot.generics.config import NomConfSchema
from bors.app.config import AppConf


class NomAppConf(AppConf):
    """NomBot configuration Object"""
    schema = NomConfSchema

    def get_currencies(self, service=None):
        """Returns the currencies that we'll be working with"""
        try:
            if service is not None:
                svc_conf = self.services_by_name[service]
                return svc_conf.get("currencies", []).copy() \
                    + self.conf.get("currencies", []).copy()
            return self.conf.get("currencies", []).copy()
        except AttributeError:
            return []
