"""
Define a family of algorithms, encapsulate each one, and make them
interchangeable. Strategy lets the algorithm vary independently from
clients that use it.
"""

import abc

from nombot.app.log import LoggerMixin


class Strategy:
    """
    Define the interface of interest to clients.
    Maintain a reference to a Strategy object.
    """

    def __init__(self, *strategies):
        """Create a strategy using the IStrategy implementation passed in"""
        self.middleware = strategies
        for ware in self.middleware:
            ware.poststartup()

    def execute(self, context):
        """Execute the strategies on the given context"""
        for ware in self.middleware:
            ware.premessage(context)
            context = ware.bind(context)
            ware.postmessage(context)
        return context

    def _shutdown(self):
        pass

    def shutdown(self):
        """Perform cleanup! We're goin' down!!!"""
        for ware in self.middleware:
            ware.preshutdown()
            self._shutdown()
            ware.postshutdown()


class IStrategy(abc.ABC, LoggerMixin):
    """
    Declare an interface common to all supported strategies. Context
    uses this interface to call the strategies.
    """
    name = "override_this_istrategy_name"

    @abc.abstractmethod
    def bind(self, context):
        """Bind to the context"""
        pass

    def poststartup(self):
        """Implement this for post-initialization"""
        pass

    def preshutdown(self):
        """Implement this for pre-shutdown cleanup"""
        pass

    def postshutdown(self):
        """Implement this for post-shutdown cleanup"""
        pass

    def premessage(self, context):
        """Implement this to run something prior to receiving a message"""
        pass

    def postmessage(self, context):
        """Implement this to run something after receiving a message"""
        pass
