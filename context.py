"""
Context for passing through middleware modules
"""


class Context(dict):
    """
    We want our context to act like a dictionary, but references to work with
    dot-notation.
    """
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


def build_context(api_call_results):
    """Assemble and return a context"""
    return Context(api_call_results)
