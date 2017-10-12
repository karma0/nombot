"""A library for use by ApiAdapters to manage and share information between
objects instantiated from the same API classes."""


class Singleton(type):
    """
    Define an instance operation that lets clients access its unique instance
    """
    def __init__(cls, name, bases, attrs, **kwargs):
        super().__init__(name, bases, attrs)
        cls._instance = None

    def __call__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__call__(*args, **kwargs)
        return cls._instance


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


class ApiContext(dict):
    """
    We want our context to act like a dictionary, but references to work with
    dot-notation.
    """
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__
