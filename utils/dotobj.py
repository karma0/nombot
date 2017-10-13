"""A library for implementing an object that stores attributes in a way that's
accessible using dot-notation."""


class DotObj(dict):
    """
    We want our context to act like a dictionary, but references to work with
    dot-notation.
    """
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__
