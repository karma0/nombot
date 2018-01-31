"""
API Core
"""

from nombot.app.log import LoggerMixin


class ApiProduct(LoggerMixin):
    """ApiAdapterFactory Product interface"""
    name = "api_product"
    thread = None
    keep_going = True

    def __init__(self):
        self.api = None
        self.context = None
        self.callback = None
        self.create_logger()

    def interface(self, context):
        """Implement the interface for the adapter object"""
        self.context = context
        self.callback = self.context.get("callback")

    def shutdown(self):
        """Executed on shutdown of application"""
        self.keep_going = False
        if hasattr(self.api, "shutdown"):
            self.api.shutdown()
