"""
Generic API Interface, mixin, and request maps/types
"""

from nombot.generics import exchange as X


REQUEST_MAP = {}


class Request:
    """A bare request object"""
    def __init__(self, **kwargs):
        self.callname = kwargs.get('callname', None)
        self.payload = kwargs.get('payload', None)
