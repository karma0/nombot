"""
Generic API Interface, mixin, and request/response maps/types
"""


class IApi:
    """Interface to an Api implementation"""
    # Use name to create a name for your api interface, and use the same
    #  name in your config
    name = "default"
    result_schema = None
    ws_result_schema = None
    request_schema = None
    ENDPOINT_OVERRIDES = None

    def shutdown(self):
        """Override to perform any shutdown necessary"""
        pass

    def call(self, method, data=None, **args):
        """
        Generic interface to REST api
        :param method:  query name
        :param data:   dictionary of inputs
        :param args:    keyword arguments added to the payload
        :return:
        """
        pass

    def on_ws_connect(self):
        """
        Called by the websocket mixin
        """
        pass
