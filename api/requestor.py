"""A requestor framework"""

import requests

from common.singleton import Singleton


class Req(metaclass=Singleton):
    """A requests adapter to take advantage of pooling features"""
    def __init__(self):
        self.session = requests.Session()

    def get_req_obj(self):
        """Return a requests implementation"""
        return self.session
