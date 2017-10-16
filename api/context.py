"""A library for use by ApiAdapters to manage and share information between
objects instantiated from the same API classes."""

from utils.dotobj import DotObj
from utils.singleton import Singleton
from common.config import Conf


class AllApiContexts(metaclass=Singleton):
    """
    Shared context between API instances.
    """
    def __init__(self):
        self.contexts = {}  # type: dict
        self.conf = Conf()

    def get(self, apiname):
        """Creates a context if one doesn't exist for given API"""
        try:
            return self.contexts[apiname]
        except KeyError:
            return self.create(apiname)

    def create(self, apiname):
        """Creates a context for given API"""
        self.contexts[apiname] = ApiContext()
        self.contexts[apiname].name = apiname
        conf = self.conf.get_api(apiname)
        conf["currencies"] = self.conf.get_currencies()
        self.contexts[apiname].populate(conf)
        return self.contexts[apiname]

    def get_safe_contexts(self):
        """Return sanitized contexts"""
        return {c.name: c.sanitize() for k, c in self.contexts}


class ApiContext(DotObj):
    """ApiContext"""
    conf = None

    def populate(self, conf):
        """Populates the context object"""
        print(f"CONTEXT->CONFIG: {conf}")
        self.conf = conf

    def return_sanitized(self):
        pass
