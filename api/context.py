"""A library for use by ApiAdapters to manage and share information between
objects instantiated from the same API classes."""

from utils.dotobj import DotObj
from utils.singleton import Singleton


class AllApiContexts(metaclass=Singleton):
    """
    Shared context between API instances.
    """
    def __init__(self):
        self.contexts = {}  # type: dict

    def get_or_create_context(self, apiname):
        """Creates a context if one doesn't exist for given API"""
        try:
            return self.contexts[apiname]
        except KeyError:
            self.contexts[apiname] = ApiContext()
            return self.contexts[apiname]


class ApiContext(DotObj):
    """
    We want our context to act like a dictionary, but references to work with
    dot-notation.
    """
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__
