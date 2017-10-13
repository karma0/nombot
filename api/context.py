"""A library for use by ApiAdapters to manage and share information between
objects instantiated from the same API classes."""

from utils.dotobj import DotObj as ApiContext
from utils.singleton import Singleton


class AllApiContexts(metaclass=Singleton):
    """
    Shared context between API instances.
    """
    def __init__(self):
        self.contexts = {}  # type: dict

    def get(self, apiname):
        """Creates a context if one doesn't exist for given API"""
        try:
            return self.contexts[apiname]
        except KeyError:
            return self.create(apiname)

    def create(self, apiname):
        """Creates a context for given API"""
        self.contexts[apiname] = ApiContext()
        return self.contexts[apiname]
